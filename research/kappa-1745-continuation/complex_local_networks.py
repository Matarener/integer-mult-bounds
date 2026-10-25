#!/usr/bin/env python3
"""Larger exact covector/receiver networks on the valid complex word.

All initial dirty columns are retained by the aggregate/undo identity. The
screen changes several coupled graph edges at once and solves their joint
frames. Numerical tariffs only nominate words for full native admission.
Credit Nick Petalas's shared-source mechanism, dataisfire's PR3734 source,
and the prior adaptive continuation's receiver rewrite and frame solver.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations
from pathlib import Path
import gzip
import json
import sys
import time

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "kappa-adaptive-continuation/native-alternatives"
SOURCE = OLD / "candidate/BORROW-WORD-43base.json.gz"
sys.path.insert(0, str(OLD))
import fanout_search as F
import opt_frames as O
from joint_fanout_search import transposed


def networks(w, section, transpose, max_donors, permanent):
    sections = F.expand(w)
    es = transposed(sections[section]) if transpose else sections[section]
    groups, reads, writes = F.pair_catalog(es, len(es))
    batches = defaultdict(list)
    for (a, b, q, ae, be), pairs in groups.items():
        if permanent and (112 <= a < 224 or str(a) in w["helper_final"] or a in w["centers"]):
            continue
        for chosen, lo, hi in F.clusters(pairs, a, b, reads, writes):
            if section == "A" and (len(es) - hi if transpose else lo) < w["prelude_events"]:
                continue
            keeps = tuple(sorted(p["keep"] for p in chosen))
            if permanent:
                if any(i >= lo and i not in keeps for i in reads[a]):
                    continue
                later = ("A", "B", "restore")[("A", "B", "restore").index(section) + 1:]
                if any(e[0] == "add" and e[2] == a for s in later for e in sections[s]):
                    continue
            batches[(a, ae, keeps)].append((b, q, be, lo, hi, chosen))
    for (a, ae, keeps), rows in sorted(batches.items()):
        for size in range(2, min(max_donors, len(rows)) + 1):
            for chosen in combinations(rows, size):
                donors = tuple(row[0] for row in chosen)
                if len(set(donors)) != size:
                    continue
                lo, hi = min(row[3] for row in chosen), max(row[4] for row in chosen)
                if any(lo <= i < hi for r in (a,) + donors for i in writes[r]):
                    continue
                if any(lo <= i < hi and i not in keeps for i in reads[a]):
                    continue
                drops = {p["drop"] for row in chosen for p in row[5]}
                if len(drops) != len(keeps) * size or drops.intersection(keeps):
                    continue
                orders = [tuple(range(size)), tuple(reversed(range(size)))]
                for order in sorted(set(orders)):
                    aggregate = [["add", a, chosen[j][0], chosen[j][1].numerator,
                                  chosen[j][1].denominator, []] for j in order]
                    undo = [["add", e[1], e[2], -e[3], e[4], []] for e in reversed(aggregate)]
                    changed = []
                    for i in range(len(es) + 1):
                        if i == lo:
                            changed.extend(aggregate)
                        if i == hi and not permanent:
                            changed.extend(undo)
                        if i < len(es) and i not in drops:
                            changed.append(es[i])
                    if transpose:
                        changed = transposed(changed)
                    out = deepcopy(w)
                    if section == "B":
                        out["B"] = []
                        for event in changed:
                            if event[0] == "warp":
                                out["warps"][event[2] - 1][0] = len(out["B"])
                            else:
                                out["B"].append(event)
                    else:
                        out[section] = changed
                    yield out, {"section": section, "transpose": transpose,
                                "permanent": permanent, "carrier": a,
                                "donors": [chosen[j][0] for j in order],
                                "coefficients": [str(chosen[j][1]) for j in order],
                                "lo": lo, "hi": hi, "keeps": list(keeps), "drops": sorted(drops)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--section", choices=("A", "B", "restore"), required=True)
    ap.add_argument("--transpose", action="store_true")
    ap.add_argument("--permanent", action="store_true")
    ap.add_argument("--max-donors", type=int, default=4)
    ap.add_argument("--limit", type=int, default=100000)
    ap.add_argument("--catalog-only", action="store_true")
    args = ap.parse_args()
    assert not (args.transpose and args.permanent)
    w = F.read(SOURCE)
    F.phi = lambda r: r ** (1 - 0.001745) if r else 0.0
    O.phi = F.phi
    label = args.section + ("-receivers" if args.transpose else "-sources") + ("-permanent" if args.permanent else "")
    outdir = HERE / "complex-local" / label
    outdir.mkdir(parents=True, exist_ok=True)
    stats, positives, catalog = Counter(), [], []
    t0 = time.monotonic()
    for index, (candidate, identity) in enumerate(networks(w, args.section, args.transpose, args.max_donors, args.permanent)):
        if index >= args.limit:
            stats["limit_reached"] += 1
            break
        stats["enumerated"] += 1
        if args.catalog_only:
            catalog.append(identity)
            continue
        try:
            candidate, result = O.optimize(candidate)
        except (ValueError, AssertionError) as exc:
            reason = exc.args[0] if exc.args else type(exc).__name__
            stats[str(reason[0] if isinstance(reason, tuple) else reason)] += 1
            continue
        stats["feasible"] += 1
        if result["saving"] > 1e-9:
            raw = json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode()
            name = "WORD-" + str(index) + ".json.gz"
            (outdir / name).write_bytes(gzip.compress(raw, mtime=0))
            rec = {"index": index, "identity": identity, "optimization": result,
                   "word": name, "payload_sha256": sha256(raw).hexdigest(),
                   "native_admission": False}
            positives.append(rec)
            (outdir / ("CANDIDATE-" + str(index) + ".json")).write_text(json.dumps(rec, indent=2) + "\n")
            print("NOMINATION", label, index, result, flush=True)
        if stats["enumerated"] % 50 == 0:
            print("PROGRESS", label, dict(stats), round(time.monotonic() - t0, 2), flush=True)
    paths = [SOURCE, Path(__file__), OLD / "fanout_search.py", OLD / "opt_frames.py", OLD / "joint_fanout_search.py"]
    receipt = {"status": "LARGER_COMPLEX_NETWORK_CATALOG" if args.catalog_only else "BOUNDED_COMPLEX_NETWORK_DISCOVERY",
               "stats": dict(stats), "candidates": positives, "catalog": catalog,
               "source_pins": {str(p.relative_to(HERE.parent.parent)): sha256(p.read_bytes()).hexdigest() for p in paths},
               "seconds": time.monotonic() - t0, "new_kappa": False,
               "scope": "At least two simultaneous donors/receivers, two aggregate orders, fixed chronological observations and provider interfaces. Numerical min-sum tariff screening only; every positive requires exact independent native replay, coefficient and physical owner invoice."}
    (outdir / "RESULT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("DONE", label, dict(stats), "positive", len(positives), "seconds", round(time.monotonic() - t0, 2), flush=True)


if __name__ == "__main__":
    main()
