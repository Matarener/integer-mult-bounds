"""Full Boolean-column endpoint checks, separate from runtime arithmetic."""

from contextlib import contextmanager
from dataclasses import dataclass
from unittest.mock import patch

import cardinality
import checks
import outer
import padding
import strict_outer
from count_ownership import audited_counts
from runtime import require


@dataclass(frozen=True)
class Parameters:
    q: int = 3
    w: int = 1
    n: int = 2
    k: int = 1
    ell: int = 0
    stock_value: int = 4
    p: int = 1
    z: int = 1
    t: int = 1

    def __post_init__(self):
        require(
            self.q in (2, 3)
            and 1 <= self.w <= 2
            and 1 <= self.n <= 3
            and 1 <= self.k <= 3
            and 0 <= self.ell < self.w,
            "bounded strict fixture digits",
        )
        require(
            all(1 <= value <= 2 for value in (self.p, self.z, self.t))
            and 1 <= self.stock_value <= 2 * self.q**self.k,
            "bounded strict fixture spectators and boundary stock",
        )

    def extents(self):
        return (
            self.q**self.w,
            self.q**self.k,
            self.q**self.ell,
            self.q ** (self.w * self.n),
        )


class Fixture(checks.Fixture):
    @contextmanager
    def chronology(self):
        self.events = []
        original_pass, original_transform = outer.body_pass, padding.transform

        def body_pass(source, *args, **kwargs):
            require(len(source.cells) - 1 == self.volume, "body uses genuine volume")
            spec = self.spec
            expected_gap = spec.q**spec.ell * spec.z * spec.q**spec.k
            require(
                checks.decode(args[4]) == expected_gap,
                "genuine other high field in body gap",
            )
            self.events.append("NEG" if kwargs.get("sign") else "ADD")
            return original_pass(source, *args, **kwargs)

        def transform(*args, **kwargs):
            restricting = kwargs.get("restricting", False)
            result = original_transform(*args, **kwargs)
            self.events.append("RESTRICT" if restricting else "PAD")
            try:
                if restricting:
                    require(
                        len(result.cells) - 1 == self.volume,
                        "immediate genuine restriction",
                    )
                return result
            except BaseException:
                result.clear()
                raise

        with (
            patch.object(outer, "body_pass", body_pass),
            patch.object(padding, "transform", transform),
        ):
            yield

    def callee(self, padded, rows):
        self.events.append("F")
        return super().callee(padded, rows)

    def check_result(self):
        result = super().check_result()
        require(
            self.events
            == [
                "ADD",
                "PAD",
                "F",
                "RESTRICT",
                "ADD",
                "PAD",
                "F",
                "RESTRICT",
                "NEG",
                "ADD",
            ],
            "two separate immediate restrictions in actual chronological trace",
        )
        result["chronology"] = self.events
        result["runtime_count_ownership"] = self.count_observation
        return result

    def run(self):
        try:
            with self.chronology(), checks.observed(self.tracker, self.meter):
                with audited_counts(cardinality.Tape) as observation:
                    self.count_observation = observation
                    self.result = strict_outer.interchange(
                        self.source,
                        self.atoms,
                        self.ring,
                        self.high,
                        self.spec.q,
                        *self.counts,
                        self.callee,
                        self.remainder,
                    )
        except ValueError as error:
            if self.fail_at is None:
                raise
            require(
                str(error) == "injected completed-callee failure"
                and len(self.calls) == self.fail_at,
                "expected strict callee failure",
            )
            require(self.tracker.live == {self.source}, "strict failed-call cleanup")
            require(
                bytes(self.source.cells) == self.saved and self.source.head == 1,
                "strict failed-call source preserved",
            )
            require(
                all(
                    bytes(c.tape.cells) == old and c.tape.head == 1
                    for c, old in zip(self.counts, self.snapshots, strict=True)
                ),
                "strict failed-call counts preserved",
            )
            return {"failed_at": self.fail_at, "calls": self.calls}
        require(self.fail_at is None, "strict expected failure occurred")
        return self.check_result()


def case(*, callee_factory=None, fail_at=None, **parameters):
    fixture = Fixture(Parameters(**parameters), callee_factory, fail_at)
    try:
        return fixture.run()
    finally:
        fixture.close()


def run_cases():
    specifications = (
        {},
        {"n": 1},
        {"stock_value": 5},
        {"q": 2, "n": 3, "k": 2, "stock_value": 6},
        {"q": 2, "n": 1, "k": 3, "stock_value": 15},
        {"q": 3, "w": 2, "n": 1, "ell": 1, "stock_value": 5},
        {
            "q": 2,
            "w": 2,
            "n": 1,
            "ell": 1,
            "k": 2,
            "stock_value": 7,
            "p": 2,
            "z": 2,
            "t": 2,
        },
        {"stock_value": 2},
        {"stock_value": 3},
        {"stock_value": 1},
    )
    return [case(**parameters) for parameters in specifications]
