"""Replay exact sequential headers and compare the committed evidence."""

import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def main():
    import checks
    import machine

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path)
    args = parser.parse_args()
    result = checks.receipt()
    if args.write_result:
        args.write_result.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        expected = json.loads((HERE / 'RESULT.json').read_text())
        machine.require(result == expected, 'committed result mismatch')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
