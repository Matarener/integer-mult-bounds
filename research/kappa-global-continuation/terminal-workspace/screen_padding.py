#!/usr/bin/env python3
"""Exact price receipts for whole-replica padding after the m81 boundary screen.

Appending W rank-d children cannot repair an already failing positive-exponent
invoice. The finite receipts illustrate a concavity proof valid for every d>0.
Apache-2.0; substantial OpenAI assistance under the user's direction.
"""
from collections import Counter
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CONT = HERE.parent
SCRIPT = CONT / "invoice-analysis/invoice.py"
RECEIPT = CONT / "invoice-analysis/evidence/RESULT.json"


def main():
    spec = importlib.util.spec_from_file_location("padding_invoice", SCRIPT)
    inv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inv)
    source = inv.read(RECEIPT)
    inv.need(source["script_sha256"] == inv.digest(SCRIPT), "frozen invoice script binding")
    inv.need(source["arithmetic_engine_sha256"] == inv.digest(inv.ENGINE_PATH), "exact arithmetic engine binding")
    inv.need(0 < inv.TARGET < 1, "strict concavity exponent range")
    families = {}
    for key in ("boundary_family", "rational_eight_port_boundary_family"):
        old = source[key]["cases"]["81"]
        productive = old["productive_per_replica"]
        base = {int(r): F(n) for r, n in old["optimistic_profile"].items()}
        tariffs = {}
        for label, rank, count in (("72_H8", 8, 72), ("8_H72", 72, 8)):
            profile = Counter(base)
            profile[rank] += count
            original = inv.moment(profile, 81, productive, inv.TARGET)
            inv.need(original[0] > 1, "strict m81 rejection needed for universal padding proof")
            cases = []
            for padding in range(1, 65):
                changed = Counter(profile)
                changed[padding] += productive
                dimension = 81 + padding
                got = inv.moment(changed, dimension, productive, inv.TARGET)
                inv.need(got[0] > 1, "whole-bank padding cannot rescue the price")
                inv.need(sum(r*n for r, n in changed.items()) == dimension*productive-320,
                         "all padding children charged exactly; no denominator-only gain")
                cases.append({"padding": padding, "dimension": dimension,
                              "added_children": {str(padding): productive},
                              "target_residual": inv.interval(got[0]-1, got[1]-1)})
            tariffs[label] = {"m81_target_residual": inv.interval(original[0]-1, original[1]-1),
                              "all_positive_padding_rejected": True, "cases_1_through_64": cases}
        families[key] = {"productive_per_replica": productive,
                         "maximum_inherited_idle_rank": 57,
                         "tariffs": tariffs}
    result = {"status": "PASS_EXACT_WHOLE_REPLICA_PADDING_REJECTION",
              "script_sha256": inv.digest(Path(__file__)),
              "invoice_receipt_sha256": inv.digest(RECEIPT),
              "target": str(inv.TARGET), "families": families,
              "proof": {
                  "notation": "p=1-a in(0,1), m0=81, A=(sum_r n_r*r^p)/W. The source-bound m81 failure proves A>m0^p.",
                  "new_moment": "(A+d^p)/(m0+d)^p after adding exactly W rank-d children and increasing ambient dimension to m0+d.",
                  "strict_concavity": "For m0,d>0 and0<p<1, (m0+d)^p<m0^p+d^p<A+d^p. Hence the new moment is greater than1 for every positive real d, including all positive integer padding dimensions.",
                  "scope": "The existing m81 profile and consumer tariff are retained; added common padding requires W rank-d children. Native gauge eligibility is granted and the original idle mass remains priced optimistically at rank57. This excludes this padding family only, not a redesigned supplier, consumer, or idle geometry."}}
    out = HERE / "PADDING-SCREEN.json"
    out.write_text(json.dumps(result, indent=2)+"\n")
    print(result["status"])
    print("All256 finite cases reject at the target; concavity proves rejection for every positive padding dimension.")


if __name__ == "__main__":
    main()
