# SPDX-License-Identifier: Apache-2.0
"""Execute source-closed physical boundary checks in a private runtime."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from prepare import prepare


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="t74-outer-boundary-") as temporary:
        controller = prepare(Path(temporary) / "runtime")
        command = [
            sys.executable,
            "-I",
            "-Werror",
            "-B",
            str(HERE / "checks.py"),
            str(controller),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=300)
        if completed.returncode or completed.stderr:
            raise ValueError(
                "physical boundary replay: " + completed.stdout + completed.stderr
            )
        receipt = json.loads(completed.stdout)
    if args.write_receipt:
        args.write_receipt.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        )
    elif json.loads((HERE / "RESULT.json").read_text()) != receipt:
        raise ValueError("exact physical boundary receipt")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
