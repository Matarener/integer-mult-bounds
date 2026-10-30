"""Independent characteristic-zero low-space certificates for the d2 controls.

conorholds, substantial OpenAI Codex assistance. Apache-2.0.
Retains independent.py's PR3161/3162, joaqcoo and DreamingOfClouds E8/P112
geometry and label lineage; predecessor credits remain in SOURCES.json.
Only its independent reconstruction, RREF annihilators and rank helpers are
loaded. Full evaluation matrices over F5 replace the primary F3 differences.
On each flat complement, disjoint sign payloads give T-evaluation rank r
in both F5 and characteristic zero. Rank r+6 modulo five supplies a nonzero
integer minor, so the six quotient columns remain independent modulo T in
characteristic zero. Thus every kernel vector lies entirely in T.
"""

from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
INPUTS = {"research/p112-root-simplex-exclusion/geometry.py",
          "research/one-sided-decoders-all-m/data/data.json"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def regular_bytes(root, name):
    relative = Path(name)
    need(not relative.is_absolute() and relative.parts
         and all(part not in (".", "..") for part in relative.parts),
         "noncanonical input path")
    need(all(not path.is_symlink() for path in (root, *root.parents)),
         "linked input ancestor")
    path = root
    for part in relative.parts:
        path /= part
        need(not path.is_symlink(), "linked input")
    need(path.is_file(), "missing regular input")
    return path.read_bytes()


def authenticate():
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate source JSON key")
            result[key] = value
        return result

    def constant(value):
        raise ValueError("nonfinite source JSON value: " + value)

    sources = json.loads(regular_bytes(PACKAGE, "SOURCES.json"),
                         object_pairs_hook=pairs, parse_constant=constant)
    need(type(sources["schema_version"]) is int and sources["schema_version"] == 1,
         "source schema")
    rows = [row for row in sources["files"] if row["usage"] == "input"]
    need(len(rows) == 2 and {row["path"] for row in rows} == INPUTS,
         "exact live-input inventory")
    hashes = {}
    for row in rows:
        actual = sha256(regular_bytes(ROOT, row["path"])).hexdigest()
        need(actual == row["sha256"], "live-input SHA256 differs: " + row["path"])
        hashes[row["path"]] = actual
    return hashes


def independent_helpers():
    module = ModuleType("independent_d2_geometry")
    path = PACKAGE / "independent.py"
    module.__file__ = str(path)
    exec(compile(regular_bytes(PACKAGE, "independent.py"), str(path), "exec"),
         module.__dict__)
    return (module.independent_model, module.annihilators,
            module.binary_rank, module.rational_rank)


def rank_mod5(rows, width, target):
    """Gaussian elimination on every column of the full evaluation matrix."""
    pivots = [None] * width
    rank = 0
    for original in rows:
        need(len(original) == width, "mod-five matrix width")
        row = [value % 5 for value in original]
        for column in range(width):
            if not row[column]:
                continue
            pivot = pivots[column]
            if pivot is not None:
                factor = row[column]
                for k in range(column, width):
                    row[k] = (row[k] - factor * pivot[k]) % 5
            else:
                inverse = pow(row[column], -1, 5)
                pivots[column] = tuple((inverse * value) % 5 for value in row)
                rank += 1
                if rank == target:
                    return rank
                break
    return rank


def run():
    hashes = authenticate()
    build, annihilators, binary_rank, rational_rank = independent_helpers()
    model = build()
    roots, dots = model["roots"], model["ordinary"]
    live = [i for i, root in enumerate(roots) if root not in model["frame"]]
    frame = [i for i, root in enumerate(roots) if root in model["frame"]]
    need(len(live) == 112 and len(frame) == 8, "live/frame inventories")
    a, b = frame[:2]
    ca = {s: dots[a][s] // 4 for s in live}
    cb = {s: dots[b][s] // 4 for s in live}
    parts = [[s for s in live if ca[s] and not cb[s]],
             [s for s in live if cb[s] and not ca[s]],
             [s for s in live if ca[s] * cb[s] > 0],
             [s for s in live if ca[s] * cb[s] < 0]]
    need([len(part) for part in parts] == [32, 32, 12, 12], "piece sizes")
    pivot = next((s for s in parts[0] if ca[s] == 1), None)
    need(pivot is not None, "positive exclusive-A unit site")
    code = [[dots[f][s] // 4 for s in live] for f in frame]
    need(rational_rank(code) == 8, "frame-code dimension")
    quotient = [tuple(dots[f][s] // 4 for f in frame[2:]) for s in live]
    residues, labels = model["residues"], model["labels"]
    cases, failed_control = [], None

    for t in (2, 3):
        pieces = [part.copy() for part in parts]
        if t == 3:
            pieces[0].remove(pivot)
            pieces.append([pivot])
        group = {s: j for j, part in enumerate(pieces) for s in part}
        need(len(group) == sum(map(len, pieces)), "overlapping low pieces")
        payload = {s: (cb[s] if j == 1 else ca[s]) for s, j in group.items()}
        need(all(abs(value) == 1 for value in payload.values()), "low payload is not a sign")
        low = [[payload[s] if group.get(s) == j else 0 for s in live]
               for j in range(len(pieces))]
        weights = [binary_rank(labels[s] for s in part) for part in pieces]
        need(weights == [7, 7, 7, 7] + ([1] if t == 3 else []), "binary piece weights")
        dimension = 8 + t
        need(rational_rank(low) == t + 2, "low-piece independence")
        need(rational_rank(low + code[2:]) == dimension
             and rational_rank(code + low) == dimension, "code-plus-low dimensions")
        # These are integer evaluations in basis order (T pieces, six frame words).
        evaluations = []
        for position, s in enumerate(live):
            head = [0] * len(pieces)
            if s in group:
                head[group[s]] = payload[s]
            evaluations.append(tuple(head) + quotient[position])

        directions = flats = 0
        t_rank_counts = {}
        for u, v in annihilators():
            directions += 1
            sections = [[], [], [], []]
            for position, s in enumerate(live):
                offset = (((u & residues[s]).bit_count() & 1) << 1
                          | ((v & residues[s]).bit_count() & 1))
                sections[offset].append(position)
            for offset in range(4):
                complement = [position for other in range(4) if other != offset
                              for position in sections[other]]
                meeting = {group[live[position]] for position in complement
                           if live[position] in group}
                # Disjoint nonzero sign payloads give rank(T_eval)=len(meeting).
                t_rank = len(meeting)
                expected = t_rank + 6
                actual = rank_mod5((evaluations[i] for i in complement), dimension, expected)
                need(actual == expected, "affine-six complement has a quotient kernel")
                if failed_control is None:
                    column = len(pieces)
                    mutant = (row[:column] + (0,) + row[column + 1:]
                              for row in (evaluations[i] for i in complement))
                    damaged = rank_mod5(mutant, dimension, expected)
                    need(damaged == expected - 1, "zeroed quotient-column control did not fail")
                    failed_control = {"t": t, "annihilators": [u, v],
                                      "offset": [offset >> 1, offset & 1],
                                      "zeroed_quotient_column": 0,
                                      "rank_before": actual, "rank_after": damaged}
                t_rank_counts[t_rank] = t_rank_counts.get(t_rank, 0) + 1
                flats += 1
        need(directions == 10795 and flats == 43180, "complete ordinary-dot affine-six coverage")
        cases.append({"t": t, "d": 2, "dimension_T": t + 2, "dimension_S": dimension,
                      "piece_sizes": list(map(len, pieces)), "piece_weights": weights,
                      "quotient_dimension": 6, "annihilator_directions": directions,
                      "affine6_flats": flats,
                      "complement_T_rank_counts": {str(k): v for k, v in sorted(t_rank_counts.items())}})

    return {"scope": "independent-d2-low-space-certificates", "field": 5,
            "source_sha256": hashes, "frame_pair": [roots[a], roots[b]],
            "unit_site": roots[pivot], "cases": cases, "failed_control": failed_control}


def main():
    try:
        result = run()
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        print("FAIL_P112_INDEPENDENT_D2: " + str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False))
    print("PASS_P112_INDEPENDENT_D2 field=5 cases=2 affine6_per_case=43180 "
          "scope=independent-low-space-certificates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
