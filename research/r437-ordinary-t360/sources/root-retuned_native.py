"""Retune the authenticated ordinary cohort before root ownership."""

from active_sources import active, require


def profile():
    return active().encoded.Profile(numerator=1, denominator=577)


def retune(native):
    cohort = active()
    require(isinstance(native, cohort.ordinary.Ordinary) and not native.closed
            and not native.pool.live and native.output.read() == cohort.ordinary.BLANK
            and all(not bank.live and not bank.initialized for bank in native.banks),
            "fresh native from the active cohort")
    current = native.profile
    require((current.dimension, current.child_rank, current.row_factor) == (64, 42, 269241600),
            "unchanged ordinary geometry and stock")
    native.profile = profile()
    return native


def build_native():
    cohort = active()
    return retune(cohort.production.build_native(cohort.production.PRIME))
