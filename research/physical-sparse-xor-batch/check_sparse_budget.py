"""Retain the actual ordinary certificate and check finite guard/record charges."""

from fractions import Fraction
import json
import subprocess
import sys

from sparse_sources import exports, require


def run():
    with exports() as roots:
        root = roots["ordinary-rate-export.tar"]
        script = root / "research/retuned-ordinary-coupling/verify.py"
        process = subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B", str(script),
                                  "--suite", "certificate"], cwd=root, capture_output=True, text=True, timeout=60)
        require(process.returncode == 0 and not process.stderr, "actual retained ordinary certificate replay")
        result = json.loads(process.stdout)
        require(result["status"] == "PASS_RETUNED_ORDINARY_CERTIFICATE"
                and result["ordinary_saving"] == "576/332929", "retained ordinary proof point")
    guard_checks = 0
    for p in (2, 3, 4, 5, 17, 255, 256, 257, 1024, 1048577):
        ceiling = (p-1).bit_length()
        G = 4*ceiling+6
        K = G+4*ceiling+10
        each = Fraction(2, 2**G)+Fraction(8*2**G, 2**K)
        require(each <= Fraction(5, 128*p**4), "finite guard coefficient")
        require(p*each <= Fraction(5, 128*p**3), "all listed targets enter the density charge")
        guard_checks += 1
    # Completing the square proves this for all x, not just these samples.
    for b in (Fraction(1, 4), Fraction(1), Fraction(3, 2)):
        for k in (0, 1, 2, 6):
            for x in range(1, 33):
                require(k*x-b*x*x <= Fraction(k*k, 4*b), "uniform polynomial/record absorption")
    return dict(status="PASS_SPARSE_GUARD_AND_RATE", ordinary_saving=result["ordinary_saving"],
                ordinary_exponent="332353/332929", guard_checks=guard_checks,
                coefficient="5/128", paid_swap_width="H", swaps_per_row=12, rotations_per_row=10,
                scope="Inherited ordinary certificate and finite arithmetic controls; all-size sparse refinement is in PROOF.md.")
