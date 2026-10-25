#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check one compact rational cover; no census or predecessor executable import.

Prepared for ToikY with substantial OpenAI Codex assistance.
"""
import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
MEMBER_SHA = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"


class Rejected(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Rejected(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def decode(data):
    need(len(data) <= 2**21, "JSON size bound")
    return json.loads(data, object_pairs_hook=unique_object)


def integer(x, lo, hi):
    need(type(x) is int and lo <= x <= hi, "strict integer range")
    return x


def dot(a, b):
    return (a & b).bit_count() % 2


def source_labels():
    need(ARCHIVE.stat().st_size <= 2**23, "archive size bound")
    need(hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_SHA, "archive hash")
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        entries = [m for m in archive.getmembers() if m.name == MEMBER]
        need(len(entries) == 1 and entries[0].isreg(), "one regular source member")
        need(entries[0].size <= 2**21, "member size bound")
        with archive.extractfile(entries[0]) as handle:
            raw = handle.read()
    need(hashlib.sha256(raw).hexdigest() == MEMBER_SHA, "member hash")
    data = decode(raw)
    integer(data["ports"], 112, 112)
    need(type(data["recipes"]) is list and len(data["recipes"]) == 112, "112 recipes")
    labels = [None] * 112
    for row in data["recipes"]:
        p = integer(row["port"], 0, 111)
        need(labels[p] is None, "unique source port")
        labels[p] = integer(row["q"], 1, 511)
    need(len(set(labels)) == 112 and all(dot(q, q) == 1 for q in labels), "distinct norm-one labels")
    return labels


def retained_sources():
    origins = decode((HERE / "ORIGINS.json").read_bytes())
    rows = origins["retained_files"]
    need(type(rows) is list and len(rows) == 3, "three retained source files")
    expected = {"inputs/pr3625-README.md", "inputs/pr3625-RESULT.json", "inputs/pr3625-best-32.json"}
    need({row["local_path"] for row in rows} == expected, "retained source paths")
    for row in rows:
        need(row["origin_commit"] == "5cc87895e86a951d43f4725b122a4bcd2675bc43", "retained source commit")
        raw = (HERE / row["local_path"]).read_bytes()
        need(type(row["bytes"]) is int and len(raw) == row["bytes"], "retained byte length")
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "retained SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == row["origin_git_blob"], "retained Git blob")
    budgets = (ROOT / "research/plane-port-copy-budgets/RESULT.json").read_bytes()
    need(hashlib.sha256(budgets).hexdigest() == "253deb61a0c90674726fa77d143e140a8f46012b1bdddc37e6f127ba8a56d464", "copy-budget source hash")
    shrink = decode(budgets)["complex"]["shrink"]
    need(shrink["rank2/incumbent_ceiling"]["charge"] == 164 and
         shrink["rank8/incumbent_ceiling"]["charge"] == 160, "retained tie-budget values")


def rational(value):
    need(type(value) is str and len(value) <= 256, "bounded rational text")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise Rejected("rational weight") from exc
    need(str(result) == value, "canonical rational text")
    return result


def check_cover(data, labels):
    need(type(data) is dict and set(data) == {"schema_version", "dimension", "port_count", "frames", "total_weight", "lost_free_bound"}, "cover schema")
    for key, value in [("schema_version", 1), ("dimension", 9), ("port_count", 112), ("lost_free_bound", 56)]:
        integer(data[key], value, value)
    frames = data["frames"]
    need(type(frames) is list and 1 <= len(frames) <= 112, "compact cover")
    coverage = [Fraction(0) for _ in range(112)]
    total = Fraction(0)
    seen = set()
    for row in frames:
        need(type(row) is dict and set(row) == {"ports", "weight"}, "frame schema")
        ports = row["ports"]
        need(type(ports) is list and len(ports) == 8, "eight ports")
        for p in ports:
            integer(p, 0, 111)
        need(len(set(ports)) == 8, "distinct frame ports")
        key = tuple(sorted(ports))
        need(key not in seen, "distinct frame records")
        seen.add(key)
        for i, a in enumerate(ports):
            for j, b in enumerate(ports):
                need(dot(labels[a], labels[b]) == int(i == j), "Gram I8")
        weight = rational(row["weight"])
        need(weight > 0, "positive weight")
        total += weight
        for p in ports:
            coverage[p] += weight
    need(all(value == 1 for value in coverage), "exact per-port coverage one")
    need(total == rational(data["total_weight"]) == 14, "exact total fourteen")
    return {"frames": len(frames), "ports": 112, "gram_entries": 64 * len(frames),
            "coverage": "1", "total_weight": str(total), "lost_free_upper_bound": 56}


def lost_free(labels, planes):
    need(type(planes) is dict and planes, "nonempty plane assignment")
    for p, r in planes.items():
        integer(p, 0, len(labels) - 1)
        integer(r, 1, 511)
        need(dot(labels[p], labels[p]) == dot(r, r) == 1 and dot(labels[p], r) == 0, "Gram I2 plane")
    for a in planes:
        for b in planes:
            if a != b and dot(labels[a], labels[b]) == 0:
                need(dot(labels[a], planes[b]) == dot(planes[a], labels[b]) == dot(planes[a], planes[b]) == 0, "lost-free cross pair")
    return len(planes)


def controls(data, labels):
    rejected = []

    def reject(name, callback):
        try:
            callback()
        except Rejected:
            rejected.append(name)
        else:
            raise Rejected("control accepted: " + name)

    def mutate(name, change):
        altered = copy.deepcopy(data)
        change(altered)
        reject(name, lambda: check_cover(altered, labels))

    mutate("omitted_frame", lambda x: x["frames"].pop())
    mutate("duplicate_frame", lambda x: x["frames"].__setitem__(1, copy.deepcopy(x["frames"][0])))
    mutate("tiny_weight_error", lambda x: x["frames"][0].update(weight=str(Fraction(x["frames"][0]["weight"]) + Fraction(1, 2**100))))
    mutate("negative_weight", lambda x: x["frames"][0].update(weight="-1"))
    mutate("zero_weight", lambda x: x["frames"][0].update(weight="0"))
    mutate("zero_denominator", lambda x: x["frames"][0].update(weight="1/0"))
    mutate("duplicate_port", lambda x: x["frames"][0]["ports"].__setitem__(1, x["frames"][0]["ports"][0]))
    mutate("boolean_port", lambda x: x["frames"][0]["ports"].__setitem__(0, False))
    mutate("out_of_range_port", lambda x: x["frames"][0]["ports"].__setitem__(0, 112))
    mutate("false_bound", lambda x: x.update(lost_free_bound=55))
    mutate("false_total", lambda x: x.update(total_weight="13"))
    first = data["frames"][0]["ports"]
    bad = next(i for i in range(112) if i not in first and dot(labels[i], labels[first[0]]) == 1)
    mutate("wrong_Gram", lambda x: x["frames"][0]["ports"].__setitem__(1, bad))
    reject("duplicate_JSON_key", lambda: decode(b'{"dimension":9,"dimension":8}'))
    four = {p: labels[r] for p, r in zip(first[:4], first[4:])}
    need(lost_free(labels, four) == 4, "four-plane actual-label positive")
    # The complement of an orthonormal eight-frame has norm one in F2^9.
    complement = 511
    for p in first:
        complement ^= labels[p]
    five = {p: r for p, r in zip(first[:5], [labels[first[5]], labels[first[6]], labels[first[7]], complement,
                                             labels[first[5]] ^ labels[first[6]] ^ labels[first[7]]])}
    need(all(dot(labels[a], labels[b]) == 0 for a in five for b in five if a != b), "five orthogonal q")
    need(all(dot(r, r) == 1 and all(dot(r, labels[p]) == 0 for p in five) for r in five.values()), "all individual and q-r plane tests pass")
    reject("missing_r_r_premise", lambda: lost_free(labels, five))
    reject("degenerate_plane", lambda: lost_free(labels, {first[0]: labels[first[0]]}))
    reject("isotropic_plane", lambda: lost_free(labels, {first[0]: labels[first[1]] ^ labels[first[2]]}))
    return rejected


def run(certificate):
    retained_sources()
    labels = source_labels()
    data = decode(certificate.read_bytes())
    result = check_cover(data, labels)
    witness_bytes = (HERE / "inputs/pr3625-best-32.json").read_bytes()
    need(hashlib.sha256(witness_bytes).hexdigest() == "a98a88ebacc2b8fa3548387c1004cbfcc583ed5a3417b681c08eff68abe75dd6", "predecessor witness hash")
    witness = decode(witness_bytes)
    planes = {}
    for p, r in witness.items():
        need(str(int(p)) == p, "canonical witness port")
        planes[int(p)] = r
    need(lost_free(labels, planes) == 32, "predecessor 32-plane witness")
    result.update(status="PASS_P112_COMPACT_FRACTIONAL_COVER", source_member_sha256=MEMBER_SHA,
                  controls=controls(data, labels), witness_size=32,
                  pricing={"model": "B+2*(112-s), fixed B=72 only", "bound_cost": 184,
                           "size_32_fixed_72_cost": 232, "sizes_33_to_36_costs": [230, 228, 226, 224],
                           "strictly_below_224_min_size": 37, "positive_saving_min_size": 49,
                           "tie_sizes_164_160": [66, 68], "strict_sizes_164_160": [67, 69],
                           "necessary_block_max_for_ties_164_160": [52, 48]})
    need(all(72 + 2 * (112 - s) >= Fraction(1792, 9) for s in range(49)), "positive threshold")
    need(72 + 2 * (112 - 49) < Fraction(1792, 9), "positive threshold attainment arithmetic")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=HERE / "COVER.json")
    parser.add_argument("--write", action="store_true", help="regenerate this package's result only")
    args = parser.parse_args()
    result = run(args.certificate)
    if args.write:
        need(args.certificate.resolve() == (HERE / "COVER.json").resolve(), "write uses owned certificate")
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(result == decode((HERE / "RESULT.json").read_bytes()), "result receipt mismatch")
    print("PASS_P112_COMPACT_FRACTIONAL_COVER frames=" + str(result["frames"]) +
          " coverage=1 weight=14 bound=56 controls=" + str(len(result["controls"])) + " no_new_kappa")


if __name__ == "__main__":
    main()
