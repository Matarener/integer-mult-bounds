#!/usr/bin/env python3
"""Exact finite H6 odd-Gram kernel screen; standard library only.

This checks the signed E8 root association algebra, its five idempotents,
the root-product eigenvalue forms, and the entire two-parameter rank
arrangement over any characteristic-zero extension field. It does not
implement a physical supplier or certify all-size/precision interfaces.
"""
import argparse
from fractions import Fraction as F
from itertools import combinations, product
from math import comb, lcm
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
N = 30960
DIM = [1, 8, 35, 112, 84]


def need(ok, label):
    if not ok:
        raise ValueError(label)


def roots():
    ans = []
    for i, j in combinations(range(8), 2):
        for x, y in product((-2, 2), repeat=2):
            q = [0] * 8
            q[i], q[j] = x, y
            ans.append(tuple(q))
    ans.extend(q for q in product((-1, 1), repeat=8) if sum(x < 0 for x in q) % 2 == 0)
    return sorted(ans)


def dot(a, b):
    z = sum(x * y for x, y in zip(a, b))
    need(z % 4 == 0, "ordinary E8 dot must be integral")
    return z // 4


def association():
    q = roots()
    need(len(set(q)) == 240, "240 signed roots")
    need(all(sum(x*x for x in a) == 8 for a in q), "root norm two")
    index = {a:i for i,a in enumerate(q)}
    anti = [index[tuple(-x for x in a)] for a in q]
    s = [[dot(a,b) for b in q] for a in q]
    r = [[x*x for x in row] for row in s]
    # Q^T Q = 240 I implies S^2 = 60 S exactly.
    need(all(sum(a[i]*a[j] for a in q) == (240 if i == j else 0)
             for i in range(8) for j in range(8)), "root second moment")
    need(all(sum(row) == 0 for row in s), "S J = 0")
    need(all(sum(row) == 120 for row in r), "R J = 120 J")
    need(all(s[anti[i]][j] == -s[i][j] and r[anti[i]][j] == r[i][j]
             for i in range(240) for j in range(240)), "antipodal parity")
    # R has entries only 0,1,4. Bit intersections replay all 57,600
    # coefficients of R^2 without a floating or modular matrix product.
    ones = [sum(1 << j for j,x in enumerate(row) if x == 1) for row in r]
    fours = [sum(1 << j for j,x in enumerate(row) if x == 4) for row in r]
    for i in range(240):
        for j in range(240):
            value = ((ones[i] & ones[j]).bit_count()
                     + 4*(ones[i] & fours[j]).bit_count()
                     + 4*(fours[i] & ones[j]).bit_count()
                     + 16*(fours[i] & fours[j]).bit_count())
            need(value == 24*r[i][j]+48, "R^2 = 24 R + 48 J")
    # S R = 0 follows by pairing k with its antipode: S is odd and R even.
    # These exact base identities define the closed five-dimensional algebra.
    basis = [[F(int(i == j)) for j in range(5)] for i in range(5)]
    unit, ap, jj, ss, rr = basis
    table = {}
    def put(a,b,v): table[a,b] = table[b,a] = v
    for i in range(5): put(0,i,basis[i])
    put(1,1,unit); put(1,2,jj); put(1,3,[-x for x in ss]); put(1,4,rr)
    put(2,2,[240*x for x in jj]); put(2,3,[F(0)]*5)
    put(2,4,[120*x for x in jj]); put(3,3,[60*x for x in ss])
    put(3,4,[F(0)]*5); put(4,4,[48*jj[i]+24*rr[i] for i in range(5)])
    def mul(a,b):
        out = [F(0)]*5
        for i in range(5):
            for j in range(5):
                for k in range(5): out[k] += a[i]*b[j]*table[i,j][k]
        return out
    # Integer numerator projectors, common denominator 240.
    pq = [[0,0,1,0,0], [0,0,0,4,0], [0,0,-5,0,10],
          [120,-120,0,-4,0], [120,120,4,0,-10]]
    pp = [[F(x,240) for x in p] for p in pq]
    need([sum(p[i] for p in pp) for i in range(5)] == unit, "projector sum")
    for i in range(5):
        for j in range(5): need(mul(pp[i],pp[j]) == (pp[i] if i == j else [F(0)]*5), "orthogonal idempotents")
    traces = [240,0,240,480,960]
    need([sum(p[i]*traces[i] for i in range(5)) for p in pp] == DIM, "projector ranks")
    return q, s, pq


