"""Compare photos of the same scene.

Usage: imgstats.py <photo> [<photo> ...] [--crops out.png]

For each photo: size, estimated JPEG quality, exposure data from EXIF,
brightness, clipped shadows/highlights, sharpness (variance of the Laplacian)
and noise (Immerkaer's estimate). Sharpness and noise come from the same
center crop, scaled to a common width, so different resolutions compare.
With --crops, saves 100% center crops side by side for a visual check.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageOps

STD_LUMA = [16, 11, 10, 16, 24, 40, 51, 61, 12, 12, 14, 19, 26, 58, 60, 55,
            14, 13, 16, 24, 40, 57, 69, 56, 14, 17, 22, 29, 51, 87, 80, 62,
            18, 22, 37, 56, 68, 109, 103, 77, 24, 35, 55, 64, 81, 104, 113, 92,
            49, 64, 78, 87, 103, 121, 120, 101, 72, 92, 95, 98, 112, 100, 103, 99]


def ijg_table(quality):
    scale = 5000 / quality if quality < 50 else 200 - 2 * quality
    return [min(255, max(1, (v * scale + 50) // 100)) for v in STD_LUMA]


def jpeg_quality(img):
    """Quality whose standard IJG table is closest to the file's luma table."""
    tables = getattr(img, "quantization", None)
    if not tables or 0 not in tables:
        return None
    table = sorted(tables[0])
    best = min(range(1, 101), key=lambda q: sum(abs(a - b) for a, b in zip(table, sorted(ijg_table(q)))))
    return best


def exif_info(img):
    exif = img.getexif()
    sub = exif.get_ifd(0x8769) if exif else {}
    exposure = sub.get(33434)
    iso = sub.get(34855)
    if isinstance(iso, tuple):
        iso = iso[0]
    if exposure:
        exposure = float(exposure)
        exposure = "1/%d" % round(1 / exposure) if 0 < exposure < 1 else "%.2fs" % exposure
    return exposure, iso, exif.get(271), exif.get(305)


def gray_center(img, longest=2000):
    g = img.convert("L")
    scale = longest / max(g.size)
    width = round(g.width * scale)
    g = g.resize((width, round(g.height * scale)), Image.LANCZOS)
    a = np.asarray(g, dtype=np.float64)
    h, w = a.shape
    return a[h // 4: 3 * h // 4, w // 4: 3 * w // 4]


def laplacian_var(a):
    lap = (-4 * a[1:-1, 1:-1] + a[:-2, 1:-1] + a[2:, 1:-1] + a[1:-1, :-2] + a[1:-1, 2:])
    return lap.var()


def immerkaer_noise(a):
    k = np.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]], dtype=np.float64)
    h, w = a.shape
    acc = np.zeros((h - 2, w - 2))
    for dy in range(3):
        for dx in range(3):
            acc += k[dy, dx] * a[dy:dy + h - 2, dx:dx + w - 2]
    return math.sqrt(math.pi / 2) / (6 * (w - 2) * (h - 2)) * np.abs(acc).sum()


def main():
    args = sys.argv[1:]
    crops_out = None
    if "--crops" in args:
        i = args.index("--crops")
        crops_out = args[i + 1]
        del args[i:i + 2]
    crops = []
    print("%-34s %9s %4s %8s %5s %6s %6s %6s %8s %6s" % (
        "arquivo", "pixels", "q", "expos", "iso", "brilho", "esc%", "estour%", "nitidez", "ruido"))
    for path in args:
        raw = Image.open(path)
        q = jpeg_quality(raw)
        exposure, iso, make, software = exif_info(raw)
        img = ImageOps.exif_transpose(raw)
        lum = np.asarray(img.convert("L"), dtype=np.uint8)
        center = gray_center(img)
        print("%-34s %9s %4s %8s %5s %6.1f %6.2f %6.2f %8.1f %6.2f" % (
            os.path.basename(path)[:34], "%dx%d" % img.size, q, exposure, iso,
            lum.mean(), 100 * (lum <= 4).mean(), 100 * (lum >= 251).mean(),
            laplacian_var(center), immerkaer_noise(center)))
        if crops_out:
            w, h = img.size
            box = (w // 2 - 300, h // 2 - 300, w // 2 + 300, h // 2 + 300)
            crops.append((os.path.basename(path), img.convert("RGB").crop(box)))
    if crops_out and crops:
        sheet = Image.new("RGB", (600 * len(crops), 630), "black")
        draw = ImageDraw.Draw(sheet)
        for i, (name, crop) in enumerate(crops):
            sheet.paste(crop, (600 * i, 30))
            draw.text((600 * i + 8, 8), name[:60], fill="white")
        sheet.save(crops_out)
        print("crops:", crops_out)


if __name__ == "__main__":
    main()
