#!/usr/bin/env python3
"""Read-only by default; --write regenerates both shipped arithmetic results."""
from pathlib import Path
import argparse
import subprocess
import sys

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    here=Path(__file__).resolve().parent
    flags=['-B'] if __debug__ else ['-O','-B']
    tail=['--write'] if args.write else []
    for script in ('check_moment.py','check_windows.py'):
        subprocess.run([sys.executable,*flags,str(here/script),*tail],check=True)
    print('PASS_FIVE_TERMINAL_MOMENT_AND_FIXED_WINDOW_OBSTRUCTION no_new_kappa')

if __name__=='__main__':
    main()