def lam(j, block):
    if j == 0: return 240 if block == 0 else 0
    if j % 2:
        return 2**(j+1)+(56 if block == 1 else -4) if block in (1,3) else 0
    return 2**(j+1)+{0:112,2:16,4:-8}[block] if block in (0,2,4) else 0


def eigenforms():
    # f(2)=0 and f(4)=1, with u=a5,v=a7.
    coeff = {1:(-F(1,12),64,1280), 3:(F(1,48),-20,-336), 5:(0,1,0), 7:(0,0,1)}
    pairs = [(1,0),(3,0),(1,2),(3,2),(1,4),(3,4)]
    forms = []
    for a,b in pairs:
        z = [F(0)]*3
        for j,c in coeff.items():
            # Canonical simultaneous-antipode quotient divides the signed
            # product operator by 2, without changing its nonzero rank.
            scale = F(sum(comb(j,k)*lam(k,a)*lam(j-k,b) for k in range(j+1)),2)
            for k in range(3): z[k] += scale*c[k]
        forms.append((a,b,2*DIM[a]*DIM[b],z))
    expect = [(-195,151200,3104640),(30,-14400,-347760),(45,-27360,-604800),
              (0,1440,25200),(0,3600,55440),(0,0,5040)]
    need([tuple(z) for a,b,d,z in forms] == expect, "six exact eigenforms")
    return forms


def value(z,u,v): return z[0]+z[1]*u+z[2]*v


def classify(forms):
    def rank(u,v): return sum(d for a,b,d,z in forms if value(z,u,v))
    need(rank(0,0) == 800, "inherited root-sector cubic rank")
    # A rank change occurs only on one of six affine lines. Over C, a point
    # with >=2 vanished eigenforms is one of their rational intersections.
    # Generic lines have exactly their own zero; constants/parallel lines
    # are handled by determinant zero and never create another case.
    points = {(F(0),F(0))}
    for _,_,_,z in forms:
        if z[1]: points.add((-z[0]/z[1],F(0)))
    for f,g in combinations(forms,2):
        x,y = f[3],g[3]
        det = x[1]*y[2]-x[2]*y[1]
        if det:
            points.add(((x[2]*y[0]-x[0]*y[2])/det,
                        (x[0]*y[1]-x[1]*y[0])/det))
    rows = [{"u":str(u),"v":str(v),"rank":rank(u,v),
             "zero_blocks":[[a,b] for a,b,d,z in forms if not value(z,u,v)]}
            for u,v in sorted(points)]
    # On v=0,u!=0: both new blocks 7840+1344 survive, and at most one
    # of the distinct old roots can vanish. The largest old block is 560.
    need(min(rank(u,v) for u,v in points if v == 0 and u) == 9424, "quintic exact minimum")
    need(rank(F(1,608),0) == 9424, "quintic attaining parameter")
    # On v!=0, the 18816 block always survives; the two new zero lines
    # cannot coincide there. The largest possible removed pair is 7840+560.
    generic_line_min = min(28800-d for a,b,d,z in forms if z[1])
    need(min([generic_line_min]+[rank(u,v) for u,v in points if v]) == 20400, "septic exact minimum")
    need(rank(-F(1,160),F(1,2800)) == 20400, "septic attaining parameter")
    return rows


