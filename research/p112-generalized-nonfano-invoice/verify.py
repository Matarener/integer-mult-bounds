"""Exact identity and fixed geometric premises for one five-target mechanism.

No candidate, coefficient, reader, or embedding optimization is performed.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    'research/p112-rational-decoder-gate/CANONICAL-SHARP-PROOF.md':
    '9b2646258e5a7956380a601bb83c9721fe9c006be768762cf3095ae0b336ca08',
    'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json':
    'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
    'research/p112-rational-decoder-gate/CANDIDATE.json':
    'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b',
}


def need(ok, text):
    if not ok:
        raise ValueError(text)


def read(path):
    raw = (ROOT / path).read_bytes()
    need(sha256(raw).hexdigest() == PINS[path], 'input pin')
    return json.loads(raw)


def rational_rank(matrix):
    rows = [[F(x) for x in row] for row in matrix]
    r = 0
    for c in range(len(rows[0])):
        found = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if found is None:
            continue
        rows[r], rows[found] = rows[found], rows[r]
        pivot = rows[r][c]
        rows[r] = [x/pivot for x in rows[r]]
        for i in range(r+1, len(rows)):
            v = rows[i][c]
            if v:
                rows[i] = [x-v*y for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


def check_endpoint(source, reader):
    need(all(sum(source[p][t]*reader[q][t] for t in range(6)) == int(p//2 == q//2)
             for p in range(10) for q in range(10)), '100 exact endpoint entries')


def main():
    for path, pin in PINS.items():
        need(sha256((ROOT/path).read_bytes()).hexdigest() == pin, 'source pin: '+path)
    # Query order y0,y1,y2,y3,y4,yB. Target-coordinate order a,b1,..,b4.
    queries = [[1]*5]
    for i in range(1, 5):
        queries.append([int(j != i) for j in range(5)])
    queries.append([0,1,1,1,1])
    source = [[queries[t][p//2] for t in range(6)] for p in range(10)]
    reader = [[F(1),F(0),F(0),F(0),F(0),F(-1)],
              [F(0),F(1,4),F(1,4),F(1,4),F(1,4),F(-3,4)]]
    for i in range(1, 5):
        row = [F(0)]*6
        row[0], row[i] = F(1), F(-1)
        reader.extend([row[:], row[:]])
    check_endpoint(source, reader)
    rejected=0
    for original, which in ((source, 'source'), (reader, 'reader')):
        for row in range(10):
            for col in range(6):
                if not original[row][col]:
                    continue
                changed=[list(r) for r in original]
                changed[row][col] += 1
                try:
                    check_endpoint(changed if which=='source' else source,
                                   changed if which=='reader' else reader)
                except ValueError:
                    rejected+=1
                else:
                    raise ValueError('endpoint mutation survived')
    need(rejected == 73, 'complete nonzero-coefficient mutation domain')
    need(rational_rank(source) == 5 and rational_rank(reader) == 6, 'factor ranks5,6')
    relation = [4,-1,-1,-1,-1,-1]
    need(all(sum(relation[t]*queries[t][j] for t in range(6)) == 0 for j in range(5)),
         'query circuit relation')
    source_masks = [sum(1 << p for p in range(10) if source[p][t]) for t in range(6)]
    reader_masks = [sum(1 << p for p in range(10) if reader[p][t]) for t in range(6)]
    need(source_masks == [1023,1011,975,831,255,1020], 'abstract source masks')
    need(reader_masks == [1021,14,50,194,770,3], 'abstract reader masks')

    data = read('research/adaptive-kernel-demotion/inputs/DATA-PHASES.json')
    cover = read('research/p112-rational-decoder-gate/CANDIDATE.json')
    labels = [r['q'] for r in sorted(data['recipes'], key=lambda r: r['port'])]
    groups = cover['groups']
    need(len(labels) == 112 and len(groups) == 38, 'literal geometry size')
    pair_vectors = [[labels[p] for g in (2*i+1, 2*i+2) for p in groups[g]] for i in range(18)]
    need(all(all((x&y).bit_count()%2 == int(i == j) for i,x in enumerate(pair)
                 for j,y in enumerate(pair)) for pair in pair_vectors), 'own six-dimensional Gram')
    annihilators = [{z for z in range(1, 512) if all((z&x).bit_count()%2 == 0 for x in pair)}
                   for pair in pair_vectors]
    need(all(len(s) == 7 for s in annihilators), 'three-dimensional annihilators')
    occupancy = Counter(sum(z in s for s in annihilators) for z in range(1, 512))
    need(dict(occupancy) == {0:395, 1:107, 2:8, 3:1}, 'literal annihilator incidence')
    intersection_profile = {}
    for count in (2, 3):
        hist = Counter(len(set.intersection(*(annihilators[i] for i in roles)))
                       for roles in combinations(range(18), count))
        intersection_profile[count] = dict(sorted(hist.items()))
    need(intersection_profile == {2:{0:142,1:11},3:{0:815,1:1}}, 'pair/triple span premises')
    j_vectors = [labels[p] for p in groups[37]]
    need(all((x&y).bit_count()%2 == int(i == j) for i,x in enumerate(j_vectors)
             for j,y in enumerate(j_vectors)), 'J own Gram identity')
    j_annihilator = {z for z in range(1, 512) if all((z&x).bit_count()%2 == 0 for x in j_vectors)}
    j_pair_profile = Counter(len(j_annihilator & ann) for ann in annihilators)
    need(dict(j_pair_profile) == {0:7,1:9,3:2}, 'J-plus-pair boundary')
    triad_annihilators = [{z for z in range(1,512)
                           if all((z&labels[p]).bit_count()%2 == 0 for p in groups[g])}
                          for g in range(1,37)]
    foreign_dimensions = Counter()
    for role, ann in enumerate(annihilators):
        for group_index, triad_ann in enumerate(triad_annihilators):
            if group_index//2 == role:
                continue
            annihilator_order = len(ann & triad_ann)+1
            need(annihilator_order & (annihilator_order-1) == 0, 'annihilator subspace order')
            dimension = 9-(annihilator_order.bit_length()-1)
            foreign_dimensions[dimension] += 1
    need(dict(foreign_dimensions) == {7:46,8:318,9:248}, 'foreign triad plus pair premise')
    need(sum(foreign_dimensions.values()) == 612, 'complete foreign triad domain')
    j_bounds = [{'J_b_targets':k, 'baseline_without_residual':30-3*k,
                 'one_ordinary_role_floor':36-3*k, 'multiple_ordinary_roles_floor':30-2*k}
                for k in (1,2,3)]
    need(all(r['multiple_ordinary_roles_floor'] >= r['baseline_without_residual']+1
             for r in j_bounds), 'residual cannot rescue J cases')
    print(json.dumps({'status':'PASS', 'input_sha256':PINS,
                      'endpoint_entries':100, 'endpoint_mutations_rejected':rejected, 'source_rank':5, 'reader_rank':6,
                      'source_masks_abstract_groups':source_masks,
                      'reader_masks_abstract_groups':reader_masks,
                      'query_dependence':relation,
                      'annihilator_occupancy':dict(sorted(occupancy.items())),
                      'nonzero_common_annihilator_profiles':intersection_profile,
                      'J_pair_nonzero_common_annihilator_profile':dict(sorted(j_pair_profile.items())),
                      'foreign_triad_plus_pair_dimension_profile':dict(sorted(foreign_dimensions.items())),
                      'J_case_analytic_bounds':j_bounds,
                      'every_four_distinct_roles_span_dimension':9,
                      'scope':'One exact six-query mechanism; fixed physical span checks, no pricing sweep.'},
                     separators=(',', ':')))


if __name__ == '__main__':
    main()
