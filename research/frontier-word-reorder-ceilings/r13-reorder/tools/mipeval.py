"""MIP re-framing (construct.py medium domains) of one-step correction rewrites.
Usage: mipeval.py SIDE PART NPARTS [MAXSITES]"""
import sys, time, json
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from rewrite import *
import construct as K
from copy import deepcopy

def evaluate(w, side, site, d, C=0.00302):
    res = swap(w['programs'][side], site[2], d)
    if res is None: return None
    new, info = res
    w2 = dict(w); w2['programs'] = dict(w['programs']); w2['programs'][side] = new
    import io, contextlib
    M = K.build_mip(w2, side, C, 'medium')
    h = K.run(M, 120, start=False); info2 = h.getInfo()
    st = h.modelStatusToString(h.getModelStatus())
    return st, info2.objective_function_value + M['const'], info

if __name__ == '__main__':
    side, part, nparts = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); mx = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
    w = load(); sites = thin_sites(w, side)[part::nparts][:mx]
    for s in sites:
        for d in ('next', 'prev'):
            t = time.time()
            try: r = evaluate(w, side, s, d)
            except (ValueError, AssertionError) as ex: print('INFEASIBLE', s, d, repr(ex)[:80], flush=True); continue
            if r is None: continue
            print('EVAL', s, d, r[0], r[1], 'gain', 5253.116991559385 - r[1], r[2], round(time.time()-t, 1), flush=True)