def direct_actions(q, forms):
    ca = [a for a in q if next(x for x in a if x) > 0]
    need(len(ca) == 120, "canonical a-lines")
    features = [lambda a,b:a[0], lambda a,b:a[0]*a[1]*a[2],
                lambda a,b:a[0]*(b[0]**2-b[1]**2),
                lambda a,b:a[0]*a[1]*a[2]*(b[0]**2-b[1]**2),
                lambda a,b:a[0]*b[0]*b[1]*b[2]*b[3],
                lambda a,b:a[0]*a[1]*a[2]*b[0]*b[1]*b[2]*b[3]]
    points = [(F(0),F(0)), (F(1,608),F(0)),(-F(1,160),F(1,2800))]
    count = 0
    for u,v in points:
        cs = [-F(1,12)+64*u+1280*v,F(1,48)-20*u-336*v,u,v]
        den = lcm(*(x.denominator for x in cs))
        fs = {t:int(den*sum(c*t**j for c,j in zip(cs,(1,3,5,7)))) for t in range(-4,5)}
        need(fs[2] == 0 and fs[4] == den, "kernel constraints")
        for (_,_,_,form),feature in zip(forms,features):
            aa,bb = next((a,b) for a in ca for b in q if feature(a,b))
            total = sum(fs[dot(aa,a)+dot(bb,b)]*feature(a,b) for a in ca for b in q)
            expected = den*value(form,u,v)*feature(aa,bb)
            need(total == expected, "direct 28,800-column exact action")
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    q,s,pq = association()
    forms = eigenforms()
    arrangements = classify(forms)
    actions = direct_actions(q,forms)
    # Corrupt eigenforms are checked against the independently evaluated
    # 28,800 actual root-product columns, including degree-five/seven inputs.
    rejected = []
    bad = [(a,b,d,[2*x for x in z]) for a,b,d,z in forms]
    try: direct_actions(q,bad)
    except ValueError as e: rejected.append({"mutation":"omit canonical quotient factor2","gate":str(e)})
    else: raise ValueError("canonical normalization mutation accepted")
    for slot,coordinate in ((3,1),(4,1),(5,2)):
        bad = [(a,b,d,list(z)) for a,b,d,z in forms]
        bad[slot][3][coordinate] += 1
        try: direct_actions(q,bad)
        except ValueError as e: rejected.append({"mutation":"change new-sector eigenform "+str(slot),"gate":str(e)})
        else: raise ValueError("new-sector coefficient mutation accepted")
    need(17*9424 > N and 17*20400 > N, "negative all-stage coverage")
    need(value(forms[5][3],0,F(1,2800)) != 0, "septic top-block control")
    out = {"status":"PASS_H6_ODD_GRAM_RANK_GAP_NO_NEW_KAPPA",
           "canonical_head":"20ecf2891d80b5acf18d980b2164fb44ea7faa90",
           "root_projector_ranks":DIM,"root_projector_integer_numerators":pq,
           "basis_order":["I","antipode","J","Gram S","Hadamard square R"],
           "projector_denominator":240,
           "canonical_root_product_ports":28800,"all_h6_ports":N,
           "eigenforms":[{"sectors":[a,b],"dimension":d,"constant_u_v":[str(x) for x in z]} for a,b,d,z in forms],
           "rank_minima":{"cubic":800,"genuine_quintic":9424,"septic":20400},
           "full_width_private_rank_floor":{"genuine_quintic":17*9424,"septic":17*20400},
           "arrangement_points":arrangements,"direct_actions":actions,
           "rejected_coefficient_controls":rejected,
           "scope":"All odd Gram functions on attainable two-block E8 Gram values, characteristic zero; cost conclusion only for full-width scalar factor return episodes. Not nonisotropic kernels, operator-valued/partial-frame networks or a physical supplier."}
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']+' projectors=5 root_entries=57600 actions='+str(actions)+' ranks=800/9424/20400')


if __name__ == '__main__': main()
