#!/usr/bin/env python3
"""Selective P112 co-delivery: exact composition, endpoint gap, scoped repair.

Standard library only. Substantial OpenAI Codex assistance; Apache-2.0.
This does not construct a native decoder or admit a supplier.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
CHEAP = (0, 3, 10, 13)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def module(path, name):
    m = types.ModuleType(name)
    m.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), m.__dict__)
    return m


def constant(path, name):
    return next(ast.literal_eval(n.value) for n in ast.parse(path.read_text()).body
                if isinstance(n, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == name for t in n.targets))


def subtract(a, b):
    return [[x-y for x, y in zip(r, s)] for r, s in zip(a, b)]


def rank(a):
    a = [[Q(x) for x in row] for row in a]
    k = 0
    for j in range(len(a[0])):
        p = next((i for i in range(k, len(a)) if a[i][j]), None)
        if p is None:
            continue
        a[k], a[p] = a[p], a[k]
        c = a[k][j]
        a[k] = [x/c for x in a[k]]
        for i in range(len(a)):
            if i != k and a[i][j]:
                c = a[i][j]
                a[i] = [x-c*y for x, y in zip(a[i], a[k])]
        k += 1
        if k == len(a):
            break
    return k


def run():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for f in pins['retained_sources'] + pins['selected_archive']['members']:
        raw = (HERE/f['retained_path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == f['sha256'],
             'changed retained source: '+f['retained_path'])
        if 'payload_sha256' in f:
            need(hashlib.sha256(gzip.decompress(raw)).hexdigest()
                 == f['payload_sha256'], 'archive member payload')
    vendor = HERE/'vendor/research'
    scatter = module(vendor/'p112-scatter-orientation/verify_scatter.py', 'scatter')
    basis = module(vendor/'p112-tetrad-dual-anchor-screen/verify.py', 'basis')
    geom = module(vendor/'p112-tetrad-local-decoder/verify.py', 'geometry')
    co = module(vendor/'p112-centre-co-delivery/verify.py', 'co')
    ceiling = module(vendor/'complex-local-word-ceiling/ceiling.py', 'ceiling')
    perm = constant(vendor/'selected-p112-tetrad-rank32-route/verify.py', 'ROOT_TO_PORT')
    mm, tr, inv, eye = scatter.mm, scatter.tr, scatter.inv, scatter.eye
    support = lambda a: sum(x != 0 for row in a for x in row)
    word = json.loads(gzip.decompress((HERE/'vendor/word.json.gz').read_bytes()))
    events = json.loads(gzip.decompress((HERE/'vendor/programs.json.gz').read_bytes()))['forward']
    recorded = json.loads((vendor/'p112-centre-co-delivery/RESULT.json').read_text())
    need((word['v'], word['R'], word['h']) == (112, 480, 9), 'word dimensions')
    roots, frame = geom.roots_and_frame()
    live = sorted(set(roots)-set(frame))
    need(sorted(perm) == list(range(112)), 'port permutation')
    need(all(((geom.dot(x,y)//4+1) % 2)
             == ((word['ports'][perm[i]] & word['ports'][perm[j]]).bit_count() % 2)
             for i,x in enumerate(live) for j,y in enumerate(live)), '12544 label pairs')
    centers = {r:k for k,r in enumerate(word['centers'])}
    s = [[Q(0)]*8 for _ in range(112)]
    for kind,dest,src,num,den,*_ in word['cut']:
        need(kind == 'add' and 112 <= dest < 224 and src in centers,
             'destination-first canonical scatter')
        s[dest-112][centers[src]] += Q(num,den)
    native_cut = Counter((e[1][1][1]-112,e[1][2][1],Q(e[1][3],e[1][4]))
        for e in events if e[0]=='scalar' and e[1][0]=='add'
        and e[1][1][0]=='L' and 112 <= e[1][1][1] < 224 and e[1][2][0]=='C')
    need(native_cut == Counter((i,k,x) for i,row in enumerate(s)
                              for k,x in enumerate(row) if x), '176 native scatter bindings')
    need(sum(native_cut.values()) == 176, 'cut size')
    groups = defaultdict(list)
    for i,root in enumerate(live):
        c = [geom.dot(root,f)//4 for f in frame]
        t = tuple(j for j,x in enumerate(c) if x)
        groups[t,sum(x < 0 for x in c) % 2].append((i,c))
    omitted = co.center_root_labels(geom,live,frame,perm,word['ports'])
    native_result = json.loads((vendor/'selected-centre-native-lift/RESULT.json').read_text())
    slots, _ = co.native_center_binding(word,omitted,native_result)
    need(slots == [7,5,4,6,3,1,0,2], 'centre label binding')
    pair = [sum(1 << j for j,q in enumerate(word['ports'])
                if (p&q).bit_count()%2) for p in word['ports']]
    cp = [sum(1 << j for j,q in enumerate(word['ports'])
              if (p&q).bit_count()%2) for p in omitted]
    labels = {('L',i):x for i,x in enumerate(word['start'])}
    for event in events:
        if event == ['phase','centers']:
            break
        if event[0] == 'climb':
            need(labels['L',event[2]] == event[3], 'pre-cut ordinary frame')
            labels['L',event[2]] = event[4]
    need(all(labels['L',i] == 0 for i in range(112,224)), 'all targets frame zero')
    need(set(centers).isdisjoint(range(112,224)), 'carriers disjoint from targets')
    blocks, receipts = [], []
    mixed = [[Q(0)]*112 for _ in range(112)]
    original = [[Q(0)]*112 for _ in range(112)]
    jglobal = [[Q(0)]*112 for _ in range(8)]
    profile = Counter()
    repair_profile = Counter()
    scratch_receipt = None
    for index,t in enumerate(sorted({t for t,_ in groups})):
        even,odd = groups[t,0],groups[t,1]
        e0 = [[c[j] for j in t] for _,c in even]
        e1 = [[c[j] for j in t] for _,c in odd]
        e = e0+e1
        ports = [perm[i] for i,_ in even+odd]
        cross = mm(mm(e0,tr(e1)),basis.D_EVEN_SUM)
        need(all(x % 4 == 0 for row in cross for x in row), 'integer kernel basis')
        u = tr([[-x/4 for x in row] for row in cross]+basis.D_EVEN_SUM)
        u += [eye(8)[i] for i in (0,5,6,7)]
        u = [[int(x) for x in row] for row in u]
        need(basis.determinant(u) == -1, 'unimodular completion')
        k,m = mm(e,tr(e)),mm(u,e)
        uk = mm(m,tr(e))
        sb = [s[p] for p in ports]
        reader = mm(tr(inv(u)),sb)
        hybrid = sb[:4]+reader[4:]
        c = subtract(sb,hybrid)
        cm = mm(tr(c),m)
        j = mm(cm,tr(e))
        need(mm(tr(sb),subtract(uk,k)) == j, 'abstract centre correction')
        need(mm(tr(hybrid),uk) == mm(tr(sb),k), 'hybrid reader identity')
        source_ranks = [len(word['frames'][labels['L',p]]) for p in ports]
        aug_ranks,old_ranks,repair_ranks = [],[],[]
        for q in range(4):
            mask = sum(1 << ports[i] for i in range(8) if e[i][q])
            aug_ranks.append(co.output_term_rank(mask,[ports[i] for i in range(8) if m[i][q]],
                [i for i in range(8) if cm[i][q]],slots,pair,cp))
            old_ranks.append(co.output_term_rank(mask,ports,[],slots,pair,cp))
            residual = subtract(e,m)
            repair_ranks.append(co.output_term_rank(mask,[ports[i] for i in range(8) if residual[i][q]],
                [],slots,pair,cp))
        need(aug_ranks == [1]*4 and old_ranks == [2]*4, 'actual support pair ranks')
        need(support(cm) == recorded['co_delivery']['block_supports'][index]
             ['C_transpose_M_centre_coefficients'], 'pinned correction support')
        chosen = index in CHEAP
        if chosen:
            repair_profile.update(repair_ranks)
        target = uk if chosen else k
        for i,p in enumerate(ports):
            for z,q in enumerate(ports):
                mixed[p][q] = target[i][z]
                original[p][q] = k[i][z]
        if chosen:
            for slot in range(8):
                for z,q in enumerate(ports):
                    jglobal[slot][q] += j[slot][z]
        profile.update(aug_ranks if chosen else old_ranks)
        us = mm(u,sb)
        b = {'ports':ports,'u':u,'us':us,'hybrid':hybrid,
             'reduce_ops':basis.reduce_to_identity(u)}
        blocks.append(b)
        receipts.append({'index':index,'tetrad':list(t),'ports':ports,'selected':chosen,
            'centre_coefficients':support(cm),'augmented_term_ranks':aug_ranks,
            'natural_port_repair_term_ranks':repair_ranks,
            'port_defect_rank_Q':rank(subtract(uk,k)),
            'literal_source_frame_ranks_at_pre_B':source_ranks,
            'old_scatter_support':support(sb),'correct_US_support':support(us),
            'correct_US_top_four_support':support(us[:4]),
            'E':e,'U':u,'M':m,'minus_CtM':[[-x for x in row] for row in cm]})
        if index == 0:
            # A chronological scalar control on an explicitly DIFFERENT contract:
            # immutable independent x[8], dirty y[8], dirty c[8], dirty scratch h.
            # Every row is its exact coefficient vector on all 25 initial roles.
            rows = [eye(25)[i] for i in range(25)]
            expected = [r[:] for r in rows]
            for i in range(8):
                for z in range(8):
                    expected[8+i][z] += uk[i][z]
                    expected[16+i][z] -= j[i][z]
            adds = 0
            for q in range(4):
                outputs = [(8+i,m[i][q]) for i in range(8) if m[i][q]]
                outputs += [(16+i,-cm[i][q]) for i in range(8) if cm[i][q]]
                inputs = [(i,e[i][q]) for i in range(8) if e[i][q]]
                for dest,z in outputs:
                    rows[dest] = [a-z*b for a,b in zip(rows[dest],rows[24])]; adds += 1
                for src,z in inputs:
                    rows[24] = [a+z*b for a,b in zip(rows[24],rows[src])]; adds += 1
                for dest,z in outputs:
                    rows[dest] = [a+z*b for a,b in zip(rows[dest],rows[24])]; adds += 1
                for src,z in inputs:
                    rows[24] = [a-z*b for a,b in zip(rows[24],rows[src])]; adds += 1
            need(rows == expected, 'all 25 dirty scalar columns and scratch restoration')
            need(adds == 2*(support(e)+support(m)+support(cm)), 'full dirty scratch ADD bill')
            scratch_receipt = {'columns_checked':25,'adds':adds,'private_dirty_scratch_roles':1,
                'model_centre_output_roles':8,
                'actively_updated_centre_output_roles':sum(any(row) for row in cm),
                'scratch_restored':True,
                'native_COPY':False,'source_acquisition_and_chart_adapters':'UNSUPPLIED',
                'does_not_realize_selected_pre_B_contract':True}
    need(profile == Counter({1:16,2:40}), 'selective augmented support rank profile')
    need([r['centre_coefficients'] for r in receipts] == [2,8,9,2,8,9,8,9,8,8,2,8,9,2],
         'original completion correction counts')
    need(mm(tr(s),subtract(mixed,original)) == jglobal, 'mixed overlapping centre outputs add exactly')
    need(any(x for row in jglobal for x in row), 'omitting centre correction fails a source column')
    # Distinct blocks have disjoint source and port supports, but centre outputs overlap.
    need(len({p for b in blocks for p in b['ports']}) == 112, 'port partition')
    defect = subtract(mixed,original)
    defect_rank = sum(receipts[i]['port_defect_rank_Q'] for i in CHEAP)
    witnesses = [(i,j,str(x)) for i,row in enumerate(defect) for j,x in enumerate(row) if x]
    need(witnesses and defect_rank > 0, 'full port endpoint differs despite exact centre readout')
    # For an abstract reader followed by port repair, centre output is already
    # correct. Repairing ports AFTER this read adds (I-U)Kx without changing it.
    # This is an algebraic cost screen, not the physical selected forward cut.
    need(repair_profile == Counter({1:12,2:4}), 'four-block natural repair profile')
    natural_repaired = [[mixed[i][j]-defect[i][j] for j in range(112)] for i in range(112)]
    need(natural_repaired == original, 'post-readout natural port repair')
    budgets = {}
    for name,local in [('baseline',{1:192,2:56,32:166}),
                       ('selective',{1:216,2:40,32:166}),
                       ('selective_post_reader_port_repair',{1:228,2:44,32:166})]:
        md = ceiling.model(local,73,896,9,112,R=51,unpaid=2)
        bracket = ceiling.ceiling(local,73,896,9,112,grid=Q(1,10**12),R=51,unpaid=2)
        one_zero = ceiling.relax(local,73,896,9,112,Q(0),R=51,unpaid=1)
        need(one_zero[0] > 1, 'fixed-law one-unpaid model has no positive saving')
        budgets[name] = {'profile':local,'local_mass':str(md['local_mass']),
            'a_ceiling_bracket':[str(x) for x in bracket],
            'optimistic_kappa_ceiling_hi':str(bracket[1]/(1+bracket[1])),
            'optimistic_kappa_ceiling_hi_decimal':format(float(bracket[1]/(1+bracket[1])),'.17g'),
            'one_unpaid_zero_saving_moment':[str(x) for x in one_zero]}
    # A post U^-1 alone fixes UKx but corrupts the independent dirty baseline.
    need(all(mm(inv(blocks[i]['u']),mm(blocks[i]['u'],eye(8))) == eye(8) for i in CHEAP), 'basis inverse')
    need(all(inv(blocks[i]['u']) != eye(8) for i in CHEAP), 'dirty entrance correction required')
    # Cheap literal forward repair. All native children/adapters stay byte-for-byte.
    original_rows,original_labels,original_profile = scatter.replay(word,events)
    changed = [row[:] for row in s]
    chosen_blocks = [blocks[i] for i in CHEAP]
    for b in chosen_blocks:
        for z,p in enumerate(b['ports']):
            changed[p] = b['us'][z]
    repaired = scatter.install(word,events,changed,chosen_blocks)
    need(scatter.replay(word,repaired) == (original_rows,original_labels,original_profile),
         '704 ordinary columns, common frames, private restoration and unchanged child histogram')
    scalars = lambda ev: Counter(z[1][0] for z in ev if z[0]=='scalar')
    delta = scalars(repaired)-scalars(events)
    need(delta == Counter(add=54*4+support(changed)-176,scale=6*4), 'all literal repair costs')
    # Reject installing the abstract hybrid as a forward scatter on the chosen four.
    wrong = [row[:] for row in s]
    for b in chosen_blocks:
        for z,p in enumerate(b['ports']):
            wrong[p] = b['hybrid'][z]
    wrong_rows,wrong_labels,wrong_profile = scatter.replay(word,scatter.install(word,events,wrong,chosen_blocks),False)
    need((wrong_labels,wrong_profile) == (original_labels,original_profile)
         and wrong_rows != original_rows, 'wrong-scatter full endpoint control')
    bad = [z for z in repaired]
    pos = bad.index(['phase','centers'])+1
    entrance_len = sum(len(scatter.basis_events(b['ports'],b['reduce_ops'])) for b in chosen_blocks)
    del bad[pos:pos+entrance_len]
    bad_rows,bad_labels,bad_profile = scatter.replay(word,bad,False)
    need((bad_labels,bad_profile) == (original_labels,original_profile),
         'missing entrance retains valid labels and recursive bill')
    need(any(bad_rows['L',i].get(j,0) != original_rows['L',i].get(j,0)
             for i in range(704) for j in range(112,224)), 'missing entrance fails dirty columns')
    return {'status':'LOCAL_PROGRESS_NO_NATIVE_SUPPLIER_NO_NEW_KAPPA',
        'selected_blocks':list(CHEAP),'block_receipts':receipts,'slot_to_root':slots,
        'mixed_coefficient_identity':{'all_112_source_columns_checked':True,
            'shared_centre_outputs':'summed, never overwritten',
            'abstract_profile':{str(k):v for k,v in sorted(profile.items())},
            'correction_coefficient_count':8,'one_unit_sensitivity_total':104,
            'baseline_sensitivity_total':112,'net_sensitivity_units_saved':8,
            'full_port_endpoint_defect_rank_Q':defect_rank,'first_port_defect':witnesses[0],
            'independent_dirty_baseline':'post U^-1 alone leaves (U^-1-I)d'},
        'dirty_scratch_scalar_control':scratch_receipt,
        'natural_post_readout_repair_screen':{'rank_profile':dict(repair_profile),
            'additional_rank_mass':20,'total_one_unit_sensitivity':124,
            'baseline_one_unit_sensitivity':112,
            'scope':'One fixed residual factorization after an abstract reader; not a minimum or native program.'},
        'hypothetical_rank32_coverage_model':{'m':73,'families':896,'stages':9,'centre':112,
            'idle_rank_cap':51,'unpaid':2,'unproved_coverage_law':True,'screens':budgets,
            'one_unpaid_failure_reason':'At a=0 the moment is 1+(112-896/9)/(73*896/9)>1 independent of local profile.',
            'not_comparable_to_T360_word':True},
        'four_block_literal_forward_sandwich':{'ordinary_columns_checked':704,
            'cut_adds':support(changed),'extra_ADDs':delta['add'],'extra_sign_scales':delta['scale'],
            'extra_scalar_operations':sum(delta.values()),'recursive_histogram_delta':{},
            'private_restoration':True,'wrong_scatter_rejected':True,'missing_entrance_rejected':True},
        'existing_recursive_profile':{str(k):v for k,v in sorted(original_profile.items())},
        'new_unpaid_coordinate_exhibited':False,'complete_supplier_cost':'UNKNOWN',
        'first_unresolved_obligation':'A source-bound chronological augmented COPY/consumer with correct full live-port endpoint, source acquisition, frames, dirty state and restoration.',
        'unrun':['Changed native kernels and recursive source acquisition','Rounded precision/magnitude and storage',
            'Whole-call hosting and both supplier coverage laws','Two-unpaid proof','Global/outer admission and selected cold replay'],
        'scope':'Exact rational local algebra and selected normalized scalar/frame replay; unchanged native recipes inherited, no fresh native kernel certification.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    result = run()
    # Fraction values in coefficient artifacts are exact strings.
    encoded = json.dumps(result,indent=2,sort_keys=True,default=str)+'\n'
    if args.write:
        (HERE/'RESULT.json').write_text(encoded)
    else:
        need(json.loads((HERE/'RESULT.json').read_text()) == json.loads(encoded), 'result drift')
    print(result['status'])
    print(json.dumps(result['mixed_coefficient_identity'],sort_keys=True))
    print(json.dumps(result['four_block_literal_forward_sandwich'],sort_keys=True))
