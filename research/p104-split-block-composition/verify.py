"""Verify the composed word, the complete caller, and the fixed-block optimum.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The source exports retain the construction, verifier, and compiler notices.
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
import construct
import checks


def reject(action):
    try:
        action()
    except (ValueError, AssertionError) as error:
        return str(error)
    raise ValueError('Invalid candidate accepted')


def derived(parent, filename, editfile):
    text = (parent/filename).read_text()
    for before, after in json.loads((HERE/editfile).read_bytes()):
        need(text.count(before) == 1, 'One declared source edit')
        text = text.replace(before, after)
    need(text == (HERE/filename).read_text(), 'Only declared source edits: '+filename)


def optimality(local, native, caller, physical, price, P, root):
    T, paid, _ = P.assemble(local, native, caller, physical)
    E = load(root/'research/higher-moment-strictification/verify.py', 'block_interval_engine')
    def parts(d):
        p = Counter({d-3: 8})
        p[9-d] += 7
        p[8-d] += 1
        p.pop(0, None)
        return Counter([d,9-d]), p
    t4, p4 = parts(4)
    result = {}
    for d in range(4,9):
        td, pd = parts(d)
        td.subtract(t4)
        pd.subtract(p4)
        t, p = T.copy(), paid.copy()
        for r, n in td.items():
            t[r] += 18*n
        for r, n in pd.items():
            p[r] += 18*n
        need(min(t.values()) >= 0 and min(p.values()) >= 0, 'Nonnegative complete interval bill')
        def margin(k):
            a, b = E.moment(t,1-k), E.moment(p,1-k)
            return a[0]-b[1], a[1]-b[0]
        lo, hi, grid = 0, 10**12, 10**14
        while hi-lo > 1:
            m = (lo+hi)//2
            if margin(Q(m,grid))[0] > 0:
                lo = m
            else:
                hi = m
        low, high = Q(lo,grid), Q(hi,grid)
        need(margin(low)[0] > 0 and margin(high)[1] < 0, 'Exact rank-specific crossing')
        signed = Counter(t)
        signed.subtract(p)
        derivative = Q(0)
        for r, n in signed.items():
            logs = E.log_bounds(r)
            a = E.mul(E.power(r,1-Q('.0034')),logs)[0]
            b = r*logs[1]
            derivative -= n*(a if n >= 0 else b)
        need(derivative < 0, 'Unique crossing throughout the declared kappa interval')
        if d != 4:
            need(high < P.KAPPA, 'Certified rank-four saving exceeds every other rank ceiling')
        result[d] = {'raw_root_interval': [low,high], 'derivative_upper': derivative,
                     'local_changed_paid': parts(d)[1], 'local_changed_targets': parts(d)[0],
                     'complete_paid_calls': sum(p.values())}
    need(result[4]['raw_root_interval'] == list(map(Q,price['raw_root_interval'])), 'Same optimal complete bill')
    return result


def local_envelope_edits(parent):
    rows = json.loads((parent/'LOCAL-EDITS.json').read_bytes())
    need(rows == [["735 <= public <= 750", "public == 767"]], 'Exact inherited finite envelope edits')
    return rows


def run():
    with ExitStack() as contexts:
        parent, _ = contexts.enter_context(sources())
        derived(parent,'pricing.py','PRICING-EDITS.json')
        cursor = parent
        predecessor = None
        split = None
        for depth in range(5):
            cursor, root = contexts.enter_context(load(cursor/'sources.py','block_sources_'+str(depth)).sources())
            if depth == 0:
                split = cursor
            if depth == 1:
                predecessor = cursor
        derived(parent,'checks.py','CHECKS-EDITS.json')
        local_text = (cursor/'local.py').read_text()
        for before, after in local_envelope_edits(parent):
            need(local_text.count(before) == 1, 'One declared source envelope edit')
            local_text = local_text.replace(before,after)
        need(local_text == (parent/'local.py').read_text(), 'Only the published exact public-count change')
        L = load(parent/'local.py','local')
        L.ROOT = root
        source = L.read(parent/'WORD.json.gz')
        word, hunks = construct.construct(source)
        old_reframe, _ = construct.construct(L.read(predecessor/'WORD.json.gz'))
        retained = L.read(HERE/'source/pr5739/WORD.json.gz')
        old_reframe['schema'] = retained['schema']
        need(old_reframe == retained, 'Exact published R22 construction on its own source')
        interval = construct.interval(word)
        independent = checks.audit(word)
        transpose = checks.transpose_audit(word)
        controls = checks.negative_controls(word)
        local = L.replay(word)
        columns = L.reverse_columns(word)
        need(local['public_inputs'] == 767 and local['owned_fields'] == 9
             and local['owned_lifetimes'] == 11 and local['peak_owned_fields'] == 2,
             'Exact public and owned inventory')
        print('PASS all 776 scalar inputs, both transpose checks, 67 legal block subspaces',flush=True)
        native = L.native(word)
        C = load(root/'research/p104-productive-controller/caller.py','block_caller')
        caller = C.construct()
        need(caller == L.read(root/'research/p104-productive-controller/CONTROLLER.json'),'Exact physical caller')
        physical = C.physical(caller,word)
        print('PASS native maps, absolute phases and full physical caller',flush=True)
        P = load(HERE/'pricing.py','block_price')
        price = P.run(local,native,caller,physical)
        ranking = optimality(local,native,caller,physical,price,P,root)
        controls.update(C.controls(caller))
        bad = deepcopy(word); bad['initial'][741] = 477
        controls['old_helper_start'] = reject(lambda: checks.audit(bad))
        bad = deepcopy(word); next(e for e in bad['program'] if e == ['ADD',42,41,'1',1090])[-1] = 477
        controls['old_scalar_chart'] = reject(lambda: checks.audit(bad))
        bad = deepcopy(word); bad['frames'][1090].pop()
        controls['illegal_rank_three_frame'] = reject(lambda: checks.audit(bad))
        bad = deepcopy(local); bad['paid'][1] -= 1
        controls['unpaid_query'] = reject(lambda: P.assemble(bad,native,caller,physical))
        bad = deepcopy(local); bad['helpers'][9] += 1
        controls['extra_target'] = reject(lambda: P.assemble(bad,native,caller,physical))
        print('PASS full invoice, two moment engines, compiler, outer predicates and fixed-block optimum',flush=True)
        return P.encode({'status':'PASS_P104_SPLIT_BLOCK_KAPPA_00311313795',
            'local':local,'independent_literal_audit':independent,'independent_transpose':transpose,
            'separate_columns':columns,'native':native,'physical_caller':physical,
            'complete_cost':price,'fixed_block_ranks':ranking,'negative_controls':controls}), interval, hunks, word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='p104-split-block-cache-') as cache:
        sys.pycache_prefix = cache
        result, interval, hunks, word = run()
    values = {'RESULT.json':result,'INTERVAL.json':interval,'HUNKS.json':hunks,'WORD.json.gz':word}
    for name, value in values.items():
        value = json.loads(json.dumps(value))
        path = HERE/name
        if args.write:
            raw = (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
            path.write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)
        else:
            raw = path.read_bytes()
            need(json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw) == value,'Exact retained output: '+name)
    print(result['status'])


if __name__ == '__main__':
    main()
