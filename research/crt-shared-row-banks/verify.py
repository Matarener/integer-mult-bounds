"""Execute the new cross-row bank interface, not a predecessor replay.

Produced by Nick Petalas. Apache-2.0.
"""
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import sys
import time

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "Module specification")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def modules():
    pins = json.loads((P / "SOURCES.json").read_text())["files"]
    for pin in pins:
        if pin["usage"] == "input":
            need(sha256((ROOT / pin["path"]).read_bytes()).hexdigest() == pin["sha256"], "Source bytes")
    old = load("shared_row_fixture", ROOT / "research/crt-paid-row-reentry/verify.py")
    mod = old.modules()
    shared = load("shared_row_bank", P / "shared.py")
    path = ROOT / "research/crt-current-row-query/join.py"
    joined = old.load("shared_row_join", path, shared.adapt_source(path.read_text()))
    return old, shared, joined, mod


def observe_bank(pool, sizes, identities):
    need(not pool.leased, "Retired bank lease")
    need({k: id(v) for k, v in pool.cells.items()} == identities, "Persistent physical identities")
    need({k: len(v) for k, v in pool.cells.items()} == sizes, "Fixed historical extents")
    need(all(all(x == "_" for x in v) for v in pool.cells.values()), "Full historical bank blank")


def new_query(mod, joined, pool, source, dirty, widths, ell, level, start, row):
    helper, base, rom, _, _, program = mod
    w, records, entry, numeric, _, _, row_module = base
    return joined.RowQuery(w, records, entry, numeric, row_module, rom, program,
                           source, dirty, widths, ell, level, start, row, pool)


def finish_row(old, mod, query, staging, source, dirty, initial_dirty, widths, expected, level, start):
    helper, base, _, _, adapter, _ = mod
    w, records, *_ = base
    owned = [] if query.output is None else [*query.entry.inputs, *query.entry.context.owned]
    adapter.consume_into_source(query, staging, widths, level, start)
    need(query.closed and source.head == 1, "Query closes before next row")
    need(old.decode(source, widths, w, records) == expected, "Current-state row endpoint")
    need(helper.snapshot(dirty) == initial_dirty, "Protected dirty bytes and heads")
    need(staging.head == 0 and all(x == "_" for x in staging.cells), "Staging retired")
    need(all(t.head == 1 and all(x == w.BLANK for x in t.cells) for t in owned), "Numerical retirement")
    need(all(t.head == 0 and all(x == "_" for x in t.cells) for t in query.ports), "Joined retirement")


