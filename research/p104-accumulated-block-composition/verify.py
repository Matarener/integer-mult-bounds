"""Replay the exact accumulated-update/two-block composition and full price.

Mason Hale with substantial OpenAI Codex assistance. Apache-2.0.
Ali Romman's source replayers, Joel Pulikkan's block edits, and the complete
native/controller/compiler lineage remain credited in NOTICE and vendor/.
"""
import argparse
from collections import Counter
from contextlib import ExitStack
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sources import sources, load, need, authenticate
import construct


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def declared_copy(source, target, changes):
    text = source.read_text(encoding='utf-8')
    for before, after in json.loads(changes.read_bytes()):
        need(text.count(before) == 1, 'One exact declared source adaptation')
        text = text.replace(before, after)
    need(text == target.read_text(encoding='utf-8'), 'Only declared source edits: '+target.name)


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid composed construction accepted')


def difference(old, new):
    result = Counter(new)
    result.subtract(old)
    return {r: c for r, c in result.items() if c}


def checker(path, name, constructor):
    """Bind each unchanged checker to its explicitly named constructor."""
    previous = sys.modules.get('construct')
    try:
        sys.modules['construct'] = constructor
        return load(path, name)
    finally:
        if previous is None:
            sys.modules.pop('construct', None)
        else:
            sys.modules['construct'] = previous


def transfer_certificate(blocks, source, word, A):
    B = checker(blocks/'compatibility.py', 'block_scalar_matrices', construct)
    edits = json.loads((blocks/'source/R22-EDITS.json').read_bytes())
    matrices = []
    for i, (old, new) in enumerate(edits['program']):
        roles = sorted({r for e in old+new if e[0] in ('ADD', 'SCALE')
                        for r in (e[1:3] if e[0] == 'ADD' else [e[1]])})
        left, right = B.matrix(old, roles), B.matrix(new, roles)
        need(left == right, 'R22 scalar transfer '+str(i))
        matrices.append(dict(edit=i, roles=roles, matrix=left))
    mutation = deepcopy(edits['program'][0][1])
    next(e for e in mutation if e[0] == 'ADD')[3] = '123456'
    need(B.matrix(mutation, matrices[0]['roles']) != matrices[0]['matrix'],
         'Wrong R22 coefficient changes the transfer')
    owned = lambda w: [e for e in w['program'] if e[0] in ('INIT', 'COPY', 'CLEAR')]
    need(owned(source) == owned(word), 'All 30 owned lifetimes and 23 COPY events preserved')
    before, after = A.copy_values(source), A.copy_values(word)
    need(before == after and len(after) == 23, 'All exact COPY values preserved')
    return dict(R22_matrices=matrices, copied_values=after,
                all_owned_events_sha256=construct.digest(owned(word)),
                wrong_scalar_coefficient_rejected=True)


def block_gain(price, L):
    """A range proof, distinct from searching the actual full-profile root."""
    E = L.load(L.ROOT/'research/higher-moment-strictification/verify.py', 'block_gain_intervals')
    cap = Q('.0034')
    derivative_upper = 20*E.log_bounds(5)[1] - 2*E.power(8, 1-cap)[0]*E.log_bounds(8)[0]
    need(derivative_upper < 0, 'Block gain derivative strictly negative')
    need(-4+4*5-2*8 == 0, 'Zero block gain at exponent one')
    need(Q(0) < Q(price['kappa']) < cap, 'Actual exponent is in certified interval')
    return dict(signed_gain_per_local={1: -4, 5: 4, 8: -2},
                derivative_upper=derivative_upper, exponent_interval=[1-cap, 1],
                scope='Strict gain for 1-.0034 <= t < 1; not a claim for every 0<t<1.')



