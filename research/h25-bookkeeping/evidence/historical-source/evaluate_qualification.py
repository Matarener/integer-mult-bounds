"""Evaluate the predeclared receipts; never run or select a replacement sample."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--first-pair', action='store_true')
    args = parser.parse_args()
    rules_raw = (HERE / 'control/QUALIFICATION-v4.json').read_bytes()
    rules = json.loads(rules_raw)
    anchor = json.loads((HERE / 'baseline/anchor.json').read_bytes())['science']
    rows = []
    sequence = rules['sequence'][:2] if args.first_pair else rules['sequence']
    for spec in sequence:
        directory = HERE / 'runtime/runs' / spec['label']
        receipt = json.loads((directory / 'receipt.json').read_bytes())
        science = json.loads((directory / 'science/receipt.json').read_bytes())
        if not (receipt['status'] == 'PASS' and receipt['job'] == spec['job'] and
                receipt['stage_sha256'] == rules['stage_sha256'] and receipt['source_bytes_and_modes_unchanged'] and
                science['status'] == 'FULL_NETWORK_COMPLETE_PASS' and science['science'] == anchor):
            raise RuntimeError('Qualified sample source/science/custody differs: ' + spec['label'])
        usage = receipt['usage']
        rows.append({'label': spec['label'], 'arm': 'C' if spec['job'] == 'full-all' else 'B',
                     'wall': receipt['wall_seconds'], 'cpu': usage['user_seconds'] + usage['system_seconds'],
                     'stage_sha256': receipt['stage_sha256'], 'spent_before': receipt['spent_before_seconds']})
    if rows != sorted(rows, key=lambda row: row['spent_before']):
        raise RuntimeError('Predeclared sample order was not preserved')
    metrics = {}
    for metric in ('wall', 'cpu'):
        baseline = [row[metric] for row in rows if row['arm'] == 'B']
        candidate = [row[metric] for row in rows if row['arm'] == 'C']
        b, c = statistics.median(baseline), statistics.median(candidate)
        saving = b - c
        noise = max(max(baseline) - min(baseline), max(candidate) - min(candidate))
        metrics[metric] = {'baseline': baseline, 'candidate': candidate,
                           'baseline_median': b, 'candidate_median': c,
                           'saving': saving, 'reduction_percent': 100 * saving / b,
                           'max_within_arm_range': noise, 'target_pass': c <= 0.85 * b,
                           'noise_pass': saving > noise}
    passed = all(row['target_pass'] and row['noise_pass'] for row in metrics.values())
    result = {'status': ('FIRST_PAIR_CREDIBLE_CONTINUE' if passed else 'FIRST_PAIR_STOP') if args.first_pair else
                       ('COMBINED_15_PERCENT_BOTH_METRICS_AND_NOISE_PASS' if passed else 'COMBINED_TARGET_OR_NOISE_MISS'),
              'qualified_factor': passed and not args.first_pair, 'metrics': metrics, 'samples': rows,
              'rules_sha256': hashlib.sha256(rules_raw).hexdigest(),
              'every_sample_retained': True, 'full_anchor_equal': True,
              'all_new_controls_and_cold_builds_billed': True,
              'publication_and_hosted_validation_remain_separate': True}
    name = 'COMBINED-FIRST-PAIR.json' if args.first_pair else 'COMBINED-GATE.json'
    (HERE / 'validation' / name).write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
