#!/usr/bin/env python3
"""Screen complex target updates modulo legally compensatable dirty inputs.

This changes the observation contract: all SOURCE, TARGET and wrapped-helper
columns remain exact in the free warp algebra; only unwrapped zero-entrance
dirty-helper responses may change. A positive still needs literal correction
synthesis and full native checks. No change is admitted by this screen alone.
"""
from collections import defaultdict
import argparse
from fractions import Fraction as Q
from hashlib import sha256
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


def combination(target, candidates, rows):
    """Exact sparse rational elimination, with a literal register witness."""
    pivots = {}
    for r in candidates:
        row = dict(rows[r])
        witness = {r: Q(1)}
        while row:
            key = max(row)
            if key not in pivots:
                q = row[key]
                row = {k: v / q for k, v in row.items()}
                witness = {k: v / q for k, v in witness.items()}
                pivots[key] = (row, witness)
                break
            old, expr = pivots[key]
            q = row[key]
            for k, v in old.items():
                value = row.get(k, Q(0)) - q * v
                if value: row[k] = value
                else: row.pop(k, None)
            for k, v in expr.items():
                value = witness.get(k, Q(0)) - q * v
                if value: witness[k] = value
                else: witness.pop(k, None)
    row, witness = dict(target), {}
    while row:
        key = max(row)
        if key not in pivots: return None
        old, expr = pivots[key]
        q = row[key]
        for k, v in old.items():
            value = row.get(k, Q(0)) - q * v
            if value: row[k] = value
            else: row.pop(k, None)
        for k, v in expr.items():
            value = witness.get(k, Q(0)) + q * v
            if value: witness[k] = value
            else: witness.pop(k, None)
    if any(q.denominator & (q.denominator - 1) for q in witness.values()): return None
    # Rebuild the projected row directly from the emitted witness.
    rebuilt = {}
    for r, q in witness.items():
        for k, v in rows[r].items():
            value = rebuilt.get(k, Q(0)) + q * v
            if value: rebuilt[k] = value
            else: rebuilt.pop(k, None)
    assert rebuilt == target
    return witness


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--combinations", action="store_true")
    args = ap.parse_args()
    t0 = time.monotonic()
    w = F.read(SOURCE)
    live = set(range(704)) - set(w["removed"])
    allowed = {r for r in live if r >= 224 and str(r) not in w["start_extra"] and str(r) not in w["helper_final"]}
    rows = {r: {} if r in allowed else {(r, ()): Q(1)} for r in live}
    groups = defaultdict(set)
    keys, factors = {}, {}
    current = {r: F.basis((w["ports"][r],)) if r < 112 else F.basis(tuple(w["start_extra"].get(str(r), []))) for r in live}

    def refresh(r):
        if r in keys:
            groups[keys[r]].remove(r)
        if not rows[r]:
            keys[r], factors[r] = (), Q(1)
        else:
            first = min(rows[r])
            factor = rows[r][first]
            keys[r] = tuple((var, word, q.numerator, q.denominator)
                            for (var, word), value in sorted(rows[r].items())
                            for q in (value / factor,))
            factors[r] = factor
        groups[keys[r]].add(r)

    def add(d, s, c):
        for key, value in tuple(rows[s].items()):
            q = rows[d].get(key, Q(0)) + c * value
            if q:
                rows[d][key] = q
            else:
                rows[d].pop(key, None)
        refresh(d)

    def execute(e):
        if e[0] == "add":
            add(e[1], e[2], Q(e[3], e[4]))
        elif e[0] == "scale":
            rows[e[1]] = {k: Q(e[2], e[3]) * q for k, q in rows[e[1]].items()}
            refresh(e[1])
        elif e[0] == "warp":
            op = e[2]
            rows[e[1]] = {(var, word[1:] if word and word[0] == -op else (op,) + word): value
                          for (var, word), value in rows[e[1]].items()}
            refresh(e[1])
        else:
            raise ValueError(e[0])

    for r in live:
        refresh(r)
    # The formal twisted corrections only use the allowed dirty coordinates
    # and therefore vanish in this exact quotient; reject a contrary source.
    for term in w["initial_corrections"]:
        assert term["source"] in allowed
    for e in w["precondition"] + w["compensation"]:
        execute(e)
    sections = F.expand(w)
    # These are fixed future contact caps, deliberately conservative. The
    # graph optimizer can relax additional frames after a nomination.
    full = F.basis(tuple(1 << i for i in range(9)))
    upper = {r: full for r in live}
    for r in live:
        if 112 <= r < 224:
            upper[r] = F.basis(tuple(x for x in range(512) if not ((x & w["ports"][r - 112]).bit_count() & 1)))
        if str(r) in w["helper_final"]:
            upper[r] = F.basis(tuple(w["helper_final"][str(r)]))
    future = {}
    if args.combinations:
        for section in ("restore", "B"):
            for index in reversed(range(len(sections[section]))):
                e = sections[section][index]
                if section == "B" and e[0] == "add" and 112 <= e[1] < 224:
                    future[index] = dict(upper)
                if e[0] == "warp":
                    upper[e[1]] = F.basis(tuple(e[3]))
                else:
                    frame = F.basis(tuple(e[-1]))
                    for r in F.regs(e): upper[r] = F.meet(upper[r], frame)
    candidates, zeros, contacts, combinations_found = [], [], 0, []
    for section in ("A", "B", "restore"):
        for index, e in enumerate(sections[section]):
            if section == "B" and e[0] == "add" and 112 <= e[1] < 224:
                d, s = e[1], e[2]
                contacts += 1
                frame = F.basis(tuple(e[-1]))
                if args.combinations and (current[d] != frame or current[s] != frame):
                    cap = future[index]
                    for test in sorted({current[d], frame}, key=lambda f: (len(f), f)):
                        if not F.contains(test, cap[d]): continue
                        available = [r for r in sorted(live) if r not in (d, s) and not 112 <= r < 224
                                     and rows[r] and F.contains(current[r], test) and F.contains(test, cap[r])]
                        available.sort(key=lambda r: (len(rows[r]), -len(current[r]), r))
                        solution = combination(rows[s], available, rows)
                        if solution is not None:
                            combinations_found.append({"section": section, "index": index, "event": e,
                                                       "frame": list(test), "replacement": [[r, str(q * Q(e[3], e[4]))] for r, q in sorted(solution.items())],
                                                       "available_registers": len(available)})
                    if contacts % 100 == 0:
                        print("COMBINATION_PROGRESS", contacts, len(combinations_found), time.monotonic() - t0, flush=True)
                if not keys[s]:
                    zeros.append({"section": section, "index": index, "event": e})
                else:
                    for r in sorted(groups[keys[s]] - {d, s}):
                        ratio = factors[s] / factors[r]
                        coeff = Q(e[3], e[4]) * ratio
                        if coeff.denominator & (coeff.denominator - 1):
                            continue
                        # Fixed event frame makes this a conservative immediate
                        # feasibility test; the joint solver may subsequently
                        # remove additional stops after the graph change.
                        if not F.contains(current[r], frame):
                            continue
                        candidates.append({"section": section, "index": index, "event": e,
                                           "new_source": r, "new_coefficient": str(coeff),
                                           "source_current": list(current[s]),
                                           "replacement_current": list(current[r]),
                                           "event_rank": len(frame),
                                           "source_climb": len(frame) - len(current[s]),
                                           "replacement_climb": len(frame) - len(current[r])})
            execute(e)
            if e[0] == "warp":
                assert current[e[1]] == F.basis(tuple(e[3]))
                current[e[1]] = F.basis(tuple(e[4]))
            else:
                frame = F.basis(tuple(e[-1]))
                for r in F.regs(e):
                    assert F.contains(current[r], frame)
                    current[r] = frame
    out = HERE / ("complex-local/projection-combinations" if args.combinations else "complex-local/projection")
    out.mkdir(parents=True, exist_ok=True)
    result = {"status": "EXACT_COMPLEX_COMPENSATABLE_PROJECTION_SCREEN", "new_kappa": False,
              "legal_zero_frame_unwrapped_inputs": sorted(allowed), "target_contacts": contacts,
              "substitutions": candidates, "zero_projection_updates": zeros,
              "combination_substitutions": combinations_found,
              "source_sha256": sha256(SOURCE.read_bytes()).hexdigest(),
              "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "seconds": time.monotonic() - t0,
              "scope": "Individual B target-source substitutions at original feasible frames, equal modulo the 213 legally compensatable dirty inputs in the full free warp algebra. No compensation synthesis, end-to-end identity or new profile is claimed."}
    (out / "SCREEN.json").write_text(json.dumps(result, indent=2) + "\n")
    print("COMPLEX_PROJECTION", "contacts", contacts, "substitutions", len(candidates), "zero_updates", len(zeros), "combinations", len(combinations_found), "seconds", time.monotonic() - t0, flush=True)


if __name__ == "__main__":
    main()
