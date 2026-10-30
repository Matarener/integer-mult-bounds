#!/usr/bin/env python3
"""Independent QQ16 profile/caller and rational quadrature budget audit.

Chris R / Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
No predecessor executable is imported. See PROOF.md for the interval argument.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha1, sha256
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
M, W, R = 73, Q(896, 9), 51
GRID = 1 << 80


def need(ok, why):
    if not ok:
        raise ValueError(why)


def unique(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, 'duplicate JSON key')
        out[key] = value
    return out


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def pinned(path, root=ROOT, manifest=None):
    if manifest is None:
        manifest = decode((HERE / 'SOURCES.json').read_bytes())
    rows = [row for row in manifest['files'] if row['path'] == path and row['usage'] == 'input']
    need(len(rows) == 1, 'unique input pin: ' + path)
    raw = (root / path).read_bytes()
    row = rows[0]
    need(sha256(raw).hexdigest() == row['sha256'], 'source SHA256: ' + path)
    need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'],
         'source Git blob: ' + path)
    return raw


def outward(lo, hi):
    return Q((lo.numerator * GRID) // lo.denominator, GRID), Q(-((-hi.numerator * GRID) // hi.denominator), GRID)


@lru_cache(None)
def integral_log(y, panels=1024):
    """Midpoint lower / trapezoid upper for integral_1^y 1/t dt."""
    y = Q(y)
    need(1 <= y <= 2 and type(panels) is int and panels > 0, 'quadrature domain')
    if y == 1:
        return Q(0), Q(0)
    h = (y - 1) / panels
    lo = h * sum(1 / (1 + (Q(j) + Q(1, 2)) * h) for j in range(panels))
    hi = h * ((1 + 1 / y) / 2 + sum(1 / (1 + j * h) for j in range(1, panels)))
    return outward(lo, hi)


@lru_cache(None)
def logarithm(x):
    x = Q(x)
    need(x >= 1, 'logarithm domain')
    powers = 0
    while x > 2:
        x /= 2
        powers += 1
    lo, hi = integral_log(x)
    two_lo, two_hi = integral_log(Q(2))
    return outward(lo + powers * two_lo, hi + powers * two_hi)


def exponential(lo, hi, degree=6):
    need(0 <= lo <= hi <= Q(1, 2), 'exponential domain')
    need(type(degree) is int and degree >= 1, 'exponential degree')
    lsum = usum = lterm = uterm = Q(1)
    for j in range(1, degree + 1):
        lterm *= lo / j
        uterm *= hi / j
        lsum += lterm
        usum += uterm
    first = uterm * hi / (degree + 1)
    tail = first / (1 - hi / (degree + 2))
    return outward(lsum, usum + tail)


@lru_cache(None)
def cost(rank, a):
    need(type(rank) is int and 0 < rank < M and a >= 0, 'child domain')
    lo, hi = logarithm(Q(M, rank))
    lo, hi = exponential(a * lo, a * hi)
    return outward(Q(rank, M) * lo, Q(rank, M) * hi)


def expand(packet, name):
    events = []

    def visit(sequence):
        for event in sequence:
            tag = event[0]
            if tag == 'retained_core':
                need(event[1] in ('forward', 'backward'), 'core orientation')
                visit(packet['core_words'][event[1]])
            elif tag in ('private_sweep', 'cover_sweep'):
                visit(event[2])
            else:
                need(tag in ('scalar', 'climb', 'adapter', 'residual_adapter',
                             'phase', 'native_line', 'cover_map'), 'unknown event')
                events.append(event)

    visit(packet['programs'][name])
    return events


def profile(packet, events):
    out = Counter()
    for event in events:
        if event[0] == 'climb':
            rank = event[5]
        elif event[0] == 'native_line':
            record = packet['native_line_recipes'][event[2]]
            rank = record['rank']
            need(record['recipe']['rank'] == rank, 'wrapper recipe rank')
        else:
            continue
        need(type(rank) is int and 0 < rank < M, 'literal child rank')
        out[rank] += 1
    return dict(sorted(out.items()))


def moment(base, decoder_pair, centre, rank8, a, idle_rank=R):
    need(all(type(r) is int and 0 < r < M and Q(n) >= 0 for r,n in base.items()), 'local profile domain')
    need(2 * idle_rank**2 < M**2 and idle_rank >= max(base), 'halving / relaxation rank')
    need(Q(decoder_pair) >= 0 and Q(centre) >= 0, 'negative budget charge')
    local = {r: Q(n) for r, n in base.items()}
    local[1] += Q(decoder_pair, 2)
    if rank8:
        local[8] = Q(8)
    total = (M - 1) * W + centre
    paid = sum(r * n for r, n in local.items())
    idle = total - paid
    need(idle >= 0, 'negative idle mass')
    lo = hi = Q(0)
    for rank, number in local.items():
        clo, chi = cost(rank, a)
        lo += number * clo
        hi += number * chi
    clo, chi = cost(idle_rank, a)
    return outward((lo + idle / idle_rank * clo) / W,
                   (hi + idle / idle_rank * chi) / W)


def decimal_interval(pair, digits=12):
    scale = 10**digits
    lo, hi = pair
    l = lo.numerator * scale // lo.denominator
    u = -((-hi.numerator * scale) // hi.denominator)
    return {'lower': str(Q(l, scale)), 'upper': str(Q(u, scale)),
            'decimal_lower': f'{l // scale}.{l % scale:0{digits}d}',
            'decimal_upper': f'{u // scale}.{u % scale:0{digits}d}'}


def calculate(root=ROOT, manifest=None):
    def source(path):
        return pinned(path, root, manifest)

    # Also authenticated for the retained predecessor replay in test_verify.py.
    source('research/complex-local-word-ceiling/ceiling.py')
    selected = decode(source('certificates/selected-result.json'))
    kappa = Q(selected['kappa'])
    need(kappa == Q(836330098538459, 500000000000000000), 'selected target')
    a = kappa / (1 - kappa)
    model = decode(source('research/complex-local-word-ceiling/RESULT.json'))['model']
    need((model['m'], Q(model['live_families_per_call']), model['centre_per_call'],
          model['idle_rank_cap']) == (M, W, 64, R), 'coverage model')
    payload = gzip.decompress(source('research/joint-query/certificate.json.gz'))
    packet = decode(payload)
    reported = decode(source('research/joint-query/evidence/CONSERVED-QQ16.json'))
    need(sha256(payload).hexdigest() == reported['payload_sha256'], 'producer payload binding')
    profiles, event_counts = {}, {}
    for name, side in [('F_0', 'F'), ('B_1_2', 'B')]:
        events = expand(packet, name)
        profiles[name] = profile(packet, events)
        event_counts[name] = len(events)
        need(profiles[name] == {int(r): n for r, n in reported['invoices'][side]['native_profile'].items()},
             'literal / reported producer profile')
        need(sum(r * n for r, n in profiles[name].items()) == reported['invoices'][side]['native_mass'],
             'literal producer mass')
    need(event_counts == {'F_0': 26099, 'B_1_2': 27019}, 'literal event counts')
    need(len(packet['programs']) == 37, 'complete native case inventory')
    for name in packet['programs']:
        expected = profiles['F_0'] if name.startswith('F_') else profiles['B_1_2']
        need(name.startswith(('F_', 'B_')) and profile(packet, expand(packet, name)) == expected,
             'native case profile: ' + name)
    f = expand(packet, 'F_0')
    cut = next(j for j, e in enumerate(f) if e[0] in ('climb', 'native_line'))
    need((cut, f[cut], f[cut+1]) ==
         (9894, ['climb', 'A', 546, 0, 4, 1], ['scalar', ['add', ['L', 546], ['L', 561], -1, 1], 4]),
         'first F0 caller and consumer')
    need(sha256(canonical(f[:cut])).hexdigest() ==
         '15115954461f2cb93e2266822d82bfac1ab8de7d460ff78fcf594d21c61d2b53',
         'first F0 prefix binding')
    decoder_word = decode(source('research/qq16-line-normalized-decoder/WORD.json'))
    dc = Counter(event[0] for event in decoder_word)
    need(dc == {'add': 2704, 'map': 464, 'line': 336, 'clear': 312, 'begin': 3, 'end': 3, 'checkpoint': 1},
         'literal decoder inventory')
    need(all(len(e) == 4 and e[3] in (-1, 1) for e in decoder_word if e[0] == 'line'),
         'decoder signed line syntax')
    decoder = decode(source('research/qq16-line-normalized-decoder/RESULT.json'))
    need(decoder['invoice']['rank_one_children'] == dc['line'] and decoder['invoice']['rank_eight_children'] == 0,
         'literal / reported decoder count')
    base = {r: Q(profiles['F_0'].get(r, 0) + profiles['B_1_2'].get(r, 0), 2)
            for r in set(profiles['F_0']) | set(profiles['B_1_2'])}
    need(base == {1:2428, 2:418, 3:432, 4:142, 5:82}, 'pair average')
    relaxed = moment(base, dc['line'], 64, False, a)
    full = moment(base, dc['line'], 64, True, a)
    centre63 = moment(base, dc['line'], 63, True, a)
    f_only = moment(profiles['F_0'], dc['line'], 64, False, a)
    need(relaxed[0] > Q(100009, 100000) and full[0] > relaxed[1], 'independent obstruction')
    need(f_only[0] > Q(100009, 100000), 'F/B reweighting with fixed decoder rate')
    need(centre63[1] < 1, 'changed-centre optimistic opening')
    rows = []
    for rank8, last_pass, first_fail in [(False, 121, 122), (True, 61, 62)]:
        passing = moment(base, last_pass, 64, rank8, a)
        failing = moment(base, first_fail, 64, rank8, a)
        need(passing[1] < 1 < failing[0], 'decoder threshold bracket')
        rows.append({'retains_eight_rank8':rank8, 'largest_integer_pair_count_passing_relaxation':last_pass,
                     'first_integer_pair_count_excluded':first_fail,
                     'passing':decimal_interval(passing), 'excluded':decimal_interval(failing)})
    p363, p364 = moment(base,363,63,True,a), moment(base,364,63,True,a)
    need(p363[1] < 1 < p364[0], 'centre63 repayment threshold')
    return {'status':'PASS_QQ16_CONSUMER_BUDGET_INDEPENDENT no_new_kappa',
            'selected_a':str(a), 'producer_profiles':{k:{str(r):n for r,n in p.items()} for k,p in profiles.items()},
            'producer_events':event_counts, 'decoder_pair_children':dc['line'],
            'native_cases_profile_checked':37,
            'f_only_lower_envelope_with_168_decoder_per_call':decimal_interval(f_only),
            'caller':{'event':cut,'child':f[cut],'next':f[cut+1],
                      'prefix_sha256':sha256(canonical(f[:cut])).hexdigest()},
            'minimal_profile_centre64':decimal_interval(relaxed),
            'reported_rank8_profile_centre64':decimal_interval(full),
            'changed_centre63_full_profile':decimal_interval(centre63),
            'centre63_normalized_extra_cost_allowance':decimal_interval((1-centre63[1],1-centre63[0])),
            'decoder_thresholds':rows,
            'centre63_decoder_pair_threshold':{'last_pass':363,'first_excluded':364,
                                               'passing':decimal_interval(p363),'excluded':decimal_interval(p364)},
            'scope':'Conditional fixed-profile coverage obstruction and optimistic changed-contract budget only; no physical supplier admission.'}


def main():
    actual = calculate()
    expected = decode((HERE / 'RESULT.json').read_bytes())
    need(canonical(actual) == canonical(expected), 'complete RESULT mismatch')
    print(json.dumps(actual, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
