#!/usr/bin/env python3
"""Exact finite evidence for the common-map tensor-pairing bound; stdlib Python 3.12.

The universal cardinality bound is the written Gram-block argument in PROOF.md.
This checker authenticates its finite model, witnesses, and scope controls. It
does not enumerate embeddings or prove a physical decoder or supplier theorem.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys
import tarfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER = "candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz"
PAYLOAD_SHA = "4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c"
INPUT_PINS = {
    "inputs/BINDING-SOURCE.py": "97440af134482e772f34e2099348625ed0f9b95823cc8cab3a8f5f6148642516",
    "inputs/PORTS.json": "b62117dada0473d3ccaca0d964b67874d468480fc7e19249a090bdd24506405e",
    "inputs/TENSOR-SOURCE.py": "dd3622aaac491bdf4da7906ba344d70907f1b7b898957ec8f511fee9f10684ff",
}
ROOT_INDICES = [0, 1, 8, 16, 39, 64, 68, 99]
TENSOR_INDICES = [0, 15, 1, 14, 2, 13, 3, 12]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def authenticate(data, expected):
    need(digest(data) == expected, "source digest mismatch")


def literal_assignment(source, name):
    values = [node.value for node in ast.walk(ast.parse(source))
              if isinstance(node, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)]
    need(len(values) == 1, "literal assignment count: " + name)
    return ast.literal_eval(values[0])


def source_inputs():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    retained = manifest["retained_inputs"]
    need(len(retained) == len(INPUT_PINS)
         and {entry["path"] for entry in retained} == set(INPUT_PINS),
         "retained input closure")
    for entry in retained:
        need(entry["sha256"] == INPUT_PINS[entry["path"]], "retained input pin")
        data = (HERE / entry["path"]).read_bytes()
        authenticate(data, entry["sha256"])
        need(git_blob(data) == entry["git_blob"], "retained Git blob mismatch")
    runtime = [entry for entry in manifest["files"] if entry["usage"] == "input"]
    need(len(runtime) == 1 and runtime[0]["path"] == ARCHIVE
         and runtime[0]["sha256"] == ARCHIVE_SHA, "runtime source closure")
    archive_bytes = (ROOT / ARCHIVE).read_bytes()
    authenticate(archive_bytes, ARCHIVE_SHA)
    need(git_blob(archive_bytes) == runtime[0]["git_blob"], "selected archive Git blob")
    ports = json.loads((HERE / "inputs/PORTS.json").read_text())
    need(ports["archive_sha256"] == ARCHIVE_SHA and ports["member"] == MEMBER
         and ports["selected_payload_sha256"] == PAYLOAD_SHA, "selected source binding")
    with tarfile.open(ROOT / ARCHIVE, "r:gz") as archive:
        stream = archive.extractfile(MEMBER)
        need(stream is not None, "selected word member")
        payload = gzip.decompress(stream.read())
    authenticate(payload, PAYLOAD_SHA)
    word = json.loads(payload)
    need((word["v"], word["h"], word["R"]) == (112, 9, 480), "selected dimensions")
    need(word["ports"] == ports["ports"], "selected ports extraction")
    declared_map = literal_assignment((HERE / "inputs/BINDING-SOURCE.py").read_text(),
                                      "ROOT_TO_PORT")
    need(declared_map == ports["root_to_port"], "predecessor port map binding")
    base = literal_assignment((HERE / "inputs/TENSOR-SOURCE.py").read_text(), "G0_int")
    need(base == [[2, 1], [1, 2]], "predecessor tensor Gram binding")
    return ports, base


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def geometry():
    # Independent enumeration: doubled norm-two roots, one sign per root line.
    lines = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            lines.append(tuple(row))
    lines += [(1,) + tail for tail in product((-1, 1), repeat=7)
              if tail.count(-1) % 2 == 0]
    frame = []
    for i in range(0, 8, 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[i + 1] = 2, 2 * sign
            frame.append(tuple(row))
    need(len(lines) == len(set(lines)) == 120 and set(frame) <= set(lines),
         "E8 root/frame census")
    live = sorted(set(lines) - set(frame))
    need(len(live) == 112 and all(dot(r, r) == 8 for r in live), "E8 norm/count")
    need(all(dot(a, b) in (-4, 0, 4) for a, b in combinations(live, 2)),
         "distinct-line inner-product alphabet")
    return live


def check_ports(roots, ports, mapping):
    need(len(mapping) == 112 and all(type(i) is int for i in mapping)
         and sorted(mapping) == list(range(112)), "port map is not a bijection")
    need(len(ports) == len(set(ports)) == 112
         and all(type(v) is int and 0 <= v < 512 for v in ports), "port labels")
    need(all(((dot(x, y) // 4 + 1) & 1)
             == ((ports[mapping[i]] & ports[mapping[j]]).bit_count() & 1)
             for i, x in enumerate(roots) for j, y in enumerate(roots)),
         "root-port pairing mismatch")


def rank2(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def kron(a, b):
    return [[x * y for x in row_a for y in row_b]
            for row_a in a for row_b in b]


def tensor_model(base):
    gram = [[1]]
    for _ in range(4):
        gram = kron(gram, base)
    pairing = [[(value + 1) & 1 for value in row] for row in gram]
    check_complement(pairing)
    need(all(gram[i][j] == 2 ** (4 - (i ^ j).bit_count())
             for i in range(16) for j in range(16)), "tensor Gram reconstruction")
    return gram, pairing


def check_complement(pairing):
    need(len(pairing) == 16 and all(len(row) == 16 for row in pairing)
         and all(pairing[i][j] == int(j != (i ^ 15))
                 for i in range(16) for j in range(16)), "complement pairing changed")


def census(pairing):
    rows = [sum(bit << j for j, bit in enumerate(row)) for row in pairing]
    need(rank2(rows) == 16, "full tensor pairing rank")
    cases = Counter()
    rank_only_max = 0
    rank_only_witness = None
    for mask in range(1 << 16):
        size = mask.bit_count()
        complete = sum(bool(mask & (1 << i)) and bool(mask & (1 << (i ^ 15)))
                       for i in range(8))
        single = size - 2 * complete
        actual = rank2(rows[i] & mask for i in range(16) if mask & (1 << i))
        expected = 2 * complete + int(single > 0)
        need(actual == expected, "principal rank formula")
        cases[size, complete, single, actual] += 1
        if actual <= 9 and size > rank_only_max:
            rank_only_max, rank_only_witness = size, mask
    need(rank_only_max == 12 and sum(cases.values()) == 65536, "rank-only screen")
    return {
        "subsets": 65536,
        "full_rank": 16,
        "rank_at_most_nine_maximum_cardinality": rank_only_max,
        "rank_only_witness_indices": [i for i in range(16) if rank_only_witness >> i & 1],
        "warning": "Rank at most nine is necessary only; this is not an injective embedding census.",
        "histogram": [{"size": k, "complete_pairs": p, "singletons": s,
                       "rank": r, "count": count}
                      for (k, p, s, r), count in sorted(cases.items())],
    }


def binary_nine_witness(pairing):
    # The even-weight hyperplane in F2^9 is a nondegenerate alternating space.
    space = [v for v in range(512) if v.bit_count() % 2 == 0]
    symplectic = []
    for _ in range(4):
        a = next(v for v in space if v)
        b = next(v for v in space if (a & v).bit_count() % 2)
        symplectic.extend((a, b))
        space = [v for v in space if (a & v).bit_count() % 2 == 0
                 and (b & v).bit_count() % 2 == 0]
    need(space == [0], "symplectic construction")
    labels = [511 ^ v for v in symplectic] + [511]
    indices = TENSOR_INDICES + [4]
    need(len(set(labels)) == 9 and all(0 <= v < 512 for v in labels),
         "abstract distinct binary labels")
    need(all(((labels[i] & labels[j]).bit_count() & 1) == pairing[x][y]
             for i, x in enumerate(indices) for j, y in enumerate(indices)),
         "abstract nine-label pairing")
    return {"tensor_indices": indices, "labels": labels,
            "scope": "Abstract nine-bit labels, not selected E8 ports."}


def check_common_map(roots, mapping, tensor_indices, pairing):
    need(len(mapping) == len(set(mapping)) == len(tensor_indices)
         and all(type(i) is int and 0 <= i < len(roots) for i in mapping),
         "common root map is not injective")
    need(all(((dot(roots[a], roots[b]) // 4 + 1) & 1) == pairing[x][y]
             for a, x in zip(mapping, tensor_indices)
             for b, y in zip(mapping, tensor_indices)), "common root pairing mismatch")


def require_masked_identity(matrix, gram):
    need(all(matrix[i][j] == 2 * value
             for i, row in enumerate(gram) for j, value in enumerate(row)
             if (value + 1) % 2), "selected masked scalar identity fails")


def root_witness(roots, ports, mapping, tensor_gram, pairing):
    check_common_map(roots, ROOT_INDICES, TENSOR_INDICES, pairing)
    selected = [roots[i] for i in ROOT_INDICES]
    gram = [[dot(a, b) // 4 for b in selected] for a in selected]
    signs = [gram[2 * i][2 * i + 1] for i in range(4)]
    need(signs == [1, 1, -1, -1]
         and all(gram[i][j] == (2 if i == j else signs[i // 2]
                                if i // 2 == j // 2 else 0)
                 for i in range(8) for j in range(8)), "A2 four-pair Gram")
    # Universal block proof uses leading minor2 and determinant3 for either sign.
    need(all(2 > 0 and 2 * 2 - sign * sign == 3 for sign in (-1, 1)),
         "positive Gram block calibration")
    restricted = [[pairing[i][j] for j in TENSOR_INDICES] for i in TENSOR_INDICES]
    need(rank2(sum(v << j for j, v in enumerate(row)) for row in restricted) == 8,
         "eight-root full pairing rank")
    normalized = [[Fraction(2 * tensor_gram[i][j], 8) for j in TENSOR_INDICES]
                  for i in TENSOR_INDICES]
    need(all(normalized[i][i] == 4 for i in range(8)), "normalized tensor diagonal")
    need(normalized[0][2] == 2 and gram[0][2] == 0, "scalar mismatch witness")
    require_masked_identity([[2 * v for v in row] for row in gram], gram)
    return ({
        "root_indices": ROOT_INDICES, "tensor_indices": TENSOR_INDICES,
        "doubled_roots": [list(v) for v in selected], "gram": gram,
        "selected_port_indices": [mapping[i] for i in ROOT_INDICES],
        "selected_port_labels": [ports[mapping[i]] for i in ROOT_INDICES],
        "pairing_rank": 8,
        "common_injective_map_cardinality_upper": 8,
        "upper_bound_basis": "Written positive-definite Gram-block proof; no embedding census.",
        "normalized_scalar_mismatch": {
            "tensor_indices": [TENSOR_INDICES[0], TENSOR_INDICES[2]],
            "root_indices": [ROOT_INDICES[0], ROOT_INDICES[2]],
            "tensor_decoder_entry_after_norm_matching": "2",
            "tensor_decoder_entry_before_norm_matching": str(2 * tensor_gram[0][1]),
            "required_selected_masked_entry": "0",
        },
    }, normalized, gram)


def controls(roots, ports, mapping, pairing, normalized, gram):
    rejected = []

    def reject(name, expected, operation):
        try:
            operation()
        except ValueError as error:
            need(str(error) == expected, "unexpected control failure: " + name)
            rejected.append(name)
        else:
            raise ValueError("negative control accepted: " + name)

    # This nine-index pairing really is preserved when injectivity is dropped:
    # one A2 pair plus seven copies of a line orthogonal to that pair.
    duplicate = [0, 1] + [8] * 7
    duplicate_indices = [0, 15, 1, 2, 3, 4, 5, 6, 7]
    need(all(((dot(roots[a], roots[b]) // 4 + 1) & 1) == pairing[x][y]
             for a, x in zip(duplicate, duplicate_indices)
             for b, y in zip(duplicate, duplicate_indices)),
         "noninjective nine-index pairing calibration")
    reject("duplicate_common_root", "common root map is not injective",
           lambda: check_common_map(roots, duplicate, duplicate_indices, pairing))
    bad_map = mapping[:]
    bad_map[1] = bad_map[0]
    reject("duplicate_port_mapping", "port map is not a bijection",
           lambda: check_ports(roots, ports, bad_map))
    swapped = mapping[:]
    swapped[0], swapped[1] = swapped[1], swapped[0]
    reject("changed_port_mapping", "root-port pairing mismatch",
           lambda: check_ports(roots, ports, swapped))
    bad_ports = ports[:]
    bad_ports[0] ^= 1
    reject("changed_selected_port_label", "root-port pairing mismatch",
           lambda: check_ports(roots, bad_ports, mapping))
    altered = [row[:] for row in pairing]
    altered[0][15] = altered[15][0] = 1
    reject("changed_complement_pair", "complement pairing changed",
           lambda: check_complement(altered))
    reject("pairing_does_not_preserve_scalar_identity", "selected masked scalar identity fails",
           lambda: require_masked_identity(normalized, gram))
    reject("changed_retained_source", "source digest mismatch",
           lambda: authenticate((HERE / "inputs/TENSOR-SOURCE.py").read_bytes() + b"\n",
                                INPUT_PINS["inputs/TENSOR-SOURCE.py"]))
    return rejected


def calculate():
    source, base = source_inputs()
    roots = geometry()
    ports, mapping = source["ports"], source["root_to_port"]
    check_ports(roots, ports, mapping)
    tensor_gram, pairing = tensor_model(base)
    rank_census = census(pairing)
    abstract = binary_nine_witness(pairing)
    witness, normalized, gram = root_witness(roots, ports, mapping, tensor_gram, pairing)
    rejected = controls(roots, ports, mapping, pairing, normalized, gram)
    return {
        "schema_version": 1,
        "source": {"archive_sha256": ARCHIVE_SHA, "selected_payload_sha256": PAYLOAD_SHA,
                   "retained_inputs_sha256": INPUT_PINS},
        "selected_binding": {"live_roots": 112, "checked_pairings": 12544,
                             "selected_label_bits": 9},
        "principal_subset_census": rank_census,
        "abstract_nine_label_control": abstract,
        "sharp_common_map_witness": witness,
        "rejected_controls": rejected,
        "scope": "Full B4 cannot fit any nine-bit bilinear source/reader maps; the sharp subset cap eight requires a common injective E8 root-line map. No physical decoder, supplier, or new kappa.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the recomputed RESULT.json")
    args = parser.parse_args()
    result = calculate()
    path = HERE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(json.loads(path.read_text()) == result, "committed result mismatch")
    print("PASS_TENSOR_PAIRING_EMBEDDING subsets=65536 pairings=12544 "
          "rank_only_max=12 common_root_max=8 abstract_labels=9 controls=7 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, StopIteration) as error:
        print("FAIL_TENSOR_PAIRING_EMBEDDING: " + str(error), file=sys.stderr)
        raise SystemExit(1)
