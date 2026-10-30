# SPDX-License-Identifier: Apache-2.0
"""Negative controls: tampered budgets or histograms must be rejected by the independent method."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

PKG = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("independent", PKG / "independent.py")
independent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(independent)
RESULT = json.loads((PKG / "RESULT.json").read_text(encoding="utf-8"))


def tampered(edit):
    res = copy.deepcopy(RESULT)
    edit(res)
    return res


class Package(unittest.TestCase):
    def test_result_reproduced(self):
        independent.main(copy.deepcopy(RESULT))

    def test_rejections(self):
        edits = {
            "one copy fewer than the sharp count": lambda r: r["lever_b_copy_charge"]["fewer_copies"].update(sharp_total_copies=92),
            "one deletion fewer per call": lambda r: r["lever_d_helper_deletion"]["sharp"]["RANK1"].update(per_call=39),
            "one reshaped call fewer": lambda r: r["lever_e_local_shape"].update(sharp_calls=51),
            "requirement 648": lambda r: r["requirement"].update(rank1_children=648),
            "bit sharing budget +1": lambda r: r["lever_b_copy_charge"]["two_call_bit_centre_sharing"]["overhead_budget"]["1"].update(total=8392),
            "flipped recorded verdict": lambda r: r["boundary_checks"][2].update(verdict="pass"),
            "edited histogram": lambda r: r["boundary_checks"][0]["hist"].update({"42": "289"}),
            "consistent shift: requirement 648 with rows rebuilt": lambda r: (
                r["requirement"].update(rank1_children=648),
                r["boundary_checks"][0].update(hist=r["boundary_checks"][1]["hist"]),
                r["boundary_checks"][1].update(hist=dict(r["boundary_checks"][1]["hist"],
                                                         **{"1": str(int(r["boundary_checks"][1]["hist"]["1"]) + 1)}))),
            "width-7 one helper fewer": lambda r: r["lever_f_width7"]["rank1_removed"].update(sharp_per_call=70),
            "complex need 510": lambda r: r["context_complex_at_c_star_need"].update(net_rank1_children=510),
            "complex budget +1": lambda r: r["context_complex_at_c_star"]["boundary_checks"][0].update(verdict="fail"),
        }
        for name, edit in edits.items():
            with self.subTest(name), self.assertRaises(AssertionError):
                independent.main(tampered(edit))


if __name__ == "__main__":
    unittest.main()
