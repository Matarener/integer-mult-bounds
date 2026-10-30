"""Exact finite prefix-code certificate. Produced by Nick Petalas. Apache-2.0."""

from collections import Counter
from fractions import Fraction
import hashlib
import heapq
import json
from pathlib import Path
import sys


PROFILE = {1: 8, 2: 24, 8: 1}
SOURCE_PATHS = {
    "research/p104-restricted-update-codes/README.md",
    "research/p104-restricted-update-codes/RESULT.json",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(raw, digest):
    require(hashlib.sha256(raw).hexdigest() == digest, "source hash mismatch")


def source_profile(package):
    root = package.parent.parent
    manifest = json.loads((package / "SOURCES.json").read_text())
    require(len(manifest["files"]) == 4, "manifest capacity")
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    require({row["path"] for row in rows} == SOURCE_PATHS, "input inventory")
    require(len(rows) == 2, "duplicate input")
    payloads = {}
    for row in rows:
        path = root / row["path"]
        require(path.is_file() and not path.is_symlink(), "regular source file")
        require(path.stat().st_size <= 200_000, "source size bound")
        raw = path.read_bytes()
        authenticate(raw, row["sha256"])
        payloads[row["path"]] = raw
    raw = payloads["research/p104-restricted-update-codes/RESULT.json"]
    published = json.loads(raw)
    record = published["censuses"][1]
    require(record["rank"] == 2 and record["cosets"] == 64, "source selector")
    coordinate = record["coordinates"][0]
    require(coordinate["coordinate"] == 0, "coordinate selector")
    step = coordinate["steps"][1]
    require(step["step"] == 2, "step selector")
    profile = {int(key): value for key, value in step["fiber_histogram"].items()}
    require(profile == PROFILE, "published premise differs from claimed profile")
    return profile, payloads


def construct(profile):
    require(profile == PROFILE, "unsupported profile")
    result = [(8, "000")]
    result.extend((2, format(value, "05b")) for value in range(4, 28))
    result.extend((1, format(value, "06b")) for value in range(56, 64))
    return tuple(result)


def validate(code):
    require(len(code) == 33, "code must have 33 states")
    require(Counter(weight for weight, _ in code) == Counter({8: 1, 2: 24, 1: 8}),
            "code weights")
    words = [word for _, word in code]
    require(all(isinstance(word, str) and 1 <= len(word) <= 6 for word in words),
            "word length")
    require(all(set(word) <= {"0", "1"} for word in words), "binary word")
    require(len(set(words)) == 33, "duplicate word")
    for i, word in enumerate(words):
        for j, other in enumerate(words):
            require(i == j or not other.startswith(word), "prefix collision")
    require(sum(Fraction(1, 1 << len(word)) for word in words) == 1, "Kraft sum")
    for weight, word in code:
        require(Fraction(weight, 64) == Fraction(1, 1 << len(word)),
                "entropy equality")
    return sum(Fraction(weight * len(word), 64) for weight, word in code)


def decode(stream, code):
    require(isinstance(stream, str) and len(stream) <= 12, "stream bound")
    require(set(stream) <= {"0", "1"}, "stream alphabet")
    dictionary = {word: i for i, (_, word) in enumerate(code)}
    labels, pending = [], ""
    for bit in stream:
        pending += bit
        if pending in dictionary:
            labels.append(dictionary[pending])
            pending = ""
        require(len(pending) <= 6, "unknown prefix")
    require(not pending, "truncated label")
    return tuple(labels)


def replacement(code, source, target):
    require(0 <= source < 33 and 0 <= target < 33, "state range")
    weight, before = code[source]
    next_weight, after = code[target]
    require(weight == next_weight, "update changes fiber size")
    require(len(before) == len(after), "update changes packed boundary")
    return after


def huffman_weighted_length(weights):
    """Independent classical merge-cost calculation, not the code builder."""
    require(len(weights) == 33 and all(0 < w <= 8 for w in weights), "weights")
    queue = list(weights)
    heapq.heapify(queue)
    total = 0
    for _ in range(32):
        first, second = heapq.heappop(queue), heapq.heappop(queue)
        merged = first + second
        total += merged
        heapq.heappush(queue, merged)
    require(len(queue) == 1 and queue[0] == 64, "merge conservation")
    return total


def finite_certificate(code):
    mean = validate(code)
    require(mean == Fraction(39, 8), "claimed mean")
    weighted = [i for i, (weight, _) in enumerate(code) for _ in range(weight)]
    require(len(weighted) == 64, "source model capacity")
    require(sum(len(code[i][1]) for i in weighted) == 312, "total source length")
    require(huffman_weighted_length([w for w, _ in code]) == 312, "optimal merge cost")
    transitions = concatenations = 0
    for source, (weight, before) in enumerate(code):
        require(decode(before, code) == (source,), "single decoding")
        for target, (next_weight, _) in enumerate(code):
            if weight != next_weight:
                continue
            after = replacement(code, source, target)
            require(replacement(code, target, source) == before, "inverse pair")
            transitions += 1
            for neighbor, (_, suffix) in enumerate(code):
                original = before + suffix
                changed = after + original[len(before):]
                require(decode(original, code) == (source, neighbor), "original parse")
                require(decode(changed, code) == (target, neighbor), "updated parse")
                require(len(changed) == len(original), "packed size")
                concatenations += 1
    require(transitions == 641 and concatenations == 21_153, "coverage counts")
    return dict(states=33, source_points=64, weighted_bits=312, mean_bits=str(mean),
                max_bits=6, same_weight_pairs=transitions, packed_cases=concatenations)


def controls(code, payloads):
    rejected = 0
    broken = [code[:-1], ((8, "00"),) + code[1:],
              ((8, "00100"),) + code[1:], code[:-1] + (code[-2],),
              ((0, "000"),) + code[1:], ((8, "00x"),) + code[1:]]
    for candidate in broken:
        try:
            validate(candidate)
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("invalid code accepted")
    for source, target in ((0, 1), (1, 25), (-1, 1), (1, 33)):
        try:
            replacement(code, source, target)
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("invalid transition accepted")
    for stream in ("11111", "000x", "0" * 13):
        try:
            decode(stream, code)
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("invalid stream accepted")
    for raw in payloads.values():
        try:
            authenticate(raw + b"\n", hashlib.sha256(raw).hexdigest())
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("corrupted source accepted")
    require(rejected == 15, "rejection count")
    return rejected


def main():
    package = Path(__file__).resolve().parent
    profile, payloads = source_profile(package)
    code = construct(profile)
    result = finite_certificate(code)
    result["rejected_controls"] = controls(code, payloads)
    files = [path for path in package.iterdir() if path.is_file()]
    require(len(files) == 6, "unexpected package inventory")
    result["package_sha256"] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in sorted(files)}
    result["input_sha256"] = {name: hashlib.sha256(raw).hexdigest()
                              for name, raw in sorted(payloads.items())}
    result["python"] = sys.version.split()[0]
    result["code"] = [dict(state=i, weight=w, bits=b)
                      for i, (w, b) in enumerate(code)]
    print(json.dumps(result, sort_keys=True))
    print("PASS_P104_PREFIX_UPDATE_LABELS mean_bits=39/8 max_bits=6")


if __name__ == "__main__":
    main()
