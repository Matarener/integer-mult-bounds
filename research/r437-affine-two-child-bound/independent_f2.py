# SPDX-License-Identifier: Apache-2.0
# Independent same-session OpenAI Codex adversarial agent, Chris R / Clear1nsight.
"""Independent finite adversarial check; not a proof of the general lemma."""
from functools import reduce

def need(ok):
    if not ok: raise ValueError("independent F2 product control failed")

def mm(A, B):
    return tuple(reduce(int.__xor__, (B[k] for k in range(len(A)) if (row >> k) & 1), 0) for row in A)

def lower(d):
    for bits in range(1 << (d * (d - 1) // 2)):
        rows, pos = [], 0
        for i in range(d):
            rows.append((1 << i) | ((bits >> pos) & ((1 << i) - 1)))
            pos += i
        yield tuple(rows)

def w(d, t):
    p = list(range(d))
    for i in range(t):
        p[i], p[d - 1 - i] = p[d - 1 - i], p[i]
    return tuple(1 << x for x in p)

G = list(lower(4))
W = w(4, 1)
target = (1, 4, 2, 8)
products = {mm(mm(L, W), M) for L in G for M in G}
full = {mm(mm(A, W), R) for A in products for R in G}
need(len(G) == 64 and len(full) == 16960 and target not in full)
W2 = w(4, 2)
lo = (1, 2, 6, 8)
need(mm(mm(lo, mm(mm(W2, lo), W2)), lo) == target)
M = (1, 2, 4, 10)
need(mm(mm(W, M), W)[0] & 14)
print({'field': 2, 'dimension': 4, 'lower_group_size': len(G), 'two_width1_product_count': len(full), 'middle_swap_present': target in full, 'two_width2_escape': True, 'equal_width_NE_can_be_nonzero': True})

# Independently found quotient bound equality, then embed it between fixed ends.
L=(1,3,7,13); M=(1,3,4,13); R=(1,3,6,15)
need(mm(mm(mm(mm(L,W),M),W),R)==W2)
def embed(A):return (1,)+tuple(row<<1 for row in A)+(32,)
large=mm(mm(mm(mm(embed(L),w(6,2)),embed(M)),w(6,2)),embed(R))
need(large==(1,16,8,4,2,32))
print({'quotient_tightness_control':True,'n':3,'r':2,'N':1,'widths':[2,2],'sum':4,'R437_attainment_claim':False})
