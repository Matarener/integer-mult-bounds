"""Exact parameter refinement of the admitted PR6030 construction.

Prepared with OpenAI Codex assistance. Apache-2.0.
The unchanged construction is DreamingOfClouds'/Ali Romman's cumulative
P104 work. Pinned interval, compiler and outer sources retain their notices.
This verifies arithmetic; it does not discharge the five framework assumptions.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from types import ModuleType
from typing import Any

HERE = Path(__file__).resolve().parent
KAPPA = Q("0.003125811")
TESTED = Q("0.0031258115")
PREVIOUS = Q("0.003125804")
BIT = Q("0.0034")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def authenticate(root: Path = HERE) -> dict[str, Any]:
    manifest: dict[str, Any] = json.loads((root / "SOURCES.json").read_text())
    for entry in manifest["files"]:
        raw = (root / entry["local"]).read_bytes()
        require(
            sha256(raw).hexdigest() == entry["sha256"],
            "Changed pinned source: " + entry["local"],
        )
    return manifest


def load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, HERE / "vendor" / name)
    require(spec is not None and spec.loader is not None, "Loadable pinned module")
    if spec is None or spec.loader is None:
        raise ValueError(name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parameters(kappa: Q, tested: Q) -> dict[str, Q]:
    require(PREVIOUS <= kappa < tested < BIT, "Strict supported exponent order")
    gap = (tested - kappa) / 7
    return {
        "kappa": kappa,
        "tested_saving": tested,
        "complex_uniform_saving": kappa + 6 * gap,
        "b": kappa + 5 * gap,
        "a": kappa + 4 * gap,
        "q": kappa + 3 * gap,
        "bit_saving": BIT,
        "epsilon": 1 - gap,
        "beta": 1 - 3 * gap,
        "r0": gap / 10,
        "stop": gap,
        "layout": gap,
        "d": gap,
    }


def outer_ledger(module: ModuleType, params: dict[str, Q]) -> dict[str, Any]:
    result: dict[str, Any] = module.ledger(params)
    result["functional_checks"]["actual_new_BIT_stock_sublinear"] = params["beta"] * (
        1 - Q(1, 250)
    )
    require(len(result["strict_checks"]) == 54, "All 54 strict predicates")
    require(len(result["functional_checks"]) == 4, "All four functional predicates")
    require(
        all(
            x > 0
            for group in ("strict_checks", "functional_checks")
            for x in result[group].values()
        ),
        "Positive outer predicates",
    )
    for name in (
        "new_BIT_row_stock_sublinear_in_active_group",
        "actual_new_BIT_stock_sublinear",
    ):
        require(result["functional_checks"][name] < 1, "Sublinear stock: " + name)
    return result


def compiler_threshold(gap: Q, power: int = 1024) -> dict[str, int]:
    require(gap > 0 and gap.numerator == 1, "Positive reciprocal compiler gap")
    step = int(gap.denominator)

    def wins(j: int) -> bool:
        return bool((step * j + 1) ** power < 2**j)

    left, right = 1, 2
    while not wins(right):
        left, right = right, 2 * right
    while right - left > 1:
        middle = (left + right) // 2
        if wins(middle):
            right = middle
        else:
            left = middle
    height = step * right
    require(
        height > 8 * power and wins(right) and not wins(right - 1),
        "Exact sufficient compiler threshold and failing preceding grid point",
    )
    return {
        "H": height,
        "integer_test_exponent": right,
        "gap_denominator": step,
        "logarithm_power": power,
    }


def verify(kappa: Q = KAPPA, tested: Q = TESTED) -> dict[str, Any]:
    manifest = authenticate()
    first, second, outer = (
        load(name) for name in ("intervals.py", "second_intervals.py", "endpoint.py")
    )
    original = json.loads((HERE / "vendor/RESULT.json").read_text())
    base = original["complete_cost"]
    require(Q(base["kappa"]) == PREVIOUS, "PR6030 baseline")
    selected = json.loads((HERE / "vendor/selected-result.json").read_text())
    require(
        sha256((HERE / "vendor/RESULT.json").read_bytes()).hexdigest()
        == selected["source_certificate_sha256"],
        "Selected source certificate binding",
    )
    targets = {int(r): n for r, n in base["targets"].items()}
    paid = {int(r): n for r, n in base["paid"].items()}
    require(
        (sum(targets.values()), sum(paid.values())) == (13444, 66834),
        "Complete inherited invoice counts",
    )
    require(
        sum(r * n for r, n in targets.items()) == 240912
        and sum(r * n for r, n in paid.items()) == 240152,
        "Complete inherited productive and paid rank mass",
    )

    baseline = outer_ledger(outer, parameters(PREVIOUS, Q("0.003125809")))
    for group in ("margins", "strict_checks", "functional_checks"):
        require(
            baseline[group] == {k: Q(v) for k, v in base["outer"][group].items()},
            "Reproduce all baseline outer rows: " + group,
        )

    t, offset, power = 1 - tested, Q(1, 7), 1024
    require(0 < tested <= offset and t + offset >= 1, "Higher-moment domain")
    target, cost = first.moment(targets, t), first.moment(paid, t)
    target2, cost2 = second.moment(targets, tested), second.moment(paid, tested)
    require(
        target[0] > cost[1] and target2[0] > cost2[1],
        "Positive complete signed moment in both exact engines",
    )
    for left, right in ((target, target2), (cost, cost2)):
        require(
            max(left[0], right[0]) <= min(left[1], right[1]),
            "Independent exact interval engines overlap",
        )
    alpha = first.divide(cost, target)
    gamma = first.divide(
        first.moment(paid, t + offset), first.mul(first.power(16, offset), target)
    )
    delta = first.divide(
        (Q(13444 * 17),) * 2, first.mul(first.power(16, tested), target)
    )
    reserve, decay = Q(1, 10**12), Q(125, 128)
    require(
        alpha[1] < 1 - reserve and gamma[1] < decay and delta[1] < decay,
        "All three funded completion and splitting ratios",
    )
    require(decay**128 < Q(1, 16), "Tail decay block")
    normalized = 1 / (1 + power * reserve) + Q(4, 2**32)
    require(
        normalized < 1 and 16**64 < 17**63, "Paid strictification and rank separation"
    )
    eta = first.scale(first.power(145, -power * tested), t)
    require(2 * (16**power) ** 64 <= (145**power) ** 63, "Shifted exit bound")
    require(eta[0] > Q(63, 64) ** power, "Strict compiler complement capacity")
    require(first.power(145, power * tested)[1] < 2**power, "Compiler initial range")

    params = parameters(kappa, tested)
    threshold = compiler_threshold(params["d"])
    ledger = outer_ledger(outer, params)
    ordinary = (1 - Q(1, 250)) * Q(69, 20000) + Q(1, 250) * Q(".0000384599")
    require(
        Q(1, 250) > ordinary > BIT > tested and Q(1, 250) < 1 - ordinary,
        "Ordinary BIT, admission and atom guards",
    )
    root_upper = Q(base["raw_root_interval"][1])
    rejected = (
        first.moment(targets, 1 - root_upper)[1] - first.moment(paid, 1 - root_upper)[0]
    )
    require(rejected < 0, "Fixed-invoice upper crossing control")
    return {
        "status": "PASS_CONDITIONAL_PARAMETER_REFINEMENT",
        "kappa": kappa,
        "tested": tested,
        "previous": PREVIOUS,
        "improvement": kappa - PREVIOUS,
        "relative_gain_percent": 100 * (kappa / PREVIOUS - 1),
        "source_commit": manifest["upstream_commit"],
        "targets": targets,
        "paid": paid,
        "moment_margin": [target[0] - cost[1], target[1] - cost[0]],
        "displayed_margin": first.display((target[0] - cost[1], target[1] - cost[0])),
        "strictification": {
            "alpha": alpha,
            "gamma": gamma,
            "delta": delta,
            "power": power,
            "reserve": reserve,
            "decay": decay,
            "normalized_paid_upper": normalized,
        },
        "compiler": dict(
            **threshold, eta=eta, uniform_saving=params["complex_uniform_saving"]
        ),
        "ordinary_bit_saving": ordinary,
        "outer": ledger,
        "negative_control_margin_upper": rejected,
        "physical_profile_changed": False,
        "scope": "Same five framework assumptions; unchanged physical construction; no novelty or new reviewed record claim",
    }


def encode(value: Any) -> Any:
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true", help="Write the exact certificate"
    )
    args = parser.parse_args()
    result = encode(verify())
    path = HERE / "CERTIFICATE.json"
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(path.read_text()) == result, "Reproduce exact certificate")
    print(result["status"], "kappa=" + result["kappa"])
    print(
        "Two interval engines; funded tails; compiler; 54 strict and four functional checks"
    )


if __name__ == "__main__":
    main()
