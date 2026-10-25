#!/usr/bin/env python3
"""Normal/optimized exact admission; discovery trials are not theorem evidence.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def need(c, message):
    if not c:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def produce():
    commands = []
    for optimized in (False, True):
        command = [sys.executable, '-B'] + (['-O'] if optimized else []) + ['admit_pairings.py']
        result = subprocess.run(command, cwd=HERE, text=True, capture_output=True, check=False)
        need(result.returncode == 0, 'exact normal/optimized admission\n' + result.stderr)
        commands.append(dict(argv=command, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
    files = ['admit_pairings.py', 'pairing_search.py', 'FULL-STOCK-CERTIFICATES.json', 'PROOF.md']
    for family in ['REPAIRED', 'TWO-SITE']:
        for q in [2, 3]:
            files.append(family + '-Q' + str(q) + '-PROPOSAL.json')
    need(not list(HERE.rglob('__pycache__')), 'no bytecode scratch from producer validation')
    return dict(status='PASS_EXACT_FULL_STOCK_PAIRINGS_NORMAL_AND_OPTIMIZED', no_new_kappa=True,
                commands=commands, producer_sha256=sha(__file__),
                files=[dict(path=p, sha256=sha(HERE / p)) for p in files],
                coverage='All four exact circuit/phase path partitions, independent direct crossed replay, native-rank sums, two-sided signed holonomy inverses, all-straight/edge-omission/SWAP controls.',
                source_semantics='Unchanged complete source caller/all-input/inverse/selected recipe evidence is inherited through its frozen pins, not claimed as freshly executed.',
                discovery='Exact-rank annealed bit-flip proposals stopped at the theoretical n*m objective maximum. Their counts are discovery records, not exhaustive search evidence.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = produce()
    output = HERE / 'VALIDATION.json'
    if args.write:
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(output.read_text()) == result, 'saved exact pairing validation')
    print(result['status'])


if __name__ == '__main__':
    main()