def role92_checks(source, word, plan, C, A, L):
    slot = source['public']+source['owned_fields']
    need(slot == 798 and word['owned_fields'] == source['owned_fields']+1, 'One new paid owned label')
    life = [(i,e) for i,e in enumerate(word['program']) if e[1] == slot
            or (e[0] in ('ADD','COPY') and e[2] == slot)]
    old = [e[:-1] for e in source['program'] if e[0] in ('INIT','COPY','CLEAR')]
    retained = [e[:-1] for e in word['program'] if e[0] in ('INIT','COPY','CLEAR') and e[1] != slot]
    need(old == retained and len(old) == 83, 'All prior lifecycle roles and coefficients retained')
    values = A.copy_values(word)
    need(values == A.copy_values(source) and len(values) == 23, 'Fourth accumulation preserves all COPY payloads')
    negative = {}
    for name, at in [('omit_query', next(i for i,e in life if e[0] == 'MOVE')),
                     ('omit_component', next(i for i,e in life if e[0] == 'ADD' and e[1] == slot)),
                     ('omit_delivery', next(i for i,e in life if e[0] == 'ADD' and e[2] == slot)),
                     ('omit_clear', next(i for i,e in life if e[0] == 'CLEAR'))]:
        bad = deepcopy(word)
        del bad['program'][at]
        negative['role92_'+name] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['owned_fields'] -= 1
    negative['role92_unallocated_storage'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    delivery = next(i for i,e in life if e[0] == 'ADD' and e[2] == slot)
    bad['program'][delivery][-2] = '-1'
    negative['role92_wrong_delivery_sign'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['initial'][753] = source['initial'][753]
    negative['role92_old_helper_boundary'] = reject(lambda: L.replay(bad))
    bad_plan = deepcopy(plan)
    bad_plan['accumulation']['uses'].pop(2)
    negative['role92_undeclared_update'] = reject(lambda: C.construct(source, bad_plan))
    bad = deepcopy(source)
    bad['program'][plan['accumulation']['uses'][1]-1] = ['ADD',63,92,'1',267]
    negative['role92_early_destination_read'] = reject(lambda: C.construct(bad, plan))
    before, after = L.replay(source), L.replay(word)
    dp, dt = difference(before['paid'], after['paid']), difference(before['helpers'], after['helpers'])
    need(dp == {1:-5,4:-1,5:5} and dt == {1:-4,5:4}, 'Complete fourth-accumulation invoice')
    signed = Counter(dt)
    signed.subtract(dp)
    need({r:c for r,c in signed.items() if c} == {1:1,4:1,5:-1}, 'Strict subadditivity gain H1+H4-H5')
    need(after['paid_rank_mass'] == before['paid_rank_mass']+16, 'New native rank mass enters the precision envelope')
    return dict(new_lifetime=life, prior_lifecycle_events=len(old), copied_values_sha256=construct.digest(values),
                delta_paid=dp, delta_helpers=dt, local_signed_gain={1:1,4:1,5:-1},
                gain_proof='Strict subadditivity: 1^t+4^t>5^t for every 0<t<1.',
                public_inputs=770, owned_fields=29, owned_lifetimes=31, peak_owned_fields=13), negative

def run():
    with ExitStack() as stack:
        accumulated, blocks = stack.enter_context(sources())
        source_auth = authenticate()
        parent, _ = stack.enter_context(load(accumulated/'sources.py', 'composition_source').sources())
        cursor = parent
        for depth in range(7):
            cursor, root = stack.enter_context(load(cursor/'sources.py', 'composition_nested_'+str(depth)).sources())
        declared_copy(blocks/'construct.py', HERE/'construct.py', HERE/'CONSTRUCT-EDITS.json')
        declared_copy(accumulated/'pricing.py', HERE/'pricing.py', HERE/'PRICING-EDITS.json')
        declared_copy(accumulated/'local.py', HERE/'local.py', HERE/'LOCAL-EDITS.json')
        L = load(HERE/'local.py', 'local')
        L.ROOT = root
        source, old = L.read(accumulated/'WORD.json.gz'), L.read(accumulated/'RESULT.json')
        need(construct.digest(source) == old['canonical_word_sha256'], 'Exact PR5802 source word')
        baseline = L.replay(source)
        need(canonical(baseline) == canonical(old['local']), 'Reproduced complete source local receipt')
        intermediate, witness = construct.construct(source)
        intermediate_local = L.replay(intermediate)
        AC = load(accumulated/'construct.py', 'accumulated_constructor')
        role_plan = L.read(HERE/'ROLE92-PLAN.json')
        word, role_witness = AC.construct(intermediate, role_plan)
        word['schema'] = 'p104-accumulated-block-composition/2'
        witness['role92'] = dict(source_sha256=construct.digest(intermediate), result_sha256=construct.digest(word), **role_witness)
        local = L.replay(word)
        reverse = L.reverse_columns(word)
        need((local['public_inputs'], local['owned_fields'], local['owned_lifetimes'], local['peak_owned_fields'])
             == (770, 29, 31, 13), 'Complete arbitrary-input and owned inventory')
        need(baseline['real_scalar_allowance'] == intermediate_local['real_scalar_allowance'] == 225026
             and local['real_scalar_allowance'] == 225038, 'Twelve additional real scalar primitives are charged')
        change = {k: difference(baseline[k], local[k]) for k in ('paid', 'helpers')}
        need(change == {'paid': {1: -3, 4: 1, 5: 3}, 'helpers': {1: -6, 4: 2, 5: 6, 8: -2}},
             'Exact complete local composition delta')
        A = checker(accumulated/'verify.py', 'accumulated_checker', AC)
        B = checker(blocks/'verify.py', 'blocks_checker', construct)
        protection = A.protected(L.read(parent/'WORD.json.gz'), source)
        compatibility = transfer_certificate(blocks, source, intermediate, A)
        role_compatibility, role_negative = role92_checks(intermediate, word, role_plan, AC, A, L)
        negative = {'block_'+k: v for k, v in B.controls(source, intermediate, L).items()}
        negative.update({'accumulation_'+k: v for k, v in A.controls(
            L.read(parent/'WORD.json.gz'), word, L.read(accumulated/'PLAN.json'), L).items()})
        negative.update(role_negative)
        print('PASS literal composition, all799 input coordinates, transpose, COPY values and controls', flush=True)
        native = L.native(word)
        C = load(root/'research/p104-productive-controller/caller.py', 'composition_caller')
        caller = C.construct()
        need(caller == L.read(root/'research/p104-productive-controller/CONTROLLER.json'),
             'Unchanged complete physical controller')
        physical = C.physical(caller, word)
        print('PASS every native map and phase, all helper normalizers and complete physical caller', flush=True)
        P = load(HERE/'pricing.py', 'composition_price')
        price = P.run(local, native, caller, physical)
        need(price['previous_pr5802'] == old['complete_cost']['kappa'], 'Exact strongest predecessor claim')
        grid = B.fixed_grid(price, L)
        gain = block_gain(price, L)
        negative.update({'caller_'+k: v for k, v in C.controls(caller).items()})
        bad = deepcopy(local)
        bad['paid'][1] -= 1
        negative['omit_paid_query_from_invoice'] = reject(lambda: P.assemble(bad, native, caller, physical))
        bad = deepcopy(local)
        bad['helpers'][8] += 1
        negative['invent_productive_credit'] = reject(lambda: P.assemble(bad, native, caller, physical))
        result = dict(status='PASS_P104_ACCUMULATED_BLOCK_COMPOSITION',
            source_commits={'accumulated': '9bab1ca917ec4d1a4e60f4eb8c81d7ef92908a62',
                            'blocks': '206cb717c0c07737d61637b93f7502ca48850348'},
            source_authentication=source_auth, canonical_word_sha256=construct.digest(word),
            instructions=len(word['program']), source_local=baseline, intermediate_local=intermediate_local, local=local, delta=change,
            role92_compatibility=role_compatibility,
            separate_columns=reverse, source_protected_contacts=protection,
            native=native, physical_caller=physical, complete_cost=price,
            block_gain_range=gain, fixed_contract_grid_optimum=grid, negative_controls=negative,
            limits=['Five inherited framework assumptions remain.',
                    'The large uniform word and rounded multiplier are not materialized.',
                    'Author-side and agent checks are not independent human or kernel acceptance.',
                    'The selected frontier is unchanged.'])
        return P.encode(result), witness, word, compatibility


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='accumulated-block-bytecode-') as cache:
        sys.pycache_prefix = cache
        result, witness, word, compatibility = run()
    for name, value in [('RESULT.json', result), ('HUNKS.json', witness),
                        ('WORD.json.gz', word), ('COMPATIBILITY.json', compatibility)]:
        path = HERE/name
        if args.write:
            raw = (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()
            path.write_bytes(gzip.compress(raw, mtime=0) if name.endswith('.gz') else raw)
        else:
            raw = path.read_bytes()
            old = json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)
            need(canonical(old) == canonical(value), 'Complete retained output: '+name)
    print(result['status'])


if __name__ == '__main__':
    main()
