"""Test one-axis queries on retained small E caller values."""
from pathlib import Path
import itertools
import json
import time
import history_module as h


def run():
    started = time.monotonic()
    history, targets, sha = h.source()
    candidates = []
    for i, (name, row) in enumerate(history):
        for axis in range(4):
            candidates.append((name, axis, h.left(row, 1 << (2*axis), h.ID)))
    bases = {}
    queries = {}
    wanted = {}
    for weight in range(5):
        chi = (1 << weight)-1
        basis = {}
        for name, row in history:
            for p in range(24):
                h.insert(h.project(row, chi, p), basis)
        bases[weight] = basis
        wanted[weight] = [h.residue(h.project(t, chi, h.ID), basis) for t in targets[:2]]
        queries[weight] = [[h.residue(h.project(row, chi, p), basis)
                            for p in range(24)] for name, axis, row in candidates]
    hits = []
    singles = []
    for i in range(len(candidates)):
        cover = []
        for target in range(2):
            good = True
            for weight in range(5):
                b = {}
                for row in queries[weight][i]:
                    h.insert(row, b)
                if h.residue(wanted[weight][target], b):
                    good = False
                    break
            cover.append(good)
        if any(cover):
            singles.append({'query': candidates[i][:2], 'targets': cover})
    for i, j in itertools.combinations(range(len(candidates)), 2):
        good = True
        for weight in range(5):
            b = {}
            for row in queries[weight][i]+queries[weight][j]:
                h.insert(row, b)
            if any(h.residue(t, b) for t in wanted[weight]):
                good = False
                break
        if good:
            hits.append([candidates[i][:2], candidates[j][:2]])
    result = {'status': 'MODULAR_ONE_AXIS_RETAINED_QUERY_SCREEN',
              'source_program_sha256': sha, 'prime': h.MOD,
              'one_query_candidates': len(candidates), 'single_target_hits': singles,
              'two_query_cases': len(candidates)*(len(candidates)-1)//2,
              'two_query_both_target_hits': hits, 'seconds': time.monotonic()-started,
              'scope': 'Small published four-axis fixture; positive widths through a finite group algebra model. Queries use one coordinate axis and one saved paid return or original input. No actual odd-E8 implementation or rational infeasibility proof.'}
    Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    run()
