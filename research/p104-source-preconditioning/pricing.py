# SPDX-License-Identifier: Apache-2.0
"""Retained optimistic screen for separately charged native source shears."""
from collections import Counter
from fractions import Fraction as Q
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bindings import authenticate, module, need


def run():
    raw = authenticate()
    engine = module(raw, "precondition_retained_ceiling", "research/complex-local-word-ceiling/ceiling.py")
    word = json.loads(raw["research/p104-native-channel/inputs/LOWRANK-WITNESS.json"])
    profile = Counter(event[4] for event in word["program"] if event[0] == "transport")
    need(dict(profile) == {1:1074, 2:58, 3:86, 4:104, 5:48, 6:24, 7:8, 8:8}, "retained native channel invoice")
    profile[1] += 208 * 9
    need(sum(r * n for r, n in profile.items()) == 4240, "208 unit-flag local mass")
    assembly = json.loads(raw["research/community-frontier1094-audit/ASSEMBLY.json"])
    selected = Q(assembly["complex_lower"])
    need(selected == Q(67018507072324140917, 40000000000000000000000), "pinned selected saving")
    scale = 10**18
    results = []
    for count in range(5):
        current = dict(profile)
        current[2] += count
        low, high = engine.relax(current, 73, 832, 9, 56 + 2 * count, selected)
        lower = low.numerator * scale // low.denominator
        upper = -((-high.numerator * scale) // high.denominator)
        need((high < 1) if count < 4 else (low > 1), "three-pass/four-fail source-shear boundary")
        results.append(dict(additive_H2=count, local_mass=4240+2*count,
                            total_mass=6712+2*count, idle_mass=2472,
                            outward_numerators=[lower, upper], denominator=scale))
    need(results[-1]["outward_numerators"] == [1000088868784313991,1000088868784313992], "exact four-H2 interval")
    return dict(status="PASS_SEPARATELY_CHARGED_SOURCE_SHEAR_REJECTION", selected_saving=str(selected),
                cases=results, assumptions="208 unit flags, nine calls, 832 families, ideal fractional rank-51 idle; same 56 private charge, no extra restoration child or idle credit",
                limitation="Rank(U-I)>=4 alone does not price a joint/fused native preparation. This rejects only at least four separately charged H2 shears in the retained screen.")


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
