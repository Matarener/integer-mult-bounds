#!/usr/bin/env python3
"""Exact arbitrary-input q2 cleanup block and its single-entry support gate.
Apache-2.0. Substantial OpenAI Codex assistance. No new caller/kappa.
"""
from pathlib import Path
from collections import Counter
import argparse, copy, hashlib, json, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RUNDIR = HERE.parent
PINS = {
    'two-site-continuation/ADMITTED-TWO-SITE-FUSIONS.json': '30d3f569d91304856118796f0c586176d0ad961eff70b09c78fce7532392101f',
    'two-site-continuation/MANIFEST.json': '44f1e264b3087ab8fdb08b4cd6e27befefbba380852b0119321724b7bc41b5da',
    'folded-fusion/SIMPLIFIED-FUSIONS.json': '4491cfe2a1f3e48510b33403b9b50c704865c3b1dc6d659ef5157840654e8fc3',
    'caller-joint/joint_algebra.py': '5782033e347c9b10ad47c01ed12a0a52ea07e901fa9e8f7aa9d3a2a928327232',
    'caller-joint/validate_recipe_links.py': '7457b3672d5a73c584d2073b5d3312e6429fd3f433151f15f8f07da33aa4c59a',
}
for relative, expected in PINS.items():
    if hashlib.sha256((RUNDIR / relative).read_bytes()).hexdigest() != expected:
        raise ValueError('frozen source pin: ' + relative)
sys.path.insert(0, str(RUNDIR / 'caller-joint'))
from joint_algebra import *
from validate_recipe_links import compile_literal, compile_recipe, embedding_circuit


def extra(e):
    return tuple(e.get('extra_global_phase_exponent_by_f_mod4',
                       [e.get('phase_exponent', 0)*(1-r) % 4 for r in range(4)]))


