"""Replay the source-bound owned-cleanup obstructions; no network or Git needed."""
from pathlib import Path
import argparse
import importlib.util
import json


HERE = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def run():
    windows = module('check_windows')
    producers = module('check_producers')
    lifetimes = module('check_lifetimes')
    exceptional = module('check_738')
    source = (HERE / 'inputs/pr5569-WORD.json.gz').read_bytes()
    control = (HERE / 'inputs/pr5561-WORD.json.gz').read_bytes()
    word = windows.decode(source, windows.SOURCE_SHA256)
    window_result, witnesses = windows.run(source, control)
    producer_receipt = producers.verify(word)
    result = {
        'status': 'PASS_P104_OWNED_CLEANUP_OBSTRUCTIONS',
        'new_bound': False,
        'windows': window_result,
        'producers': producer_receipt,
        'joint_cut': producers.verify_joint_cut(word, producer_receipt),
        'owned738': exceptional.verify(word),
        'producer_controls': producers.controls(word),
        'lifetimes': lifetimes.verify(word),
        'lifetime_controls': lifetimes.mutation_controls(word),
    }
    return result, witnesses


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='author the receipt')
    parser.add_argument('--witnesses', type=Path, help='export all window witnesses')
    args = parser.parse_args()
    result, witnesses = run()
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write:
        (HERE / 'RESULT.json').write_text(encoded, encoding='utf-8', newline='\n')
    elif encoded != (HERE / 'RESULT.json').read_text(encoding='utf-8'):
        raise ValueError('fresh exact result differs from committed receipt')
    if args.witnesses:
        args.witnesses.write_text(json.dumps(witnesses, separators=(',', ':')) + '\n',
                                 encoding='utf-8', newline='\n')
    print(json.dumps({'status': result['status'], 'new_bound': False,
                      'window_cases': result['windows']['event_boundaries_with_helper_owned_pairs'],
                      'tight_local_stars': 7, 'source_rows': 743}))
