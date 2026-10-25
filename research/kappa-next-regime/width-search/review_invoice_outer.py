#!/usr/bin/env python3
"""Independent source binding, complete finite invoice and outer balance review.

This checker does not import complete_invoice.py, either outer ledger, the
word constructor, the native emitter, or their moment engines. It rederives
both literal IR programs from the audited word and uses rational series with
explicit tails for prices. Physical/all-size hypotheses remain conditional.
Apache-2.0; substantial OpenAI assistance.
"""
from __future__ import annotations

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import ast
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
REPO = TASK.parents[1]
BASE = TASK/'sources/PR3647/research/bit-p111-r437-gl464-470-20261018'
OUTER = TASK/'outer/package'
WORD_HASH = '3f7de7e1d8a6ff9da8ab7650209b559062da4cc053de2b2566b306eb4fbeffd0'


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def plain_hash(value):
    return sha256(json.dumps(value,separators=(',',':')).encode()).hexdigest()


def pins(receipt):
    for name,digest in receipt['source_sha256'].items():
        need(sha256((REPO/name).read_bytes()).hexdigest() == digest, 'source SHA256 '+name)


def record_programs(word):
    # Frame dimensions are independently certified over Q in the local review;
    # the ranks here are rederived by rational row elimination, not frame IDs.
    def rank(frame):
        rows = [[Q(x) for x in word['lines'][j]] for j in frame]
        pivot_row = 0
        for column in range(8):
            chosen = next((i for i in range(pivot_row,len(rows)) if rows[i][column]),None)
            if chosen is None:
                continue
            rows[pivot_row],rows[chosen] = rows[chosen],rows[pivot_row]
            divisor = rows[pivot_row][column]
            rows[pivot_row] = [x/divisor for x in rows[pivot_row]]
            for i in range(pivot_row+1,len(rows)):
                coefficient = rows[i][column]
                rows[i] = [x-coefficient*y for x,y in zip(rows[i],rows[pivot_row])]
            pivot_row += 1
        return pivot_row
    dimensions = [rank(frame) for frame in word['frames']]
    current = word['start'][:]
    records = []
    def move(role, frame):
        old = current[role]
        if old != frame:
            need(set(word['frames'][old]) <= set(word['frames'][frame]), 'record move is exact nested frame')
            records.append((0,role,old,frame,dimensions[frame]-dimensions[old],0))
            current[role] = frame
    for phase,section in [(1,'D'),(2,'A'),(4,'B'),(5,'C')]:
        if section == 'B':
            for j,role in enumerate(word['ret']):
                frame = current[role]
                records.append((2,role,659,frame,0,dimensions[frame]))
                records.extend((1,111+t,659,1,0,3) for t,terms in enumerate(word['scatter']) if j in terms)
                records.append((3,role,659,frame,0,0))
        for frame,destination,sources in word[section]:
            for role in [destination]+sources:
                move(role,frame)
            records.extend((1,destination,source,1,frame,phase) for source in sources)
    for role,frame in enumerate(word['final']):
        move(role,frame)
    programs,details = {},{}
    for orientation,reverse in [('forward',False),('reverse',True)]:
        events,profile = [],Counter()
        values = [1 << i for i in range(659)]+[0]
        bounds = [1]*659+[0]
        opened,maximum,copies,adds = None,1,0,0
        for op,d,s,c,f,z in records[::-1] if reverse else records:
            if op == 0:
                old,new = (c,s) if reverse else (s,c)
                events.append([0,d,old,new,f,int(reverse)])
                profile[f] += bool(f)
                need(opened is None, 'no frame move during COPY window')
            elif op == 1:
                need(d != opened and (s != 659 or opened is not None), 'COPY source immutable and WORK read only when open')
                events.append([1,d,s,-c if reverse else c,f,int(reverse)])
                values[d] ^= values[s]
                bounds[d] += abs(c)*bounds[s]
                maximum = max(maximum,bounds[d]); adds += 1
            elif op == (3 if reverse else 2):
                need(opened is None and values[659] == bounds[659] == 0, 'clean private entry')
                opened = d
                values[659],bounds[659] = values[d],bounds[d]
                r = abs(dimensions[c]-dimensions[f])
                events.append([2,d,659,c,f,r,int(reverse)])
                profile[r] += 1; copies += 1
            else:
                need(opened == d and values[659] == values[d], 'literal same-source private erase')
                events.append([3,d,659,c,f,z,int(reverse)])
                values[659],bounds[659],opened = 0,0,None
        need(values == [(1 << r)^((1 << (r-111)) if 111 <= r < 222 else 0) for r in range(659)]+[0],
             'independent raw native IR complete dirty interface in both orientations')
        need(copies == 9 and opened is None, 'nine clean native COPY episodes')
        programs[orientation] = events
        details[orientation] = {'adds':adds,'copies':copies,'prefix_l1':maximum,
                                'profile':dict(sorted(profile.items())),'events':len(events)}
    return programs,details


