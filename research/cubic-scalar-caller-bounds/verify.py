#!/usr/bin/env python3
"""Authenticate and replay the cubic scalar caller package.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError("nonfinite JSON constant: " + value)


def decoded(raw):
    return gzip.decompress(raw) if raw.startswith(b"\x1f\x8b") else raw


def data(raw):
    return json.loads(decoded(raw), object_pairs_hook=unique_object,
                      parse_constant=invalid_constant)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


class Frozen:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.hashes = data((self.root / "FROZEN-SHA256.json").read_bytes())
        self.origins = data((self.root / "ORIGINS.json").read_bytes())
        self.compared = []

    def path(self, name):
        parts = PurePosixPath(name)
        require(not parts.is_absolute() and ".." not in parts.parts,
                "unsafe package path")
        path = self.root / name
        require(path.is_file() and not path.is_symlink(), "missing regular input: " + name)
        require(path.resolve().is_relative_to(self.root), "input escapes package")
        return path

    def raw(self, name):
        require(name in self.hashes, "unregistered input: " + name)
        raw = self.path(name).read_bytes()
        require(digest(raw) == self.hashes[name], "changed frozen input: " + name)
        return raw

    def check_all(self):
        require(set(self.origins) == set(self.hashes), "frozen/origin inventory mismatch")
        for name in self.hashes:
            raw = self.raw(name)
            origin = self.origins[name]
            require(origin["sha256"] == digest(raw), "origin digest mismatch: " + name)
            if "original_sha256" in origin:
                require(digest(decoded(raw)) == origin["original_sha256"],
                        "original decoded bytes changed: " + name)

    def compare(self, expected, generated):
        require(canonical(data(self.raw(expected))) == canonical(data(generated)),
                "complete typed record mismatch: " + expected)
        self.compared.append(expected)

    def run(self, script, arguments):
        source = self.raw(script)
        bootstrap = (
            "import sys\n"
            "source = sys.stdin.buffer.read()\n"
            "sys.argv = sys.argv[1:]\n"
            "namespace = {'__name__': '__main__', '__file__': sys.argv[0]}\n"
            "exec(compile(source, sys.argv[0], 'exec', dont_inherit=True, optimize=0), namespace)\n"
        )
        completed = subprocess.run(
            [sys.executable, "-I", "-B", "-c", bootstrap,
             str(self.path(script)), *map(str, arguments)],
            cwd=self.root, input=source, capture_output=True, check=False)
        require(completed.returncode == 0,
                "checker failed: " + script + "\n"
                + completed.stdout.decode(errors="replace")
                + completed.stderr.decode(errors="replace"))


STAGES = {
    "cubic": ("cubic/check.py", "cubic/CHECKS.json.gz"),
    "independent": ("independent/check.py", "independent/CHECKS.json.gz"),
}


def expected_records(stage):
    return {STAGES[stage][1]}


def check_coverage(stage, compared):
    expected = expected_records(stage)
    require(set(compared) == expected and len(compared) == len(expected),
            "complete stage record coverage changed: " + stage)


def replay(frozen, scratch, stage):
    script, expected = STAGES[stage]
    output = scratch / (stage + ".json")
    arguments = ["--output", output]
    if stage == "independent":
        arguments += ["--historical-receipt", frozen.path("cubic/frozen/CUBIC-FOUR-CALL-GATE.json")]
    frozen.run(script, arguments)
    frozen.compare(expected, output.read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, choices=tuple(STAGES))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    if args.output is not None:
        require(args.output.is_absolute(), "output must be absolute")
        require(not args.output.exists(), "output already exists")
        require(not args.output.resolve().is_relative_to(root), "output must be external")
    frozen = Frozen(root)
    frozen.check_all()
    with tempfile.TemporaryDirectory(prefix="Cubic caller replay ") as directory:
        replay(frozen, Path(directory), args.stage)
    check_coverage(args.stage, frozen.compared)
    frozen.check_all()
    result = {"status": "PASS_CUBIC_CALLER_" + args.stage.upper(),
              "compared": sorted(frozen.compared),
              "no_new_kappa": True}
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        with args.output.open("x") as destination:
            destination.write(encoded)
    print(encoded, end="")


if __name__ == "__main__":
    main()
