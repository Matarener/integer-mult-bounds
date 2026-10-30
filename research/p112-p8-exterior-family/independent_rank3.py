"""Independent exact arrangement audit; no producer imports or sampling claims.

This replay intersects
all sets of at most three planes: any consistent system in three variables has
such a basis. No producer code, scratch data or generated input is used.  Generic points are certified by all 84 literal determinants.
"""
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
from math import gcd
from pathlib import Path
from collections import Counter
import argparse
import json
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = [(1,0,0),(0,1,0),(0,0,1),(0,0,0),(0,1,1),
        (1,0,1),(1,1,0),(2,1,1),(1,0,0)]
WEIGHT = [0,0,0,1,2,1,1,0,1]


def need(test, message):
    if not test:
        raise ValueError(message)


def det(a,b,c):
    return (a[0]*(b[1]*c[2]-b[2]*c[1])
            -a[1]*(b[0]*c[2]-b[2]*c[0])
            +a[2]*(b[0]*c[1]-b[1]*c[0]))


def minor_form(ids):
    cols = [BASE[i] for i in ids]
    # Terms with two updated columns vanish since both are multiples of h.
    linear = []
    for axis in range(3):
        e = tuple(int(i == axis) for i in range(3))
        coefficient = 0
        for j, index in enumerate(ids):
            changed = list(cols)
            changed[j] = e
            coefficient += WEIGHT[index]*det(*changed)
        linear.append(coefficient)
    return (det(*cols), *linear)


