#!/usr/bin/env python3
"""Verify two complete fixed-source BIT price gates without discovery."""
import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path
import struct
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BIT = 'research/kappa-rebuild/bit/sources/pr589-regenerated/'
CUBE = 'research/paired-cube-bit-fast/'
ENGINE = 'research/bit-compact-productive-controller/exact_series.py'
DEFECT = 'research/kappa-rebuild/bit/PR589-H-NATIVE.json.gz'
SOURCE_PATHS = {
    BIT+'WORD.json.gz', BIT+'records/frames.json', BIT+'records/249-records.bin',
    CUBE+'paired_cube_bit_word.py', CUBE+'SOURCE.json', CUBE+'data/arcs_p12.json',
    CUBE+'data/pair_module_p12.json', CUBE+'data/qmod_p12.json', ENGINE, DEFECT,
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def reject(name, operation):
    try:
        operation()
    except ValueError as error:
        return {'name':name, 'result':'REJECT', 'reason':str(error)}
    raise ValueError('A negative control passed: '+name)


def load(name, path, raw):
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec', dont_inherit=True, optimize=0), module.__dict__)
    return module


def check_pin(row, raw):
    need(sha256(raw).hexdigest()==row['sha256'], 'Source bytes differ: '+row['path'])


def source_bytes():
    pins = json.loads((PACKAGE/'SOURCES.json').read_text())
    live = [row for row in pins['files'] if row['usage']=='input']
    declared = json.loads((PACKAGE/'VERIFY.json').read_text())['inputs']
    need(len(live)==10 and {r['path'] for r in live}==set(declared)==SOURCE_PATHS,
         'Every live source must be pinned and declared')
    data = {}
    controls = []
    for row in live:
        name = row['path']
        raw = (ROOT/name).read_bytes()
        check_pin(row,raw)
        changed = bytes([raw[0]^1])+raw[1:]
        controls.append(reject('changed_source:'+name,lambda:check_pin(row,changed)))
        data[name] = raw
    return data, controls


def helper_census(word, frames, records):
    need((word['v'],word['R'],word['h'])==(111,439,8), 'The PR589 dimensions differ')
    need(frames['0']['dim']==0 and frames['1']['dim']==8, 'The helper endpoint rank differs')
    need(all(word['start'][i]==0 and word['final'][i]==1 for i in range(222,661)),
         'The helper endpoint frames differ')
    by_owner = {i:[] for i in range(222,661)}
    for index, event in enumerate(records):
        op,a,b,c,r,_ = event
        need(op in (0,1,2,3), 'Unknown source operation')
        if op==0 and a in by_owner:
            by_owner[a].append((index,r))
        if op in (2,3):
            need(b==661, 'An owned instruction changes a helper register')
    need(all(rows for rows in by_owner.values()), 'A helper has no paid MOVE')
    need(all(1<=r<=7 for rows in by_owner.values() for _,r in rows),
         'The helper paid-rank hypothesis fails')
    maxima = Counter(max(r for _,r in rows) for rows in by_owner.values())
    return {'helpers':439, 'target_rank':8, 'maximum_own_paid_rank':7,
            'owner_maximum_rank_counts':dict(sorted(maxima.items())),
            'own_paid_move_events':sum(len(rows) for rows in by_owner.values())}


def axis_gate(data):
    word = json.loads(gzip.decompress(data[BIT+'WORD.json.gz']))
    frames = json.loads(data[BIT+'records/frames.json'])['frames']
    records = list(struct.iter_unpack('<6i', data[BIT+'records/249-records.bin']))
    forward = helper_census(word,frames,records)
    reverse = helper_census(word,frames,list(reversed(records)))
    need(forward==reverse, 'Reversal changes the own-register rank census')
    bad_records = list(records)
    index = next(i for i,e in enumerate(records) if e[0]==0 and 222<=e[1]<661)
    event = list(bad_records[index]);event[4]=8;bad_records[index]=tuple(event)
    controls = [reject('rank_eight_helper_move',lambda:helper_census(word,frames,bad_records)),
                reject('helper_without_paid_path',lambda:helper_census(word,frames,[e for e in records if not(e[0]==0 and e[1]==222)]))]
    return {'status':'PASS_FIXED_WORD_HELPER_AXIS_EXCLUSION', 'forward':forward, 'reverse':reverse,
            'scope':'Any nonempty helper subset, positive integer number of new commuting axes, and real 0<C<1; original events and scalar contacts fixed; other target credits unchanged.',
            'proof':'For each helper, the changed-axis counts on its own paid MOVEs sum to at least k. Every old rank is at most 7. The increasing concave increment g(s)=(7+s)^(1-C)-7^(1-C) is subadditive, so the own-path increment is at least g(k)>(8+k)^(1-C)-8^(1-C). Distinct helper paths use distinct paid events.',
            'mincut_run':False, 'negative_controls':controls}


def profile(p,v,h,local,helpers):
    d = h-1
    paid = Counter({r:(p+2)*count for r,count in local.items()})
    paid[1] += (p-1)*v
    targets = Counter({h:(p+2)*helpers})
    targets[1+d*(p+2)] += 2*v
    left = (p-1)//2
    for arm in (left,p-1-left):
        for j in range(1,arm+1):
            targets[1+d*(j+1)] += 2*v
            paid[d*(j+1)] += 2*v
    return paid,targets


def mass(values):
    return sum(r*count for r,count in values.items())


def rounded(interval):
    lo,hi = interval
    scale = 10**12
    a,b = lo*scale,hi*scale
    lower = F(a.numerator//a.denominator,scale)
    upper = F(-(-b.numerator//b.denominator),scale)
    need(lower<=lo<=hi<=upper, 'The displayed rational enclosure fails')
    return [str(lower),str(upper)]


def cube_gate(data):
    module = load('retained_paired_cube',ROOT/(CUBE+'paired_cube_bit_word.py'),data[CUBE+'paired_cube_bit_word.py'])
    exact = load('retained_exact_series',ROOT/ENGINE,data[ENGINE])
    source_manifest = json.loads(data[CUBE+'SOURCE.json'])
    for name,digest in source_manifest['data'].items():
        need(sha256(data[CUBE+'data/'+name]).hexdigest()==digest, 'The retained cube data pin differs')
    plan = json.loads(data[CUBE+'data/pair_module_p12.json'])
    graph = module.BitGraph(12).finish(plan,module.pinned_all_but_one('qmod_p12.json',10),merge=True,l1=True)
    need(module.check_decoder(graph)==0, 'The retained scalar decoder fails')
    local,witness = module.compile_word(graph,frozen=json.loads(data[CUBE+'data/arcs_p12.json']))
    h,v,helpers = local['h'],local['v'],local['R']
    need((h,v,helpers,local['loss'])==(24,1760,19788,528), 'The retained cube dimensions differ')
    source = Counter({1:v,h-4:v//2,2:v//2,h-2:v//2})
    paid = Counter(witness['H'])+source+Counter(witness['targetH'])
    paid.pop(0,None)
    targets = {h:helpers}
    def invoice_check(paid_,targets_):
        need(mass(source)==mass(witness['targetH'])==v*(h-1), 'A main boundary is unpaid')
        need(mass(paid_)-mass(targets_)==2*v*(h-1)+528, 'The full local invoice loses a charge or debit')
        need(max(paid_)<h, 'The normalized-moment monotonicity hypothesis fails')
    invoice_check(paid,targets)
    def power(r,c):
        lo,hi = exact.logbound(r)
        return F(r)/exact.expbound(c*hi)[1],F(r)/exact.expbound(c*lo)[0]
    def moment(values,c):
        rows = [(count,power(r,c)) for r,count in values.items()]
        return sum(n*a for n,(a,b) in rows),sum(n*b for n,(a,b) in rows)
    def margin(a,b,c):
        x,y = moment(a,c),moment(b,c)
        return y[0]-x[1],y[1]-x[0]
    c = F(1,500)
    rows = []
    for p in range(1,65):
        cp,ct = profile(p,v,h,paid,helpers)
        need(mass(ct)-mass(cp)==1232*p+704, 'The complete controller mass law differs')
        interval = margin(cp,ct,c)
        need(interval[1]<0, 'The finite controller gate is not negative')
        rows.append({'controller_parameter':p,'margin_at_1_over_500':rounded(interval)})
    cost,credit = moment(paid,c),moment(targets,c)
    gap = cost[0]-credit[1]
    p0,d,t = 64,h-1,1-c
    rank_ = 1+(p0+2)*d
    endpoint = power(rank_,c)[1]
    def tail(gap_):
        value = -(p0+2)*gap_+v*(p0-1)+2*v*endpoint
        slope = -gap_+v+2*v*d*t*endpoint/rank_
        need(value<0 and slope<0, 'The analytic parameter tail is not closed')
        return value,slope
    tail_value,tail_slope = tail(gap)
    p11,t11 = profile(11,v,h,paid,helpers)
    bracket = [margin(p11,t11,F(x)) for x in ('0.00164539220','0.00164539221')]
    need(bracket[0][0]>0>bracket[1][1], 'The retained positive crossing control fails')
    bad_paid = paid.copy();bad_paid[1]-=1
    controls = [reject('missing_paid_rank_one',lambda:invoice_check(bad_paid,targets)),
                reject('unearned_helper_credit',lambda:invoice_check(paid,{h:helpers+1})),
                reject('missing_local_gap_in_tail',lambda:tail(F(0)))]
    return {'status':'PASS_PAIRED_TRIPLE_P12_ALL_PARAMETER_PRICE_GATE',
            'geometry_parameter':12,'h':h,'ports':v,'helpers':helpers,'centre_debt':528,
            'local_paid':dict(sorted(paid.items())),'local_helper_targets':targets,
            'source_main':dict(source),'target_main':dict(witness['targetH']),
            'finite_prefix':rows,'all_positive_integer_controller_parameters_raw_saving_below':'1/500',
            'tail':{'first_parameter':64,'upper_margin':rounded((tail_value,tail_value))[1],
                    'upper_derivative':rounded((tail_slope,tail_slope))[1]},
            'normalized_margin_decreases_with_C':{'local_paid_ranks_below_h':max(paid)<h,
                    'first_side_paid_rank':2*d,'normalizing_target_rank':h},
            'positive_crossing_control':{'controller_parameter':11,'root_bracket':['0.00164539220','0.00164539221'],
                    'margin_enclosures':[rounded(x) for x in bracket],'global_optimum_claimed':False},
            'negative_controls':controls,'matching_search_run':False,'root_search_run':False}


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length()-1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def combine(mask, rows):
    result = 0
    for index,row in enumerate(rows):
        if mask>>index & 1:
            result ^= row
    return result


def permutation_certificate(geometry):
    j = geometry['J_rows']
    u,v = geometry['U_rows'],geometry['V_rows']
    need(len(j)==len(u)==111 and len(v)==9, 'The defect source shape differs')
    defect = [row^(1<<i) for i,row in enumerate(j)]
    need([combine(row,v) for row in u]==defect, 'The defect factorization differs')
    need(binary_rank(defect)==9, 'The identity correction rank is not nine')
    columns = [sum(((row>>bit)&1)<<i for i,row in enumerate(u)) for bit in range(9)]
    weights = Counter(combine(mask,columns).bit_count() for mask in range(1,512))
    need(sum(weights.values())==511 and min(weights)==48, 'The defect code distance differs')
    moved_bound = 2*(9+8)
    need(min(weights)>moved_bound, 'The deleted-row argument has no distance gap')
    return {'defect_rank':9,'nonzero_codewords':511,'minimum_code_weight':48,
            'weight_counts':dict(sorted(weights.items())),
            'hypothetical_rank_bound':8,'permutation_difference_rank_bound':17,
            'moved_rows_bound':moved_bound,'minimum_rank_J_plus_permutation':9,
            'attaining_permutation':'identity','native_factorization_cost_bound':False}


def permutation_gate(data):
    geometry=json.loads(gzip.decompress(data[DEFECT]))['geometry']
    result=permutation_certificate(geometry)
    bad=dict(geometry);bad['J_rows']=list(geometry['J_rows']);bad['J_rows'][0]^=1
    zero=dict(geometry);zero['J_rows']=[1<<i for i in range(111)];zero['U_rows']=[0]*111;zero['V_rows']=[0]*9
    result['negative_controls']=[reject('changed_decoder_row',lambda:permutation_certificate(bad)),
                                 reject('zero_defect_rank',lambda:permutation_certificate(zero))]
    return result


def run():
    data,controls = source_bytes()
    result = {'schema_version':1,'status':'PASS_BIT_FIXED_SOURCE_PRICE_GATES',
              'source_sha256':{name:sha256(raw).hexdigest() for name,raw in sorted(data.items())},
              'source_mutation_controls':controls,'helper_axis':axis_gate(data),
              'paired_triple':cube_gate(data),'permutation_only_appendix':permutation_gate(data),'new_supplier':False,'new_kappa':False}
    return json.loads(json.dumps(result))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=run()
    expected=PACKAGE/'RESULT.json'
    if expected.exists() and json.loads(expected.read_text())!=result:
        raise ValueError('The exact retained result differs')
    if args.output:args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS_BIT_FIXED_SOURCE_PRICE_GATES helper_axis=all_k_C paired_k3=all_controller_p source_controls=10 new_kappa=false')


if __name__=='__main__':
    main()
