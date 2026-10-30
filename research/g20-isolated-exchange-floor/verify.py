#!/usr/bin/env python3
"""Independent distance-label check, without BFS or generator imports.

Charan ., with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha1, sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
IDENTITY = 0x8421


def need(condition, message):
    if not condition:
        raise ValueError(message)


def invertible(matrix):
    # Independent column-span enumeration, including every singular encoding.
    span = {0}
    for column in range(4):
        vector = sum(((matrix >> (4 * row + column)) & 1) << row for row in range(4))
        if vector in span:
            return False
        span |= {x ^ vector for x in span}
    return len(span) == 16


def right_neighbors(matrix):
    # The generator uses left row additions. Check right column additions,
    # extracting individual bits instead of reusing the generator's row step.
    for source in range(4):
        for target in range(4):
            if source != target:
                change = sum(((matrix >> (4 * row + source)) & 1)
                             << (4 * row + target) for row in range(4))
                yield matrix ^ change


def check_labels(labels, full_inventory=True):
    need(len(labels) == 65536, "complete 16-bit matrix inventory")
    states = [i for i, x in enumerate(labels) if x != 255]
    need(len(states) == 20160, "exact GL(4,2) cardinality")
    need(labels[IDENTITY] == 0 and all(labels[i] > 0 for i in states if i != IDENTITY),
         "unique zero is identity")
    if full_inventory:
        need(all((labels[i] != 255) == invertible(i) for i in range(65536)),
             "every invertible and singular matrix classified independently")
    edges = 0
    for state in states:
        neighbors = list(right_neighbors(state))
        need(all(labels[n] != 255 and abs(labels[state] - labels[n]) <= 1 for n in neighbors),
             "closed graph and 1-Lipschitz distance labels")
        if state != IDENTITY:
            need(any(labels[n] + 1 == labels[state] for n in neighbors),
                 "descending witness from every nonidentity")
        edges += len(neighbors)
    need(edges == 241920, "all twelve ADD neighbors of every GL4 element")
    return Counter(labels[i] for i in states)


def encode(rows):
    return sum(row << (4 * i) for i, row in enumerate(rows))


def replay(word):
    # Literal action on all Boolean inputs, separate from row/column labels.
    outputs = []
    for value in range(16):
        bits = [(value >> i) & 1 for i in range(4)]
        for d, s in word:
            need(type(d) is int and type(s) is int and 0 <= d < 4 and 0 <= s < 4 and d != s,
                 "legal ADD operands")
            bits[d] = (bits[d] + bits[s]) % 2
        outputs.append(sum(bit << i for i, bit in enumerate(bits)))
    return outputs


def check_endpoints(certificate, labels):
    expected = {(a << 2, b << 2, c, d)
                for a in range(1, 4) for b in range(1, 4) if a != b
                for c in range(1, 4) for d in range(1, 4) if c != d}
    seen, histogram = set(), Counter()
    for endpoint in certificate["endpoints"]:
        rows, word = tuple(endpoint["rows"]), endpoint["word"]
        need(rows in expected and rows not in seen, "one witness for each exchange map")
        seen.add(rows)
        length = endpoint["distance"]
        need(len(word) == length == labels[encode(rows)], "attaining shortest length")
        truth = [sum(((row & value).bit_count() % 2) << i for i, row in enumerate(rows))
                 for value in range(16)]
        need(replay(word) == truth, "every input of every attaining word")
        histogram[length] += 1
    need(seen == expected and len(seen) == 36, "all independent GL2 block pairs")
    need(histogram == Counter({6: 2, 7: 8, 8: 24, 9: 2}), "exchange distance histogram")
    return histogram


def boundary_matrix(program):
    rows = [1 << i for i in range(32)]
    for op, d, s in program:
        need(0 <= d < 32 and 0 <= s < 32 and d != s, "source boundary operands")
        if op == "ADD":
            rows[d] ^= rows[s]
        else:
            need(op == "SWAP", "source opcode")
            rows[d], rows[s] = rows[s], rows[d]
    return rows


def check_source(controller):
    diagonal = controller["diagonal"]
    need(all(diagonal[2*j] == diagonal[2*j+1] for j in range(16)), "actual equal-target pair contract")
    right, left = [controller["boundaries"][s + "_program"] for s in ("right", "left")]
    need(left == right[::-1], "source inverse boundary")
    need(len(right) == 22 and all(e[0] == "ADD" for e in right[:14])
         and all(e[0] == "SWAP" for e in right[14:]), "fixed 14-ADD then exchange factorization")
    need(boundary_matrix(right) == controller["boundaries"]["right_rows"]
         and boundary_matrix(left) == controller["boundaries"]["left_rows"], "source matrices")
    need(boundary_matrix(right + left) == [1 << i for i in range(32)], "exact inverse")
    components = {}
    for _, d, s in right[14:]:
        banks = tuple(sorted((d // 2, s // 2)))
        need(banks[0] != banks[1], "exchange distinct banks")
        components.setdefault(banks, []).append((d, s))
    need(set(components) == {(7, 15), (8, 14), (9, 13), (10, 12)}, "four actual mirror-bank exchanges")
    used = set()
    for banks, swaps in components.items():
        wires = [2*b + i for b in banks for i in range(2)]
        need(not used.intersection(wires), "disjoint exchange components")
        used.update(wires)
        need(len(swaps) == 2 and sorted(x for pair in swaps for x in pair) == wires,
             "whole rank-two bank exchange")
        word = []
        for d, s in swaps:
            d, s = wires.index(d), wires.index(s)
            word += [[d, s], [s, d], [d, s]]
        truth = replay(word)
        rows = [sum(((truth[1 << c] >> r) & 1) << c for c in range(4)) for r in range(4)]
        need(all(0 < x < 16 for x in rows) and rows[0] & 3 == rows[1] & 3 == 0
             and rows[2] & 12 == rows[3] & 12 == 0, "attaining anti-diagonal block map")
    need(controller["boundaries"]["boundary_unit_ADDs_per_port"] == 76, "source total 2*(14+4*6)")
    return sorted([list(x) for x in components])


def rejects(label, function):
    try:
        function()
    except ValueError:
        return label
    raise ValueError("semantic corruption accepted: " + label)


def run():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    raw = (HERE / "inputs/CONTROLLER.json").read_bytes()
    need(sha256(raw).hexdigest() == sources["controller_source"]["sha256"], "frozen controller bytes")
    need(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
         == sources["controller_source"]["git_blob"], "source Git blob identity")
    controller = json.loads(raw)
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    labels = (HERE / "distances.bin").read_bytes()
    need(sha256(labels).hexdigest() == certificate["distance_table_sha256"], "distance-table digest")
    levels = check_labels(labels)
    need(dict(sorted(levels.items())) == {int(k): v for k, v in certificate["levels"].items()}, "distance levels")
    need(certificate["schema"] == "g20-isolated-exchange-distance/v1"
         and certificate["invertible_states"] == 20160 and certificate["directed_edges"] == 241920
         and certificate["exchange_minimum"] == 6, "certificate counts and scoped floor")
    histogram = check_endpoints(certificate, labels)
    need(histogram == {int(k): v for k, v in certificate["exchange_histogram"].items()}, "endpoint histogram")
    components = check_source(controller)
    controls = []
    bad = bytearray(labels)
    bad[encode(certificate["endpoints"][0]["rows"])] = 5
    controls.append(rejects("false five-ADD exchange label", lambda: check_labels(bad, False)))
    bad_zero = bytearray(labels)
    bad_zero[0] = 1
    bad_zero[0x8423] = 255
    controls.append(rejects("cardinality-preserving singular substitution", lambda: check_labels(bad_zero)))
    bad_endpoint = deepcopy(certificate)
    bad_endpoint["endpoints"][0]["word"].pop()
    controls.append(rejects("deleted attaining ADD", lambda: check_endpoints(bad_endpoint, labels)))
    bad_source = deepcopy(controller)
    bad_source["diagonal"][1] ^= 1
    controls.append(rejects("unequal target pair", lambda: check_source(bad_source)))
    bad_source2 = deepcopy(controller)
    bad_source2["boundaries"]["right_program"][-1][2] = 26
    controls.append(rejects("changed exchange wire", lambda: check_source(bad_source2)))
    print(json.dumps(dict(status="PASS_G20_ISOLATED_EXCHANGE_FLOOR", states=20160,
        directed_edges=241920, endpoint_maps=36, exchange_histogram=dict(sorted(histogram.items())),
        minimum_ADDs=6, components=components, fixed_chain_ADDs=14,
        isolated_boundary_pair_floor=76, ports=111, scalar_ADD_floor=8436,
        controls=controls, new_kappa=False), sort_keys=True))


if __name__ == "__main__":
    run()
