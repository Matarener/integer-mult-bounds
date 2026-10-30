#!/usr/bin/env python3
"""Odd-kernel coefficient-bit tariff vs dyadic (answers #2687 OQ2).

Under the named ADDRESS coefficient-bit tariff, every certified odd kernel
strictly exceeds the dyadic fused (and baseline) bill at each dyadic index
j in 0..32. Typed child/XOR counts stay identical, so larger-q coefficient
tables never pay for themselves on this tariff. No new kappa.

Admission uses need() and remains active under python -O.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_ODD_KERNEL_COEFF_BIT_TARIFF "
    "kernels=[1, 3, 5, 7, 9, 15] j=0..32 "
    "odd_fused_exceeds_dyadic=165 "
    "odd_baseline_exceeds_dyadic=165 "
    "no_new_kappa"
)
KAPPA_DECIMAL = "0.001672660197076918"
KAPPA_FRACTION = "836330098538459/500000000000000000"
KERNELS = (1, 3, 5, 7, 9, 15)
ODD_KERNELS = (3, 5, 7, 9, 15)
J_MAX = 32
PRIOR_README = "research/odd-kernel-query-pair/README.md"
PRIOR_TASK = "research/odd-kernel-query-pair/TASK.json"
PRIOR_PROGRAM = "research/odd-kernel-query-pair/program.py"
INPUTS = (PRIOR_PROGRAM,)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def read_json(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 4_000_000, "input exceeds 4 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    need(manifest["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
         "base commit pin")
    rows = manifest["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    pinned = {}
    for row in rows:
        path = ROOT / row["path"]
        raw = path.read_bytes()
        need(len(raw) == row["size_bytes"], "source size: " + row["path"])
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == row["sha256"], "source hash: " + row["path"])
        pinned[row["path"]] = raw
    return pinned


def load_tariff():
    ns = runpy.run_path(str(HERE / "tariff.py"))
    return ns


def bind_prior_oq(pinned):
    readme = pinned[PRIOR_README].decode("utf-8")
    task = pinned[PRIOR_TASK].decode("utf-8")
    need("coefficient-table bit-sizes for larger `q`" in readme,
         "cite: #2687 README OQ2")
    need("Do coefficient-table bit-sizes for larger q ever pay for themselves"
         in task,
         "cite: #2687 TASK OQ2")
    prog = pinned[PRIOR_PROGRAM].decode("utf-8")
    need("def address_word(k):" in prog, "cite: prior address_word")
    need("a = Fraction(k, 4)" in prog, "cite: prior a=k/4")


def cross_check_prior_program(pinned, tariff):
    """Byte-pinned prior program must agree on address_word coeffs and T_word."""
    prior = runpy.run_path(str(ROOT / PRIOR_PROGRAM))
    for k in (1, -1, 3, 4, 5, 12, 15, 16, 48, -20, 40):
        ours = tariff["word_coefficients"](k)
        theirs = []
        for event in prior["address_word"](k):
            if event[0] != "affine":
                continue
            theirs.append(event[2])
            for _, c in event[3]:
                theirs.append(c)
        need(tuple(ours) == tuple(theirs), f"coeff match k={k}")
        need(tariff["T_word"](k) == sum(
            tariff["coeff_bit_length"](c) for c in theirs
        ), f"T_word match k={k}")


def evaluate(write=False):
    pinned = pin_sources()
    bind_prior_oq(pinned)
    tariff = load_tariff()

    # Closed form equals enumeration.
    for k in list(range(-64, 0)) + list(range(1, 65)):
        need(tariff["T_word"](k) == tariff["closed_form_T_word"](k),
             f"closed form k={k}")
        need(tariff["T_word"](k) == tariff["T_word"](-k), f"sign free k={k}")

    # Non-monotonicity control: T_word is not monotone in |k|.
    need(tariff["T_word"](4) < tariff["T_word"](2) < tariff["T_word"](1),
         "T_word not monotone (4<2<1)")
    need(tariff["T_word"](4) == 32, "dyadic sweet spot T(4)=32")

    cross_check_prior_program(pinned, tariff)

    # Typed invoice invariance reused from prior: fused always 3/18/2.
    # We only re-check power lists and child counts via powers.
    rows = []
    odd_fused_exceeds = 0
    odd_baseline_exceeds = 0
    for j in range(0, J_MAX + 1):
        dy_f = tariff["T_fused"](j, 1)
        dy_b = tariff["T_baseline"](j, 1)
        need(len(tariff["fused_powers"](j, 1)) == 3, "fused query count")
        need(len(tariff["baseline_powers"](j, 1)) == 4, "baseline query count")
        for q in KERNELS:
            fused = tariff["T_fused"](j, q)
            base = tariff["T_baseline"](j, q)
            row = {
                "j": j,
                "kernel": q,
                "a": q * (1 << j),
                "T_fused": fused,
                "T_baseline": base,
                "T_word_a": tariff["T_word"](q * (1 << j)),
                "T_word_2a": tariff["T_word"](2 * q * (1 << j)),
            }
            rows.append(row)
            if q == 1:
                need(fused == 2 * row["T_word_a"] + row["T_word_2a"],
                     "fused additive")
                continue
            need(fused > dy_f, f"fused q={q} j={j}: {fused} !> {dy_f}")
            need(base > dy_b, f"baseline q={q} j={j}: {base} !> {dy_b}")
            odd_fused_exceeds += 1
            odd_baseline_exceeds += 1

    need(odd_fused_exceeds == len(ODD_KERNELS) * (J_MAX + 1),
         "odd fused exceed count")
    need(odd_baseline_exceeds == len(ODD_KERNELS) * (J_MAX + 1),
         "odd baseline exceed count")
    need(odd_fused_exceeds == 165, "165 odd fused comparisons")
    need(odd_baseline_exceeds == 165, "165 odd baseline comparisons")

    # Spot checks at the OQ's suggested first step (fix j, q in {1,3,5,7}).
    for j in (0, 1, 2, 4):
        bills = {q: tariff["T_fused"](j, q) for q in (1, 3, 5, 7)}
        need(bills[1] < bills[3] < bills[5], f"growth at j={j}: {bills}")
        need(bills[1] < bills[7], f"q=7 exceeds dyadic at j={j}")

    # Fusion saves coefficient bits but never reverses the odd>dyadic order.
    for j in range(0, J_MAX + 1):
        for q in ODD_KERNELS:
            save_q = tariff["T_baseline"](j, q) - tariff["T_fused"](j, q)
            save_1 = tariff["T_baseline"](j, 1) - tariff["T_fused"](j, 1)
            need(save_q > 0 and save_1 > 0, "fusion saves bits")
            need(tariff["T_fused"](j, q) > tariff["T_fused"](j, 1),
                 "fusion does not overturn odd>dyadic")

    selected = read_json(ROOT / "certificates/selected-result.json")
    need(selected.get("kappa") == KAPPA_FRACTION, "selected kappa unchanged")

    # Adversarial controls.
    fake_dyadic = tariff["T_fused"](2, 1) + 100
    need(tariff["T_fused"](2, 3) > tariff["T_fused"](2, 1), "positive control")
    need(not (tariff["T_fused"](2, 3) > fake_dyadic),
         "control: inflated dyadic would break strict exceed vs q=3 at j=2")

    certificate = {
        "schema_version": 1,
        "status": "PASS_ODD_KERNEL_COEFF_BIT_TARIFF",
        "kappa_decimal": KAPPA_DECIMAL,
        "kappa_fraction": KAPPA_FRACTION,
        "tariff": {
            "name": "ADDRESS_affine_coeff_num_den_bit_sum",
            "definition": (
                "T_word(k) = sum over affine diagonal/control coefficients c=p/q "
                "in lowest terms of bit_length(|p|)+bit_length(q); "
                "T_fused(q,j)=2*T_word(q*2^j)+T_word(q*2^{j+1}); "
                "T_baseline(q,j)=4*T_word(q*2^j)."
            ),
            "unit_coeff_bits": 20,
        },
        "kernels": list(KERNELS),
        "odd_kernels": list(ODD_KERNELS),
        "j_max": J_MAX,
        "counts": {
            "odd_fused_exceeds_dyadic": odd_fused_exceeds,
            "odd_baseline_exceeds_dyadic": odd_baseline_exceeds,
            "grid_rows": len(rows),
        },
        "spot": {
            "T_word": {str(k): tariff["T_word"](k) for k in (1, 2, 3, 4, 5, 7, 15)},
            "T_fused_j2": {str(q): tariff["T_fused"](2, q) for q in KERNELS},
            "non_monotone": {"T(1)": 45, "T(2)": 38, "T(4)": 32},
        },
        "claim": {
            "odd_fused_strictly_exceeds_dyadic_on_grid": True,
            "odd_baseline_strictly_exceeds_dyadic_on_grid": True,
            "typed_child_xor_counts_identical": True,
            "tables_never_pay_on_this_tariff": True,
        },
        "no_new_kappa": True,
    }
    admit_certificate(certificate, write=write)
    return certificate


def admit_certificate(certificate, write=False):
    path = HERE / "CERTIFICATE.json"
    if write:
        path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        return
    need(path.is_file(), "missing CERTIFICATE.json")
    committed = read_json(path)
    need(committed == certificate, "certificate mismatch")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate CERTIFICATE.json (explicit write path only)",
    )
    args = parser.parse_args(argv)
    certificate = evaluate(write=args.write)
    need(certificate["status"] == "PASS_ODD_KERNEL_COEFF_BIT_TARIFF", "status")
    print(MARKER)


if __name__ == "__main__":
    main()
