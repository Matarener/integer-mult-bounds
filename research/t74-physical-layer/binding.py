# SPDX-License-Identifier: Apache-2.0
"""Bind the emitted mixed-provider T74 controller to physical packet groups.

I retain PR3385's common-view directions and nonlocal event implementations.
The changed initialization binds every provider, owner and private Z role.
"""
from collections import Counter
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compile_word import Compiler, canonical, need, read_native
from bundles import authenticate_prepared
from predecessor import activate
activate()
from cover import OrthogonalCover, act, is_orthogonal, multiply
from scalar_program import ScalarProgram
from selected_binding import Group, Owner, SelectedBinding, data_route, embed, literal, port_basis


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


class T74Binding(SelectedBinding):
    dimension = 73
    maximum_rank = 48
    families = 66304
    slots = 632
    centres = 8
    private = 99

    def __init__(self, prepared):
        prepared = Path(prepared)
        authenticate_prepared(prepared)
        self.providers = {pid: read_native(prepared / "bound/base/providers" / pid)
                          for pid in ("gauge44", "extra")}
        template = read(prepared / "hosted/GLOBAL-TEMPLATE.json.gz")
        self.data = dict(template=template, word=self.providers["gauge44"]["word"],
                         phases=read(prepared / "bound/base/work/complex-nine-native/DATA-PHASES.json"),
                         sigmas=read(prepared / "hosted/ACTUAL-SIGMAS.json.gz"))
        self.template = template
        need((template["m"], template["live"], template["physical"]) == (73, 66304, 66813),
             "complete T74 namespace")
        need(template["private_namespace"] == {"centers": [66304, 66312], "reserved_tableau": [66312, 66720],
             "zero_buffers": [66720, 66811], "coefficient": [66811, 66813]}, "actual private namespace")
        need(set(template["local_providers"]) == set(self.providers) and
             template["private_zero_buffer_lowering"]["frame"] == "FULL", "complete provider/private contract")
        need(len(template["calls"]) == 666 and len(template["execution_schedule"]) == 2222,
             "complete changed call/event inventory")
        self.events = tuple(template["execution_schedule"])
        self.cover = OrthogonalCover(self.dimension)
        self.identity = tuple(1 << i for i in range(self.dimension))
        self.bases = tuple(port_basis(q) for q in self.data["word"]["ports"])
        need(all(is_orthogonal(b) for b in self.bases), "source port bases")
        self.codes, self.recipes, self.catalogue = {}, {}, {}
        for pid, data in self.providers.items():
            need(data["word"]["ports"] == self.data["word"]["ports"], "common data-port order")
            need(template["local_providers"][pid]["local_programs"] == data["programs"],
                 "global-to-local literal program binding")
            for direction in ("forward", "backward"):
                code, recipes, _ = Compiler(data, direction).run()
                self.codes[pid, direction] = code
                for key, record in recipes.items():
                    expanded = embed(record, self.dimension)
                    need(key not in self.recipes or self.recipes[key] == expanded, "shared exact monomial")
                    self.recipes[key] = expanded
                for op in code:
                    if op[0] == "scalar" and op[4] not in self.catalogue:
                        self.catalogue[op[4]] = ScalarProgram(*op[4])
        for key in (("scale", -1, 1), ("add", 1, 1), ("add", -1, 1)):
            if key not in self.catalogue:
                self.catalogue[key] = ScalarProgram(*key)
        self.calls = {c["time"]: c for c in template["calls"]}
        need(set(self.calls) == set(range(666)), "complete distinct call times")
        self.remainders = {(r["replica"], r["child"], r["port"]): r for r in template["idle_children"]}
        need(len(self.remainders) == len(template["idle_children"]), "unique idle tails")
        self.owner_specs = {}
        self.bind_owners()
        need(not template["bank_padding"]["children"], "no unpriced bank child")
        self.check_profile()

    def bind_owners(self):
        cached, used = {}, set()
        for time, call in self.calls.items():
            pid = call["provider_id"]
            need(pid in self.providers and len(call["owners"]) == self.slots, "provider and complete owner slots")
            maps = self.template["private_zero_buffer_lowering"]["provider_maps"][pid]
            expected_z = {str(label): 66720 + i for i, label in enumerate(sorted(self.providers[pid]["word"]["zero_buffers"]))}
            need(maps == expected_z, "provider-specific disjoint Z map")
            owners = []
            for role, (family, route) in enumerate(call["owners"]):
                need(0 <= family < self.families, "borrowed live family")
                if role < 224:
                    port, stage = role % 112, call["stage"]
                    need(route == [1, stage, port], "literal data route")
                    key = ("data", stage, port)
                    if key not in cached:
                        cached[key] = data_route(self.bases[port], stage)
                    sigma = cached[key]
                    align = self.data["phases"]["recipes"][port]["stage_alignment"][stage]
                    side = "X" if role < 112 else "Y"
                    owners.append(Owner(family, sigma, act(sigma, align["entry_" + side]),
                                        act(sigma, align["exit_" + side])))
                    continue
                port = family % 112
                typ, child, offset = route[:3]
                need(typ in (3, 4), "helper route type")
                width = 9 if typ == 3 else route[3]
                spectators = () if typ == 3 else tuple(route[4])
                need(width == self.template["local_providers"][pid]["widths"][role - 224], "actual provider width")
                key = ("helper", port, child, offset, width, spectators)
                if key not in cached:
                    basis = self.bases[port]
                    axes = self.data["phases"]["recipes"][port]["idle_children"][child]["orthogonal_axes"]
                    active = tuple(axes[offset:offset + width])
                    need(len(active) == width, "available pending helper axes")
                    positions = tuple(basis.index(v) for v in active)
                    expected = tuple(i for i in range(73) if i not in positions)[:9 - width]
                    need(spectators == expected, "literal spectator completion")
                    order = positions + spectators + tuple(i for i in range(73) if i not in positions and i not in spectators)
                    sigma = tuple(basis[i] for i in order)
                    digest = sha256(canonical(sigma)).hexdigest()
                    need(self.data["sigmas"].get(digest) == list(sigma), "actual emitted helper chart")
                    used.add(digest)
                    cached[key] = sigma
                owners.append(Owner(family, cached[key]))
            need(len({o.family for o in owners}) == self.slots, "distinct call owners")
            self.owner_specs[time] = tuple(owners)
        need(len(used) == len(self.data["sigmas"]) == 8659, "complete emitted chart inventory")

    def check_profile(self):
        profile = Counter()
        for call in self.calls.values():
            profile.update(op[3] for op in self.codes[call["provider_id"], call["orientation"]] if op[0] == "child")
        profile.update(row["rank"] for row in self.template["idle_children"])
        need(dict(profile) == {1:1645680,2:470196,3:159468,4:71928,5:13716,8:5328,48:28190},
             "complete physical positive-child invoice")
        return dict(sorted(profile.items()))

    def group(self, event_index, subgroup, cover_index):
        event = self.events[event_index]
        if event["kind"] != "local_cover_sweep":
            return super().group(event_index, subgroup, cover_index)
        need(subgroup == 0, "one complete local invocation")
        call = self.calls[event["time"]]
        need(call["provider_id"] == event["provider_id"], "dispatch at actual call")
        g = self.cover.unrank(cover_index)
        owners = self.owner_specs[call["time"]]
        keys = tuple((o.family, self.cover.rank(multiply(g, o.sigma_columns))) for o in owners)
        code, recipes = [], {}

        def mono(role, rows, offset=0, inverse=False):
            record = literal(rows, offset)
            key = "global:" + sha256(canonical(record)).hexdigest()
            recipes[key] = record
            code.append(("monomial", -1, role, key, inverse))

        for role, owner in enumerate(owners):
            mono(role, g, inverse=True)
            if owner.entry:
                mono(role, self.identity, owner.entry)
        code.extend(self.codes[call["provider_id"], call["orientation"]])
        recipes.update(self.recipes)
        for role, owner in enumerate(owners):
            if owner.exit:
                mono(role, self.identity, owner.exit)
            mono(role, g)
        need(len(keys) == len(set(keys)) == self.slots and len(code) < 65536, "finite complete local group")
        return Group(keys, tuple(code), recipes)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared", type=Path)
    args = parser.parse_args()
    binding = T74Binding(args.prepared)
    print(json.dumps(dict(binding.inventory(), physical=binding.template["physical"],
                          positive_children=binding.check_profile(), scalar_literals=len(binding.catalogue)),
                     sort_keys=True, indent=2))
