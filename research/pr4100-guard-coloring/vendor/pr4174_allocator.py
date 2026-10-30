"""Construct the bit-field placements specified by PR4100 CRT.md, section 3.

Positions increase from the front (most significant end) of the complete
address. Logical axes appear physically in order d-1, ..., 0. Every interval
is half-open. This module manipulates address descriptors, not payload tapes;
it makes no machine-cost claim and performs no I/O.

API:
    layout = Layout(p, ell, widths)  # widths indexed by logical axis
    for plan in iter_plans(layout, level=None):
        plan.active_axes                 # at most layout.r_max logical axes
        plan.dependencies                # original own/left-child intervals
        plan.source_blocks               # three original reservoir intervals
        plan.destination_blocks          # front u, front t, back b intervals
        plan.map_position(position)      # involution, also the inverse map
        plan.map_interval(lo, hi)        # translation fragments, original order
        plan.descriptor_fragment_count   # all d axes, without enumerating them

The generator holds only one batch at a time. Layout's prefix index is built
once in O(d) space; no plan allocates the descriptors for all d axes.

Cinna Davis supplies the audited CRT construction. This constructive
descriptor implementation is by Hiroki KUMAZAKI (@kumagi), with substantial
OpenAI Codex assistance. Apache-2.0.
"""
from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass, field
from itertools import islice
from typing import Iterable, Iterator


