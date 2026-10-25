#!/usr/bin/env python3
"""Length-≤2 dest-in divergence census for the four #3696 B[0] rejects.

Answers #3696 OQ2: the four selected-word checker rejects are not exhaustive
for dest-in-sources divergence on the pinned word. Proves a dest-in closed
form, enumerates exactly 661 length-≤2 divergences at B[0]'s destination, and
shows only two of the four named rejects lie in that set. No new kappa.

Admission uses need() and remains active under python -O.
"""

from __future__ import annotations

import copy
import gzip
import hashlib
import itertools
import json
import runpy
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_SELECTED_WORD_REJECT_EXHAUSTION "
    "len2_divergences=661 named_diverge=2 "
    "four_exhaustive=false no_new_kappa"
)
KAPPA_DECIMAL = "0.001672660197076918"
KAPPA_FRAC = "836330098538459/500000000000000000"
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
INPUTS = (WORD, CHECKER)
B0_FRAME = 127
B0_DEST = 111
B0_SRC = 3
N_REGS = 661
LEN2_DIVERGENCES = 661
NAMED = ("self_even", "dest_with_src", "dup_src", "self_once")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def read_json(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 4_000_000, "input exceeds 4 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    need(manifest["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
         "base commit pin")
    rows = manifest["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    pinned = {}
    for row in rows:
        path = ROOT / row["path"]
        raw = path.read_bytes()
        need(len(raw) == row["size_bytes"], "source size: " + row["path"])
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == row["sha256"], "source hash: " + row["path"])
        pinned[row["path"]] = raw
    return pinned


def sym_coeffs(d, srcs, n):
    coeff = [0] * n
    coeff[d] = 1
    for s in srcs:
        coeff[s] ^= 1
    return tuple(coeff)


def exp_coeffs(d, srcs, n):
    coeff = [0] * n
    coeff[d] = 1
    for s in srcs:
        if s == d:
            coeff = [0] * n
        else:
            coeff[s] ^= 1
    return tuple(coeff)


def agree(d, srcs, n):
    return sym_coeffs(d, srcs, n) == exp_coeffs(d, srcs, n)


def closed_form_agree(d, srcs):
    """Dest-in closed form; dest-free always True."""
    if d not in srcs:
        return True
    last = max(i for i, s in enumerate(srcs) if s == d)
    if srcs.count(d) % 2 == 0:
        return False
    for s, count in Counter(srcs[:last]).items():
        if s != d and count % 2:
            return False
    return True


def make_mutant_srcs(kind):
    if kind == "self_even":
        return [B0_DEST, B0_DEST]
    if kind == "dest_with_src":
        return [B0_SRC, B0_DEST]
    if kind == "dup_src":
        return [B0_SRC, B0_SRC]
    if kind == "self_once":
        return [B0_DEST]
    need(False, "unknown mutant " + kind)
    return []


def length2_census(d, n):
    """Enumerate all srcs of length ≤2; return divergence list and agree count."""
    divergences = []
    dest_in_agree = 0
    dest_free = 0
    for length in range(0, 3):
        for srcs in itertools.product(range(n), repeat=length):
            need(agree(d, srcs, n) == closed_form_agree(d, srcs),
                 "closed form mismatch")
            if d not in srcs:
                need(agree(d, srcs, n), "dest-free must agree")
                dest_free += 1
            elif agree(d, srcs, n):
                dest_in_agree += 1
            else:
                divergences.append(list(srcs))
    return {
        "divergences": divergences,
        "dest_in_agree": dest_in_agree,
        "dest_free": dest_free,
        "total_lists": dest_free + dest_in_agree + len(divergences),
    }


def expected_divergences(d, n):
    # Length-2 product order: every [a, d] for a in range(n), including [d, d].
    return [[a, d] for a in range(n)]


def bind_source_lines(pinned):
    checker = pinned[CHECKER].decode("utf-8")
    need("len(set(regs)) == len(regs)" in checker, "cite: checker distinct operands")
    need("bad operands" in checker, "cite: checker bad-operands message")


def load_word(pinned):
    return json.loads(gzip.decompress(pinned[WORD]), object_pairs_hook=pairs_unique)


def selected_anchor(word):
    need(word["v"] == 111, "v pin")
    need(word["R"] == 439, "R pin")
    need(2 * word["v"] + word["R"] == N_REGS, "register count")
    need(word["B"][0] == [B0_FRAME, B0_DEST, [B0_SRC]], "B0 fixture")
    gates = 0
    for name in ("D", "A", "B", "C"):
        for gate in word[name]:
            _f, d, srcs = gate
            regs = [d] + list(srcs)
            need(len(set(regs)) == len(regs), "selected gate non-distinct")
            need(d not in srcs, "selected gate dest-in")
            gates += 1
    need(gates == 5472, "selected gate count")
    return gates


def checker_rejects_kinds(word, kinds):
    ns = runpy.run_path(str(ROOT / CHECKER))
    check = ns["check"]
    Reject = ns["Reject"]
    check(word)
    rejected = []
    for kind in kinds:
        mutant = copy.deepcopy(word)
        mutant["B"][0] = [B0_FRAME, B0_DEST, make_mutant_srcs(kind)]
        try:
            check(mutant)
            need(False, "checker accepted " + kind)
        except Reject as exc:
            need("bad operands" in str(exc), "reject message: " + kind)
            rejected.append(kind)
        except Exception as exc:  # noqa: BLE001
            need("bad operands" in str(exc), "reject message: " + kind)
            rejected.append(kind)
    return rejected


