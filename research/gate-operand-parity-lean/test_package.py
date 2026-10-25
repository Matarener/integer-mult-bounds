"""Negative controls for research/gate-operand-parity-lean/verify.py.

Each control must be rejected for its own reason, so a passing verify run is
not a run of a checker that accepts anything.  Standard library only.
Prepared by Nick Petalas with AI assistance.  Apache-2.0.
"""
from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gate_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)

FAILURES = []


def expect_error(label, function, needle):
    try:
        function()
    except ValueError as error:
        if needle not in str(error):
            FAILURES.append("control rejected for the wrong reason: %s (%s)"
                            % (label, str(error)[:60]))
        return label
    FAILURES.append("control accepted: " + label)
    return label


good = verify.LEAN_SOURCE.read_text()


# 1. A `sorry` in the proof body must be rejected.
sorry_source = good.replace("theorem xfold_nil : xfold [] = false := rfl",
                            "theorem xfold_nil : xfold [] = false := by sorry")
expect_error("sorry escape", lambda: verify.check_lean_source(sorry_source), "sorry")

# 2. A dropped axiom report must be rejected.
dropped = good.replace("#print axioms GateParity.exp_split_d\n", "")
expect_error("missing axiom report",
             lambda: verify.check_lean_source(dropped), "missing axiom report")

# 3. A changed contract body must be rejected.
changed = good.replace("d ∉ srcs ∨ ∃ p t, srcs = p ++ (d :: t) ∧ d ∉ t ∧ ∀ r, EvenCount (p.count r)",
                       "d ∉ srcs")
expect_error("changed Contract body",
             lambda: verify.check_lean_source(changed), "statement binding missing")

# 4. A changed checker operator line must be rejected.
real_root = verify.ROOT




def tampered_pins():
    original = verify.PINNED
    verify.PINNED = [(original[0][0], original[0][1],
                      original[0][2] + ["acc ^= val[d]"])]
    try:
        verify.check_pins(real_root)
    finally:
        verify.PINNED = original


expect_error("changed pinned operator line", tampered_pins, "pinned operator line missing")

# 5. The finite census must reject a wrong contract predicate.
expect_error("wrong contract predicate",
             lambda: verify.census(registers=3, max_len=3, contract=lambda d, s: True),
             "contract mismatch")

# 6. Axiom parsing: unexpected axiom, sorryAx, and missing target.
expect_error("unexpected axiom",
             lambda: verify.parse_axioms(
                 "'GateParity.x' depends on axioms: [Foo.sorryAx]",
                 ["GateParity.x"]),
             "unexpected axiom")
expect_error("sorryAx report",
             lambda: verify.parse_axioms(
                 "'GateParity.x' depends on axioms: [propext]\nsorryAx",
                 ["GateParity.x"]),
             "unchecked proof")
expect_error("missing target report",
             lambda: verify.parse_axioms("'GateParity.y' does not depend on any axioms",
                                         ["GateParity.x"]),
             "axiom report set mismatch")

# Positive control: the real package passes all six underlying checks.
verify.check_lean_source()
verify.check_pins(real_root)
total, agree, diverge = verify.census(registers=3, max_len=3)
assert total > 0 and agree + diverge == total

if FAILURES:
    for line in FAILURES:
        print("FAIL " + line)
    raise SystemExit(1)
print("PASS_GATE_OPERAND_PARITY_LEAN_CONTROLS controls=6 positive_total=%d" % total)
