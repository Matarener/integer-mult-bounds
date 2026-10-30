#!/usr/bin/env python3
"""A later add would change the coefficient. The sample does."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_channel_correction_absent", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    program = [
        ["add", "Y34", "X0", "1/2", []],
        ["add", "Y34", "X0", "-1/2", []],
    ]
    trace = verify.coefficient_trace(program, ["X0", "Y34"])
    if [str(value) for _index, value in trace] != ["1/2"]:
        raise SystemExit("a cancelling add was kept in the trace")
    print("PASS_P104_CHANNEL_CORRECTION_ABSENT_TESTS groups=1")


if __name__ == "__main__":
    main()
