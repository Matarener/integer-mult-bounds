"""Run an unchanged complete PR5831 entry point from its authenticated export."""
import json
import runpy
import sys

from source import baseline, require

EXPECTED = {
    'source_result_sha256': 'cc7739703ed23532d187949c8507d09c13ac4c152e07a930f0087cde0d7a3d98',
    'events': 25984, 'coordinates': 799, 'source_controls': 6,
    'guards': {'owned': 22, 'prefix': 26, 'public': 23},
}


def main():
    mode = 'qualify' if not sys.argv[1:] else sys.argv[1].removeprefix('--')
    require(len(sys.argv) <= 2 and mode in ('baseline', 'candidate', 'qualify'), 'Exact replay mode')
    with baseline() as package:
        expected = json.loads((package / 'RESULT.json').read_bytes()) if mode == 'qualify' else EXPECTED
        previous = sys.argv
        try:
            sys.argv = [str(package / 'verify.py'), '--' + mode]
            result = runpy.run_path(sys.argv[0], run_name='__main__')
        finally:
            sys.argv = previous
        require(result['mode'] == mode and result['receipt'] == expected,
                'Complete frozen scientific receipt')


if __name__ == '__main__':
    main()
