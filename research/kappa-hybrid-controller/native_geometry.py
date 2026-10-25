#!/usr/bin/env python3
"""Independent exact audit of native/direct controller specialization.

The local supplier is separately validated by the complete source-bound gate.
This checks the literal specialized Laurent word, every surviving native
contact, every whole idle and endpoint phase, and both direct Q kernels.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE = HERE.parent/'pr4359-p7-padding/source'
LOCAL_HELPERS = {4: 26, 5: 2, 7: 29, 8: 42, 9: 309}
LOCAL_PAID = {1: 2253, 2: 515, 3: 445, 4: 102, 5: 40, 8: 8}
PINS = {
    'research/kappa-rebuild/transfer-audit/p3_native_audit.py': '5504a55a50546418d10c522984438cdeedb44993f7c1dab7bd4aa1ae0515d902',
    'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json': 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
}
CLIFFORD_SHA256 = '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'


def need(ok, why):
    if not ok:
        raise AssertionError(why)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


# Phase algebra adapted without mathematical changes from PR4416 native_inventory.py.
def norm(terms):
    out = Counter()
    for axis, value in terms:
        out[axis] += value
    return tuple(sorted((axis, value % 4) for axis, value in out.items() if axis and value % 4))


def act(columns, value):
    result = 0
    while value:
        low = value & -value
        result ^= columns[low.bit_length()-1]
        value ^= low
    return result


@lru_cache(None)
def polynomial(terms, dimension):
    linear = [0]*dimension
    quadratic = [0]*dimension
    for axis, value in terms:
        support = [i for i in range(dimension) if axis >> i & 1]
        for i in support:
            linear[i] = (linear[i]+value) % 4
            if value % 2:
                for j in support:
                    if i < j:
                        quadratic[i] ^= 1 << j
    return tuple(linear), tuple(quadratic)


def contact(old, new, route, dimension):
    moved = norm((act(route, axis), value) for axis, value in old)
    left, right = polynomial(moved, dimension), polynomial(new, dimension)
    need(left[1] == right[1], 'Actual native contact has identical quadratic part')
    delta = tuple((a-b) % 4 for a, b in zip(right[0], left[0]))
    need(all(value in (0, 2) for value in delta), 'Even linear phase is a physical translation')
    shift = sum((value//2) << i for i, value in enumerate(delta))
    need(polynomial(norm(list(moved)+[(shift, 2)]), dimension) == right, 'Full native forward phase')
    inverse_shift = act(route, shift)
    inverse = norm([(act(route, axis), value) for axis, value in new]+[(inverse_shift, 2)])
    need(polynomial(inverse, dimension) == polynomial(old, dimension), 'Full inverse contact phase')
    return {'translation': shift, 'inverse_translation': inverse_shift}


def scalar_invoice(case, native_scalar):
    word = case['right_program']+case['left_program']
    counts = Counter(row[0] for row in word)
    need(all(Q(row[-1]) in (1, -1) for row in word if row[0] in ('ADD', 'SCALE')),
         'Literal boundary word has only unit coefficients')
    adds = counts['ADD']+3*counts['SWAP']
    negs = counts['SCALE']+counts['SWAP']
    bridges = sum(row[0] == 'ADD' for row in case['physical_events'])
    swaps = sum(row[0] == 'SIGNED_SWAP' for row in case['physical_events'])
    return native_scalar+112*(8*(adds+bridges+3*swaps)+2*negs)


def specialize(case, native_mask):
    """Apply the ring homomorphism D_s -> 1 to the actual finite word."""
    result = json.loads(json.dumps(case))
    for event in result['physical_events']:
        if event[0] == 'LOCAL' and not (native_mask >> event[1]) & 1:
            event[0] = 'DIRECT'
        elif event[0] == 'IDLE':
            event[2] = [s for s in event[2] if (native_mask >> s) & 1]
    for monomial in result['exact_diagonal_monomials']:
        for stage in range(2*case['pairs']+1):
            if not (native_mask >> stage) & 1:
                monomial[stage+1] = 0
    for window in result['retained_idle_windows']:
        window['original_stages'] = window['stages'][:]
        window['stages'] = [s for s in window['stages'] if (native_mask >> s) & 1]
        window['rank'] = 8*len(window['stages'])
    result['native_mask'] = native_mask
    return result


def replay(case):
    """Replay all input columns over the exact integer Laurent ring."""
    rows = 2*case['pairs']
    variables = len(case['coefficient_variables'])
    zero = (0,)*variables
    matrix = [[{zero:Q(1)} if i == j else {} for j in range(rows)] for i in range(rows)]

    def add(a, b, coefficient=1):
        out = a.copy()
        for term, value in b.items():
            out[term] = out.get(term, Q(0))+coefficient*value
            if not out[term]:
                del out[term]
        return out

    def shift(row, delta):
        return {tuple(x+y for x,y in zip(term,delta)):value for term,value in row.items()}

    events = case['right_program']+case['physical_events']+case['left_program']
    for event in events:
        kind = event[0]
        if kind == 'ADD':
            _, destination, source, coefficient = event
            matrix[destination] = [add(a,b,Q(coefficient)) for a,b in zip(matrix[destination],matrix[source])]
        elif kind == 'SCALE':
            _, role, coefficient = event
            matrix[role] = [{term:Q(coefficient)*value for term,value in row.items()} for row in matrix[role]]
        elif kind == 'SWAP':
            _, a, b = event
            matrix[a],matrix[b] = matrix[b],matrix[a]
        elif kind == 'SIGNED_SWAP':
            _, a, b = event
            matrix[a],matrix[b] = matrix[b],[{term:-value for term,value in row.items()} for row in matrix[a]]
        elif kind == 'IDLE':
            _, pair, stages = event
            delta = (0,)+tuple(int(s in stages) for s in range(variables-1))
            for role in (2*pair,2*pair+1):
                matrix[role] = [shift(row,delta) for row in matrix[role]]
        elif kind in ('LOCAL','DIRECT'):
            _, stage, pair, backward = event
            x,y = 2*pair,2*pair+1
            destination,source,coefficient = (x,y,-1) if backward else (y,x,1)
            delta = (1 if backward else -1,)+(0,)*(variables-1)
            matrix[destination] = [add(a,shift(b,delta),coefficient)
                                   for a,b in zip(matrix[destination],matrix[source])]
            if kind == 'LOCAL':
                delta = tuple(int(i == stage+1) for i in range(variables))
                for role in (x,y):
                    matrix[role] = [shift(row,delta) for row in matrix[role]]
        else:
            raise AssertionError('Unrecognized literal event '+kind)
    expected = [[{tuple(case['exact_diagonal_monomials'][i]):Q(1)} if i == j else {}
                 for j in range(rows)] for i in range(rows)]
    need(matrix == expected,'Every exact coefficient of the specialized physical controller')
    return {'input_columns':rows,'matrix_entries':rows*rows,'literal_events':len(events)}


def direct_recipes(phases, ce):
    """Complete-phase rank-one kernels, with literal owned-copy semantics."""
    records = []
    negative_missing_inverse_shift = 0
    for port, recipe in enumerate(phases['recipes']):
        q = recipe['q']
        basis = recipe['idle_children'][0]['orthogonal_axes'][:8]
        columns = (q,*basis)
        need(all((a&b).bit_count()%2 == int(i == j)
                 for i,a in enumerate(columns) for j,b in enumerate(columns)),
             'The actual port supplies a full orthonormal coordinate basis')
        P = ce.perm(9,ce.transpose(columns,9))
        child = ce.fourier(9,[0])
        forward = P.adjoint().then(child).then(P)
        inverse = forward.then(ce.xgate(9,q))
        directions = {}
        for direction,op,sign in (('forward_Q',forward,1),('inverse_Q',inverse,-1)):
            exact = ce.cgate(9,q,sign)
            need(op.tab == exact.tab and op.zero_state() == exact.zero_state(),
                 'All Pauli generators and the absolute phase of the actual Q kernel')
            # The tableau fixes translation covariance, so equality on |0>
            # proves every literal column; this loop independently checks the
            # two nonzero coefficients of all 512 columns using the route.
            a,b = (1,sign),(1,-sign)
            for x in range(512):
                y = ce.mv(ce.inv(ce.transpose(columns,9),9),x)
                destinations = [ce.mv(ce.transpose(columns,9),y),
                                ce.mv(ce.transpose(columns,9),y^1)]
                coefficients = [(1,1),(1,-1)]
                if sign == -1:
                    destinations = [z^q for z in destinations]
                observed = dict(zip(destinations,coefficients))
                need(observed == {x:a,x^q:b},'Literal two-point kernel on every coordinate column')
            lowered,compiled = ce.lower_child(exact)
            need(lowered['rank'] == 1 and compiled.tab == exact.tab and
                 compiled.zero_state() == exact.zero_state(),'Independent complete-phase rank-one lowering')
            directions[direction] = {'kernel_numerator_at_x':a,'kernel_numerator_at_x_xor_q':b,
                                     'kernel_denominator':2,'rank':1,'phase_Z4':0,
                                     'translation_after':q if sign == -1 else 0,
                                     'independent_lowering':lowered}
        need(forward.tab != inverse.tab or forward.zero_state() != inverse.zero_state(),
             'Omitting the inverse translation changes the operator')
        negative_missing_inverse_shift += 1
        records.append({'port':port,'q':q,'route_columns':columns,'directions':directions,
                        'owned_scratch_fields':1,'productive_scratch_endpoints':0,
                        'paid_queries_per_direct_stage':1,
                        'literal_forward':[['ZERO','tmp'],['ADD','tmp','X',1],
                                           ['GAUSSIAN_Q_INVERSE','tmp'],['ADD','Y','tmp',1],['RELEASE','tmp']],
                        'literal_backward':[['ZERO','tmp'],['ADD','tmp','Y',1],
                                            ['GAUSSIAN_Q','tmp'],['ADD','X','tmp',-1],['RELEASE','tmp']]})
    return records,negative_missing_inverse_shift


def geometry(case, phases, native_mask):
    p = case['pairs']
    dimension = 9+16*p
    axes = tuple(1<<i for i in range(dimension))

    def completed(stage):
        return norm((axis,1) for axis in axes[:9+8*stage])

    def stage_frame(stage,q):
        return norm([(axis,1) for axis in axes[:9]]+[(q,-1)] if stage == 0 else
                    [(axis,1) for axis in axes[9+8*(stage-1):9+8*stage]])

    contacts = []
    stages = [event for event in case['physical_events'] if event[0] == 'LOCAL']
    for _,stage,pair,backward in stages:
        sign = -1 if backward else 1
        spectator = norm((axis,1) for axis in axes[9:9+8*stage])
        for port,recipe in enumerate(phases['recipes']):
            q = recipe['q']
            basis = recipe['idle_children'][0]['orthogonal_axes'][:8]
            need(all((b&q).bit_count()%2 == 0 for b in basis),'Actual owner basis orthogonal to q')
            need(all((a&b).bit_count()%2 == int(i == j)
                     for i,a in enumerate(basis) for j,b in enumerate(basis)), 'Actual owner basis orthonormal')
            swaps = [] if stage == 0 else [b^axes[9+8*(stage-1)+i] for i,b in enumerate(basis)]
            route = tuple(e^act(swaps,sum(((e&v).bit_count()%2)<<i for i,v in enumerate(swaps))) for e in axes)
            need(all(act(route,route[i]) == axes[i] for i in range(dimension)), 'Full route involution')
            need(all((a&b).bit_count()%2 == int(i == j)
                     for i,a in enumerate(route) for j,b in enumerate(route)), 'Full route orthogonal')
            need(act(route,q) == q,'The port axis is fixed')
            raw_x = norm([(q,1)]) if stage == 0 else completed(stage-1)
            raw_y = () if stage == 0 else norm(list(raw_x)+[(q,-1)])
            local_x0 = norm(list(spectator)+[(q,sign)])
            local_y0 = spectator
            local_x1 = norm(list(spectator)+[(axis,sign) for axis in axes[:9]])
            local_y1 = norm(list(local_x1)+[(q,-sign)])
            out_x = completed(stage)
            out_y = norm(list(out_x)+[(q,-1)])
            maps = {name:contact(old,new,route,dimension) for name,old,new in (
                ('entry_X',raw_x,local_x0),('entry_Y',raw_y,local_y0),
                ('exit_X',local_x1,out_x),('exit_Y',local_y1,out_y))}
            delta = stage_frame(stage,q)
            for incoming,outgoing in ((raw_x,out_x),(raw_y,out_y)):
                need(polynomial(norm(list(outgoing)+[(a,-c) for a,c in incoming]),dimension) ==
                     polynomial(delta,dimension),'Actual diagonal operator is D_s on arbitrary physical inputs')
            cross = norm(list(out_y if sign == 1 else out_x)+
                         [(a,-c) for a,c in (raw_x if sign == 1 else raw_y)])
            need(polynomial(cross,dimension) == polynomial(norm(list(delta)+[(q,-sign)]),dimension),
                 'Actual cross operator is D_s Q^(-sign) on arbitrary physical inputs')
            contacts.append({'stage':stage,'pair':pair,'port':port,'backward':backward,'route':route,'maps':maps})
    endpoints = []
    target_main = Counter()
    endpoint_negative = 0
    for role,term in enumerate(case['exact_diagonal_monomials']):
        qp,selected = term[0],term[1:]
        need(qp in (-1,1) and set(selected) <= {0,1},'Endpoint exponent alphabet')
        need(all(not yes or (native_mask>>stage)&1 for stage,yes in enumerate(selected)),
             'No productive rank on any specialized-away D axis')
        for port,recipe in enumerate(phases['recipes']):
            q = recipe['q']
            physical = norm([(q,qp)]+[entry for stage,yes in enumerate(selected) if yes
                                      for entry in stage_frame(stage,q)])
            positive = list(axes[:9]) if selected[0] else [q]
            positive += [axis for stage in range(1,len(selected)) if selected[stage]
                         for axis in axes[9+8*(stage-1):9+8*stage]]
            shift = q if qp == -1 else 0
            need(len(positive) == 1+8*sum(selected),'Specialized productive endpoint rank')
            need(polynomial(norm(list(physical)+[(shift,2)]),dimension) ==
                 polynomial(norm((axis,1) for axis in positive),dimension),'Complete specialized endpoint phase')
            if shift:
                need(polynomial(physical,dimension) != polynomial(norm((axis,1) for axis in positive),dimension),
                     'Omitting the endpoint translation changes the operator')
                endpoint_negative += 1
            endpoints.append({'role':role,'port':port,'rank':len(positive),'axes':positive,'translation':shift})
            target_main[len(positive)] += 1
    literal = Counter((row[1],tuple(row[2])) for row in case['physical_events'] if row[0] == 'IDLE')
    recorded = Counter((row['pair'],tuple(row['stages'])) for row in case['retained_idle_windows'])
    need(literal == recorded,'Bijection of specialized literal IDLE records and whole idle invoices')
    idle,records = Counter(),[]
    for window in case['retained_idle_windows']:
        selected = window['stages']
        for port,recipe in enumerate(phases['recipes']):
            q = recipe['q']
            positive = recipe['idle_children'][0]['orthogonal_axes'][:8] if 0 in selected else []
            positive += [axis for stage in selected if stage > 0
                         for axis in axes[9+8*(stage-1):9+8*stage]]
            shift = recipe['idle_children'][0]['translation_after'] if 0 in selected else 0
            desired = norm(entry for stage in selected for entry in stage_frame(stage,q))
            actual = norm([(axis,1) for axis in positive]+[(shift,2)])
            need(len(positive) == window['rank'],'Exact specialized whole idle rank')
            need(all((a&b).bit_count()%2 == int(i == j)
                     for i,a in enumerate(positive) for j,b in enumerate(positive)),
                 'Exact specialized whole idle independent orthogonal axes')
            need(polynomial(actual,dimension) == polynomial(desired,dimension),'Complete specialized whole idle phase')
            if positive:
                idle[len(positive)] += 2
            records.append({'window':window['index'],'pair':window['pair'],'stages':selected,'port':port,
                            'axes':positive,'translation':shift,'paid_queries':2 if positive else 0})
    targets = target_main+Counter({r:c*len(stages) for r,c in LOCAL_HELPERS.items()})
    paid = Counter({r:c*len(stages) for r,c in LOCAL_PAID.items()})+idle
    direct = [event for event in case['physical_events'] if event[0] == 'DIRECT']
    paid[1] += len(phases['recipes'])*len(direct)
    scalar_native = sum(158168 if row[3] else 158120 for row in stages)
    scalar_boundary = scalar_invoice(case,scalar_native)
    scalar_direct = 64*len(phases['recipes'])*len(direct)
    receipt = {'dimension':dimension,'native_stages':len(stages),'direct_stages':len(direct),
               'native_stage_indices':[row[1] for row in stages],
               'direct_stage_indices':[row[1] for row in direct],
               'main_contact_checks':4*len(contacts),'productive_main_fields':sum(target_main.values()),
               'fresh_helper_fields':408*len(stages),'productive_fields':sum(targets.values()),
               'targets':dict(sorted(targets.items())),'paid':dict(sorted(paid.items())),
               'whole_idle_profile':dict(sorted(idle.items())),
               'direct_paid_queries':len(phases['recipes'])*len(direct),
               'direct_scalar_allowance':scalar_direct,'native_and_boundary_scalar_allowance':scalar_boundary,
               'scalar_allowance':scalar_boundary+scalar_direct,
               'paid_calls':sum(paid.values()),'rank_margin':sum(r*c for r,c in targets.items())-sum(r*c for r,c in paid.items()),
               'omitted_endpoint_translation_rejected':endpoint_negative}
    return receipt,{'contacts':contacts,'endpoints':endpoints,'whole_idles':records}


def run(case_path, native_mask, source_root=DEFAULT_SOURCE, output_dir=None):
    root = Path(source_root).resolve()
    source_pins = {}
    for relative,expected in PINS.items():
        data = (root/relative).read_bytes()
        need(sha256(data).hexdigest() == expected,'Exact source pin: '+relative)
        source_pins[relative] = expected
    ce_path = HERE/'dependencies/clifford_exact.py'
    need(sha256(ce_path.read_bytes()).hexdigest() == CLIFFORD_SHA256,'Pinned exact Clifford compiler')
    ce = load(ce_path,'hybrid_exact_clifford_audit')
    independent = load(root/list(PINS)[0],'hybrid_original_laurent')
    phases = read(root/list(PINS)[1])
    need(len(phases['recipes']) == 112,'All112 actual ports')
    original_case = read(case_path)
    need(0 < native_mask < 1<<(2*original_case['pairs']+1) and native_mask&1,
         'Selected mixed controller retains D0')
    independent.replay(original_case)
    case = specialize(original_case,native_mask)
    laurent = replay(case)
    negative = json.loads(json.dumps(case))
    direct_event = next(event for event in negative['physical_events'] if event[0] == 'DIRECT')
    direct_event[3] = not direct_event[3]
    negative_ok = False
    try:
        replay(negative)
    except AssertionError:
        negative_ok = True
    need(negative_ok,'A wrong direct shear orientation fails the full exact Laurent word')
    direct,missing_shift = direct_recipes(phases,ce)
    receipt,artifact = geometry(case,phases,native_mask)
    artifact.update({'formal':case,'direct_recipes':direct})
    payload = canonical(artifact)
    receipt.update({'schema':'independent-exact-native-direct-controller-audit/1',
                    'status':'PASS_SPECIALIZED_LAURENT_NATIVE_CONTACTS_DIRECT_KERNELS_ENDPOINTS_IDLES',
                    'p':case['pairs'],'keep':case['keep_idle_mask'],'native_mask':native_mask,
                    'laurent':laurent,'wrong_direct_orientation_rejected':negative_ok,
                    'omitted_direct_inverse_translation_rejected':missing_shift,
                    'direct_query_rank_for_f_columns':'f, with the same ancestor weight; never f rank-one column queries',
                    'direct_scratch_ownership':'Copy source to an owned zero array; query that copy; add to destination; release. No arbitrary helper or productive scratch credit.',
                    'artifact_sha256':sha256(payload).hexdigest(),
                    'artifact_hash_encoding':'Uncompressed UTF-8 JSON, sort_keys=True, separators=(comma,colon)',
                    'case_sha256':sha256(case_path.read_bytes()).hexdigest(),
                    'clifford_source_sha256':CLIFFORD_SHA256,
                    'source_sha256':source_pins,
                    'local_profiles':'Independently audited PR4441 retimed local supplier; the enclosing native_inventory reruns its complete literal and phase gate.',
                    'limits':'Finite exact native/direct phase and scalar accounting; tensor strictification, full finite route and owned stock invoices, precision, analytic and fixed-tape/recovery premises remain separate.'})
    if output_dir is not None:
        output_dir.mkdir(parents=True,exist_ok=True)
        (output_dir/'HYBRID-GEOMETRY.json.gz').write_bytes(gzip.compress(payload,compresslevel=9,mtime=0))
        (output_dir/'HYBRID-GEOMETRY.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    return receipt,artifact


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',type=Path,default=HERE/'controller/P17-FULL-LAURENT-CASE.json')
    parser.add_argument('--native-mask',type=int,default=28633115307)
    parser.add_argument('--source-root',type=Path,default=DEFAULT_SOURCE)
    parser.add_argument('--output-dir',type=Path)
    args = parser.parse_args()
    result,_ = run(args.case,args.native_mask,args.source_root,args.output_dir)
    print(json.dumps({k:result[k] for k in ('status','p','keep','native_mask','native_stages','direct_stages','targets','paid','rank_margin','scalar_allowance')},sort_keys=True))
