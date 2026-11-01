"""Summarize the output of frame-sample.sh.

Usage: frame-stats.py <file>

Each frame's actual present time is counted once, so overlapping samples are
safe. Gaps of one second or more mean the samples did not overlap: they are
reported as lost windows and left out of the averages.
"""
import re
import statistics
import sys


def cpu_busy(text):
    start = re.search(r"CPU_START cpu\s+(.*)", text)
    end = re.search(r"CPU_END cpu\s+(.*)", text)
    if not start or not end:
        return None
    delta = [int(b) - int(a) for a, b in zip(start.group(1).split(), end.group(1).split())]
    total = sum(delta[:8])
    return 100 * (total - delta[3] - delta[4]) / total if total else None


def main():
    with open(sys.argv[1], encoding="ascii", errors="ignore") as f:
        text = f.read()
    if "ERRO" in text:
        raise SystemExit(text.strip())

    times, period, expect_period = set(), None, False
    for line in text.splitlines():
        parts = line.split()
        if parts[:1] == ["SAMPLE"]:
            expect_period = True
        elif expect_period and len(parts) == 1 and parts[0].isdigit():
            period, expect_period = int(parts[0]), False
        elif len(parts) == 3 and all(p.isdigit() for p in parts):
            actual = int(parts[1])
            if 0 < actual < 2**62:
                times.add(actual)

    ordered = sorted(times)
    if len(ordered) < 3:
        raise SystemExit("poucos quadros: %d. O app estava desenhando na tela?" % len(ordered))
    gaps = [(b - a) / 1e6 for a, b in zip(ordered, ordered[1:])]
    real = sorted(g for g in gaps if g < 1000)
    if not real:
        raise SystemExit("os quadros lidos estao espalhados demais para medir. Repita com o app em movimento.")
    print("periodo_tela_ms %.2f" % (period / 1e6 if period else 0))
    print("quadros %d em %.1f s" % (len(real) + 1, sum(real) / 1000))
    print("fps %.2f" % (1000 * len(real) / sum(real)))
    print("intervalo_ms mediana %.2f p95 %.2f p99 %.2f max %.1f" % (
        statistics.median(real),
        real[int(len(real) * 0.95)],
        real[int(len(real) * 0.99)],
        real[-1],
    ))
    print("engasgos acima_de_25ms %d acima_de_50ms %d janelas_perdidas %d" % (
        sum(g > 25 for g in real),
        sum(g > 50 for g in real),
        len(gaps) - len(real),
    ))
    busy = cpu_busy(text)
    if busy is not None:
        print("cpu_em_uso %.1f%%" % busy)
    for key in ("TEMP_START", "TEMP_END"):
        found = re.search(key + r"\s+temperature: (\d+)", text)
        if found:
            print("%s %.1f C" % (key.lower(), int(found.group(1)) / 10))


if __name__ == "__main__":
    main()
