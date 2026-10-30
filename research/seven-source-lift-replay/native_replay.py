"""Compile and fully replay the frozen second native enumeration.

Requires a C++17 compiler. Generic Python-only checks are separate; the
dedicated native workflow runs this complete command, with no skipped stage.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

P = Path(__file__).resolve().parent
SOURCE = '225e2a8fe167864254d3f0bdc8be28820a14886ceb7e07f711d8aa8454d7d658'
EXPECTED = 'f9e50d14b7c5f0d802af9dd15df44829dbc086d358642594df7ed786e144a2f7'


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def run(package):
    source = (package/'census.cpp').read_bytes()
    expected = (package/'NATIVE.json').read_bytes()
    need(hashlib.sha256(source).hexdigest() == SOURCE, 'native source authentication')
    need(hashlib.sha256(expected).hexdigest() == EXPECTED, 'frozen native receipt authentication')
    compiler = shutil.which('c++')
    need(compiler is not None, 'C++17 compiler c++ is required; no census stage is skipped')
    with tempfile.TemporaryDirectory(prefix='seven-source-native-') as directory:
        binary = Path(directory)/'census'
        command = [compiler, '-O3', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                   '-pedantic-errors', str(package/'census.cpp'), '-o', str(binary)]
        built = subprocess.run(command, capture_output=True, timeout=60)
        need(built.returncode == 0, 'native compilation failed: '+built.stderr.decode(errors='replace'))
        result = subprocess.run([str(binary)], capture_output=True, timeout=120)
        need(result.returncode == 0, 'full native replay failed: '+result.stderr.decode(errors='replace'))
        need(result.stdout == expected, 'complete native output differs from frozen receipt')
    need((package/'census.cpp').read_bytes() == source and (package/'NATIVE.json').read_bytes() == expected,
         'full replay changed its committed source or receipt')
    record = json.loads(expected)
    need(record['quick_only'] is False, 'quick-only receipt is not a full enumeration')
    return {'status': 'PASS_FULL_SECOND_NATIVE_L20_REPLAY_NO_NEW_KAPPA',
            'source_sha256': SOURCE, 'native_result_sha256': EXPECTED,
            'canonical_five_cores': record['five_source']['canonical_words'],
            'six_source_candidates': record['six_source_candidates']['insertions'],
            'full56_canonical_unique': record['six_source_candidates']['full56_canonical_unique'],
            'seven_source_candidates': record['seven_source_candidates']['raw_lifts'],
            'full98_candidates': record['seven_source_candidates']['full98_lifts'],
            'filtered_candidate_maximum': record['seven_source_candidates']['candidate_lift_max_coverage'],
            'scope': 'Complete frozen C++17 five-to-six-to-seven candidate replay; filtered maximum is not a global maximum over all seven-source words. No L16/L18 native census or complete218-call theorem recertification.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root', type=Path, default=P)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run(args.package_root.resolve())
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'])
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
