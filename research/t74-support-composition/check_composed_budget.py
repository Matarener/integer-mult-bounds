"""Finite exact controls for the written composition and fallback inequalities."""

from fractions import Fraction as F
from composed_sources import require


def run():
    alpha, tau, beta = F(99827101, 10**8), F(332353, 332929), F(997, 1000)
    span_slack = 1-beta*F(501, 500)
    require(span_slack == F(503, 500000) and span_slack > F(1, 1024), "strict complete-target span slack")
    require(alpha-tau == F(36908829, 33292900000000) > 0, "root and router exponents remain distinct")
    require(2*tau <= 1+tau, "pay both external suffix swaps")
    cutoffs = 0
    for L in range(10, 129):
        X = 1024*(L+11)
        require(2**(L+22) > (X+1)**2, "retained gap cutoff base inequality")
        require(F(1, 2**(L+11)) < F(1, 4*2**L), "target span at eventual cutoff")
        cutoffs += 1
    return dict(status="PASS_COMPOSED_FINITE_BUDGET", alpha=str(alpha), tau=str(tau),
                target_span_slack=str(span_slack), cutoff_checks=cutoffs,
                scope="Finite rational controls; the universal argument and inherited premises remain in PROOF.md.")
