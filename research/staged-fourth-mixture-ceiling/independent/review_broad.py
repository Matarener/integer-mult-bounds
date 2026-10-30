"""Independent review of the three broad-interval owner duals and affine fills.

Imports only this directory's independent enclosure implementation; no solver,
source pricing implementation or owner checker is executed/imported.
"""
from fractions import Fraction as Q
import argparse
import importlib.util
import json
from pathlib import Path

_spec = importlib.util.spec_from_file_location('independent_pooled_check', Path(__file__).resolve().with_name('check.py'))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

LO, HI = Q('.00173'), Q('.00174')


def potentials(piece):
    u, v = C.dual_vectors()
    if piece == 'left':
        v[8] = C.vec((Q(1, 2), v[7]), (Q(1, 2), v[9]))
        v[6] = C.vec((2, v[7]), (-1, v[8]))
    elif piece == 'right':
        v[6] = C.vec((-Q(1, 2), C.h(48)), (-2, v[9]))
        v[8] = C.vec((2, v[7]), (-1, v[6]))
    else:
        C.need(piece == 'middle', 'dual piece')
    u[8] = C.vec((-1, v[8]))
    return u, v


def divided_difference_bounds():
    # For t=log(r)>=0, g(a)=r(exp(-at)-1)/a has derivative
    # r[1-(1+at)exp(-at)]/a^2>=0, by exp(at)>=1+at.
    # Thus its entire interval is enclosed by its two endpoint values.
    result = {}
    for r in range(1, 49):
        pl = C.power_enclosure(r, LO)
        ph = C.power_enclosure(r, HI)
        result[r] = ((Q(pl[0], C.SCALE) - r) / LO,
                     (Q(ph[1], C.SCALE) - r) / HI)
    return result


def normalized_enclosure(form, divided):
    C.need(sum(r * n for r, n in form.items()) == 0, 'factoring nonzero rank mass')
    lo = hi = Q(0)
    for r, n in form.items():
        a, b = divided[r]
        lo += n * (a if n > 0 else b)
        hi += n * (b if n > 0 else a)
    return lo, hi


def verify_dual(piece, divided, *, perturb=False):
    u, v = potentials(piece)
    if perturb:
        # Preserve zero rank mass while making the formerly tight cap8 pattern
        # infeasible: 2H1-H2>0 throughout the checked positive-k interval.
        u[8] = C.vec((1, u[8]), (2, C.h(1)), (-1, C.h(2)))
    identities = 0
    strict = 0
    minimum = None
    for capacity in C.CAPACITIES:
        for counts, remainder in C.patterns(capacity):
            slack = C.vec((1, C.h(remainder)), (-1, u[capacity]),
                          *((-n, v[w]) for w, n in zip(C.WIDTHS, counts)))
            if not slack:
                identities += 1
            else:
                interval = normalized_enclosure(slack, divided)
                C.need(interval[0] > 0, 'broad interval pattern slack')
                strict += 1
                if minimum is None or interval[0] < minimum:
                    minimum = interval[0]
    C.need(identities + strict == 841, 'complete broad pattern coverage')
    slope = C.vec((1, C.LOCAL_DELTA), (1, v[7]), (-1, v[8]))
    slo, shi = normalized_enclosure(slope, divided)
    if piece == 'left':
        C.need(shi < 0, 'left slope not strictly negative')
    elif piece == 'right':
        C.need(slo > 0, 'right slope not strictly positive')
    else:
        C.need(not slope and slo == shi == 0, 'middle slope not identically zero')
    return {'identities': identities, 'strict_patterns': strict,
            'minimum_normalized_slack_lower': str(minimum),
            'slope_over_k_interval': [str(slo), str(shi)],
            'slope_over_k_decimal': [C.decimal_str(slo), C.decimal_str(shi)]}


def affine_rows(piece):
    """Each row is capacity, integer width counts, constant y0, x coefficient y1."""
    common = [
        (8, (0, 0, 0, 1, 0), Q(241920), Q(0)),
        (16, (0, 0, 1, 0, 1), Q(161280), Q(0)),
        (32, (1, 0, 0, 0, 3), Q(90720), Q(0)),
    ]
    if piece == 'left':
        return common + [
            (32, (0, 0, 0, 0, 3), Q(1890), -Q(1, 4)),
            (32, (0, 0, 1, 2, 1), Q(540), -Q(1, 2)),
            (32, (0, 0, 2, 0, 2), Q(9810), Q(3, 4)),
            (32, (0, 1, 0, 1, 2), Q(58320), Q(0)),
            (48, (0, 0, 0, 0, 0), Q(138438), Q(1, 20)),
            (48, (0, 0, 0, 0, 5), Q(22842), -Q(1, 20)),
        ]
    C.need(piece == 'right', 'affine fill piece')
    return common + [
        (32, (0, 0, 0, 0, 3), Q(1080), Q(1, 2)),
        (32, (0, 0, 2, 0, 2), Q(10080), Q(1, 2)),
        (32, (0, 1, 0, 1, 2), Q(59400), -Q(1)),
        (48, (0, 0, 0, 0, 0), Q(138492), Q(0)),
        (48, (0, 0, 0, 0, 5), Q(23328), -Q(1, 2)),
        (48, (0, 2, 0, 0, 4), -Q(540), Q(1, 2)),
    ]


