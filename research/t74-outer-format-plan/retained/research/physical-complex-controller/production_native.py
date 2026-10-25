# SPDX-License-Identifier: Apache-2.0
"""Genuine selected PR2899 factory; no reduced fixture program in production."""
import cohort
cohort.activate()
PRIME = 213 * (1 << 80) + 1


def build_native(q=PRIME):
    """Fix a source-admissible prime q>2**80 before varying input precision.

    The caller must discharge the selected denominator/chart hypotheses.
    The inherited constructor also performs its finite primality check. This
    factory is explicit but not claimed practically executable at this q.
    """
    from catalogue import Catalogue, Specifications
    from node import selected_topology
    from macro_binding import SelectedBinding
    from macro_code import compile_node
    from encoded import Profile
    from ordinary import Ordinary
    from words import need
    need(type(q) is int and q > 1 << 80, "fixed selected native prime range")
    catalogue = Catalogue(q)
    specifications = Specifications(catalogue)
    topology = selected_topology(catalogue)
    binding = SelectedBinding(specifications)
    programs = (compile_node(topology, binding, mode=0),)
    return Ordinary(q, binding, topology, programs, capacity=1 << 24,
                    profile=Profile(), fixture_index_floor=0)
