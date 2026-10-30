"""Exact byte, full-receipt and rejection checks for the streaming adapter.

This contribution was produced by Nick Petalas. Apache-2.0.
"""
import ast
import copy
from hashlib import sha256
import itertools
import json
from pathlib import Path
import sys
from types import SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import accelerator as fast


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reference_bytes(circuit):
    return json.dumps(
        [[i, circuit.args[i], str(circuit.support[i])]
         for i in sorted(circuit.active)], separators=(",", ":")
    ).encode()


def coverage_guard(candidate=None):
    """Compare the complete checker AST, allowing only the digest replacement."""
    source = ast.parse((fast.ROOT / "scripts/experiments/disjoint_tensor.py").read_text())
    cls = next(x for x in source.body if isinstance(x, ast.ClassDef)
               and x.name == "DisjointTensor")
    original = next(x for x in cls.body if isinstance(x, ast.FunctionDef)
                    and x.name == "verify")
    assignment = ast.parse(
        "encoded = json.dumps([[i,self.args[i],str(self.support[i])] "
        "for i in sorted(self.active)], separators=(',',':')).encode()"
    ).body[0]
    matches = [i for i, node in enumerate(original.body)
               if ast.dump(node) == ast.dump(assignment)]
    require(len(matches) == 1, "Expected one exact JSON assignment")
    original.body.pop(matches[0])
    result = original.body[-1].value
    digest = [kw for kw in result.keywords if kw.arg == "dag_sha256"]
    require(len(digest) == 1, "Expected one digest field")
    require(ast.dump(digest[0].value) == ast.dump(
        ast.parse("sha256(encoded).hexdigest()", mode="eval").body), "Wrong old digest")
    digest[0].value = ast.parse("stream_digest(self)", mode="eval").body
    if candidate is None:
        tree = ast.parse((PACKAGE / "accelerator.py").read_text())
        candidate = next(x for x in tree.body if isinstance(x, ast.FunctionDef)
                         and x.name == "verify")
    require(ast.dump(original) == ast.dump(candidate), "A nondigest checker changed")
    return candidate


def rejects(call, label):
    try:
        call()
    except (ValueError, AssertionError):
        return
    raise ValueError("Accepted invalid control: " + label)


def check_bytes():
    cases = 0
    for size in range(3):
        options = [None] + list(itertools.product(range(size), repeat=2))
        for supports in itertools.product(range(4), repeat=size):
            for pairs in itertools.product(options, repeat=size):
                for mask in range(1 << size):
                    circuit = SimpleNamespace(support=supports, args=pairs,
                                              active={i for i in range(size) if mask >> i & 1})
                    expected = reference_bytes(circuit)
                    for budget in (1, 7, 64, fast.CHUNK_BYTES):
                        actual = b"".join(fast.chunks(circuit, budget))
                        require(actual == expected, "Tiny-schema bytes differ")
                    require(fast.stream_digest(circuit) == sha256(expected).hexdigest(),
                            "Tiny-schema digest differs")
                    cases += 1
    for bits in (1, 8, 64, 127, 1024, fast.MAX_SUPPORT_BITS):
        circuit = SimpleNamespace(support=[0, (1 << bits) - 1],
                                  args=[None, (0, 1)], active={1, 0})
        require(b"".join(fast.chunks(circuit, 7)) == reference_bytes(circuit),
                "Large-integer bytes differ")
        cases += 1
    return cases


def check_rejections():
    cases = [
        ([0], [None], {-1}), ([0], [None], {1}), ([0], [None], {True}),
        ([-1], [None], {0}), (["1"], [None], {0}),
        ([1 << fast.MAX_SUPPORT_BITS], [None], {0}),
        ([0], [(0,)], {0}), ([0], [(0, True)], {0}),
        ([0], [[0, 0]], {0}), ([0], [(0, 1)], {0}),
        ([0], [], {0}), ([0], [None], {0, 1}),
        (range(fast.MAX_NODES + 1), range(fast.MAX_NODES + 1), set()),
    ]
    for support, args, active in cases:
        circuit = SimpleNamespace(support=support, args=args, active=active)
        rejects(lambda: fast.stream_digest(circuit), "malformed schema")
    good = SimpleNamespace(support=[0], args=[None], active={0})
    for budget in (0, -1, True, fast.CHUNK_BYTES + 1):
        rejects(lambda: list(fast.chunks(good, budget)), "chunk budget")
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    for row in inputs:
        data = (fast.ROOT / row["path"]).read_bytes() + b"\n"
        rejects(lambda: fast.check_sources(overrides={row["path"]: data}), "source drift")
    original = coverage_guard()
    for index in range(len(original.body) - 1):
        mutant = copy.deepcopy(original)
        mutant.body.pop(index)
        rejects(lambda: coverage_guard(mutant), "omitted checker statement")
    return len(cases) + 4 + len(inputs) + len(original.body) - 1


def check_circuits():
    fixtures = [(4, 1), (6, 2), (6, 3), (8, 3), (10, 3), (26, 3)]
    records = []
    for h, k in fixtures:
        circuit = fast.DisjointTensor(h, k)
        baseline = circuit.verify()
        streamed = fast.verify(circuit)
        require(baseline == streamed, "Complete verification receipts differ")
        pieces = list(fast.chunks(circuit))
        require(max(map(len, pieces)) <= fast.CHUNK_BYTES + 3039,
                "Row-buffer bound exceeded")
        require(b"".join(pieces) == reference_bytes(circuit),
                "Real-circuit bytes differ")
        records.append(streamed)
    for kind in range(4):
        circuit = fast.DisjointTensor(8)
        node = next(i for i in sorted(circuit.active) if circuit.args[i] is not None)
        if kind == 0:
            circuit.support[node] ^= 1
        elif kind == 1:
            circuit.args[node] = (node, circuit.args[node][1])
        elif kind == 2:
            circuit.additions = 1_000_000_000
        else:
            target = next(iter(circuit.outputs))
            circuit.outputs[target] = 1
        rejects(circuit.verify, "baseline circuit fault")
        rejects(lambda: fast.verify(circuit), "streamed circuit fault")
    return records


def main():
    fast.check_sources()
    coverage_guard()
    byte_cases = check_bytes()
    rejection_cases = check_rejections()
    records = check_circuits()
    print(json.dumps({
        "status": "PASS_DISJOINT_DAG_STREAMING",
        "schema_cases": byte_cases, "rejection_cases": rejection_cases + 8,
        "full_receipt_fixtures": len(records), "h26": records[-1],
        "claim_type": "tooling improvement with scoped serialization equivalence",
        "no_new_kappa": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
