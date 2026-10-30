"""Full replay of the shared587 residual relay and conditional P104 saving.

Prepared for flyingviper with substantial OpenAI Codex assistance and
independent agents. Native/caller/pricing framework credited to Ali Romman,
zxv, Cao Yifan, Jacob Alan Sussman, Cinna Davis and retained predecessors.
Apache-2.0. This is not a proof-kernel verification.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import closure, load, need, read
from construct import construct


def inventory(base, word):
    need(set(base) == set(word), 'Same word fields')
    for key in base:
        if key != 'program':
            need(base[key] == word[key], 'Unchanged word field: '+key)
    def bill(w):
        return Counter(abs(len(w['frames'][e[2]])-len(w['frames'][e[3]]))
                       for e in w['program'] if e[0] == 'MOVE')
    before, after = bill(base), bill(word)
    delta = {r: after[r]-before[r] for r in before.keys() | after.keys() if after[r] != before[r]}
    need(delta == {1: -1, 2: -1, 3: -1, 6: 1}, 'Exact shared-relay paid profile')
    need(sum(r*n for r,n in delta.items()) == 0, 'Unchanged rank mass')
    counts0, counts1 = Counter(e[0] for e in base['program']), Counter(e[0] for e in word['program'])
    changed = {k: counts1[k]-counts0[k] for k in counts0.keys() | counts1.keys() if counts1[k] != counts0[k]}
    need(changed == {'ADD': 29, 'MOVE': -2}, 'Exact ordinary and paid operation delta')
    return {'source_events': len(base['program']), 'events': len(word['program']),
            'operation_delta': changed, 'local_paid_delta': delta,
            'global_paid_delta': {r: 18*n for r,n in delta.items()},
            'public_endpoints_fixed': True, 'productive_targets_fixed': True,
            'owned_lifetimes_fixed': True, 'extra_owned_fields': 0}


def controls(L, base, word):
    variants = {}
    bad = deepcopy(word);bad['program'].pop(0)
    variants['missing_zero_frame_correction'] = bad
    bad = deepcopy(word)
    bad['program'].remove(['ADD',21,133,'-1',127])
    variants['missing_full_frame_correction'] = bad
    bad = deepcopy(word)
    event = next(e for e in bad['program'] if e == ['ADD',21,587,'1',652]);event[3] = '2'
    variants['wrong_relay_coefficient'] = bad
    bad = deepcopy(word);bad['program'].remove(['MOVE',587,597,652,False])
    variants['missing_relay_transport'] = bad
    rejected = {}
    for name,bad in variants.items():
        try:
            L.replay(bad)
        except ValueError as error:
            rejected[name] = str(error)
        else:
            raise ValueError('Accepted invalid word: '+name)
    try:
        inventory(base, base)
    except ValueError as error:
        rejected['unchanged_word'] = str(error)
    else:
        raise ValueError('Accepted unchanged word as a saving')
    return rejected


def ceiling(E, targets, paid):
    cap = Q('0.0034');lower = upper = Q(0)
    for rank in targets.keys() | paid.keys():
        coefficient = paid.get(rank,0)-targets.get(rank,0)
        power = (E.power(rank,1-cap)[0], Q(rank))
        term = E.scale(E.mul(power,E.log_bounds(rank)),coefficient)
        lower += term[0];upper += term[1]
    need(upper < 0, 'Strictly decreasing complete moment on retained BIT band')
    return {'kappa_interval':[Q(0),cap], 'moment_derivative':[lower,upper],
            'scope':'This fixed invoice with the inherited BIT cap, not a family optimum.'}


def main():
    sources = read(HERE/'SOURCES.json')
    for pin in sources['external_inputs']:
        raw = (HERE/pin['local_path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'Source bytes: '+pin['local_path'])
        need(sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest() == pin['git_blob'],
             'Source Git blob: '+pin['local_path'])
    base, word = read(HERE/'inputs/pr5580-WORD.json.gz'), read(HERE/'WORD.json.gz')
    need(construct(base) == word, 'Exact regenerated complete word payload')
    inv = inventory(base,word)
    source_price = (HERE/'inputs/pr5580-pricing.py').read_text()
    for before,after in (
        ("KAPPA, TESTED = Q('.00308189'), Q('.0030818905')", "KAPPA, TESTED = Q('.00308326'), Q('.0030832605')"),
        ("PREVIOUS = Q('.00308181')", "PREVIOUS = Q('.00308189')"),
        ("'kappa_decimal':'.00308189'", "'kappa_decimal':'.00308326'"),
        ("'previous_open_pr5569':PREVIOUS", "'previous_open_pr5580':PREVIOUS"),
        ("sum(paid.values()) == 66852", "sum(paid.values()) == 66816")):
        need(source_price.count(before) == 1, 'Unique pricing declaration: '+before)
        source_price = source_price.replace(before,after)
    need(source_price == (HERE/'pricing.py').read_text(), 'Pricing only changes declared claims and exact call census')
    print('PASS source pins, construction and H6-H1-H2-H3 invoice',flush=True)
    with closure() as root:
        L=load(root/'research/p104-productive-controller/local.py','local');L.ROOT=root
        parent_local,local=L.replay(base),L.replay(word)
        need(parent_local['helpers'] == local['helpers'], 'Unchanged productive helper census')
        need(local['peak_owned_fields'] == parent_local['peak_owned_fields'] == 1, 'No extra owned storage')
        rejected=controls(L,base,word)
        print('PASS all743 arbitrary-input rows, frames, ownership and controls',flush=True)
        reverse=L.reverse_columns(word)
        print('PASS dense exact transpose',flush=True)
        native=L.native(word)
        print('PASS all exact signed native maps',native['distinct_maps'],flush=True)
        C=load(root/'research/p104-productive-controller/caller.py','shared_relay_caller')
        caller=C.construct()
        need(caller == read(root/'research/p104-productive-controller/CONTROLLER.json'), 'Exact physical caller')
        physical=C.physical(caller,word)
        print('PASS complete physical caller',flush=True)
        P=load(HERE/'pricing.py','shared_relay_pricing')
        result=P.run(local,native,caller,physical)
        print('PASS two interval engines, complete pricing, compiler and58 outer predicates',result['raw_root_interval'],flush=True)
        E=L.load(root/'research/higher-moment-strictification/verify.py','shared_relay_margin')
        targets={int(r):n for r,n in result['targets'].items()};paid={int(r):n for r,n in result['paid'].items()}
        parent_paid=dict(paid)
        for r,n in inv['global_paid_delta'].items():parent_paid[r]-=n
        parent_interval=[Q('0.00308189496866'),Q('0.00308189496867')]
        margins=[]
        for k in parent_interval:
            t,p=E.moment(targets,1-k),E.moment(parent_paid,1-k)
            margins.append((t[0]-p[1],t[1]-p[0]))
        need(margins[0][0] > 0 > margins[1][1], 'Exact predecessor raw crossing')
        lo,hi=map(Q,result['raw_root_interval'])
        gain=[lo-parent_interval[1],hi-parent_interval[0]]
        need(gain[0] > 0, 'Strict raw gain over complete predecessor')
        fixed_ceiling=ceiling(E,targets,paid)
    receipt=P.encode({'status':'PASS_P104_SHARED_RESIDUAL_KAPPA_00308326','inventory':inv,
                      'local':local,'transpose':reverse,'native':native,'physical':physical,
                      'controls':rejected,'parent_raw_interval':parent_interval,'raw_gain_interval':gain,
                      'fixed_invoice_ceiling':fixed_ceiling,'result':result})
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    else:
        need(receipt == read(HERE/'RESULT.json'),'Exact committed complete receipt')
    print(receipt['status'],flush=True)


if __name__ == '__main__':
    main()
