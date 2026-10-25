#!/usr/bin/env python3
"""Source-bound caller ownership join, complete small cube and failure controls.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
The retained fixture/oracles are JoyboyBrian's #5055, used without deletions.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
from types import FunctionType, SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(value, message):
    if not value:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate():
    rows = json.loads((HERE / "SOURCES.json").read_text())["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    for row in inputs:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
             "source bytes: " + row["path"])
    return len(inputs)


def image(tape):
    return bytes(tape.cells), tape.head


def meter(tapes):
    unique = tuple({id(tape): tape for tape in tapes}.values())
    return {name: sum(getattr(tape.meter, name) for tape in unique)
            for name in ("reads", "writes", "moves")}


def cell(value):
    return (lambda: value).__closure__[0]


def exercise():
    observations = []
    path = ROOT / "research/r437-streaming-directory/verify.py"

    def replacement():
        adapter = load("r437_canonical_adapter", HERE / "adapter.py")
        predecessor = load("r437_standalone_workspace",
                           ROOT / "research/r437-streamed-leaf-workspace/pooled.py")
        import records
        from macro_machine import Machine
        from scratch_pool import ScratchPool
        from words import BLANK, LEFT

        bounds = load("r437_canonical_bounds", HERE / "bounds.py")
        tariff_cases = 0
        for n in range(17):
            for t in range(17):
                returned, destination = records.Tape(), records.Tape()
                for k in range(n):
                    returned.append((k // 2) % 2)
                for k in range(t):
                    destination.append((k + 1) % 2)
                returned.rewind()
                destination.rewind()
                shell = object.__new__(Machine)
                shell.roles = {"current": destination}
                before = meter((returned, destination))
                Machine.commit(shell, returned, "current")
                returned.clear()
                after = meter((returned, destination))
                actual = {key: after[key] - before[key] for key in before}
                need(actual == bounds.commit_and_retire(n, t), "literal complete commit/retirement tariff")
                need(destination.cells[1:] == bytes((k // 2) % 2 for k in range(n)) +
                     bytes([BLANK]) * max(0, t - n), "overwrite preserves full destination backing")
                need(all(x == BLANK for x in returned.cells[1:]), "retired raw output remains charged")
                destination.clear()
                tariff_cases += 1

        def run(*args, **kwargs):
            q = args[3].q
            roles = tuple(records.Tape() for _ in range(4))
            destination = records.Tape()
            pool = ScratchPool(adapter.capacity(q))
            controls = []
            # Failure probes execute the identical coefficient body but use a
            # separate checker-only callback counter. Production calls retain
            # the original closure, including every fixture assertion.
            coefficient = args[9]
            names = coefficient.__code__.co_freevars
            need(names.count("calls") == 1, "source fixture call observer")
            calls = [0]
            closure = tuple(cell(calls) if name == "calls" else value
                            for name, value in zip(names, coefficient.__closure__))
            control_coefficient = FunctionType(coefficient.__code__, coefficient.__globals__,
                                               coefficient.__name__, coefficient.__defaults__, closure)
            active_args = (*args[:9], control_coefficient, *args[10:])

            def reject(name, expected, call):
                try:
                    call()
                except ValueError as error:
                    need(str(error) == expected, name + " wrong rejection: " + str(error))
                else:
                    raise ValueError(name + " accepted")
                controls.append(dict(name=name, reason=expected))

            def invoke(**changes):
                settings = dict(pool=pool, roles=roles)
                settings.update(changes)
                return adapter.run_into(*active_args, **kwargs, **settings)

            reject("uninstalled pool", "canonical pool already installed", invoke)
            with pool.install():
                reject("borrowed output alias", "persistent roles disjoint from borrows and scratch",
                       lambda: invoke(roles=(args[0], *roles[1:])))
                reject("scratch physical alias", "persistent roles disjoint from borrows and scratch",
                       lambda: invoke(roles=(pool.tapes[0], *roles[1:])))
                roles[1].write(0)
                reject("dirty producer role", "empty persistent body", invoke)
                roles[1].clear()
                lease = pool.acquire()
                reject("live macro entry", "empty canonical pool at macro entry", invoke)
                # The original CALL guard executes before any other machine use.
                shell = object.__new__(Machine)
                shell.pool = pool
                reject("live lease at actual CALL", "completed macro closes all scratch leases",
                       lambda: shell.call(None))
                lease.clear()
            short = ScratchPool(adapter.capacity(q) - 1)
            with short.install():
                reject("under-reserved pool", "canonical stream role reserve",
                       lambda: invoke(pool=short))

            old_workspace = predecessor.Workspace(q)
            with pool.install():
                reject("standalone adapter under caller", "physical Tape allocation inside a completed macro",
                       lambda: predecessor.run(*active_args, **kwargs, workspace=old_workspace))
            leaked_on_failure = len(pool.live)
            need(leaked_on_failure == 2, "old failure leaves fibre and single Counts")
            # Explicit test cleanup, not an assertion of exception rollback.
            for lease in tuple(pool.live.values()):
                lease.clear()
            pool.empty()
            old_workspace.pool.empty()

            original_preserve = adapter.preserve
            adapter.preserve = lambda current, residents: current.empty()
            try:
                with pool.install():
                    reject("global empty at local prefix", "completed macro closes all scratch leases", invoke)
            finally:
                adapter.preserve = original_preserve
            pool.empty()
            need(all(t.head == 1 and all(x == BLANK for x in t.cells[1:]) for t in roles),
                 "specific failed-prefix cleanup")

            def leak_at_entry(when, current, residents, prefix):
                if when == "entry":
                    current.acquire()

            with pool.install():
                reject("unretired consumer lease", "consumer preserves exactly the producer leases",
                       lambda: invoke(boundary_observer=leak_at_entry))
            need(len(pool.live) == 1, "one deliberate leaked lease")
            for lease in tuple(pool.live.values()):
                lease.clear()
            pool.empty()

            def replace_resident(current, residents):
                slot = min(residents)
                residents[slot].clear()
                replacement = current.acquire()
                need(replacement.slot == slot and len(current.live) == len(residents),
                     "same-slot control preserves lease count")
                original_preserve(current, residents)

            adapter.preserve = replace_resident
            try:
                with pool.install():
                    reject("same-slot producer replacement", "consumer preserves exactly the producer leases", invoke)
            finally:
                adapter.preserve = original_preserve
            for lease in tuple(pool.live.values()):
                lease.clear()
            pool.empty()
            need(calls[0] == 18, "three controlled complete prefixes, six callbacks each")

            # Independently count every record tape touched by the standalone
            # source interval, then the installed-pool interval. This generic
            # fixture has no borrowed Program; its explicit record borrows are
            # precisely these payload/directory/cardinality tapes.
            explicit = (args[0], args[1], args[4], args[6].tape, args[8].highs.tape,
                        args[3].before.tape, args[3].gap.tape, args[3].suffix.tape)
            numeric = (args[5].arena, args[8].ring.arena)
            created = []
            old_init = records.Tape.__init__

            def count_created(tape):
                old_init(tape)
                created.append(tape)

            record_start = meter(explicit)
            numeric_start = [meter((arena,)) for arena in numeric]
            calls[0] = 0
            records.Tape.__init__ = count_created
            try:
                reference = adapter.source.run(*active_args, **kwargs)
            finally:
                records.Tape.__init__ = old_init
            record_end = meter((*explicit, *created))
            numeric_end = [meter((arena,)) for arena in numeric]
            reference_actions = {key: record_end[key] - record_start[key] for key in record_start}
            reference_numeric = [{key: end[key] - start[key] for key in start}
                                 for start, end in zip(numeric_start, numeric_end)]
            need(calls[0] == 1458, "complete standalone source tariff calibration")
            reference_output = image(reference)
            reference.clear()

            active_args = args
            pool = ScratchPool(adapter.capacity(q))
            roles = tuple(records.Tape() for _ in range(4))
            before = meter((*pool.tapes, *roles, destination))
            record_start = meter((*explicit, *pool.tapes, *roles))
            numeric_start = [meter((arena,)) for arena in numeric]
            boundaries = 0
            resident_snapshot = None
            stable_residents = None
            physical_ids = tuple(map(id, pool.tapes))
            backing_first = None
            backing_last = None
            maximum_residents = 0

            def observe(when, current, residents, prefix):
                nonlocal boundaries, resident_snapshot, stable_residents
                nonlocal backing_first, backing_last, maximum_residents
                need(tuple(map(id, current.tapes)) == physical_ids, "fixed canonical physical inventory")
                need(len(residents) == 5, "exact live producer Count inventory")
                if when == "entry":
                    resident_snapshot = {slot: (lease, image(lease.physical)) for slot, lease in residents.items()}
                    maximum_residents = max(maximum_residents, len(residents))
                    if stable_residents is None:
                        stable_residents = dict(residents)
                    need(residents == stable_residents, "same producer leases across all prefixes")
                    need(prefix is roles[2], "same physical current-prefix role")
                else:
                    need(all(lease is resident_snapshot[slot][0] and
                             image(lease.physical) == resident_snapshot[slot][1]
                             for slot, lease in residents.items()),
                         "producer Count bytes and heads restored by every consumer")
                    need(all(t.cells[0] == LEFT and t.head == 1 and
                             all(x == BLANK for x in t.cells[1:])
                             for slot, t in enumerate(current.tapes) if slot not in residents),
                         "all nonresident scratch backing erased at every prefix")
                    boundaries += 1
                    backing_last = sum(len(t.cells) for t in pool.tapes)
                    if backing_first is None:
                        backing_first = backing_last

            with pool.install():
                result = invoke(boundary_observer=observe)
                record_end = meter((*explicit, *pool.tapes, *roles))
                numeric_end = [meter((arena,)) for arena in numeric]
                joined_actions = {key: record_end[key] - record_start[key] for key in record_start}
                joined_numeric = [{key: end[key] - start[key] for key in start}
                                  for start, end in zip(numeric_start, numeric_end)]
                need(image(result) == reference_output, "standalone source and installed caller output")
                need(joined_numeric == reference_numeric, "identical complete numerical Word traffic")
                need(result is roles[0] and not pool.live, "owned output and no leases before commit")
                shell = object.__new__(Machine)
                shell.roles = {"current": destination}
                Machine.commit(shell, result, "current")
                need(image(destination) == image(result), "literal canonical output commit")
                need(result.cells[1] != BLANK, "raw commit retains source ownership")
                result.clear()
                pool.empty()
                need(all(t.head == 1 and all(x == BLANK for x in t.cells[1:]) for t in roles),
                     "all four temporary persistent roles blank before caller boundary")
            after = meter((*pool.tapes, *roles, destination))
            bound = bounds.backing(q=q, prefixes=243, fibre=81, old_fields=1,
                                   code_bits=4, dimension=2, residue_bits=5, index_bits=8,
                                   program_body=0, callback_depth=0)
            need(sum(len(t.cells) for t in pool.tapes) <= bound["pool_cells"] and
                 sum(len(t.cells) for t in roles[1:]) <= bound["three_producer_cells"] and
                 len(roles[0].cells) <= bound["full_output_cells"], "conditional source extent bounds")
            surcharge = bounds.pooling_surcharge(roles=len(pool.tapes), prefixes=boundaries,
                                                  acquisitions=pool.allocations, callback_closes=0)
            difference = sum(joined_actions.values()) - sum(reference_actions.values())
            need(difference <= surcharge, "complete fixture record-traffic surcharge bound")
            observations.append(dict(
                prefixes=boundaries, capacity=len(pool.tapes), maximum_live=pool.peak,
                producer_residents=maximum_residents, acquisitions=pool.allocations,
                backing_after_first=backing_first, backing_after_last=backing_last,
                final_pool_backing=sum(len(t.cells) for t in pool.tapes),
                producer_role_backing=[len(t.cells) for t in roles[1:]],
                full_output_backing=len(roles[0].cells), canonical_destination_backing=len(destination.cells),
                owned_record_actions={name: after[name] - before[name] for name in before},
                all_leases_retired=not pool.live, canonical_commit=True,
                old_failure_live_counts=leaked_on_failure, controls=controls,
                exact_commit_tariff_cases=tariff_cases, conditional_backing_bound=bound,
                fixture_pooling_surcharge_bound=surcharge,
                fixture_record_traffic_difference=difference,
                standalone_record_actions=reference_actions,
                joined_record_actions_before_commit=joined_actions,
                unchanged_numerical_actions=dict(index=joined_numeric[0], residue=joined_numeric[1]),
            ))
            return destination

        return SimpleNamespace(visit=adapter.source.visit, run=run)

    tree = ast.parse(path.read_text(), filename=str(path))
    edits = 0

    class Bind(ast.NodeTransformer):
        def visit_Assign(self, node):
            nonlocal edits
            if any(isinstance(t, ast.Name) and t.id == "streaming" for t in node.targets):
                need(isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
                     and node.value.func.id == "module", "pinned fixture load")
                edits += 1
                node.value = ast.Call(ast.Name("REPLACEMENT", ast.Load()), [], [])
            return self.generic_visit(node)

    tree = ast.fix_missing_locations(Bind().visit(tree))
    need(edits == 1, "one fixture binding change and no deleted checks")
    namespace = {"__file__": str(path), "__name__": "r437_canonical_fixture", "REPLACEMENT": replacement}
    exec(compile(tree, str(path), "exec"), namespace)
    result = namespace["run"]()
    need(len(observations) == 1 and observations[0]["prefixes"] == 243,
         "all complete producer-consumer boundaries")
    return dict(status="PASS_R437_CANONICAL_WORKSPACE", fixture=result,
                caller_boundary=observations[0], fixture_ast_edits=edits,
                full_node_executed=False, source87_calibration_executed=False,
                selected_frontier_changed=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    count = authenticate()
    result = exercise()
    result["authenticated_inputs"] = count
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    path = HERE / "RESULT.json"
    if args.write:
        path.write_text(encoded)
    else:
        need(path.read_text() == encoded, "complete deterministic receipt")
    print(result["status"])


if __name__ == "__main__":
    main()
