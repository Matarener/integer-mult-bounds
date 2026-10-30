"""Complete high-route comparisons; incumbent includes PR3343's carry saving."""
from fractions import Fraction as F
from unittest.mock import patch
import fused_sources
fused_sources.activate()
from fused_adapter import AffineAdapter
from words import need


def old_checks():
    return fused_sources.load('affine_incumbent_routes', 'research/high-carry-streams/check_routes.py')


def run_case(case, optimized):
    old = old_checks()
    with patch.object(old, 'CarryAdapter', AffineAdapter if optimized else old.CarryAdapter):
        return old.run_case(case, True)


def cases():
    return [
        dict(q=3, width=2, low=((2, 1), (1, 1)), word=(("scale", 0, 0, F(4)),),
             old_prefixes=2, fibre_value=3),
        dict(q=3, width=2, low=((2, 1), (1, 1)), word=(("scale", 0, 0, F(1, 4)),),
             old_prefixes=2, fibre_value=3),
        dict(q=3, width=2, low=((1, 2), (2, 2)), word=(("add", 0, 1, F(1, 2)),)*3,
             old_prefixes=2, fibre_value=3),
        dict(q=5, width=2, low=((1, 4), (2, 1)),
             word=(("add", 0, 1, F(-1, 4)), ("scale", 1, 1, F(4)), ("swap", 0, 1, F(1))),
             old_prefixes=1, fibre_value=1),
        dict(q=3, width=3, low=((2, 1), (1, 1)),
             word=(("add", 0, 1, F(1, 4)), ("scale", 1, 1, F(2))),
             old_prefixes=1, fibre_value=1),
        dict(q=3, width=1, low=((1, 2), (2, 2)),
             word=(("add", 0, 1, F(1, 4)), ("scale", 1, 1, F(4))),
             old_prefixes=2, fibre_value=3),
    ]


def run():
    result = []
    for index, case in enumerate(cases()):
        before, _ = run_case(case, False)
        after, _ = run_case(case, True)
        need(before['calls'] == after['calls'], 'complete native call bill unchanged')
        need(before['columns'] == after['columns'], 'same complete route source')
        result.append(dict(case=index, before=before, after=after))
    return result