def run_case(old, shared, joined, mod, mixed=False):
    helper, base, rom, _, _, _ = mod
    w, records, entry, _, caller_module, crt, _ = base
    moduli, widths, state = (5, 7, 3, 2), (3, 3, 2, 2), (3, 2, 1, 1)
    if mixed:
        moduli, widths, state = (2, 5, 7, 3), (2, 3, 3, 2), (1, 4, 7, 3)
    ell, level, start = 3, 2, 0
    precision = 1 + sum(widths)
    source = helper.axis_stream(w, records, entry, moduli, widths, state)
    source_identity = id(source.cells)
    original = bytes(source.cells)
    dirty = [helper.port(w, entry, helper.bits(3 * i + 1, precision) + [w.RIGHT]) for i in range(8)]
    for i, tape in enumerate(dirty):
        for _ in range(i % 3):
            tape.step(1)
    initial_dirty = helper.snapshot(dirty)
    staging = joined.Tape()
    sizes = shared.capacities(rom.REGS, precision, max(widths[2:]))
    pool = shared.BankPool(sizes)
    identities = {k: id(v) for k, v in pool.cells.items()}
    caller = caller_module.Caller(moduli, widths, ell, crt)
    expected, retained_queries, backings, trace = state, [], {}, []
    schedule = tuple(range(2 * ell - 1)) + tuple(reversed(range(2 * ell - 1)))
    if mixed:
        schedule = (1, 1)  # Same involutive row twice, with height 3 then 2 each time.
    for row in schedule:
        specs = [s for s in caller.row(expected, level, row) if 2 <= s[0] < 4]
        expected = caller.apply(expected, specs)
        before = bytes(source.cells), source.head
        query = new_query(mod, joined, pool, source, dirty, widths, ell, level, start, row)
        need((bytes(source.cells), source.head) == before, "Query borrows source unchanged")
        row_backings, _ = old.footprint(query)
        retained_queries.append(query)
        finish_row(old, mod, query, staging, source, dirty, initial_dirty, widths, expected, level, start)
        observe_bank(pool, sizes, identities)
        need(id(source.cells) == source_identity, "Persistent owned source")
        backings.update(row_backings)
        trace.append(dict(row=row, state=list(expected), producer_calls=query.invocations,
                          row_backing_cells=sum(map(len, row_backings.values()))))
    need(bytes(source.cells) == original and expected == state, "Complete forward/reverse endpoint")
    bank_cells = sum(sizes.values())
    fresh_cells = sum(x["row_backing_cells"] for x in trace) + len(staging.cells)
    shared_cells = sum(map(len, backings.values())) + len(staging.cells)
    active = sum(q.output is not None for q in retained_queries)
    need(shared_cells == fresh_cells - (active - 1) * bank_cells, "Exact retained storage reduction")
    need(shared_cells < fresh_cells, "Strict storage improvement")
    return dict(rows=len(schedule), active_rows=active, producer_calls=sum(q.invocations for q in retained_queries),
                precision=precision, height=max(widths[2:]), bank_roles=len(sizes), bank_cells=bank_cells,
                distinct_bank_baseline_cells=fresh_cells, shared_bank_cells=shared_cells,
                saved_cells=fresh_cells - shared_cells, trace=trace)


def controls(shared, mod):
    rom = mod[2]
    sizes = shared.capacities(rom.REGS, 11, 3)
    pool = shared.BankPool(sizes)
    ids = {k: id(v) for k, v in pool.cells.items()}
    rejected = []
    messages = {"overlapping_lease": "Bank already leased", "wrong_release": "Bank lease ownership",
                "dirty_historical_tail": "Full historical bank blank", "changed_extent": "Fixed historical extents",
                "source_drift": "Exact source-bound allocation seam"}
    for label, message in messages.items():
        fresh = shared.BankPool(sizes)
        try:
            if label == "overlapping_lease":
                fresh.acquire(); fresh.acquire()
            elif label == "wrong_release":
                fresh.acquire(); fresh.release({})
            elif label == "dirty_historical_tail":
                pool.cells["arena"][-1] = "1"
                observe_bank(pool, sizes, ids)
            elif label == "changed_extent":
                fresh.cells["rom"].append("_")
                observe_bank(fresh, sizes, {k: id(v) for k, v in fresh.cells.items()})
            else:
                shared.adapt_source("not the pinned query")
        except ValueError as error:
            need(str(error) == message, "Expected semantic rejection: " + label)
            rejected.append(label)
        else:
            raise ValueError("Defective interface accepted: " + label)
        if label == "dirty_historical_tail":
            pool.cells["arena"][-1] = "_"
    observe_bank(pool, sizes, ids)
    return rejected


def main():
    start = time.monotonic()
    old, shared, joined, mod = modules()
    hashes = {name: sha256((P / name).read_bytes()).hexdigest()
              for name in ("shared.py", "verify.py", "SOURCES.json")}
    result = dict(status="PASS_CRT_SHARED_ROW_BANKS", claim_type="scoped construction and composition proof",
                  implementation_sha256=hashes,
                  case=run_case(old, shared, joined, mod),
                  mixed_height_control=run_case(old, shared, joined, mod, mixed=True),
                  controls=controls(shared, mod))
    if "--write" in sys.argv:
        (P / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(result == json.loads((P / "RESULT.json").read_text()), "Generated receipt")
    print(result["status"], json.dumps(result["case"], sort_keys=True), "controls=" + str(len(result["controls"])))
    print("elapsed_seconds=" + str(round(time.monotonic() - start, 3)))


if __name__ == "__main__":
    main()
