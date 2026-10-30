#!/usr/bin/env python3
"""ROOT ONLY: one exact pre13 stage and restricted dyadic capacity certificate.

Static preparation is not a run. No native, pricing, census, alternate cut, or
physical split realization is performed by this checker.
"""
import ast
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E = [57, 81, 92, 224, 225, 234]
RESULT = {'schema': 'one-pre13-cut-capacity-result/v1', 'new_kappa': None,
          'physical_witness': False, 'execution_scope': 'one exact cut; restricted E6'}


class PremiseFailure(ValueError):
    pass


def need(ok, why):
    if not ok:
        raise ValueError(why)


def premise(ok, why):
    if not ok:
        raise PremiseFailure(why)


def pairs_unique(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, 'duplicate JSON key')
        out[key] = value
    return out


def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=pairs_unique)


def encoded(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {str(k): encoded(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [encoded(v) for v in x]
    return x


def canonical(x):
    return json.dumps(encoded(x), sort_keys=True, separators=(',', ':')).encode()


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def shape(a, m, n, name):
    need(len(a) == m and all(len(row) == n for row in a), name+' exact widths')


def transpose(a, m, n):
    shape(a, m, n, 'transpose')
    return [[a[i][j] for i in range(m)] for j in range(n)]


def product(a, b, m, k, n):
    shape(a, m, k, 'left product'); shape(b, k, n, 'right product')
    return [[sum((a[i][t]*b[t][j] for t in range(k)), Q(0))
             for j in range(n)] for i in range(m)]


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def dyadic(x):
    d = Q(x).denominator
    return d & (d-1) == 0


def determinant(a):
    n = len(a); shape(a, n, n, 'determinant')
    a = [[Q(x) for x in row] for row in a]; out = Q(1)
    for j in range(n):
        p = next((i for i in range(j, n) if a[i][j]), None)
        if p is None:
            return Q(0)
        if p != j:
            a[p], a[j] = a[j], a[p]; out = -out
        pivot = a[j][j]; out *= pivot
        for i in range(j+1, n):
            q = a[i][j]/pivot
            for k in range(j+1, n):
                a[i][k] -= q*a[j][k]
            a[i][j] = Q(0)
    return out


def smith_checked(C, a, m, n):
    shape(a, m, n, 'integer constraint')
    need(all(type(x) is int for row in a for x in row), 'integer entries')
    if m == 0:
        return [], [], eye(n), 0
    u, s, v = C.smith(a)
    shape(u, m, m, 'Smith U'); shape(s, m, n, 'Smith S'); shape(v, n, n, 'Smith V')
    need(all(type(x) is int for z in (u, s, v) for row in z for x in row), 'integer Smith transforms')
    need(abs(determinant(u)) == abs(determinant(v)) == 1, 'unimodular Smith transforms')
    need(product(product(u, a, m, m, n), v, m, n, n) == s, 'U A V = S')
    factors = [s[i][i] for i in range(min(m, n))]
    rank = sum(x != 0 for x in factors)
    need(all(s[i][j] == 0 for i in range(m) for j in range(n) if i != j), 'Smith diagonal')
    need(all(x > 0 for x in factors[:rank]) and all(x == 0 for x in factors[rank:]), 'Smith positive ordered rank')
    need(all(factors[i+1] % factors[i] == 0 for i in range(rank-1)), 'Smith divisibility')
    return u, s, v, rank


def kernel(C, rows, n, name):
    # Keep a Q-independent subset of at most six ORIGINAL constraints. Later
    # verify ALL original constraints annihilate the free columns of V. With
    # selected rank r and unimodular V this certifies the full D kernel, while
    # avoiding a large left-Smith transform/determinant.
    shape(rows, len(rows), n, name)
    need(all(dyadic(x) for row in rows for x in row), 'dyadic constraints')
    rows = sorted(set(tuple(Q(x) for x in row) for row in rows if any(row)))
    echelon = []; selected = []
    for original in rows:
        row = list(original)
        for pivot, known in echelon:
            q = row[pivot]
            row = [x-q*y for x,y in zip(row,known)]
        pivot = next((i for i,x in enumerate(row) if x), None)
        if pivot is not None:
            q = row[pivot]
            normalized = [x/q for x in row]
            echelon = sorted([(p,[x-known[pivot]*y for x,y in zip(known,normalized)])
                              for p,known in echelon]+[(pivot,normalized)])
            selected.append(original)
    need(len(selected) <= n, 'independent constraint bound')
    d = max((x.denominator for row in selected for x in row), default=1)
    a = [[int(d*x) for x in row] for row in selected]
    u, s, v, rank = smith_checked(C, a, len(a), n)
    basis = [row[rank:] for row in v]
    shape(basis, n, n-rank, name+' full kernel basis')
    need(product(a, basis, len(a), n, n-rank) == [[0]*(n-rank) for _ in a], 'kernel equation')
    need(rank == len(selected), 'selected constraints independent')
    need(product(rows, basis, len(rows), n, n-rank) == [[0]*(n-rank) for _ in rows], 'ALL original constraints annihilate full kernel')
    return basis, {'constraint_rows': len(rows), 'independent_rows':len(a),
                   'all_constraints_sha256':digest(rows),'variables': n, 'denominator': d,
                   'integer_constraints': a, 'U': u, 'S': s, 'V': v,
                   'rank': rank, 'basis_columns': basis,
                   'completeness': 'Unimodular V; diagonal nonzero coordinates forced zero over D.'}


def capacity(C, k, m, n):
    shape(k, m, n, 'pairing')
    if m == 0 or n == 0:
        return {'capacity': 0, 'rational_rank': 0, 'denominator': 1,
                'factors': [], 'U': eye(m), 'S': [[0]*n for _ in range(m)],
                'V': eye(n), 'left': [], 'right': [[] for _ in range(n)]}
    out = C.capacity(k)
    d = out['denominator']; need(type(d) is int and d > 0 and d & (d-1) == 0, 'dyadic denominator')
    a = [[int(d*x) for x in row] for row in k]
    need(all(Q(a[i][j], d) == k[i][j] for i in range(m) for j in range(n)), 'exact denominator clearing')
    # Verify the returned certificate independently, without silently truncating.
    u, s, v = out['U'], out['S'], out['V']
    shape(u, m, m, 'capacity U'); shape(s, m, n, 'capacity S'); shape(v, n, n, 'capacity V')
    need(all(type(x) is int for z in (u, s, v) for row in z for x in row), 'integer capacity transforms')
    need(abs(determinant(u)) == abs(determinant(v)) == 1, 'capacity unimodular')
    need(product(product(u, a, m, m, n), v, m, n, n) == s, 'capacity Smith identity')
    need(all(s[i][j] == 0 for i in range(m) for j in range(n) if i != j), 'capacity diagonal')
    f = [s[i][i] for i in range(min(m, n)) if s[i][i]]
    need(all(x > 0 for x in f) and all(f[i+1] % f[i] == 0 for i in range(len(f)-1)), 'capacity factor order')
    need([s[i][i] for i in range(min(m,n))] == f+[0]*(min(m,n)-len(f)), 'capacity trailing zeros')
    count = sum(x & (x-1) == 0 for x in f)
    need(out['factors'] == f and out['rational_rank'] == len(f) and out['capacity'] == count, 'unit factor count')
    shape(out['left'], count, m, 'capacity X'); shape(out['right'], n, count, 'capacity Y')
    need(all(dyadic(x) for z in (out['left'], out['right']) for row in z for x in row), 'dyadic unit witnesses')
    need(product(product(out['left'], k, count, m, n), out['right'], count, n, count) == eye(count), 'X K Y = I')
    return out


def import_source(path, name, allowed):
    tree = ast.parse(path.read_bytes(), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            need(all(x.name.split('.')[0] in allowed for x in node.names), 'unexpected source import')
        if isinstance(node, ast.ImportFrom):
            need(node.level == 0 and node.module.split('.')[0] in allowed, 'unexpected source from-import')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def propagate(w, events, initial_rows):
    rows = [{k:Q(v) for k,v in row.items()} for row in initial_rows]
    for e in events:
        op, r = e[:2]
        if op == 'MOVE':
            continue
        if op in ('INIT', 'CLEAR'):
            rows[r] = {}
        elif op == 'SCALE':
            rows[r] = {k:Q(e[-2])*v for k,v in rows[r].items()}
        elif op == 'COPY':
            rows[r] = {k:Q(e[-2])*v for k,v in rows[e[2]].items()}
        else:
            need(op == 'ADD', 'propagation opcode')
            for k,v in tuple(rows[e[2]].items()):
                z = rows[r].get(k, Q(0))+Q(e[-2])*v
                if z: rows[r][k] = z
                else: rows[r].pop(k, None)
    return rows


def bilinear(a, b):
    need(len(a) == len(b), 'pair widths')
    return sum((x*y for x,y in zip(a,b)), Q(0))


def whole_invoice(paid, helpers):
    paid = Counter({int(k):18*v for k,v in paid.items()})
    targets = Counter({int(k):18*v for k,v in helpers.items()})
    paid[1] += 1560; targets[145] += 208
    for length in (7,8):
        for k in range(2,length+2):
            paid[8*k] += 208; targets[8*k+1] += 208
    return {'paid':dict(paid),'targets':dict(targets),'paid_count':sum(paid.values()),
            'target_count':sum(targets.values()),'paid_rank_mass':sum(k*v for k,v in paid.items()),
            'target_rank_mass':sum(k*v for k,v in targets.items())}


def controls(C):
    out = {}
    def rejected(name, action):
        try:
            action()
        except ValueError:
            out[name] = 'rejected'
        else:
            raise ValueError('mutation accepted: '+name)
    rejected('truncated_product_width',lambda:product([[1,0]],[[1]],1,2,1))
    rejected('odd_denominator_constraint',lambda:kernel(C,[[Q(1,3)]],1,'control'))
    rejected('nonunit_transform',lambda:need(abs(determinant([[2]]))==1,'nonunit transform'))
    rejected('rank_not_dyadic_capacity',lambda:need(capacity(C,[[Q(3)]],1,1)['capacity']==1,'odd Smith factor'))
    rejected('double_credit_same_channel',lambda:need([[bilinear(x,y) for y in ([Q(1)],[Q(1)])]
        for x in ([Q(1)],[Q(1)])] == eye(2),'nonorthogonal reused pair'))
    basis,cert = kernel(C,[[Q(3),Q(0)]],2,'saturation control')
    need(cert['rank']==1 and basis == [[0],[1]], 'full D kernel, no arbitrary odd rescaling')
    out['saturated_odd_constraint_kernel'] = 'verified_full_basis'
    return out


def main():
    inputs = read(HERE/'INPUTS.json')
    # All closure/source/import pins are authenticated BEFORE imports or gzip.
    for path, expected in inputs['files'].items():
        need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected, 'input SHA '+path)
    hand = ROOT/inputs['stage_handoff']; exp = hand/'pr5608-export'
    manifest = read(exp/'.research-export.json')
    need(len(manifest['files']) == 24, 'complete export24')
    for item in manifest['files']:
        path = exp/item['path']; raw = path.read_bytes()
        need(len(raw) == item['size'] and hashlib.sha256(raw).hexdigest() == item['sha256'], 'export byte '+item['path'])
    nomination = read(ROOT/inputs['nomination'])
    h = read(hand/'pr5612-package/SPLITS.json')
    need(len(h) == 13 and h[12] == nomination['object']['record'], 'literal published record13')
    RESULT['inputs_authenticated'] = True
    L = import_source(exp/'research/p104-relay-split-composition/inputs/pr5599-local.py', 'local',
                      {'collections','fractions','functools','hashlib','pathlib','gzip','importlib','json','sys'})
    S = import_source(exp/'research/p104-relay-split-composition/inputs/pr5599-construct.py', 'onecut_split', {'copy','fractions','local'})
    C0 = import_source(exp/'research/p104-relay-split-composition/construct.py', 'onecut_parent', {'copy','fractions'})
    D = import_source(hand/'pr5612-package/delayed.py', 'onecut_delayed', {'copy','hashlib','json'})
    base = json.loads(gzip.decompress((exp/'research/p104-relay-split-composition/inputs/pr5580-WORD.json.gz').read_bytes()), object_pairs_hook=pairs_unique)
    try:
        stage = C0.construct_parent(base)
    except ValueError as error:
        raise PremiseFailure('source parent premise: '+str(error)) from error
    premise(digest(stage) == nomination['reconstruction']['known_parent_canonical_hash'], 'parent hash')
    try:
        stage = D.construct(stage)
    except ValueError as error:
        raise PremiseFailure('source delayed premise: '+str(error)) from error
    premise(digest(stage) == nomination['reconstruction']['known_delayed_canonical_hash'], 'delayed hash')
    for number,record in enumerate(h[:12],1):
        try:
            stage = S.split(stage, record)
        except ValueError as error:
            raise PremiseFailure('published predecessor split '+str(number)+': '+str(error)) from error
    RESULT['stage_canonical_sha256'] = digest(stage)
    RESULT['public'] = stage['public']; RESULT['events'] = len(stage['program'])
    RESULT['reconstruction'] = 'authenticated base -> construct_parent -> delayed -> exactly first12 split'
    premise(stage['public'] == 747, 'pre13 public count')
    try:
        census = L.replay(stage)  # The sole full endpoint replay.
    except ValueError as error:
        raise PremiseFailure('source endpoint replay: '+str(error)) from error
    RESULT['local_census'] = census
    eco = nomination['economics']
    premise(encoded(census['paid']) == eco['pre13_local_paid'], 'pre13 paid invoice')
    premise(encoded(census['helpers']) == eco['pre13_local_targets'], 'pre13 helper invoice')
    actual_whole = whole_invoice(census['paid'],census['helpers'])
    premise(encoded(actual_whole) == eco['pre13'], 'all-charged fixed caller invoice')
    RESULT['actual_derived_complete_pre13_invoice'] = actual_whole
    n = stage['public']; cut = h[12]['cut_after']; frame = h[12]['frame']
    premise((cut, frame, h[12]['pivot']) == (12626, 267, 225), 'fixed exact cut')
    current = list(stage['initial'])+[None]*8; owned = set()
    for e in stage['program'][:cut+1]:
        op,r = e[:2]
        if op == 'MOVE': current[r] = e[3]
        elif op == 'INIT': owned.add(r); current[r] = e[2]
        elif op == 'CLEAR': owned.remove(r); current[r] = None
    main_roles = set(stage['live']) | {r+112 for r in stage['live']}
    u,v = stage['initial'][225],stage['final'][225]
    H = [r for r in range(n) if r not in main_roles and (stage['initial'][r],stage['final'][r]) == (u,v)]
    RESULT['cut'] = {'after_zero_based_event':cut,'frame':frame,'E':E,'current_E':{r:current[r] for r in E},
                     'live_owned':sorted(owned),'H':H,'boundary_frames':[u,v],
                     'boundary_bases':[stage['frames'][u],stage['frames'][v]],
                     'middle_basis':stage['frames'][frame],'carriers':[225,224],
                     'all_public_cut_frames':current[:n],'owned_cut_frames':current[n:],
                     'main_roles':sorted(main_roles),'initial_public_frames':stage['initial'],
                     'final_public_frames':stage['final']}
    premise(not owned and all(current[r] is None for r in range(n,n+8)), 'live owned at cut: public-square theorem inapplicable')
    premise(all(current[r] == frame for r in E), 'literal E not coframed')
    premise(224 in H and 225 in H and 224 != 225, 'unchanged original helper carrier boundary')
    premise(L.span(stage['frames'][u]) < L.span(stage['frames'][frame]) < L.span(stage['frames'][v]), 'strict actual frame inclusions')
    premise([len(stage['frames'][frame])-len(stage['frames'][u]),len(stage['frames'][v])-len(stage['frames'][frame])] == [8,1], 'split ranks')
    try:
        a0,b0,c0,d0 = S.check_cut(stage,h[12])
    except ValueError as error:
        raise PremiseFailure('known published record13: '+str(error)) from error
    RESULT['known_published_channel'] = {'check_cut':True,'a':a0,'b':b0,'c':c0,'d':d0,'credited_once':True}
    # Native geometry is inherited, not replayed. Public arbitrary-input
    # endpoint replay and empty owned cut give BA=M with M invertible over D;
    # hence square A,B are invertible over D. H is an identity direct summand.
    prefix = propagate(stage, stage['program'][:cut+1], [{r:Q(1)} for r in range(n)]+[{} for _ in range(8)])
    suffix = propagate(stage, stage['program'][cut+1:], [{E.index(r):Q(1)} if r in E else {} for r in range(n+8)])
    premise(all(not prefix[r] for r in range(n,n+8)), 'owned prefix rows not zero')
    premise(all(not suffix[r] for r in range(n,n+8)), 'owned suffix response not zero')
    A = [[prefix[r].get(j,Q(0)) for j in range(n)] for r in E]
    B = [[suffix[r].get(i,Q(0)) for i in range(6)] for r in range(n)]
    outside = [r for r in range(n) if r not in H]
    left_constraints = [[A[i][r] for i in range(6)] for r in outside]
    right_constraints = [B[r] for r in outside]
    av = [a0.get(r,Q(0)) for r in E]; bv = [b0.get(r,Q(0)) for r in E]
    premise(set(a0)|set(b0) <= set(E), 'known pair uses outside E')
    need([sum((av[i]*A[i][j] for i in range(6)),Q(0)) for j in range(n)] ==
         [c0.get(j,Q(0)) for j in range(n)], 'independent known prefix equation')
    need([bilinear(row,bv) for row in B] == [d0.get(j,Q(0)) for j in range(n)], 'independent known suffix equation')
    premise(all(bilinear(row,av) == 0 for row in left_constraints) and all(bilinear(row,bv) == 0 for row in right_constraints), 'known pair module membership')
    premise(bilinear(av,bv) == 1, 'known pair unit')
    C = import_source(ROOT/inputs['capacity_module'], 'onecut_released_capacity', {'fractions'})
    RESULT['controls'] = controls(C)
    kl,cl = kernel(C,left_constraints,6,'L'); kr,cr = kernel(C,right_constraints,6,'R')
    l = transpose(kl,6,len(kl[0])); r = kr
    k = product(l,r,len(l),6,len(r[0])); full = capacity(C,k,len(l),len(r[0]))
    premise(full['capacity'] >= 1, 'known positive channel contradicts capacity')
    ql,cql = kernel(C,left_constraints+[bv],6,'L orthogonal to known b')
    qr,cqr = kernel(C,right_constraints+[av],6,'R orthogonal to known a')
    ll = transpose(ql,6,len(ql[0])); rr = qr
    kk = product(ll,rr,len(ll),6,len(rr[0])); residual = capacity(C,kk,len(ll),len(rr[0]))
    premise(full['capacity'] == 1+residual['capacity'], 'unit direct-summand residual identity')
    RESULT['modules'] = {'L':cl,'R':cr,'L_residual':cql,'R_residual':cqr,
                         'prefix_selected_rows_sha256':digest(A),'suffix_selected_columns_sha256':digest(B)}
    RESULT['capacity'] = {'pairing':k,'certificate':full,'residual_pairing':kk,'residual_certificate':residual,
                          'incremental_extra':max(full['capacity']-1,0),'support_scope':'literal E6 only'}
    if residual['capacity']:
        ln = product([residual['left'][0]],ll,1,len(ll),6)[0]
        rn = [row[0] for row in product(rr,residual['right'],6,len(rr[0]),residual['capacity'])]
        cutblock = [[bilinear(x,y) for y in (bv,rn)] for x in (av,ln)]
        cn = [sum((ln[i]*A[i][j] for i in range(6)),Q(0)) for j in range(n)]
        dn = [bilinear(row,rn) for row in B]
        need(all(cn[j] == dn[j] == 0 for j in outside), 'new boundary support')
        oldc = [c0.get(j,Q(0)) for j in range(n)]; oldd = [d0.get(j,Q(0)) for j in range(n)]
        boundaryblock = [[bilinear(x,y) for y in (oldd,dn)] for x in (oldc,cn)]
        need(cutblock == boundaryblock == eye(2), 'preserved joint old/new identity and zero cross pairings')
        RESULT['joint_block'] = {'new_a_E':ln,'new_b_E':rn,'new_c':{j:x for j,x in enumerate(cn) if x},
                                 'new_d':{j:x for j,x in enumerate(dn) if x},'cut_pairing':cutblock,'boundary_pairing':boundaryblock,
                                 'old_carrier':225,'only_new_carrier':224,'physical_basis_program_constructed':False}
        RESULT['status'] = 'CONDITIONAL_ALGEBRAIC_EXTRA_CHANNEL_ONLY'
    else:
        RESULT['status'] = 'NO_ADDITIONAL_RESTRICTED_CHANNEL_STOP_THIS_OBJECT'
    RESULT['endpoint_argument'] = 'One all-input replay; empty owned cut; square dyadic A/B with invertible BA=M; H identity direct summand.'
    targets = Counter({int(k):v for k,v in census['helpers'].items()})
    derived = {}
    for key in ('after_published13','after_one_extra_optimistic'):
        targets[9] -= 1; targets[8] += 1; targets[1] += 1
        need(min(targets.values()) >= 0, 'target parents charged once')
        invoice = whole_invoice(census['paid'],targets)
        need(encoded(invoice) == eco[key], 'derived signed target invoice '+key)
        need(invoice['paid_rank_mass']==actual_whole['paid_rank_mass'] and invoice['target_rank_mass']==actual_whole['target_rank_mass'], 'rank mass conservation')
        derived[key] = invoice
    RESULT['derived_optimistic_comparison_invoices'] = derived
    RESULT['unfulfilled'] = ['dyadic basis scalar programs and physical carrier realization','native all-width phase replay',
                            'complete ordinary costs and pricing','any later5613-stage transfer']


if __name__ == '__main__':
    try:
        main()
    except PremiseFailure as error:
        RESULT['status'] = 'PREMISE_FAILURE_STOP_THIS_EXACT_OBJECT'
        RESULT['failure'] = str(error)
    except Exception as error:
        RESULT['status'] = 'INPUT_PARSER_OR_CERTIFICATE_FAILURE_STOP'
        RESULT['failure'] = type(error).__name__+': '+str(error)
    print(canonical(RESULT).decode())
    if RESULT['status'] == 'INPUT_PARSER_OR_CERTIFICATE_FAILURE_STOP':
        sys.exit(2)
