"""Select and consume one exact strict-volume plan without numerical decoding."""

from contextlib import ExitStack

import outer
import plan_geometry as geometry
import strict_outer
import strict_selector
from cardinal_counts import positive


def run(
    source, original, q, prefixes, spectators, suffix, factory, profile, compatibility=1
):
    """factory(geometry) is a context manager yielding completed rowwise F.

    Input payload and Counts are borrowed. Return a distinct owned payload.
    On no-fit, use the complete ordinary swap and never enter the callee.
    """
    for extent in (original, prefixes, spectators, suffix):
        positive(extent)
    plan = strict_selector.select(original, q, profile, compatibility)
    try:
        if not plan["fits"]:
            with ExitStack() as work:
                modulus = geometry.power(original, q, work)
                ring = geometry.ring(modulus, work)
                return outer.swap_chunks(source, ring, q, prefixes, spectators, suffix)
        with geometry.fitted(plan, q, spectators, suffix) as shape:
            with factory(shape) as callee:
                return strict_outer.interchange(
                    source,
                    shape.atoms,
                    shape.ring,
                    shape.high,
                    q,
                    prefixes,
                    spectators,
                    suffix,
                    plan["stock"],
                    callee,
                    shape.remainder,
                )
    finally:
        strict_selector.close_plan(plan)
