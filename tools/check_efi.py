"""Read-only comparison of an EFI copy with this repository's dated Tahoe baseline."""
import argparse
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import plistlib

from validate_publication import IDENTITY_KEYS, ROOT


def public_profile(value):
    value = copy.deepcopy(value)

    def clean(node):
        if isinstance(node, dict):
            for key, child in node.items():
                if key.lower() in IDENTITY_KEYS:
                    node[key] = b"" if isinstance(child, bytes) else ""
                else:
                    clean(child)
        elif isinstance(node, list):
            for child in node:
                clean(child)

    clean(value)
    value["Misc"]["Entries"] = []
    value["Misc"]["Tools"] = []
    for namespace in value["NVRAM"]["Add"].values():
        for key in list(namespace):
            if key.startswith("bluetooth"):
                del namespace[key]
    return value


def different_keys(actual, expected, path=""):
    if type(actual) is not type(expected):
        return [path]
    if isinstance(actual, dict):
        differences = []
        for key in sorted(actual.keys() | expected.keys()):
            where = path + "/" + key
            differences.extend(different_keys(actual[key], expected[key], where)
                               if key in actual and key in expected else [where])
        return differences
    if isinstance(actual, list):
        if len(actual) != len(expected):
            return [path + "/length"]
        return [key for i, (a, b) in enumerate(zip(actual, expected))
                for key in different_keys(a, b, path + "/" + str(i))]
    return [] if actual == expected else [path]


def inside(root, relative):
    path = PurePosixPath(relative.replace("\\", "/"))
    if path.is_absolute() or not path.parts or any(p in {".", ".."} or ":" in p for p in path.parts):
        raise ValueError("Unsafe relative path")
    target = (root / Path(*path.parts)).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError("Path escapes EFI root")
    return target


def references():
    components = json.loads((ROOT / "evidence/tahoe26-boot-components.json").read_text("utf-8"))
    entries = list(components["files"])
    drivers = json.loads((ROOT / "evidence/tahoe26-drivers.json").read_text("utf-8"))["drivers"]
    for driver in drivers:
        if not driver["Enabled"]:
            continue
        for path_key, hash_key in (("PlistPath", "PlistSHA256"), ("ExecutablePath", "ExecutableSHA256")):
            if driver[path_key]:
                entries.append({"Path": "OC/Kexts/" + driver["BundlePath"] + "/" + driver[path_key],
                                "SHA256": driver[hash_key]})
    return entries


def compare_files(root, entries):
    failures = []
    for entry in entries:
        relative = entry["Path"]
        try:
            target = inside(root, relative)
            if not target.is_file():
                failures.append({"path": relative, "issue": "missing"})
                continue
            if "Bytes" in entry and target.stat().st_size != entry["Bytes"]:
                failures.append({"path": relative, "issue": "size"})
                continue
            digest = hashlib.sha256()
            with target.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
            if digest.hexdigest() != entry["SHA256"]:
                failures.append({"path": relative, "issue": "sha256"})
        except (OSError, ValueError):
            failures.append({"path": relative, "issue": "unreadable_or_unsafe"})
    return failures


def audit(root):
    actual = plistlib.loads(inside(root, "OC/config.plist").read_bytes())
    expected = plistlib.loads((ROOT / "config/config.tahoe26.known-good.sample.plist").read_bytes())
    differences = different_keys(public_profile(actual), expected)
    entries = references()
    failures = compare_files(root, entries)
    return {"status": "PASS" if not differences and not failures else "DIFFERENT",
            "reference_date": "2026-11-01", "reference_os": "26.7.1 / 25G241",
            "checked_file_references": len(entries), "file_failures": failures,
            "configuration_differences_key_paths_only": differences,
            "identity_values_printed": False, "writes_performed": False,
            "native_boot_verified": False,
            "not_checked": ["personal identity validity", "custom entries and tools", "disabled files and icons",
                            "macOS system drivers/AuxKC", "physical boot and peripheral functionality"]}


def self_test():
    import tempfile
    profile = plistlib.loads((ROOT / "config/config.tahoe26.known-good.sample.plist").read_bytes())
    private = copy.deepcopy(profile)
    private["PlatformInfo"]["Generic"]["SystemSerialNumber"] = "test-value-never-printed"
    private["Misc"]["Tools"] = [{"Name": "local-only"}]
    apple = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
    private["NVRAM"]["Add"][apple]["bluetoothInternalControllerInfo"] = b"test"
    assert public_profile(private) == profile
    assert private["PlatformInfo"]["Generic"]["SystemSerialNumber"] != ""
    for token in (" -v", " cpus=1", " -nvoff"):
        changed = copy.deepcopy(profile)
        changed["NVRAM"]["Add"][apple]["boot-args"] += token
        assert different_keys(public_profile(changed), profile)
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        fixture = root / "fixture.txt"
        fixture.write_bytes(b"test")
        entry = {"Path": "fixture.txt", "Bytes": 4, "SHA256": hashlib.sha256(b"test").hexdigest()}
        assert compare_files(root, [entry]) == []
        fixture.write_bytes(b"bad!")
        assert compare_files(root, [entry])[0]["issue"] == "sha256"
        fixture.write_bytes(b"short")
        assert compare_files(root, [entry])[0]["issue"] == "size"
        fixture.unlink()
        assert compare_files(root, [entry])[0]["issue"] == "missing"
        for bad in ("../outside", "..\\outside", "/absolute", "C:/outside"):
            assert compare_files(root, [{"Path": bad, "SHA256": ""}])[0]["issue"] == "unreadable_or_unsafe"
    print("PASS: identity omission, configuration drift, file corruption, missing files and path boundaries.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("efi", nargs="?", type=Path, help="EFI copy containing BOOT and OC")
    parser.add_argument("--self-test", action="store_true", help="Only create temporary synthetic fixtures")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.efi:
        try:
            result = audit(args.efi)
        except (OSError, ValueError, KeyError, TypeError, plistlib.InvalidFileException):
            print("STOP: cannot read the expected EFI/config/reference structure; no files changed.")
            raise SystemExit(2)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(0 if result["status"] == "PASS" else 1)
    else:
        parser.error("Provide an EFI directory or --self-test")
