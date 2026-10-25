"""Exact exponent, total normalization and restoration-margin arithmetic."""
from fractions import Fraction as Q
from tensor_sources import require


def run():
    tau, epsilon, rho_u, delta = Q(332353, 332929), Q(997, 1000), Q(2, 1000), Q(1, 10000)
    beta = 1-epsilon*(1-tau)
    phi = Q(99827619697, 100000000000)
    require(beta == Q(41544341, 41616125), "complete full-support batch summation exponent")
    require(phi-beta == Q(36798102513, 33292900000000000) > 0,
            "strict separate routing margin")
    gaussian = max(epsilon+delta, 1-rho_u+delta)
    require(gaussian == Q(9981, 10000) < phi and epsilon+rho_u < 1,
            "Gaussian logarithmic allowance and sublinear total restoration")
    require(1-epsilon == Q(3, 1000) and epsilon+(1-epsilon) == 1,
            "target-axis bit width differs from the concentration exponent")
    require(delta > phi-beta, "Gaussian logarithmic allowance cannot replace the routing gap")
    guards = []
    for D, p, u, A in ((2, 48, 4, 3), (7, 1000, 9, 16), (100, 100000, 16, 1000)):
        j = (32*p-1).bit_length()
        gamma = D*(2*u+j+1)
        E = D*p*p+32+2*D
        threshold = gamma+A+(E-1).bit_length()+8
        error = Q(E, 1 << (threshold-gamma-A))
        require(error <= Q(1, 256) and Q(1, 2)+error < 1,
                "exact sufficient total restored-error guard before narrowing")
        require(gamma != 2*D*u, "old inverse normalization omits actual j and expansion factors")
        guards.append({"D": D, "p": p, "u": u, "A": A, "gamma": gamma,
                       "required_precision": threshold, "error_bound": str(error), "guard_admitted": p >= threshold})
    require(guards[0]["gamma"] == 40 and not guards[0]["guard_admitted"],
            "finite p48 fixture does not inherit the production error theorem")
    require(Q(1, 2)+Q(1, 20**4-1) < Q(21, 38) < Q(3, 5),
            "source-bound expansion norm leaves the chirp entrance margin")
    require(epsilon+rho_u == Q(999, 1000) and epsilon+Q(3, 1000) == 1,
            "sublinear gamma and linear total address width are distinct conditions")
    return {"tau": str(tau), "epsilon": str(epsilon), "rho_u": str(rho_u),
            "axis_width_exponent": str(1-epsilon), "beta": str(beta), "phi": str(phi),
            "routing_gap": str(phi-beta), "gaussian_power": str(gaussian), "guards": guards,
            "scope": "exact arithmetic under the stated source and growth-law premises"}
