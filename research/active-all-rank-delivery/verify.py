"""Check the complete fixed-chart delivery floor with exact rational cuts.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The unchanged response census is credited to PR5808 and its predecessors.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, label):
    if not ok:
        raise ValueError(label)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def authenticate():
    rows = json.loads((HERE / 'SOURCES.json').read_bytes())['files']
    for row in rows:
        if row['usage'] == 'input':
            need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'source hash ' + row['path'])


def determinant(matrix):
    """Use integer elimination, separate from the sparse response algebra."""
    a = [row[:] for row in matrix]
    sign, previous = 1, 1
    for k in range(len(a)-1):
        pivot = next((i for i in range(k, len(a)) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        value = a[k][k]
        for i in range(k+1, len(a)):
            for j in range(k+1, len(a)):
                numerator = value*a[i][j]-a[i][k]*a[k][j]
                need(numerator % previous == 0, 'Exact determinant division')
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = value
    return sign*a[-1][-1]


def check_certificate(charts, target, certificate, include_rank8=False):
    need(certificate['minimum_channels'] == 9 and certificate['rank_excluded'] == 8,
         'Exact channel and rank domain')
    selected = {f: c for f, c in charts.items() if c['basis'] and c['rank'] > 0
                and (c['rank'] != 8 or include_rank8)}
    loads = {f: F(0) for f in selected}
    bound, details = F(0), []
    for row in certificate['rows']:
        weight = F(row['weight'])
        need(weight > 0, 'Positive dual weight')
        if 'channels' in row:
            need(row['channels'] == 9, 'At least nine channels')
            rank, active, kind = 9, list(selected), 'channel count'
        elif 'coordinates' in row:
            coordinates = row['coordinates']
            need(len(coordinates) == len(set(coordinates)) == 8
                 and all(type(i) is int and 0 <= i < 112 for i in coordinates),
                 'Eight distinct actual coordinates')
            rank = len(R.span({i: v for i, v in t.items() if i in coordinates} for t in target))
            need(rank == row['rank'] == 8, 'Full target rank on the coordinate basis')
            matrix = [[t.get(i, F(0)) for i in coordinates] for t in target]
            need(all(v.denominator == 1 for t in matrix for v in t), 'Integral source modes')
            need(determinant([[int(v) for v in t] for t in matrix]) != 0,
                 'Independent coordinate determinant')
            active = [f for f, c in selected.items() if set(coordinates) & c['support']]
            kind = 'coordinate basis'
        else:
            need(set(row['frames']) <= charts.keys(), 'Actual cut frames')
            rank, all_active = R.rank_cut(charts, target, row['frames'])
            need(rank == row['rank'] and rank > 0, 'Exact target quotient rank')
            active = [f for f in all_active if f in selected]
            kind = 'response span'
        for f in active:
            loads[f] += weight
        bound += weight * rank
        details.append(dict(kind=kind, rank=rank, active=len(active),
                            active_sha256=sha256(canonical(active)).hexdigest()))
    need(all(loads[f] <= c['rank'] for f, c in selected.items()), 'Every exact dual capacity')
    need(str(bound) == certificate['lower_bound'] and bound > 72, 'Strict rank-mass bound above 72')
    return dict(charts=len(selected), rows=details, lower_bound=str(bound),
                integer_rank_mass=-(-bound.numerator // bound.denominator),
                capacity_sha256=sha256(canonical([[f, str(v)] for f, v in loads.items()])).hexdigest())


def combine(vectors, coefficients):
    value = {}
    for v, coefficient in zip(vectors, coefficients):
        R.add(value, v, F(coefficient))
    return value


def clean_witness(charts, target):
    """Find exact target directions in each rank-eight response space."""
    witnesses = []
    intersections = {}
    for f, chart in charts.items():
        basis = list(chart['basis'].values())
        dimension = len(basis) + 8 - len(R.span([*basis, *target]))
        if dimension:
            intersections[f] = dimension
            need(chart['rank'] >= 8, 'No low-rank clean response')
        if chart['rank'] != 8 or not dimension:
            continue
        rows, relations = {}, []
        vectors = basis + target
        for j, vector in enumerate(vectors):
            v, coefficients = dict(vector), {j: F(1)}
            for pivot, (old, origin) in rows.items():
                if v.get(pivot):
                    q = -v[pivot]
                    R.add(v, old, q)
                    R.add(coefficients, origin, q)
            if v:
                pivot = min(v)
                q = v[pivot]
                rows[pivot] = ({i: a/q for i, a in v.items()},
                               {i: a/q for i, a in coefficients.items()})
            else:
                relations.append(coefficients)
        for relation in relations:
            response = [-relation.get(i, F(0)) for i in range(len(basis))]
            modes = [relation.get(len(basis)+i, F(0)) for i in range(8)]
            value = combine(basis, response)
            need(value and value == combine(target, modes), 'Exact clean response witness')
            witnesses.append(dict(frame=f, response_coefficients=list(map(str, response)),
                                  mode_coefficients=list(map(str, modes))))
    need(len(witnesses) == 8 and len(R.span(
        {i: F(v) for i, v in enumerate(w['mode_coefficients']) if F(v)} for w in witnesses)) == 8,
        'Eight independent rank-eight attaining directions')
    return dict(intersections=intersections, witnesses=witnesses)


def replacement_and_price(charts, target, integer_mass):
    full = [f for f, c in charts.items() if c['rank'] == 9 and len(c['basis']) == 112]
    need(len(full) == 1 and all(not R.reduce({i: F(1)}, charts[full[0]]['basis'])
                               for i in range(112)), 'Rank-nine universal response space')
    need(all(not c['basis'] for c in charts.values() if c['rank'] == 0), 'Ground has zero response')
    need(integer_mass == 73, 'Exact integer certificate consequence')
    masses = [integer_mass-k for k in range(8)]
    need(min(masses) == 66, 'Replacing at most seven rank-eight channels')
    # A weaker mass-65 consequence gives a simple strict gap for every power.
    need(9**18 > 8**19, 'Rational comparison of logarithms')
    gap = F(2) - F(8, 19) * F(144, 133)**18
    need(gap > F(1, 5), 'Global minimum of the comparison polynomial')
    for n in range(9, 66):
        majorant = [9]*7 + [1, 1] + [0]*(n-9)
        need(sum(majorant) == 65 and
             all(sum(majorant[:k]) >= min(9*k, 65-(n-k)) for k in range(1, n+1)),
             'Every rank-mass-65 channel vector is majorized')
    return dict(universal_rank9_frame=full[0], original_rank_mass_by_rank8_count=masses,
                recursive_floor='8*H8', more_than_eight_channel_gap='greater than H1/5',
                power_domain='0 < q <= 1; Hr = r^q H1; H1 > 0',
                polynomial_gap_lower_bound=str(gap))


def reject(action, expected):
    try:
        action()
    except ValueError as error:
        need(expected in str(error), 'Wrong rejection: ' + str(error))
        return expected
    raise ValueError('Accepted invalid control: ' + expected)


def controls(charts, target, cert):
    out = []
    bad = deepcopy(cert)
    for row in bad['rows']:
        row['weight'] = str(10*F(row['weight']))
    bad['lower_bound'] = str(10*F(bad['lower_bound']))
    out.append(reject(lambda: check_certificate(charts, target, bad), 'Every exact dual capacity'))
    bad = deepcopy(cert)
    next(row for row in bad['rows'] if 'frames' in row)['rank'] -= 1
    out.append(reject(lambda: check_certificate(charts, target, bad), 'Exact target quotient rank'))
    bad = deepcopy(cert)
    row = next(row for row in bad['rows'] if 'coordinates' in row)
    row['coordinates'][0] = row['coordinates'][1]
    out.append(reject(lambda: check_certificate(charts, target, bad), 'Eight distinct actual coordinates'))
    bad = deepcopy(cert)
    bad['minimum_channels'] = 8
    out.append(reject(lambda: check_certificate(charts, target, bad), 'Exact channel and rank domain'))
    out.append(reject(lambda: check_certificate(charts, target, cert, include_rank8=True),
                      'Every exact dual capacity'))
    bad = deepcopy(charts)
    full = next(f for f, c in bad.items() if c['rank'] == 9)
    bad[full]['basis'].pop(next(iter(bad[full]['basis'])))
    out.append(reject(lambda: replacement_and_price(bad, target, 73), 'Rank-nine universal response space'))
    bad = dict(charts)
    bad[-1] = dict(rank=1, basis=R.span(target), support=set(range(112)))
    out.append(reject(lambda: clean_witness(bad, target), 'No low-rank clean response'))
    # Noise can cancel jointly: two clean target columns from three noisy channels.
    noisy = [{0: F(1), 2: F(1)}, {1: F(1), 2: F(-1)}, {2: F(1)}]
    need(combine(noisy, [1, 0, -1]) == {0: F(1)}
         and combine(noisy, [0, 1, 1]) == {1: F(1)}, 'Joint-noise positive control')
    # Eight rank-nine channels satisfy every quotient cut but not the count premise.
    need(all(8 >= row.get('rank', 0) for row in cert['rows'] if 'channels' not in row)
         and 8 < cert['minimum_channels'], 'Eight-channel branch stays separate')
    return dict(semantic_rejections=out, joint_noise=True, eight_channel_domain_control=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    authenticate()
    sys.path.insert(0, str(HERE))
    global R
    import responses as R
    word, modes = R.load()
    charts, target, coverage = R.scan(word, modes)
    cert = json.loads((HERE / 'CERTIFICATE.json').read_bytes())
    checked = check_certificate(charts, target, cert)
    result = dict(coverage=coverage, certificate=checked, attaining=clean_witness(charts, target),
                  all_rank_floor=replacement_and_price(charts, target, checked['integer_rank_mass']),
                  controls=controls(charts, target, cert),
                  scope='Fixed word, immutable payload and chart, arbitrary rational scatter and joint noise; inherited native specialization.')
    authenticate()
    text = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.record:
        (HERE / 'RESULT.json').write_text(text)
    else:
        need((HERE / 'RESULT.json').read_text() == text, 'Exact typed complete receipt')
    print('PASS_ALL_RANK_IMMUTABLE_DELIVERY_FLOOR_8H8')


if __name__ == '__main__':
    main()
