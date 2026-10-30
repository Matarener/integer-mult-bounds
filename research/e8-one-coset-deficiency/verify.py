#!/usr/bin/env python3
"""Read-only exact replay of the one-coset theorem's finite inputs and controls.

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
Use --emit explicitly to replace CERTIFICATE.json and RESULT.json. Normal
execution writes neither files nor bytecode. This is not an E8 proof assistant.
"""

import argparse
from hashlib import sha256
import json
from math import factorial
from pathlib import Path
import sys
from types import ModuleType


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def check_receipt(expected, actual):
    # JSON integer/boolean/float types remain distinct; dict key order does not matter.
    require(canonical_json(expected) == canonical_json(actual), "RESULT.json differs from replay")


def scientific_hashes(certificate_bytes=None):
    inventory = {}
    for path in sorted(PACKAGE.rglob("*")):
        if not path.is_file() or path.name == "RESULT.json" or path.suffix not in (
                ".py", ".md", ".json", ".lean"):
            continue
        require(not path.is_symlink(), "scientific input is a symbolic link")
        relative = path.relative_to(PACKAGE).as_posix()
        data = certificate_bytes if relative == "CERTIFICATE.json" and certificate_bytes is not None else path.read_bytes()
        inventory[relative] = sha256(data).hexdigest()
    if certificate_bytes is not None:
        inventory["CERTIFICATE.json"] = sha256(certificate_bytes).hexdigest()
    return dict(sorted(inventory.items()))


def load_source(name):
    """Execute current source bytes directly; stale .pyc caches cannot replace them."""
    path = PACKAGE / (name + ".py")
    module = ModuleType("one_coset_" + name)
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def check_sources():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    checked = []
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        require(sha256(path.read_bytes()).hexdigest() == row["sha256"],
                "live source pin differs: " + row["path"])
        checked.append(row["path"])
    return checked