def produce():
    admitted = json.loads((RUNDIR / 'two-site-continuation/ADMITTED-TWO-SITE-FUSIONS.json').read_text())
    source = json.loads((RUNDIR / 'folded-fusion/SIMPLIFIED-FUSIONS.json').read_text())
    f = next(f for f in admitted['fixtures'] if f['q'] == 2)
    old = next(f for f in source['fixtures'] if f['q'] == 2)
    E = f['events']; m, n, cut = f['ambient_arity'], f['banks'], 69
    need(E[cut]['label'] == 'final independent a J query', 'exact local physical entrance cut')
    suffix = copy.deepcopy(E[cut:])
    inverse = copy.deepcopy(f['inverse_events'][:len(suffix)])
    compiled = {}
    used_pool = {}
    # Every unchanged suffix unary retains an explicit source-event binding.
    for direction, events in [('forward', suffix), ('inverse', inverse)]:
        for e in events:
            if e['kind'] in ('ADD', 'SCALE', 'BANK_SWAP'):
                continue
            source_event = old['events'][e['source_event_ordinal']]
            g = qc.decode(source_event, m)
            if e['source_operator_is_adjoint']:
                g = g.inv()
            e['x_monomial'] = g.data()
            op = compile_literal(e['one_coordinate_literal_circuit'], m)
            need(op.tab == tuple(tuple(t) for t in e['one_coordinate_tableau']), 'actual signed source unary')
            need(ce.rank(x for x,z,p in op.tab[m:]) == e['rank_per_f'], 'actual source unary native rank')
            # The physical definition is compared with the pinned symbolic
            # coordinate definition using a separately constructed circuit.
            from joint_prefix import inverse_transpose
            circ=[]
            for i,a in enumerate(g.alpha):
                if a%4 == 1:circ.append(('C',1<<i,1))
                elif a%4 == 2:circ.extend([('C',1<<i,1)]*2)
                elif a%4 == 3:circ.append(('C',1<<i,-1))
            for i,row in enumerate(g.quad):
                for j in range(i+1,m):
                    if row>>j&1:circ.extend([('C',1<<i,1),('C',1<<j,1),('C',(1<<i)|(1<<j),-1)])
            circ.extend([('P',inverse_transpose(g.rows)),('D',(0,)*m,tuple(2*((g.offset>>i)&1)for i in range(m))),
                         ('phase',(g.constant+g.global_phase)%4)])
            same(compile_literal(circ,m), op, 'actual source unary exact Gaussian phase')
            need(extra(e) == tuple(g.global_phase*(1-r)%4 for r in range(4)), 'actual all-f source tensor phase correction')
            if e['kind'] == 'NATIVE':
                key=e['native_recipe_id']; rec=f['native_recipe_pool'][key]
                local_n=len(rec['one_coordinate_tableau'])//2
                selected=compile_recipe(rec['selected_native_recipe'],local_n)
                full=compile_literal(embedding_circuit(selected.circuit,e['recipe_embedding'],m),m)
                same(full,op,'every used forward/inverse selected source recipe and embedding')
                need(tuple(rec['extra_global_phase_exponent_by_f_mod4'])==extra(e),'selected source recipe tensor-phase correction')
                used_pool[key]=rec
            compiled[(direction,e['label'])] = op
    M = qc.replay(suffix,n,m); Mi = qc.replay(inverse,n,m)
    need(mm(M,Mi) == mm(Mi,M) == eye(n,m), 'complete serialized suffix inverse both orders on every arbitrary input')
    A = qc.decode(next(e for e in suffix if e['label']=='final independent a J query'),m)
    W = qc.decode(next(e for e in suffix if e['label']=='dual Q1 recovery'),m)
    reverse_events = [e for e in suffix if e['label'] in ('w reverse2 ADDRESS','w reverse2 selected native2','final extraction D_final inverse sign')]
    RR = qc.identity(m)
    for e in reverse_events:RR = qc.decode(e,m) @ RR
    F5 = prefix(m,5); Q = j_operator(m).inv() @ plane_swap(m,0,1) @ n_pair(m,0).inv() @ j_operator(m) @ j_operator(m)
    need(mono(A) == mono(F5@j_operator(m)@F5.inv()), 'actual A definition')
    need(mono(W) == mono(F5@Q.inv()@F5.inv()), 'actual W definition')
    minus = qc.Mono(qc.identity(m).rows,0,(0,)*m,(0,)*m,0,2)
    need(mono(RR) == mono(minus@n_pair(m,5)@plane_swap(m,0,5)), 'actual reverse-current operator and minus phase')
    I = mono(qc.identity(m)); Z = {}; IW = add(I,scale(mono(W),-1))
    expected = [[{}for _ in range(n)]for _ in range(n)]
    expected[0][0] = mono(A)
    expected[1][0] = scale(mono(W@A),-1); expected[1][2] = IW; expected[1][3] = mono(W@RR); expected[1][4] = IW
    expected[2][0] = scale(mono(A),-1); expected[2][2] = I
    expected[3][0] = scale(mono(A@W@A),-1); expected[3][1] = mono(A)
    expected[3][2] = product(mono(A),IW)
    expected[3][3] = product(mono(A),product(scale(IW,-1),mono(RR)))
    expected[3][4] = scale(mono(A@W),-1)
    expected[4][4] = I; expected[5][5] = I
    need(M == expected, 'literal entire local block equals six-by-six symbolic operator target')
    need(len(M[1][3]) == 1 and qc.rank(next(iter(M[1][3])).polar()) == 6, 'single actual arity-six input3/output1 coefficient')
    # Independently lower that exact coefficient to certify its uniform row
    # support. This recipe is a witness, not a proposed complete cleanup.
    C = ce.ident(m); ce_extra = [0]*4
    for e in reverse_events + [next(e for e in suffix if e['label']=='dual Q1 recovery')]:
        C = C.then(compile_literal(e['one_coordinate_literal_circuit'],m))
        ce_extra = [(x+y)%4 for x,y in zip(ce_extra,extra(e))]
    need(ce.rank(x for x,z,p in C.tab[m:]) == 6, 'coefficient physical B-rank6')
    recipe, lowered = ce.lower_child(C)
    need(recipe['rank'] == 6, 'explicit selected Fourier rank for support witness')
    same(lowered,C,'support-witness selected child exact Gaussian phase')
    same(compile_recipe(recipe,m),C,'independent support-witness recipe recompilation')
    before = sum(e['rank_per_f']for e in E[:cut]if e['kind']=='NATIVE')
    local_hist = Counter(e['rank_per_f']for e in suffix if e['kind']=='NATIVE')
    local = sum(r*c for r,c in local_hist.items())
    need(before == 66 and local == 10 and before+local == f['native_mass'] == 76, 'complete unchanged-prefix plus local-native bill')
    need(f['stock'] == 72 and f['stock']-before == 6, 'exact below-stock local threshold')
    mutant = [[dict(v) for v in row] for row in M];mutant[1][3] = {}
    need(mutant != M, 'discarding arbitrary incoming bank3 changes an original coefficient')
    omitted_reverse = [e for e in suffix if e['label'] != 'w reverse2 selected native2']
    wrong = qc.replay(omitted_reverse,n,m)
    need(wrong != M and len(wrong[1][3]) == 1, 'omitting the reverse-current native query changes the arbitrary-input block')
    need(qc.rank(next(iter(wrong[1][3])).polar()) == 4, 'omitted reverse query spuriously lowers the witness rank')
    need(not any(e['kind']=='SCALE'for e in suffix),'actual suffix needs no hidden SCALE cancellation')
    return dict(status='PASS_EXACT_COUPLED_CLEANUP_BLOCK_AND_SUPPORT_BOUNDARY', no_new_kappa=True,
                producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                source_pins=[dict(path=str(RUNDIR/p),sha256=h)for p,h in PINS.items()],
                q=2,banks=n,ambient_arity=m,cut_event_ordinal=cut,cut_label=E[cut]['label'],
                unchanged_prefix_native_mass=before,local_native_histogram=dict(sorted(local_hist.items())),local_native_mass=local,
                complete_mass=76,endpoint_stock=72,strict_improvement_requires_local_native_mass_less_than=6,
                events=suffix,inverse_events=inverse,native_recipe_pool=used_pool,
                all_original_local_columns=n,literal_inverse_orders=2,
                complete_local_matrix=sm(M),complete_local_inverse=sm(Mi),
                operators=dict(A=A.data(),W=W.data(),R=RR.data()),
                unavoidable_entry=dict(row=1,column=3,operator=serial(M[1][3]),native_arity_per_f=6,
                                      one_coordinate_tableau=C.tab,one_coordinate_literal_circuit=C.circuit,
                                      extra_global_phase_exponent_by_f_mod4=ce_extra,
                                      support_witness_selected_native_recipe=recipe,
                                      role='Only certifies row support of an entry; not an executed new cleanup/native invoice.'),
                all_f_support_inequality='sum_native_arities_R_f + binary_fullbank_ADD_count_S_f >=6f',
                constant_scan_consequence='For this exact local interface, bounded-in-f ADD count implies liminf R_f/f>=6; unchanged prefix66f then gives asymptotic total>=72f.',
                finite_f_scope='R_f>=6f-S_f, not a pointwise native-only6f lower bound when S_f is positive.',
                non_native_event_counts=dict(Counter(e['kind']for e in suffix if e['kind']!='NATIVE')),
                negative_controls=['Discarding arbitrary incoming bank3 deletes a nonzero arity6 coefficient and is rejected.',
                                   'Omitting reverse-current N5 changes the exact matrix and spuriously lowers entry rank6 to4; rejected.'],
                limits=['Any replacement must realize this exact current-input matrix on all arbitrary banks, not only a clean/correlated subspace.',
                        'Arbitrary extra dirty registers restored are permitted by the support proof; their identity coefficient rows start with support1.',
                        'Native rank mass lower bound uses monomial adapters/scalars of row support1 and binary ADD/COPY gates, counting every support-doubling scan.',
                        'Growing O(f) ADD counts, partial/fused scan machine models, changed input/output gauges or an earlier fresh/source/coupled cut require separate analysis.',
                        'No expensive enumeration, new full cleanup factorization, supplier, owner, BIT, recurrence or kappa admission.'])


def main():
    p = argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    result=json.loads(json.dumps(produce()));out=HERE/'LOCAL-BLOCK.json'
    if a.write:out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(out.read_text())==result,'saved coupled local block')
    print(result['status'],'fixed66 + local10; unavoidable entry6f; no bounded-scan local bill<6f')


if __name__=='__main__':main()
