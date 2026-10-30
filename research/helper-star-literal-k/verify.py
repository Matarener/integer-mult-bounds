#!/usr/bin/env python3
"""The restored helper edge does not make the literal K mask true.

One edge is h0 ^= h1, then y ^= h0, then the same helper gate again. Both
helpers finish at their starting columns. The checker's literal mask names
only the target gate's source. The value delivered to y also contains h1.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
CHECKER = ROOT / "research/e8-bit-p111-tuned/code/xcheck_p.py"
BUILD = ROOT / "research/r439-helper-stars-seed19/build.py"
STARS = ROOT / "research/r439-bsection-stars-seed01/README.md"
SEMANTIC = ROOT / "research/r439-semantic-d-contract-seed10/README.md"
MARKER = "PASS_HELPER_STAR_LITERAL_K literal_k_matches=false no_new_kappa"
SOURCE = 0
TARGET = 1
HELPER0 = 2
HELPER1 = 3


def fail(message):
    raise SystemExit("FAIL_HELPER_STAR_LITERAL_K " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/e8-bit-p111-tuned/code/xcheck_p.py",
        "research/r439-helper-stars-seed19/build.py",
        "research/r439-bsection-stars-seed01/README.md",
        "research/r439-semantic-d-contract-seed10/README.md",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def replay(gates, values):
    for dest, sources in gates:
        acc = 0
        for source in sources:
            acc ^= values[source]
        values[dest] ^= acc


def named_mask(gates):
    mask = 0
    for dest, sources in gates:
        if dest == TARGET:
            for source in sources:
                mask ^= 1 << source
    return mask


def helper_mask(value):
    return value & (((1 << 2) - 1) << 2)


def start():
    return [1 << register for register in range(4)]


def finish(gates):
    values = start()
    replay(gates, values)
    return values


def evaluate():
    authenticate()
    checker = CHECKER.read_text(encoding="utf-8")
    build = BUILD.read_text(encoding="utf-8")
    stars = STARS.read_text(encoding="utf-8")
    semantic = SEMANTIC.read_text(encoding="utf-8")
    require('C["K_equals_D"] = all(raw[v + t] & smask == N[t] for t in range(v))' in checker, "the K test moved")
    require("N[g[1] - v] ^= 1 << s" in checker, "the literal source mask moved")
    require("helper = [[0, 2 * v + a, [2 * v + b]] for a, b in edges]" in build, "the star edge moved")
    require('word["D"] = helper + parent["D"][:306] + middle + parent["D"][306 + v:] + helper[::-1]' in build, "the restoration bracket moved")
    require("syntactic `H2_D_frame0_targets_from_helpers` and `K_equals_D`" in stars, "the false-flag sentence moved")
    require("`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`" in stars, "the paid profile moved")
    require("h0 += h1; y += h0; h0 += h1 restores both arbitrary helpers and adds h0+h1 to y." in semantic, "the displayed edge moved")
    star = [(HELPER0, [HELPER1]), (TARGET, [HELPER0]), (HELPER0, [HELPER1])]
    plain = [(TARGET, [HELPER0]), (TARGET, [HELPER1])]
    done = finish(star)
    delivered = helper_mask(done[TARGET])
    named = named_mask(star)
    require(done[SOURCE] == 1 << SOURCE, "the source moved")
    require(done[HELPER0] == 1 << HELPER0 and done[HELPER1] == 1 << HELPER1, "a helper was not restored")
    require(named == 1 << HELPER0, "the literal mask is not h0")
    require(delivered == (1 << HELPER0) ^ (1 << HELPER1), "the delivered mask is not h0 XOR h1")
    require(delivered != named, "the literal mask matched the delivery")
    cut = start()
    replay(star[:1], cut)
    require(cut[HELPER0] == (1 << HELPER0) ^ (1 << HELPER1), "the cut helper was clean")
    plain_done = finish(plain)
    require(helper_mask(plain_done[TARGET]) == named_mask(plain), "the unrestored pair did not match its names")
    return {
        "named_mask": named,
        "delivered_mask": delivered,
        "literal_k_matches": False,
        "helpers_restored": True,
        "cut_helper_clean": False,
        "plain_matches": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
