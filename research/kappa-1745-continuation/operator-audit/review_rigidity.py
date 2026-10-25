#!/usr/bin/env python3
"""Independent dense Gaussian-matrix check of the twenty rigidity columns.

Each column is obtained by replacing one identity phase with i, computing
the full matrix, and dividing M-I exactly by i-1. This differs from the
certificate generator's simultaneous mod-2 derivative propagation.
"""
import gzip
import hashlib
import json
from pathlib import Path
import independent_witness as W

HERE = Path(__file__).resolve().parent
SCOPE = HERE.parent
TEMPLATE = HERE / "checkout/research/rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz"
CERTIFICATE = SCOPE / "complex/SLOT-PROJECTOR-RIGIDITY.json"


def changed_matrix(template, selected):
    context = {"template": template, "recipe": {"q": 0, "idle_children": [{"translation_after": 0} for _ in range(20)]}}
    residual = {c: [] for c in range(20)}
    result = W.identity()
    for event in template["execution_schedule"]:
        if event["kind"] in ("bank_padding_cover_sweep", "translate_every_live_family"):
            continue
        for elementary in W.event_matrices(event, context, residual, 0):
            result = W.multiply(elementary, result)
        if event["kind"] == "idle_cover_sweep":
            for side, child in enumerate(event["child_indices"]):
                if child == selected:
                    result = W.multiply(W.diagonal(2 * event["pair"] + side, 1), result)
    return result


def main():
    template = json.loads(gzip.decompress(TEMPLATE.read_bytes()))
    certificate = json.loads(CERTIFICATE.read_text())
    baseline = changed_matrix(template, None)
    assert baseline == W.identity()
    columns, integer_derivatives = [], []
    for c in range(20):
        changed = changed_matrix(template, c)
        values, bits = [], 0
        for r in range(8):
            row = []
            for s in range(8):
                re = changed[r][s][0] - baseline[r][s][0]
                im = changed[r][s][1] - baseline[r][s][1]
                # (re+i im)/(i-1) = ((im-re)-i(re+im))/2.
                assert (im - re) % 2 == 0 and re + im == 0
                value = (im - re) // 2
                row.append(value)
                bits |= (value & 1) << (8 * r + s)
            values.append(row)
        columns.append(bits)
        integer_derivatives.append(values)
    assert columns == list(map(int, certificate["columns"]))
    inverse = list(map(int, certificate["left_inverse_rows"]))
    assert len(inverse) == 20
    assert all(((inverse[r] & columns[s]).bit_count() & 1) == (r == s) for r in range(20) for s in range(20))
    # Exact Gaussian ring arithmetic control for epsilon=i-1.
    def times(a, b): return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])
    epsilon = (-1, 1)
    assert times(epsilon, epsilon) == (0, -2)
    assert times(times(epsilon, epsilon), epsilon) == (2, 2)
    out = {"status": "PASS_INDEPENDENT_DENSE_SLOT_RIGIDITY_CERTIFICATE_REVIEW",
           "columns_reconstructed": 20, "left_inverse_entries_checked": 400,
           "integer_derivatives": integer_derivatives, "columns_mod2": list(map(str, columns)),
           "source_pins": {str(p.relative_to(SCOPE.parent.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (TEMPLATE, CERTIFICATE, Path(__file__), Path(W.__file__))},
           "proof_review": "The written second-order argument was reviewed separately: equality of each first-order slot term cancels cross terms; linear translation/sign controls cannot cancel degree-two coefficients; polarization fixes each orthogonal projector. Fixed integral scalar/local graph and twenty slots only.",
           "new_kappa": False}
    (HERE / "RIGIDITY-REVIEW.json").write_text(json.dumps(out, indent=2) + "\n")
    print("PASS_INDEPENDENT_DENSE_SLOT_RIGIDITY_CERTIFICATE_REVIEW columns=20 identity_entries=400")


if __name__ == "__main__":
    main()
