"""Read-only checks for this small public repository; not an EFI boot test."""
import argparse
import hashlib
from pathlib import Path
import plistlib
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
IDENTITY_KEYS = {"systemserialnumber", "boardserialnumber", "serialnumber", "mlb",
                 "rom", "systemuuid", "system-id", "systemid", "smuuid",
                 "macaddress", "mac-address", "local-mac-address"}
ALLOWED = {".md", ".json", ".plist", ".dsl", ".py", ".txt"}
FORBIDDEN = [r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----",
             r"\bgh[pousr]_[A-Za-z0-9]{20,}\b", r"\bgithub_pat_[A-Za-z0-9_]{20,}\b",
             r"[A-Za-z]:[\\/]Users[\\/]", r"/Users/(?!<)[A-Za-z0-9_.-]+/"]


def private_identity_errors(value, path=""):
    errors = []
    if isinstance(value, dict):
        for key, child in value.items():
            where = path + "/" + key
            if key.lower() in IDENTITY_KEYS and child not in ("", b""):
                errors.append(where)
            errors.extend(private_identity_errors(child, where))
    elif isinstance(value, list):
        for number, child in enumerate(value):
            errors.extend(private_identity_errors(child, path + "/" + str(number)))
    return errors


def local_target(root, document, link):
    url = urlsplit(link)
    if url.scheme or url.netloc or not url.path:
        return None
    target = (document.parent / unquote(url.path)).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError("Link escapes publication directory")
    return target


def publication_files(root):
    files = []
    for item in root.rglob("*"):
        relative = item.relative_to(root)
        if ".git" in relative.parts or "__pycache__" in relative.parts:
            continue
        if item.is_symlink():
            raise ValueError("Publication must not contain symlinks")
        if item.is_file():
            files.append(item)
    return sorted(files)


def self_test():
    assert private_identity_errors({"PlatformInfo": {"MLB": "", "ROM": b""}}) == []
    assert private_identity_errors({"x": [{"SystemSerialNumber": "example-identity"}]})
    assert private_identity_errors({"x": {"ROM": b"\x01\x02"}})
    assert local_target(ROOT, ROOT / "docs" / "x.md", "../README.md") == ROOT / "README.md"
    assert local_target(ROOT, ROOT / "README.md", "https://github.com/example/project") is None
    try:
        local_target(ROOT, ROOT / "README.md", "../private.txt")
    except ValueError:
        pass
    else:
        raise AssertionError("Escaping link accepted")
    print("PASS: identity fields, binary identity, nested fields and link boundaries.")


def validate():
    files = publication_files(ROOT)
    assert files, "No publication files"
    total = 0
    for item in files:
        relative = item.relative_to(ROOT).as_posix()
        assert item.name in {"LICENSE", ".gitignore", ".gitattributes", "SHA256SUMS"} or item.suffix in ALLOWED, relative
        assert item.stat().st_size < 1024 ** 2, "Unexpected large file: " + relative
        raw = item.read_bytes()
        total += len(raw)
        text = raw.decode("utf-8")
        for pattern in FORBIDDEN:
            assert not re.search(pattern, text), "Potential private material in " + relative
        if item.suffix == ".plist":
            data = plistlib.loads(raw)
            assert not private_identity_errors(data), "Identity fields not empty in " + relative
            assert data["Misc"]["Entries"] == [] and data["Misc"]["Tools"] == []
            bootargs = data["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]
            assert "cpus=1" in bootargs.split() and "-s" not in bootargs.split()
        if item.suffix == ".md":
            for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                target = local_target(ROOT, item, link)
                assert target is None or target.is_file(), "Missing local link in " + relative
    manifest = ROOT / "SHA256SUMS"
    if manifest.exists():
        actual = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in files if p != manifest}
        declared = {}
        for line in manifest.read_text(encoding="utf-8").splitlines():
            digest, name = line.split("  ", 1)
            assert re.fullmatch(r"[0-9a-f]{64}", digest)
            assert name not in declared, "Duplicate manifest entry"
            declared[name] = digest
        assert actual == declared, "Manifest differs from publication files"
    assert total < 1024 ** 2, "Publication unexpectedly exceeds one MiB"
    print(f"PASS: {len(files)} small UTF-8 files, {total:,} bytes; local links and sanitized identity checked.")
    print("No disks, firmware, accounts or system configuration were modified.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    self_test() if args.self_test else validate()
