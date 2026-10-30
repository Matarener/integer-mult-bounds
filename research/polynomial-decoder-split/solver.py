"""Maximum disjoint binary minor packing with a matching rank-cut certificate.

The algorithm specializes classical unweighted matroid intersection twice.
The decoder extraction interface follows Charan/theon199 PR2330 and
DreamingOfClouds PR2162; new construction produced by Nick Petalas.
Apache-2.0.
"""

from collections import deque
from collections.abc import Callable, Sequence
from dataclasses import dataclass


Independent = Callable[[frozenset[int]], bool]
MAX_WIDTH = 32
MAX_COLORS = 8
MAX_COPIES = 96


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def rank(vectors: Sequence[int]) -> int:
    """Binary rank; input vectors have at most MAX_COPIES bits."""
    pivots = [0] * MAX_COPIES
    result = 0
    for vector in vectors:
        for _ in range(MAX_COPIES):
            if vector == 0:
                break
            bit = vector.bit_length() - 1
            if pivots[bit] == 0:
                pivots[bit] = vector
                result += 1
                break
            vector ^= pivots[bit]
    return result


def exchange_graph(n: int, chosen: frozenset[int], first: Independent,
                   second: Independent) -> tuple[list[list[int]], list[int], set[int]]:
    """Inside -> outside uses first; outside -> inside uses second."""
    graph: list[list[int]] = [[] for _ in range(n)]
    sources, sinks = [], set()
    for outside in range(n):
        if outside in chosen:
            continue
        added = chosen | {outside}
        if first(added):
            sources.append(outside)
        if second(added):
            sinks.add(outside)
        for inside in sorted(chosen):
            exchanged = added - {inside}
            if first(exchanged):
                graph[inside].append(outside)
            if second(exchanged):
                graph[outside].append(inside)
    return graph, sources, sinks


def shortest_path(graph: list[list[int]], sources: list[int],
                  sinks: set[int]) -> tuple[frozenset[int], frozenset[int]]:
    """Return a shortest augmenting path, or complete terminal reachability."""
    n = len(graph)
    parents = [-2] * n
    queue = deque(sources)
    for source in sources:
        parents[source] = -1
    for _ in range(n):
        if not queue:
            break
        current = queue.popleft()
        if current in sinks:
            path = set()
            for _ in range(n):
                path.add(current)
                current = parents[current]
                if current == -1:
                    return frozenset(path), frozenset()
            raise RuntimeError("cyclic predecessor chain")
        for neighbor in graph[current]:
            if parents[neighbor] == -2:
                parents[neighbor] = current
                queue.append(neighbor)
    require(not queue, "BFS exceeded its vertex bound")
    return frozenset(), frozenset(i for i in range(n) if parents[i] != -2)


def intersect(n: int, capacity: int, first: Independent,
              second: Independent) -> tuple[frozenset[int], frozenset[int]]:
    chosen: frozenset[int] = frozenset()
    for _ in range(capacity + 1):
        graph, sources, sinks = exchange_graph(n, chosen, first, second)
        path, reachable = shortest_path(graph, sources, sinks)
        if not path:
            return chosen, reachable
        new = chosen ^ path
        require(len(new) == len(chosen) + 1, "augmentation size")
        require(first(new) and second(new), "augmentation independence")
        chosen = new
    raise RuntimeError("matroid intersection exceeded its rank bound")


def outer_intersection(n: int, capacity: int, first: Independent,
                       second: Independent) -> tuple[frozenset[int], frozenset[int]]:
    """Finish inner oracle calls before building each outer exchange graph."""
    chosen: frozenset[int] = frozenset()
    for _ in range(capacity + 1):
        answers = {}
        for outside in range(n):
            if outside in chosen:
                continue
            added = chosen | {outside}
            answers[added] = second(added)
            for inside in sorted(chosen):
                exchanged = added - {inside}
                answers[exchanged] = second(exchanged)

        def lookup(elements: frozenset[int]) -> bool:
            return answers[elements]

        graph, sources, sinks = exchange_graph(n, chosen, first, lookup)
        path, reachable = shortest_path(graph, sources, sinks)
        if not path:
            return chosen, reachable
        new = chosen ^ path
        require(len(new) == len(chosen) + 1, "outer augmentation size")
        require(first(new) and second(new), "outer augmentation independence")
        chosen = new
    raise RuntimeError("outer intersection exceeded its rank bound")


def partition_independent(elements: frozenset[int], width: int) -> bool:
    return len({element % width for element in elements}) == len(elements)