def primitive(values):
    divisor = 0
    for value in values:
        divisor = gcd(divisor, abs(value))
    need(divisor > 0, 'nonzero plane form')
    divisor *= 1 if next(x for x in values if x) > 0 else -1
    return tuple(x//divisor for x in values)


def rref(equations):
    a = [list(map(F,row)) for row in equations]
    n = 0
    for col in range(3):
        pivot = next((i for i in range(n,len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[n],a[pivot] = a[pivot],a[n]
        value = a[n][col]
        a[n] = [v/value for v in a[n]]
        for i in range(len(a)):
            if i != n:
                value = a[i][col]
                a[i] = [v-value*w for v,w in zip(a[i],a[n])]
        n += 1
    if any(not any(row[:3]) and row[3] for row in a[n:]):
        return None
    return tuple(tuple(row) for row in a[:n])


def affine_coordinates(flat):
    pivots = [next(i for i in range(3) if row[i]) for row in flat]
    free = [i for i in range(3) if i not in pivots]
    origin = [F(0)]*3
    directions = []
    for row, pivot in zip(flat,pivots):
        origin[pivot] = row[3]
    for i in free:
        vector = [F(0)]*3
        vector[i] = F(1)
        for row,pivot in zip(flat,pivots):
            vector[pivot] = -row[i]
        directions.append(vector)
    return origin,directions


def evaluate(form,point):
    return form[0]+sum(a*b for a,b in zip(form[1:],point))


def generic_point(flat,planes):
    origin,directions = affine_coordinates(flat)
    zeros = [i for i,p in enumerate(planes)
             if not evaluate(p,origin) and all(not sum(a*b for a,b in zip(p[1:],v)) for v in directions)]
    nonzero = [p for i,p in enumerate(planes) if i not in zeros]
    # Substitute distinct powers t,t^2,t^3 for the free coordinates.  Each
    # nonidenticallyzero affine form stays a nonzero univariate polynomial.
    bound = len(nonzero)*len(directions)
    for t in range(bound+1):
        point = [origin[j]+sum(t**(i+1)*v[j] for i,v in enumerate(directions)) for j in range(3)]
        if all(evaluate(p,point) for p in nonzero):
            return point,zeros,t,bound
    raise ValueError('polynomial root-count guarantee failed')


def rank(vectors):
    # In Q^3, inspect literal determinants/cross products, independently of the
    # arrangement's maximal-basis classification.
    rows = [v for v in vectors if any(v)]
    if not rows:
        return 0
    for a,b in combinations(rows,2):
        cross = (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
        if any(cross):
            if any(sum(x*y for x,y in zip(cross,c)) for c in rows):
                return 3
            return 2
    return 1


def classify():
    forms = {ids:minor_form(ids) for ids in combinations(range(9),3)}
    planes = sorted({primitive(f) for f in forms.values() if any(f[1:])})
    need(len(planes) == 25, '25 independent affine planes')
    flats = {()}
    inconsistent = Counter()
    for size in range(1,4):
        for selected in combinations(planes,size):
            flat = rref([(*p[1:],-p[0]) for p in selected])
            if flat is None:
                inconsistent[size] += 1
            else:
                flats.add(flat)
    ordered = sorted(flats,key=lambda f:(len(f),f))
    need(len(ordered) == 443, 'all 443 intersections of up to three planes')
    records = []
    total_rank_checks = 0
    for index,flat in enumerate(ordered):
        point,zeros,t,bound = generic_point(flat,planes)
        columns = [tuple(F(x)+w*y for x,y in zip(v,point)) for v,w in zip(BASE,WEIGHT)]
        bases = [list(ids) for ids,f in forms.items() if evaluate(f,point)]
        need(all(det(*(columns[i] for i in ids)) == evaluate(f,point) for ids,f in forms.items()), 'literal 84 determinants at generic point')
        need([0,1,2] in bases, 'marked identity basis')
        bmasks = [sum(1<<i for i in b) for b in bases]
        ranks = []
        for mask in range(512):
            actual = rank([v for i,v in enumerate(columns) if mask>>i&1])
            expected = max((b&mask).bit_count() for b in bmasks)
            need(actual == expected, 'all subset ranks from maximal bases')
            ranks.append(actual)
        total_rank_checks += 512
        opts = []
        for target in range(3):
            good = [s for s in range(64) if ranks[s<<3] == ranks[(s<<3)|(1<<target)]]
            minimal = [s for s in good if not any(v != s and v&s == v for v in good)]
            need(minimal and all(s.bit_count() == ranks[s<<3] for s in minimal), 'minimal recovery independence and existence')
            opts.append(minimal)
        records.append(dict(index=index,generic_h=list(map(str,point)),dimension=3-len(flat),
                            generic_parameter=t,parameter_bound=bound,
                            source_coordinate_masks=[sum(1<<j for j in range(3) if columns[i+3][j]) for i in range(6)],
                            reader_minimal_masks=opts,rank_table_sha256=sha256(bytes(ranks)).hexdigest()))
    # These guard the empty, parallel-inconsistent and dependent constraints.
    need(rref([]) == (), 'ambient flat control')
    need(rref([(1,0,0,0),(1,0,0,1)]) is None, 'parallel inconsistency control')
    need(rref([(1,0,0,0),(2,0,0,0)]) == ((F(1),F(0),F(0),F(0)),), 'dependent plane control')
    summary = dict(status='PASS',
                   maximal_minors=84,zero_minors=sum(not any(f) for f in forms.values()),
                   nonzero_constant_minors=sum(bool(f[0]) and not any(f[1:]) for f in forms.values()),
                   planes=25,flats=len(records),flats_by_dimension=dict(sorted(Counter(str(r['dimension']) for r in records).items())),
                   exact_subset_rank_checks=total_rank_checks,inconsistent_plane_subsets=dict(inconsistent),
                   generic_representatives='Exact moment-curve choices, each certified against all 25 planes and 84 minors',
                   scope='All rational h in Q^3 for the fixed six-query P8 extension, no invoice claim',
                   strata=records)
    need(summary['flats_by_dimension'] == {'0':250,'1':167,'2':25,'3':1}, 'complete dimension census')
    return summary



PINS = {
 'research/p112-rational-decoder-gate/CANDIDATE.json': 'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b',
 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json': 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
}
def binary_rank(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length()-1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def geometry():
    inputs = []
    for path,pin in PINS.items():
        raw = (ROOT/path).read_bytes()
        need(sha256(raw).hexdigest() == pin,'scientific input pin')
        inputs.append(json.loads(raw))
    candidate,data = inputs
    ids = [17,18,29,30,31,32]
    groups = [candidate['groups'][i] for i in ids]
    need([[groups[2*j][0],groups[2*j+1][0]] for j in range(3)] == [[0,67],[7,64],[1,75]],'fixed target placement')
    labels = {r['port']:r['q'] for r in data['recipes']}
    spaces = [[labels[p] for j,g in enumerate(groups) if mask>>j&1 for p in g] for mask in range(64)]
    table = [[binary_rank(sum(((a&b).bit_count()%2)<<j for j,b in enumerate(spaces[t])) for a in spaces[s])
              for t in range(64)] for s in range(64)]
    need(all(0 <= x <= 9 for row in table for x in row),'byte lane cost range')
    need(all(table[s][t] <= table[s|(1<<g)][t] and table[s][t] <= table[s][t|(1<<g)]
             for s in range(64) for t in range(64) for g in range(6)), 'all whole-group monotonic extensions')
    return table,groups,candidate['groups']


def profiles(options,groups):
    return [(choice,tuple(sum(1<<g for g,s in zip(groups,choice) if s>>q&1) for q in range(6)))
            for choice in product(*(options[g//2] for g in groups))]


def below(packed,count,threshold):
    high = int.from_bytes(bytes([128])*count,'little')
    shift = int.from_bytes(bytes([128-threshold])*count,'little')
    return high ^ ((packed+shift)&high)


def threshold_check(source,options,table):
    rows = [table[s] for s in source]
    halves = [profiles(options,groups) for groups in ((0,2,4),(1,3,5))]
    kept = [[(choice,masks) for choice,masks in half if sum(rows[q][masks[q]] for q in range(6)) < 18] for half in halves]
    left,right = kept
    count = len(right)
    cells = len(halves[0])*len(halves[1])
    checked = len(left)*count
    witness = None
    if count and left:
        # Each lane holds one right-profile objective. Six nonnegative costs
        # are at most54, so neither their sum nor +110 carries across bytes.
        masks_left = [sum(1<<g for g in (0,2,4) if mask>>(g//2)&1) for mask in range(8)]
        costs = [{mask:int.from_bytes(bytes(rows[q][mask|tm[q]] for _,tm in right),'little')
                  for mask in masks_left} for q in range(6)]
        high = int.from_bytes(bytes([128])*count,'little')
        offset = int.from_bytes(bytes([110])*count,'little')
        for choice,lm in left:
            packed = (costs[0][lm[0]]+costs[1][lm[1]]+costs[2][lm[2]]+
                      costs[3][lm[3]]+costs[4][lm[4]]+costs[5][lm[5]])
            violations = high ^ ((packed+offset)&high)
            # Independently unpack every surviving cell and compare its
            # ordinary six-term integer sum. Only123,990 cells survive over
            # the entire arrangement, so this exact control is inexpensive.
            literal = [sum(rows[q][lm[q]|rm[q]] for q in range(6)) for _,rm in right]
            need(packed.to_bytes(count,'little') == bytes(literal),'every packed lane equals literal invoice')
            need(bool(violations) == any(value < 18 for value in literal),'packed threshold agrees with all literal comparisons')
            if violations:
                j = ((violations&-violations).bit_length()-1)//8
                other,rm = right[j]
                masks = [a|b for a,b in zip(lm,rm)]
                costs_literal = [rows[q][masks[q]] for q in range(6)]
                need(sum(costs_literal) < 18,'unpacked improving witness')
                groups = [choice[0],other[0],choice[1],other[1],choice[2],other[2]]
                witness = dict(group_query_masks=groups,reader_group_masks=masks,term_costs=costs_literal,cost=sum(costs_literal))
                break
    return dict(closed_below_18=witness is None,all_cartesian_cells=cells,
                half_counts=list(map(len,halves)),retained_half_counts=list(map(len,kept)),
                packed_cell_count=checked,improving_witness=witness)


def equality_control(table,groups,all_groups):
    # Literal h=0, six queries in their declared order. This equality uses
    # three nonzero terms; the unused prescribed queries are permitted.
    queries = [(0,0,0),(0,1,1),(1,0,1),(1,1,0),(2,1,1),(1,0,0)]
    recoveries = [(0,0,0,0,0,1),(0,0,0,1,0,-1),(0,0,1,0,0,-1)]
    targets = [[groups[2*j][0],groups[2*j+1][0]] for j in range(3)]
    kind = {p:j for j,ps in enumerate(targets) for p in ps}
    ports = sorted(p for g in all_groups for p in g)
    need(len(ports) == len(set(ports)) == 112,'literal physical port partition')
    source = {p:tuple(col[kind[p]] for col in queries) if p in kind else (0,)*6 for p in ports}
    reader = {p:recoveries[kind[p]] if p in kind else (0,)*6 for p in ports}
    for p in ports:
        for q in ports:
            need(sum(a*b for a,b in zip(source[p],reader[q])) == int(p in kind and q in kind and kind[p] == kind[q]),'h=0 complete literal endpoint')
    sm = [sum(1<<g for g,ps in enumerate(groups) if any(source[p][i] for p in ps)) for i in range(6)]
    tm = [sum(1<<g for g,ps in enumerate(groups) if any(reader[p][i] for p in ps)) for i in range(6)]
    costs = [table[s][t] for s,t in zip(sm,tm)]
    need(sum(costs) == 18 and costs == [0,0,6,6,0,6],'attained family equality')
    corrupted = list(recoveries[0])
    corrupted[5] = 2
    need(sum(queries[i][0]*corrupted[i] for i in range(6)) != 1,'coefficient mutation endpoint rejected')
    return dict(h=[0,0,0],source_masks=sm,reader_masks=tm,term_costs=costs,
                cost=sum(costs),literal_endpoint_entries=len(ports)**2,
                coefficient_readers=list(map(list,recoveries)),coefficient_fault_rejected=True)


def run():
    own = classify()
    classification_payload = json.dumps(own,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
    support_profiles = [dict(index=r['index'],source_coordinate_masks=r['source_coordinate_masks'],
                             reader_minimal_masks=[sorted(x) for x in r['reader_minimal_masks']])
                        for r in own['strata']]
    profiles_payload = json.dumps(support_profiles,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
    table,groups,all_groups = geometry()
    # Boundary and large-lane controls independently unpack every byte.
    test = int.from_bytes(bytes([17,18,54,0,35]),'little')
    flags = below(test,5,18)
    need([bool(flags & (128<<(8*i))) for i in range(5)] == [True,False,False,True,False],'strict threshold boundary control')
    six = sum(int.from_bytes(bytes([9,0,8,1]),'little') for _ in range(6))
    need(six.to_bytes(4,'little') == bytes([54,0,48,6]),'all-six-term carry control')
    records = []
    strata = own['strata']
    for r in strata:
        masks = [sum(3<<(2*j) for j in range(3) if s>>j&1) for s in r['source_coordinate_masks']]
        checked = threshold_check(masks,r['reader_minimal_masks'],table)
        records.append(dict(index=r['index'],dimension=r['dimension'],source_group_masks=masks,**checked))
    need(len(records) == 443 and all(r['closed_below_18'] for r in records), 'all443 strata exclude invoices below18')
    record_payload = json.dumps(records,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
    result = dict(status='PASS',
                complete=True,strata=len(records),classification_sha256=sha256(classification_payload).hexdigest(),
                scientific_inputs=PINS,tariff_sha256=sha256(bytes(x for row in table for x in row)).hexdigest(),
                total_cartesian_cells=sum(r['all_cartesian_cells'] for r in records),
                packed_cells=sum(r['packed_cell_count'] for r in records),
                scope='Fixed rank3 P8 dictionary on the declared three ordinary targets; every rational h and every actual reader',
                equality=equality_control(table,groups,all_groups),
                threshold_records_sha256=sha256(record_payload).hexdigest(),
                support_profiles_sha256=sha256(profiles_payload).hexdigest(),
                classification_summary={k:v for k,v in own.items() if k != 'strata'},
                all_remaining_cells_checked_as_literal_sums=True,
                algorithm='Three-groups versus three-groups; monotone partial deletion and exact packed/literal invoice comparison',
                frozen_receipt_contract='443 ordered classifications and443 ordered threshold records recomputed; compact hashes commit all rows')
    return json.loads(json.dumps(result))




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-receipt',action='store_true')
    args = parser.parse_args()
    result = run()
    path = HERE/'INDEPENDENT-RANK3-RESULT.json'
    if args.write_receipt:
        path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:
        need(json.loads(path.read_text(encoding='utf-8')) == result,'frozen independent rank3 receipt')
    print(json.dumps(result,sort_keys=True))