Interval = tuple[int, int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def ceil_log2(value: int) -> int:
    """Return ceil(log2(value)) exactly for a positive integer."""
    require(type(value) is int and value >= 1, "positive integer logarithm input")
    return (value - 1).bit_length()


def intersects(first: Interval, second: Interval) -> bool:
    """Whether two half-open intervals have positive-length intersection."""
    return max(first[0], second[0]) < min(first[1], second[1])


@dataclass(frozen=True, init=False)
class Layout:
    """One validated actual-family layout, with widths in logical-axis order."""

    p: int
    ell: int
    widths: tuple[int, ...]
    prefix: tuple[int, ...]
    d: int
    L: int
    G: int
    K: int
    r_max: int
    H: int

    def __init__(self, p: int, ell: int, widths: Iterable[int]) -> None:
        require(type(p) is int and p >= 1, "p must be a positive integer")
        require(type(ell) is int and ell >= 2, "ell must be an integer at least 2")
        logarithm = ceil_log2(p + 2)
        require(ell >= logarithm, "ell must be at least ceil(log2(p+2))")
        widths = tuple(widths)
        d = len(widths)
        require(d >= 51200 and d & (d - 1) == 0,
                "d must be a power of two at least 51200")
        require(all(type(width) is int and width in (ell - 1, ell) for width in widths),
                "every axis width must be ell-1 or ell")
        prefix = [0]
        for width in widths:
            prefix.append(prefix[-1] + width)
        length = prefix[-1]
        guard_digit_bits = 64 * (ell + logarithm)
        maximum_batch = length // (100 * guard_digit_bits)
        field_bits = maximum_batch * guard_digit_bits
        require(maximum_batch >= 1, "the compact reservoir must have an active digit")
        require(100 * field_bits <= length, "compact fields exceed their volume bound")
        for name, value in (
            ("p", p), ("ell", ell), ("widths", widths), ("prefix", tuple(prefix)),
            ("d", d), ("L", length), ("G", guard_digit_bits),
            ("K", 64 * guard_digit_bits), ("r_max", maximum_batch), ("H", field_bits),
        ):
            object.__setattr__(self, name, value)

    @property
    def levels(self) -> int:
        return self.d.bit_length() - 1

    def axes_interval(self, lo: int, hi: int) -> Interval:
        """Physical span of consecutive logical axes [lo, hi)."""
        require(type(lo) is int and type(hi) is int and 0 <= lo <= hi <= self.d,
                "logical axis interval out of range")
        return self.L - self.prefix[hi], self.L - self.prefix[lo]

    def axis_interval(self, axis: int) -> Interval:
        """Original physical interval occupied by one complete logical axis."""
        require(type(axis) is int and 0 <= axis < self.d, "logical axis out of range")
        return self.axes_interval(axis, axis + 1)

    def is_axis_boundary(self, position: int) -> bool:
        """Test a physical boundary in O(log d), without building all intervals."""
        require(type(position) is int and 0 <= position <= self.L,
                "physical boundary out of range")
        value = self.L - position
        index = bisect_left(self.prefix, value)
        return index < len(self.prefix) and self.prefix[index] == value


@dataclass(frozen=True)
class Dependency:
    """Conservative original support of one axis's Beneš switch function.

    own_interval contains the entire active axis, including its target bit.
    The actual function omits that one target; retaining it here gives a
    stronger reservoir-disjointness check. left_axes and left_interval are
    the complete logical and physical left child of the current tree node.
    """

    axis: int
    own_interval: Interval
    left_axes: Interval
    left_interval: Interval


@dataclass(frozen=True)
class Fragment:
    """A piece translated without reversal from original to image interval."""

    original_interval: Interval
    image_interval: Interval

    @property
    def delta(self) -> int:
        return self.image_interval[0] - self.original_interval[0]


@dataclass(frozen=True)
class Placement:
    """Strict exchange geometry, independently of the large-family cutoff.

    This also permits small exhaustive geometry fixtures without weakening
    Layout's parameter checks. The three destinations are always [0,H),
    [H,2H), and [length-H,length). Each supplied source has exactly H bits.
    """

    length: int
    H: int
    source_blocks: tuple[Interval, Interval, Interval]
    destination_blocks: tuple[Interval, Interval, Interval] = field(init=False)

    def __post_init__(self) -> None:
        require(type(self.length) is int and self.length > 0, "positive address length")
        require(type(self.H) is int and self.H > 0, "positive field width")
        sources = tuple(tuple(block) for block in self.source_blocks)
        require(len(sources) == 3, "exactly three source fields are required")
        require(all(len(block) == 2 and all(type(point) is int for point in block)
                    and 0 <= block[0] < block[1] <= self.length
                    and block[1] - block[0] == self.H for block in sources),
                "each source must be an in-range interval of width H")
        destinations = ((0, self.H), (self.H, 2 * self.H),
                        (self.length - self.H, self.length))
        require(3 * self.H <= self.length, "destination fields do not fit")
        all_blocks = sources + destinations
        require(all(not intersects(first, second) for i, first in enumerate(all_blocks)
                    for second in all_blocks[i + 1:]),
                "source and destination fields must be pairwise disjoint")
        object.__setattr__(self, "source_blocks", sources)
        object.__setattr__(self, "destination_blocks", destinations)

    @property
    def swaps(self) -> tuple[tuple[Interval, Interval], ...]:
        """Three endpoint pairs; all six intervals are mutually disjoint."""
        return tuple(zip(self.source_blocks, self.destination_blocks))

    @property
    def cuts(self) -> tuple[int, ...]:
        """At most twelve distinct endpoints of the six exchange intervals."""
        return tuple(sorted({point for block in self.source_blocks + self.destination_blocks
                             for point in block}))

    def map_position(self, position: int) -> int:
        """Map an original bit to its current position; also the inverse map."""
        require(type(position) is int and 0 <= position < self.length,
                "bit position out of range")
        for source, destination in self.swaps:
            if source[0] <= position < source[1]:
                return position + destination[0] - source[0]
            if destination[0] <= position < destination[1]:
                return position + source[0] - destination[0]
        return position

    def map_interval(self, lo: int, hi: int) -> tuple[Fragment, ...]:
        """Split an original interval only at exchange cuts and translate it.

        Fragments are ordered by original position, so concatenating their
        current bit slices reconstructs the original field. Their image
        intervals need not occur in physical order. An empty input returns ().
        """
        require(type(lo) is int and type(hi) is int and 0 <= lo <= hi <= self.length,
                "physical interval out of range")
        if lo == hi:
            return ()
        boundaries = [lo] + [cut for cut in self.cuts if lo < cut < hi] + [hi]
        fragments = []
        for start, stop in zip(boundaries, boundaries[1:]):
            image_start = self.map_position(start)
            fragments.append(Fragment((start, stop), (image_start, image_start + stop - start)))
        return tuple(fragments)


@dataclass(frozen=True)
class Plan:
    """A batch plus three disjoint source/destination field exchanges.

    partition is 0 or 1: a global half at non-root levels, and a quarter of
    the logical right child at the root. batch_index starts at zero within
    each partition. Every support interval is expressed before placement.
    The Plan retains its shared Layout reference, not a copy of that index.
    """

    layout: Layout
    level: int
    partition: int
    batch_index: int
    active_axes: tuple[int, ...]
    reservoir_axes: Interval
    reservoir_interval: Interval
    placement: Placement
    dependencies: tuple[Dependency, ...]

    @property
    def source_blocks(self) -> tuple[Interval, Interval, Interval]:
        return self.placement.source_blocks

    @property
    def destination_blocks(self) -> tuple[Interval, Interval, Interval]:
        return self.placement.destination_blocks

    @property
    def swaps(self) -> tuple[tuple[Interval, Interval], ...]:
        return self.placement.swaps

    @property
    def cuts(self) -> tuple[int, ...]:
        return self.placement.cuts

    def map_position(self, position: int) -> int:
        return self.placement.map_position(position)

    def map_interval(self, lo: int, hi: int) -> tuple[Fragment, ...]:
        return self.placement.map_interval(lo, hi)

    @property
    def descriptor_fragment_count(self) -> int:
        """Exact number from splitting all d axes at the exchange endpoints.

        Every non-axis-boundary cut splits precisely one original axis.
        This uses at most twelve binary searches and creates no d-axis list.
        """
        return self.layout.d + sum(not self.layout.is_axis_boundary(cut) for cut in self.cuts)


def _active_in_region(lo: int, hi: int, width: int) -> Iterator[int]:
    """Enumerate logical right-child axes of all nodes wholly in the region."""
    for start in range(lo, hi, width):
        yield from range(start + width // 2, start + width)


def _regions(layout: Layout, level: int) -> Iterator[tuple[int, Iterator[int], Interval]]:
    """Return partition, lazy active-axis stream, and unused logical interval."""
    half = layout.d // 2
    if level == layout.levels:
        middle = half + layout.d // 4
        yield 0, iter(range(half, middle)), (middle, layout.d)
        yield 1, iter(range(middle, layout.d)), (half, middle)
    else:
        width = 1 << level
        yield 0, _active_in_region(0, half, width), (half, layout.d)
        yield 1, _active_in_region(half, layout.d, width), (0, half)


def _make_plan(layout: Layout, level: int, partition: int, batch_index: int,
               active_axes: tuple[int, ...], reservoir_axes: Interval) -> Plan:
    reservoir = layout.axes_interval(*reservoir_axes)
    require(8 * (reservoir[1] - reservoir[0]) >= layout.L,
            "chosen reservoir is shorter than L/8")
    field_bits = layout.H
    free_lo = max(reservoir[0], 2 * field_bits)
    free_hi = min(reservoir[1], layout.L - field_bits)
    first = ((free_lo + field_bits - 1) // field_bits) * field_bits
    require(first + 3 * field_bits <= free_hi,
            "three aligned source fields do not fit after excluding destinations")
    source_blocks = tuple((first + i * field_bits, first + (i + 1) * field_bits)
                          for i in range(3))
    placement = Placement(layout.L, field_bits, source_blocks)
    width = 1 << level
    dependencies = []
    for axis in active_axes:
        node_start = axis // width * width
        left_axes = (node_start, node_start + width // 2)
        require(left_axes[1] <= axis < node_start + width,
                "active axis is not in the node's right child")
        own = layout.axis_interval(axis)
        left = layout.axes_interval(*left_axes)
        require(not intersects(reservoir, own) and not intersects(reservoir, left),
                "reservoir intersects an active switch's original support")
        dependencies.append(Dependency(axis, own, left_axes, left))
    return Plan(layout, level, partition, batch_index, active_axes, reservoir_axes,
                reservoir, placement, tuple(dependencies))


def iter_plans(layout: Layout, level: int | None = None) -> Iterator[Plan]:
    """Yield the construction lazily, in increasing level/partition/batch order.

    level=None covers levels 1 through log2(d), each containing exactly d/2
    active axes. A supplied level selects only that level. Each partition's
    right-child stream is cut into consecutive groups of at most r_max axes.
    A group may cross a node boundary; its dependencies retain each node's
    own left child. No list of all plans is constructed.
    """
    require(isinstance(layout, Layout), "a validated Layout is required")
    if level is None:
        levels = range(1, layout.levels + 1)
    else:
        require(type(level) is int and 1 <= level <= layout.levels,
                "tree level out of range")
        levels = (level,)
    for current_level in levels:
        for partition, axes, reservoir_axes in _regions(layout, current_level):
            batch_index = 0
            while True:
                active = tuple(islice(axes, layout.r_max))
                if not active:
                    break
                yield _make_plan(layout, current_level, partition, batch_index,
                                 active, reservoir_axes)
                batch_index += 1
