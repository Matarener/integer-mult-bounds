"""Minimum-support gathers for indistinguishable aligned neighborhoods.

Produced by Nick Petalas. Apache-2.0.
The spectator wrapper and support-router contracts retain their source credit.
"""
from dataclasses import dataclass
from typing import Sequence

MAX_BLOCKS = (1 << 31) - 1
MAX_SELECTED = 256
MAX_SELECTED_BITS = 65536
MAX_EXECUTED_BITS = 16


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def integer(value: int, lower: int, upper: int, name: str) -> None:
    require(type(value) is int and lower <= value <= upper, name)


@dataclass(frozen=True)
class Gather:
    blocks: int
    width: int
    sources: tuple[int, ...]
    targets: tuple[int, ...]
    exchanges: tuple[tuple[int, int], ...]

    def bit_swaps(self) -> tuple[tuple[int, int], ...]:
        return tuple((a*self.width+j, b*self.width+j)
                     for a, b in self.exchanges for j in range(self.width))

    def mapping(self) -> dict[int, int]:
        swaps = self.bit_swaps()
        return dict(tuple(swaps) + tuple((b, a) for a, b in swaps))


def compile_gather(blocks: int, width: int, sources: Sequence[int],
                   targets: Sequence[int]) -> Gather:
    """Offsets are preserved; the assignment of identical kernels is free."""
    integer(blocks, 1, MAX_BLOCKS, 'Invalid block count')
    integer(width, 1, MAX_SELECTED_BITS, 'Invalid neighborhood width')
    require(type(sources) in (tuple, list) and type(targets) in (tuple, list),
            'Neighborhoods must be finite lists or tuples')
    require(1 <= len(sources) == len(targets) <= MAX_SELECTED,
            'Equal nonempty bounded neighborhood counts required')
    require(len(sources)*width <= MAX_SELECTED_BITS, 'Selected-bit capacity')
    for block in tuple(sources) + tuple(targets):
        integer(block, 0, blocks-1, 'Invalid neighborhood index')
    source, target = frozenset(sources), frozenset(targets)
    require(len(source) == len(sources) and len(target) == len(targets),
            'Repeated neighborhoods')
    leaving, entering = sorted(source-target), sorted(target-source)
    require(len(leaving) == len(entering), 'Unbalanced symmetric difference')
    exchanges = tuple(zip(leaving, entering))
    return Gather(blocks, width, tuple(sorted(source)), tuple(sorted(target)),
                  exchanges)


def address(value: int, plan: Gather) -> int:
    """Literal address oracle; symbolic plans can be much larger."""
    bits = plan.blocks*plan.width
    integer(bits, 1, MAX_EXECUTED_BITS, 'Literal-address capacity')
    integer(value, 0, (1 << bits)-1, 'Invalid address')
    result = value
    for a, b in plan.bit_swaps():
        i, j = bits-1-a, bits-1-b
        different = ((result >> i) ^ (result >> j)) & 1
        result ^= different*((1 << i) | (1 << j))
    return result


def permute(values: list, plan: Gather) -> list:
    bits = plan.blocks*plan.width
    integer(bits, 1, MAX_EXECUTED_BITS, 'Literal-vector capacity')
    require(type(values) is list and len(values) == 1 << bits,
            'Complete binary rectangle required')
    out = [None]*len(values)
    for index, value in enumerate(values):
        out[address(index, plan)] = value
    return out
