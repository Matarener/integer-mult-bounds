"""Replay exact compact-program execution. Nick Petalas. Apache-2.0."""

import json
from pathlib import Path
import sys


def main():
    package = Path(__file__).resolve().parent
    sys.path.insert(0, str(package))
    from checks import collect
    result = collect(package)
    expected = json.loads((package / 'RESULT.json').read_text())
    if result != expected:
        raise ValueError('scientific receipt differs')
    print(json.dumps(result, sort_keys=True))
    print('PASS_COMPACT_TWIDDLE_TAPES')


if __name__ == '__main__':
    main()
