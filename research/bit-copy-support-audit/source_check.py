#!/usr/bin/env python3
"""Independent finite support controls and exact predecessor trace applicability."""
import argparse
from collections import Counter, deque
import gzip
from hashlib import sha256
import json
from math import gcd
from pathlib import Path

WORD_SHA = "c46ccd7d3eedabc6a7efbb1a91ec13f2928bad8ee0bac57c6e593a092d13d96c"
GEOMETRY_SHA = "a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022"


def need(ok, why):
    if not ok:
        raise ValueError(why)


def rational_rank(rows):
    """Fraction-free primitive integer elimination, independent of producer."""
    def primitive(row):
        g = 0
        for x in row:
            g = gcd(g, abs(x))
        if g:
            row = [x // g for x in row]
            if next(x for x in row if x) < 0:
                row = [-x for x in row]
        return row

    basis = {}
    for row in rows:
        row = primitive(list(row))
        for pivot in sorted(basis):
            if row[pivot]:
                old = basis[pivot]
                a, b = row[pivot], old[pivot]
                row = primitive([b*x-a*y for x, y in zip(row, old)])
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            basis[pivot] = row
    return len(basis)


def tiny_closure():
    # Rational lines 0, e1, e2, e1+e2, and the plane represented by their
    # intersections with these three nonzero root directions. For this
    # finite lattice, set containment exactly equals rational containment.
    frames = (0, 1, 2, 4, 7)

    def contained(a, b):
        return a & ~b == 0

    counts = []
    for low in frames:
        seeds = {(a, b, 0, 0) for a in frames for b in frames}
        seen, pending = set(seeds), deque(sorted(seeds))
        edges = 0
        while pending:
            a, b, da, db = pending.popleft()
            fs, ds = (a, b), (da, db)
            need(all(not d or contained(low, f) for f, d in zip(fs, ds)),
                 "finite causal invariant")
            successors = []
            for dest in range(2):
                for newframe in frames:
                    if contained(fs[dest], newframe):
                        newfs = list(fs)
                        newfs[dest] = newframe
                        successors.append(tuple(newfs) + ds)
                if contained(low, fs[dest]):
                    newds = list(ds)
                    newds[dest] ^= 1
                    successors.append(fs + tuple(newds))
            if a == b:
                successors.extend(((a, b, da ^ db, db), (a, b, da, db ^ da)))
            edges += len(successors)
            for nxt in successors:
                if nxt not in seen:
                    seen.add(nxt)
                    pending.append(nxt)
        counts.append({"L_mask": low, "reachable_states": len(seen), "edges": edges})
    return {
        "scope": "Complete finite-state closure for two F2 public scalar differences over the five rational subspaces of Q2 represented by 0,e1,e2,e1+e2,Q2; arbitrary finite trace length, not a proof for all frame spaces",
        "closures": counts,
        "total_states": sum(x["reachable_states"] for x in counts),
        "total_edges": sum(x["edges"] for x in counts),
    }


def relaxation_controls():
    # Actual paired executions, with every dirt assignment and q in F2.
    # Positive rank-one entrance COPY from Q2 to L=e1 and exact ERASE are
    # outside this public trace; the source q never changes.
    rows = []
    for q in (0, 1):
        for a in (0, 1):
            # Same logical scalar after a deliberately downward public move.
            base, changed = a, a ^ q
            need((base ^ changed) == q, "downward relaxation difference")
            rows.append({"control": "downward_public_move", "q": q,
                         "dirty": [a], "baseline": base, "changed": changed})
            for b in (0, 1):
                base, changed = b ^ a, b ^ (a ^ q)
                need((base ^ changed) == q, "cross-frame ADD relaxation difference")
                rows.append({"control": "unequal_frame_public_add", "q": q,
                             "dirty": [a, b], "baseline": base, "changed": changed})
    # A real cancellation control: two equal reads cancel in F2 at an
    # allowed frame; this is accepted rather than counted as an obstruction.
    need(all(a ^ q ^ q == a for a in (0, 1) for q in (0, 1)),
         "F2 cancellation remains an accepted legal control")
    return {"paired_executions": rows,
            "nonzero_q_failure_count": sum(x["baseline"] != x["changed"] for x in rows),
            "allowed_F2_cancellation_cases": 4,
            "meaning": "Named relaxations permit influence outside L containment; original hypotheses are not contradicted"}


def actual_trace(inputs):
    paths = {"word": inputs / "WORD.json.gz", "geometry": inputs / "GEOMETRY.json.gz"}
    raws = {k: p.read_bytes() for k, p in paths.items()}
    need(sha256(raws["word"]).hexdigest() == WORD_SHA, "word immutable hash")
    need(sha256(raws["geometry"]).hexdigest() == GEOMETRY_SHA, "geometry immutable hash")
    word, geom = (json.loads(gzip.decompress(raws[k])) for k in ("word", "geometry"))
    rootsets = [frozenset(xs) for xs in geom["frames"]]
    need(len(rootsets) == 636 and len(geom["lines"]) == 111, "actual source dimensions")
    need(all(len(row) == 8 and all(type(x) is int for x in row) for row in geom["lines"]),
         "integer eight-dimensional actual roots")
    ranks = [rational_rank(geom["lines"][q] for q in roots) for roots in rootsets]
    need(ranks[0] == 0 and ranks[1] == 8, "zero and full frame rational ranks")
    current = word["start"][:] + [None]
    need(len(current) == 661, "660 public and one private slot")
    counts = Counter()
    last_erase = None
    copy_source = None
    copy_rows = []
    last_target_add = None
    frames_at = {}
    for index, row in enumerate(word["records"]):
        op, d, s, c, f, phase = row
        need(0 <= d < 660 and 0 <= s <= 660, "operand range")
        if op == 0:
            need(current[d] == s, "MOVE entrance frame")
            need(rootsets[s] <= rootsets[c], "upward MOVE via included root generators")
            need(f > 0 and ranks[c] - ranks[s] == f, "positive exact rational MOVE rank")
            current[d] = c
            counts["MOVE"] += 1
        elif op == 1:
            need(current[d] == current[s] == f, "ADD same actual frame")
            need(c in (-1, 1), "fixed signed unit scalar")
            need(d != copy_source, "active copied source is unchanged")
            need(not 111 <= s < 222, "targets never feed another ADD")
            if 111 <= d < 222:
                last_target_add = index
            counts["ADD"] += 1
        elif op == 2:
            need(current[660] is None and copy_source is None and s == 660, "fresh COPY")
            need(current[d] == c and rootsets[f] <= rootsets[c], "COPY source/destination frames")
            need(ranks[c] > ranks[f], "strictly positive exact COPY rank")
            current[660], copy_source = f, d
            copy_rows.append({"index": index, "source_register": d, "source_frame": c})
            counts["COPY"] += 1
        elif op == 3:
            need(s == 660 and d == copy_source, "ERASE same source")
            need(current[d] == c and current[660] == f, "ERASE same actual frames")
            current[660], copy_source = None, None
            last_erase = index
            frames_at[index + 1] = current[:]
            counts["ERASE"] += 1
        else:
            raise ValueError("unknown opcode")
    need(current[:-1] == word["final"] and current[-1] is None, "exact final frame labels")
    need(last_erase is not None and last_target_add is not None, "actual bounds exist")
    begin, end = last_erase + 1, last_target_add + 1
    need((begin, end) == (24069, 25768), "exact postscatter interval")
    suffix = word["records"][begin:end]
    need(all(r[0] in (0, 1) for r in suffix), "suffix has no COPY or ERASE")
    need(not any(r[0] in (0, 1) and 471 <= r[1] < 480 for r in suffix),
         "nine source values and frames unchanged in suffix")
    need([x["source_register"] for x in copy_rows] == list(range(471, 480)),
         "nine actual source identities")
    need(all(ranks[x["source_frame"]] == 7 for x in copy_rows), "nine source ranks seven")
    dots = 0
    for p in range(111):
        normal = geom["lines"][p]
        cap = word["final"][111 + p]
        need(sum(x*x for x in normal) == 4 and ranks[cap] == 7,
             "nonzero norm-four root and rank-seven final cap")
        for q in rootsets[cap]:
            need(sum(a*b for a, b in zip(normal, geom["lines"][q])) == 0,
                 "final frame generators orthogonal to actual port root")
            dots += 1
    return {
        "word_sha256": WORD_SHA,
        "geometry_sha256": GEOMETRY_SHA,
        "records": len(word["records"]),
        "operation_counts": dict(counts),
        "postscatter_interval": [begin, end],
        "postscatter_records": len(suffix),
        "postscatter_counts": dict(Counter(str(r[0]) for r in suffix)),
        "source_registers": list(range(471, 480)),
        "source_entry_frames": frames_at[begin][471:480],
        "final_cap_orthogonality_checks": dots,
        "exact_rational_frame_ranks": ranks,
        "rank_seven_final_caps": 111,
        "rank_eight_full_frames": [i for i, rank in enumerate(ranks) if rank == 8],
        "limits": "Checks actual trace, public upward containment via explicitly included root generators, all 636 supplied span ranks, signed same-frame ADDs, unchanged sources, no suffix COPY, exact final labels and equality of all final caps with their root-orthogonal hyperplanes. Does not compute complete root closures, actual R/K coefficients, full decoded endpoint, or physical MOVE semantics.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", "--inputs", dest="inputs", type=Path,
                        default=Path(__file__).resolve().parent / "source")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = {
        "status": "PASS_INDEPENDENT_CAUSAL_SUPPORT_AUDIT_NO_NEW_KAPPA",
        "predecessor_head": "ddfc3133cbdf548e163c867d5671f8f01dd5d5ae",
        "finite_toy_closure": tiny_closure(),
        "hypothesis_relaxation_controls": relaxation_controls(),
        "actual_source_trace": actual_trace(args.inputs),
        "code_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "not_a_formal_kernel_proof": True,
    }
    if args.output is not None:
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
