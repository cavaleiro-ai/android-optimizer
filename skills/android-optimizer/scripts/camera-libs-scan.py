"""Inspect camera libraries pulled from a phone, without running them.

Usage:
  camera-libs-scan.py props   <dir>             properties read by the camera code
  camera-libs-scan.py missing <dir>             libraries referenced but absent from <dir>
  camera-libs-scan.py refs    <lib.so> <text>   does the code really use <text>?

<dir> is a folder with copies of the phone's camera libraries (camera HAL,
libmmcamera*, libchromatix*, liboemcamera...). Pull them with adb; nothing here
touches the phone.

"props" lists names for any ELF. Default values and "refs" need the optional
packages capstone and pyelftools, and only understand 32-bit ARM (Thumb) code,
the usual case for camera stacks up to about 2016 (HAL1, mm-camera2). For
64-bit libraries the tool still lists names, but says it cannot disassemble.

Why "refs" matters: a feature can have strings, a parameter key and a setter in
the HAL and still never be wired. On the test phone, "opti-zoom",
"chroma-flash" and "af-bracket" existed in the Motorola HAL with zero code
references, so installing their libraries changed nothing. Run "refs" before
installing anything into /vendor.
"""
import os
import re
import struct
import sys

try:
    import capstone
    from capstone import arm as A
    from elftools.elf.elffile import ELFFile
    from elftools.elf.relocation import RelocationSection
    HAVE_DISASM = True
except ImportError:
    HAVE_DISASM = False

PROP_RE = re.compile(rb"(?:persist|vendor|debug|ro)\.[A-Za-z0-9_.]*camera[A-Za-z0-9_.]*|persist\.(?:denoise|capture)\.[A-Za-z0-9_.]+")
LIB_RE = re.compile(rb"lib[A-Za-z0-9_+-]+\.so")


def is_elf32_arm(data):
    return data[:4] == b"\x7fELF" and data[4] == 1 and struct.unpack_from("<H", data, 18)[0] == 40


class Thumb:
    """Linear Thumb-2 disassembly with literal-pool address tracking."""

    def __init__(self, path):
        self.data = open(path, "rb").read()
        self.elf = ELFFile(open(path, "rb"))
        self.text = self.elf.get_section_by_name(".text")
        self.slot_sym = {}
        got_sym = {}
        for sec in self.elf.iter_sections():
            if isinstance(sec, RelocationSection):
                symtab = self.elf.get_section(sec["sh_link"])
                for r in sec.iter_relocations():
                    if r["r_info_sym"]:
                        name = symtab.get_symbol(r["r_info_sym"]).name
                        self.slot_sym[r["r_offset"]] = name
                        if sec.name == ".rel.plt":
                            got_sym[r["r_offset"]] = name
        self.plt_sym = self._plt(got_sym)

    def _plt(self, got_sym):
        out = {}
        plt = self.elf.get_section_by_name(".plt")
        if not plt:
            return out
        md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
        md.detail = True
        base = plt["sh_addr"]
        blob = self.data[plt["sh_offset"]:plt["sh_offset"] + plt["sh_size"]]
        for off in range(20, len(blob) - 11, 12):
            ins = list(md.disasm(blob[off:off + 12], base + off))
            if len(ins) != 3:
                continue
            try:
                ip = base + off + 8 + ins[0].operands[2].imm + ins[1].operands[2].imm + ins[2].operands[1].mem.disp
            except (IndexError, AttributeError, capstone.CsError):
                continue
            if ip in got_sym:
                out[base + off] = got_sym[ip]
        return out

    def vread(self, addr, n):
        for seg in self.elf.iter_segments():
            if seg["p_type"] == "PT_LOAD" and seg["p_vaddr"] <= addr < seg["p_vaddr"] + seg["p_filesz"]:
                o = seg["p_offset"] + addr - seg["p_vaddr"]
                return self.data[o:o + n]
        return None

    def cstr(self, addr):
        b = self.vread(addr, 256)
        if not b or b"\0" not in b:
            return None
        s = b[:b.index(b"\0")]
        return s.decode("ascii") if s and all(32 <= c < 127 for c in s) else None

    def instructions(self):
        md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
        md.detail = True
        base = self.text["sh_addr"]
        code = self.data[self.text["sh_offset"]:self.text["sh_offset"] + self.text["sh_size"]]
        off = 0
        while off < len(code):
            moved = False
            for i in md.disasm(code[off:], base + off):
                yield i
                off = i.address + i.size - base
                moved = True
            if not moved:
                off += 2

    def walk(self):
        """Yield (instruction, resolved address or None, register) for literal loads."""
        pending = {}
        for i in self.instructions():
            ops = i.operands
            if i.mnemonic.startswith("ldr") and len(ops) == 2 and ops[1].type == A.ARM_OP_MEM \
                    and ops[1].mem.base == A.ARM_REG_PC:
                lit = ((i.address + 4) & ~3) + ops[1].mem.disp
                b = self.vread(lit, 4)
                if b:
                    value = struct.unpack("<I", b)[0]
                    pending[ops[0].reg] = value
                    yield i, ("abs", lit, value), ops[0].reg
                continue
            if i.mnemonic == "add" and len(ops) == 2 and ops[1].type == A.ARM_OP_REG \
                    and ops[1].reg == A.ARM_REG_PC and ops[0].reg in pending:
                addr = (pending.pop(ops[0].reg) + i.address + 4) & 0xFFFFFFFF
                yield i, ("pcrel", addr, addr), ops[0].reg
                continue
            yield i, None, None


