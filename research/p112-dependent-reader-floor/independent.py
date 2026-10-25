"""Separate finite-field and expanded-identity checks. Nick Petalas. Apache-2.0."""

import itertools
import json
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def bounded_bytes(path, capacity):
    require(0 < capacity <= 1_048_576, "read capacity")
    with path.open("rb") as stream:
        raw = stream.read(capacity + 1)
    require(len(raw) <= capacity, "bounded input")
    return raw


def finite_fields():
    records = []
    for prime in (2, 3, 5, 7):
        projective = [(0, 1)] + [(1, t) for t in range(prime)]
        cases = coefficients = axis_outputs = 0
        for count in (2, 3):
            for old in itertools.combinations(projective, count):
                maps = [
                    new
                    for new in itertools.permutations(((1, 0), (0, 1), (1, 1)), count)
                    if all(
                        not new[i][j] or old[i][j]
                        for i in range(count)
                        for j in range(2)
                    )
                ]
                require(bool(maps), "axis-preserving injection exists")
                new = maps[-1]
                for values in itertools.product(range(prime), repeat=count):
                    coefficients += 1
                    target = tuple(
                        sum(v * d[j] for v, d in zip(values, old, strict=True)) % prime
                        for j in range(2)
                    )
                    if target not in ((0, 0), (1, 0), (0, 1)):
                        continue
                    active = [i for i, v in enumerate(values) if v]
                    possible = set()
                    for mask in range(1 << len(active)):
                        possible.add(
                            tuple(
                                sum(
                                    new[i][j]
                                    for k, i in enumerate(active)
                                    if mask >> k & 1
                                )
                                % 2
                                for j in range(2)
                            )
                        )
                    require(target in possible, "pointwise reader support")
                    axis_outputs += target != (0, 0)
                cases += 1
        records.append(
            {
                "prime": prime,
                "direction_sets": cases,
                "coefficient_tuples": coefficients,
                "axis_outputs": axis_outputs,
            }
        )
    return records


def set_rank(matrix):
    require(len(matrix) <= 112, "matrix row bound")
    basis = {}
    for original in matrix:
        row = set(original)
        for pivot in range(111, -1, -1):
            if pivot not in row:
                continue
            if pivot in basis:
                row.symmetric_difference_update(basis[pivot])
            else:
                basis[pivot] = row
                break
    return len(basis)


def expanded_identity():
    meta = json.loads(bounded_bytes(HERE / "SOURCES.json", 32768))
    pin = next(row for row in meta["files"] if row["usage"] == "input")
    raw = bounded_bytes(HERE.parents[1] / pin["path"], 1_048_576)
    require(
        len(raw) < 1_048_576 and sha256(raw).hexdigest() == pin["sha256"], "live labels"
    )
    recipes = json.loads(raw)["recipes"]
    require(len(recipes) == 112, "112 labels")
    labels = [row["q"] for row in sorted(recipes, key=lambda row: row["port"])]
    vectors = [tuple((q // (2**bit)) % 2 for bit in range(9)) for q in labels]
    retained = bounded_bytes(HERE / "RETAINED-RANK32.json", 32768)
    require(
        sha256(retained).hexdigest() == meta["retained_rank32"]["sha256"],
        "retained groups",
    )
    groups = json.loads(retained)["orthonormal_groups"]
    require(
        len(groups) == 16 and sorted(p for g in groups for p in g) == list(range(112)),
        "partition",
    )
    require(all(len(g) in (4, 6, 8) for g in groups), "even group capacity")
    owners = {
        p: g[i : i + 2]
        for g in groups
        for i in range(0, len(g), 2)
        for p in g[i : i + 2]
    }
    half = {p: (i, j % 2) for i, g in enumerate(groups) for j, p in enumerate(g)}
    pairings = [
        [sum(x * y for x, y in zip(v, w, strict=True)) % 2 for w in vectors]
        for v in vectors
    ]
    tariff = 0
    for g in groups:
        gram = [{q for q in g if pairings[p][q]} for p in g]
        require(set_rank(gram) == len(g), "full orthonormal group rank")
        tariff += 2 * set_rank(gram)
    for p, q in itertools.product(range(112), repeat=2):
        scalar = int(half[p] == half[q])
        for i, j in itertools.product(range(2), repeat=2):
            value = scalar * pairings[owners[p][i]][owners[q][j]]
            require(value == int(p == q and i == j), "expanded literal I224")
    require(tariff == 224, "literal tariff")
    return {"expanded_entries": 224**2, "expanded_rank": 224, "literal_tariff": tariff}


def fourth_direction_boundary():
    # Abstract twelve reader sites: each of six direction pairs must serve both axes.
    # This limits the universal binary map. It is not a literal P112 counterexample.
    directions = ((1, 1), (1, 2), (1, 3), (1, 4))
    pairs = tuple(itertools.combinations(range(4), 2))
    require(
        all(directions[j][1] != directions[i][1] for i, j in pairs),
        "rational pair ranks",
    )
    failed = 0
    for images in itertools.product(((0, 0), (1, 0), (0, 1), (1, 1)), repeat=4):
        feasible = True
        for i, j in pairs:
            span = {
                (0, 0),
                images[i],
                images[j],
                tuple(x ^ y for x, y in zip(images[i], images[j], strict=True)),
            }
            feasible &= (1, 0) in span and (0, 1) in span
        failed += not feasible
    require(failed == 256, "four-direction binary-map obstruction")
    return {
        "abstract_reader_sites": 12,
        "binary_maps_rejected": failed,
        "literal_cost_counterexample": False,
    }


def main():
    result = {
        "status": "PASS_SEPARATE_DEPENDENT_CHECK",
        "finite_fields": finite_fields(),
        "identity": expanded_identity(),
        "four_direction_boundary": fourth_direction_boundary(),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
