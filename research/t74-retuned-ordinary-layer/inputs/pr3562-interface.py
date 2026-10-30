"""Opt-in ordinary backend with the proved reciprocal root coupling."""

from predecessor import require, runtime


def profile():
    _, encoded, _ = runtime()
    return encoded.Profile(numerator=1, denominator=577)


def ordinary(q, binding, topology, programs, **options):
    """Retain the source backend and its selected-source theorem premises.

    Reduced geometries may exercise the interface but do not establish the
    selected odd-prime theorem. This factory changes no global default.
    """
    require("profile" not in options, "one certified coupling profile")
    module, _, _ = runtime()
    return module.Ordinary(q, binding, topology, programs, profile=profile(), **options)


def binary(native):
    _, _, module = runtime()
    require(native.profile == profile(), "retuned binary consumer profile")
    return module.Binary(native)
