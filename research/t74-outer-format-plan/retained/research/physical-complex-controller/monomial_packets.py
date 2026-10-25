# SPDX-License-Identifier: Apache-2.0
"""One physical monomial inventory with bounded finite geometry selection.

I reuse PR3087's execution body and PR3055's completed Compact calls. Selection
changes finite geometry only; input widths and payloads remain encoded tapes.
"""
import cohort
inherited = cohort.monomial_api()
from pair_dispatch import PairDispatch
from phase_recipe import Recipe
from records import Tape
from scratch_pool import ScratchPool
from session import OuterScope, erase_marker
from words import BLANK, need


def identity_literal(dimension):
    return dict(matrix_rows=[1 << i for i in range(dimension)], offset=0, phase=0,
                linear_Z4=[0] * dimension, quadratic_rows=[0] * dimension)


def embed(literal, dimension):
    old = len(literal["matrix_rows"])
    need(0 < old <= dimension <= 73, "fixed monomial embedding dimensions")
    return dict(matrix_rows=list(literal["matrix_rows"]) + [1 << i for i in range(old, dimension)],
                offset=literal["offset"], phase=literal["phase"],
                linear_Z4=list(literal["linear_Z4"]) + [0] * (dimension - old),
                quadratic_rows=list(literal["quadratic_rows"]) + [0] * (dimension - old))


class MonomialPackets(inherited.MonomialEngine):
    def __init__(self, names, vectors, native):
        need(type(names) is tuple and len(names) == len(set(names)), "fixed monomial schema")
        self.names = names
        self.vectors = tuple(vectors)
        self.recipe = Recipe(identity_literal(len(vectors)), vectors)
        positions = tuple(names.index(name) for name in vectors)
        need(not set(vectors) & {"u", "t", "b"} and
             names.index("u") < min(positions) and names.index("t") < min(positions) and
             names.index("b") > max(positions), "complete compact placement")
        # The union contains the finite affine alphabet for this schema.
        # It does not depend on a payload, width or variable address value.
        actions = tuple((None, target, False) for target in vectors) + tuple(
            (source, target, names.index(source) > names.index(target))
            for target in vectors for source in vectors if source != target)
        self.compact = PairDispatch(names, actions, vectors[0], native)
        self.pool = ScratchPool(8 * len(names) + 256)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)
        self.closed = True

    def select(self, literal):
        """Caller supplies a source-derived bounded geometry, never payload data."""
        need(self.closed and self.output.read() == BLANK and not self.pool.live and
             self.compact.closed and self.compact.output.read() == BLANK and
             not self.compact.pool.live and self.compact.binary.closed and
             self.compact.binary.native.closed, "closed consumed monomial selection")
        recipe = Recipe(literal, self.vectors)
        need(all(self.action_for(recipe, gate) in self.compact.actions for gate in recipe.word),
             "compiled universal affine alphabet")
        self.recipe = recipe

    def action_for(self, recipe, gate):
        kind, target, source = gate
        target_name = recipe.vectors[target]
        source_name = None if kind == "flip" else recipe.vectors[source]
        late = source_name is not None and self.names.index(source_name) > self.names.index(target_name)
        return source_name, target_name, late
