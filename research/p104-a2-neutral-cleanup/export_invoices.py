"""Export complete source-bound invoices for the shared concave-order preflight.

Prepared for zxv with substantial OpenAI Codex assistance; Apache-2.0.
This is receipt extraction, not a circuit or supplier-admission verifier.
"""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
CONTRACT = {
    'model': 'mixed-target-unnormalized-power-v1',
    'rank_semantics': 'H_r costs r^(1-C); debit surrendered productive fields',
    'ambient_rank': 145,
    'boundary': 'Complete PR5627-derived p16/a7 caller before the same mixed-target compiler',
}


def main():
    output = HERE/'invoices'
    output.mkdir(exist_ok=True)
    for name, source in (
        ('pr5644', HERE/'inputs/pr5644/RESULT.json'),
        ('common', HERE/'FULL-RESULT.json'),
    ):
        cost = json.loads(source.read_bytes())['complete_cost']
        invoice = {
            'schema': 'integer-mult-recursive-invoice/v1',
            'contract': CONTRACT,
            'paid': cost['paid'],
            'targets': cost['targets'],
        }
        (output/(name+'.json')).write_text(json.dumps(invoice, indent=2)+'\n')
    print('EXPORTED_COMPLETE_RECURSIVE_INVOICES')


if __name__ == '__main__':
    main()
