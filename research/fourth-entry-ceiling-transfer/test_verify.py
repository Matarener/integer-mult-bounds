#!/usr/bin/env python3.12
"""Behavioural controls for verify.py: each must make the audit reject."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import verify as V  # noqa: E402


def expect_false(name, value):
    if value:
        print("CONTROL_FAILED (control did not reject): " + name)
        return 1
    print("control rejects as expected: " + name)
    return 0


def main():
    rc = 0
    with open(os.path.join(V.CEIL, "RESULT.json"), encoding="utf-8") as fh:
        ceil_res = json.load(fh)
    with open(os.path.join(V.MIX4, "RESULT.json"), encoding="utf-8") as fh:
        mix_res = json.load(fh)

    # 1. A paid profile with 100 extra rank-1 children breaks the word law.
    bad = dict(ceil_res["complete_profile"])
    bad["1"] += 100
    rc |= expect_false(
        "extra_rank1_breaks_word_law",
        V.derive_x(bad, ceil_res["idle"])["x_consistent"])

    # 2. A wrong stock divisor moves the recomputed root out of the bracket.
    from decimal import Decimal
    prof_pool = {int(k): v
                 for k, v in ceil_res["complete_profile"].items()}
    good_root = V.solve_root(prof_pool)
    saved = V.STOCK_W
    V.STOCK_W = saved + 1
    shifted = V.solve_root(prof_pool)
    V.STOCK_W = saved
    lo = Decimal(ceil_res["root_decimal_bracket"][0])
    hi = Decimal(ceil_res["root_decimal_bracket"][1])
    rc |= expect_false("wrong_stock_moves_root_out_of_bracket",
                      lo <= shifted <= hi)

    # 3. A tampered word delta breaks the derived-L4 cross-check.
    saved_w4 = dict(V.WORDS4)
    V.WORDS4[3] += 1
    anchors = V.check_word_anchors()
    V.WORDS4.clear()
    V.WORDS4.update(saved_w4)
    rc |= expect_false("tampered_word_delta_breaks_anchor",
                      anchors["derived_L4_matches"])

    # 4. A corrupted word-file payload fails byte equivalence.
    name = "FOUR-base.json.gz"
    import gzip
    with open(os.path.join(V.CEIL, "source4088", "inputs", name),
              "rb") as fh:
        old = gzip.decompress(fh.read())
    corrupted = old[:-1] + bytes([old[-1] ^ 1])
    rc |= expect_false("corrupted_word_payload_detected",
                      V.sha(old) == V.sha(corrupted))

    # 5. A shifted idle total breaks the constant-residual cross-check.
    bad_idle = dict(mix_res["idle"])
    bad_idle["48"] = bad_idle["48"] - 1
    with open(os.path.join(V.MIX4, "TASK.json"), encoding="utf-8") as fh:
        text = fh.read()
    bins = V.check_bins(ceil_res, {"raw": text, "idle": bad_idle})
    rc |= expect_false("shifted_idle_total_rejected",
                      bins["idle_total_constant"])

    if rc == 0:
        print("PASS_ALL_CONTROLS")
    return rc


if __name__ == "__main__":
    sys.exit(main())
