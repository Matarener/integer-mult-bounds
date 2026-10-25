"""Serialize the two explicit verification groups within the eight-hook cap."""
from pathlib import Path
import argparse
import subprocess
import sys

HERE = Path(__file__).resolve().parent
GROUPS = {
    'forward': ('family_geometry.py', 'core.py'),
    'terminal': ('terminal_bound.py', 'terminal_independent.py'),
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('group', choices=sorted(GROUPS))
    args = parser.parse_args()
    flags = ['-I', *(['-O'] if sys.flags.optimize else []), '-W', 'error', '-B']
    for name in GROUPS[args.group]:
        subprocess.run([sys.executable, *flags, str(HERE / name)], check=True)
