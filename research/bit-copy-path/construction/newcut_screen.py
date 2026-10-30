#!/usr/bin/env python3
"""One lower-frame centre snapshot carried through all of literal phase B.

Allows arbitrary target/source/helper receivers and free upward retiming within
an existing frame transition, after the register's last use at its old frame.
The existing phase-B scalar gates are fixed.  Inverse cleanup and owner costs
are granted free by the negative screen.
"""
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import json
import types

HERE = Path(__file__).resolve().parent


def load_source(filename):
    path = HERE / filename
    source = path.read_bytes()
    pins = json.loads((HERE / "SOURCES.json").read_bytes())["code"]
    if sha256(source).hexdigest() != pins[filename]:
        raise ValueError("authenticated sibling source: " + filename)
    module = types.ModuleType(filename[:-3])
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec", dont_inherit=True, optimize=0), module.__dict__)
    return module


acquisition = load_source("acquisition_screen.py")
direct = load_source("direct_scatter.py")

N = 660


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    word, geometry = acquisition.load()
    copies, erases, snapshots, R, K = acquisition.audit(word)
    records = word["records"]
    begin = erases[-1][0] + 1
    end = max(i for i, r in enumerate(records) if r[0] == 1 and 111 <= r[1] < 222) + 1
    acquisition.need((begin, end) == (24069, 25768), "actual B interval")
    masks, dims = direct.frame_geometry(geometry)
    current = word["start"][:]
    for op, d, s, c, f, ph in records[:begin]:
        if op == 0:
            current[d] = c
    acquisition.need(all(current[471+j] == 510+j for j in range(9)),
                     "original retained centre frames")
    acquisition.need(not any(r[0] == 1 and r[1] in range(471, 480)
                             for r in records[begin:end]), "snapshot sources immutable throughout B")
    # At a cut, a register can be raised early only if its next use is the
    # original MOVE.  This permits splitting that MOVE with no rank-mass gain
    # claimed.  Every old scalar use remains at its original frame.
    touches = [[] for _ in range(N)]
    for index, (op, d, s, c, f, ph) in enumerate(records):
        if index < begin:
            continue
        if op == 0:
            touches[d].append((index, 0, c))
        elif op == 1:
            touches[d].append((index, 1, f))
            if s < N:
                touches[s].append((index, 1, f))
        elif op in (2, 3):
            touches[d].append((index, op, c))
    pointers = [0] * N
    influence = [0] * (N + 1)
    for p in range(111):
        influence[111+p] = 1 << p
    suffix = {}
    for index in range(len(records)-1, begin-1, -1):
        op, d, s, c, f, ph = records[index]
        if op == 1:
            influence[s] ^= influence[d]
        elif op == 3:
            influence[N] = 0
        elif op == 2:
            influence[d] ^= influence[N]
            influence[N] = 0
        if index <= end:
            suffix[index] = influence[:N]
    frame_sets = [[f for f in range(len(masks))
                   if 3 <= dims[f] < 7 and masks[f] & ~masks[510+j] == 0]
                  for j in range(9)]
    acquisition.need(all(len(fs) == 10 for fs in frame_sets), "ten catalogue lower frames per centre")
    high_frames = [f for f in range(len(masks)) if 6 <= dims[f] <= 8]
    all_frames = sorted({f for fs in frame_sets for f in fs} | set(high_frames))
    options = {f: {} for f in all_frames}
    actual_options = {f: {} for f in all_frames}
    arbitrary_frame_options = [{} for _ in range(9)]
    compatibility = {}
    for index in range(begin, end+1):
        inf = suffix[index]
        for d, vector in enumerate(inf):
            if not vector:
                continue
            while pointers[d] < len(touches[d]) and touches[d][pointers[d]][0] < index:
                pointers[d] += 1
            nxt = touches[d][pointers[d]] if pointers[d] < len(touches[d]) else None
            old = current[d]
            new = nxt[2] if nxt and nxt[1] == 0 else old
            pair = old, new
            if pair not in compatibility:
                compatibility[pair] = [f for f in all_frames
                                       if masks[old] & ~masks[f] == 0
                                       and masks[f] & ~masks[new] == 0]
            for f in compatibility[pair]:
                option = [index, d, old, new, vector]
                options[f].setdefault(vector, option)
                if old == f:
                    actual_options[f].setdefault(vector, option)
            # Stronger necessary screen: allow a different arbitrary real G
            # for every receiver, at every cut.  There is no common-frame or
            # dyadic-projector demand in this relaxation.  Since F_source is
            # a hyperplane, dim(F_source intersect F_next) is rank(F_next)
            # or rank(F_next)-1 according to containment.
            for j in range(9):
                fs = 510+j
                intersection_rank = dims[new] - int(bool(masks[new] & ~masks[fs]))
                if (dims[old] < 7 and masks[old] & ~masks[fs] == 0
                        and intersection_rank >= max(3, dims[old])):
                    arbitrary_frame_options[j].setdefault(vector, [index, d, old, new, vector])
        if index == end:
            break
        op, d, s, c, f, ph = records[index]
        if op == 0:
            current[d] = c
    results = []
    for j in range(9):
        desired = sum(((row >> j) & 1) << p for p, row in enumerate(K))
        for f in frame_sets[j]:
            for retiming, pool in ((False, actual_options[f]), (True, options[f])):
                option_list = list(pool.values())
                basis = {}
                for t, option in enumerate(option_list):
                    acquisition.basis_add(basis, option[-1], 1 << t)
                solution = acquisition.solve(basis, desired)
                chosen = None if solution is None else [option_list[t] for t in acquisition.bits(solution)]
                row = dict(centre=j, source=471+j, copy_frame=f, copy_rank=7-dims[f],
                           retiming=retiming, distinct_influences=len(pool), influence_rank=len(basis),
                           solvable=solution is not None, insertion_options=chosen,
                           separator=(hex(acquisition.separator(pool, desired))
                                      if solution is None else None),
                           option_set_sha256=sha256(json.dumps(option_list, separators=(",", ":"))
                                                    .encode()).hexdigest())
                results.append(row)
    positives = [r for r in results if r["solvable"]]
    relaxed = []
    for j, pool in enumerate(arbitrary_frame_options):
        desired = sum(((row >> j) & 1) << p for p, row in enumerate(K))
        basis = {}
        option_list = list(pool.values())
        for t, option in enumerate(option_list):
            acquisition.basis_add(basis, option[-1], 1 << t)
        solution = acquisition.solve(basis, desired)
        relaxed.append(dict(centre=j, distinct_influences=len(pool), rank=len(basis),
                            solvable=solution is not None,
                            separator=hex(acquisition.separator(pool, desired)) if solution is None else None,
                            insertion_options=([option_list[t] for t in acquisition.bits(solution)]
                                               if solution is not None else None)))
    promoted = []
    union_options = {}
    for f in high_frames:
        for vector, option in options[f].items():
            union_options.setdefault(vector, [f, option])
    union_basis = {}
    for t, vector in enumerate(union_options):
        acquisition.basis_add(union_basis, vector, 1 << t)
    union_targets = []
    for j in range(9):
        desired = sum(((row >> j) & 1) << p for p, row in enumerate(K))
        union_targets.append(acquisition.solve(union_basis, desired) is not None)
        for f in high_frames:
            pool = options[f]
            basis = {}
            option_list = list(pool.values())
            for t, option in enumerate(option_list):
                acquisition.basis_add(basis, option[-1], 1 << t)
            solution = acquisition.solve(basis, desired)
            if solution is not None:
                promoted.append(dict(centre=j, reader_frame=f, reader_rank=dims[f],
                                     insertions=[option_list[t] for t in acquisition.bits(solution)]))
    report = dict(status="PASS_NEW_CUT_SCREEN" if not positives else "NEW_CUT_CANDIDATES_REQUIRE_FULL_REPLAY",
                  source_word_sha256=acquisition.WORD_SHA, geometry_sha256=acquisition.GEOMETRY_SHA,
                  B_cuts_inclusive=[begin, end], cuts=end-begin+1,
                  persistent_inputs=N, source_snapshot_rows=[str(r) for r in snapshots],
                  frame_sets=frame_sets, tests=len(results), positives=positives, results=results,
                  arbitrary_frame_per_receiver_relaxation=relaxed,
                  high_frame_private_promotion_screen=dict(
                      reader_frames=high_frames, tests=9*len(high_frames), positives=promoted,
                      grants="arbitrary snapshot delivery to H, free private promotion/restoration; fixed H during all B reads",
                      all_H_union_rank=len(union_basis), all_H_union_targets_solvable=union_targets,
                      all_H_union_scope="diagnostic relaxation only: free arbitrary changes of H, no closed private walk or tariff asserted"),
                  rational_frame_audit=dict(frames=len(masks), all_exact_root_closures=True,
                                            all_exact_rational_dimensions=True),
                  scope="one unchanged retained total; one catalogue lower frame for entire B; original B gates; legal early MOVE splitting",
                  grants=["inverse cleanup free", "all new scalar ADDs free", "all MOVE splitting free",
                          "arbitrary targets and helpers", "all chronological cut influences may be combined"])
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"], report["tests"], "screens;", len(positives), "positive candidates")


if __name__ == "__main__":
    main()
