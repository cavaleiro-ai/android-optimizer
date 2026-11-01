"""Helpers for RetroArch files, run on the computer.

Usage:
  retroarch-tools.py set <retroarch.cfg> key=value [key=value ...]
  retroarch-tools.py playlist <output.lpl> <game path on device> <core path on device> <label> [core name]

"set" keeps LF line endings and prints each change. Edit the file only while
RetroArch is closed, because it rewrites its configuration when it exits.
"""
import json
import re
import sys


def set_values(path, pairs):
    with open(path, encoding="utf-8", newline="") as f:
        lines = f.read().split("\n")
    seen = set()
    for i, line in enumerate(lines):
        match = re.match(r"^([A-Za-z0-9_]+) = ", line)
        if match and match.group(1) in pairs:
            key = match.group(1)
            lines[i] = '%s = "%s"' % (key, pairs[key])
            seen.add(key)
            print("%s -> %s" % (line, pairs[key]))
    for key in pairs:
        if key not in seen:
            position = len(lines) - 1 if lines and not lines[-1] else len(lines)
            lines.insert(position, '%s = "%s"' % (key, pairs[key]))
            print("novo: %s = %s" % (key, pairs[key]))
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))


def write_playlist(path, game, core, label, core_name):
    data = {
        "version": "1.5",
        "default_core_path": core,
        "default_core_name": core_name,
        "label_display_mode": 0,
        "right_thumbnail_mode": 0,
        "left_thumbnail_mode": 0,
        "thumbnail_match_mode": 0,
        "sort_mode": 0,
        "items": [{
            "path": game,
            "label": label,
            "core_path": core,
            "core_name": core_name,
            "crc32": "DETECT",
            "db_name": "Sony - PlayStation.lpl",
        }],
    }
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("lista criada: " + path)


def main():
    args = sys.argv[1:]
    if len(args) >= 3 and args[0] == "set":
        set_values(args[1], dict(a.split("=", 1) for a in args[2:]))
    elif len(args) in (5, 6) and args[0] == "playlist":
        name = args[5] if len(args) == 6 else "Sony - PlayStation (PCSX ReARMed)"
        write_playlist(args[1], args[2], args[3], args[4], name)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
