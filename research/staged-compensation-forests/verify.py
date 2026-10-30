#!/usr/bin/env python3
"""Authenticate and replay the finite staged compensation package.

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


def construction_names():
    names = {"DESIGN.json"}
    for provider in ("base", "extra"):
        names.add("SOURCE-" + provider + ".json.gz")
        for family in ("FOREST", "TWO-SIDED"):
            for kind in ("COMPENSATION", "WORD"):
                names.add(f"{family}-{kind}-{provider}.json.gz")
    return names


def expected_records(stage):
    if stage == "construction":
        return {"artifacts/" + name for name in construction_names()} | {
            "artifacts/PRICES.json", "artifacts/PR1080-COMPARISON.json"}
    return {"forest": {"artifacts/INDEPENDENT-FOREST.json.gz"},
            "wholeword": {"artifacts/WHOLE-WORD.json.gz"}}[stage]


def check_coverage(stage, compared):
    expected = expected_records(stage)
    require(set(compared) == expected and len(compared) == len(expected),
            "complete stage record coverage changed: " + stage)


def construction(frozen, scratch):
    output = scratch / "construction"
    frozen.run("construct.py", [
        "--source-dir", frozen.root / "frozen/inputs", "--out", output])
    names = construction_names()
    require({p.name for p in output.iterdir()} == names,
            "construction output inventory changed")
    for name in sorted(names):
        frozen.compare("artifacts/" + name, (output / name).read_bytes())
    price = scratch / "prices.json"
    frozen.run("price_replay.py", [
        "--artifacts", frozen.root / "artifacts", "--output", price])
    frozen.compare("artifacts/PRICES.json", price.read_bytes())
    prior = scratch / "prior.json"
    frozen.run("compare_prior.py", [
        "--current-word", frozen.root / "frozen/inputs/SOURCE-base.json.gz",
        "--prior-word", frozen.root / "frozen/prior/PR1080-CANONICAL-WORD.json.gz",
        "--prior-recipe", frozen.root / "frozen/prior/PR1080-RECIPE.json",
        "--output", prior])
    frozen.compare("artifacts/PR1080-COMPARISON.json", prior.read_bytes())


def forest(frozen, scratch):
    output = scratch / "forest.json"
    frozen.run("independent_mst.py", [
        "--source-dir", frozen.root / "frozen/inputs",
        "--candidate-dir", frozen.root / "artifacts",
        "--transport-source", frozen.root / "frozen/producers/bw_transport.py",
        "--output", output])
    frozen.compare("artifacts/INDEPENDENT-FOREST.json.gz", output.read_bytes())


def wholeword(frozen, scratch):
    output = scratch / "wholeword.json"
    arguments = []
    for provider in ("base", "extra"):
        arguments += ["--source-" + provider,
                      frozen.root / f"frozen/inputs/SOURCE-{provider}.json.gz",
                      "--candidate-" + provider,
                      frozen.root / f"artifacts/TWO-SIDED-WORD-{provider}.json.gz",
                      "--historical-panel-" + provider,
                      frozen.root / f"frozen/inputs/HISTORICAL-{provider}.json.gz"]
    arguments += [
        "--transport-source", frozen.root / "frozen/producers/bw_transport.py",
        "--emitter-source", frozen.root / "frozen/producers/bw_emit.py",
        "--output", output]
    frozen.run("check_word.py", arguments)
    frozen.compare("artifacts/WHOLE-WORD.json.gz", output.read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True,
                        choices=("construction", "forest", "wholeword"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    if args.output:
        output = args.output.resolve()
        require(not output.is_relative_to(root), "output must be outside package")
        require(not output.exists(), "output already exists")
    frozen = Frozen(root)
    frozen.check_all()
    with tempfile.TemporaryDirectory(prefix="staged-compensation-") as temporary:
        globals()[args.stage](frozen, Path(temporary))
    check_coverage(args.stage, frozen.compared)
    frozen.check_all()
    receipt = {"status": "PASS_STAGED_COMPENSATION_" + args.stage.upper(),
               "complete_records": sorted(frozen.compared),
               "frozen_inputs": len(frozen.hashes), "no_new_kappa": True}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], "records=" + str(len(frozen.compared)))


if __name__ == "__main__":
    main()
