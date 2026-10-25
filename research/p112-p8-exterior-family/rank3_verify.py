"""Exact threshold replay of all rational rank-three P8 zero-pattern strata.

The complete affine classifier is regenerated here. No generic sample point
is used to derive a reader or source support in the cost proof.
Prepared by flyingviper with substantial OpenAI Codex assistance. Apache-2.0.
Default execution checks the receipt without writing it.
"""
from argparse import ArgumentParser
from fractions import Fraction as F
from functools import reduce
from itertools import combinations, permutations
from math import gcd
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = {
    'research/p112-rational-decoder-gate/CANDIDATE.json':
        'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b',
    'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json':
        'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
}
GROUPS = [17, 18, 29, 30, 31, 32]
Q0 = [[0,0,0], [0,1,1], [1,0,1], [1,1,0], [2,1,1], [1,0,0]]
B = [1,2,1,1,0,1]
ZERO = (0,0,0)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def add(p,q,scale=1):
 out=dict(p)
 for monomial,c in q.items():
  out[monomial]=out.get(monomial,0)+scale*c
  if not out[monomial]:del out[monomial]
 return out
def mul(p,q):
 out={}
 for a,x in p.items():
  for b,y in q.items():
   z=tuple(a[i]+b[i]for i in range(3));out[z]=out.get(z,0)+x*y
 return {m:c for m,c in out.items()if c}
def entry(column,row):
 if column<3:return {ZERO:int(column==row)}if column==row else{}
 j=column-3;out={ZERO:Q0[j][row]}if Q0[j][row]else{}
 if B[j]:out[tuple(int(i==row)for i in range(3))]=B[j]
 return out
def determinant(columns):
 out={}
 for perm in permutations(range(3)):
  sign=(-1)**sum(perm[i]>perm[j]for i in range(3)for j in range(i+1,3));term={ZERO:1}
  for row in range(3):term=mul(term,entry(columns[perm[row]],row))
  out=add(out,term,sign)
 need(all(sum(m)<=1 for m in out),'maximal minor is affine by rank-one update')
 return tuple([out.get(ZERO,0)]+[out.get(tuple(int(i==j)for i in range(3)),0)for j in range(3)])
