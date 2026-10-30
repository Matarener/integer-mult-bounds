"""Reject malformed supports, unsafe lifetimes and lost composition operations."""

from unittest.mock import patch
from composed_sources import require


def rejects(function, label, fragment=None):
    try:
        function()
    except ValueError as error:
        require(fragment is None or fragment in str(error), "specific rejection: " + label)
        return label
    raise ValueError("missing rejection: " + label)


def descriptor_rejection(n, selected, kind):
    from cardinal_counts import Count
    from check_composed import selected_tape
    from composed_plan import Positions
    from words import BLANK
    tape = selected_tape(n, selected)
    width_value = max(1, (n-1).bit_length()) + (1 if kind == "noncanonical width" else 0)
    count, width, dimension = (Count.literal(v) for v in (len(selected), width_value, n))
    try:
        if kind == "short descriptor":
            tape.clear()
        if kind == "trailing descriptor":
            while tape.read() != BLANK:
                tape.step(1)
            tape.append(0)
            tape.rewind()
        Positions(tape, count, width).validate(dimension)
    finally:
        tape.clear()
        for value in (count, width, dimension):
            value.close()


def run():
    from check_composed import run_packet
    from check_composed_metadata import plan_case
    from composed_engine import ComposedRoot
    from composed_plan import ExposurePlan
    from router_metadata import indices, owned
    from cardinal_counts import Count
    from encoded import subtract
    from session import erase_marker
    rejected = []
    for n, positions, label in (
        (4, (1, 1), "duplicate selected position"),
        (4, (2, 1), "unsorted selected positions"),
        (3, (0, 3), "coordinate outside rectangle"),
        (4, (0, 1), "short descriptor"),
        (4, (0, 1), "trailing descriptor"),
        (4, (0, 1), "noncanonical width"),
    ):
        rejected.append(rejects(lambda: descriptor_rejection(n, positions, label), label))
    rejected.append(rejects(lambda: plan_case(3, 2, (0, 1)), "root width cap", "root domain"))

    import composed_plan
    original_sort, sorts = composed_plan.stable_radix, [0]

    def omit_inverse_sort(source, *arguments):
        sorts[0] += 1
        return source if sorts[0] == 2 else original_sort(source, *arguments)

    with patch.object(composed_plan, "stable_radix", omit_inverse_sort):
        rejected.append(rejects(lambda: plan_case(5, 5, (0, 4), "fixture-ell1"),
                                "omitted inverse descriptor sort", "sorted unique support"))

    owner, _ = run_packet(2, 2, (), consume=False)
    rejected.append(rejects(lambda: run_packet(2, 2, (), owner=owner),
                            "protected composed output", "consume prior composed output"))
    owner[0].output.clear()
    erase_marker(owner[0].output)
    run_packet(2, 2, (), owner=owner)

    from records import Tape as PhysicalTape

    def allocate(*_args):
        PhysicalTape()

    with patch.object(ExposurePlan, "compile", allocate):
        rejected.append(rejects(lambda: run_packet(2, 2, ()), "physical allocation inside composition",
                                "physical Tape allocation"))

    def truncate_each(self, plan, selected, coefficients, C, _gaussians, _h):
        with owned(Count.literal(1)) as (one,):
            with owned(subtract(plan.n, one)) as (last,):
                for index in indices(plan.g):
                    with selected.at(index) as right, owned(subtract(last, right)) as (left,):
                        self.transform(plan.p, one, left, right, coefficients, C)

    with patch.object(ComposedRoot, "literal", truncate_each):
        rejected.append(rejects(
            lambda: run_packet(2, 3, (0, 1), values=[(-3, 0), (-2, 0), (-3, 0), (0, 0)]),
            "premature physical truncation", "complete composed endpoint"))
    return dict(status="PASS_COMPOSED_REJECTIONS", rejected=rejected)
