"""Rank-7 pinning after the T1 closure: zm = cert ZM (lines Gram on zm x zm).  One step (every line outside zm with
orthogonal zm-lines of root rank 7) and the iterated closure.  usage: python3 t1lean/pincheck.py k,k,..."""
import sys, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
sys.path.insert(0, B + '/t2hand/rev')
from common import N, R, G
import numpy as np
rw = [r for r in json.load(open(B + '/orbitsW.json')) if r['frame']]
def rank(vs): return int(np.linalg.matrix_rank(np.array(vs, dtype=float))) if vs else 0
for k in [int(x) for x in sys.argv[1].split(',')]:
    Z = [i for i in range(N) if int(rw[k]['mask']) >> i & 1]
    zm = set(json.load(open(HERE + '/cert/T1_%d.json' % k))['ZM'])
    one = [v for v in range(N) if v not in zm and rank([R[s] for s in zm if G[v][s] == 0]) < 7]
    cur = set(zm); rounds = 0; ch = True
    while ch:
        ch = False; rounds += 1
        add = [v for v in range(N) if v not in cur and rank([R[s] for s in cur if G[v][s] == 0]) >= 7]
        if add: cur |= set(add); ch = True
    print(k, '|Z|', len(Z), 'zm', len(zm), 'rank(zm)', rank([R[s] for s in zm]), 'one-step unpinned: in Z', [v for v in one if v in Z],
          'outside Z', len([v for v in one if v not in Z]), 'iterated', len(cur), 'rounds', rounds, flush=True)
