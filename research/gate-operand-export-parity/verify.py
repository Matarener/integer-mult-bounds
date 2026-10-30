#!/usr/bin/env python3
"""Gate operand symbolic/export parity at the selected checker/exporter boundary.

Answers PR #3004 open question 2 under the #2977 supplier-boundary cascade:
destination-in-sources gates make accumulate-XOR and sequential ADD disagree,
while destination-free gates always agree. The checker rejects those gates;
the exporter does not. No new kappa.

Admission uses need() and remains active under python -O.
"""

from __future__ import annotations

import copy
import gzip
import hashlib
import itertools
import json
import runpy
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_GATE_OPERAND_EXPORT_PARITY "
    "dest_free_agree=4686 dest_in_disagree_witnesses=2 "
    "selected_distinct_gates=5472 checker_rejects=4 "
    "no_new_kappa"
)
KAPPA_DECIMAL = "0.001672660197076918"
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
PRIOR_README = "research/scatter-parity-contract-audit/README.md"
PRIOR_TASK = "research/scatter-parity-contract-audit/TASK.json"
INPUTS = (WORD, CHECKER, EXPORTER)
# B[0] on the selected word: frame 127, dest 111, sources [3].
B0_FRAME = 127
B0_DEST = 111
B0_SRC = 3


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


def symbolic(d, srcs, val):
    """Accumulate source XOR from the pre-gate valuation, then XOR into d."""
    out = list(val)
    acc = 0
    for s in srcs:
        acc ^= val[s]
    out[d] ^= acc
    return out


def export_seq(d, srcs, val):
    out = list(val)
    for s in srcs:
        out[d] ^= out[s]
    return out


def small_domain_census(n=6, max_len=4):
    """Exhaustive agreement census on n registers and source lists length <= max_len."""
    dest_free_agree = 0
    dest_free_disagree = 0
    dest_in_agree = 0
    dest_in_disagree = 0
    disagree_witnesses = []
    for length in range(0, max_len + 1):
        for srcs in itertools.product(range(n), repeat=length):
            for d in range(n):
                # Formal coefficients over F2.
                def coeffs(op):
                    basis = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
                    if op == "sym":
                        acc = [0] * n
                        for s in srcs:
                            acc = [a ^ b for a, b in zip(acc, basis[s])]
                        return tuple(a ^ b for a, b in zip(basis[d], acc))
                    cur = [row[:] for row in basis]
                    for s in srcs:
                        cur[d] = [a ^ b for a, b in zip(cur[d], cur[s])]
                    return tuple(cur[d])

                agree = coeffs("sym") == coeffs("exp")
                if d not in srcs:
                    if agree:
                        dest_free_agree += 1
                    else:
                        dest_free_disagree += 1
                else:
                    if agree:
                        dest_in_agree += 1
                    else:
                        dest_in_disagree += 1
                        if len(disagree_witnesses) < 8:
                            disagree_witnesses.append([d, list(srcs)])
    return {
        "dest_free_agree": dest_free_agree,
        "dest_free_disagree": dest_free_disagree,
        "dest_in_agree": dest_in_agree,
        "dest_in_disagree": dest_in_disagree,
        "disagree_witnesses": disagree_witnesses,
    }


def named_witnesses():
    """Concrete PROOF.md witnesses with numeric valuations."""
    # self_even: srcs=[d,d]
    val = [7, 3, 5]
    d = 0
    srcs = [0, 0]
    need(symbolic(d, srcs, val) != export_seq(d, srcs, val), "witness self_even")
    need(symbolic(d, srcs, val)[0] == 7, "self_even sym keeps value")
    need(export_seq(d, srcs, val)[0] == 0, "self_even exp clears")
    # dest_with_src: srcs=[a,d]
    val = [7, 3, 5]
    d = 0
    srcs = [1, 0]
    need(symbolic(d, srcs, val) != export_seq(d, srcs, val), "witness dest_with_src")
    need(symbolic(d, srcs, val)[0] == 3, "dest_with_src sym = a")
    need(export_seq(d, srcs, val)[0] == 0, "dest_with_src exp clears")
    # Positive control: d not in srcs, duplicate sources still agree.
    val = [7, 3, 5]
    d = 0
    srcs = [1, 1, 2]
    need(symbolic(d, srcs, val) == export_seq(d, srcs, val), "dest_free dup agrees")
    return {
        "self_even": {"d": 0, "srcs": [0, 0], "val0": [7, 3, 5],
                      "sym": symbolic(0, [0, 0], [7, 3, 5]),
                      "exp": export_seq(0, [0, 0], [7, 3, 5])},
        "dest_with_src": {"d": 0, "srcs": [1, 0], "val0": [7, 3, 5],
                          "sym": symbolic(0, [1, 0], [7, 3, 5]),
                          "exp": export_seq(0, [1, 0], [7, 3, 5])},
        "dest_free_dup": {"d": 0, "srcs": [1, 1, 2], "val0": [7, 3, 5],
                          "sym": symbolic(0, [1, 1, 2], [7, 3, 5]),
                          "exp": export_seq(0, [1, 1, 2], [7, 3, 5])},
    }


