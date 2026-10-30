"""Exact constant setup for the one-axis p16 complete physical witness."""
from contextlib import contextmanager
from unittest.mock import patch
from chirp_sources import require


@contextmanager
def compiled_setup():
    from cardinal_counts import Count
    from encoded import compare
    from router_metadata import owned
    # These exact integer inequalities certify the retained floor-power values.
    # This specializes metadata only; all data and child operations still run.
    require(16**1000 <= 17**997 < 17**1000
            and 17**1000 <= 18**997 < 18**1000 and 1**500 == 1,
            "exact compiled fractional-power fixture certificates")
    calls = {"17^(.997)": 0, "18^(.997)": 0, "1^(.002)": 0}

    def floor_power(value, numerator, denominator):
        if (numerator, denominator) == (997, 1000):
            for incoming, output in ((17, 16), (18, 17)):
                with owned(Count.literal(incoming)) as (constant,):
                    if compare(value, constant) == 0:
                        calls[str(incoming)+"^(.997)"] += 1
                        return Count.literal(output)
        elif (numerator, denominator) == (1, 500):
            with owned(Count.literal(1)) as (one,):
                if compare(value, one) == 0:
                    calls["1^(.002)"] += 1
                    return Count.literal(1)
        raise ValueError("outside the certified one-axis p16 setup fixture")

    with patch("composed_plan.floor_power", floor_power), patch("active_plan.floor_power", floor_power):
        yield calls
