"""Separate Fraction elimination for the pinned local rational frame geometry.

No primary engine or retained producer is imported. Shared source geometry
is explicit: this cross-checks Q ranks and MOVE containment, not its origin,
odd-characteristic projector laws, numeric RAW/VALUE operations, or callers.
Prepared by ToikY with substantial OpenAI Codex assistance, Apache-2.0.
"""

from fractions import Fraction
import gzip
import hashlib
import io
import json
from pathlib import Path


PINS = {
    "WORD.json.gz": "69fc50430f0062c040e0686f59ad32ee5af2387ae9a97d7d11b4af1aa994ed5b",
    "GEOMETRY.json.gz": "a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022",
}


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                    separators=(",", ":")).encode("ascii")).hexdigest()


def load_data():
    directory = Path(__file__).resolve().parent / "source/provider/inputs"
    result = {}
    for name, expected in PINS.items():
        path = directory / name
        require(path.is_file() and not path.is_symlink(), "regular pinned oracle input")
        require(path.stat().st_size <= 16_000_000, "compressed oracle input bound")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == expected, "oracle input SHA256")
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            decoded = stream.read(16_000_001)
        require(len(decoded) <= 16_000_000, "decoded oracle input bound")
        result[name] = json.loads(decoded)
    return result["WORD.json.gz"], result["GEOMETRY.json.gz"]


def basis(rows, dimension):
    """Gauss-Jordan row space over Q, using division by Fraction pivots."""
    require(all(len(row) == dimension for row in rows), "oracle vector dimension")
    matrix = [[Fraction(value) for value in row] for row in rows]
    pivot_row = 0
    for column in range(dimension):
        candidate = next((index for index in range(pivot_row, len(matrix))
                          if matrix[index][column] != 0), None)
        if candidate is None:
            continue
        matrix[pivot_row], matrix[candidate] = matrix[candidate], matrix[pivot_row]
        divisor = matrix[pivot_row][column]
        matrix[pivot_row] = [value / divisor for value in matrix[pivot_row]]
        for index in range(len(matrix)):
            if index == pivot_row:
                continue
            multiplier = matrix[index][column]
            if multiplier:
                matrix[index] = [a - multiplier * b
                                 for a, b in zip(matrix[index], matrix[pivot_row])]
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return tuple(tuple(row) for row in matrix[:pivot_row])


def check(primary):
    word, geometry = load_data()
    require(geometry["h"] == 8 and geometry["v"] == 111, "local oracle geometry")
    roots, frames = geometry["lines"], geometry["frames"]
    require(len(roots) == 111 and len(frames) == 636, "complete oracle frame catalogue")
    require(all(len(row) == 8 and all(type(x) is int for x in row) for row in roots),
            "integer oracle root vectors")
    require(all(isinstance(frame, list) and len(frame) == len(set(frame))
                and all(type(x) is int and 0 <= x < len(roots) for x in frame)
                for frame in frames), "oracle frame members")
    spaces = [basis([roots[index] for index in frame], 8) for frame in frames]
    ranks = [len(space) for space in spaces]
    require(all(type(x) is int for x in primary["rational_frame_ranks"])
            and primary["rational_frame_ranks"] == ranks, "all Fraction ranks agree")

    pairs = sorted({(row[2], row[3]) for row in word["records"] if row[0] == 0})
    require(pairs, "actual MOVE pair domain")
    require(word["namespace"] == 658 and len(word["start"]) == len(word["final"]) == 658,
            "actual WORD namespace; historical geometry namespace not reused")
    for name, reverse in (("forward", False), ("reverse", True)):
        transitions = [row for row in primary["orientations"][name]["paid_transition_records"]
                       if row["kind"] == "MOVE"]
        normalized = {(row["to_frame"], row["from_frame"]) if reverse else
                      (row["from_frame"], row["to_frame"]) for row in transitions}
        require(normalized == set(pairs), "actual MOVE pair coverage in both orientations")
        for row in transitions:
            low, high = ((row["to_frame"], row["from_frame"]) if reverse else
                         (row["from_frame"], row["to_frame"]))
            require(row["nested_over_Q"] is True and
                    row["derived_paid_rank"] == ranks[high] - ranks[low],
                    "primary containment and paid rank claims agree")

    certificates = []
    for low, high in pairs:
        union_rank = len(basis(spaces[high] + spaces[low], 8))
        require(union_rank == ranks[high], "Fraction union-rank MOVE containment")
        increment = ranks[high] - ranks[low]
        require(0 < increment < 8, "Fraction-derived proper positive MOVE rank")
        certificates.append({"lower_frame": low, "upper_frame": high,
                             "lower_rank": ranks[low], "upper_rank": ranks[high],
                             "union_rank": union_rank, "paid_rank": increment})

    # A same-rank replacement must still satisfy containment. Find an actual
    # nonzero lower frame and demonstrate that rank alone is insufficient.
    control = None
    for low, high in pairs:
        if not ranks[low]:
            continue
        for replacement, rank in enumerate(ranks):
            if rank == ranks[high]:
                union_rank = len(basis(spaces[replacement] + spaces[low], 8))
                if union_rank > rank:
                    control = {"lower_frame": low, "original_upper_frame": high,
                               "replacement_upper_frame": replacement,
                               "unchanged_upper_rank": rank, "union_rank": union_rank,
                               "nonnested_same_rank_rejected": True}
                    break
        if control is not None:
            break
    require(control is not None, "discriminating Fraction containment control")
    require(len(basis([[2, 0], [0, 2]], 2)) == 2,
            "rational arithmetic does not collapse even integer vectors")
    serialized_spaces = [[[[v.numerator, v.denominator] for v in row]
                          for row in space] for space in spaces]
    return {"status": "PASS_SEPARATE_FRACTION_LOCAL_GEOMETRY",
            "arithmetic": "Fraction Gauss-Jordan rank and union-rank containment over Q",
            "source_geometry": "shared pinned source; no primary or producer imports",
            "frames_checked": len(frames), "frame_ranks": ranks,
            "unique_actual_MOVE_pairs": len(pairs), "MOVE_pair_certificates": certificates,
            "rational_spaces_sha256": digest(serialized_spaces),
            "MOVE_certificates_sha256": digest(certificates),
            "control": control, "even_integer_Q_rank_control": True,
            "scope": "Local Q spans and MOVE paid ranks only; not odd-prime Gram, numeric COPY/ERASE/SOURCE, operator, native, caller, physical or outer verification."}