def bind_source_lines(pinned):
    checker = pinned[CHECKER].decode("utf-8")
    exporter = pinned[EXPORTER].decode("utf-8")
    prior = pinned[PRIOR_README].decode("utf-8")
    prior_task = pinned[PRIOR_TASK].decode("utf-8")
    need("len(set(regs)) == len(regs)" in checker, "cite: checker distinct operands")
    need("bad operands" in checker, "cite: checker bad-operands message")
    compact = exporter.replace(" ", "")
    need("forsinsrcs:rec.append((1,d,s,1,f,ph))" in compact,
         "cite: exporter one ADD per source occurrence")
    need("forrin[d]+srcs:move(r,f)" in compact,
         "cite: exporter moves each listed operand")
    need("Gate operand lists" in prior, "cite: #3004 OQ2 heading")
    need("no known divergent word exists" in prior, "cite: #3004 no-divergence claim")
    need("Should the schema validator also cover the gate operand lists?" in prior_task,
         "cite: #3004 TASK gate OQ")
    # Scatter contrast remains occurrence vs membership.
    need("if k in row" in exporter, "cite: scatter membership emission")


def load_word(pinned):
    return json.loads(gzip.decompress(pinned[WORD]), object_pairs_hook=pairs_unique)


def selected_gate_census(word):
    total = 0
    distinct = 0
    for name in ("D", "A", "B", "C"):
        for gate in word[name]:
            need(len(gate) == 3, "malformed gate")
            _f, d, srcs = gate
            regs = [d] + list(srcs)
            total += 1
            if len(set(regs)) == len(regs) and srcs:
                distinct += 1
            else:
                need(False, "selected word has non-distinct gate operands")
    need(word["B"][0] == [B0_FRAME, B0_DEST, [B0_SRC]], "B0 fixture anchor")
    return {"gates": total, "distinct_operand_gates": distinct}


def section_sim(word, section, mode):
    n = 2 * word["v"] + word["R"]
    val = [1 << r for r in range(n)]
    for _f, d, srcs in word[section]:
        if mode == "sym":
            val = symbolic(d, srcs, val)
        else:
            val = export_seq(d, srcs, val)
    return val


def make_mutant(word, kind):
    w = copy.deepcopy(word)
    if kind == "self_even":
        w["B"][0] = [B0_FRAME, B0_DEST, [B0_DEST, B0_DEST]]
    elif kind == "dest_with_src":
        w["B"][0] = [B0_FRAME, B0_DEST, [B0_SRC, B0_DEST]]
    elif kind == "dup_src":
        w["B"][0] = [B0_FRAME, B0_DEST, [B0_SRC, B0_SRC]]
    elif kind == "self_once":
        w["B"][0] = [B0_FRAME, B0_DEST, [B0_DEST]]
    else:
        need(False, "unknown mutant")
    return w


def checker_rejects(pinned, word, kinds):
    ns = runpy.run_path(str(ROOT / CHECKER))
    check = ns["check"]
    Reject = ns["Reject"]
    # Baseline must pass.
    check(word)
    rejected = []
    for kind in kinds:
        mutant = make_mutant(word, kind)
        try:
            check(mutant)
            need(False, "checker unexpectedly accepted " + kind)
        except Reject as exc:
            need("bad operands" in str(exc), "reject message: " + kind)
            rejected.append(kind)
        except Exception as exc:  # noqa: BLE001 — surface unexpected failures
            # Some wrappers raise ValueError via need().
            need("bad operands" in str(exc), "reject message: " + kind)
            rejected.append(kind)
    return rejected


