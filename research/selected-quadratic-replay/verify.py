"""Check source binding, state conversion and the complete selected result."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pins import authenticate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    inputs = authenticate()
    import binding
    import checks
    import state_adapter as A
    import verify_source
    bound = binding.check()
    controls = checks.run()
    verify_source.main([])
    source = HERE.parents[1] / binding.SOURCE
    result = {'source_inputs': inputs, 'derived_files': bound, 'controls': controls,
              'source_scientific_sha256': sha256((source / 'RESULT.json').read_bytes()).hexdigest(),
              'source_word_sha256': sha256((source / 'WORD.json.gz').read_bytes()).hexdigest(),
              'state_evaluations': dict(A.COUNTS), 'cache': A.signature.cache_info()._asdict()}
    path = HERE / 'RESULT.json'
    if args.record:
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    elif result != json.loads(path.read_bytes()):
        raise ValueError('Selected quadratic replay receipt changed')
    print('PASS_COMPLETE_SELECTED_QUADRATIC_REPLAY')


if __name__ == '__main__':
    main()
