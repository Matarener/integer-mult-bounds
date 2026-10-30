#!/usr/bin/env python3
"""Native selected-data alias exchanges around the frozen H112 kernel.

Forward adds eight arbitrary productive-cache candidates with paid I->F9
paths, then exchanges source function and cache at the completed X frame.
Backward moves each original selected X field to the Y entrance frame and
back, paying two rank-one children. No borrowed state is cleared.
Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
COMPLEX = HERE.parent/'complex'
sys.path.insert(0, str(COMPLEX))
import affine_core as A
import port_state_lift as PS
import involution112 as HN
P = A.P
HROOT = COMPLEX/'involution112-native'
H_RECEIPT_SHA = 'd14edeacd37e526f8723ebdfb22f6b8d470ebf1daa7ef7c87aacfe7bae00484c'


def add(target, source, q, frame):
    q = Q(q)
    return ['scalar', ['add', list(target), list(source), q.numerator, q.denominator], frame]


def forward_suffix(selected, L):
    out = [['phase', 'alias_forward_H_complete']]
    out += [['cache_child', j, 0, 1, 9] for j in range(8)]
    out.append(['phase', 'alias_forward_cache_full'])
    # Form v in the old A fields before changing U.
    for a, row in zip(selected, L):
        out += [add(('L', a), ('L', p), q, 1) for p, q in sorted(row.items())]
    for j, (a, row) in enumerate(zip(selected, L)):
        for p, q in sorted(row.items()):
            out += [add(('L', p), ('P', j), q, 1),
                    add(('L', p), ('L', a), -q, 1)]
    # Ordinary swap (v,d)->(d,v), using three shears and a sign.
    for j, a in enumerate(selected):
        out += [add(('L', a), ('P', j), 1, 1),
                add(('P', j), ('L', a), -1, 1),
                add(('L', a), ('P', j), 1, 1),
                ['scalar', ['scale', ['P', j], -1, 1], 1]]
    return out+[['phase', 'alias_forward_final']]


def backward_prefix(c, selected, L):
    out = [['phase', 'alias_backward_entry']]
    for j, (a, row) in enumerate(zip(selected, L)):
        line = c['start'][a]
        out.append(['state_child', a, line, 0, 1, f'{a}:down'])
        # Current Y remains untouched in U while its selected function is used.
        out += [add(('L', 112+a), ('L', 112+p), q, 0) for p, q in sorted(row.items())]
        out += [add(('L', a), ('L', 112+a), 1, 0),
                add(('L', 112+a), ('L', a), -1, 0),
                add(('L', a), ('L', 112+a), 1, 0)]
        out += [add(('L', 112+a), ('L', 112+p), -q, 0) for p, q in sorted(row.items())]
        out.append(['state_child', a, 0, line, 1, f'{a}:up'])
    return out+[['phase', 'alias_backward_prefix_complete']]


def paid(word):
    out = Counter()
    for e in word:
        if e[0] == 'climb': out[e[5]] += 1
        elif e[0] in ('center', 'cache_child', 'state_child'): out[e[4]] += 1
    return out


def initial(v, forward):
    rows = {('L', i): v.identity(('L', i)) for i in range(632)}
    if forward: rows.update({('P', j): v.identity(('P', j)) for j in range(8)})
    rows['C', 0] = {}
    return rows


def expected(v, selected, ordinary, L, H, direction, cut='final'):
    forward = direction == 'forward'
    rows = initial(v, forward)
    ident = v.identity
    if forward:
        for p in range(112):
            for q, c in H[p].items(): v.add(rows['L', 112+p], ident(('L', q)), c)
        if cut in ('alias_forward_H_complete', 'alias_forward_cache_full'): return rows
        for j, a in enumerate(selected):
            rows['P', j] = ident(('L', a))
            for p, q in L[j].items(): v.add(rows['P', j], ident(('L', p)), q)
        for p in ordinary:
            for j, a in enumerate(selected):
                q = L[j].get(p, Q(0))
                if q:
                    v.add(rows['L', p], ident(('P', j)), q)
                    v.add(rows['L', p], rows['P', j], -q)
        for j, a in enumerate(selected): rows['L', a] = ident(('P', j))
    elif cut == 'alias_backward_prefix_complete':
        # The prefix does not use owned C0. The inherited H body clears it
        # later, so its arbitrary starting symbol still exists at this cut.
        rows['C', 0] = ident(('C', 0))
        for j, a in enumerate(selected):
            rows['L', a] = ident(('L', 112+a))
            rows['L', 112+a] = {}
            v.add(rows['L', 112+a], ident(('L', a)), Q(-1))
            for p, q in L[j].items():
                v.add(rows['L', a], ident(('L', 112+p)), q)
                v.add(rows['L', 112+a], ident(('L', 112+p)), -q)
    else:
        # Direct closed formula, independent of applying H to a simulated prefix.
        for p in ordinary:
            v.add(rows['L', p], ident(('L', 112+p)), Q(-1))
            for j, a in enumerate(selected):
                if p in L[j]: v.add(rows['L', p], ident(('L', a)), -L[j][p])
        for j, a in enumerate(selected):
            rows['L', a] = ident(('L', 112+a))
            v.add(rows['L', a], ident(('L', a)), Q(12))
            rows['L', 112+a] = {}
            v.add(rows['L', 112+a], ident(('L', a)), Q(-1))
            for p, q in L[j].items():
                v.add(rows['L', a], ident(('L', 112+p)), 2*q)
                v.add(rows['L', 112+a], ident(('L', 112+p)), -q)
    return rows


def phase_receipt(c, selected):
    ce = P.load(P.CLIFFORD, 'accounted_alias_clifford')
    identity = ce.Op.identity(9)
    def lower(op, rank):
        child, _ = ce.lower_child(op)
        P.need(child['rank'] == rank, 'Exact physical recursive rank')
        result = P.monomial(ce, child['right'], 9).then(ce.fourier(9, range(rank))).then(P.monomial(ce, child['left'], 9))
        P.need(result.tab == op.tab and result.zero_state() == op.zero_state(),
               'Child and both monomial wrappers match the complete absolute phase')
        return child
    routes = {}
    for a in selected:
        P.need(c['frames'][c['start'][a]] == [c['ports'][a]], 'Selected physical entrance is its actual normal line')
        actual = P.conjugate(ce, ce.cgate(9, c['ports'][a]))
        down, up = actual.adjoint(), actual
        for name, op, old, new in [('down', down, c['start'][a], 0), ('up', up, 0, c['start'][a])]:
            routes[f'{a}:{name}'] = {'port': a, 'old_frame': old, 'new_frame': new,
                                   'child': lower(op, 1), 'actual_operator': 'conj(Cq)^-1' if name == 'down' else 'conj(Cq)'}
        for product in (actual.then(down), down.then(up), up.then(down)):
            P.need(product.tab == identity.tab and product.zero_state() == identity.zero_state(),
                   'Selected state normalization and return are exact inverse physical operators')
        wrong = actual.then(up)
        P.need(wrong.tab != identity.tab or wrong.zero_state() != identity.zero_state(),
               'Wrong normalization orientation is rejected')
    return {'backward_selected_routes': routes, 'forward_cache_I_to_F9': lower(ce.fourier(9), 9),
            'all_absolute_phases_checked': True, 'wrong_normalization_orientation_rejected': True,
            'backward_convention': 'The selected X entrance is the complex conjugate of actual C_q; the down child is its adjoint, and the return child is the original operator.'}


def replay(v, c, word, selected, ordinary, L, H, direction, phase):
    forward = direction == 'forward'
    rows = initial(v, forward)
    # The owned input may initially contain arbitrary data, and must be cleared.
    rows['C', 0] = v.identity(('C', 0))
    current = {('L', i): f for i, f in enumerate(c['start'])}
    if forward: current.update({('P', j): 0 for j in range(8)})
    current['C', 0] = None
    spaces = [v.span(f) for f in c['frames']]
    dims = [len(s).bit_length()-1 for s in spaces]
    scalar, profile, counts, cuts = 0, Counter(), Counter(), []
    max_l1, max_abs, max_den = Q(1), Q(1), 1
    witness = None
    for position, e in enumerate(word):
        kind = e[0]; counts[kind] += 1
        changed = None
        if kind in ('climb', 'center', 'cache_child', 'state_child'):
            if kind == 'climb':
                _, _, index, old, new, rank = e; role = 'L', index
                P.need(spaces[old] < spaces[new], 'Unchanged native climb remains nested')
            else:
                _, index, old, new, rank, *extra = e
                role = ('C' if kind == 'center' else 'P' if kind == 'cache_child' else 'L'), index
                P.need(spaces[old] < spaces[new] or spaces[new] < spaces[old], 'Paid normalization is a nested move')
                if kind == 'cache_child':
                    P.need(forward and (old, new, rank) == (0, 1, 9), 'Paid arbitrary-cache whole local path')
                if kind == 'state_child':
                    item = phase['backward_selected_routes'][extra[0]]
                    P.need(not forward and item['port'] == index and (old, new) == (item['old_frame'], item['new_frame']),
                           'Exact selected original-state physical route')
            P.need(current[role] == old and rank == abs(dims[new]-dims[old]), 'Paid edge actual source and rank')
            current[role] = new; profile[rank] += 1
        elif kind == 'warp':
            _, role, operator, old, new = e; role = tuple(role)
            P.need(current[role] == old, 'Warp source frame')
            rows[role] = v.warp(rows[role], operator, not forward); current[role] = new
        elif kind == 'scalar':
            g, f = e[1:]; target = tuple(g[1]); changed = target
            if g[0] == 'clear':
                P.need(target == ('C', 0), 'Only owned C0 may be cleared')
                rows[target] = {}; current[target] = f; scalar += 1
            else:
                P.need(current[target] == f, 'Scalar target frame')
                if g[0] in ('add', 'copy'):
                    source = tuple(g[2]); P.need(current[source] == f, 'Scalar source frame')
                    if g[0] == 'copy':
                        P.need(target == ('C', 0) and not rows[target], 'Copy only into cleared owned field')
                        rows[target] = dict(rows[source]); scalar += 1
                    else:
                        q = Q(g[3], g[4]); num, den = abs(q.numerator), q.denominator
                        P.need(target != source and num and not den & (den-1), 'Legal reversible dyadic ADD')
                        v.add(rows[target], rows[source], q)
                        scalar += 3+num.bit_length()-1+num.bit_count()+den.bit_length()-1
                else:
                    P.need(g[0] == 'scale', 'Known scalar operation')
                    q = Q(g[2], g[3]); num, den = abs(q.numerator), q.denominator
                    P.need(num and not num & (num-1) and not den & (den-1), 'Unit dyadic scale')
                    rows[target] = {k: q*x for k, x in rows[target].items()}
                    scalar += abs(num.bit_length()-den.bit_length())+int(q < 0)
        elif kind == 'phase':
            if e[1] in ('alias_forward_H_complete', 'alias_forward_cache_full', 'alias_forward_final',
                        'alias_backward_prefix_complete'):
                P.need(rows == expected(v, selected, ordinary, L, H, direction, e[1]), 'Alias cut operator: '+e[1])
                want_l = c['start'] if e[1] == 'alias_backward_prefix_complete' else c['final']
                P.need([current['L', i] for i in range(632)] == want_l, 'Alias cut L frames')
                if forward:
                    pframe = 0 if e[1] == 'alias_forward_H_complete' else 1
                    P.need(all(current['P', j] == pframe for j in range(8)), 'Alias cut cache frames')
                cuts.append({'name': e[1], 'event': position, 'every_arbitrary_input_checked': True})
        else:
            P.need(kind in ('adapter', 'residual_adapter'), 'Known inherited native phase event')
        if changed is not None and rows[changed]:
            l1 = sum(map(abs, rows[changed].values()), Q(0))
            if l1 > max_l1: max_l1, witness = l1, {'event': position, 'role': list(changed)}
            max_abs = max(max_abs, *(abs(q) for q in rows[changed].values()))
            max_den = max(max_den, *(q.denominator for q in rows[changed].values()))
    P.need(rows == expected(v, selected, ordinary, L, H, direction), 'Complete alias endpoint operator mismatch')
    P.need([current['L', i] for i in range(632)] == c['final'], 'All original endpoint frames retained')
    P.need(not rows['C', 0], 'Owned C0 cleared at return')
    if forward: P.need(all(current['P', j] == 1 for j in range(8)), 'All new cache outputs have full frame')
    P.need(all(rows['L', i] == v.identity(('L', i)) for i in range(224,632)), 'All408 arbitrary original helpers restored')
    P.need(profile == paid(word), 'Literal complete paid profile')
    return {'direction': direction, 'all_original_632_inputs_arbitrary': True,
            'arbitrary_new_cache_inputs': 8 if forward else 0, 'total_arbitrary_persistent_inputs': 640 if forward else 632,
            'restored_original_helpers': 408, 'owned_temporary_peak_inherited_from_H': 1,
            'no_borrowed_clear_or_copy': True, 'all_owned_temporaries_cleared': True,
            'paid_profile': dict(sorted(profile.items())), 'paid_rank_mass': sum(r*n for r,n in profile.items()),
            'conservative_real_scalar_primitive_allowance': 2*scalar,
            'event_counts': dict(counts), 'cuts': cuts,
            'prefix_growth': {'max_exact_formal_row_l1': str(max_l1), 'l1_witness': witness,
                              'max_abs_coefficient': str(max_abs), 'max_denominator': max_den,
                              'scope': 'Exact logical prefix bound; not a rounded precision induction.'}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=HERE/'native')
    args = parser.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    P.need(P.digest(HROOT/'RESULT.json') == H_RECEIPT_SHA, 'Frozen H112 receipt')
    freeze = P.read(COMPLEX/'FREEZE.json')
    for name in ('affine_core.py', 'port_state_lift.py', 'involution112.py'):
        P.need(P.digest(COMPLEX/name) == freeze['files'][name], 'Frozen shared native source '+name)
    P.need(P.digest(P.CHECKER) == P.CHECKER_SHA and P.digest(P.CLIFFORD) == P.CLIFFORD_SHA,
           'Pinned exact native and physical checkers')
    v = P.load(P.CHECKER, 'accounted_alias_arbitrary_checker'); v.authenticate()
    R, selected, ordinary, L = PS.geometry(v.read(v.PACKET)); H = HN.kernel(R, selected, ordinary, L)
    source = P.read(HROOT/'RESULT.json'); providers, artifacts, phases = {}, {}, {}
    for tag in P.TAGS:
        cp, np = (HROOT/(tag+'-'+s+'.json.gz') for s in ('CANONICAL','NATIVE-WORD'))
        for path in (cp,np): P.need(P.digest(path) == source['artifacts'][path.name], 'Frozen H artifact')
        c, base = P.read(cp), P.read(np); phase = phase_receipt(c, selected)
        phases[tag] = phase
        word = {'forward': deepcopy(base['forward'])+forward_suffix(selected,L),
                'backward': backward_prefix(c,selected,L)+deepcopy(base['backward'])}
        checks = {name: replay(v,c,w,selected,ordinary,L,H,name,phase) for name,w in word.items()}
        for name, delta in [('forward',Counter({9:8})),('backward',Counter({1:16}))]:
            P.need(paid(word[name]) == paid(base[name])+delta, 'Complete added recursive profile')
            scalar = checks[name]['conservative_real_scalar_primitive_allowance']-source['providers'][tag]['checks'][name]['conservative_real_scalar_primitive_allowance']
            P.need(scalar == (12688 if name == 'forward' else 8512), 'Complete alias scalar bill')
        for direction in ('forward','backward'):
            bad = deepcopy(word[direction])
            if direction == 'forward':
                index = max(i for i,e in enumerate(bad) if e[0]=='scalar' and e[1][0]=='scale')
            else:
                index = next(i for i,e in enumerate(bad) if e[0]=='state_child' and e[3]!=0)
            del bad[index]
            rejected = False
            try: replay(v,c,bad,selected,ordinary,L,H,direction,phase)
            except (ValueError,KeyError): rejected = True
            P.need(rejected, 'Missing alias sign/selected return child negative control')
        canonical = deepcopy(c)
        canonical['local_profile_is_H_base_only'] = True
        canonical['local_profiles_by_direction'] = {k: checks[k]['paid_profile'] for k in checks}
        canonical['alias_extension'] = {'selected_ports': selected, 'extra_forward_P_fields':8,
            'P_start':0,'P_final':1,'complete_paid_profiles':{k:checks[k]['paid_profile'] for k in checks},
            'state_child_grammar':'state_child,index,old,new,rank,exact_phase_route_id; applies the emitted actual recursive child to original L[index], retaining its logical value between declared frames.'}
        paths=[]
        for suffix,value in [('CANONICAL',canonical),('NATIVE-WORD',word)]:
            path=args.out/(tag+'-'+suffix+'.json.gz');P.save(path,value)
            artifacts[path.name]=P.digest(path);paths.append(path.name)
        providers[tag]={'checks':checks,'baseline_H_checks':source['providers'][tag]['checks'],
            'extra_children_over_H':{'forward':{'9':8},'backward':{'1':16}},
            'extra_scalar_over_H':{'forward':12688,'backward':8512},
            'meaningful_omitted_gate_controls_rejected':True,'artifacts':paths}
        print('PASS native selected alias',tag,'both orientations',flush=True)
    path=args.out/'PHASES.json.gz';P.save(path,phases);artifacts[path.name]=P.digest(path)
    result={'schema':'native-selected-state-alias/1','status':'PASS_LOCAL_F_POST_AND_B_PRE_ALIAS_WITH_COMPLETE_COST',
        'generator_sha256':P.digest(Path(__file__)),'frozen_H_receipt_sha256':H_RECEIPT_SHA,
        'shared_sources_sha256':{n:P.digest(COMPLEX/n) for n in ('affine_core.py','port_state_lift.py','involution112.py')},
        'native_checker_sha256':P.CHECKER_SHA,'clifford_checker_sha256':P.CLIFFORD_SHA,
        'selected_ports':selected,'providers':providers,'artifacts':artifacts,
        'forward_contract':{'X_U':'a+K(d-v), v=b+L a','X_A':'d','P':'v','Y':'y+H x'},
        'backward_prefix_contract':{'X_U':'a','X_A':'Y_A+L Y_U','Y_U':'c','Y_A':'-b-L c'},
        'backward_whole_contract':{'X_U':'a-c-K b','X_A':'Y_A_in+2 L c+12 b','Y_U':'c','Y_A':'-b-L c'},
        'local_same_pair_ordinary_composition':'If a forward source feeds the next backward target without another ordinary mutation, X_U_after_B=-Y_U_before_F+(K_s-K_t)d in the corresponding owner-aware notation. Only a matched scalar chart cancels the difference automatically.',
        'forward_wrapper_inverse':'a=a_prime-K(b_prime-P_prime); b=P_prime-L a; d=b_prime',
        'backward_wrapper_inverse':'c=Y_U_prime; b=-(Y_A_prime+L c); Y_A_in=X_A_prime-L c',
        'width_and_productive_scope':'Forward introduces eight independent arbitrary cache fields, paid I->F9. Their outputs are old source functions, not transforms of their own original data. Original cache inputs move into selected X data. No productive cache credit, global idle/hosting plan or final return is claimed. Backward introduces no persistent field.',
        'physical_scope':'Forward wrapper follows the full H word when X is coframed. Backward wrapper precedes H; every selected X datum makes a paid exact dual-normalization round trip to the Y identity frame. There is no free backward post-capture.',
        'new_kappa_claimed':False}
    (args.out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],flush=True)


if __name__=='__main__': main()
