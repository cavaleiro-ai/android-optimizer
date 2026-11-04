"""Print duration, resolution and real bitrates of MP4 files.

Usage: mp4info.py <file.mp4> [...]
Reads only the box headers; no external tools needed.
"""
import os
import struct
import sys

CONTAINERS = {b"moov", b"trak", b"mdia", b"minf", b"stbl"}


def boxes(f, start, end):
    pos = start
    while pos + 8 <= end:
        f.seek(pos)
        size, kind = struct.unpack(">I4s", f.read(8))
        header = 8
        if size == 1:
            size = struct.unpack(">Q", f.read(8))[0]
            header = 16
        elif size == 0:
            size = end - pos
        if size < header:
            return
        yield kind, pos + header, pos + size
        pos += size


def walk(f, start, end, info, track):
    for kind, body, stop in boxes(f, start, end):
        if kind == b"trak":
            track = {}
            info["tracks"].append(track)
            walk(f, body, stop, info, track)
        elif kind in CONTAINERS:
            walk(f, body, stop, info, track)
        elif kind == b"mvhd":
            f.seek(body)
            version = f.read(1)[0]
            f.seek(body + (20 if version == 1 else 12))
            if version == 1:
                scale, duration = struct.unpack(">IQ", f.read(12))
            else:
                scale, duration = struct.unpack(">II", f.read(8))
            info["duration"] = duration / scale
        elif kind == b"mdhd" and track is not None:
            f.seek(body)
            version = f.read(1)[0]
            f.seek(body + (20 if version == 1 else 12))
            if version == 1:
                scale, duration = struct.unpack(">IQ", f.read(12))
            else:
                scale, duration = struct.unpack(">II", f.read(8))
            track["duration"] = duration / scale
        elif kind == b"hdlr" and track is not None:
            f.seek(body + 8)
            track["type"] = f.read(4).decode("ascii", "replace")
        elif kind == b"stsd" and track is not None:
            f.seek(body + 12)
            track["codec"] = f.read(4).decode("ascii", "replace")
            if track.get("type") == "vide":
                f.seek(body + 8 + 8 + 24)
                track["size"] = "%dx%d" % struct.unpack(">HH", f.read(4))
            elif track.get("type") == "soun":
                f.seek(body + 8 + 8 + 16)
                channels, _, _, _, rate = struct.unpack(">HHHHI", f.read(12))
                track["audio"] = "%d canais %d Hz" % (channels, rate >> 16)
        elif kind == b"stsz" and track is not None:
            f.seek(body + 4)
            fixed, count = struct.unpack(">II", f.read(8))
            if fixed:
                track["bytes"] = fixed * count
            else:
                data = f.read(4 * count)
                track["bytes"] = sum(struct.unpack(">%dI" % count, data))
            track["samples"] = count


def main():
    for path in sys.argv[1:]:
        info = {"tracks": []}
        with open(path, "rb") as f:
            walk(f, 0, os.path.getsize(path), info, None)
        print("%s: %.2f s, %.1f MB" % (os.path.basename(path), info.get("duration", 0),
                                       os.path.getsize(path) / 1e6))
        for t in info["tracks"]:
            seconds = t.get("duration") or info.get("duration") or 1
            line = "  %s %s" % (t.get("type"), t.get("codec"))
            if "size" in t:
                line += " %s %.1f fps" % (t["size"], t.get("samples", 0) / seconds)
            if "audio" in t:
                line += " " + t["audio"]
            line += " %.2f Mbps" % (8 * t.get("bytes", 0) / seconds / 1e6)
            print(line)


if __name__ == "__main__":
    main()
