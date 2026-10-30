#!/usr/bin/env python3
"""Nine coordinate calls fit the three data registers, and two frames have rank two."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("three_data_aux_direct", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if verify.coordinate_eight_possible():
        raise SystemExit("eight coordinate calls were accepted")
    if not any(sum(counts) == 9 and all(counts[register] >= 3 for register in range(3))
               for counts in verify.product(range(10), repeat=4)):
        raise SystemExit("the direct nine-call distribution disappeared")
    combined = tuple(verify.basis_frame(0)[i] + verify.basis_frame(1)[i] for i in range(9))
    if verify.matrix_rank(combined) != 2:
        raise SystemExit("two coordinate frames did not have rank two")
    print("PASS_THREE_DATA_AUX_DIRECT_TESTS groups=1")


if __name__ == "__main__":
    main()