def inner(blocks: tuple[tuple[int, ...], ...], width: int,
          rows: frozenset[int]) -> tuple[frozenset[int], frozenset[int]]:
    """A column partition matroid intersected with restricted column rank."""
    n = width * len(blocks)
    vectors = [0] * n
    for position, row in enumerate(sorted(rows)):
        color, original = divmod(row, width)
        for column in range(width):
            vectors[color * width + column] |= (
                ((blocks[color][original] >> column) & 1) << position)

    def linear(elements: frozenset[int]) -> bool:
        return rank([vectors[element] for element in sorted(elements)]) == len(elements)

    def partition(elements: frozenset[int]) -> bool:
        return partition_independent(elements, width)

    return intersect(n, width, linear, partition)


@dataclass(frozen=True)
class Certificate:
    rows: tuple[tuple[int, ...], ...]
    columns: tuple[tuple[int, ...], ...]
    cut_rows: tuple[int, ...]
    cut_columns: tuple[int, ...]


def validate(blocks: tuple[tuple[int, ...], ...]) -> int:
    require(type(blocks) is tuple and 1 <= len(blocks) <= MAX_COLORS,
            "expected one to eight tuple blocks")
    require(type(blocks[0]) is tuple, "expected tuple rows")
    width = len(blocks[0])
    require(1 <= width <= MAX_WIDTH and width * len(blocks) <= MAX_COPIES,
            "width or total-copy capacity exceeded")
    for block in blocks:
        require(type(block) is tuple and len(block) == width, "nonsquare block")
        require(all(type(row) is int and 0 <= row < (1 << width) for row in block),
                "row is not a binary bitmask of the declared width")
    return width


def solve(blocks: tuple[tuple[int, ...], ...]) -> Certificate:
    width = validate(blocks)
    n = width * len(blocks)

    def row_partition(elements: frozenset[int]) -> bool:
        return partition_independent(elements, width)

    def induced(elements: frozenset[int]) -> bool:
        if len(elements) > width:
            return False
        active_colors = 0
        for color, block in enumerate(blocks):
            vectors = [block[element % width] for element in elements
                       if element // width == color]
            if rank(vectors) != len(vectors):
                return False
            active_colors += bool(vectors)
        if active_colors <= 1:
            return True
        columns, _ = inner(blocks, width, elements)
        return len(columns) == len(elements)

    rows, reachable = outer_intersection(n, width, row_partition, induced)
    columns, _ = inner(blocks, width, rows)
    deleted_originals = {row % width for row in range(n) if row not in reachable}
    cut_rows = tuple(i for i in range(width) if i not in deleted_originals)
    saturated_rows = frozenset(c * width + i for c in range(len(blocks)) for i in cut_rows)
    _, inner_reachable = inner(blocks, width, saturated_rows)
    deleted_columns = {column % width for column in inner_reachable}
    cut_columns = tuple(i for i in range(width) if i not in deleted_columns)
    certificate = Certificate(
        tuple(tuple(i for i in range(width) if c * width + i in rows)
              for c in range(len(blocks))),
        tuple(tuple(i for i in range(width) if c * width + i in columns)
              for c in range(len(blocks))), cut_rows, cut_columns)
    certify(blocks, certificate)
    return certificate


def certify(blocks: tuple[tuple[int, ...], ...], certificate: Certificate) -> int:
    """Check primal feasibility and equality to an elementary cut upper bound."""
    width = validate(blocks)
    require(type(certificate) is Certificate, "expected Certificate")
    require(type(certificate.rows) is tuple and type(certificate.columns) is tuple
            and len(certificate.rows) == len(blocks) == len(certificate.columns),
            "wrong color count")
    used_rows, used_columns = set(), set()
    for color, block in enumerate(blocks):
        rows, columns = certificate.rows[color], certificate.columns[color]
        require(type(rows) is tuple and type(columns) is tuple
                and len(rows) <= width and len(columns) <= width,
                "invalid minor dimensions")
        require(len(rows) == len(columns), "nonsquare selected minor")
        for subset in (rows, columns):
            require(type(subset) is tuple and all(type(i) is int and 0 <= i < width for i in subset)
                    and len(set(subset)) == len(subset), "invalid selected indices")
        require(not used_rows.intersection(rows) and not used_columns.intersection(columns),
                "reused original row or column")
        used_rows.update(rows)
        used_columns.update(columns)
        mask = sum(1 << i for i in columns)
        require(rank([block[i] & mask for i in rows]) == len(rows), "singular selected minor")
    for subset in (certificate.cut_rows, certificate.cut_columns):
        require(type(subset) is tuple and len(subset) <= width
                and all(type(i) is int and 0 <= i < width for i in subset)
                and len(set(subset)) == len(subset), "invalid cut")
    mask = sum(1 << i for i in certificate.cut_columns)
    cut = 2 * width - len(certificate.cut_rows) - len(certificate.cut_columns)
    cut += sum(rank([block[i] & mask for i in certificate.cut_rows]) for block in blocks)
    require(len(used_rows) == cut, "primal/cut gap")
    return cut
