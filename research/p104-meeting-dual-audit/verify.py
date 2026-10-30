"""Replay the exact paid-meeting cut audit without archived source imports.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit as A
import controls
from evidence import HERE, authenticate, load, need


def difference(new, old):
    result = Counter(new)
    result.subtract(old)
    return dict(sorted((rank, n) for rank, n in result.items() if n))


def invoice_document(price):
    return {'schema': 'integer-mult-recursive-invoice/v1', 'contract': {
        'model': 'mixed-target-unnormalized-power-v1',
        'rank_semantics': 'H_r costs r^(1-C); debit surrendered productive fields',
        'ambient_rank': 145,
        'boundary': 'Complete p16/a7 moment gate; compiler completion parameters are excluded'},
        'paid': price['paid'], 'targets': price['targets']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    data = load()
    oracle = controls.vector_oracle()
    counterexample = controls.commutation_counterexample()
    word, witness, snapshots = A.rebuild(data['source'], data['plan'])
    need(word == data['word'] and witness == data['witness'], 'Exact complete word and witness')
    local, before = A.chronology(word), A.chronology(data['source'])
    columns = A.all_columns(word)
    price = A.invoice(local, data['controller'])
    source_price = A.invoice(before, data['controller'])
    expected = data['result']['complete_cost']
    for label, actual_price, reference in (
        ('new', price, expected), ('source', source_price, data['source_result']['complete_cost'])
    ):
        for field in actual_price:
            actual = actual_price[field]
            if isinstance(actual, dict):
                actual = {str(k): v for k, v in actual.items()}
            need(actual == reference[field], 'Exact declared complete bill: ' + label + ' ' + field)
    need(local['scalar'] == expected['nonrecursive']['local_scalar'], 'Exact scalar allowance')
    routes = (sum(local['paid'].values()) + 2 * sum(local['helpers'].values())
              + 208 + 4 * 104 + 4 * local['owned_lifetimes']) * 1000
    need(routes == expected['nonrecursive']['local_routes']
         and routes + local['scalar'] < 10**7, 'Declared local ordinary-work allowance')
    paid_delta = difference(local['paid'], before['paid'])
    target_delta = difference(local['helpers'], before['helpers'])
    need(paid_delta == {1: 35, 2: -5, 3: -3, 5: 16, 6: -16}
         and target_delta == {1: 23, 8: 23, 9: -23}, 'All charged split deltas')
    negative = controls.source_controls(data, snapshots, local)
    result = {
        'source_commit': '8483f9a679d06c1e270141dbc686a7e76e7a7522',
        'archive_inventory': data['archive_inventory'],
        'controller_sha256': data['controller_sha256'],
        'source_word_sha256': A.digest(data['source']), 'word_sha256': A.digest(word),
        'meetings': len(witness['meetings']),
        'cuts': sum(len(m['steps']) for m in witness['meetings']),
        'added_paid_queries': sum(m['added_queries'] for m in witness['meetings']),
        'frame105': next(m for m in witness['meetings'] if m['frame'] == 105),
        'cut_certificate_sha256': A.digest(witness),
        'columns': columns, 'local': local, 'local_routes': routes,
        'paid_delta': paid_delta, 'target_delta': target_delta, 'invoice': price,
        'source_invoice': source_price,
        'vector_oracle': oracle, 'commutation_counterexample': counterexample,
        'negative_controls': negative,
        'scope': 'Exact scalar cuts, all columns, local chronology and declared complete invoice; not native phase, compiler or outer admission',
    }
    for name, document in (
        ('RESULT.json', result), ('INVOICE.json', invoice_document(price)),
        ('SOURCE-INVOICE.json', invoice_document(source_price))
    ):
        encoded = json.dumps(document, sort_keys=True, indent=2) + '\n'
        path = HERE / name
        if args.record:
            path.write_text(encoded)
        else:
            need(path.read_text() == encoded, 'Exact audit receipt: ' + name)
    print('PASS_P104_MEETING_DUAL_AUDIT', json.dumps({
        'cuts': result['cuts'], 'columns': columns['columns'],
        'paid_calls': price['paid_calls'], 'targets': price['productive_fields'],
        'negative_controls': len(negative), 'dense_oracle_programs': oracle['programs']}))


if __name__ == '__main__':
    main()
