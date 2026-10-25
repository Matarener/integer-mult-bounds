"""Exact controls for the quantified short-block proof and complete tile bill."""
from fractions import Fraction as Q
import importlib.util
from math import isqrt
from expansion_sources import active, require


def run():
    cases = 0
    for p in (*range(101, 513), 1000, 4096, 4800, 16384):
        root = isqrt(p)+(isqrt(p)**2 < p)
        largest = isqrt(p-1)
        for alpha in sorted({2, largest, max(2, largest//2)}):
            b, u = alpha*root, alpha*alpha
            require(Q(b*b, u) < Q(5*p, 4), "production radius squared bound")
            require(3*b+3 < 4*p and 4*b+2 < 5*p, "whole short stencil and prefix convolution bound")
            require(Q((2*b+2)**2, u) < 20*p and Q((b+1)**2, u) < 3*p
                    and Q((2*b+1)**2, u) < 12*p, "real Gaussian exponent magnitude controls")
            P, sigma = 32768*p, 4096*p
            guard = (32*(3*b+4)-1).bit_length()
            require(P >= 2*sigma+p+guard+12, "production fine grid covers normalization before extraction")
            require(Q(1, alpha)+Q(alpha, 6*b) < 1 and 3*p > p+12,
                    "Gaussian tail coefficient and final-grid error separation")
            require(2*sigma > 2*80*p and 2*sigma < P-p,
                    "normalized chirp factors and retained fine bits")
            cases += 1
    path = active().ring_package / "ring_check_budget.py"
    spec = importlib.util.spec_from_file_location("expansion_inherited_fourier_budget", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    inherited = module.run()
    phi = Q(inherited["fourier_power"])
    epsilon, delta = Q(997, 1000), Q(1, 10000)
    expansion = epsilon+delta
    require(expansion == Q(9971, 10000) and phi-expansion == Q(117619697, 100000000000),
            "complete expansion arithmetic fits the inherited Fourier allowance")
    return {"production_guard_cases": cases,
            "block_word_calls": "4*n+6*m+8",
            "tile_word_calls": "2*input_capacity+sum_i(4*n_i+6*m_i+8)",
            "tile_online_time": "O((input_capacity+L+b)*p*log2(p+2)^2)",
            "tile_online_space": "O((L+b)*p)", "coefficient_catalogue": "O((L+b)*p)",
            "setup": "polynomial(t,p), retained separately from online payload work",
            "expansion_arithmetic_power": str(expansion), "fourier_power": str(phi),
            "gap": str(phi-expansion), "scope": "finite algebraic controls; quantified claims and inherited premises in PROOF.md"}
