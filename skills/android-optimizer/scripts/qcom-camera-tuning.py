"""Read sensor modes and auto-exposure limits from Qualcomm mm-camera2 libraries.

Usage:
  qcom-camera-tuning.py modes <libmmcamera_<sensor>.so>
  qcom-camera-tuning.py aec   <libchromatix_<sensor>_<mode>.so> [line_time_us]

Only for 32-bit Qualcomm camera stacks of about 2013-2016 (mm-camera2, HAL1),
with copies pulled from the phone. Read-only and standard library only.
Tested on Sony IMX179 and IMX132 (Moto G 2014). Other sensors may use other
register maps: treat the decoded timings as a lead, and confirm on the device
(for example by counting video frames against the clock).

modes: finds the register tables ({u16 addr, u16 data, u32 delay}) and the
output table ({u16 x, y, line_length, frame_length; u32 vt_clk, op_clk;
u16 binning; float min_fps, max_fps; u32 mode}) and decodes SMIA timings.
fps = pixel_rate / (line_length * frame_length). Sony sensors usually move two
pixels per clock, so both values are printed; the output table tells which one
the vendor used.

aec: finds the exposure table ({u16 gain Q8, u16 pad, u32 line_count}, total
exposure never decreasing). Its last entry is the longest exposure and the
highest gain the automatic mode will ever use. line_time_us = line_length /
pixel_rate; for the IMX179 here it was 3440 / 259.2 MHz = 13.27 us.
"""
import struct
import sys


