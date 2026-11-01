"""Minimal 7z reader using only the Python standard library.

Usage: read7z.py list <archive>
       read7z.py extract <archive> <empty-output-dir>

Supports chains of Copy, LZMA, LZMA2, Delta and BCJ filters. BCJ2 and AES are
reported as unsupported. Every extracted file is checked against its CRC.
"""
import io
import lzma
import os
import struct
import sys
import zlib

SIG = b"7z\xbc\xaf\x27\x1c"
CHUNK = 1 << 20


def num(s):
    first = s.read(1)[0]
    mask, value = 0x80, 0
    for i in range(8):
        if not first & mask:
            return value + ((first & (mask - 1)) << (8 * i))
        value |= s.read(1)[0] << (8 * i)
        mask >>= 1
    return value


def bits(s, n):
    out, cur, mask = [], 0, 0
    for _ in range(n):
        if not mask:
            cur, mask = s.read(1)[0], 0x80
        out.append(bool(cur & mask))
        mask >>= 1
    return out


def digests(s, n):
    defined = [True] * n if s.read(1)[0] else bits(s, n)
    return [struct.unpack("<I", s.read(4))[0] if d else None for d in defined]


class Folder:
    def __init__(self, s):
        self.coders = []
        for _ in range(num(s)):
            flag = s.read(1)[0]
            cid = s.read(flag & 0x0F)
            n_in = n_out = 1
            if flag & 0x10:
                n_in, n_out = num(s), num(s)
            props = s.read(num(s)) if flag & 0x20 else b""
            self.coders.append(dict(id=cid, n_in=n_in, n_out=n_out, props=props))
        self.n_out = sum(c["n_out"] for c in self.coders)
        self.n_in = sum(c["n_in"] for c in self.coders)
        self.binds = [(num(s), num(s)) for _ in range(self.n_out - 1)]
        n_packed = self.n_in - len(self.binds)
        self.packed = [num(s) for _ in range(n_packed)] if n_packed > 1 else None
        if self.packed is None:
            bound = {i for i, _ in self.binds}
            self.packed = [i for i in range(self.n_in) if i not in bound]
        self.sizes, self.crc = [], None

    def unpack_size(self):
        bound = {o for _, o in self.binds}
        for i, size in enumerate(self.sizes):
            if i not in bound:
                return size
        raise ValueError("no final output stream")

    def filters(self):
        if any(c["n_in"] != 1 or c["n_out"] != 1 for c in self.coders):
            raise ValueError("unsupported multi-stream coder (BCJ2?): "
                             + ",".join(c["id"].hex() for c in self.coders))
        order, cur = [], self.packed[0]
        while True:
            order.append(self.coders[cur])
            nxt = [i for i, o in self.binds if o == cur]
            if not nxt:
                break
            cur = nxt[0]
        chain = [make_filter(c) for c in order]
        chain = [f for f in chain if f is not None]
        chain.reverse()
        return chain


