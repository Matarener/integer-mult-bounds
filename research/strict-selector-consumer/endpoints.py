"""Independent full-origin endpoints for the actual selected-plan caller."""

from contextlib import contextmanager

import cardinality
import checks
import strict_call
import strict_selector
from binding_source import require
from cardinal_counts import Count
from count_ownership import audited_counts
from fixtures import Fixture, Parameters


@contextmanager
def synthetic(fixture, shape):
    """Observe each completed callee using the predecessor's independent oracle."""
    spec = fixture.spec

    def call(source, rows):
        return checks.model_callee(
            source,
            rows,
            n=spec.n,
            m=spec.q**spec.w,
            p=spec.p,
            gap=spec.q**spec.ell * spec.z * spec.q**spec.k,
            suffix=spec.q**spec.ell * spec.t,
            ring=shape.ring,
            q=spec.q,
        )

    old = fixture.factory
    fixture.factory = call
    try:
        yield fixture.callee
    finally:
        fixture.factory = old


def one(*, e=5, profile=None, factory=None, fail_at=None, **parameters):
    if profile is None:
        profile = strict_selector.Profile(0, 1, 2, 1, 1)
    fixture = Fixture(
        Parameters(q=2, n=3, k=2, stock_value=6, **parameters), None, fail_at
    )
    original = Count.literal(e)
    before = bytes(original.tape.cells)

    @contextmanager
    def build(shape):
        manager = (
            synthetic(fixture, shape) if factory is None else factory(fixture, shape)
        )
        with manager as callee:
            yield callee

    try:
        with fixture.chronology(), checks.observed(fixture.tracker, fixture.meter):
            with audited_counts(cardinality.Tape) as observation:
                fixture.count_observation = observation
                try:
                    fixture.result = strict_call.run(
                        fixture.source,
                        original,
                        2,
                        *fixture.counts[:3],
                        build,
                        profile,
                    )
                except ValueError as error:
                    require(
                        fail_at is not None,
                        "unexpected caller rejection: " + str(error),
                    )
                    require(
                        str(error) == "injected completed-callee failure",
                        "expected callee failure",
                    )
                    require(len(fixture.calls) == fail_at, "failure at requested call")
                require(
                    original.tape.head == 1 and bytes(original.tape.cells) == before,
                    "original restored",
                )
        if fail_at is None:
            return fixture.check_result()
        require(
            fixture.tracker.live == {fixture.source},
            "failure releases all owned payload",
        )
        require(
            bytes(fixture.source.cells) == fixture.saved,
            "failed caller source preserved",
        )
        return dict(failed_at=fail_at, calls=fixture.calls, count_ownership=observation)
    finally:
        original.close()
        fixture.close()


def full_cases():
    """The same least e=5 plan under every binary spectator combination."""
    return [one(p=p, z=z, t=t) for p in (1, 2) for z in (1, 2) for t in (1, 2)]
