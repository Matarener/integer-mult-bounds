"""Run the retained accepted solver variant, or the complete first fold step."""

import argparse
import os
import sys
from pathlib import Path

from runtime import PACKAGE, install

FLAGS = [
    "--flex", "--strip-sym", "--first-hop", "--root-frames-only",
    "--f0", "--f0-wide", "--improve", "0", "--newton", "8",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("baseline", "candidate"))
    parser.add_argument("toolkit", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--whole-fold", action="store_true")
    args = parser.parse_args()
    root = args.toolkit.resolve()
    os.environ["TK_WORK"] = str(args.output.resolve().parent)
    os.environ["TK_PROFILE"] = "6030_772dd10a"
    os.environ["FOLD_TOOLKIT_ROOT"] = str(root)
    os.environ["FOLD_SOLVER_MODE"] = args.mode
    install(root, args.mode)
    if args.whole_fold:
        import fold

        fold.IOB = str(PACKAGE / "iob_entry.py")
        sys.argv = ["fold.py", "6030", str(args.output), "--max", "1"]
        fold.main()
    else:
        import iob2

        iob2.main([
            "6030", str(args.output), "--root", "5", "--strip-regs", "705",
            "--insert", "770:553:+0", "--insert", "770:1047:+0",
            "--relocate", "770:13614:15597", *FLAGS,
        ])


if __name__ == "__main__":
    main()
