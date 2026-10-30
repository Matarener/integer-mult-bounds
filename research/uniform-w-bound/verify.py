#!/usr/bin/env python3
"""Show that dividing by W does not bound the normalized recurrence alone.

The transfer review proves F(e) <= A e^tau when Psi(tau) < 1. The instance
below keeps 1 <= t < m and the factor 1/W, drops Psi(tau) < 1, and the
normalized values exceed sqrt(e).
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
AUDIT = ROOT / "docs/audit.md"
REVIEW = ROOT / "docs/research/community-transfer-review.md"
RECURRENCE = "F(e) <= (1/W) sum_i F(t_i floor(e/m)) + C."
PSI = "Psi(tau)=(1/W)sum_i(t_i/m)^tau<1"
AUDIT_SENTENCE = "The normalization by W is the critical implementation assertion"
MARKER = "PASS_UNIFORM_W_BOUND psi_sq=2 exceeds=true no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_UNIFORM_W_BOUND " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized(width, children, roles, modulus, overhead):
    if width < modulus:
        return Fraction(0)
    arguments = [child * (width // modulus) for child in children]
    require(all(1 <= argument < width for argument in arguments), "a child width did not shrink")
    return sum(normalized(argument, children, roles, modulus, overhead) for argument in arguments) / roles + overhead


def half_psi_square(children, roles):
    """Square of Psi(1/2) when every child width is half the modulus."""
    require(roles > 0, "roles")
    return Fraction(len(children) ** 2, 2 * roles ** 2)


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "docs/audit.md",
        "docs/research/community-transfer-review.md",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    require(RECURRENCE in REVIEW.read_text(encoding="utf-8"), "the normalized recurrence moved")
    require(PSI in REVIEW.read_text(encoding="utf-8"), "the Psi hypothesis moved")
    require(AUDIT_SENTENCE in AUDIT.read_text(encoding="utf-8"), "the normalization sentence moved")
    children = (2, 2, 2, 2)
    roles = 2
    modulus = 4
    overhead = Fraction(1)
    psi_square = half_psi_square(children, roles)
    value = normalized(8, children, roles, modulus, overhead)
    require(psi_square == 2 and value == 3 and value ** 2 > 8, "the equal-role counterexample moved")
    positive_children = (1,)
    positive_psi = Fraction(1, 4) * Fraction(1, 2)
    allowance = overhead / (1 - positive_psi)
    positive = {
        width: normalized(width, positive_children, 4, 4, overhead)
        for width in (4, 16, 64)
    }
    require(positive_psi == Fraction(1, 8) and allowance == Fraction(8, 7), "the strict example moved")
    require(all(item ** 2 <= allowance ** 2 * width for width, item in positive.items()), "the strict bound failed")
    return {
        "counterexample_children": list(children),
        "counterexample_roles": roles,
        "counterexample_modulus": modulus,
        "psi_square": str(psi_square),
        "normalized_at_8": str(value),
        "exceeds_square_root": True,
        "strict_psi": "1/8",
        "strict_allowance": "8/7",
        "strict_holds_through": 64,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
