#!/usr/bin/env python3
"""Exact finite cross-cut fusion screen, not a frame/random search.

Freeze all scalar gates, ADDRESSs and native sites except one existing
prefix native. Delete an arbitrary nonempty subset of tail native sites.
The unique correction at every prefix cut is computed over the complete
Gaussian noncommutative operator algebra, with all f residues retained.
Apache-2.0. Substantial OpenAI Codex assistance. No new kappa.
"""
from pathlib import Path
import hashlib, json, sys, time
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'inputs'))
from joint_algebra import F, qc, need, mono, eye, mm, product, add, scale, serial, sm, ZERO, ONE


def inverse(events, m):
    out = []
    for e in reversed(events):
        e = dict(e)
        if e['kind'] == 'ADD': e['coefficient'] = str(-F(e['coefficient']))
        elif e['kind'] == 'SCALE': e['coefficient'] = str(1/F(e['coefficient']))
        elif e['kind'] != 'BANK_SWAP': e['x_monomial'] = qc.decode(e, m).inv().data()
        out.append(e)
    return out


def conjugate_back(C, e, m):
    """Current cut pullback C <- E^-1 C E, no commutation assumed."""
    C = [[dict(x) for x in row] for row in C]
    kind = e['kind']
    if kind == 'ADD':
        d, s, c = e['dst'], e['src'], F(e['coefficient'])
        C[d] = [add(x, scale(y, -c)) for x, y in zip(C[d], C[s])]
        for row in C: row[s] = add(row[s], scale(row[d], c))
    elif kind == 'BANK_SWAP':
        i, j = e['banks']; C[i], C[j] = C[j], C[i]
        for row in C: row[i], row[j] = row[j], row[i]
    elif kind == 'SCALE':
        b, c = e['bank'], F(e['coefficient'])
        C[b] = [scale(x, 1/c) for x in C[b]]
        for row in C: row[b] = scale(row[b], c)
    else:
        b = e['bank']; G = mono(qc.decode(e, m)); Gi = mono(qc.decode(e, m).inv())
        C[b] = [product(Gi, x) for x in C[b]]
        for row in C: row[b] = product(row[b], G)
    return C


def bank_only(C, bank, I):
    return all(C[i][j] == I[i][j] for i in range(len(C)) for j in range(len(C)) if (i,j) != (bank,bank))


def screen(f,include_zero=False):
    q, n, m = f['q'], f['banks'], f['ambient_arity']
    P, T = f['prefix_events'], f['tail_events']; I = eye(n,m)
    oldT = qc.replay(T,n,m); oldP = qc.replay(P,n,m)
    G = mono(qc.decode(next(e for e in reversed(f['events']) if e.get('native_recipe_id') == 'tail-J'),m))
    # Complete target is read from frozen actual all-input word, not a right gauge.
    target = qc.replay(f['events'],n,m)
    need(mm(oldT,oldP)==target, 'frozen source decomposition')
    base_mass = f['native_mass']; sites = [i for i,e in enumerate(T) if e['kind']=='NATIVE']
    prefix_sites = [i for i,e in enumerate(P) if e['kind']=='NATIVE'or(include_zero and e['kind']not in('ADD','BANK_SWAP','SCALE'))]
    accepted = []; nonlocal_rows = 0; combinations = 0; checks = 0
    failures = {}; start = time.monotonic()
    for mask in range(1,1<<len(sites)):
        removed = {sites[j] for j in range(len(sites)) if mask>>j&1}
        newT = [e for i,e in enumerate(T) if i not in removed]
        invnewT = qc.replay(inverse(newT,m),n,m)
        # T_new P_new = T_old P, so P_new = C P, C=T_new^-1 T_old.
        C = mm(invnewT,oldT); H = C
        removed_mass = sum(T[i]['rank_per_f'] for i in removed)
        need(mm(qc.replay(newT,n,m),C)==oldT,'tail correction direction')
        combinations += 1
        for at in range(len(P)-1,-1,-1):
            e = P[at]
            if at in prefix_sites:
                checks += 1; b = e['bank']
                if bank_only(C,b,I):
                    replacement = product(C[b][b],mono(qc.decode(e,m)))
                    # A native Clifford has one Gaussian X-character monomial.
                    if len(replacement)==1:
                        g, coeff = next(iter(replacement.items()))
                        unit = all(coeff[2*r]**2+coeff[2*r+1]**2==1 for r in range(4))
                        if unit:
                            rank=qc.rank(g.polar());mass=base_mass-removed_mass-e['rank_per_f']+rank
                            accepted.append({'removed_tail_sites':sorted(removed),'removed_tail_labels':[T[i]['label'] for i in sorted(removed)],
                                'prefix_site':at,'prefix_label':e['label'],'prefix_bank':b,'old_prefix_rank':e['rank_per_f'],
                                'removed_tail_rank':removed_mass,'replacement_rank':rank,'complete_mass':mass,'stock':f['stock'],
                                'replacement':serial(replacement),'cut_correction':sm(C)})
                        else: failures['nonunit_scalar'] = failures.get('nonunit_scalar',0)+1
                    else: failures['non_Clifford_sum'] = failures.get('non_Clifford_sum',0)+1
                else: nonlocal_rows += 1
            C = conjugate_back(C,e,m)
        need(mm(oldP,C)==mm(H,oldP), 'complete pullback through original prefix')
    accepted.sort(key=lambda a:(a['complete_mass'],a['removed_tail_sites'],a['prefix_site']))
    return {'q':q,'n':n,'m':m,'frozen_complete_mass':base_mass,'stock':f['stock'],'tail_native_sites':sites,
        'prefix_native_sites':sum(e['kind']=='NATIVE'for e in P),'prefix_candidate_sites':len(prefix_sites),
        'nonempty_tail_subsets':combinations,'candidate_cut_checks':checks,'not_single_bank':nonlocal_rows,'other_rejections':failures,'include_zero_rank_prefix_unaries':include_zero,
        'accepted_single_site_fusions':accepted,'best_complete_mass':min((a['complete_mass'] for a in accepted),default=base_mass),
        'elapsed_seconds':time.monotonic()-start,'domain':'q as listed; every original independent bank; exact Gaussian coefficients for every f mod4 and tensor family.'}


def main():
    source=HERE/'inputs/DUAL-CORE-RANK-ONLY.json'
    need(hashlib.sha256(source.read_bytes()).hexdigest()=='7b4828681a86da9477328a7b04f85adf535abc834ff0aee935f91a65a1ee2783','frozen dual source pin')
    f=[x for x in json.loads(source.read_text())['fixtures'] if x['name']=='folded-dual']
    results=[]
    for fixture in f:
        results.append(screen(fixture));(HERE/'SINGLE-SITE-ABSORPTION.json').write_text(json.dumps({'results':results,'no_new_kappa':True},indent=2,sort_keys=True)+'\n')
        r=results[-1];print('q',r['q'],'cuts',r['candidate_cut_checks'],'accepted',len(r['accepted_single_site_fusions']),'best',r['best_complete_mass'],'stock',r['stock'],flush=True)


if __name__=='__main__':main()