def primitive(form):
 if not any(form):return form
 g=reduce(gcd,(abs(x)for x in form if x));s=1 if next(x for x in form if x)>0 else-1
 return tuple(s*x//g for x in form)
def intersect(flat,plane):
 rows=[list(row)for row in flat]+[[F(x)for x in plane[1:]]+[F(-plane[0])]];k=0
 for col in range(4):
  pivot=next((i for i in range(k,len(rows))if rows[i][col]),None)
  if pivot is None:continue
  if col==3:return None
  rows[k],rows[pivot]=rows[pivot],rows[k];div=rows[k][col];rows[k]=[x/div for x in rows[k]]
  for i in range(len(rows)):
   if i!=k:
    c=rows[i][col];rows[i]=[a-c*b for a,b in zip(rows[i],rows[k])]
  k+=1
 return tuple(tuple(row)for row in rows[:k])
def classify():
 minors=[(columns,determinant(columns))for columns in combinations(range(9),3)]
 planes=sorted({primitive(form)for _,form in minors if any(form[1:])});index={p:i for i,p in enumerate(planes)}
 flats={()}
 for plane in planes:
  flats.update(x for f in list(flats)if(x:=intersect(f,plane))is not None)
 ordered=sorted(flats,key=lambda f:(len(f),f));records=[];counts={str(d):0 for d in range(4)}
 for flat in ordered:
  zeros=[i for i,plane in enumerate(planes)if intersect(flat,plane)==flat]
  basis=[list(columns)for columns,form in minors if any(form)and(not any(form[1:])or index[primitive(form)]not in zeros)]
  need([0,1,2]in basis,'identity target basis always survives')
  dimension=3-len(flat);counts[str(dimension)]+=1
  records.append({'dimension':dimension,'rref_equations':[[str(x)for x in row]for row in flat],'zero_hyperplanes':zeros,'basis_count':len(basis),'bases':basis})
 receipt={'scope':'complete rational rank3 h affine-flat source/reader classification; no invoice evaluation','query_base_columns':Q0,'rank_one_coefficients':B,'augmented_ground_order':['c0','c1','c2','q0','q1','q2','q3','q4','q5'],'maximal_minor_count':len(minors),'identically_zero_minors':sum(not any(f)for _,f in minors),'constant_nonzero_minors':sum(bool(f[0])and not any(f[1:])for _,f in minors),'affine_nonconstant_minors':sum(any(f[1:])for _,f in minors),'distinct_hyperplanes':len(planes),'hyperplane_coefficients_constant_x_y_z':[list(p)for p in planes],'flat_count':len(records),'flats_by_dimension':counts,'minor_forms':[{'columns':list(c),'coefficients':list(f),'hyperplane_index':index[primitive(f)]if any(f[1:])else None}for c,f in minors],'flats':records}
 return receipt


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            k = row.bit_length() - 1
            if k in pivots:
                row ^= pivots[k]
            else:
                pivots[k] = row
                break
    return len(pivots)


def geometry():
    records = []
    for path, expected in INPUTS.items():
        raw = (ROOT / path).read_bytes()
        need(sha256(raw).hexdigest() == expected, 'Scientific input hash: ' + path)
        records.append(json.loads(raw))
    candidate, data = records
    ports = [candidate['groups'][g] for g in GROUPS]
    need(all(len(group) == 3 for group in ports), 'Whole physical triads')
    targets = [[ports[2*j][0], ports[2*j+1][0]] for j in range(3)]
    need(targets == [[0,67],[7,64],[1,75]], 'Fixed marking')
    need(all(set(target) in map(set, candidate['factor_supports']) for target in targets),
         'Canonical target marks')
    labels = {row['port']: row['q'] for row in data['recipes']}
    unions = [[labels[p] for g in range(6) if mask >> g & 1 for p in ports[g]]
              for mask in range(64)]
    tariffs = [[binary_rank([sum(((a & b).bit_count() % 2) << j
                                for j,b in enumerate(reader)) for a in source])
                for reader in unions] for source in unions]
    for s in range(64):
        for r in range(64):
            for g in range(6):
                need(tariffs[s][r] <= tariffs[s | 1 << g][r], 'Source monotonicity')
                need(tariffs[s][r] <= tariffs[s][r | 1 << g], 'Reader monotonicity')
    return targets, tariffs


def support_patterns(flat):
    """Recover the entire subset rank function from the surviving bases."""
    bases = [sum(1 << i for i in basis) for basis in flat['bases']]
    need(7 in bases, 'Identity basis')
    ranks = [max((basis & mask).bit_count() for basis in bases) for mask in range(512)]
    sources = []
    for query in range(6):
        sources.append(sum(1 << j for j in range(3)
                           if ((7 ^ (1 << j)) | (1 << (3+query))) in bases))
    readers = []
    for target in range(3):
        minimal = []
        for mask in sorted(range(64), key=lambda m:(m.bit_count(),m)):
            columns = mask << 3
            if ranks[columns] == ranks[columns | 1 << target]:
                if not any(previous & mask == previous for previous in minimal):
                    minimal.append(mask)
        need(minimal and 0 not in minimal, 'Nonzero recoverable target')
        # Minimal spanning sets are independent and have no unused member.
        need(all(ranks[mask << 3] == mask.bit_count() for mask in minimal),
             'Independent minimal recovery')
        readers.append(minimal)
    return sources, readers


def threshold_decision(costs, options, threshold=18):
    """Complete B&B for the existence of a cost strictly below threshold.

    Each single remaining-group extension is a valid lower bound.  We take
    their maximum by early rejection; we never add their increments together.
    """
    used = {mask: [i for i in range(6) if mask >> i & 1]
            for row in options for mask in row}
    increments = [[[costs[i][mask | 1 << g] - costs[i][mask] for mask in range(64)]
                   for i in range(6)] for g in range(6)]
    need(all(x >= 0 for group in increments for row in group for x in row),
         'Nonnegative tariff increment')
    nodes = [0] * 7
    witness = None

    def visit(depth, readers, partial, choices):
        nonlocal witness
        nodes[depth] += 1
        if partial >= threshold:
            return False
        if depth == 6:
            need(partial == sum(costs[i][readers[i]] for i in range(6)), 'Leaf repricing')
            witness = {'cost':partial, 'group_query_masks':choices,
                       'query_reader_masks':readers,
                       'term_costs':[costs[i][readers[i]] for i in range(6)]}
            return True
        next_options = None
        for group in range(depth, 6):
            additions = [(sum(increments[group][i][readers[i]] for i in used[mask]), mask)
                         for mask in options[group]]
            if partial + min(extra for extra, _ in additions) >= threshold:
                return False
            if group == depth:
                next_options = sorted(additions)
        for extra, mask in next_options:
            if partial + extra >= threshold:
                continue
            extended = readers[:]
            for i in used[mask]:
                extended[i] |= 1 << depth
            if visit(depth+1, extended, partial+extra, choices+[mask]):
                return True
        return False

    found = visit(0, [0]*6, 0, [])
    return {'closed_below_18':not found, 'nodes_by_depth':nodes,
            'improving_witness':witness}


def equality_witness(targets, tariffs):
    # At h=0: c0=q5, c1=q3-q5, c2=q2-q5. Copy readers independently.
    coefficients = [[0,0,0,0,0,1], [0,0,0,1,0,-1], [0,0,1,0,0,-1]]
    queries = [[sum(Q0[t][j] for j in range(3) if p in targets[j])
                for p in range(112)] for t in range(6)]
    readers = [[sum(coefficients[j][t] for j in range(3) if p in targets[j])
                for p in range(112)] for t in range(6)]
    need(all(sum(queries[t][a]*readers[t][b] for t in range(6)) ==
             sum(int(a in target and b in target) for target in targets)
             for a in range(112) for b in range(112)), 'All 12544 endpoint entries')
    source_masks = [sum(3 << (2*j) for j in range(3) if Q0[t][j]) for t in range(6)]
    reader_masks = [sum(3 << (2*j) for j in range(3) if coefficients[j][t]) for t in range(6)]
    costs = [tariffs[s][r] for s,r in zip(source_masks,reader_masks)]
    need(costs == [0,0,6,6,0,6], 'Equality invoice')
    need(sum(costs) == 18, 'Family equality')
    return {'h':['0','0','0'], 'reader_coefficients_by_target':coefficients,
            'source_group_masks':source_masks, 'reader_group_masks':reader_masks,
            'term_costs':costs, 'cost':sum(costs), 'endpoint_entries_checked':112**2}


def run():
    classification = classify()
    need(classification['maximal_minor_count'] == 84, 'Complete minor count')
    need(classification['identically_zero_minors'] == 3, 'Identically zero minors')
    need(classification['constant_nonzero_minors'] == 4, 'Constant nonzero minors')
    need(classification['distinct_hyperplanes'] == 25, 'Hyperplane coverage')
    need(classification['flat_count'] == 443, 'Flat coverage')
    need(classification['flats_by_dimension'] == {'0':250,'1':167,'2':25,'3':1},
         'Complete affine intersection lattice')
    targets, tariffs = geometry()
    rows = []
    cells = 0
    for index, flat in enumerate(classification['flats']):
        sources, readers = support_patterns(flat)
        physical_sources = [sum(3 << (2*j) for j in range(3) if mask >> j & 1)
                            for mask in sources]
        options = [readers[g//2] for g in range(6)]
        count = 1
        for row in options:
            count *= len(row)
        cells += count
        answer = threshold_decision([tariffs[mask] for mask in physical_sources], options)
        rows.append({'index':index, 'dimension':flat['dimension'],
                     'source_coordinate_masks':sources, 'source_group_masks':physical_sources,
                     'reader_minimal_masks':readers, 'unpruned_cells':count, **answer})
    need(cells == 2785849439, 'Complete Cartesian coverage count')
    need(all(row['closed_below_18'] for row in rows), 'Improvement found; inspect witness')
    return {'status':'PASS',
            'scope':'Exact family minimum 18 for all rational rank3 P8 exteriors at the fixed marking; no per-stratum minimum claim',
            'input_pins':INPUTS,
            'classification':{
                'maximal_minors':84, 'identically_zero_minors':3,
                'constant_nonzero_minors':4, 'affine_nonconstant_minors':77,
                'hyperplanes':classification['hyperplane_coefficients_constant_x_y_z'],
                'flats_by_dimension':classification['flats_by_dimension'],
                'complete_minor_forms_sha256':digest(classification['minor_forms']),
                'complete_flats_sha256':digest(classification['flats'])},
            'strata':443, 'augmented_subset_ranks_rebuilt':443*512,
            'tariff_entries':4096, 'tariff_sha256':digest(tariffs),
            'unpruned_cells':cells,
            'branch_nodes':sum(sum(row['nodes_by_depth']) for row in rows),
            'nodes_by_depth':[sum(row['nodes_by_depth'][i] for row in rows) for i in range(7)],
            'complete_threshold_rows_sha256':digest(rows),
            'support_profiles_sha256':digest([
                {'index':row['index'], 'source_coordinate_masks':row['source_coordinate_masks'],
                 'reader_minimal_masks':[sorted(x) for x in row['reader_minimal_masks']]}
                for row in rows]),
            'closed_below_18':443, 'family_minimum':18,
            'equality_witness':equality_witness(targets,tariffs)}


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--write-receipt', action='store_true')
    args = parser.parse_args()
    result = run()
    receipt = HERE / 'RANK3-RESULT.json'
    if args.write_receipt:
        receipt.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    else:
        need(receipt.is_file() and json.loads(receipt.read_text()) == result, 'Read-only receipt comparison')
    print(json.dumps({k:v for k,v in result.items() if k not in ('classification','equality_witness','input_pins')}))