def round_interval(low, high, places=70):
    scale = 10**places
    return Q((low*scale).__floor__(),scale),Q(-((-high*scale).__floor__()),scale)


@lru_cache(None)
def log_interval(value):
    scale = 0
    while value >= 2:
        value /= 2; scale += 1
    def series(z):
        total,term = Q(0),z
        for k in range(48):
            total += 2*term/(2*k+1)
            term *= z*z
        return total,total+2*term/(97*(1-z*z))
    low,high = series((value-1)/(value+1))
    l2,h2 = series(Q(1,3))
    return round_interval(low+scale*l2,high+scale*h2)


def exp_interval(low,high):
    def series(value):
        need(0 <= value < Q(1,50), 'exponential series domain')
        total = term = Q(1)
        for k in range(1,25):
            term = term*value/k; total += term
        return total,total+(term*value/25)/(1-value/26)
    return round_interval(series(low)[0],series(high)[1])


def moment(profile,m,W,endpoint,bad_fallback=0):
    counts = {r:Q(n) for r,n in profile.items()}
    if bad_fallback:
        counts[1] = counts.get(1,Q(0))+Q(bad_fallback,10**16)
    lower = upper = Q(0)
    for rank,count in counts.items():
        low,high = log_interval(Q(m,rank))
        low,high = exp_interval(endpoint*low,endpoint*high)
        weight = Q(count*rank,m*W)
        lower += weight*low; upper += weight*high
    return round_interval(lower,upper)


def function_node(path,name):
    node = next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name == name)
    return ast.dump(node,include_attributes=False)


