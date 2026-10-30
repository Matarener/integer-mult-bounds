#!/usr/bin/env python3
"""D-internal cross-term tally for the retained R439 helper-star K defect.

On each pinned word, K is the helper-column mask that the frame-free replay of
(A, scatter, B) leaves on each target. N is the syntactic XOR of register ids
named by D-gates that write that target. E is the helper-column mask actually
xored into the target when D is executed alone from identity columns.

The cross-term tally is C = E XOR (N restricted to helper columns). It also
equals the per-gate XOR of (delivered helper columns XOR named helper columns).
The K_equals_D defect is K XOR (N restricted to helper columns). Those two
masks agree on a target exactly when E = K.

This script checks that agreement on the three words named by PR #4092, agrees
with the owner checker that the syntactic flag is false, and rejects two
controls: deleting one helper-to-helper gate, and a synthetic restored edge
whose raw word is empty.
"""
import gzip
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
WORDS = (
    ("helper_star", "research/r439-helper-stars-seed19/candidate.json.gz"),
    ("composition", "research/r439-bsection-stars-seed01/composition.json.gz"),
    ("candidate", "research/r439-bsection-stars-seed01/candidate.json.gz"),
)
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"


def fail(message):
    raise SystemExit("FAIL_R439_K_CROSS_TERM_TALLY " + message)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_word(path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        word = json.load(handle)
    if not isinstance(word, dict) or "D" not in word or "v" not in word:
        fail("word is not a D-section object: " + path)
    return word


def helper_mask(word):
    return ((1 << word["R"]) - 1) << (2 * word["v"])


def syntactic_N(word):
    """Register-id mask named by D-gates that write each target."""
    width = word["v"]
    named = [0] * width
    for _frame, dest, srcs in word["D"]:
        if width <= dest < 2 * width:
            acc = 0
            for src in srcs:
                acc ^= 1 << src
            named[dest - width] ^= acc
    return named


def raw_K(word):
    """Helper columns on each target after (A, scatter, B), frames off."""
    width, helpers = word["v"], word["R"]
    columns = 2 * width + helpers
    mask = helper_mask(word)
    val = [1 << reg for reg in range(columns)]
    for name in ("A", "scatter", "B"):
        if name == "scatter":
            copies = [val[reg] for reg in word["ret"]]
            for target, row in enumerate(word["scatter"]):
                acc = 0
                for index in row:
                    acc ^= copies[index]
                val[width + target] ^= acc
        else:
            for _frame, dest, srcs in word[name]:
                acc = 0
                for src in srcs:
                    acc ^= val[src]
                val[dest] ^= acc
    return [val[width + target] & mask for target in range(width)]


def executed_D(word):
    """Execute D from identity columns.

    Returns E, the per-gate cross tally, and whether every helper register is
    back to its own column. E XOR (syntactic helper mask) equals the cross
    tally for any D section; that identity is checked by the caller.
    """
    width, helpers = word["v"], word["R"]
    columns = 2 * width + helpers
    mask = helper_mask(word)
    val = [1 << reg for reg in range(columns)]
    delivered = [0] * width
    cross = [0] * width
    for _frame, dest, srcs in word["D"]:
        acc = 0
        for src in srcs:
            acc ^= val[src]
        if width <= dest < 2 * width:
            named_helper = 0
            for src in srcs:
                if src >= 2 * width:
                    named_helper ^= 1 << src
            got = acc & mask
            delivered[dest - width] ^= got
            cross[dest - width] ^= got ^ named_helper
        val[dest] ^= acc
    restored = all(val[reg] == (1 << reg) for reg in range(2 * width, columns))
    return delivered, cross, restored


def popcount(mask):
    return bin(mask).count("1")


def sector_counts(masks, width):
    seen = set()
    for mask in masks:
        bit = 0
        while mask:
            if mask & 1:
                seen.add(bit - 2 * width)
            mask >>= 1
            bit += 1
    return len(seen)


def first_helper_edge(word):
    width = word["v"]
    for index, (_frame, dest, srcs) in enumerate(word["D"]):
        if dest >= 2 * width and srcs and all(src >= 2 * width for src in srcs):
            return index
    return None


def without_gate(word, index):
    clone = dict(word)
    clone["D"] = list(word["D"])
    del clone["D"][index]
    return clone


def synthetic_restored_edge():
    """h0 ^= h1; y ^= h0; h0 ^= h1, with an empty raw word.

    Executed delivery is h0 XOR h1. The syntactic mask names only h0. The raw
    helper part is 0, so the defect is not the cross term.
    """
    return {
        "v": 1,
        "R": 2,
        "D": [[0, 2, [3]], [0, 1, [2]], [0, 2, [3]]],
        "A": [],
        "B": [],
        "scatter": [[]],
        "ret": [2],
    }


def pin_inputs():
    with open(os.path.join(HERE, "SOURCES.json"), encoding="utf-8") as handle:
        rows = json.load(handle)["files"]
    for row in rows:
        if row["usage"] != "input":
            continue
        path = os.path.join(ROOT, row["path"])
        digest = sha256(path)
        if digest != row["sha256"]:
            fail("sha256 mismatch for " + row["path"])


def load_checker():
    path = os.path.join(ROOT, CHECKER)
    spec = importlib.util.spec_from_file_location("xcheck_p_pinned", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checker_raw_K(module, word):
    width = word["v"]
    mask = helper_mask(word)
    raw, _cur, _stats = module.Word(word).replay(
        sections=("A", "scatter", "B"), frames_on=False)
    return [raw[width + target] & mask for target in range(width)]


def main():
    pin_inputs()
    checker = load_checker()
    summaries = []
    for name, relative in WORDS:
        word = load_word(os.path.join(ROOT, relative))
        width = word["v"]
        mask = helper_mask(word)
        named = syntactic_N(word)
        helper_named = [row & mask for row in named]
        observed = raw_K(word)
        delivered, cross, restored = executed_D(word)
        if not restored:
            fail(name + " does not restore helpers at the end of D")
        if checker_raw_K(checker, word) != observed:
            fail(name + " raw helper part disagrees with the owner checker")
        _hypotheses, conclusion, _info = checker.Word(word).interface()
        if conclusion["K_equals_D"]:
            fail(name + " syntactic K_equals_D is true; the defect premise failed")
        for target in range(width):
            identity = delivered[target] ^ helper_named[target]
            defect = observed[target] ^ helper_named[target]
            if identity != cross[target]:
                fail(name + " cross tally is not E XOR syntactic helper mask")
            if delivered[target] != observed[target] or defect != cross[target]:
                fail(name + " target %d defect is not the cross tally" % target)
        edge = first_helper_edge(word)
        if edge is None:
            fail(name + " has no helper-to-helper gate to delete")
        mutated, _mut_cross, _mut_restored = executed_D(without_gate(word, edge))
        if mutated == observed:
            fail(name + " still matches K after deleting one helper edge")
        bits = sum(popcount(row ^ helper_named[target]) for target, row in enumerate(observed))
        summaries.append((name, width, bits, sector_counts(
            [observed[t] ^ helper_named[t] for t in range(width)], width)))

    synthetic = synthetic_restored_edge()
    syn_named = [row & helper_mask(synthetic) for row in syntactic_N(synthetic)]
    syn_K = raw_K(synthetic)
    syn_E, syn_cross, syn_restored = executed_D(synthetic)
    if not syn_restored or syn_K != [0]:
        fail("synthetic restored edge is not an empty-raw restored helper")
    if syn_E[0] ^ syn_named[0] != syn_cross[0]:
        fail("synthetic cross identity failed")
    if syn_cross[0] == 0 or syn_K[0] ^ syn_named[0] == syn_cross[0]:
        fail("synthetic edge did not separate the defect from the cross term")

    bits = "/".join(str(item[2]) for item in summaries)
    sectors = "/".join(str(item[3]) for item in summaries)
    targets = "/".join(str(item[1]) for item in summaries)
    print(
        "PASS_R439_K_CROSS_TERM_TALLY words=3 targets=%s equal_targets=%s "
        "defect_bits=%s cross_bits=%s sectors=%s helpers_restored=3/3 "
        "checker_K_equals_D=false/false/false mutation_breaks=3/3 "
        "synthetic_unequal=1 no_new_kappa" % (targets, targets, bits, bits, sectors))


if __name__ == "__main__":
    main()
