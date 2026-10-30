"""Exact finite controls for the inequalities in the written universal proof."""

from fractions import Fraction
import importlib.util
from ring_sources import active, require


def ceiling_log(value):
    return (value-1).bit_length()


def run():
    require(3**5 < 2**8, "strict Karatsuba exponent below 8/5")
    plans = 0
    for p in range(2, 129):
        for ell in range(1, p):
            m = ell+1
            s = ceiling_log(12*m+2)+3
            Q = 2*p+2*m+s
            require(16 <= Q <= 8*p and m <= Q, "precision and twiddle admission")
            require(Fraction(12*m+2, 1 << s) <= Fraction(1, 8), "strict-error recovery allowance")
            plans += 1
    twiddles = 0
    for Q in range(16, 257):
        T, J = Q+64, Q+8
        R = Q+ceiling_log(T)+12
        require(R <= 2*Q+18 and 4*J+2 > R, "Machin alternating tail below one R ulp")
        require(20*(J+2)+1 < 20*T, "angle padding")
        require(Fraction(64*T, 1 << (R-Q)) <= Fraction(1, 64), "inward interval width")
        require(Fraction(16, T)**T < Fraction(1, 1 << (Q+12)), "Taylor tail")
        require((1 << (R-Q-12)) <= 2*T, "Taylor tail in R ulps")
        twiddles += 1
    epsilon = Fraction(997, 1000)
    # Bind the full Fourier cost to the authenticated predecessor. Its primitive
    # rate tau differs from the relaxed native rate alpha and the completed
    # Fourier power after the encoded batch cap.
    path = active().fourier_package / "check_fourier.py"
    spec = importlib.util.spec_from_file_location("ring_fourier_budget_source", path)
    inherited = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inherited)
    source = inherited.budget()
    alpha, tau = Fraction(source["alpha"]), Fraction(source["tau"])
    product_power = Fraction(8, 5)-epsilon
    fourier_power = 1-epsilon*(1-alpha)
    require(fourier_power == 1-Fraction(source["saturated_saving"])
            == Fraction(99827619697, 100000000000), "authenticated complete Fourier power")
    require(product_power < tau < alpha < fourier_power < 1,
            "primitive, relaxed native and complete Fourier rates remain distinct")
    require(Fraction(8, 5)-Fraction(1, 40) > 1, "conservative epsilon does not give this allowance")
    # These exact controls distinguish the strict sign of the complete invoice.
    require(Fraction(2, 1)-epsilon > fourier_power,
            "quadratic data products would fail this same Fourier allowance")
    return {"finite_precision_plans": plans, "finite_twiddle_bounds": twiddles,
            "karatsuba_inequality": [3**5, 2**8], "epsilon": str(epsilon),
            "product_power": str(product_power), "primitive_power": str(tau),
            "relaxed_native_power": str(alpha), "fourier_power": str(fourier_power),
            "scope": "Finite exact controls; PROOF.md supplies universal arguments and outer hypotheses."}
