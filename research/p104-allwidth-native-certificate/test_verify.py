#!/usr/bin/env python3
"""Rejecting controls for verify.py: each mutation must be detected by the dense engine or the pins."""
import copy
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dense as D  # noqa: E402
import verify as V  # noqa: E402


def rejected(fn, label):
    try:
        fn()
    except SystemExit as e:
        print("rejected:", label, "->", str(e)[:80])
        return
    except ValueError as e:
        print("rejected:", label, "->", str(e)[:80])
        return
    raise SystemExit("FAIL: control not rejected: " + label)


def main():
    faults = []
    # 1. pinned input drift
    rejected(lambda: V.check_pins({V.WORD: "0" * 64}), "pinned input drift")
    faults.append("input_drift")
    ce = V.load_module(V.COMPILER, "p104_allwidth_control_compiler")
    w = json.loads(V.gzip.open(V.ROOT / V.WORD).read().decode("utf-8"))
    frames = [tuple(v) for v in w["frames"]]
    a, b = w["program"][9589][2], w["program"][9589][3]          # first MOVE: [] -> [11]
    recipe, _ = ce.lower_child(ce.canonical_frame(9, frames[a]).adjoint().then(ce.canonical_frame(9, frames[b])))
    target = D.circuit_matrix(D.frame_circuit(frames[b])).matmul(D.circuit_matrix(D.frame_circuit(frames[a])).dagger()).normalize()
    assert target.equals(D.circuit_matrix(D.recipe_circuit(recipe))), "the unmutated recipe must pass"

    def mutated(change, label):
        r = copy.deepcopy(recipe)
        change(r)
        got = D.circuit_matrix(D.recipe_circuit(r))
        if target.equals(got):
            raise SystemExit("FAIL: control not rejected: " + label)
        print("rejected:", label)
        faults.append(label)

    def set_phase(r):
        r["left"]["phase"] = (r["left"]["phase"] + 1) % 4
    mutated(set_phase, "left_phase_plus_one")

    def toggle_offset(r):
        r["left"]["offset"] ^= 1
    mutated(toggle_offset, "left_offset_bit_zero")

    def swap_factors(r):
        r["left"], r["right"] = r["right"], r["left"]
    mutated(swap_factors, "reversed_factor_order")
    # 2. conjugated child and an extra Fourier axis, built directly as circuits
    conj = D.monomial_circuit(recipe["right"]) + [("C", 1, -1)] + D.monomial_circuit(recipe["left"])
    if target.equals(D.circuit_matrix(conj)):
        raise SystemExit("FAIL: control not rejected: conjugated child")
    print("rejected: conjugated_child")
    faults.append("conjugated_child")
    extra = D.monomial_circuit(recipe["right"]) + D.fourier(2) + D.monomial_circuit(recipe["left"])
    m = D.circuit_matrix(extra)
    if target.equals(m) or m.support_rank() != 2 or target.support_rank() != 1:
        raise SystemExit("FAIL: control not rejected: extra Fourier axis")
    print("rejected: extra_fourier_axis (support rank 2 vs 1)")
    faults.append("extra_fourier_axis")
    # 3. a chart with the uncomplemented Gram diagonal is a different operator
    W = (11,)
    cols = D.complete_basis(W)
    G = D.transpose(cols)
    Gi = D.inverse(G)
    icols = D.transpose(Gi)
    Qbad = tuple(sum(D.parity(icols[i] & icols[j]) << j for j in range(D.N)) for i in range(D.N))
    alpha = tuple((Qbad[i] >> i) & 1 for i in range(D.N))
    bad = [("D", Qbad, tuple((-x) % 4 for x in alpha)), ("P", Gi)] + D.fourier(1) + [("P", G), ("D", Qbad, alpha)]
    if D.circuit_matrix(bad).equals(D.circuit_matrix(D.frame_circuit(W))):
        raise SystemExit("FAIL: control not rejected: uncomplemented Gram diagonal")
    print("rejected: uncomplemented_gram_diagonal")
    faults.append("uncomplemented_gram_diagonal")
    # 4. a termwise tensor lift of the closed form is not the lifted operator
    axes = (0, 1, 3)
    U = D.small_matrix(D.frame_circuit(frames[b]), axes)
    xz = D.small_matrix([("X", 11), ("D", (0,) * 9, (2, 2, 0, 0, 0, 0, 0, 0, 0))], axes)
    ident = D.Dense(D.np.eye(8, dtype=D.np.complex128), 0)
    termwise = D.Dense((1 + 1j) * D.tensor_power(ident, 2).num + (1 - 1j) * D.tensor_power(xz, 2).num, 1)
    if D.tensor_power(U, 2).equals(termwise):
        raise SystemExit("FAIL: control not rejected: termwise lift")
    print("rejected: termwise_tensor_lift")
    faults.append("termwise_tensor_lift")
    # 5. a rank-one Gaussian is not accepted as a monomial
    if D.circuit_matrix([("C", 1, 1)]).is_monomial():
        raise SystemExit("FAIL: control not rejected: Gaussian as monomial")
    print("rejected: gaussian_as_monomial")
    faults.append("gaussian_as_monomial")
    # 6. tampered RESULT.json
    stored = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    tampered = copy.deepcopy(stored)
    tampered["chart_changes"]["recipe_payload_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "RESULT.json"
        p.write_text(json.dumps(tampered), encoding="utf-8")
        if V.result_matches(stored, p) or not V.result_matches(tampered, p):
            raise SystemExit("FAIL: control not rejected: tampered RESULT.json")
    print("rejected: tampered_result")
    faults.append("tampered_result")
    print(f"PASS_P104_ALLWIDTH_NATIVE_CONTROLS faults={len(faults)} [{', '.join(faults)}]")


if __name__ == "__main__":
    main()
