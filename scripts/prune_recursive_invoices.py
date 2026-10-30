#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Keep the exact concave-order frontier of a finite invoice pool.

Classical Pareto reduction of the hinge coordinates from
compare_recursive_invoices.py. Prepared for Ali Romman with OpenAI Codex.
"""
import argparse
import json
import sys
from compare_recursive_invoices import compare_invoices, load_invoice, require, validate_invoice


def validate_pool(invoices):
    require(type(invoices) is list and 1 <= len(invoices) <= 256, "Use 1..256 invoices")
    clean = [validate_invoice(v) for v in invoices]
    require(all(v['contract'] == clean[0]['contract'] for v in clean), "Contracts differ")
    knots = sorted({int(r) for v in clean for side in ('paid', 'targets') for r in v[side]})
    require(len(knots) <= 8192, "At most 8192 union rank knots")
    return clean, knots


def coordinates(invoice, knots):
    """Use a sparse sweep; do not allocate an ambient-rank array."""
    net = {int(r): invoice['paid'].get(r, 0) - invoice['targets'].get(r, 0)
           for side in ('paid', 'targets') for r in invoice[side]}
    count, mass, out = sum(net.values()), 0, []
    for r in knots:
        n = net.get(r, 0)
        count -= n
        mass += r * n
        out.append(mass + r * count)
    return tuple(out)


def frontier(invoices):
    invoices, knots = validate_pool(invoices)
    vectors = [coordinates(v, knots) for v in invoices]
    representatives = {}
    for i, vector in enumerate(vectors):
        representatives.setdefault(vector, i)
    reps = list(representatives.values())
    kept = [i for i in reps if not any(j != i and all(a <= b for a, b in zip(vectors[j], vectors[i]))
                                     for j in reps)]
    discarded = []
    for i, vector in enumerate(vectors):
        if i in kept:
            continue
        j = next(j for j in kept if all(a <= b for a, b in zip(vectors[j], vector)))
        proof = compare_invoices(invoices[i], invoices[j])
        discarded.append({'candidate': i, 'retained': j, 'relation': proof['classification'],
                          'hinges': proof['hinges']})
    result = {'schema': 'recursive-invoice-frontier/v1', 'retained': kept, 'discarded': discarded,
              'candidates': len(invoices), 'union_knots': len(knots),
              'scope': 'Declared complete invoices only; no physical compatibility or kappa admission'}
    verify_frontier(invoices, result)
    return result


def verify_frontier(invoices, report):
    """Check coverage and witnesses with the existing pairwise comparator."""
    invoices, knots = validate_pool(invoices)
    require(type(report) is dict and report.get('schema') == 'recursive-invoice-frontier/v1',
            "Invalid frontier report")
    require(type(report.get('candidates')) is int and report['candidates'] == len(invoices)
            and type(report.get('union_knots')) is int and report['union_knots'] == len(knots),
            "Changed pool size or rank count")
    kept, discarded = report.get('retained'), report.get('discarded')
    require(type(kept) is list and kept and type(discarded) is list, "Invalid frontier partition")
    require(all(type(i) is int and 0 <= i < len(invoices) for i in kept), "Invalid retained index")
    require(len(kept) == len(set(kept)), "Duplicate retained index")
    seen = set(kept)
    for row in discarded:
        require(type(row) is dict, "Invalid discarded row")
        i, j = row.get('candidate'), row.get('retained')
        require(type(i) is int and 0 <= i < len(invoices) and i not in seen,
                "Duplicate or invalid discarded index")
        require(type(j) is int and j in kept, "Witness must be retained")
        proof = compare_invoices(invoices[i], invoices[j])
        require(proof['classification'] in ('equal', 'uniformly_better'), "Invalid dominance claim")
        require(row.get('relation') == proof['classification'] and row.get('hinges') == proof['hinges'],
                "Changed dominance evidence")
        seen.add(i)
    require(seen == set(range(len(invoices))), "Incomplete candidate coverage")
    for offset, i in enumerate(kept):
        for j in kept[offset + 1:]:
            require(compare_invoices(invoices[i], invoices[j])['classification'] == 'inconclusive',
                    "Retained candidates must be distinct and incomparable")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('invoices', nargs='+')
    args = parser.parse_args(argv)
    try:
        require(len(args.invoices) <= 256, "At most 256 invoices")
        loaded = [load_invoice(p) for p in args.invoices]
        report = frontier([v for v, _ in loaded])
        report['inputs'] = [e for _, e in loaded]
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
