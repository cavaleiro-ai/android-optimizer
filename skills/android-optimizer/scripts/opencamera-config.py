"""Write an Open Camera settings file with chosen values.

Usage:
  opencamera-config.py <saved.xml> <out.xml> [--preset qualidade] [key=value ...]

<saved.xml> is a file made by Open Camera itself (Settings > Settings manager >
Save settings), pulled from
/sdcard/Android/data/net.sourceforge.opencamera/files/backups/.
Starting from it keeps the camera-specific keys the app already chose.
Push <out.xml> back to that folder and load it with "Restore settings". The
file list there starts with a "Parent Folder" row: read the positions from the
screen before tapping.

Values are strings unless they are true/false, which become booleans.
Keys and values come from Open Camera 1.56 (PreferenceKeys.java,
res/xml/preferences_sub_*.xml and res/values/arrays.xml).

The "qualidade" preset is the one tested on the Moto G 2014:
  preference_quality=100        JPEG 100%. Some HALs ignore it in standard
                                mode; check the quantization table of a photo.
  preference_video_bitrate=...  default 20000000. Never above the encoder
                                maxBitRate in media_profiles; check the result
                                with mp4info.py.
  preference_grid=preference_grid_3x3
  preference_show_auto_level=true, preference_show_face_detection=true
"""
import sys
from xml.etree import ElementTree as ET

PRESETS = {
    "qualidade": {
        "preference_quality": "100",
        "preference_photo_mode": "preference_photo_mode_std",
        "preference_video_bitrate": "20000000",
        "preference_grid": "preference_grid_3x3",
        "preference_show_auto_level": "true",
        "preference_show_face_detection": "true",
    }
}


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    src, dst, rest = args[0], args[1], args[2:]
    changes = {}
    i = 0
    while i < len(rest):
        if rest[i] == "--preset":
            changes.update(PRESETS[rest[i + 1]])
            i += 2
            continue
        key, _, value = rest[i].partition("=")
        if not key or not _:
            sys.exit("Use chave=valor: %r" % rest[i])
        changes[key] = value
        i += 1
    root = ET.parse(src).getroot()
    if root.tag != "open_camera_prefs":
        sys.exit("Este arquivo nao foi salvo pelo Open Camera.")
    existing = {el.get("key"): el for el in root}
    for key, value in changes.items():
        kind = "boolean" if value in ("true", "false") else "string"
        if key in existing:
            el = existing[key]
            if el.tag != kind:
                el.tag = kind
            el.set("value", value)
        else:
            ET.SubElement(root, kind, {"key": key, "value": value})
    body = ET.tostring(root, encoding="unicode")
    with open(dst, "w", encoding="utf-8", newline="") as f:
        f.write("<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>" + body)
    for key, value in changes.items():
        print("%s = %s" % (key, value))
    print("Gravado em", dst)


if __name__ == "__main__":
    main()