def outer_review(invoice,invoice_path):
    spec,claim,bj = (read(OUTER/'new/SPEC.json'),read(OUTER/'CLAIM.json'),read(OUTER/'outer/B.json'))
    pins(spec)
    need(spec['source_sha256'][invoice_path.relative_to(REPO).as_posix()] == sha256(invoice_path.read_bytes()).hexdigest(),
         'outer inputs bind exact reviewed final invoice')
    cx_path = TASK/'sources/PR3959/research/rank7-idle-frame-select/CLAIM.json'
    cx = read(cx_path)
    bit = Q(invoice['bit_lower']); complex_lower = Q(cx['complex_root'][0])
    need(Q(spec['expected']['bit_lower']) == bit and Q(spec['expected']['complex_lower']) == complex_lower,
         'both independent supplier endpoints bound into outer SPEC')
    endpoint = min(bit,complex_lower)
    need(bit < complex_lower and claim['binding'] == 'bit', 'BIT genuinely binds')
    D = spec['outer_refinement']['endpoint_digits']
    need(D == 24, 'fixed decimal grid dimension')
    R = Q(1,10**(D+80)); b = endpoint-R; q = b-R; a = (q+b)/2
    delta = Q(1025,1024)*R; eps = 1-delta; beta = 1-3*delta
    floor = 10**(D+46); backoff = Q(1,10**(D+22))
    kappa = Q((eps*q*floor).__floor__(),floor)-backoff
    need(kappa == endpoint-Q(1,floor)-backoff == Q(claim['kappa']), 'independently derived exact grid maximum and outer loss')
    need(Q(bj['b']) == b and Q(claim['endpoint_lower']) == endpoint, 'common strict interior endpoint is exact minimum')
    target = Q('0.001736738651088946052684')
    need(kappa > target and Q(claim['strict_gain_over_target']) == kappa-target, 'strict gain exceeds displayed3959 endpoint')
    need(0 < q < a < b < bit < complex_lower and (1-R/10**6)*b > a, 'both stopped supplier interfaces have strict gaps')
    c = Q(3,32); xi = eps*(1+q)+R-c
    costs = {'transform':1-eps*q,'global_router':1-a,'gaussian':eps-q*beta,
             'group_router':eps-a*beta,'group_scans':eps-beta,'boundary':eps-xi+Q(29,32),
             'sparse_union':eps+Q(1,2)-xi,'polynomials':1-eps,'microfaces':eps+beta+48-128+2}
    need(max(costs.values()) == costs['transform'] and all(value < 1-kappa for value in costs.values()),
         'independent nine outer cost powers strictly below target')
    need(7**16 < 2**45 and Q(1,2) < xi < eps < 1 and 0 < beta < eps,
         'integer Strassen and cap domains')
    need(1-eps-R > 0 and 1-(2*xi-2)-R-beta > R/100 > 0,
         'strict global gamma and group gauge slacks')
    need(1-beta-2*(1-eps) == delta > 0 and 1-eps+q*beta-eps*q == delta*(1-2*q) > 0,
         'membership and Gaussian margins')
    need(spec['finite_bit_coefficient_envelope'] == invoice['coefficient_envelopes'][invoice['chosen_envelope']],
         'outer preserves the fully paid coefficient envelope')
    binding = read(TASK/'outer/BINDING.json')
    for filename,entry in binding.items():
        original = REPO/entry['original']; bound = OUTER/'outer'/filename
        need(sha256(original.read_bytes()).hexdigest() == entry['original_sha256'], 'outer predecessor script SHA')
        text = original.read_text()
        for change in entry['source_replacements']:
            need(text.count(change['from']) == 1, 'unique source-bound outer replacement')
            text = text.replace(change['from'],change['to'])
        if entry['added_assertions_enabled_guard']:
            text = "if not __debug__: raise RuntimeError('Assertions must be enabled')\n"+text
        need(text == bound.read_text() and sha256(bound.read_bytes()).hexdigest() == entry['bound_sha256'],
             'generated outer script differs only by declared endpoint/scope bindings')
    predecessor = REPO/binding['check_ledger.py']['original']
    need(function_node(predecessor,'ledger') == function_node(OUTER/'outer/check_ledger.py','ledger'),
         'all63 outer exponent rows and definitions unchanged at AST level')
    ledger = read(OUTER/'outer/LEDGER.json')
    row = ledger['rows']['struct_boundary_radix_union']
    need(len(row['strict_checks']) == 63 and all(Q(x['rational']) > 0 for x in row['strict_checks'].values()),
         'all63 exact outer receipt inequalities strictly positive')
    controls = ledger['rejecting_controls']['struct_boundary_radix_union']
    need(len(controls) == 17 and all(failures and all(Q(v['rational']) <= 0 for v in failures.values()) for failures in controls.values()),
         'all17 inherited rejecting variants remain rejected')
    need(Q(row['kappa']['rational']) == kappa, 'main outer receipt final kappa binding')
    independent = read(OUTER/'outer/INDEPENDENT.json')
    need(Q(independent['rows']['struct_boundary_radix_union']['kappa']) == kappa, 'independent outer receipt final kappa binding')
    cx_profile = {int(r):n for r,n in cx['profile'].items()}
    low,high = moment(cx_profile,73,896*cx['T'],b)
    need(high < 1, 'independent complex price accepts minimum supplier endpoint')
    upper = Q(cx['complex_root'][1]); reject = moment(cx_profile,73,896*cx['T'],upper)
    need(reject[0] > 1, 'independent complex price rejects certified upper endpoint')
    return {'binding_endpoint':str(endpoint),'bit_lower':str(bit),'complex_lower':str(complex_lower),
            'kappa':str(kappa),'gain_over_3959_displayed_endpoint':str(kappa-target),
            'outer_loss':str(endpoint-kappa),'strict_rows':63,'rejecting_controls':17,
            'complex_moment_at_common_interior':[str(low),str(high)],
            'complex_upper_rejection':[str(x) for x in reject],
            'ledger_AST_unchanged':True,'independent_cost_powers':{k:str(v) for k,v in costs.items()}}


