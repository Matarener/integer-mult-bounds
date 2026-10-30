#!/usr/bin/env python3
"""Actual full-rank H6 subfamilies with cyclic partial-frame mixed channels.

Two ± source channels per group, all ordinary dirty, no private compensation
return. Frame visits increase along cyclic arcs. Whole K+C word included.
Finite r=2..7 E8 family; abstract arc lemma is written separately.
"""
from fractions import Fraction as F
from pathlib import Path
import importlib.util, json, hashlib

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('mixed_base',HERE/'mixed_rectangle.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
need = m.need


def fixture(r):
    n = 2*r
    beta = (2,2,0,0,0,0,0,0)
    gamma = (2,-2,0,0,0,0,0,0)
    aa = []
    for g in range(r):
        a = [0]*8; a[0] = 2; a[g+1] = -2; aa.append(tuple(a))
    ports = [a+b for a in aa for b in (beta,gamma)]
    labels,indices = m.actual_labels(ports)
    planes = [m.basis(labels[2*g:2*g+2]) for g in range(r)]
    arcs = {(g,k):m.basis(v for j in range(k) for v in planes[(g+j)%r])
            for g in range(r) for k in range(1,r)}
    need(all(len(f) == k+1 for (g,k),f in arcs.items()),'actual arc dimensions')
    need(all(m.included(arcs[g,k],m.perp(labels[2*((g+k)%r)+z]))
             for g in range(r) for k in range(1,r) for z in range(2)), 'whole opposite target cap')
    need(all(m.included(arcs[g,k],arcs[g,k+1]) for g in range(r) for k in range(1,r-1)), 'helper nested arcs')
    need(all(m.included(arcs[(t-k)%r,k],arcs[(t-k-1)%r,k+1])
             for t in range(r) for k in range(1,r-1)), 'target nested preceding arcs')
    k = [[F(m.dot(p,q)**3-4*m.dot(p,q),48) for q in ports] for p in ports]
    c = [[F(int(i == j))-k[i][j] for j in range(n)] for i in range(n)]
    need(c == [[F(0) if i//2 == j//2 else F(-5 if i%2 == j%2 else 1,16)
                for j in range(n)] for i in range(n)], 'actual full-rank block compensation')
    # L is blockwise ± source mixing; R scatters each channel to all other groups.
    l = [[F(0)]*n for _ in range(n)]
    decoder = [[F(0)]*n for _ in range(n)]
    for g in range(r):
        l[2*g][2*g] = l[2*g][2*g+1] = 1
        l[2*g+1][2*g] = 1; l[2*g+1][2*g+1] = -1
        for t in range(n):
            if t//2 != g:
                decoder[t][2*g] = -F(1,8)
                decoder[t][2*g+1] = F(3 if t%2 else -3,16)
    need(all(sum(decoder[i][g]*l[g][j] for g in range(n)) == c[i][j]
             for i in range(n) for j in range(n)), 'exact C=R L including exceptional t3')
    starts = {f'x{i}':m.basis([labels[i]]) for i in range(n)}
    starts.update({f'y{i}':() for i in range(n)})
    starts.update({f'c{i}':() for i in range(n)})
    starts.update({f'h{i}':() for i in range(n)})
    ends = {a:m.FULL for a in starts}; ends.update({f'y{i}':m.perp(labels[i]) for i in range(n)})
    ev = []
    def add(dst,src,q,tag):
        if q:ev.append({'op':'add','dst':dst,'src':src,'q':str(q),'tag':tag})
    def climb(reg,frame,tag):ev.append({'op':'climb','register':reg,'frame':list(frame),'tag':tag})
    for t in range(n):
        for j in range(n):
            add(f'y{t}',f'h{j}',-decoder[t][j],'comp_prefix')
            add(f'y{t}',f'c{j}',-k[t][j],'K_prefix')
    for g in range(r):
        for i in range(2*g,2*g+2):climb(f'x{i}',planes[g],'source_plane')
        for j in range(2*g,2*g+2):
            climb(f'h{j}',planes[g],'mixed_gather_plane')
            for i in range(2*g,2*g+2):add(f'h{j}',f'x{i}',l[j][i],'comp_gather')
    for i in range(n):climb(f'x{i}',m.FULL,'source_full')
    for i in range(n):
        climb(f'c{i}',m.FULL,'K_center_full');add(f'c{i}',f'x{i}',F(1),'K_gather')
    for j in range(n):ev.append({'op':'private','center':f'c{j}',
        'targets':[[f'y{i}',str(k[i][j])] for i in range(n) if k[i][j]],'tag':'K_private'})
    for i in range(n):add(f'c{i}',f'x{i}',-F(1),'K_restore')
    for depth in range(1,r):
        for g in range(r):
            target = (g+depth)%r
            frame = arcs[g,depth]
            for j in range(2*g,2*g+2):climb(f'h{j}',frame,'helper_arc')
            for t in range(2*target,2*target+2):
                climb(f'y{t}',frame,'target_arc')
                for j in range(2*g,2*g+2):add(f'y{t}',f'h{j}',decoder[t][j],'comp_scatter')
    for i in range(n):climb(f'y{i}',m.perp(labels[i]),'target_cap')
    for j in range(n):
        climb(f'h{j}',m.FULL,'mixed_restore_full')
        for i in range(n):add(f'h{j}',f'x{i}',-l[j][i],'comp_restore')
    return {'r':r,'N':n,'ports_doubled':ports,'source_indices':indices,'labels':labels,
            'planes':[list(x) for x in planes],'arcs':{str(g)+':'+str(d):list(f) for (g,d),f in arcs.items()},
            'K':[[str(q) for q in row] for row in k],'C':[[str(q) for q in row] for row in c],
            'L':[[str(q) for q in row] for row in l],'R':[[str(q) for q in row] for row in decoder],
            'starts':{a:list(f) for a,f in starts.items()},'ends':{a:list(f) for a,f in ends.items()},'events':ev}


def matrix_check(fix):
    # Independent closed block products, rather than a scalar-event interpreter.
    n = fix['N']; dim = 4*n
    k = [[F(q) for q in row] for row in fix['K']]
    l = [[F(q) for q in row] for row in fix['L']]
    rr = [[F(q) for q in row] for row in fix['R']]
    def eye():return [[F(int(i == j)) for j in range(dim)] for i in range(dim)]
    rows = eye(); dual = eye()
    def block(entries):
        # All entries in one block have pairwise-zero products.
        for dst,src,q in entries:
            rows[dst] = [x+q*y for x,y in zip(rows[dst],rows[src])]
            dual[src] = [x-q*y for x,y in zip(dual[src],dual[dst])]
    block([(n+i,2*n+j,-k[i][j]) for i in range(n) for j in range(n) if k[i][j]]
          +[(n+i,3*n+j,-rr[i][j]) for i in range(n) for j in range(n) if rr[i][j]])
    block([(3*n+i,j,l[i][j]) for i in range(n) for j in range(n) if l[i][j]])
    block([(2*n+i,i,F(1)) for i in range(n)])
    block([(n+i,2*n+j,k[i][j]) for i in range(n) for j in range(n) if k[i][j]])
    block([(2*n+i,i,-F(1)) for i in range(n)])
    block([(n+i,3*n+j,rr[i][j]) for i in range(n) for j in range(n) if rr[i][j]])
    block([(3*n+i,j,-l[i][j]) for i in range(n) for j in range(n) if l[i][j]])
    a,b = eye(),eye()
    for i in range(n):a[n+i][i] += 1;b[i][n+i] -= 1
    need(rows == a and dual == b,'independent all-input block closure')
    # C=(J-I) tensor B: its eigenvalues are -(r-1)/4,1/4,
    # -3(r-1)/8,3/8, all nonzero. K=I-C is also invertible.
    r=fix['r']
    ev=[-F(r-1,4),F(1,4),-F(3*(r-1),8),F(3,8)]
    need(all(x and x != 1 for x in ev),'C and restricted K both full rank')
    return 2*dim*dim


def main():
    results=[];controls=[]
    for r in range(2,8):
        fix=fixture(r);n=2*r
        forward=m.replay(fix);dual=m.replay(fix,True)
        need(forward['rank_mass'] == dual['rank_mass'] == 83*n,'whole paid rank mass')
        need(forward['scalar_primitives_before_real_doubling'] == n*(72*r-37),'whole forward Horner bill')
        need(dual['scalar_primitives_before_real_doubling'] == n*(72*r-34),'whole dual Horner bill')
        independent=matrix_check(fix)
        for tag in ('comp_prefix','comp_gather','comp_scatter','comp_restore','K_prefix','K_private','helper_arc','target_arc'):
            for d in (False,True):
                try:m.replay(fix,d,tag)
                except ValueError as e:controls.append({'r':r,'omit':tag,'dual':d,'gate':str(e)})
                else:
                    # At r=2 helpers already occupy the only U, so its redundant
                    # arc CLIMB is intentionally unnecessary.
                    need(r == 2 and tag == 'helper_arc','meaningful mutation rejected')
        results.append({'r':r,'N':n,'C_rank':n,'restricted_K_rank':n,'compensation_helpers':n,
                        'edge_baseline':4*r*(r-1),'private_K_rank':17*n,
                        'independent_operator_entries':independent,
                        'forward':forward,'dual':dual,'fixture':fix})
    out={'status':'PASS_ACTUAL_H6_CYCLIC_MIXED_FULL_RANK_SUBFAMILIES_NO_NEW_KAPPA',
         'source_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','cases':results,'controls':controls,
         'limits':'Actual E8 examples r=2..7 only, N=4..14. Whole subfamily K has rankN and private C=17N, hence fails standalone coverage for every L. Does not give the full30960-port network or permit block tiling with the unchanged816-center K.',
         'source_sha256':hashlib.sha256((HERE/'mixed_rectangle.py').read_bytes()).hexdigest()}
    (HERE/'CYCLIC-MIXED-RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']+' r=2..7 controls='+str(len(controls)))
    for x in results:print('r',x['r'],'N',x['N'],'helpers',x['compensation_helpers'],'edge',x['edge_baseline'],'rank',x['forward']['rank_mass'],'primitives',x['forward']['scalar_primitives_before_real_doubling'],x['dual']['scalar_primitives_before_real_doubling'])


if __name__=='__main__':main()
