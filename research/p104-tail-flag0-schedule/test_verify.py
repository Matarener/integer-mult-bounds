#!/usr/bin/env python3
"""The tail event number is the citation this check looks for."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_tail_flag0_schedule", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if not verify.cites_tail("event 5759"):
        raise SystemExit("the event number was missed")
    if verify.cites_tail("416 reads on 104 targets"):
        raise SystemExit("an unrelated sentence was treated as the tail")
    print("PASS_P104_TAIL_FLAG0_SCHEDULE_TESTS groups=1")


if __name__ == "__main__":
    main()
