#!/usr/bin/env python3
"""Independent forward-perturbation oracle for the first PR5786 hub.

New audit: ToikY with substantial OpenAI Codex assistance in a separate
implementation context. Ali Romman supplied the asynchronous construction,
plan and retained-copy word. Apache-2.0; NOTICE retains predecessor credit.
No predecessor implementation or the package verifier is imported.
"""
from fractions import Fraction
from hashlib import sha1, sha256
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORD_SHA256 = "7c393444fa5b9a6941471d02047beb2aa8285e5614bb052fb85458b69236a38a"
WORD_BLOB = "3ae3c4ebc8fc92098784f717a3107e6fa958dd86"
CANONICAL_WORD = "75f429fc0c8b206f4439bfbda4b621fc62ea892e6e3008c17409f2d3ee0981bb"
PLAN_SHA256 = "2c4878f78dc393339f8cccf24441d9bfb50257784459c2f253ebcb27c964211c"
PLAN_BLOB = "9cf72d400fdb2adef54eca047c752a657a0d4a33"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticated(name, expected_sha256, expected_blob):
    raw = (HERE / "inputs" / name).read_bytes()
    require(sha256(raw).hexdigest() == expected_sha256,
            "Exact oracle input SHA256: " + name)
    blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(blob == expected_blob, "Exact oracle Git blob: " + name)
    return raw


def sparse(vector):
    return {str(i): str(value) for i, value in enumerate(vector) if value}


def role(event, position, size):
    value = event[position]
    require(type(value) is int and 0 <= value < size, "Oracle role range")
    return value


def split_time(word, time2):
    require(type(time2) is int and 0 <= time2 <= 2 * len(word["program"]),
            "Oracle contact time range")
    index, midpoint = divmod(time2, 2)
    if midpoint:
        require(index == 13750 and word["program"][index]
                == ["MOVE", 770, 591, 597, True],
                "Oracle actual paid interior query")
    return index, midpoint


def prefix_functional(word, contact):
    """Backpropagate one read functional, without inverting the prefix."""
    size = word["public"] + word["owned_fields"]
    vector = [Fraction(0) for _ in range(size)]
    source = contact["role"]
    require(type(source) is int and 0 <= source < size, "Oracle collection role")
    vector[source] = Fraction(contact["coefficient"])
    index, midpoint = split_time(word, contact["time2"])
    # A decoded MOVE is the identity, including either half of a subdivision.
    for event in reversed(word["program"][:index]):
        op = event[0]
        dst = role(event, 1, size)
        if op == "MOVE":
            continue
        if op in ("INIT", "CLEAR"):
            vector[dst] = Fraction(0)
        elif op == "SCALE":
            vector[dst] *= Fraction(event[-2])
        else:
            require(op in ("ADD", "COPY"), "Oracle prefix opcode")
            src = role(event, 2, size)
            require(src != dst, "Oracle distinct prefix operands")
            vector[src] += Fraction(event[-2]) * vector[dst]
            if op == "COPY":
                vector[dst] = Fraction(0)
    return vector


def forward_delivery(word, contact):
    """Inject one perturbation, then execute the remaining decoded program."""
    size = word["public"] + word["owned_fields"]
    vector = [Fraction(0) for _ in range(size)]
    target = contact["role"]
    require(type(target) is int and 0 <= target < size, "Oracle injection role")
    vector[target] = Fraction(contact["coefficient"])
    index, midpoint = split_time(word, contact["time2"])
    for event in word["program"][index + midpoint:]:
        op = event[0]
        dst = role(event, 1, size)
        if op == "MOVE":
            continue
        if op in ("INIT", "CLEAR"):
            vector[dst] = Fraction(0)
        elif op == "SCALE":
            vector[dst] *= Fraction(event[-2])
        else:
            require(op in ("ADD", "COPY"), "Oracle forward opcode")
            src = role(event, 2, size)
            require(src != dst, "Oracle distinct forward operands")
            value = Fraction(event[-2]) * vector[src]
            vector[dst] = value if op == "COPY" else vector[dst] + value
    return vector


