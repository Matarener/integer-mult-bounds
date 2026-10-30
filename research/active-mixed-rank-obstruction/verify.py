"""Check exact mixed-rank channel certificates without an optimizer.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256, sha1
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from responses import load, need, rank_cut, scan, span, reduce


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def check_certificate(charts, target, certificate):
    cap = certificate['rank_cap']
    selected = {f: c for f, c in charts.items() if c['basis'] and 1 <= c['rank'] <= cap}
    weights = [F(v) for v in certificate['support_weights']]
    need(len(weights) == 112 and min(weights) >= 0, 'Nonnegative support weights')
    channel_weight = F(certificate.get('channel_weight', '0'))
    minimum_channels = certificate.get('minimum_channels', 0)
    need(channel_weight >= 0 and minimum_channels in (0, 9), 'Channel count premise')
    loads = {f: sum(weights[i] for i in c['support']) + channel_weight
             for f, c in selected.items()}
    bound = sum(weights) + minimum_channels * channel_weight
    for cut in certificate['cuts']:
        weight = F(cut['weight'])
        need(weight >= 0 and set(cut['span_frames']) <= selected.keys(), 'Cut domain')
        rank, active = rank_cut(selected, target, cut['span_frames'])
        need(rank == cut['target_rank'] and
             sha256(canonical(active)).hexdigest() == cut['active_sha256'], 'Exact quotient cut')
        for f in active:
            loads[f] += weight
        bound += weight * rank
    need(all(loads[f] <= selected[f]['rank'] for f in selected), 'Dual chart capacity')
    need(str(bound) == certificate['lower_bound'], 'Exact dual objective')
    integer = -(-bound.numerator // bound.denominator)
    need(integer == certificate['integer_rank_mass'], 'Integer rank mass')
    return dict(rank_cap=cap, minimum_channels=minimum_channels, charts=len(selected),
                cuts=len(certificate['cuts']), lower_bound=str(bound),
                integer_rank_mass=integer)


def support_optimum(charts, certificate):
    cap = certificate['rank_cap']
    weights = list(map(F, certificate['weights']))
    counts = {int(f): F(v) for f, v in certificate['counts'].items()}
    selected = {f: c for f, c in charts.items() if c['basis'] and 1 <= c['rank'] <= cap}
    need(len(weights) == 112 and min(weights) >= 0 and
         all(v >= 0 for v in counts.values()) and set(counts) <= selected.keys(), 'Cover domain')
    need(all(sum(weights[i] for i in c['support']) <= c['rank']
             for c in selected.values()), 'Cover dual capacity')
    need(all(sum(n for f, n in counts.items() if i in selected[f]['support']) >= 1
             for i in range(112)), 'Cover primal feasibility')
    value = sum(n * selected[f]['rank'] for f, n in counts.items())
    need(value == sum(weights) == F(certificate['optimum']), 'Exact cover strong duality')
    return dict(rank_cap=cap, optimum=str(value))


def fails(action, message):
    try:
        action()
    except ValueError:
        return message
    raise ValueError('Accepted control: ' + message)


def main(write_receipt=False):
    for record in json.loads((ROOT / 'ORIGINS.json').read_text()):
        raw = (ROOT / record['local']).read_bytes()
        need(sha256(raw).hexdigest() == record['sha256'] and
             sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == record['git_blob'],
             'Frozen predecessor bytes')
    word, modes = load()
    charts, target, coverage = scan(word, modes)
    saved = json.loads((ROOT / 'CERTIFICATES.json').read_text())
    bounds = [check_certificate(charts, target, c) for c in saved['rank_cuts']]
    covers = [support_optimum(charts, c) for c in saved['support_optima']]
    # The target has eight independent output directions.
    need(len(span(target)) == 8, 'Eight target directions')
    intersections = {}
    for f, c in charts.items():
        common = len(c['basis']) + 8 - len(span([*c['basis'].values(), *target]))
        if common:
            intersections[f] = common
    need(all(charts[f]['rank'] >= 8 for f in intersections), 'Low-rank clean exclusion')
    cover_limit = json.loads((ROOT / 'COVER-LIMIT.json').read_text())
    fields = cover_limit['frames']
    missing, _ = rank_cut(charts, target, fields)
    need(missing == cover_limit['missing_target_rank'] == 5 and
         sum(charts[f]['rank'] for f in fields) == cover_limit['rank_mass'] == 62 and
         set().union(*(charts[f]['support'] for f in fields)) == set(range(112)),
         'Cheap cover misses five target directions')
    rank1 = json.loads((ROOT / 'source/PR5755-RANK1.json').read_text())
    # The independent predecessor records every rank-one support.
    expected_rank1 = rank1['chart_Z_support']
    need({str(f): sorted(c['support']) for f, c in charts.items() if c['rank'] == 1}
         == expected_rank1, 'Independent rank-one supports')
    controls = []
    c = saved['rank_cuts'][0]
    mutant = deepcopy(c)
    mutant['support_weights'] = ['1000'] * 112
    controls.append(fails(lambda: check_certificate(charts, target, mutant), 'overweight dual'))
    mutant = deepcopy(c)
    mutant['cuts'][0]['target_rank'] += 1
    controls.append(fails(lambda: check_certificate(charts, target, mutant), 'wrong target quotient rank'))
    mutant = deepcopy(c)
    mutant['cuts'][0]['active_sha256'] = '0' * 64
    controls.append(fails(lambda: check_certificate(charts, target, mutant), 'omitted active chart'))
    extra = dict(charts)
    extra[-1] = dict(rank=1, basis=span(target), support=set(range(112)), responses=8)
    controls.append(fails(lambda: check_certificate(extra, target, c), 'unpriced all-mode chart'))
    raw_charts, _, _ = scan(word, modes, restore_y=False)
    controls.append(fails(lambda: check_certificate(raw_charts, target, c), 'free final-Y cleanup'))
    wrong = deepcopy(word)
    op = wrong['programs']['backward'][21113][1]
    need(op == ['add', ['L', 51], ['L', 53], 1, 1], 'Main-output control site')
    op[3] += op[4]
    controls.append(fails(lambda: scan(wrong, modes), 'changed scalar endpoint'))
    mutant = deepcopy(saved['support_optima'][0])
    mutant['counts'] = {}
    controls.append(fails(lambda: support_optimum(charts, mutant), 'incomplete cover'))
    # Three noisy channels can supply two clean directions by cancellation.
    a, b, noise = {0:F(1),2:F(1)}, {1:F(1),2:F(-1)}, {2:F(1)}
    need(len(span([a,b,noise])) == 3 and
         not reduce({0:F(1)}, span([a,b,noise])) and
         not reduce({1:F(1)}, span([a,b,noise])), 'Joint noise positive control')
    result = dict(coverage=coverage, exact_rank_bounds=bounds, exact_support_optima=covers,
                  clean_intersections={str(f):d for f,d in intersections.items()},
                  controls=controls, cover_limit=cover_limit, scope='Fixed immutable canonical channels; no new kappa')
    if write_receipt:
        (ROOT / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(result == json.loads((ROOT / 'RESULT.json').read_text()), 'Complete receipt')
    print('PASS_ACTIVE_MIXED_RANK_OBSTRUCTION', json.dumps(coverage, sort_keys=True))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-receipt', action='store_true')
    main(parser.parse_args().write_receipt)
