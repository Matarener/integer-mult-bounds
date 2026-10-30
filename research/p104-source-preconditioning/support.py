# SPDX-License-Identifier: Apache-2.0
"""Pooled path compression and a separately replayed full-memory certificate."""
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bindings import authenticate, canonical, module, need
from boundary import correction

SOURCES = (0, 1, 2, 3)
ROWS = (4, 6, 8, 39)
EXPECTED = ("0x15088a1021120142242d061684", "0x1504102110011204022d109084",
            "0x1b0000480c4084800021001083", "0x2a889524212d01425a52a06020")


def dimension(space):
    size = len(space)
    need(size > 0 and not size & (size - 1), "binary subspace cardinality")
    return size.bit_length() - 1


@dataclass(frozen=True)
class PooledModel:
    """Explicit bounded extension to2309 helpers; predecessor Model is unchanged."""
    bounds: tuple
    sources: tuple
    targets: tuple

    def __post_init__(self):
        need(len(self.bounds) == 8 and len(self.sources) == 4 and len(self.targets) == 104,
             "four-source pooled model dimensions")
        for d, layer in enumerate(self.bounds, 1):
            need(len(layer) == 2309, "complete pooled helper inventory")
            for low, high in layer:
                need(low <= high and dimension(low) <= d <= dimension(high), "nonempty helper interval")
        for chain in self.sources + self.targets:
            need(1 <= len(chain) <= 10 and all(a < b for a, b in zip(chain, chain[1:])), "nested snapshot path")
        need(all(dimension(chain[0]) >= 1 for chain in self.sources) and
             all(dimension(chain[-1]) <= 8 for chain in self.targets), "source/target layer boundary")


def virtual_helpers(model):
    """One recombined endpoint pair admitting nested read/write snapshots.

    The written pooled path-compression lemma makes this a necessary test.
    This routine imports no memory acquisition, relay or pruning operation.
    """
    @lru_cache(maxsize=1080)
    def hosts(space):
        d = dimension(space)
        if not 1 <= d <= 8:
            return 0
        return sum(1 << h for h, (low, high) in enumerate(model.bounds[d - 1]) if low <= space <= high)

    outputs = []
    for target in model.targets:
        mask = 0
        for s, source in enumerate(model.sources):
            for read in source:
                for write in target:
                    if read == write or (read <= write and hosts(read) & hosts(write)):
                        mask |= 1 << s
                        break
                if mask >> s & 1:
                    break
        outputs.append(mask)
    # Both snapshots can fit the same interval without belonging to one flag.
    low, high = model.bounds[2][0]
    first = min(high - low)
    read = frozenset(low | {point ^ first for point in low})
    second = min(high - read)
    write = frozenset(low | {point ^ second for point in low})
    need(hosts(read) & hosts(write) and not read <= write and not write <= read,
         "nonnested same-dimension control")
    return outputs


def memory_replay(model, pooled, memory, paths):
    """Use PR3252's unchanged transfer bodies under the explicit larger model."""
    need(memory.MAX_MEMORIES == 16, "unchanged fail-closed memory capacity")
    state = [{} for _ in range(2309)]
    outputs = [sum(1 << s for s, chain in enumerate(model.sources) if set(chain) & set(target))
               for target in model.targets]
    peak, layers = 0, []
    for d, bounds in enumerate(model.bounds, 1):
        masks = pooled.interval_relation(bounds, d)
        adjacency = [[j for j in range(2309) if mask >> j & 1] for mask in masks]
        reads = [[s for s, chain in enumerate(model.sources) if any(memory.fits(bound, d, frame) for frame in chain)]
                 for bound in bounds]
        writes = [[t for t in range(104) if mask >> t & 1]
                  for mask in pooled.contacts(bounds, d, paths, "Y")]
        following = [{s: list(memories) for s, memories in row.items()} for row in state]
        memory.acquire(following, model, bounds, reads, d, True)
        # Old state only. Complete untimed reads cover fresh same-frame starts.
        memory.relay(state, following, bounds, adjacency, d, True)
        state = following
        memory.deliver(outputs, state, model, bounds, writes, d)
        peak = max(peak, max((len(values) for row in state for values in row.values()), default=0))
        layers.append([sum(s in row for row in state) for s in range(4)])
    return outputs, peak, layers


def determinant(matrix):
    rows = [list(map(Q, row)) for row in matrix]
    value = Q(1)
    for column in range(len(rows)):
        pivot = next((i for i in range(column, len(rows)) if rows[i][column]), None)
        if pivot is None:
            return Q(0)
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            value = -value
        scale = rows[column][column]
        value *= scale
        rows[column] = [x / scale for x in rows[column]]
        for i in range(column + 1, len(rows)):
            scale = rows[i][column]
            rows[i] = [x - scale * y for x, y in zip(rows[i], rows[column])]
    return value


def run():
    raw = authenticate()
    pooled = module(raw, "rank_four_pooled_source", "research/p104-pooled-cut-independent/verify.py")
    memory = module(raw, "rank_four_memory_source", "research/p104-memory-relaxation-soundness/memory.py")
    cert, word, fixture = pooled.load_inputs()
    paths = pooled.data_paths(word)
    frames = pooled.endpoints(cert, paths)
    model = PooledModel(tuple(tuple(pooled.bounds_at(frames, d)) for d in range(1, 9)),
                        tuple(tuple(paths["X" + str(s)]) for s in SOURCES),
                        tuple(tuple(paths["Y" + str(t)]) for t in range(104)))
    direct = virtual_helpers(model)
    replay, peak, layers = memory_replay(model, pooled, memory, paths)
    need(direct == replay, "all416 support entries agree across the two methods")
    columns = tuple(hex(sum(1 << t for t, mask in enumerate(direct) if mask >> s & 1)) for s in range(4))
    need(columns == EXPECTED, "complete four-column support receipt")
    need(not set(ROWS) & set(SOURCES) and all(direct[t] == 0 for t in ROWS), "disjoint forbidden minor")
    ports, gram_half, _ = correction(fixture)
    minor = tuple(tuple(gram_half[t][s] for s in SOURCES) for t in ROWS)
    want = ((Q(1,2),Q(-1,2),0,Q(1,2)), (0,0,Q(1,2),0),
            (0,0,Q(-1,2),Q(1,2)), (Q(1,2),0,Q(1,2),0))
    need(minor == want and determinant(minor) == Q(1,16), "exact rank-four minor")
    doubled = tuple(tuple(int(2 * value) for value in row) for row in minor)
    leibniz = 0
    for perm in permutations(range(4)):
        term = (-1) ** sum(perm[i] > perm[j] for i in range(4) for j in range(i+1,4))
        for i, j in enumerate(perm):
            term *= doubled[i][j]
        leibniz += term
    need(leibniz == 1, "independent24-term integral determinant")
    result = dict(status="PASS_P104_PRECONDITIONER_RANK_FOUR_OBSTRUCTION", sources=SOURCES, rows=ROWS,
                  support_columns=columns, all_zero_rows=[t for t, mask in enumerate(direct) if not mask and t not in SOURCES],
                  twice_minor=doubled, determinant="1/16", memory_peak=peak, memory_cap=16,
                  reached_helpers_by_layer=layers, source_roots=[ports[s] for s in SOURCES],
                  target_roots=[ports[t] for t in ROWS], preconditioner_rank_lower_bound=4,
                  scope="Scalar invertible source preconditioners under the fixed pooled monotone correction contract; no general native tariff or unrestricted P104 barrier.")
    result["sha256"] = sha256(canonical(result)).hexdigest()
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
