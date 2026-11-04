"""Check an APK downloaded from f-droid.org against the official index.

Usage: fdroid-verify.py <package.name> <file.apk> [--index index-v2.json]

Downloads https://f-droid.org/repo/index-v2.json (about 70 MB) unless --index
points to a copy, then looks for a published version of <package.name> whose
SHA-256 equals the file's. Prints the version, minimum Android, native ABIs and
permissions, so they can be checked against the phone before installing.
Exit code 0 only when the hash matches. Delete the index afterwards.
"""
import hashlib
import json
import os
import sys
import tempfile
import urllib.request

INDEX_URL = "https://f-droid.org/repo/index-v2.json"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_index(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    fd, tmp = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        req = urllib.request.Request(INDEX_URL, headers={"User-Agent": "android-optimizer-fdroid-verify"})
        with urllib.request.urlopen(req, timeout=600) as r, open(tmp, "wb") as out:
            while True:
                block = r.read(1 << 20)
                if not block:
                    break
                out.write(block)
        with open(tmp, encoding="utf-8") as f:
            return json.load(f)
    finally:
        os.remove(tmp)


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    package, apk = args[0], args[1]
    index_path = args[args.index("--index") + 1] if "--index" in args else None
    digest = sha256(apk)
    index = load_index(index_path)
    pkg = index.get("packages", {}).get(package)
    if not pkg:
        sys.exit("Pacote %s nao esta no indice do F-Droid." % package)
    for version in pkg["versions"].values():
        if version["file"]["sha256"] == digest:
            m = version["manifest"]
            print("CONFERE: %s %s (codigo %s)" % (package, m.get("versionName"), m.get("versionCode")))
            print("  sha256", digest)
            print("  Android minimo (SDK):", m.get("usesSdk", {}).get("minSdkVersion"))
            print("  codigo nativo:", m.get("nativecode") or "nenhum")
            print("  permissoes:", ", ".join(sorted(p["name"].split(".")[-1] for p in m.get("usesPermission", []))))
            print("  licenca:", pkg.get("metadata", {}).get("license"))
            return
    print("NAO CONFERE: o sha256 %s nao corresponde a nenhuma versao publicada de %s." % (digest, package))
    for version in sorted(pkg["versions"].values(), key=lambda v: -v["manifest"]["versionCode"])[:3]:
        print("  publicado: %s %s" % (version["manifest"].get("versionName"), version["file"]["sha256"]))
    sys.exit(1)


if __name__ == "__main__":
    main()