def cmd_props(folder):
    found = {}
    for root, _, files in os.walk(folder):
        for name in sorted(files):
            if not name.endswith(".so"):
                continue
            path = os.path.join(root, name)
            data = open(path, "rb").read()
            for m in PROP_RE.finditer(data):
                found.setdefault(m.group().decode(), {})[name] = None
            if HAVE_DISASM and is_elf32_arm(data):
                for key, default in property_defaults(path):
                    found.setdefault(key, {})[name] = default
    if not HAVE_DISASM:
        print("(sem capstone/pyelftools: so os nomes, sem valores padrao)")
    for key in sorted(found):
        where = ", ".join("%s%s" % (lib, "" if d is None else " [padrao %r]" % d) for lib, d in sorted(found[key].items()))
        print("%-45s %s" % (key, where))


def property_defaults(path):
    t = Thumb(path)
    regs = {}
    out = []
    for i, ref, reg in t.walk():
        if ref and ref[0] == "pcrel":
            regs[reg] = ref[2]
            continue
        if ref:
            continue
        ops = i.operands
        if i.mnemonic in ("mov", "movs") and len(ops) == 2 and ops[1].type == A.ARM_OP_REG and ops[1].reg in regs:
            regs[ops[0].reg] = regs[ops[1].reg]
        elif i.mnemonic in ("bl", "blx") and ops and ops[0].type == A.ARM_OP_IMM:
            if t.plt_sym.get(ops[0].imm) == "property_get" and A.ARM_REG_R0 in regs:
                key = t.cstr(regs[A.ARM_REG_R0])
                default = t.cstr(regs[A.ARM_REG_R2]) if A.ARM_REG_R2 in regs else None
                if key:
                    out.append((key, default))
            regs = {}
        elif i.mnemonic in ("pop", "bx"):
            regs = {}
    return out


def cmd_missing(folder):
    present = set()
    refs = {}
    for root, _, files in os.walk(folder):
        for name in files:
            present.add(name)
    for root, _, files in os.walk(folder):
        for name in sorted(files):
            if not name.endswith(".so"):
                continue
            data = open(os.path.join(root, name), "rb").read()
            for m in LIB_RE.finditer(data):
                lib = m.group().decode()
                if lib != name:
                    refs.setdefault(lib, set()).add(name)
    imaging = re.compile(r"(?i)camera|chromatix|imglib|cac|morpho|arcsoft|ubifocus|optizoom|chromaflash|refocus|"
                         r"trueportrait|seemore|stillmore|denoise|hdr|faceproc|fastcv|adsp|dsp|eis|tnr|altm|scalado")
    print("Bibliotecas de camera ou imagem citadas que nao estao na pasta")
    print("(confira no aparelho com: adb shell ls /vendor/lib /system/lib | grep <nome>):")
    for lib in sorted(refs):
        if lib not in present and imaging.search(lib):
            print("  %-40s citada por %s" % (lib, ", ".join(sorted(refs[lib]))))


def cmd_refs(path, needle):
    if not HAVE_DISASM:
        sys.exit("refs precisa de: python -m pip install capstone pyelftools")
    data = open(path, "rb").read()
    if not is_elf32_arm(data):
        sys.exit("refs so entende ARM de 32 bits. Para 64 bits, use um desmontador completo.")
    t = Thumb(path)
    hits = 0
    for i, ref, reg in t.walk():
        if not ref:
            continue
        kind, where, value = ref
        name = t.slot_sym.get(where) if kind == "pcrel" else (t.slot_sym.get(where) or t.cstr(value))
        if kind == "pcrel" and not name:
            name = t.cstr(value)
        if name and needle in name:
            hits += 1
            print("%#x usa %r" % (i.address, name))
    in_strings = needle.encode() in data
    print("%d referencias no codigo; o texto %s nos dados." % (hits, "aparece" if in_strings else "nao aparece"))
    if in_strings and hits == 0:
        print("O texto existe, mas nenhum codigo o usa: o recurso provavelmente nao esta ligado nesta versao.")


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("props", "missing", "refs"):
        sys.exit(__doc__)
    if sys.argv[1] == "props":
        cmd_props(sys.argv[2])
    elif sys.argv[1] == "missing":
        cmd_missing(sys.argv[2])
    else:
        if len(sys.argv) < 4:
            sys.exit(__doc__)
        cmd_refs(sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    main()