def checker_rejects_srcs(word, srcs_list):
    ns = runpy.run_path(str(ROOT / CHECKER))
    check = ns["check"]
    Reject = ns["Reject"]
    for srcs in srcs_list:
        mutant = copy.deepcopy(word)
        mutant["B"][0] = [B0_FRAME, B0_DEST, list(srcs)]
        try:
            check(mutant)
            need(False, "checker accepted " + str(srcs))
        except Reject as exc:
            need("bad operands" in str(exc), "reject message: " + str(srcs))
        except Exception as exc:  # noqa: BLE001
            need("bad operands" in str(exc), "reject message: " + str(srcs))


def small_domain_closed_form(n=8, max_len=5):
    mismatches = 0
    for length in range(0, max_len + 1):
        for srcs in itertools.product(range(n), repeat=length):
            for d in range(n):
                if agree(d, srcs, n) != closed_form_agree(d, srcs):
                    mismatches += 1
    need(mismatches == 0, "small-domain closed form mismatches")
    return {"n": n, "max_len": max_len, "mismatches": mismatches}


def admit_certificate(certificate, write=False):
    path = HERE / "CERTIFICATE.json"
    if write:
        path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        return
    need(path.is_file(), "missing CERTIFICATE.json")
    committed = read_json(path)
    need(committed == certificate, "certificate mismatch")


def evaluate(write=False):
    pinned = pin_sources()
    bind_source_lines(pinned)
    word = load_word(pinned)
    gates = selected_anchor(word)

    small = small_domain_closed_form()
    census = length2_census(B0_DEST, N_REGS)
    expected = expected_divergences(B0_DEST, N_REGS)
    need(len(census["divergences"]) == LEN2_DIVERGENCES, "divergence count")
    need(census["divergences"] == expected, "divergence set")
    need(census["dest_in_agree"] == LEN2_DIVERGENCES, "dest-in agree count")
    need(census["total_lists"] == 1 + N_REGS + N_REGS * N_REGS, "total lists")

    named_status = {}
    named_diverge = []
    named_agree = []
    for kind in NAMED:
        srcs = make_mutant_srcs(kind)
        diverges = not closed_form_agree(B0_DEST, srcs)
        need(diverges == (not agree(B0_DEST, srcs, N_REGS)), "named closed form")
        bad = len(set([B0_DEST] + srcs)) != len([B0_DEST] + srcs)
        need(bad, "named must be bad operands")
        named_status[kind] = {
            "srcs": srcs,
            "diverges": diverges,
            "in_len2_divergence_set": srcs in census["divergences"],
        }
        if diverges:
            named_diverge.append(kind)
        else:
            named_agree.append(kind)
    need(named_diverge == ["self_even", "dest_with_src"], "named diverge pair")
    need(named_agree == ["dup_src", "self_once"], "named agree pair")
    four_exhaustive = len(named_diverge) == LEN2_DIVERGENCES
    need(four_exhaustive is False, "four must not be exhaustive")

    # Distinctness catches every length-≤2 divergence (algebraic, plus spot checks).
    for srcs in census["divergences"]:
        need(B0_DEST in srcs, "divergence must be dest-in")
        need(len(set([B0_DEST] + srcs)) < len([B0_DEST] + srcs),
             "divergence must fail distinctness")
    rejected = checker_rejects_kinds(word, NAMED)
    need(rejected == list(NAMED), "four checker rejects")
    spot = [[B0_DEST, B0_DEST], [0, B0_DEST], [N_REGS - 1, B0_DEST], [B0_SRC, B0_DEST]]
    checker_rejects_srcs(word, spot)

    selected_result = read_json(ROOT / "certificates/selected-result.json")
    need(selected_result.get("kappa") == KAPPA_FRAC, "selected kappa fraction")
    need(selected_result.get("decimal") == KAPPA_DECIMAL, "selected kappa decimal")

    certificate = {
        "schema_version": 1,
        "status": "PASS_SELECTED_WORD_REJECT_EXHAUSTION",
        "kappa_decimal": KAPPA_DECIMAL,
        "claim": {
            "closed_form": (
                "agree iff d not in srcs, or count(d) odd and every non-d "
                "has even multiplicity before the last d"
            ),
            "small_domain_closed_form": small,
            "length2": {
                "destination": B0_DEST,
                "n_registers": N_REGS,
                "divergences": LEN2_DIVERGENCES,
                "dest_in_agree": census["dest_in_agree"],
                "dest_free": census["dest_free"],
                "total_lists": census["total_lists"],
                "form": "[[d,d]] U [[a,d] : a != d]",
            },
            "named_rejects": named_status,
            "named_diverge_count": len(named_diverge),
            "four_exhaustive_for_len2_divergence": False,
        },
        "selected_word": {
            "path": WORD,
            "sha256": hashlib.sha256(pinned[WORD]).hexdigest(),
            "gates": gates,
            "B0": [B0_FRAME, B0_DEST, [B0_SRC]],
            "n_registers": N_REGS,
        },
        "controls": {
            "checker_rejects": rejected,
            "checker_spot_divergences": spot,
            "all_len2_divergences_fail_distinctness": True,
        },
        "no_new_kappa": True,
    }
    admit_certificate(certificate, write=write)
    return certificate


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate CERTIFICATE.json (explicit write path only)",
    )
    args = parser.parse_args(argv)
    certificate = evaluate(write=args.write)
    need(certificate["status"] == "PASS_SELECTED_WORD_REJECT_EXHAUSTION", "status")
    print(MARKER)


if __name__ == "__main__":
    main()
