#!/usr/bin/env python3
"""Retimed lower-rank centre snapshots before the other centre COPYs."""
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


def screen(word, geometry, centre, masks, dims):
    records = word["records"]
    copies, erases, snapshots, R, K = acquisition.audit(word)
    lo, hi = copies[centre][0], erases[centre][0]
    begin = 1 + max(i for i, r in enumerate(records)
                    if r[0] == 1 and r[1] == 471 + centre and r[-1] == 2)
    end = copies[0][0]
    current = word["start"][:]
    for op, d, s, c, f, phase in records[:begin]:
        if op == 0:
            current[d] = c
    source_frame = current[471+centre]
    acquisition.need(source_frame == 510+centre, "completed source centre frame")
    acquisition.need(not any(r[0] == 1 and r[1] == 471+centre for r in records[begin:end]),
                     "completed source remains immutable")
    influence = [0] * 661
    for p in range(111):
        influence[111+p] = 1 << p
    suffix = {}
    for index in range(len(records)-1, begin-1, -1):
        op, d, s, c, f, phase = records[index]
        if not lo <= index <= hi:
            if op == 1:
                influence[s] ^= influence[d]
            elif op == 3:
                influence[660] = 0
            elif op == 2:
                influence[d] ^= influence[660]
                influence[660] = 0
        if index <= end:
            suffix[index] = influence[:660]
    touches = [[] for _ in range(660)]
    for index, (op, d, s, c, f, phase) in enumerate(records):
        if index < begin or lo <= index <= hi:
            continue
        if op == 0:
            touches[d].append((index, 0, c))
        elif op == 1:
            touches[d].append((index, 1, f))
            if s < 660:
                touches[s].append((index, 1, f))
        elif op in (2, 3):
            # Both operations read their persistent source at frame c.
            # An early public MOVE must not cross that unchanged read.
            touches[d].append((index, op, c))
    pointers = [0] * 660
    frames = [f for f in range(len(masks))
              if 3 <= dims[f] < 7 and masks[f] & ~masks[source_frame] == 0]
    options = {f: {} for f in frames}
    relaxed = {}
    for index in range(begin, end+1):
        for d, vector in enumerate(suffix[index]):
            if not vector or d == 471+centre:
                continue
            while pointers[d] < len(touches[d]) and touches[d][pointers[d]][0] < index:
                pointers[d] += 1
            nxt = touches[d][pointers[d]] if pointers[d] < len(touches[d]) else None
            old = current[d]
            new = nxt[2] if nxt and nxt[1] == 0 else old
            option = [index, d, old, new]
            for f in frames:
                if masks[old] & ~masks[f] == 0 and masks[f] & ~masks[new] == 0:
                    options[f].setdefault(vector, option)
            intersection = dims[new] - int(bool(masks[new] & ~masks[source_frame]))
            if (dims[old] < 7 and masks[old] & ~masks[source_frame] == 0
                    and intersection >= max(3, dims[old])):
                relaxed.setdefault(vector, option)
        if index < end:
            op, d, s, c, f, phase = records[index]
            if op == 0:
                current[d] = c
    target = sum(((row >> centre) & 1) << p for p, row in enumerate(K))
    results = []
    for f, pool in list(options.items()) + [(None, relaxed)]:
        basis = {}
        vectors = list(pool)
        for t, vector in enumerate(vectors):
            acquisition.basis_add(basis, vector, 1 << t)
        solution = acquisition.solve(basis, target)
        results.append(dict(frame=f, distinct_influences=len(pool), influence_rank=len(basis),
                            solvable=solution is not None,
                            insertions=([pool[vectors[t]] for t in acquisition.bits(solution)]
                                        if solution is not None else None),
                            separator=(hex(acquisition.separator(vectors, target))
                                       if solution is None else None),
                            option_set_sha256=sha256(json.dumps(list(pool.items()), separators=(",", ":"))
                                                    .encode()).hexdigest()))
    return dict(centre=centre, source=471+centre, completed_cut=begin, final_cut=end,
                cuts=end-begin+1, results=results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    word, geometry = acquisition.load()
    masks, dims = direct.frame_geometry(geometry)
    results = [screen(word, geometry, j, masks, dims) for j in range(9)]
    positives = [[r["centre"], q] for r in results for q in r["results"] if q["solvable"]]
    report = dict(status="PASS_LATE_FACTORY_CENTRE_SCREEN" if not positives else "LATE_FACTORY_CANDIDATES",
                  source_word_sha256=acquisition.WORD_SHA, geometry_sha256=acquisition.GEOMETRY_SHA,
                  results=results, positives=positives,
                  scope="completed retained centre before first remaining COPY; unchanged other scalar gates; legal early MOVE splitting; lower COPY rank at most four",
                  relaxation="frame None permits a different arbitrary real frame for each receiver and cut",
                  rational_frame_audit=dict(frames=len(masks), all_exact_root_closures=True,
                                            all_exact_rational_dimensions=True),
                  grants=["free restoration", "free added scalar gates", "free MOVE splitting"])
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"], sum(r["cuts"] for r in results), "cuts;", len(positives), "positives")


if __name__ == "__main__":
    main()
