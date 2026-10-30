#!/usr/bin/env python3
"""Exact certificate checks for the P104 A2 packing maximum. Apache-2.0."""

import copy
import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PORT_PATH = "research/p104-carrier-code-uniqueness/e8/ports.json"
PORT_SHA = "ba6a0b9cf76b7cccc1ce8b3d1aa78a4aa329b34d45aded694648f0cf43fc9fce"
MASK = 511
MAX_BYTES = 65536


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_json(path):
    require(path.stat().st_size <= MAX_BYTES, "oversized JSON input")
    raw = path.read_bytes()
    require(len(raw) <= MAX_BYTES, "JSON input grew while reading")
    return json.loads(raw), raw


def xor_sum(values):
    result = 0
    for value in values:
        result ^= value
    return result


def root3(q):
    """Three times the A8-coordinate root attached to the odd port q."""
    require(type(q) is int and 0 < q <= MASK, "port outside nine bits")
    require(q.bit_count() in (3, 7), "port has unsupported weight")
    if q.bit_count() == 3:
        return tuple(2 if (q >> i) & 1 else -1 for i in range(9))
    a, b = [i for i in range(9) if not (q >> i) & 1]
    return tuple(3 * (int(i == a) - int(i == b)) for i in range(9))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


def validate_ports(ports):
    require(type(ports) is list and len(ports) == 104, "need 104 ports")
    roots = [root3(q) for q in ports]
    require(len(set(ports)) == 104, "duplicate port")
    for q, root in zip(ports, roots, strict=True):
        require(sum(root) == 0 and dot(root, root) == 18, "invalid root")
        parity = sum((x % 2) << i for i, x in enumerate(root))
        require(parity == (MASK ^ q), "root/label parity mismatch")
    require(xor_sum(ports) == 0, "total port XOR is not zero")
    return roots


def parity_upper_bound(labels):
    """Apply the written parity lemma; triangle XOR is its hypothesis."""
    require(2 <= len(labels) <= 120, "parity domain size")
    require(all(type(q) is int and 0 <= q <= MASK for q in labels), "bad label")
    require(len(set(labels)) == len(labels), "parity needs distinct labels")
    require(len(labels) % 6 == 2, "parity needs size 6m+2")
    require(xor_sum(labels) == 0, "parity needs total XOR zero")
    return len(labels) // 3 - 1


def validate_packing(ports, certificate):
    roots = validate_ports(ports)
    require(type(certificate) is dict, "packing is not an object")
    require(set(certificate) == {"schema_version", "triangles", "uncovered"},
            "unexpected packing fields")
    require(type(certificate["schema_version"]) is int and
            certificate["schema_version"] == 1, "packing schema")
    triangles = certificate["triangles"]
    require(type(triangles) is list and len(triangles) == 33, "need 33 triangles")
    used = set()
    for triangle in triangles:
        require(type(triangle) is list and len(triangle) == 3, "triangle arity")
        require(all(type(i) is int and 0 <= i < 104 for i in triangle),
                "triangle index")
        require(triangle == sorted(set(triangle)), "triangle ordering/distinctness")
        require(not used.intersection(triangle), "triangles overlap")
        require(all((ports[u] & ports[v]).bit_count() % 2 == 0
                    for u, v in itertools.combinations(triangle, 2)),
                "conflicting ports in triangle")
        a, b, c = (roots[i] for i in triangle)
        ab, bc, ca = dot(a, b), dot(b, c), dot(c, a)
        require(all(abs(x) == 9 for x in (ab, bc, ca)) and
                ab * bc * ca == -729, "not an A2 triangle")
        require(all(c[i] == (ca // 9) * a[i] + (bc // 9) * b[i]
                    for i in range(9)), "signed root relation")
        require(xor_sum(ports[i] for i in triangle) == MASK, "triangle XOR")
        used.update(triangle)
    uncovered = certificate["uncovered"]
    require(type(uncovered) is list and
            all(type(i) is int for i in uncovered), "uncovered index types")
    require(uncovered == sorted(set(range(104)) - used), "uncovered indices")
    require(len(used) == 99 and len(uncovered) == 5, "coverage")
    require(xor_sum(ports[i] for i in uncovered) == MASK, "uncovered XOR")
    require(parity_upper_bound(ports) == len(triangles), "upper/lower bound gap")
    return {"maximum_triangles": len(triangles), "covered_ports": len(used),
            "minimum_uncovered": len(uncovered), "uncovered_indices": uncovered,
            "uncovered_labels": [ports[i] for i in uncovered]}


def expect_rejection(label, function, *args):
    try:
        function(*args)
    except ValueError:
        return label
    raise ValueError("control accepted: " + label)


def controls(ports, certificate):
    rejected = []
    for label, replacement in (("duplicate triangle", certificate["triangles"][0]),
                               ("nontriangle", [0, 1, 2]),
                               ("invalid index", [0, 45, 104]),
                               ("boolean index", [False, 45, 67])):
        bad = copy.deepcopy(certificate)
        bad["triangles"][1 if label == "duplicate triangle" else 0] = replacement
        rejected.append(expect_rejection(label, validate_packing, ports, bad))
    bad = copy.deepcopy(certificate)
    bad["uncovered"] = [12, 13]
    rejected.append(expect_rejection("false two-port leave", validate_packing, ports, bad))
    bad = copy.deepcopy(certificate)
    bad["triangles"].pop()
    rejected.append(expect_rejection("missing triangle", validate_packing, ports, bad))
    bad_ports = ports.copy()
    bad_ports[0] = ports[1]
    rejected.append(expect_rejection("duplicate port", validate_ports, bad_ports))
    for q in (True, -1, 512, 1):
        rejected.append(expect_rejection("invalid root " + repr(q), root3, q))
    for labels in ([0, 1], [0, 0], [0, 1, 2, 3], [False, 0]):
        rejected.append(expect_rejection("parity premise " + repr(labels),
                                         parity_upper_bound, labels))
    return rejected


def local_lemma_controls():
    """An independent complete small-label check of the parity argument."""
    cases = 0
    for labels in itertools.combinations(range(16), 8):
        if xor_sum(labels):
            continue
        for first in itertools.combinations(labels, 3):
            remaining = tuple(q for q in labels if q not in first)
            for second in itertools.combinations(remaining, 3):
                require(xor_sum(first) != xor_sum(second),
                        "two disjoint equal-XOR triples in zero-XOR eight-set")
                cases += 1
        require(parity_upper_bound(labels) == 1, "small parity bound")
    return cases


def main():
    sources, _ = load_json(HERE / "SOURCES.json")
    pins = [row for row in sources["files"] if row["path"] == PORT_PATH]
    require(len(pins) == 1 and pins[0]["usage"] == "input" and
            pins[0]["sha256"] == PORT_SHA, "port source declaration")
    ports, raw = load_json(ROOT / PORT_PATH)
    require(hashlib.sha256(raw).hexdigest() == PORT_SHA, "port source hash")
    certificate, _ = load_json(HERE / "PACKING.json")
    result = validate_packing(ports, certificate)
    result["rejected_controls"] = controls(ports, certificate)
    result["small_label_cases"] = local_lemma_controls()
    payload = sorted(HERE.iterdir())
    require(len(payload) <= 16 and all(p.is_file() for p in payload), "payload shape")
    result["sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in payload}
    result["input_sha256"] = {PORT_PATH: hashlib.sha256(raw).hexdigest()}
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_P104_A2_PACKING_MAXIMUM")


if __name__ == "__main__":
    main()
