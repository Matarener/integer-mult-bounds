#!/usr/bin/env python3
"""Run two independent, source-complete feasibility certificates.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
This bounded replay is not a physical caller or a supplier admission.
"""

from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parent
    flags = ["-I"] + (["-O"] if sys.flags.optimize else []) + ["-Werror", "-B"]
    for component in ("consumer/budget.py", "physical/verify_format.py"):
        completed = subprocess.run(
            [sys.executable, *flags, str(root / component)],
            cwd=root, check=False, timeout=90,
        )
        if completed.returncode:
            raise SystemExit(completed.returncode)
    print("PASS_P104_CALLER_FEASIBILITY: exact conditional budget and finite format; "
          "no physical caller, changed network, complete tariff or all-size admission")


if __name__ == "__main__":
    main()
