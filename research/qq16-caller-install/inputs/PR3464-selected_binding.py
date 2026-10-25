# SPDX-License-Identifier: Apache-2.0
"""Finite selected global groups and exact cover/common-view conventions.

I retain PR2287's chronological construction, Gareth Davidson's actual helper
charts and the selected DATA-PHASES conventions. This compiles their physical
dispatch; it does not replace their native operator proofs.
"""
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json

from cover import OrthogonalCover, act, is_orthogonal, multiply, parity, transpose
from native_program import compile_local


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def literal(rows, offset=0):
    n = len(rows)
    return dict(matrix_rows=list(rows), offset=offset, phase=0,
                linear_Z4=[0] * n, quadratic_rows=[0] * n)


def embed(record, dimension):
    n = len(record["matrix_rows"])
    require(n <= dimension, "native embedding")
    return dict(matrix_rows=list(record["matrix_rows"]) + [1 << i for i in range(n, dimension)],
                offset=record["offset"], phase=record["phase"],
                linear_Z4=list(record["linear_Z4"]) + [0] * (dimension - n),
                quadratic_rows=list(record["quadratic_rows"]) + [0] * (dimension - n))


def port_basis(q, dimension=73):
    missing = next(i for i in range(9) if not (q >> i & 1))
    v = q ^ (1 << missing)
    order = list(range(dimension))
    order[0], order[missing] = order[missing], order[0]
    return tuple((1 << i) ^ (v if v >> i & 1 else 0) for i in order)


def data_route(basis, stage):
    identity = tuple(1 << i for i in range(len(basis)))
    if stage == 0:
        return identity
    swaps = [basis[1 + i] ^ (1 << (9 + 8 * (stage - 1) + i)) for i in range(8)]
    cols = []
    for coordinate in identity:
        value = coordinate
        for vector in swaps:
            if parity(coordinate & vector):
                value ^= vector
        cols.append(value)
    return tuple(cols)


@dataclass(frozen=True)
class Owner:
    family: int
    sigma_columns: tuple
    entry: int = 0
    exit: int = 0


@dataclass(frozen=True)
class Group:
    keys: tuple
    code: tuple
    recipes: dict


