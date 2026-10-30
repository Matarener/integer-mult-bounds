"""Independent exact P8 dictionary, geometry and all-324-stratum invoice audit.

No producer imports or artifact writes, except explicit --write-receipt.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, permutations, product
from collections import Counter
import argparse
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = {
 'research/p112-rational-decoder-gate/CANDIDATE.json': 'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b',
 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json': 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
}
Q = [(0,0,0,1),(0,1,1,2),(1,0,1,1),(1,1,0,1),(2,1,1,0),(1,0,0,1)]
P8 = [tuple(int(i == j) for i in range(4)) for j in range(4)] + Q[1:5]
NONBASES = [(1,2,3,8),(1,2,4,7),(1,3,4,6),(2,3,4,5),(1,4,5,8),
            (2,3,6,7),(1,5,6,7),(2,5,6,8),(3,5,7,8),(4,6,7,8)]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rank(rows):
    a = [list(map(F, row)) for row in rows]
    if not a:
        return 0
    r = 0
    for j in range(len(a[0])):
        p = next((i for i in range(r, len(a)) if a[i][j]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        v = a[r][j]
        a[r] = [x/v for x in a[r]]
        for i in range(r+1, len(a)):
            v = a[i][j]
            a[i] = [x-v*y for x,y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def determinant(a):
    total = F(0)
    for p in permutations(range(len(a))):
        value = F((-1)**sum(p[i] > p[j] for i in range(len(p)) for j in range(i+1,len(p))))
        for i,j in enumerate(p):
            value *= a[i][j]
        total += value
    return total


def characteristic_obstruction_control():
    # Formal determinants after the seven spanning-tree scalings. Five
    # variables are a,b,c,d,e; equality up to a global sign is immaterial.
    zero = (0,)*5
    def const(n):
        return {zero:n} if n else {}
    def variable(i):
        return {tuple(int(j == i) for j in range(5)):1}
    def add(*args):
        out = Counter()
        for poly in args:
            for k,v in poly.items():
                out[k] += v
        return {k:v for k,v in out.items() if v}
    def neg(p):
        return {k:-v for k,v in p.items()}
    def mul(p,q):
        out = Counter()
        for a,x in p.items():
            for b,y in q.items():
                out[tuple(s+t for s,t in zip(a,b))] += x*y
        return {k:v for k,v in out.items() if v}
    def det(rows):
        out = {}
        for p in permutations(range(len(rows))):
            term = const((-1)**sum(p[i]>p[j] for i in range(len(p)) for j in range(i+1,len(p))))
            for i,j in enumerate(p):
                term = mul(term,rows[i][j])
            out = add(out,term)
        return out
    one,z = const(1),{}
    a,b,c,d,e = [variable(i) for i in range(5)]
    cols = [[const(i == j) for i in range(4)] for j in range(4)] + [[z,one,one,d],[one,z,c,one],[one,one,z,e],[a,b,one,z]]
    specs = [((1,4,5,8),add(b,neg(one))),((2,3,6,7),add(e,neg(one)))]
    for ids,expected in specs:
        actual = det([cols[i-1] for i in ids])
        need(actual == expected or actual == neg(expected), 'formal b/e incidence')
    cols[6][3] = one
    cols[7][1] = one
    specs = [((1,5,6,7),add(c,one,neg(mul(c,d)))),
             ((2,5,6,8),add(d,a,neg(mul(mul(a,c),d)))),
             ((3,5,7,8),add(d,a,neg(mul(a,d)))),
             ((4,6,7,8),add(one,c,neg(mul(a,c))))]
    for ids,expected in specs:
        actual = det([cols[i-1] for i in ids])
        need(actual == expected or actual == neg(expected), 'formal normalized incidence')
    return {'formal_incidence_determinants':6,
            'deduction':'b=e=1; cd=c+1; d=ac=c+1; (c-1)(c+1)=0; d nonzero forces c=1,d=2, excluding characteristic2.'}


def inverse(a):
    n = len(a)
    rows = [list(map(F,row)) + [F(i == j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        p = next((i for i in range(j,n) if rows[i][j]), None)
        need(p is not None, 'Gram matrix nonsingular')
        rows[j],rows[p] = rows[p],rows[j]
        v = rows[j][j]
        rows[j] = [x/v for x in rows[j]]
        for i in range(n):
            if i != j:
                v = rows[i][j]
                rows[i] = [x-v*y for x,y in zip(rows[i],rows[j])]
    return [row[n:] for row in rows]


def brank(rows):
    basis = {}
    for x in rows:
        while x:
            i = x.bit_length()-1
            if i in basis:
                x ^= basis[i]
            else:
                basis[i] = x
                break
    return len(basis)


def coefficient_readers():
    options, recoveries, feasible = [], {}, []
    for j in range(3):
        target = tuple(int(i == j) for i in range(4))
        good = [s for s in range(64) if rank([Q[i] for i in range(6) if s>>i&1]) ==
                rank([Q[i] for i in range(6) if s>>i&1]+[target])]
        small = sorted(s for s in good if not any(t != s and t&s == t for t in good))
        need(all(any(t&s == t for t in small) for s in good), 'minimal reader domination')
        for s in small:
            ids = [i for i in range(6) if s>>i&1]
            vectors = [Q[i] for i in ids]
            need(rank(vectors) == len(ids), 'minimal reader independence')
            gram = [[sum(x*y for x,y in zip(v,w)) for w in vectors] for v in vectors]
            gi = inverse(gram)
            rhs = [v[j] for v in vectors]
            coeff = [sum(x*y for x,y in zip(row,rhs)) for row in gi]
            row = [F(0)]*6
            for i,c in zip(ids,coeff):
                row[i] = c
            need(all(row[i] != 0 for i in ids), 'minimal reader nonzero coefficients')
            need(all(sum(Q[i][k]*row[i] for i in range(6)) == target[k] for k in range(4)), 'Gram recovery endpoint')
            recoveries[j,s] = row
        options.append(small)
        feasible.append(len(good))
    need(list(map(len,options)) == [5,6,6], 'literal minimal reader census')
    return options,recoveries,feasible


def load_geometry():
    inputs = []
    for path,digest in PINS.items():
        raw = (ROOT/path).read_bytes()
        need(sha256(raw).hexdigest() == digest, 'input pin '+path)
        inputs.append(json.loads(raw))
    candidate,data = inputs
    gids = [17,18,29,30,31,32]
    groups = [candidate['groups'][g] for g in gids]
    targets = [[groups[2*j][0],groups[2*j+1][0]] for j in range(3)]
    need(targets == [[0,67],[7,64],[1,75]], 'declared placement')
    need(all(set(t) in list(map(set,candidate['factor_supports'])) for t in targets), 'canonical marks')
    labels = {r['port']:r['q'] for r in data['recipes']}
    spaces = [[labels[p] for g in range(6) if s>>g&1 for p in groups[g]] for s in range(64)]
    tariffs = [[brank(sum(((a&b).bit_count()%2)<<j for j,b in enumerate(spaces[t])) for a in spaces[s])
                for t in range(64)] for s in range(64)]
    need(all(tariffs[s][t] <= tariffs[s|(1<<g)][t] and tariffs[s][t] <= tariffs[s][t|(1<<g)]
             for s in range(64) for t in range(64) for g in range(6)), 'whole-space tariff monotonicity')
    ports = sorted(p for group in candidate['groups'] for p in group)
    need(len(ports) == 112 and len(set(ports)) == 112, 'literal 112 ports')
    return gids,groups,targets,tariffs,ports


def source_masks(xs):
    return [sum(1<<g for g,x in enumerate(xs) if F(col[g//2])+col[3]*x) for col in Q]


def reader_profiles(options):
    return [(choices, tuple(sum(1<<g for g,s in enumerate(choices) if s>>q&1) for q in range(6)))
            for choices in product(*(options[g//2] for g in range(6)))]


def exhaust(sm, profiles, tariffs):
    rows = [tariffs[s] for s in sm]
    best, count, dense_count, dense_union, first = 100,0,0,0,None
    for choices,tm in profiles:
        value = rows[0][tm[0]]+rows[1][tm[1]]+rows[2][tm[2]]+rows[3][tm[3]]+rows[4][tm[4]]+rows[5][tm[5]]
        if value < best:
            best,count,dense_count,dense_union,first = value,0,0,0,(choices,tm)
        if value == best:
            count += 1
            dense = (int(bool(tm[1])) << 1) | (int(bool(tm[4])) << 4)
            dense_count += bool(dense)
            dense_union |= dense
    choices,tm = first
    return {'minimum':best,'minimizers':count,'minimizers_using_q1_or_q4':dense_count,
            'dense_query_union':dense_union,'group_query_masks':list(choices),
            'reader_group_masks':list(tm),'term_costs':[rows[i][tm[i]] for i in range(6)]}


def endpoint_control(xs, optimum, recoveries, targets, groups, ports, tariffs):
    source = {p:[F(0)]*6 for p in ports}
    readers = {p:[F(0)]*6 for p in ports}
    kind = {p:j for j,ts in enumerate(targets) for p in ts}
    for g,x in enumerate(xs):
        p = targets[g//2][g%2]
        source[p] = [F(col[g//2])+col[3]*x for col in Q]
        readers[p] = recoveries[g//2,optimum['group_query_masks'][g]]
    for p in ports:
        for q in ports:
            need(sum(a*b for a,b in zip(source[p],readers[q])) == int(p in kind and q in kind and kind[p] == kind[q]), 'literal endpoint')
    sm = [sum(1<<g for g,ps in enumerate(groups) if any(source[p][i] for p in ps)) for i in range(6)]
    tm = [sum(1<<g for g,ps in enumerate(groups) if any(readers[p][i] for p in ps)) for i in range(6)]
    costs = [tariffs[s][t] for s,t in zip(sm,tm)]
    need(costs == optimum['term_costs'] and sum(costs) == optimum['minimum'], 'literal invoice')
    return {'entries':len(ports)**2,'source_masks':sm,'reader_masks':tm,'costs':costs,
            'reader_columns':[[str(c) for c in readers[targets[g//2][g%2]]] for g in range(6)]}


def run():
    need(rank(P8) == rank(Q) == 4, 'P8 and query ranks')
    determinants = {ids:determinant([P8[i-1] for i in ids]) for ids in combinations(range(1,9),4)}
    need(sorted(ids for ids,d in determinants.items() if not d) == sorted(NONBASES), 'ten literal nonbases')
    need(all(not d or (abs(int(d)) & (abs(int(d))-1)) == 0 for d in determinants.values()), 'all nonzero maximal minors powers of2')
    options,recoveries,feasible = coefficient_readers()
    gids,groups,targets,tariffs,ports = load_geometry()
    profiles = reader_profiles(options)
    need(len(profiles) == 32400, 'all reader support cells')
    original = [F(1),F(-1),F(0),F(0),F(0),F(0)]
    reduced = [F(0),F(-1),F(0),F(0),F(0),F(0)]
    oldsm,newsm = source_masks(original),source_masks(reduced)
    need(oldsm == [3,63,49,13,63,1] and newsm == [2,62,49,13,63,1], 'source support cancellations')
    need(all(new&old == new for old,new in zip(oldsm,newsm)), 'source support dominance')
    need(all(tariffs[new][t] <= tariffs[old][t] for old,new in zip(oldsm,newsm) for t in range(64)), 'all 384 tariff dominations')
    fixed = []
    for name,xs in [('fixed-p8',original),('reduced-p8',reduced)]:
        result = exhaust(source_masks(xs),profiles,tariffs)
        control = endpoint_control(xs,result,recoveries,targets,groups,ports,tariffs)
        fixed.append({'name':name,**result,'endpoint':control})
    need([x['minimum'] for x in fixed] == [21,18], 'two exact fixed minima')
    roots = []
    for j in range(3):
        rr = sorted(set(-F(col[j],col[3]) for col in Q if col[3]))
        need(rr == ([-F(1),F(0)] if j == 0 else [-F(1),-F(1,2),F(0)]), 'complete affine zero roots')
        roots.append(rr)
    mutation_controls = []
    bad = dict(fixed[1])
    bad['minimum'] -= 1
    try:
        endpoint_control(reduced,bad,recoveries,targets,groups,ports,tariffs)
    except ValueError:
        mutation_controls.append('underpriced invoice rejected')
    bad_readers = {key:list(row) for key,row in recoveries.items()}
    bad_readers[0,fixed[1]['group_query_masks'][0]][0] += 1
    try:
        endpoint_control(reduced,fixed[1],bad_readers,targets,groups,ports,tariffs)
    except ValueError:
        mutation_controls.append('corrupted reader coefficient rejected')
    need(len(mutation_controls) == 2, 'fault controls')
    # With h=0 the literal q5 equals c0, although its coefficient column
    # is e0+e3: an extra reader after collapse, outside this result's scope.
    need(Q[5] == (1,0,0,1) and 32 not in options[0], 'rank-three extra-reader coefficient control')
    need(all(Q[5][j] == int(j == 0) for j in range(3)), 'rank-three literal reader endpoint')
    mutation_controls.append('rank-three extra reader exists but violates inherited A r=e0')
    result = {'status':'PASS_INDEPENDENT_P8','input_pins':PINS,'groups':gids,'targets':targets,
              'rank':4,'four_subset_minor_count':70,'nonbases':[list(t) for t in sorted(NONBASES)],
              'characteristic_obstruction':characteristic_obstruction_control(),
              'absolute_nonzero_minor_histogram':dict(sorted(Counter(str(abs(d)) for d in determinants.values() if d).items())),
              'minimal_reader_supports':options,'all_feasible_reader_support_counts':feasible,
              'subset_recovery_checks':192,'whole_group_tariffs_checked':4096,'reader_cells_per_source':len(profiles),
              'fixed_source_results':fixed,'source_roots':[[str(x) for x in row] for row in roots],
              'fault_controls':mutation_controls,
              'scope':'One fixed six-query coefficient matrix and one literal target placement; all reader coefficients exact.'}
    allrows = []
    for index,xs in enumerate(product(*(roots[g//2] for g in range(6)))):
        sm = source_masks(xs)
        outcome = exhaust(sm,profiles,tariffs)
        embedding_rank = 3 + int(any(xs[2*j] != xs[2*j+1] for j in range(3)))
        allrows.append({'index':index,'h':[str(x) for x in xs],'embedding_rank':embedding_rank,
                        'source_masks':sm,**outcome})
    need(len(allrows) == 324, 'complete source strata')
    for row in allrows:
        # Every minimizing rank-four stratum has the unique dense-free
        # minimal profile. Dense terms cost strictly positively for any
        # nonzero reader, so a nonminimal optimum cannot add one either.
        if row['embedding_rank'] == 4 and row['minimum'] == 18:
            need(row['minimizers'] == 1 and row['minimizers_using_q1_or_q4'] == 0, 'rank-four minimizer structure')
            need(all(tariffs[row['source_masks'][q]][t] > 0 for q in [1,4] for t in range(1,64)), 'dense added reader is strictly priced')
    need(min(r['minimum'] for r in allrows) == 18, 'complete family minimum')
    by_h = {tuple(F(x) for x in r['h']):r for r in allrows}
    minimum_rows = []
    for twice_h in product((0,-2),(0,-2),(0,-1,-2),(0,-1,-2),(0,-1,-2),(0,-1,-2)):
        row = by_h[tuple(F(x,2) for x in twice_h)]
        minimum_rows.append({'twice_h':list(twice_h),'physical_coordinate_rank':row['embedding_rank'],
                             'source_group_masks':row['source_masks'],'optimum':row['minimum']})
    digest = sha256(json.dumps(minimum_rows,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')).hexdigest()
    result['exterior_family'] = {
        'strata':324,'cells':324*len(profiles),'embedding_rank_histogram':dict(sorted(Counter(str(r['embedding_rank']) for r in allrows).items())),
        'minimum':min(r['minimum'] for r in allrows),'minimum_histogram':dict(sorted(Counter(str(r['minimum']) for r in allrows).items())),
        'minimum_rows_sha256':digest,
        'rank4_minimizing_strata':[r for r in allrows if r['embedding_rank'] == 4 and r['minimum'] == 18],
        'scope':'Covers all original rank-4 exterior h by support domination. Rank-3 strata retain A R=[I3;0], not their additional readers.'}
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--write-receipt',action='store_true')
    args = ap.parse_args()
    result = run()
    receipt = HERE/'INDEPENDENT-RESULT.json'
    if args.write_receipt:
        receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:
        need(json.loads(receipt.read_text(encoding='utf-8')) == result, 'frozen independent receipt')
    print(json.dumps({'status':result['status'],'source_strata':324,'objective_cells':10497600,'minimum':18,
                      'receipt_sha256':sha256(receipt.read_bytes()).hexdigest()},indent=2))