def verify_affine(piece, bins, demands, *, rows=None):
    u, v = potentials(piece)
    region = (Q(0), Q(1080)) if piece == 'left' else (Q(1080), Q(3240))
    bin_forms = {c: [Q(0), Q(0)] for c in C.CAPACITIES}
    item_forms = {w: [Q(0), Q(0)] for w in C.WIDTHS}
    idle_forms = {}
    for capacity, counts, y0, y1 in (affine_rows(piece) if rows is None else rows):
        C.need(all(type(n) is int and n >= 0 for n in counts), 'whole integer widths')
        remainder = capacity - sum(w * n for w, n in zip(C.WIDTHS, counts))
        C.need(remainder >= 0, 'affine pattern capacity')
        C.need(all(y0 + y1 * x >= 0 for x in region), 'nonnegative affine endpoints')
        # Affineness implies endpoint nonnegativity on every real x in the segment.
        slack = C.vec((1, C.h(remainder)), (-1, u[capacity]),
                      *((-n, v[w]) for w, n in zip(C.WIDTHS, counts)))
        C.need(not slack, 'affine complementary slackness identity')
        bin_forms[capacity][0] += y0
        bin_forms[capacity][1] += y1
        for w, n in zip(C.WIDTHS, counts):
            item_forms[w][0] += n * y0
            item_forms[w][1] += n * y1
        if remainder:
            idle_forms.setdefault(remainder, [Q(0), Q(0)])
            idle_forms[remainder][0] += y0
            idle_forms[remainder][1] += y1
    C.need(bin_forms == {c: [Q(n), Q(0)] for c, n in bins.items()}, 'affine bin polynomial coefficients')
    C.need(item_forms == {w: [Q(n), Q(int(w == 7) - int(w == 8))] for w, n in demands.items()}, 'affine item polynomial coefficients')
    return {'x_interval': [str(x) for x in region],
        'all_coefficients_exact': True, 'all_multiplicities_nonnegative': True,
        'idle_coefficients_y0_plus_x_y1': {r: [str(x) for x in form] for r, form in idle_forms.items()},
        'scope': 'Real multiplicities; integral helper patterns; no chronology or family allocation.'}


def controls(bins, demands, divided):
    out = []

    def rejects(name, callback):
        try:
            callback()
        except ValueError:
            out.append(name)
        else:
            raise ValueError('broad control was accepted: ' + name)

    rejects('factoring_nonzero_rank_mass', lambda: normalized_enclosure(C.h(1), divided))
    rejects('raised_zero_mass_capacity8_dual', lambda: verify_dual('middle', divided, perturb=True))
    bad_bins = dict(bins)
    bad_bins[48] -= 1
    rejects('one_missing_capacity48_bin', lambda: verify_affine('right', bad_bins, demands))
    bad_rows = affine_rows('left')
    c, nn, y0, y1 = bad_rows[3]
    bad_rows[3] = (c, nn, y0 + 1, y1)
    rejects('one_extra_affine_pattern', lambda: verify_affine('left', bins, demands, rows=bad_rows))
    bad_rows = affine_rows('right')
    c, nn, y0, y1 = bad_rows[-1]
    bad_rows[-1] = (c, nn, y0 - 1, y1)
    rejects('negative_endpoint_multiplicity', lambda: verify_affine('right', bins, demands, rows=bad_rows))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    bins, demands, _, _ = C.source_accounting(args.source)
    divided = divided_difference_bounds()
    result = {'status': 'PASS_INDEPENDENT_BROAD_DUAL_AND_AFFINE_REVIEW',
        'k_interval': [str(LO), str(HI)],
        'duals': {piece: verify_dual(piece, divided) for piece in ('left', 'middle', 'right')},
        'affine_primal': {piece: verify_affine(piece, bins, demands) for piece in ('left', 'right')},
        'controls': controls(bins, demands, divided)}
    if args.output:
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