class SelectedBinding:
    dimension = 73
    maximum_rank = 48
    families = 14336
    slots = 704
    private = 8

    def __init__(self, data):
        self.data = data
        self.template = data["template"]
        self.events = tuple(self.template["execution_schedule"])
        self.cover = OrthogonalCover(self.dimension)
        self.identity = tuple(1 << i for i in range(self.dimension))
        self.bases = tuple(port_basis(q) for q in data["word"]["ports"])
        require(all(is_orthogonal(b) for b in self.bases), "selected port bases")
        self.codes, self.recipes = {}, {}
        for direction in ("forward", "backward"):
            code, recipes, _ = compile_local(data, direction)
            self.codes[direction] = code
            for key, record in recipes.items():
                extended = embed(record, self.dimension)
                if key in self.recipes:
                    require(self.recipes[key] == extended, "shared native recipe")
                self.recipes[key] = extended
        self.calls = {c["time"]: c for c in self.template["calls"]}
        self.remainders = {(r["replica"], r["child"], r["port"]): r
                           for r in self.template["idle_children"]}
        self.owner_specs = {}
        cached = {}
        used = set()
        for time, call in self.calls.items():
            owners = []
            for role, (family, route) in enumerate(call["owners"]):
                if role < 224:
                    port = role % 112
                    stage = call["stage"]
                    require(route == [1, stage, port], "literal data owner route")
                    key = ("data", stage, port)
                    if key not in cached:
                        cached[key] = data_route(self.bases[port], stage)
                    sigma = cached[key]
                    alignment = data["phases"]["recipes"][port]["stage_alignment"][stage]
                    side = "X" if role < 112 else "Y"
                    owners.append(Owner(family, sigma, act(sigma, alignment["entry_" + side]),
                                        act(sigma, alignment["exit_" + side])))
                else:
                    port = family % 112
                    typ, child, offset = route[:3]
                    width = 9 if typ == 3 else route[3]
                    spectators = () if typ == 3 else tuple(route[4])
                    require(typ in (3, 4), "helper owner type")
                    key = ("helper", port, child, offset, width, spectators)
                    if key not in cached:
                        basis = self.bases[port]
                        axes = data["phases"]["recipes"][port]["idle_children"][child]["orthogonal_axes"]
                        active = tuple(axes[offset:offset + width])
                        positions = tuple(basis.index(v) for v in active)
                        expected = tuple(i for i in range(73) if i not in positions)[:9 - width]
                        require(spectators == expected, "serialized helper spectator completion")
                        order = positions + spectators + tuple(i for i in range(73)
                                                               if i not in positions and i not in spectators)
                        sigma = tuple(basis[i] for i in order)
                        digest = sha256(canonical(sigma)).hexdigest()
                        require(data["sigmas"].get(digest) == list(sigma), "actual emitted helper chart")
                        used.add(digest)
                        cached[key] = sigma
                    owners.append(Owner(family, cached[key]))
            require(len(owners) == len({o.family for o in owners}) == 704, "distinct local owner families")
            self.owner_specs[time] = tuple(owners)
        require(len(used) == len(data["sigmas"]) == 10002, "complete emitted helper chart inventory")
        require(not self.template["bank_padding"]["children"], "selected padding has no child")

    def group_count(self, event_index):
        kind = self.events[event_index]["kind"]
        counts = {"local_cover_sweep": 1, "idle_cover_sweep": 224, "bridge": 112,
                  "terminal_Y_translations": 112, "terminal": 112,
                  "bank_padding_cover_sweep": 0, "translate_every_live_family": self.families}
        require(kind in counts, "complete selected global alphabet")
        return counts[kind]

    def group(self, event_index, subgroup, cover_index):
        require(0 <= subgroup < self.group_count(event_index), "finite global subgroup")
        event = self.events[event_index]
        kind = event["kind"]
        g = self.cover.unrank(cover_index)
        code, recipes = [], {}

        def mono(role, rows, offset=0, inverse=False):
            record = literal(rows, offset)
            key = "global:" + sha256(canonical(record)).hexdigest()
            recipes[key] = record
            code.append(("monomial", -1, role, key, inverse))

        if kind == "local_cover_sweep":
            call = self.calls[event["time"]]
            owners = self.owner_specs[call["time"]]
            keys = tuple((o.family, self.cover.rank(multiply(g, o.sigma_columns))) for o in owners)
            for role, owner in enumerate(owners):
                mono(role, g, inverse=True)
                if owner.entry:
                    mono(role, self.identity, owner.entry)
            code.extend(self.codes[call["orientation"]])
            recipes.update(self.recipes)
            for role, owner in enumerate(owners):
                if owner.exit:
                    mono(role, self.identity, owner.exit)
                mono(role, g)
        elif kind == "idle_cover_sweep":
            side, port = divmod(subgroup, 112)
            child = event["child_indices"][side]
            family = 896 * event["replica"] + (2 * event["pair"] + side) * 112 + port
            original = self.data["phases"]["recipes"][port]["idle_children"][child]
            remainder = self.remainders.get((event["replica"], child, port))
            if remainder:
                require(remainder["family"] == family, "idle family binding")
                active = tuple(original["orthogonal_axes"][remainder["pending_offset"]:])
                require(len(active) == remainder["rank"], "exact pending suffix")
                basis = self.bases[port]
                chart = active + tuple(v for v in basis if v not in active)
                frame = multiply(g, transpose(chart))
                mono(0, frame, inverse=True)
                code.append(("child", -1, 0, len(active)))
                mono(0, frame)
            theta = act(g, original["translation_after"])
            if theta:
                mono(0, self.identity, theta)
            keys = ((family, cover_index),)
        elif kind == "bridge":
            port = subgroup
            base = 896 * event["replica"] + port
            src, dst, c = event["src"], event["dst"], event["coefficient"]
            keys = tuple((base + 224 * pair + 112 * side, cover_index)
                         for pair, side in ((dst, 0), (src, 0), (src, 1), (dst, 1)))
            code = [("scalar", -1, 0, 1, ("add", c, 1)),
                    ("scalar", -1, 2, 3, ("add", -c, 1))]
        elif kind in ("terminal_Y_translations", "terminal"):
            port = subgroup
            base = 896 * event["replica"] + port
            if kind == "terminal_Y_translations":
                keys = tuple((base + 224 * pair + 112, cover_index) for pair in range(4))
                theta = act(g, self.data["phases"]["recipes"][port]["terminal_Y_translation"])
                for role in range(4):
                    mono(role, self.identity, theta)
            else:
                keys = tuple((base + 112 * role, cover_index) for role in range(8))
                code = [("exchange", -1, 2 * pair, 2 * pair + 1) for pair in range(4)]
        else:
            require(kind == "translate_every_live_family", "final global correction")
            mask = sum((((row.bit_count() - 1) // 2) & 1) << i for i, row in enumerate(g))
            keys = ((subgroup, cover_index),)
            if mask:
                mono(0, self.identity, mask)
        require(len(keys) == len(set(keys)) and 0 < len(keys) <= self.slots, "distinct global packets")
        return Group(tuple(keys), tuple(code), recipes)

    def inventory(self):
        return {"events": len(self.events), "event_counts": dict(Counter(e["kind"] for e in self.events)),
                "calls": len(self.calls), "owner_entries": sum(len(v) for v in self.owner_specs.values()),
                "helper_charts": len(self.data["sigmas"]), "cover_bits": self.cover.size.bit_length(),
                "subgroups_per_cover": sum(self.group_count(i) for i in range(len(self.events))),
                "scope": "Finite complete global dispatcher binding; numerical fixtures use reduced geometry."}