def run():
    raw = authenticated("WORD.json.gz", WORD_SHA256, WORD_BLOB)
    word = json.loads(gzip.decompress(raw))
    plan = json.loads(authenticated("PLAN.json", PLAN_SHA256, PLAN_BLOB))
    canonical = json.dumps(word, sort_keys=True, separators=(",", ":")).encode()
    require(sha256(canonical).hexdigest() == CANONICAL_WORD
            == plan["source_canonical_sha256"], "Oracle canonical source word")
    step = plan["steps"][0]
    require((word["public"], word["owned_fields"], len(word["program"]))
            == (767, 22, 25882), "Oracle fixed input inventory")
    require((step["pivot"], step["frame"], step["time2"], step["queries"])
            == (696, 1031, 27044, [13750]), "Oracle fixed first-step scope")
    require(step["source_sha256"] == CANONICAL_WORD, "Oracle step source pin")
    require(step["collection"] == [{"time2": 27026, "role": 696,
                                     "coefficient": "1"}], "Oracle fixed collection")
    require([(c["time2"], c["role"], c["coefficient"])
             for c in step["injection"]]
            == [(27044, 696, "1"), (27044, 697, "1"),
                (27501, 770, "1"), (27516, 699, "1")],
            "Oracle fixed injections")
    size = word["public"] + word["owned_fields"]
    collected = [Fraction(0) for _ in range(size)]
    delivered = [Fraction(0) for _ in range(size)]
    for contact in step["collection"]:
        vector = prefix_functional(word, contact)
        collected = [left + right for left, right in zip(collected, vector)]
    individual = []
    for contact in step["injection"]:
        vector = forward_delivery(word, contact)
        delivered = [left + right for left, right in zip(delivered, vector)]
        individual.append({"time2": contact["time2"], "role": contact["role"],
                           "delivered": sparse(vector)})
    require(sparse(collected) == {"696": "1"} == step["input"],
            "Oracle exact collection on all input axes")
    require(sparse(delivered) == step["output"],
            "Oracle exact delivery on all output axes")
    pairing = sum((a * b for a, b in zip(collected, delivered)), Fraction(0))
    require(pairing == 1 and delivered[696] == 1, "Oracle unit pairing and pivot")
    main = set(word["live"]) | {r + 112 for r in word["live"]}
    support = {i for i in range(size) if collected[i] or delivered[i]}
    require(all(i < word["public"] and i not in main
                and word["initial"][i] == 3 and word["final"][i] == 127
                for i in support), "Oracle independent full-boundary support")
    require(133 in support and 133 not in main,
            "Oracle derives helper eligibility without an ID cutoff")
    # Here c=e_696 and d_696=1, so Q=I+(d-e_696)e_696^T. These
    # literal source column/row checks establish TQ=QT without assuming a
    # complete source endpoint theorem or replaying all its columns.
    for index in sorted(support):
        column = forward_delivery(word, {"time2": 0, "role": index,
                                         "coefficient": "1"})
        require(sparse(column) == {str(index): "1"},
                "Oracle source identity column on basis support")
    row = prefix_functional(word, {"time2": 2 * len(word["program"]),
                                   "role": 696, "coefficient": "1"})
    require(sparse(row) == {"696": "1"},
            "Oracle source pivot row including arbitrary outside inputs")
    return {
        "status": "PASS_P104_ASYNC_FIRST_HUB_ORACLE",
        "source_word_sha256": WORD_SHA256,
        "canonical_word_sha256": CANONICAL_WORD,
        "plan_sha256": PLAN_SHA256,
        "axes": size,
        "input_row": sparse(collected),
        "output_column": sparse(delivered),
        "individual_injections": individual,
        "unit_pairing": str(pairing),
        "eligible_support": sorted(support),
        "source_identity_columns": sorted(support),
        "source_identity_row": 696,
        "basis_commutes_with_literal_source": True,
        "scope": "Exact decoded temporal identities only; native phases, physical "
                 "contact legality, full source endpoint and complete price remain "
                 "separate obligations.",
    }


if __name__ == "__main__":
    result = run()
    expected = json.loads((HERE / "ORACLE.json").read_bytes())
    require(json.dumps(result, sort_keys=True, separators=(",", ":"))
            == json.dumps(expected, sort_keys=True, separators=(",", ":")),
            "Frozen independent oracle receipt differs")
    print(json.dumps(result, indent=2, sort_keys=True))
