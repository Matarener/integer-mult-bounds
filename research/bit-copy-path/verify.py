#!/usr/bin/env python3
"""Replay the actual BIT path package, keeping generated evidence externally.

Apache-2.0. Substantial OpenAI Codex assistance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def package_path(name):
    relative = Path(name)
    require(not relative.is_absolute() and ".." not in relative.parts,
            "literal package-relative path")
    path = ROOT / relative
    require(not any(p.is_symlink() for p in (path, *path.parents)
                    if p.is_relative_to(ROOT)), "no package source symlinks")
    return path


def source_inventory():
    manifest_path = ROOT / "SOURCES.json"
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw)
    require(manifest["format"] == "bit-copy-path-sources-v1", "source format")
    require(manifest["base"] == "12fa8c5c844be21bfefb38a19503fbd867a11244",
            "scientific checkout pin")
    seen = set()
    for item in manifest["files"]:
        name = item["path"]
        require(name not in seen and name != "SOURCES.json",
                "unique nonrecursive manifest entries")
        seen.add(name)
        data = package_path(name).read_bytes()
        require(len(data) == item["bytes"] and sha(data) == item["sha256"],
                "source bytes changed: " + name)
    actual = {
        str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
        and p.suffix != ".pyc" and p != manifest_path
    }
    require(seen == actual, "source inventory must cover every package file")
    predecessor = json.loads((ROOT / "PREDECESSOR.json").read_bytes())
    require(predecessor["commit"] == "b4ec15cbdb017776c04b0bf369a807f2278113cd",
            "exact predecessor commit")
    require(len(predecessor["files"]) == 10, "exact predecessor input slice")
    for name, item in predecessor["files"].items():
        require(sha(package_path("inputs/" + name).read_bytes()) == item["sha256"],
                "immutable predecessor bytes: " + name)
    replay = json.loads((ROOT / "REPLAY.json").read_bytes())
    require(replay["format"] == "bit-copy-path-replay-v1", "replay format")
    require(len({r["name"] for r in replay["checks"]}) == len(replay["checks"]),
            "unique replay names")
    for row in replay["checks"]:
        require(row["name"].replace("-", "").isalnum(), "simple check name")
        package_path(row["script"])
        package_path(row["expected"])
        require(row["output_flag"] in ("--out", "--output"), "output interface")
        require(isinstance(row["arguments"], list)
                and all(isinstance(a, str) for a in row["arguments"]),
                "literal command arguments")
    return sha(raw), len(seen), replay["checks"]


def main(output):
    output = output.resolve()
    require(not output.is_relative_to(ROOT), "write evidence outside package")
    require(not output.exists(), "choose a fresh output path")
    output.parent.mkdir(parents=True, exist_ok=True)
    evidence = output.with_suffix(".checks")
    evidence.mkdir(exist_ok=True)
    require(not any(evidence.iterdir()), "choose an empty evidence directory")
    source_digest, source_count, checks = source_inventory()
    results = []
    for row in checks:
        name = row["name"]
        expected = package_path(row["expected"]).read_bytes()
        hashes = []
        for optimized in (False, True):
            mode = "optimized" if optimized else "normal"
            receipt = evidence / f"{name}-{mode}.json"
            command = [sys.executable, "-I", "-B"]
            if optimized:
                command.append("-O")
            command += [str(package_path(row["script"])), *row["arguments"],
                        row["output_flag"], str(receipt)]
            process = subprocess.run(command, cwd=ROOT, capture_output=True,
                                     text=True, timeout=300, check=False)
            (evidence / f"{name}-{mode}.log").write_text(
                process.stdout + process.stderr)
            require(process.returncode == 0,
                    f"{name}/{mode} failed:\n{process.stdout}\n{process.stderr}")
            data = receipt.read_bytes()
            require(data == expected,
                    f"{name}/{mode} differs from its frozen mathematical receipt")
            hashes.append(sha(data))
        require(hashes[0] == hashes[1], name + " optimized-mode mismatch")
        results.append({"check": name, "receipt_sha256": hashes[0],
                        "normal": "PASS", "optimized": "PASS"})
        print("PASS " + name, flush=True)
    require(source_inventory() == (source_digest, source_count, checks),
            "source changed during execution")
    result = {
        "status": "PASS_ACTUAL_BIT_COPY_PATH_SCOPED_OBSTRUCTION_NO_NEW_KAPPA",
        "sources_sha256": source_digest,
        "source_files": source_count,
        "fresh_check_invocations": 2 * len(checks),
        "checks": results,
        "predecessor_input_slice_verified": 10,
        "predecessor_full_suite_reexecuted": False,
        "source_bytes_unchanged": True,
        "formal_kernel_proof": False,
        "physical_caller_installed": False,
        "new_kappa": False,
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    main(parser.parse_args().output)
