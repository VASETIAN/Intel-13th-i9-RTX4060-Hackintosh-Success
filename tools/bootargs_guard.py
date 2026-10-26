"""Read-only example of ordered boot-argument comparison; no system access."""
import argparse
import re


def normalize(value):
    return " ".join(re.split(r"[ \t\r\n]+", value.strip(" \t\r\n")))


def equivalent(expected, actual):
    expected = normalize(expected)
    return bool(expected) and expected == normalize(actual)


def self_test():
    expected = "-v cpus=1 -s"
    accepted = [expected, expected + " ", " " + expected, "  " + expected + "  ",
                "-v  cpus=1 -s", "-v\tcpus=1 -s", "-v\ncpus=1 -s",
                "-v cpus=1 -s\r\n", "\t-v\t cpus=1\n-s\t", "-v cpus=1\t-s"]
    rejected = ["-v cpus=1", "-v cpus=2 -s", "-s cpus=1 -v", expected + " extra=1",
                "extra=1 " + expected, expected + " slide=73", expected + " *",
                expected + "\x00", expected + "\u00a0", "", "   ", "-v cpus=1 -s -s"]
    assert all(equivalent(expected, value) for value in accepted)
    assert not any(equivalent(expected, value) for value in rejected)
    assert not equivalent("", "")
    print("PASS: 22 argument fixtures plus empty-profile rejection; no system access.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--compare", nargs=2, metavar=("EXPECTED", "ACTUAL"))
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.compare:
        passed = equivalent(*args.compare)
        print("PASS" if passed else "STOP: unexpected boot arguments")
        raise SystemExit(0 if passed else 1)
    else:
        parser.print_help()