def bind_models(g, first, other):
    """Match all root lines, scalar orientations and binary label matroids."""
    standard = g.standard_binding(first)
    lookup = {g.canonical(row): i for i, row in enumerate(other["roots"])}
    require(len(lookup) == 120, "independent root lines are not distinct")
    mapping, signs, basis = [], [], {}
    for root, label in zip(standard, first["labels"]):
        key = g.canonical(root)
        require(key in lookup, "independent root alphabet differs")
        index = lookup[key]
        mapping.append(index)
        signs.append(1 if root == other["roots"][index] else -1)
        a, b = label, other["labels"][index]
        while a:
            pivot = a.bit_length() - 1
            if pivot in basis:
                x, y = basis[pivot]
                a, b = a ^ x, b ^ y
            else:
                basis[pivot] = (a, b)
                break
        if not a:
            require(b == 0, "label graph is not a linear map")
    require(len(set(mapping)) == 120 and len(basis) == 9, "model map is not a full-rank bijection")

    def transport(value):
        image = 0
        while value:
            pivot = value.bit_length() - 1
            a, b = basis[pivot]
            value, image = value ^ a, image ^ b
        return image

    images = [transport(1 << i) for i in range(9)]
    require(all(g.parity(a & b) == int(i == j) for i, a in enumerate(images)
                for j, b in enumerate(images)), "label transport does not preserve beta")
    require(transport(g.OMEGA) == g.OMEGA, "characteristic vector transport")
    for value in range(512):
        image = transport(value)
        require(g.parity(value) == g.parity(image), "parity transport")
        if not g.parity(value):
            require((value.bit_count() // 2) % 2 == (image.bit_count() // 2) % 2,
                    "even quadratic colour transport")
    for i, root in enumerate(first["roots"]):
        for j, other_root in enumerate(first["roots"]):
            product = g.dot(other["roots"][mapping[i]], other["roots"][mapping[j]])
            require(4 * g.dot(root, other_root) == 9 * signs[i] * signs[j] * product,
                    "independent scalar Gram isometry")
    return {"root_bijection": 120, "gram_pairs": 14400, "label_graph_rank": 9,
            "orthonormal_transport_checks": 81, "binary_vectors_transported": 512,
            "even_quadratic_colours_transported": 256}


def receipt_controls():
    check_receipt({"count": 1}, {"count": 1})
    rejected = []
    for name, value in (("boolean", True), ("float", 1.0), ("string", "1"), ("wrong_integer", 2)):
        try:
            check_receipt({"count": value}, {"count": 1})
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("receipt type control accepted: " + name)
    return rejected


def run(emit=False):
    inputs = check_sources()
    geometry, independent, fixtures, controls, sparse_pair = [
        load_source(name) for name in ("geometry", "independent", "fixtures", "controls", "sparse_pair")]
    model = geometry.build_model()
    if emit:
        certificate = geometry.make_certificate(model)
        certificate_bytes = geometry.certificate_text(certificate).encode()
    else:
        certificate_bytes = (PACKAGE / "CERTIFICATE.json").read_bytes()
        certificate = json.loads(certificate_bytes)
    first = geometry.check_certificate(model, certificate)
    reflections = geometry.reflection_transport(model)
    second = independent.run()
    require(second["single_rank_histogram"] == {"8": 511}, "independent single ranks differ")
    require(second["pair_rank_histogram"] == {"0": 255, "6": 3360, "7": 35640, "8": 91050},
            "independent pair ranks differ from the retained census")
    ordered = forbidden_ordered = 0
    for counts, a, b in geometry.pair_profiles():
        orbit = factorial(9)
        for count in counts:
            orbit //= factorial(count)
        ordered += orbit
        if geometry.forbidden(a, b):
            forbidden_ordered += orbit
    require(ordered == 511 * 510 and forbidden_ordered == 2 * second["forbidden_pairs_proved_full_rank"],
            "profile orbit sizes disagree with the independent exhaustive pairs")
    other_model = independent.build_model()
    bound = bind_models(geometry, model, other_model)
    sparse_roots, sparse_table = sparse_pair.build_model()
    lookup = {row: i for i, row in enumerate(other_model["roots"])}
    require(len(sparse_roots) == 120 and set(sparse_roots) == set(lookup),
            "sparse-pair root alphabet differs from the bound models")
    mapping = [lookup[row] for row in sparse_roots]
    for i in range(120):
        for j in range(120):
            require(((sparse_table[i] >> j) & 1) == geometry.parity(
                other_model["labels"][mapping[i]] & other_model["labels"][mapping[j]]),
                "sparse-pair dense table differs from the bound models")
    bound["sparse_pair_root_bijection"] = 120
    bound["sparse_pair_table_entries"] = 14400
    actual_factors = fixtures.run(geometry, model)
    fault_controls = controls.run(geometry, model, certificate)
    result = {
        "schema_version": 1,
        "scope": "finite proof inputs and controls for the written all-m one-coset theorem",
        "live_inputs_authenticated": inputs,
        "primary_certificate": first,
        "odd_field_profile_transport": reflections,
        "independent_exhaustion": second,
        "profile_orbit_accounting": {"ordered_pairs": ordered, "forbidden_ordered_pairs": forbidden_ordered},
        "model_binding": bound,
        "actual_factors": actual_factors,
        "sparse_pair_evidence": sparse_pair.run(),
        "integrity_and_hypothesis_controls": fault_controls,
        "receipt_type_controls": receipt_controls(),
        "scientific_sha256": scientific_hashes(certificate_bytes if emit else None),
    }
    return json.loads(json.dumps(result, sort_keys=True)), certificate_bytes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="explicitly replace both deterministic receipts")
    args = parser.parse_args()
    try:
        expected = None
        if not args.emit:
            expected = json.loads((PACKAGE / "RESULT.json").read_text())
            require(expected["scientific_sha256"] == scientific_hashes(),
                    "scientific source inventory/hash differs before execution")
        result, certificate = run(args.emit)
        if args.emit:
            (PACKAGE / "CERTIFICATE.json").write_bytes(certificate)
            (PACKAGE / "RESULT.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        else:
            check_receipt(expected, result)
    except (ValueError, RuntimeError, OSError, KeyError, TypeError, IndexError) as error:
        print("FAIL_E8_ONE_COSET_DEFICIENCY: " + str(error), file=sys.stderr)
        return 1
    print("PASS_E8_ONE_COSET_DEFICIENCY minors=109 characters=511 pairs=130305 "
          "exact_factorizations=8 strict_rank9_equality=72 "
          "sparse_pair_basis_floor=72 "
          "normalized_sparse_rank10_equality=72 "
          "scope=written-proof-inputs-and-controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
