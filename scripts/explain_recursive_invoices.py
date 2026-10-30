#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Show exact capped-linear tariff witnesses for a declared invoice comparison.

The method is the classical concave order used by compare_recursive_invoices
and mightyOil's t16-moment-order-audit. No new theorem is claimed.
Prepared for aliromman with OpenAI Codex assistance.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from compare_recursive_invoices import compare_invoices, load_invoice
finally:
    sys.path.pop(0)


def tariff_cost(invoice, cap):
    return sum(min(int(r), cap) * n for r, n in invoice['paid'].items()) - sum(
        min(int(r), cap) * n for r, n in invoice['targets'].items())


def explain_invoices(old, new):
    report = compare_invoices(old, new)
    witnesses = {}
    for direction, choose, sign in (('negative_change', min, -1), ('positive_change', max, 1)):
        hinge = choose(report['hinges'], key=lambda row: row['value'])
        if sign * hinge['value'] <= 0:
            continue
        cap = hinge['rank']
        before, after = tariff_cost(old, cap), tariff_cost(new, cap)
        witnesses[direction] = {'tariff': 'min(r, cap)', 'cap': cap,
                                'old_paid_minus_targets': before, 'new_paid_minus_targets': after,
                                'new_minus_old': after - before}
    report['concave_tariff_witnesses'] = witnesses
    report['witness_scope'] = ('These are increasing concave tariffs. Opposite signs do not prove '
                               'a crossing for powers r^t, a legal circuit or a kappa improvement.')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('old'); parser.add_argument('new')
    args = parser.parse_args(argv)
    try:
        old, old_pin = load_invoice(args.old)
        new, new_pin = load_invoice(args.new)
        report = explain_invoices(old, new)
        report['inputs'] = {'old': old_pin, 'new': new_pin}
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(json.dumps({'status': 'INVALID_RECURSIVE_INVOICE', 'error': str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
