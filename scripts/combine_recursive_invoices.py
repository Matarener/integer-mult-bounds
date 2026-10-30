#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Add declared invoices with positive integer multiplicities.

Write the compatible invoice to stdout and its source receipt to stderr.
This is arithmetic composition, not proof that physical callers compose.
Prepared for aliromman with OpenAI Codex assistance. The invoice schema and
accounting retain the compare_recursive_invoices predecessor credits.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from compare_recursive_invoices import load_invoice, validate_invoice, require, MAX_COUNT
finally:
    sys.path.pop(0)


def combine_invoices(terms):
    require(isinstance(terms, list) and 1 <= len(terms) <= 128, 'provide 1..128 invoice terms')
    combined = None
    for count, raw in terms:
        require(type(count) is int and 1 <= count <= MAX_COUNT, 'multiplicity must be an integer in 1..10^60')
        invoice = validate_invoice(raw)
        if combined is None:
            combined = {**invoice, 'paid': {}, 'targets': {}}
        require(combined['contract'] == invoice['contract'], 'declared invoice contracts differ')
        for side in ('paid', 'targets'):
            for rank, amount in invoice[side].items():
                combined[side][rank] = combined[side].get(rank, 0) + count * amount
    return validate_invoice(combined, 'combined invoice')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--term', nargs=2, action='append', required=True, metavar=('COUNT', 'FILE'))
    args = parser.parse_args(argv)
    try:
        require(len(args.term) <= 128, 'provide at most 128 invoice terms')
        terms, evidence = [], []
        for count_text, path in args.term:
            require(re.fullmatch(r'[1-9][0-9]{0,60}', count_text) is not None, 'use a positive decimal multiplicity')
            count = int(count_text)
            require(count <= MAX_COUNT, 'multiplicity exceeds 10^60')
            invoice, pin = load_invoice(path)
            terms.append((count, invoice)); evidence.append({'multiplicity': count, 'input': pin})
        result = combine_invoices(terms)
        payload = (json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + '\n').encode('utf-8')
        receipt = {'schema': 'integer-mult-invoice-composition-receipt/v1', 'terms': evidence,
                   'output_sha256': sha256(payload).hexdigest(), 'output_bytes': len(payload),
                   'scope': 'Exact declared histogram sum. Physical composition, ownership, '
                            'shared costs, extraction and kappa are not verified.'}
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(json.dumps({'status': 'INVALID_INVOICE_COMBINATION', 'error': str(exc)}), file=sys.stderr)
        return 2
    # Binary output makes the receipt hash independent of platform newline rules.
    sys.stdout.buffer.write(payload)
    sys.stdout.buffer.flush()
    print(json.dumps(receipt, sort_keys=True), file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
