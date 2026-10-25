"""Exact finite controls for the phase, norm and complete cost arguments."""
from fractions import Fraction
import importlib.util
from chirp_sources import active, require


def run():
    cases = 0
    for p in range(16, 129):
        for ell in range(2, p):
            L = ell+1
            guard = (L-1).bit_length()+4
            Q = p+guard
            require(16 <= Q <= 2*p and ell+1 <= Q, "phase setup and operand width")
            require(Fraction(4*L, 1 << guard) <= Fraction(1, 4), "fine phase accumulation")
            cases += 1
    require(Fraction(7, 4)**2 > 2 and Fraction(7, 4)+Fraction(1, 4) == 2,
            "strict final phase error below two ulps")
    require(32*1000**2 < 2**26, "strict .001 ring margin at p-A thirteen")
    require(Fraction(3, 5)+Fraction(1, 1000) == Fraction(601, 1000), "chirp norm margin")
    require(3*4+2+2*4 == 22, "complete cyclic, kernel and endpoint phase bill")
    path = active().ring_package / "ring_check_budget.py"
    spec = importlib.util.spec_from_file_location("chirp_inherited_budget", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    inherited = module.run()
    power = Fraction(8, 5)-Fraction(997, 1000)
    phi = Fraction(inherited["fourier_power"])
    require(power == Fraction(603, 1000) < phi == Fraction(99827619697, 100000000000),
            "actual complete Fourier allowance")
    require(Fraction(inherited["primitive_power"]) < phi,
            "primitive rate does not replace the complete Fourier bound")
    return {"finite_precision_cases": cases, "phase_guard": "ceil(log2(ell+1))+4",
            "phase_error_ulps": "<2", "middle_error_ulps": "<4*sqrt(2)*M+22",
            "output_norm": "<.601", "online_power": str(power), "fourier_power": str(phi),
            "scope": "Finite controls; PROOF.md supplies the quantified argument and inherited premises."}