def make_filter(c):
    cid, p = c["id"].hex(), c["props"]
    if cid == "00":
        return None
    if cid == "030101":
        v = p[0]
        return dict(id=lzma.FILTER_LZMA1, lc=v % 9, lp=(v // 9) % 5, pb=v // 45,
                    dict_size=struct.unpack("<I", p[1:5])[0])
    if cid == "21":
        d = p[0] & 0x3F
        size = 0xFFFFFFFF if d == 40 else (2 | (d & 1)) << (d // 2 + 11)
        return dict(id=lzma.FILTER_LZMA2, dict_size=size)
    if cid == "03":
        return dict(id=lzma.FILTER_DELTA, dist=p[0] + 1)
    bcj = {"03030103": lzma.FILTER_X86, "04": lzma.FILTER_X86,
           "03030205": lzma.FILTER_POWERPC, "05": lzma.FILTER_POWERPC,
           "03030501": lzma.FILTER_ARM, "07": lzma.FILTER_ARM,
           "03030701": lzma.FILTER_ARMTHUMB, "08": lzma.FILTER_ARMTHUMB,
           "03030805": lzma.FILTER_SPARC, "09": lzma.FILTER_SPARC}
    if cid in bcj:
        return dict(id=bcj[cid])
    raise ValueError("unsupported coder " + cid)


def decode(f, pos, packed, folder):
    """Yield decoded chunks of one folder."""
    if len(folder.packed) != 1:
        raise ValueError("folders with several packed streams are unsupported")
    chain = folder.filters()
    left, want = packed, folder.unpack_size()
    f.seek(pos)
    if not chain:
        while left:
            data = f.read(min(CHUNK, left))
            if not data:
                raise ValueError("truncated archive")
            left -= len(data)
            yield data
        return
    dec = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=chain)
    while want > 0:
        if dec.needs_input:
            data = f.read(min(CHUNK, left)) if left else b""
            left -= len(data)
            if not data and dec.needs_input:
                raise ValueError("truncated archive")
        else:
            data = b""
        out = dec.decompress(data, max_length=min(CHUNK, want))
        want -= len(out)
        if out:
            yield out
        if dec.eof and want:
            raise ValueError("stream ended early")


class Streams:
    def __init__(self):
        self.pack_pos, self.pack_sizes, self.folders = 0, [], []
        self.counts, self.sub_sizes, self.sub_crcs = None, [], []

    def read(self, s):
        while True:
            t = s.read(1)[0]
            if t == 0x00:
                return self
            if t == 0x06:
                self.pack_pos = num(s)
                n = num(s)
                while True:
                    a = s.read(1)[0]
                    if a == 0x00:
                        break
                    if a == 0x09:
                        self.pack_sizes = [num(s) for _ in range(n)]
                    elif a == 0x0A:
                        digests(s, n)
                    else:
                        raise ValueError("bad PackInfo")
            elif t == 0x07:
                self.read_unpack(s)
            elif t == 0x08:
                self.read_sub(s)
            else:
                raise ValueError("bad StreamsInfo %02x" % t)

    def read_unpack(self, s):
        if s.read(1)[0] != 0x0B:
            raise ValueError("expected Folder")
        n = num(s)
        if s.read(1)[0]:
            raise ValueError("external folders unsupported")
        self.folders = [Folder(s) for _ in range(n)]
        if s.read(1)[0] != 0x0C:
            raise ValueError("expected CodersUnpackSize")
        for fo in self.folders:
            fo.sizes = [num(s) for _ in range(fo.n_out)]
        while True:
            a = s.read(1)[0]
            if a == 0x00:
                return
            if a != 0x0A:
                raise ValueError("bad UnpackInfo")
            for fo, c in zip(self.folders, digests(s, n)):
                fo.crc = c

    def read_sub(self, s):
        self.counts = [1] * len(self.folders)
        t = s.read(1)[0]
        if t == 0x0D:
            self.counts = [num(s) for _ in self.folders]
            t = s.read(1)[0]
        for fo, n in zip(self.folders, self.counts):
            if not n:
                continue
            sizes = []
            if t == 0x09:
                sizes = [num(s) for _ in range(n - 1)]
            self.sub_sizes.extend(sizes + [fo.unpack_size() - sum(sizes)])
        if t == 0x09:
            t = s.read(1)[0]
        known, missing = [], 0
        for fo, n in zip(self.folders, self.counts):
            if n == 1 and fo.crc is not None:
                known.append(fo.crc)
            else:
                known.extend([None] * n)
                missing += n
        while t != 0x00:
            if t != 0x0A:
                raise ValueError("bad SubStreamsInfo")
            got = iter(digests(s, missing))
            known = [k if k is not None else next(got) for k in known]
            t = s.read(1)[0]
        self.sub_crcs = known

    def defaults(self):
        if self.counts is None:
            self.counts = [1] * len(self.folders)
            self.sub_sizes = [fo.unpack_size() for fo in self.folders]
            self.sub_crcs = [fo.crc for fo in self.folders]


def read_files(s):
    n = num(s)
    empty, empty_file, names = [False] * n, None, [""] * n
    while True:
        t = s.read(1)[0]
        if t == 0x00:
            break
        data = io.BytesIO(s.read(num(s)))
        if t == 0x0E:
            empty = bits(data, n)
        elif t == 0x0F:
            empty_file = bits(data, sum(empty))
        elif t == 0x11:
            if data.read(1)[0]:
                raise ValueError("external names unsupported")
            names = data.read().decode("utf-16-le").split("\0")[:n]
    files, ei = [], 0
    for i in range(n):
        is_dir = False
        if empty[i]:
            is_dir = not (empty_file[ei] if empty_file else False)
            ei += 1
        files.append(dict(name=names[i], has_stream=not empty[i], is_dir=is_dir))
    return files


def open_archive(f):
    head = f.read(32)
    if head[:6] != SIG:
        raise ValueError("not a 7z archive")
    off, size = struct.unpack("<QQ", head[12:28])
    f.seek(32 + off)
    raw = f.read(size)
    if len(raw) != size:
        raise ValueError("truncated archive")
    s = io.BytesIO(raw)
    t = s.read(1)[0]
    while t == 0x17:
        st = Streams().read(s)
        pos, buf = 32 + st.pack_pos, b""
        for idx, fo in enumerate(st.folders):
            buf = b"".join(decode(f, pos, st.pack_sizes[idx], fo))
            pos += st.pack_sizes[idx]
            if fo.crc is not None and zlib.crc32(buf) & 0xFFFFFFFF != fo.crc:
                raise ValueError("header CRC mismatch")
        s = io.BytesIO(buf)
        t = s.read(1)[0]
    if t != 0x01:
        raise ValueError("bad header %02x" % t)
    st, files = Streams(), []
    t = s.read(1)[0]
    if t == 0x02:
        raise ValueError("archive properties unsupported")
    if t == 0x03:
        raise ValueError("additional streams unsupported")
    if t == 0x04:
        st.read(s)
        t = s.read(1)[0]
    st.defaults()
    if t == 0x05:
        files = read_files(s)
    return st, files


def safe_path(root, name):
    parts = [p for p in name.replace("\\", "/").split("/") if p not in ("", ".")]
    if any(p == ".." or ":" in p for p in parts) or not parts:
        raise ValueError("unsafe path in archive: %r" % name)
    return os.path.join(root, *parts)


def describe(st, files):
    sizes = iter(st.sub_sizes)
    for x in files:
        x["size"] = next(sizes) if x["has_stream"] else 0
    for fo in st.folders:
        print("folder:", " ".join(c["id"].hex() for c in fo.coders),
              "unpacked", fo.unpack_size())
    for x in files:
        print("%14d %s %s" % (x["size"], "D" if x["is_dir"] else "F", x["name"]))
    print("total", sum(x["size"] for x in files))


def extract(f, st, files, out):
    if os.path.exists(out) and os.listdir(out):
        raise ValueError("output directory is not empty")
    os.makedirs(out, exist_ok=True)
    for x in files:
        path = safe_path(out, x["name"])
        if x["is_dir"]:
            os.makedirs(path, exist_ok=True)
        elif not x["has_stream"]:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "wb").close()
    with_stream = iter([x for x in files if x["has_stream"]])
    sizes, crcs = iter(st.sub_sizes), iter(st.sub_crcs)
    pos = 32 + st.pack_pos
    pack_index = 0
    for fo, count in zip(st.folders, st.counts):
        packed = st.pack_sizes[pack_index]
        pack_index += len(fo.packed)
        stream = decode(f, pos, packed, fo)
        pos += packed
        pending = b""
        for _ in range(count):
            x, size, crc = next(with_stream), next(sizes), next(crcs)
            path = safe_path(out, x["name"])
            os.makedirs(os.path.dirname(path), exist_ok=True)
            left, c = size, 0
            with open(path, "wb") as w:
                while left:
                    if not pending:
                        pending = next(stream)
                    part = pending[:left]
                    pending = pending[len(part):]
                    w.write(part)
                    c = zlib.crc32(part, c)
                    left -= len(part)
            ok = crc is None or (c & 0xFFFFFFFF) == crc
            print("%s %d %s" % ("OK " if ok else "BAD", size, x["name"]), flush=True)
            if not ok:
                raise ValueError("CRC mismatch: " + x["name"])
    print("DONE")


def main():
    mode, archive = sys.argv[1], sys.argv[2]
    with open(archive, "rb") as f:
        st, files = open_archive(f)
        if mode == "list":
            describe(st, files)
        elif mode == "extract":
            extract(f, st, files, sys.argv[3])
        else:
            raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
