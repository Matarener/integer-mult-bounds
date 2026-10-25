#!/usr/bin/env python3
"""Source-bound replay of a fixed signed lift, without repeating its search.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class Frozen:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.hashes = json.loads((self.root / "FROZEN-SHA256.json").read_bytes())
        self.executed = {}
        self.compared = set()

    def raw(self, name):
        need(name in self.hashes, "unregistered frozen input: " + name)
        data = (self.root / name).read_bytes()
        need(hashlib.sha256(data).hexdigest() == self.hashes[name],
             "frozen input changed: " + name)
        return data

    def decoded(self, name):
        data = self.raw(name)
        return gzip.decompress(data) if data.startswith(b"\x1f\x8b") else data

    def data(self, name):
        return json.loads(self.decoded(name))

    def check_all(self):
        for name in self.hashes:
            self.raw(name)
        origins = json.loads((self.root / "ORIGINS.json").read_bytes())
        for name, row in origins.items():
            if "original_sha256" in row:
                need(hashlib.sha256(self.decoded(name)).hexdigest() == row["original_sha256"],
                     "compressed original bytes changed: " + name)

    def functions(self, name, names, globals_):
        """Compile only named original definitions from authenticated bytes."""
        tree = ast.parse(self.raw(name), filename=str(self.root / name))
        nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
        need(Counter(n.name for n in nodes) == Counter(names), "function selection changed")
        code = compile(ast.Module(body=nodes, type_ignores=[]), str(self.root / name),
                       "exec", dont_inherit=True, optimize=0)
        namespace = dict(globals_)
        exec(code, namespace)
        self.executed[name] = list(names)
        return SimpleNamespace(**{name: namespace[name] for name in names})

    def compare(self, name, value):
        need(canonical(value) == canonical(self.data(name)), "complete receipt mismatch: " + name)
        self.compared.add(name)

    def module(self, name):
        namespace = {"__name__": "authenticated_review", "__file__": str(self.root / name)}
        code = compile(self.raw(name), str(self.root / name), "exec",
                       dont_inherit=True, optimize=0)
        exec(code, namespace)
        self.executed[name] = ["complete independent checker"]
        return namespace


def retained_functions(frozen):
    cap = frozen.functions("frozen/old/bit_cap_copy_local.py", ["need", "canonical", "rank"],
                           {"json": json, "Q": Fraction})
    scalar = frozen.functions(
        "frozen/old/bit_signed_audit.py",
        ["identity", "add", "row_weights", "parity", "block_norms", "code", "global_bound"],
        {"N": 660, "V": 111, "need": need, "Counter": Counter})
    prune = frozen.functions("frozen/old/bit_prune_audit.py", ["execute"],
                             {"need": need, "cap": cap, "scalar": scalar, "Counter": Counter})
    growth = frozen.functions("frozen/old/bit_pruned_growth.py", ["coefficients"],
                              {"scalar": scalar})
    scoring = frozen.functions("frozen/old/signed_quotient_search.py", ["score"], {})
    return cap, scalar, prune, growth, scoring


def historical(frozen):
    cap, scalar, prune, growth, scoring = retained_functions(frozen)
    parent = frozen.data("frozen/parent/WORD.json.gz")
    candidate = frozen.data("frozen/candidate/WORD.json.gz")
    raw = frozen.data("frozen/geometry/WORD.json.gz")
    baseline, records = parent["records"], candidate["records"]
    need(len(records) == len(baseline) == 16102, "complete literal word length")
    positions = [i for i, r in enumerate(baseline) if r[0] == 1 and r[5] == 23]
    need(len(positions) == 47 and all(baseline[i][3] == 1 for i in positions),
         "fixed binary quotient alphabet")
    signs = [records[i][3] for i in positions]
    need(all(c in (-1, 1) for c in signs) and signs.count(-1) == 23,
         "fixed signed witness")
    changed = [r[:] for r in baseline]
    for i, c in zip(positions, signs):
        changed[i][3] = c
    need(candidate == dict(parent, format="coded-r429-signed-quotient-variant-v1",
                           records=changed), "change outside declared quotient signs")
    pivots = sorted({baseline[i][j] for i in positions for j in (1, 2)})
    need(len(pivots) == 9, "quotient register count")
    index = {p: i for i, p in enumerate(pivots)}
    gates = [(index[baseline[i][1]], index[baseline[i][2]]) for i in positions]
    keep = [i for i in range(660) if i not in range(471, 480)]
    need(parent["start"] == [raw["start"][i] for i in keep]
         and parent["final"] == [raw["final"][i] for i in keep], "physical boundary binding")
    forward, fs = prune.execute(raw, keep, records)
    inverse, rs = prune.execute(raw, keep, records, True)
    roundtrip, _ = prune.execute(raw, keep, records, True, forward)
    need(roundtrip == scalar.identity(651), "full signed integer roundtrip")
    oldforward, oldfs = prune.execute(raw, keep, baseline)
    oldinverse, oldrs = prune.execute(raw, keep, baseline, True)
    need(scalar.parity(forward) == scalar.parity(oldforward)
         and scalar.parity(inverse) == scalar.parity(oldinverse),
         "complete binary endpoints changed")
    need(all(forward[i] == inverse[i] == {i: 1} for i in range(222, 651)),
         "arbitrary integer helper restoration")
    receipt = {
        "status": "PASS_LOCAL_INTEGER_SIGN_VARIANT_SAME_F2_AND_RANK_NO_PRECISION_ADMISSION",
        "parent_sha256": hashlib.sha256(frozen.raw("frozen/parent/WORD.json.gz")).hexdigest(),
        "word_sha256": hashlib.sha256(frozen.raw("frozen/candidate/WORD.json.gz")).hexdigest(),
        "word_canonical_sha256": hashlib.sha256(frozen.decoded("frozen/candidate/WORD.json.gz")).hexdigest(),
        "original_small_score": list(scoring.score(gates, [1] * 47)),
        "new_small_score": list(scoring.score(gates, signs)),
        "quotient_signs": signs, "changed_gates": 23, "forward": fs, "inverse": rs,
        "scope": "47fixedbinaryquotientgates only; all651integer/F2columns andhelpers. Notthepublishedword; no globalprecision/stock/controller/tape or kappa.",
    }
    # JSON converts histogram integer keys in the original returned value.
    receipt = json.loads(json.dumps(receipt))
    frozen.compare("frozen/candidate/RESULT.json", receipt)
    ordered = frozen.data("frozen/controller/WORD.json.gz")["ordered_controller"]
    bounds = {}
    for label, word, pair in (("parent", parent, [oldfs, oldrs]),
                              ("candidate", candidate, [fs, rs])):
        rows, maxima, envelopes = [], [], []
        for backward in (False, True):
            result, maximum, envelope = growth.coefficients(word["records"], backward)
            rows.append(result)
            maxima.append(maximum)
            envelopes.append(envelope)
        need(maxima == [r["prefix_row_l1"] for r in pair], "two retained prefix calculations disagree")
        code_records, code_rows, code_prefix, code_norm = scalar.code(word["records"])
        need(len(code_records) == 1499 and rows[0][:111] == code_rows[0]
             and rows[1][:111] == code_rows[1], "selected source-code interface")
        bound = scalar.global_bound(
            ordered, [scalar.block_norms(a) for a in rows], maxima, envelopes,
            code_prefix, code_norm)
        bounds[label] = {
            "local_prefix": maxima, "code_prefix": code_prefix, "code_endpoint_norm": code_norm,
            "whole_controller": bound,
            "terminal_64_bit_reserve": 64 * ((bound["after_easy_completed_bank_decode_upper_bits"] + 63) // 64),
        }
    signed_growth = {
        "status": "NORMALIZED_SIGN_VARIANT_GROWTH_ONLY_NO_NATIVE_CHILD_ERROR_ADMISSION",
        "word_canonical_sha256": receipt["word_canonical_sha256"],
        **{k: bounds["candidate"][k] for k in
           ("local_prefix", "code_prefix", "code_endpoint_norm", "whole_controller")},
    }
    frozen.compare("frozen/candidate/GROWTH.json", signed_growth)
    return {
        "status": "PASS_FIXED_SIGNED_WITNESS_AND_NORMALIZED_RANGE",
        "baseline": bounds["parent"], "candidate": bounds["candidate"],
        "full_signed_receipts_compared": sorted(frozen.compared),
        "executed_original_functions": frozen.executed,
        "search_repeated": False,
        "controller_contract": "Instantiate each abstract ordered code sweep with this word's actual 1499 source ADDs or their literal inverse; legacy inplace_code_CNOTs are not the selected integer code.",
        "no_precision_admission": True,
    }


def independent(frozen, stage):
    names = {
        "integer": ("frozen/reviews/integer/check_integer.py",
                    "frozen/reviews/integer/CHECKS.json.gz"),
        "range": ("frozen/reviews/range/check_range.py",
                  "frozen/reviews/range/CHECKS.json.gz"),
    }
    source, receipt = names[stage]
    module = frozen.module(source)
    old_argv = sys.argv
    with tempfile.TemporaryDirectory(prefix="signed R429 check ") as tmp:
        output = Path(tmp) / "fresh.json"
        sys.argv = [str(frozen.root / source),
                    "--parent-word", str(frozen.root / "frozen/parent/WORD.json.gz")]
        if stage == "integer":
            sys.argv += [
                "--signed-word", str(frozen.root / "frozen/candidate/WORD.json.gz"),
                "--raw-word", str(frozen.root / "frozen/geometry/WORD.json.gz"),
                "--matrices", str(frozen.root / "frozen/geometry/MATRICES.json.gz"),
                "--out", str(output)]
        else:
            sys.argv += [
                "--candidate-word", str(frozen.root / "frozen/candidate/WORD.json.gz"),
                "--controller", str(frozen.root / "frozen/controller/WORD.json.gz"),
                "--output", str(output)]
        try:
            module["main"]()
            frozen.compare(receipt, json.loads(output.read_bytes()))
        finally:
            sys.argv = old_argv
    return {"status": "PASS_INDEPENDENT_SIGNED_R429_" + stage.upper(),
            "complete_receipt": receipt, "no_precision_admission": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["historical", "integer", "range"], required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    frozen = Frozen(Path(__file__).resolve().parent)
    frozen.check_all()
    if args.stage == "historical":
        result = historical(frozen)
        frozen.compare("frozen/historical/REPLAY.json", result)
        expected_receipts = {"frozen/candidate/RESULT.json", "frozen/candidate/GROWTH.json",
                             "frozen/historical/REPLAY.json"}
    else:
        result = independent(frozen, args.stage)
        expected_receipts = {result["complete_receipt"]}
    need(frozen.compared == expected_receipts, "incomplete receipt coverage")
    frozen.check_all()
    if args.output:
        need(not args.output.resolve().is_relative_to(frozen.root), "output must be external")
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(canonical(result))


if __name__ == "__main__":
    main()