def export_record_count(word):
    with tempfile.TemporaryDirectory(prefix="gate-op-export-") as tmp:
        wp = Path(tmp) / "w.json.gz"
        out = Path(tmp) / "out"
        wp.write_bytes(gzip.compress(json.dumps(word, separators=(",", ":")).encode(), mtime=0))
        subprocess.check_call(
            ["python3", "-I", "-B", str(ROOT / EXPORTER), str(wp), str(out)],
            stdout=subprocess.DEVNULL,
            timeout=60,
        )
        raw = (out / "249-records.bin").read_bytes()
        need(len(raw) % 24 == 0, "aligned records")
        return len(raw) // 24


def scatter_only_guard_accepts_self_operand(word):
    """A scatter-uniqueness guard does not inspect gate lists."""
    mutant = make_mutant(word, "self_even")
    rows = mutant["scatter"]
    simple = all(len(row) == len(set(row)) for row in rows)
    need(simple, "selected scatter rows remain simple under gate mutant")
    return simple


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
    census = small_domain_census()
    need(census["dest_free_disagree"] == 0, "dest-free must always agree")
    need(census["dest_free_agree"] == 4686, "dest-free agree count")
    need(census["dest_in_disagree"] > 0, "dest-in must have disagreements")
    witnesses = named_witnesses()
    selected = selected_gate_census(word)
    need(selected["gates"] == 5472, "selected gate count")
    need(selected["distinct_operand_gates"] == 5472, "all selected gates distinct")

    # Section-level Sym/Exp on mutants.
    base_sym = section_sim(word, "B", "sym")
    base_exp = section_sim(word, "B", "exp")
    need(base_sym == base_exp, "baseline B section agrees")

    self_even = make_mutant(word, "self_even")
    need(section_sim(self_even, "B", "sym") != section_sim(self_even, "B", "exp"),
         "self_even section diverges")
    need(section_sim(self_even, "B", "sym")[B0_DEST] != section_sim(self_even, "B", "exp")[B0_DEST],
         "self_even diverges at dest")

    dest_with = make_mutant(word, "dest_with_src")
    need(section_sim(dest_with, "B", "sym") != section_sim(dest_with, "B", "exp"),
         "dest_with_src section diverges")

    dup_src = make_mutant(word, "dup_src")
    need(section_sim(dup_src, "B", "sym") == section_sim(dup_src, "B", "exp"),
         "dup_src dest-free agrees")

    self_once = make_mutant(word, "self_once")
    need(section_sim(self_once, "B", "sym") == section_sim(self_once, "B", "exp"),
         "self_once agrees")

    rejected = checker_rejects(
        pinned, word, ("self_even", "dest_with_src", "dup_src", "self_once"),
    )
    need(len(rejected) == 4, "four checker rejects")

    base_records = export_record_count(word)
    need(base_records == 27234, "selected export record count")
    # Exporter accepts the mutant bytes and emits an extra ADD for the duplicate.
    self_even_records = export_record_count(self_even)
    need(self_even_records == base_records + 1, "exporter emits extra ADD on self_even")

    need(scatter_only_guard_accepts_self_operand(word),
         "scatter-only guard misses gate self-operand")

    selected_result = read_json(ROOT / "certificates/selected-result.json")
    need(selected_result.get("kappa") == "836330098538459/500000000000000000",
         "selected kappa fraction unchanged")

    certificate = {
        "schema_version": 1,
        "status": "PASS_GATE_OPERAND_EXPORT_PARITY",
        "kappa_decimal": KAPPA_DECIMAL,
        "claim": {
            "dest_free_always_agree": True,
            "dest_in_can_disagree": True,
            "small_domain": census,
            "named_witnesses": {
                "self_even": witnesses["self_even"],
                "dest_with_src": witnesses["dest_with_src"],
            },
        },
        "selected_word": {
            "path": WORD,
            "sha256": hashlib.sha256(pinned[WORD]).hexdigest(),
            "gates": selected["gates"],
            "distinct_operand_gates": selected["distinct_operand_gates"],
            "B0": [B0_FRAME, B0_DEST, [B0_SRC]],
            "export_records": base_records,
        },
        "controls": {
            "checker_rejects": rejected,
            "self_even_export_records": self_even_records,
            "scatter_only_guard_misses_gate_self_operand": True,
            "dup_src_section_agrees": True,
            "self_once_section_agrees": True,
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
    need(certificate["status"] == "PASS_GATE_OPERAND_EXPORT_PARITY", "status")
    print(MARKER)


if __name__ == "__main__":
    main()
