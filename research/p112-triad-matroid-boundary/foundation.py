"""Sequential, source-isolated replay of the inherited and four-term foundation."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMMANDS = (
    ROOT / 'research/p112-five-term-reader-floor/verify.py',
    ROOT / 'research/p112-five-term-reader-floor/independent.py',
    HERE / 'verify.py',
    HERE / 'independent_vvv.py',
    HERE / 'independent_mmm.py',
    HERE / 'check_gauge.py',
    HERE / 'test_controls.py',
)


def main():
    for path in COMMANDS:
        # -B alone still allows old cache reads. Each child gets an empty namespace.
        with tempfile.TemporaryDirectory(prefix='p112-foundation-cache-') as cache:
            argv = [sys.executable, '-I', '-O', '-Werror', '-B',
                    '-X', 'pycache_prefix=' + cache, str(path)]
            subprocess.run(argv, cwd=ROOT, check=True, timeout=90)
    print(json.dumps({'status': 'PASS_SEVEN_FOUNDATION_REPLAYS',
                      'commands': [p.relative_to(ROOT).as_posix() for p in COMMANDS]}))


if __name__ == '__main__':
    main()
