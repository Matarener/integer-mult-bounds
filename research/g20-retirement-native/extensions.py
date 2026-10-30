"""Check further return-tail cohorts before freezing the constructive word."""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import retirement as L


def run():
    source = L.original_word()
    eligible = set(range(222, 658)) - set(source["owned"])
    candidates = {frozenset(eligible)} | {frozenset({h} | L.PARTIAL) for h in eligible - L.PARTIAL}
    rows = [1 << i for i in range(660)]
    for e in source["records"]:
        op, d = e[:2]
        value = rows[e[2]] if op == "ADD" else rows[d]
        if op == "Q" or (op == "ADD" and e[2] in eligible):
            if value and not value & ((1 << 222) - 1):
                support = frozenset(i for i in eligible if value >> i & 1)
                if len(support) > 1 and value == sum(1 << i for i in support):
                    candidates.add(support | L.PARTIAL)
        if op == "ADD":
            rows[d] ^= rows[e[2]]
        elif op == "ERASE":
            rows[d] = 0
    candidates.discard(L.PARTIAL)
    series = L.load("extension_positive_series", L.S / "ordinary-certificate/inputs/separate_series.py")
    debit = series.power(8, F(99, 100))[0]
    baseline_saved = Counter({1: 4, 3: 4})
    results = []
    for cohort in sorted(candidates, key=lambda a: (len(a), sorted(a))):
        _, _, _, edits = L.construct(cohort)
        saved = Counter(e["event"][4] for e in edits if e["event"][0] == "Q")
        difference = {r: saved[r] - baseline_saved[r] for r in set(saved) | set(baseline_saved)}
        L.need(all(n >= 0 for n in difference.values()), "Monotone specialized query saving")
        mass = sum(r * n for r, n in difference.items())
        extra = len(cohort - L.PARTIAL)
        L.need(extra > 0 and F(mass) < extra * debit, "No favorable extension in the declared census")
        results.append({"additional_owners": sorted(cohort - L.PARTIAL), "additional_paid_removed": difference,
                        "saved_rank_mass": mass, "debited_rank8_targets": extra})
    result = {"status": "PASS_G20_DECLARED_RETIREMENT_EXTENSION_CENSUS", "cohorts": len(results),
              "single_additions": sum(len(x["additional_owners"]) == 1 for x in results),
              "strict_rank8_debit_lower": str(debit), "saving_band": "0<=C<=1/100",
              "scope": "All single additions, complete pure-helper supports at source reads/queries, and the all-helper cohort. Other subsets and changed reconstruction programs remain open.",
              "results": results}
    L.put("EXTENSIONS.json.gz", result)
    print(result["status"], result["cohorts"], result["single_additions"])
    return result


if __name__ == "__main__":
    run()
