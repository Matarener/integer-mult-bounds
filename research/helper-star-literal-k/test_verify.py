#!/usr/bin/env python3
"""The plain target pair matches its names, and a missing restore leaves the helper dirty."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("helper_star_literal_k", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    plain = [(verify.TARGET, [verify.HELPER0]), (verify.TARGET, [verify.HELPER1])]
    done = verify.finish(plain)
    if verify.helper_mask(done[verify.TARGET]) != verify.named_mask(plain):
        raise SystemExit("the plain pair was rejected")
    star = [(verify.HELPER0, [verify.HELPER1]), (verify.TARGET, [verify.HELPER0])]
    cut = verify.finish(star)
    if cut[verify.HELPER0] == 1 << verify.HELPER0:
        raise SystemExit("the omitted restore left the helper clean")
    print("PASS_HELPER_STAR_LITERAL_K_TESTS groups=1")


if __name__ == "__main__":
    main()
