#!/usr/bin/env python3
"""Bounded exact GF(2) screen for new source acquisitions in the literal A.

No source endpoint code and no new MOVE is allowed in this screen.  An option
is one literal h += x_i at a cut where both registers already have the same
frame.  It is a screening witness, not a supplier admission.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / "inputs"
N, V = 660, 111
WORD_SHA = "c46ccd7d3eedabc6a7efbb1a91ec13f2928bad8ee0bac57c6e593a092d13d96c"
GEOMETRY_SHA = "a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load():
    wb = (INPUT / "WORD.json.gz").read_bytes()
    gb = (INPUT / "GEOMETRY.json.gz").read_bytes()
    need(sha256(wb).hexdigest() == WORD_SHA, "literal word pin")
    need(sha256(gb).hexdigest() == GEOMETRY_SHA, "geometry pin")
    return json.loads(gzip.decompress(wb)), json.loads(gzip.decompress(gb))


def basis_add(basis, row, witness):
    while row:
        p = row.bit_length() - 1
        if p in basis:
            old, old_witness = basis[p]
            row ^= old
            witness ^= old_witness
        else:
            basis[p] = row, witness
            return True
    return False


def solve(basis, row):
    witness = 0
    while row:
        p = row.bit_length() - 1
        if p not in basis:
            return None
        old, old_witness = basis[p]
        row ^= old
        witness ^= old_witness
    return witness


def separator(rows, target):
    """Return l with l.rows=0 and l.target=1, or reject if none exists."""
    equations = {}
    for row, rhs in [(r, 0) for r in rows] + [(target, 1)]:
        while row:
            p = row.bit_length() - 1
            if p in equations:
                old, old_rhs = equations[p]
                row ^= old
                rhs ^= old_rhs
            else:
                equations[p] = row, rhs
                break
        else:
            need(rhs == 0, "no dual separator")
    result = 0
    for p, (row, rhs) in sorted(equations.items()):
        if ((row & result).bit_count() & 1) != rhs:
            result ^= 1 << p
    need(all((row & result).bit_count() % 2 == 0 for row in rows),
         "dual annihilates every legal acquisition")
    need((target & result).bit_count() % 2 == 1, "dual detects missing centre")
    return result


def bits(row):
    while row:
        b = row & -row
        yield b.bit_length() - 1
        row ^= b


def audit(word):
    records = word["records"]
    copies = [(i, r) for i, r in enumerate(records) if r[0] == 2]
    erases = [(i, r) for i, r in enumerate(records) if r[0] == 3]
    need(len(copies) == len(erases) == 9, "nine original copy episodes")
    values = [1 << j for j in range(N)] + [0]
    snapshots = []
    K = [0] * V
    for index, (op, d, s, c, f, phase) in enumerate(records):
        if op == 1:
            values[d] ^= values[s]
            if s == N:
                need(V <= d < 2 * V, "scatter target")
                K[d - V] ^= 1 << (len(snapshots) - 1)
        elif op == 2:
            need(values[N] == 0, "fresh private")
            values[N] = values[d]
            snapshots.append(values[d])
        elif op == 3:
            need(values[N] == values[d], "snapshot restoration at actual ERASE")
            values[N] = 0
    desired = [1 << j for j in range(N)] + [0]
    for i in range(V):
        desired[V + i] ^= 1 << i
    need(values == desired, "complete original F2 boundary")
    need(all(s >> (2 * V) == 1 << (471 + j - 2 * V)
             for j, s in enumerate(snapshots)), "one independent centre dirt")
    R = [s & ((1 << V) - 1) for s in snapshots]
    return copies, erases, snapshots, R, K


def screen(word, removed, safe_partial=True):
    """Screen all existing-frame A insertion cuts for one deleted episode."""
    records = word["records"]
    copies, erases, snapshots, R, K = audit(word)
    lo, hi = copies[removed][0], erases[removed][0]
    A = [i for i, r in enumerate(records) if r[0] == 1 and r[-1] == 2]
    a_start, a_stop = A[0], A[-1] + 1
    partial = [j for j in range(2 * V, N) if word["final"][j] != 1]
    need(partial == [462, 463, 464, 467, 470], "actual partial terminals")
    influence = [0] * (N + 1)
    for j in range(V):
        influence[V + j] = 1 << j
    # Exact integer cotangents for partial endpoints.  Individual zero options
    # cannot add any error to those early-retired arbitrary-input fields.
    terminal = [[int(j == p) for p in partial] for j in range(N + 1)]
    cuts = {}
    for index in range(len(records) - 1, a_start - 1, -1):
        op, d, s, c, f, phase = records[index]
        if not lo <= index <= hi:
            if op == 1:
                influence[s] ^= influence[d]
                terminal[s] = [x + c * y for x, y in zip(terminal[s], terminal[d])]
            elif op == 3:
                influence[N] = 0
                terminal[N] = [0] * len(partial)
            elif op == 2:
                influence[d] ^= influence[N]
                terminal[d] = [x + y for x, y in zip(terminal[d], terminal[N])]
                influence[N] = 0
                terminal[N] = [0] * len(partial)
        if a_start <= index <= a_stop:
            cuts[index] = (influence[:], [any(x) for x in terminal])
    current = word["start"][:]
    source = [1 << j for j in range(V)]
    options = [[] for _ in range(V)]
    seen = [set() for _ in range(V)]
    for index, (op, d, s, c, f, phase) in enumerate(records):
        if index in cuts:
            inf, unsafe = cuts[index]
            by_frame = {}
            for h in range(2 * V, N):
                if inf[h] and (not safe_partial or not unsafe[h]):
                    by_frame.setdefault(current[h], []).append(h)
            for i in range(V):
                for h in by_frame.get(current[i], []):
                    key = inf[h]
                    if key not in seen[i]:
                        seen[i].add(key)
                        options[i].append((index, h, current[i], key))
        if op == 0:
            current[d] = c
        elif op == 1 and d < V:
            need(index >= a_stop, "source not clean through A")
        if index >= a_stop:
            break
    target = sum(((row >> removed) & 1) << i for i, row in enumerate(K))
    results, insertions = [], []
    for i in bits(R[removed]):
        basis = {}
        for t, option in enumerate(options[i]):
            basis_add(basis, option[3], 1 << t)
        result = solve(basis, target)
        chosen = [] if result is None else [options[i][t] for t in bits(result)]
        insertions += [[cut, h, i, frame] for cut, h, frame, _ in chosen]
        results.append(dict(source=i, options=len(options[i]), rank=len(basis),
                            solvable=result is not None, ADDs=len(chosen),
                            dual_separator=(hex(separator([t[3] for t in options[i]], target))
                                            if result is None else None),
                            options_sha256=sha256(json.dumps(options[i], separators=(",", ":"))
                                                  .encode()).hexdigest()))
    return dict(removed=removed, source_register=471 + removed,
                missing_source_weight=R[removed].bit_count(),
                missing_target_weight=target.bit_count(),
                safe_partial=safe_partial, all_solvable=all(r["solvable"] for r in results),
                solvable=sum(r["solvable"] for r in results),
                total_ADDs=len(insertions), sources=results, insertions=insertions)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    word, geometry = load()
    copies, erases, snapshots, R, K = audit(word)
    ranks = {}
    for label, rows in (("R", R), ("K", K), ("snapshot", snapshots)):
        b = {}
        for i, row in enumerate(rows):
            basis_add(b, row, 1 << i)
        ranks[label] = len(b)
    results = []
    for j in range(9) if args.all else [0]:
        result = screen(word, j, not args.allow_partial)
        results.append(result)
        print(json.dumps({k: v for k, v in result.items()
                          if k not in ("sources", "insertions")}), flush=True)
    report = dict(source_word_sha256=WORD_SHA, geometry_sha256=GEOMETRY_SHA,
                  persistent_inputs=N, arbitrary_helpers=438, cut_ranks=ranks,
                  R=[str(r) for r in R], K=K,
                  snapshot_rows=[str(r) for r in snapshots], results=results,
                  claim="fixed-existing-frame source-acquisition GF2 screen only")
    if args.out:
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