def main():
    sys.set_int_max_str_digits(0)
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--invoice',type=Path,default=TASK/'COMPLETE-INVOICE.json')
    ap.add_argument('--out',type=Path,default=HERE/'FINAL-INVOICE-OUTER-REVIEW.json')
    args = ap.parse_args()
    invoice_path = args.invoice.resolve(); invoice = read(invoice_path)
    pins(invoice)
    paths = {Path(name).name:REPO/name for name in invoice['source_sha256']}
    word_path = next(path for path in paths.values() if path.name == 'WORD.json.gz')
    word = read(word_path)
    need(sha256(canonical(word)).hexdigest() == WORD_HASH, 'final invoice uses independently audited covector word')
    template_path = paths['GLOBAL-TEMPLATE.json.gz']; template = read(template_path)
    pool = template_path.parent
    pool_result = read(pool/'RESULT.json')
    need(sha256(canonical(template)).hexdigest() == pool_result['template_content_sha256'], 'exact pooled template content SHA')
    programs,details = record_programs(word)
    need(template['local_programs'] == programs, 'both complete native IR programs independently rederived from exact final word')
    for orientation,computed in details.items():
        claimed = dict(invoice['local'][orientation])
        claimed['profile'] = {int(r):n for r,n in claimed['profile'].items()}
        need(computed == claimed, 'all local scalar counts, paid profiles and coefficient bounds recomputed')
    need((template['replicas'],template['live'],template['private_centre_reserve']) == (35,31080,9), 'complete finite physical dimensions')
    call_counts = [Counter() for _ in range(7)]; seen = set()
    profile = Counter()
    for call in template['calls']:
        stage,replica,orientation = call['stage'],call['replica'],call['orientation']
        need((stage,replica) not in seen and 0 <= stage < 9 and 0 <= replica < 35, 'all literal stage/replica calls unique')
        seen.add((stage,replica)); call_counts[replica//5][orientation] += 1
        need(call['local_hash'] == plain_hash(programs[orientation]), 'each call binds correct exact local orientation')
        need(len(call['owners']) == 659 and all(0 <= family < 31080 and family//4440 == replica//5 for family,route in call['owners']),
             'all regular call owners remain within exact five-replica payload block')
        profile.update(details[orientation]['profile'])
    need(len(seen) == 315 and all(c == {'forward':25,'reverse':20} for c in call_counts), 'seven blocks each contain all45 calls')
    old_template = read(BASE/'generated/GLOBAL-TEMPLATE.json.gz')
    need(template['schedule'] == old_template['schedule'], 'unchanged literal predecessor bridge/controller sequence')
    bridges = [e for e in template['schedule'] if e['kind'] == 'bridge']
    need(len(bridges) == 9 and all(e['dst'] != e['src'] and e['coefficient'] in (-1,1) for e in bridges), '18 norm-two bridge shear layers per replica')
    idles = read(paths['IDLE-INVENTORY.json.gz'])
    need(all(0 <= family < 31080 and family//4440 == replica//5 and rank > 0 for child,replica,cp,family,used,rank in idles),
         'all absolute idle children are positive and block local')
    profile.update(row[-1] for row in idles)
    profile = dict(sorted(profile.items()))
    need(profile == {int(r):n for r,n in invoice['profile'].items()}, 'complete actual315call plus every absolute idle child price')
    T,W,m,R,V,L,N = 35,31080,64,437,111,9,128
    E = sum(profile.values()); need(E == invoice['paid_requests'] == 988155, 'all paid requests')
    need(m*W-sum(r*n for r,n in profile.items()) == 11235, 'unchanged productive rank deficit')
    pf,pb = details['forward']['prefix_l1'],details['reverse']['prefix_l1']
    single = 2**18*pf**5*pb**4; block = single**5
    need(invoice['chosen_envelope'] == 'five_replica_block_upper_bound', 'uses complete five-replica product envelope')
    episodes = 9*L*T
    J = 8*T*L*(2*V+R)+8*(8*V*T)+2*L*T*R+2*episodes
    geometry = read(BASE/'data/GEOMETRY.json')
    common = {'unit':L*T*details['forward']['adds']+18*V*T,
              'J_times_high':J*16*(m*m+1)**2,'J_times_physical':J*(W+9),
              'E_times_good':E*(8*m*m+8),'E_times_compiler':E*128*N**3,
              'matrix_test':16*m**3,'copy_erase_episodes':episodes,
              'selectors':2*L*T*((W-1)+R*m*(geometry['max_route_factors']+144+2+(m-1)+m)), 'one':1}
    need({k:str(v) for k,v in common.items()} == invoice['components_without_prefix'] and J == invoice['J'],
         'all ordinary operations, selector, compiler, private and matrix invoice terms')
    for name,prefix in [('retained_replica_formula',single),('five_replica_block_upper_bound',block),('complete_sequential_upper_bound',single**35)]:
        actual = invoice['coefficient_envelopes'][name]
        coefficient = sum(common.values())+prefix
        two = (coefficient+1)**2*(E+1)**2
        need((int(actual['prefix']),int(actual['coefficient']),int(actual['two_level_coefficient'])) == (prefix,coefficient,two),
             'all coefficient envelopes exactly recomputed')
        need(prefix < 2**actual['charged_prefix_bits'] and two < 2**actual['charged_two_level_bits'], 'charged coefficient upper bounds')
    chosen = invoice['coefficient_envelopes'][invoice['chosen_envelope']]
    need(chosen['charged_prefix_bits'] == 896 and chosen['charged_two_level_bits'] == 1856 < 210000, 'chosen five-block envelope fully charged within inherited umbrella')
    need(invoice['ROW'] == 2*(m*m+1)+9909+252 == 18355 < invoice['ROW_cap'] == 20161, 'retained ROW cap remains strict')
    need(invoice['halving'] == [2*max(profile)**2,m*m] and 2*max(profile)**2 < m*m, 'strict two-level halving')
    fallback = 32*m*m*E
    need(invoice['fallback_total'] == fallback and invoice['fallback_exact_bound'] == 6*N*(N-1)+3*N+6*(N-1) == 98682 < 32*m*m,
         'every bad-class child retains the complete fallback surcharge')
    lower,upper = Q(invoice['bit_lower']),Q(invoice['bit_upper'])
    need(upper-lower == Q(1,10**24), 'adjacent exact bit bracket endpoints')
    sign_checks = []
    for label,endpoint in [('lower',lower),('upper',upper)]:
        lo,hi = moment(profile,m,W,endpoint,fallback)
        need(hi < 1 if label == 'lower' else lo > 1, 'independent rational complete bit moment sign')
        sign_checks.append({'endpoint':str(endpoint),'lower':str(lo),'upper':str(hi)})
    outer = outer_review(invoice,invoice_path)
    bound_paths = [Path(__file__),invoice_path,TASK/'complete_invoice.py',TASK/'outer/prepare.py',
                   TASK/'outer/BINDING.json',OUTER/'new/SPEC.json',OUTER/'CLAIM.json',OUTER/'outer/B.json',
                   OUTER/'outer/check_ledger.py',OUTER/'outer/independent_check.py',OUTER/'outer/LEDGER.json',
                   OUTER/'outer/INDEPENDENT.json',word_path,template_path,paths['IDLE-INVENTORY.json.gz'],
                   HERE/'COMPOSED-WORD-INDEPENDENT-NATIVE-REVIEW.json']
    result = {'status':'PASS_INDEPENDENT_FINAL_LITERAL_IR_COMPLETE_INVOICE_MINIMUM_SUPPLIER_OUTER',
              'source_sha256':{p.relative_to(REPO).as_posix():sha256(p.read_bytes()).hexdigest() for p in bound_paths},
              'independent_method':'Standard-library literal word-to-IR reconstruction; exact rational log/exp series with explicit tails; independent coefficient and outer-balance arithmetic; unchanged ledger AST/source bindings.',
              'profile':profile,'paid_requests':E,'rank_mass':sum(r*n for r,n in profile.items()),
              'local_details':details,'payload_blocks':7,'replicas_per_block':5,
              'chosen_prefix_bits':block.bit_length(),'chosen_charged_prefix_bits':896,'chosen_charged_two_level_bits':1856,
              'ROW':18355,'independent_bit_moments':sign_checks,'outer':outer,
              'reviewed_boundaries':['Native payload/route/recursive-D/cover lifting are retained conditional interfaces.',
                  'Five-replica owner geometry requires the separate full owner and idle audit.',
                  'The complex finite move-catalogue audit does not prove universal GL64 or all-size physical realization.',
                  'No maintainer admission, independent human review, or unconditional kappa is asserted.']}
    with args.out.open('x') as handle:
        json.dump(result,handle,indent=2,sort_keys=True); handle.write('\n')
    print(result['status'], 'bit',str(lower),'outer gain',outer['gain_over_3959_displayed_endpoint'])


if __name__ == '__main__':
    main()
