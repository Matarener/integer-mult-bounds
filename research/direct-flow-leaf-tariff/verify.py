#!/usr/bin/env python3
"""Exact finite controls for the new leaf moment identities; no asymptotic replay."""

import ast
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
MAX_DEPTH = 4
P = {1: 37305, 2: 10695, 3: 3360, 4: 1530, 5: 300,
     8: 1464, 16: 448, 32: 448, 48: 448}
M = 121


def need(condition, message):
    if not condition:
        raise ValueError(message)


def check_digest(data, expected):
    need(sha256(data).hexdigest() == expected, "source SHA256 mismatch")


def authenticate():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    need(len(manifest["files"]) <= 10, "source inventory bound")
    checked = 0
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        source = ROOT / row["path"]
        need(source.stat().st_size <= 1048576, "source size bound")
        data = source.read_bytes()
        check_digest(data, row["sha256"])
        checked += 1
        if row["path"].endswith("verify.py"):
            values = {}
            for node in ast.parse(data).body:
                if isinstance(node, ast.Assign) and len(node.targets) == 1:
                    target = node.targets[0]
                    if isinstance(target, ast.Name) and target.id in {"P", "M"}:
                        values[target.id] = ast.literal_eval(node.value)
            need(values == {"P": P, "M": M}, "inventory binding")
    need(checked == 2, "exactly two live source bindings")
    return checked


def prefix_table(depth, cap):
    """Bounded DP for the moment factorization, retaining each prefix barrier."""
    need(0 <= depth <= MAX_DEPTH and cap >= 1, "prefix domain")
    table = {1: 1}
    for _ in range(depth):
        following = defaultdict(int)
        for rho, count in table.items():
            for rank, multiplicity in P.items():
                if rho * rank <= cap:
                    following[rho * rank] += count * multiplicity
        table = dict(following)
    return table


def ordered_leaves(depth, n):
    """Independent ordered-word enumeration, truncating only the final prefix."""
    need(0 <= depth <= MAX_DEPTH and n >= M, "leaf domain")
    leaves = defaultdict(int)
    accepted = 0
    for word in product(tuple(P), repeat=depth):
        rho, count = 1, 1
        for rank in word:
            rho *= rank
            count *= P[rank]
        if M * rho > n:
            continue
        accepted += 1
        for rank, multiplicity in P.items():
            leaves[rho * rank] += count * multiplicity
    need(accepted > 0, "all-ones prefix exists")
    return dict(leaves), accepted


def partition(exponent):
    return sum(Fraction(count) * Fraction(rank) ** exponent
               for rank, count in P.items())


def moment(histogram, exponent):
    return sum(Fraction(count) * Fraction(rank) ** exponent
               for rank, count in histogram.items())


def normalized(leaves, n, t, shift):
    return moment(leaves, t + shift) / (Fraction(n) ** shift * moment(leaves, t))


def tilted_j(prefix, depth, n, alpha, tilt):
    # exp(-tilt*Y)=(M*rho/n)^tilt; all exponents here are integral.
    return (Fraction(M, n) ** tilt * moment(prefix, alpha + tilt)
            / partition(alpha) ** depth)


def finite_checks():
    fixtures = identities = words = tilt_identities = second_changes = 0
    for depth in range(MAX_DEPTH + 1):
        start = M * 5 ** depth
        for n in (start, 2 * start, 5 * start - 1):
            prefix = prefix_table(depth, n // M)
            leaves, accepted = ordered_leaves(depth, n)
            fixtures += 1
            words += accepted
            for t in (-1, 0, 1):
                for shift in (-2, -1, 0, 1, 2):
                    observed = normalized(leaves, n, t, shift)
                    terminal = partition(t + shift) / partition(t)
                    factor = (Fraction(n) ** (-shift) * terminal
                              * moment(prefix, t + shift) / moment(prefix, t))
                    need(observed == factor, "finite leaf factorization")
                    identities += 1
                    for alpha in (0, 1):
                        lam = t - alpha
                        ratio = (Fraction(M) ** (-shift) * terminal
                                 * tilted_j(prefix, depth, n, alpha, lam + shift)
                                 / tilted_j(prefix, depth, n, alpha, lam))
                        need(observed == ratio, "exact tilted quotient")
                        tilt_identities += 1
            for alpha in (0, 1):
                for beta in range(-3, 4):
                    v = beta - alpha
                    survival = moment(leaves, beta) / partition(beta) ** (depth + 1)
                    changed = ((partition(beta) / partition(alpha)) ** depth
                               * Fraction(M, n) ** v * survival)
                    need(changed == tilted_j(prefix, depth, n, alpha, v),
                         "second exact change of measure")
                    second_changes += 1
    return fixtures, identities, tilt_identities, second_changes, words


def rejection_controls():
    depth, n, t, shift, alpha = 2, 2 * M * 25, 1, 1, 0
    prefix = prefix_table(depth, n // M)
    leaves, _ = ordered_leaves(depth, n)
    observed = normalized(leaves, n, t, shift)
    terminal = partition(t + shift) / partition(t)
    lam = t - alpha
    no_terminal = observed / terminal
    extra_truncation = {rank: c for rank, c in leaves.items() if M * rank <= n}
    reversed_power = normalized(leaves, n, t, -shift)
    dropped_offset = normalized(leaves, M * 25, t, shift)
    wrong_tilt = (Fraction(M) ** (-shift) * terminal
                  * tilted_j(prefix, depth, n, alpha, lam - shift)
                  / tilted_j(prefix, depth, n, alpha, lam))
    variants = (no_terminal, normalized(extra_truncation, n, t, shift),
                reversed_power, dropped_offset, wrong_tilt)
    for variant in variants:
        need(variant != observed, "semantic mutation must be distinguished")
    rejected = len(variants)
    for depth_arg, cap_arg in ((MAX_DEPTH + 1, 1), (0, 0)):
        try:
            prefix_table(depth_arg, cap_arg)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid domain was accepted")
    try:
        check_digest(b"changed", sha256(b"original").hexdigest())
    except ValueError:
        rejected += 1
    else:
        raise ValueError("corrupted source was accepted")
    return rejected


def main():
    sources = authenticate()
    fixtures, identities, tilts, second_changes, words = finite_checks()
    controls = rejection_controls()
    print(json.dumps({
        "status": "PASS_DIRECT_FLOW_LEAF_TARIFF_FINITE_IDENTITIES",
        "source_bindings": sources,
        "finite_fixtures": fixtures,
        "ordered_prefixes_accepted_across_fixtures": words,
        "moment_identities": identities,
        "tilted_quotient_identities": tilts,
        "second_measure_change_identities": second_changes,
        "rejecting_controls": controls,
        "scope": "Exact finite identities only; asymptotics are the written proof.",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
