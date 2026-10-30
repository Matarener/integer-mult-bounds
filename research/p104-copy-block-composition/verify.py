"""Replay the complete retained-copy and R22 composition.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
All source construction, native, caller and compiler credit remains in NOTICE.
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
from sources import sources, load, need
from construct import construct, digest


def declared_price(parent):
    text = (parent/'pricing.py').read_text()
    for before, after in json.loads((HERE/'PRICING-EDITS.json').read_bytes()):
        need(text.count(before) == 1, 'One declared price edit')
        text = text.replace(before, after)
    need(text == (HERE/'pricing.py').read_text(), 'Only declared price changes')


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid composition accepted')


def delta(before, after):
    values = Counter(after)
    values.subtract(before)
    return {r: n for r, n in values.items() if n}


def controls(source, word, L):
    out = {}
    bad = deepcopy(word)
    bad['initial'][741] = source['initial'][741]
    out['omit_R22_input_endpoint'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['final'][405] = source['final'][405]
    out['retain_old_R22_target'] = reject(lambda: L.replay(bad))
    move = next(i for i, e in enumerate(word['program'])
                if e[0] == 'MOVE' and e[1] == 41 and e[3] == 1090)
    bad = deepcopy(word)
    del bad['program'][move]
    out['omit_paid_R22_query'] = reject(lambda: L.replay(bad))
    first_cache = word['public'] + 9
    move = next(i for i, e in enumerate(word['program']) if e[0] == 'MOVE' and e[1] >= first_cache)
    copy = next(i for i, e in enumerate(word['program']) if e[0] == 'COPY' and e[1] >= first_cache)
    clear = next(i for i, e in enumerate(word['program']) if e[0] == 'CLEAR' and e[1] >= first_cache)
    bad = deepcopy(word)
    del bad['program'][move]
    out['omit_paid_copy_query'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['program'][copy][-2] = '2'
    out['wrong_copy_value'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    del bad['program'][clear]
    out['omit_copy_clear'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['initial'][742] = source['initial'][742]
    out['omit_second_block_input'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['final'][225] = source['final'][225]
    out['omit_second_block_output'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    move = next(i for i, e in enumerate(bad['program']) if e[0] == 'MOVE' and e[3] == 1092)
    del bad['program'][move]
    out['omit_second_block_query'] = reject(lambda: L.replay(bad))
    return out


def fixed_grid(price, L):
    E = L.load(L.ROOT/'research/higher-moment-strictification/verify.py', 'composed_grid_intervals')
    targets = {int(k): v for k, v in price['targets'].items()}
    paid = {int(k): v for k, v in price['paid'].items()}
    reserve, step, gap, cap = Q(1, 10**12), Q(1, 10**14), Q(5, 10**12), Q('.0034')
    claim, tested = Q(price['kappa']), Q(price['strictification']['tested'])
    need((tested/step).denominator == 1 and tested-claim == gap, 'Fixed published/tested grid')
    def margin(c):
        t, p = E.moment(targets, 1-c), E.moment(paid, 1-c)
        return ((1-reserve)*t[0]-p[1], (1-reserve)*t[1]-p[0])
    positive, negative = margin(tested), margin(tested+step)
    need(positive[0] > 0 and negative[1] < 0, 'The next tested grid point fails the fixed reserve')
    derivative_upper = Q(0)
    for rank in set(targets) | set(paid):
        count = (1-reserve)*targets.get(rank, 0)-paid.get(rank, 0)
        logarithm = E.log_bounds(rank)
        low = E.mul(E.power(rank, 1-cap), logarithm)[0]
        high = rank*logarithm[1]
        derivative_upper -= count*(low if count >= 0 else high)
    need(derivative_upper < 0, 'Fixed-reserve margin decreases on the entire retained BIT interval')
    return dict(grid=step, tested_gap=gap, reserve=reserve, cap=cap,
        largest_published_grid=claim, largest_tested_grid=tested, next_tested_grid=tested+step,
        accepted_margin=positive, rejected_margin=negative, derivative_upper=derivative_upper,
        scope='Maximum on the 1e-14 grid for this exact profile, fixed reserve and tested gap. Different compiler parameters, words and BIT caps remain outside this claim.')


def run():
    with ExitStack() as stack:
        parent, _ = stack.enter_context(sources())
        cursor = parent
        for depth in range(7):
            cursor, root = stack.enter_context(load(cursor/'sources.py', 'copy_block_source_'+str(depth)).sources())
        declared_price(parent)
        L = load(parent/'local.py', 'local')
        L.ROOT = root
        source, old = L.read(parent/'WORD.json.gz'), L.read(parent/'RESULT.json')
        need(digest(source) == old['canonical_word_sha256'], 'Exact published retained-copy word')
        baseline = L.replay(source)
        need(json.loads(json.dumps(baseline)) == old['local'], 'Exact source local receipt')
        word, witness = construct(source)
        local = L.replay(word)
        transpose = L.reverse_columns(word)
        need((local['public_inputs'], local['owned_fields'], local['owned_lifetimes'], local['peak_owned_fields'])
             == (770, 25, 27, 13), 'Complete arbitrary-input and storage inventory')
        need(local['real_scalar_allowance'] == baseline['real_scalar_allowance'], 'No extra scalar allowance')
        change = dict(paid=delta(baseline['paid'], local['paid']), targets=delta(baseline['helpers'], local['helpers']))
        need(change == {'paid': {1: 2, 4: 2, 5: -2}, 'targets': {1: -2, 4: 2, 5: 2, 8: -2}},
             'Exact changed paid and target profiles')
        negative = controls(source, word, L)
        print('PASS composition, all795 scalar inputs, transpose and owned lifetimes', flush=True)
        native = L.native(word)
        C = load(root/'research/p104-productive-controller/caller.py', 'copy_block_caller')
        caller = C.construct()
        need(caller == L.read(root/'research/p104-productive-controller/CONTROLLER.json'), 'Exact source physical caller')
        physical = C.physical(caller, word)
        print('PASS every native phase and complete physical caller', flush=True)
        P = load(HERE/'pricing.py', 'copy_block_price')
        price = P.run(local, native, caller, physical)
        grid = fixed_grid(price, L)
        need(price['previous_pr5786'] == old['complete_cost']['kappa'], 'Exact predecessor claim')
        negative.update(C.controls(caller))
        bad = deepcopy(local)
        bad['paid'][1] -= 1
        negative['omit_query_from_invoice'] = reject(lambda: P.assemble(bad, native, caller, physical))
        bad = deepcopy(local)
        bad['helpers'][8] += 1
        negative['retain_obsolete_helper_credit'] = reject(lambda: P.assemble(bad, native, caller, physical))
        result = dict(status='PASS_P104_COMPOSED_BLOCKS_KAPPA_00312289583377',
            source_commit='6b936acd68a7e0f9062037900f0fe9bc4b6fdd25',
            canonical_word_sha256=digest(word), instructions=len(word['program']),
            source_local=baseline, local=local, delta=change, separate_columns=transpose,
            native=native, physical_caller=physical, complete_cost=price, negative_controls=negative,
            fixed_contract_grid_optimum=grid,
            limits=['Five inherited framework assumptions remain.', 'Independent scientific acceptance is pending.',
                    'The large uniform word and rounded multiplier are not materialized.', 'The selected frontier is unchanged.'])
        return P.encode(result), witness, word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='copy-block-bytecode-') as cache:
        sys.pycache_prefix = cache
        result, witness, word = run()
    for name, value in (('RESULT.json', result), ('HUNKS.json', witness), ('WORD.json.gz', word)):
        path = HERE/name
        if args.write:
            raw = (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()
            path.write_bytes(gzip.compress(raw, mtime=0) if name.endswith('.gz') else raw)
        else:
            raw = path.read_bytes()
            need(json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw) == value, 'Exact retained output: '+name)
    print(result['status'])


if __name__ == '__main__':
    main()
