#!/usr/bin/env python3
"""A missing Lean pair is rejected, and the self-partner gate is the first tail gate."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("hpe_partner_binding", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    pairs = verify.parse_pairs(verify.EXACT.read_text(encoding="utf-8"))
    word, adapters = verify.synthetic(pairs, True)
    if word["tail"][0][1] != word["tail"][0][2]:
        raise SystemExit("the first gate was not a self-partner")
    word["frames"][0] = [0]
    if verify.binding_accepts(word, adapters, pairs):
        raise SystemExit("a frame outside the three pairs was accepted")
    print("PASS_HPE_PARTNER_BINDING_TESTS groups=1")


if __name__ == "__main__":
    main()
