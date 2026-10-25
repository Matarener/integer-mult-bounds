#!/usr/bin/env python3
"""Portable fixed-cut replay. Chris R/OpenAI Codex assistance; Apache-2.0."""
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE_PATH = "research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz"
SOURCE_SHA = "7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05"
CORE_SHA = "f5c45a13239ea521140920c016e2436195580f78112a45240adaba314041cd12"
EXPECTED_SHA = "70a30ac467a8d9a2b15e54d88b519258ef5bfff98fed11832a208c31c4fd0c81"

def require(ok, message):
    if not ok:
        raise ValueError(message)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def coefficient(row, variable):
    entries = [term for term in row if term["input"] == variable]
    require(all(not term["warp_word"] for term in entries), "witness empty warp words")
    return sum((Fraction(t["numerator"], t["denominator"]) for t in entries), Fraction(0))

def span(basis):
    points = {0}
    for vector in basis:
        points |= {point ^ vector for point in tuple(points)}
    return points

def main():
    source = ROOT / SOURCE_PATH
    core = PACKAGE / "cut9047.py"
    expected = (PACKAGE / "expected/RESULT.json").read_bytes()
    require(sha(source.read_bytes()) == SOURCE_SHA, "live native source bytes")
    require(sha(core.read_bytes()) == CORE_SHA, "unchanged independent checker bytes")
    require(sha(expected) == EXPECTED_SHA, "frozen original scientific evidence bytes")
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    live = [row for row in sources["files"] if row["path"] == SOURCE_PATH]
    require(len(live) == 1 and live[0]["usage"] == "input" and live[0]["sha256"] == SOURCE_SHA,
            "source declaration binds live input")
    outputs = []
    for flags in ([], ["-O"]):
        command = [sys.executable, "-I", *flags, "-B", str(core), "--source", str(source)]
        done = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=65)
        require(done.returncode == 0, "checker exit: " + done.stderr.decode(errors="replace"))
        require(not done.stderr, "checker empty stderr")
        require(done.stdout == expected, "complete replay equals frozen evidence; zero exclusions")
        outputs.append(done.stdout)
    require(outputs[0] == outputs[1], "complete normal/optimized equality")
    result = json.loads(outputs[0])
    require(result["all_coframed_owner_inventory"] == [["L", 19], ["L", 300], ["L", 301]],
            "complete coframed owner inventory")
    require(all(value == "PASS" for value in result["controls"].values()), "declared checker controls")
    for target in ("300", "301"):
        for name, rank in (("span_all_coframed", 3), ("span_all_coframed_with_successors", 5)):
            record = result[name][target]
            require(not record["member"] and record["span_rank"] == rank
                    and record["augmented_rank"] == rank + 1, "negative exact rank certificate")
    for row in result["selected_rows"].values():
        require(coefficient(row, "L300") - 4 * coefficient(row, "L505") == 0,
                "first separator annihilates every available row")
        require(coefficient(row, "L301") + coefficient(row, "L226") == 0,
                "second separator annihilates every available row")
    document = json.loads(gzip.decompress(source.read_bytes()))
    canonical = document["canonical"]
    for owner in (300, 505, 301, 226):
        require(canonical["start"][owner] == 0 and canonical["frames"][0] == [],
                "witness input chart compatibility")
    anchors = [span(canonical["frames"][i]) for i in (423, 430, 419)]
    require(anchors == [{0, 102, 273, 375}, {0, 85, 273, 324}, {0, 51, 273, 290}],
            "literal retained-anchor spans")
    require(set.intersection(*anchors) == span(canonical["frames"][21]) == {0, 273},
            "retained-anchor common frame dimension one")
    require(sha(source.read_bytes()) == SOURCE_SHA and sha(core.read_bytes()) == CORE_SHA,
            "source and checker unchanged after replay")
    print("PASS_SHARED_CROSSING_CUT9047_SCALAR_OBSTRUCTION")
    print(json.dumps({"source_sha256": SOURCE_SHA, "scientific_output_sha256": EXPECTED_SHA,
                      "normal_optimized_complete_equality": True,
                      "scope": "original prefix, exact cut9047/frame21, rational scalar recoding only",
                      "new_kappa": None}, sort_keys=True))

if __name__ == "__main__":
    main()