class Elf:
    def __init__(self, path):
        self.d = d = open(path, "rb").read()
        if d[:4] != b"\x7fELF" or d[4] != 1 or d[5] != 1:
            sys.exit("Esperado ELF de 32 bits little-endian.")
        (shoff,) = struct.unpack_from("<I", d, 0x20)
        shentsize, shnum, shstrndx = struct.unpack_from("<HHH", d, 0x2E)
        (phoff,) = struct.unpack_from("<I", d, 0x1C)
        phentsize, phnum = struct.unpack_from("<HH", d, 0x2A)
        self.segments = []
        for i in range(phnum):
            p_type, off, vaddr, _, filesz, _, _, _ = struct.unpack_from("<8I", d, phoff + i * phentsize)
            if p_type == 1:
                self.segments.append((vaddr, off, filesz))
        raw = [struct.unpack_from("<10I", d, shoff + i * shentsize) for i in range(shnum)]
        names_off = raw[shstrndx][4]
        self.sections = {}
        for s in raw:
            end = d.index(b"\0", names_off + s[0])
            self.sections[d[names_off + s[0]:end].decode()] = {"addr": s[3], "off": s[4], "size": s[5]}
        self.relocs = {}
        for name in (".rel.dyn", ".rel.plt"):
            s = self.sections.get(name)
            if s:
                for i in range(s["size"] // 8):
                    r_off, r_info = struct.unpack_from("<II", d, s["off"] + i * 8)
                    self.relocs[r_off] = r_info & 0xFF

    def off(self, vaddr):
        for va, off, filesz in self.segments:
            if va <= vaddr < va + filesz:
                return off + vaddr - va
        return None

    def u32(self, vaddr):
        o = self.off(vaddr)
        return None if o is None else struct.unpack_from("<I", self.d, o)[0]


def register_tables(e):
    data = e.sections[".data"]
    lo, hi = data["addr"], data["addr"] + data["size"]
    for va in range(lo, hi - 20, 4):
        if va not in e.relocs:
            continue
        p, count, addr_type, data_type = e.u32(va), e.u32(va + 4), e.u32(va + 8), e.u32(va + 12)
        if lo <= p < hi and 8 <= count <= 400 and addr_type in (1, 2) and data_type in (1, 2):
            regs = [struct.unpack_from("<HHI", e.d, e.off(p + 8 * i)) for i in range(count)]
            yield p, regs


def output_table(e):
    data = e.sections[".data"]
    d, base = e.d, data["off"]
    for o in range(base, base + data["size"] - 32, 2):
        x, y, llp, fll, vt, op, binning = struct.unpack_from("<HHHHIIH", d, o)
        mn, mx = struct.unpack_from("<ff", d, o + 20)
        mode = struct.unpack_from("<I", d, o + 28)[0]
        if 160 <= x <= 9000 and 120 <= y <= 7000 and llp >= x // 2 and fll > y // 2 and 1e7 < vt < 3e9 \
                and binning in (1, 2, 4) and 1 <= mn <= 1000 and 1 <= mx <= 1000 and mode < 64:
            yield dict(x=x, y=y, line_length=llp, frame_length=fll, vt_clk=vt, binning=binning,
                       min_fps=round(mn, 2), max_fps=round(mx, 2), mode=mode,
                       fps_calculated=round(vt / (llp * fll), 2))


def decode(regs):
    r = {a: v for a, v, _ in regs}
    w = lambda hi: (r.get(hi, 0) << 8) | r.get(hi + 1, 0)
    inck = (r.get(0x3368, 0) << 8 | r.get(0x3369, 0)) / 256 or 24.0
    pll = inck / max(r.get(0x0305, 1), 1) * w(0x030C)
    vt_pix = pll / max(r.get(0x0301, 1) * r.get(0x0303, 1), 1)
    llp, fll = w(0x0342), w(0x0340)
    out = {
        "saida": "%dx%d" % (w(0x034C), w(0x034E)),
        "janela_do_sensor": "x %d-%d, y %d-%d" % (w(0x0344), w(0x0348), w(0x0346), w(0x034A)),
        "binning (0x0390)": r.get(0x0390),
        "line_length / frame_length": "%d / %d" % (llp, fll),
        "pll_mhz (inck %.1f)" % inck: round(pll, 1),
    }
    if llp and fll and vt_pix:
        out["fps se 1 pixel/clock"] = round(vt_pix * 1e6 / (llp * fll), 2)
        out["fps se 2 pixels/clock"] = round(vt_pix * 2e6 / (llp * fll), 2)
    return out


def cmd_modes(path):
    e = Elf(path)
    tables = list(register_tables(e))
    if not tables:
        print("Nenhuma tabela de registradores no formato esperado.")
    for p, regs in tables:
        print("Tabela de registradores em %#x, %d escritas" % (p, len(regs)))
        for k, v in decode(regs).items():
            print("   %-28s %s" % (k, v))
    print("Tabela de saida (modos que o driver pode escolher):")
    for row in output_table(e):
        print("  ", row)


def cmd_aec(path, line_us):
    e = Elf(path)
    data = e.sections[".data"]
    d, o, end = e.d, data["off"], data["off"] + data["size"]
    found = 0
    while o < end - 8:
        run, p, prev = [], o, 0
        while p < end - 8:
            g, pad, lc = struct.unpack_from("<HHI", d, p)
            if not (128 <= g <= 16384 and pad == 0 and 1 <= lc <= 200000 and g * lc >= prev):
                break
            run.append((g, lc))
            prev = g * lc
            p += 8
        if len(run) >= 40:
            found += 1
            count = struct.unpack_from("<H", d, o - 4)[0]
            valid = run[:count] if 0 < count <= len(run) else run
            g_last, l_last = valid[-1]
            lines_max = max(l for _, l in valid)
            print("Tabela de exposicao em %#x: %d entradas" % (o, len(valid)))
            print("   exposicao maxima: %d linhas = %.1f ms (1/%.0f s)" % (lines_max, lines_max * line_us / 1000,
                                                                         1e6 / (lines_max * line_us)))
            print("   ganho maximo: %.2fx (ultima entrada %.2fx com %d linhas)" % (max(g for g, _ in valid) / 256,
                                                                                g_last / 256, l_last))
            o = p
        else:
            o += 4
    if not found:
        print("Nenhuma tabela de exposicao no formato esperado.")


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("modes", "aec"):
        sys.exit(__doc__)
    if sys.argv[1] == "modes":
        cmd_modes(sys.argv[2])
    else:
        cmd_aec(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 3440 / 259.2)


if __name__ == "__main__":
    main()
