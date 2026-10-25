"""Check exact committed evidence. Nick Petalas, Apache-2.0."""

from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checks import science


def main():
    actual = science()
    expected = json.loads(Path(__file__).with_name('RESULT.json').read_text())
    if actual != expected:
        raise ValueError('committed RESULT.json differs from actual replay')
    print(json.dumps(actual, sort_keys=True))


if __name__ == '__main__':
    main()
