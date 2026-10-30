#!/usr/bin/env python3
"""A one-step phase change fails the operator comparison."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_tail_flag0_restore", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    module = verify.checker()
    base = module.fourier(1)
    bumped = (("phase", 1),) + base
    if not verify.same_operator(module, base, base):
        raise SystemExit("a circuit differed from itself")
    if verify.same_operator(module, bumped, base):
        raise SystemExit("a phase change was accepted")
    print("PASS_P104_TAIL_FLAG0_RESTORE_TESTS groups=1")


if __name__ == "__main__":
    main()
