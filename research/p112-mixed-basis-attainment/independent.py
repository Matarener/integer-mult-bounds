"""Raw scalar factors and actual rectangular Gram matrices. Apache-2.0."""

import hashlib
import importlib.util
import itertools
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def boundary(directory):
    spec = importlib.util.spec_from_file_location(
        "input_boundary", directory / "verify.py"
    )
    require(spec is not None and spec.loader is not None, "boundary loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Only byte/contract parsing is shared. No mask, criterion or tariff code is called.
    return module.load(directory)


def row_rank(rows):
    work = list(rows)
    used = 0
    for bit in range(71, -1, -1):
        found = next((j for j in range(used, len(work)) if work[j] & (1 << bit)), None)
        if found is None:
            continue
        work[used], work[found] = work[found], work[used]
        for j in range(used + 1, len(work)):
            if work[j] & (1 << bit):
                work[j] ^= work[used]
        used += 1
    return used


def geometry(case):
    labels = [[] for _ in case["cells"]]
    offsets = []
    offset = 0
    for block in case["blocks"]:
        offsets.append(offset)
        offset += block["dimension"]
    for i, cell in enumerate(case["cells"]):
        for h, j in cell["ports"]:
            labels[i].append(case["blocks"][h]["bases"][cell["group"]][j] << offsets[h])
    require(offset <= 24 and sum(map(len, labels)) <= 72, "raw geometry limit")
    return labels


def factors(case, parameter, family):
    count = len(case["cells"]) + 2
    a = [int(i < count - 2 and case["cells"][i]["group"] == "A") for i in range(count)]
    b = [int(i < count - 2 and case["cells"][i]["group"] == "B") for i in range(count)]
    c = [int(i < count - 2 and case["cells"][i]["group"] == "C") for i in range(count)]
    queries, readers = [[] for _ in range(4)], [[] for _ in range(4)]
    for aa, bb, cc, w in zip(a, b, c, parameter, strict=True):
        if family == "VVV":
            q = (aa + bb, aa + cc, bb + cc, aa + bb + cc)
            u = (aa + bb - cc - w, aa - bb + cc - w, -aa + bb + cc - w, 2 * w)
        else:
            q = (aa + bb - cc, aa - bb + cc, -aa + bb + cc, aa + bb + cc)
            u = (aa + bb - w, aa + cc - w, bb + cc - w, w)
        for term in range(4):
            queries[term].append(q[term])
            readers[term].append(u[term])
    return queries, readers, (a, b, c)


def raw_charges(case, labels, values, family):
    queries, readers, _ = factors(case, [*values, 0, 0], family)
    costs = []
    for query, reader in zip(queries, readers, strict=True):
        rows = [v for i, cell in enumerate(labels) if query[i] for v in cell]
        columns = [v for i, cell in enumerate(labels) if reader[i] for v in cell]
        matrix = [
            sum(((r & c).bit_count() % 2) << j for j, c in enumerate(columns))
            for r in rows
        ]
        costs.append(row_rank(matrix))
    return costs


def replay(case):
    labels = geometry(case)
    floor = sum(
        b["dimension"] * (1 if len(b["bases"]) == 1 else 3) for b in case["blocks"]
    )
    digest = hashlib.sha256()
    hist, mmm_hist = {}, {}
    hits, first = 0, None
    for values in itertools.product((0, 1, -1), repeat=len(labels)):
        costs = raw_charges(case, labels, values, "VVV")
        total = sum(costs)
        hit = total == floor
        require(total >= floor, "raw VVV floor")
        digest.update(bytes([*costs, int(hit)]))
        hist[str(total)] = hist.get(str(total), 0) + 1
        if hit:
            hits += 1
            if first is None:
                first = list(values)
    for values in itertools.product((0, 1), repeat=len(labels)):
        total = sum(raw_charges(case, labels, values, "MMM"))
        mmm_hist[str(total)] = mmm_hist.get(str(total), 0) + 1
    mmm_floor = sum(
        b["dimension"] * (2 if len(b["bases"]) == 1 else 3) for b in case["blocks"]
    )
    require(min(map(int, mmm_hist)) == mmm_floor, "raw MMM optimum")
    return {
        "name": case["name"],
        "floor": floor,
        "assignments": 3 ** len(labels),
        "stream_sha256": digest.hexdigest(),
        "histogram": hist,
        "attaining": hits,
        "first": first,
        "minimum": min(map(int, hist)),
        "mmm_floor": mmm_floor,
        "mmm_histogram": mmm_hist,
    }


def identities(case):
    size = len(case["cells"]) + 2
    entries = 0
    for family in ("VVV", "MMM"):
        parameter = [(j * 3 + 1) % 7 - 3 for j in range(size)]
        q, u, targets = factors(case, parameter, family)
        for modulus in (0, 3, 5, 7):
            gauges = [1] * 4 if modulus == 0 else [1, 2, modulus - 1, 1]
            for i in range(size):
                for j in range(size):
                    wanted = 2 * sum(t[i] * t[j] for t in targets)
                    if modulus:
                        actual = sum(
                            (u[k][i] * pow(gauges[k], -1, modulus))
                            * (q[k][j] * gauges[k])
                            for k in range(4)
                        )
                        require(
                            (actual - wanted) % modulus == 0, "finite-field identity"
                        )
                    else:
                        require(
                            sum(u[k][i] * q[k][j] for k in range(4)) == wanted,
                            "integer identity",
                        )
                    entries += 1
    return entries


def main():
    directory = Path(__file__).resolve().parent
    cases, expected = boundary(directory)
    actual = [replay(case) for case in cases]
    require(actual == expected["cases"], "raw result mismatch")
    entries = sum(identities(case) for case in cases)
    print(
        f"PASS_RAW_MIXED_BASIS cases={len(cases)} "
        f"assignments={sum(r['assignments'] for r in actual)} "
        f"operator_entries={entries}"
    )


if __name__ == "__main__":
    main()
