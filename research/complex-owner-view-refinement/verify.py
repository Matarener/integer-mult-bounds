#!/usr/bin/env python3
"""Exact original-PR3385 owner/common-view controls, without a numerical payload.

SPDX-License-Identifier: Apache-2.0
Sagar Thakrar (thakrarsagar), with substantial OpenAI Codex assistance.
Jose Manuel/jmbarrancoml's frozen PR3385 modules remain unchanged. The owner
algebra is credited to the retained PR2569/PR2287/PR3106 lineage.
"""

from collections import Counter
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sys
from types import ModuleType
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "inputs/pr3385/"
N = 73
IDENTITY = tuple(1 << i for i in range(N))
MODULES = ("scalar_program", "native_program", "cover", "selected_binding", "selected_source")


def require(value, reason):
    if not value:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def authenticate(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    rows = [(root, row) for row in manifest["files"] if row["usage"] == "input"]
    rows += [(HERE, row) for row in manifest["frozen_sources"]]
    raw, hashes = {}, {}
    for base, row in rows:
        value = (base / row["path"]).read_bytes()
        require(sha(value) == row["sha256"], "Input changed: " + row["path"])
        hashes[row["path"]] = row["sha256"]
        if base == HERE:
            raw[row["path"]] = value
    return raw, hashes


def execute(name, raw):
    module = ModuleType(name)
    module.__file__ = str(ROOT / "research/physical-complex-controller" / (name + ".py"))
    sys.modules[name] = module
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return module


@contextmanager
def source_modules(raw):
    require(not any(name in sys.modules for name in MODULES), "cold source module namespace")
    try:
        loaded = {name: execute(name, raw[PREFIX + name + ".py"]) for name in MODULES}
        yield loaded
    finally:
        for name in MODULES:
            sys.modules.pop(name, None)


def apply(columns, vector):
    """Independent convention: columns are images of standard basis vectors."""
    out = 0
    while vector:
        bit = vector & -vector
        out ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return out


def transpose(columns):
    rows = [0] * len(columns)
    for j, column in enumerate(columns):
        while column:
            bit = column & -column
            rows[bit.bit_length() - 1] |= 1 << j
            column ^= bit
    return tuple(rows)


def compose(left, right):
    return tuple(apply(left, column) for column in right)


def orthogonal(columns):
    return (len(columns) == N and all(type(c) is int and 0 <= c < 1 << N for c in columns)
            and compose(transpose(columns), columns) == IDENTITY)


def port_columns(port):
    missing = next(i for i in range(9) if not port & (1 << i))
    normal = port ^ (1 << missing)
    reflection = tuple(unit ^ (normal if (normal & unit).bit_count() % 2 else 0)
                       for unit in IDENTITY)
    out = list(reflection)
    out[0], out[missing] = out[missing], out[0]
    require(out[0] == port and orthogonal(tuple(out)), "independent port chart")
    return tuple(out)


def data_columns(basis, stage):
    """Exchange the eight named port axes with their stage-coordinate axes."""
    require(type(stage) is int and 0 <= stage <= 8, "data stage")
    if stage == 0:
        return IDENTITY
    pairs = tuple(zip(basis[1:9], IDENTITY[9 + 8 * (stage - 1):9 + 8 * stage]))
    out = []
    for unit in IDENTITY:
        image = unit
        for left, right in pairs:
            if ((unit & left).bit_count() + (unit & right).bit_count()) % 2:
                image ^= left ^ right
        out.append(image)
    require(orthogonal(tuple(out)), "independent stage exchange")
    return tuple(out)


def helper_columns(data, basis, port, route):
    kind, child, offset = route[:3]
    require(kind in (3, 4), "helper route type")
    width = 9 if kind == 3 else route[3]
    spectators = () if kind == 3 else tuple(route[4])
    axes = data["phases"]["recipes"][port]["idle_children"][child]["orthogonal_axes"]
    active = tuple(axes[offset:offset + width])
    require(len(active) == width and len(set(active)) == width, "complete helper active axes")
    remaining = tuple(i for i, vector in enumerate(basis) if vector not in active)
    require(spectators == remaining[:9 - width], "independent helper completion")
    leading = active + tuple(basis[i] for i in spectators)
    columns = leading + tuple(vector for vector in basis if vector not in leading)
    require(orthogonal(columns), "independent complete helper chart")
    key = sha(canonical(columns))
    require(data["sigmas"].get(key) == list(columns), "literal emitted helper chart")
    return columns, key


def owner_inventory(data, binding):
    bases = tuple(port_columns(port) for port in data["word"]["ports"])
    charts, used, expected = {}, set(), {}
    digest, kinds, nonzero = hashlib.sha256(), Counter(), Counter()
    for call in data["template"]["calls"]:
        rows = []
        for role, (family, route) in enumerate(call["owners"]):
            port = role % 112 if role < 224 else family % 112
            key = ("data", call["stage"], port) if role < 224 else ("helper", port, canonical(route))
            if key not in charts:
                if role < 224:
                    charts[key] = data_columns(bases[port], call["stage"])
                else:
                    charts[key], emitted = helper_columns(data, bases[port], port, route)
                    used.add(emitted)
            columns = charts[key]
            if role < 224:
                require(route == [1, call["stage"], port], "literal data route")
                side = "X" if role < 112 else "Y"
                alignment = data["phases"]["recipes"][port]["stage_alignment"][call["stage"]]
                incoming, outgoing = alignment["entry_" + side], alignment["exit_" + side]
                kinds["data_" + side] += 1
            else:
                incoming = outgoing = 0
                kinds["helper_type_" + str(route[0])] += 1
            pulled = (apply(transpose(columns), incoming), apply(transpose(columns), outgoing))
            actual = binding.owner_specs[call["time"]][role]
            require((actual.family, actual.sigma_columns, actual.entry, actual.exit) ==
                    (family, columns, *pulled), "source owner chart or translation")
            record = (family, columns, incoming, outgoing)
            rows.append(record)
            digest.update(canonical((call["time"], role, *record)) + b"\n")
            nonzero["entry"] += bool(incoming)
            nonzero["exit"] += bool(outgoing)
        require(len(rows) == len({row[0] for row in rows}) == 704, "independent distinct owner families")
        expected[call["time"]] = rows
    require(len(expected) == 144 and len(used) == len(data["sigmas"]) == 10002, "complete literal owner inventory")
    return expected, dict(calls=len(expected), owners=144 * 704, owner_sha256=digest.hexdigest(),
                          helper_charts=len(used), kinds=dict(kinds), nonzero_translations=dict(nonzero))


class MatrixCover:
    """Declared dispatch adapter: labels are exact matrices, not cover ordinals.

    Only rank/unrank representation is substituted. The original group body,
    all its matrix multiplications, recipe construction and opcode order run.
    """
    def __init__(self, rows, size):
        self.rows, self.size = rows, size

    def unrank(self, token):
        require(token == "chosen_cover", "symbolic cover token")
        return self.rows

    def rank(self, rows):
        return tuple(rows)


def affine_operations(operations, recipes):
    maps, order = {}, []
    for op in operations:
        require(len(op) == 5 and op[:2] == ("monomial", -1), "global wrapper opcode")
        _, _, role, key, inverse = op
        if not order or role != order[-1]:
            order.append(role)
        record = recipes[key]
        require(record["phase"] == 0 and not any(record["linear_Z4"]) and
                not any(record["quadratic_rows"]), "unexpected owner wrapper phase")
        columns = transpose(tuple(record["matrix_rows"]))
        offset = record["offset"]
        if inverse:
            columns = transpose(columns)
            offset = apply(columns, offset)
        old, shift = maps.get(role, (IDENTITY, 0))
        maps[role] = compose(columns, old), apply(columns, shift) ^ offset
    require(order == list(range(704)), "wrapper owner order and coverage")
    return maps


def check_group(binding, event_index, owners, rows, cache):
    group = binding.group(event_index, 0, "chosen_cover")
    call = binding.calls[binding.events[event_index]["time"]]
    start = next(i for i, op in enumerate(group.code) if op[1] != -1)
    middle = binding.codes[call["orientation"]]
    end = start + len(middle)
    require(group.code[start:end] == middle, "complete unchanged local word")
    incoming = affine_operations(group.code[:start], group.recipes)
    outgoing = affine_operations(group.code[end:], group.recipes)
    d_columns = transpose(rows)
    for role, (family, sigma, eta_in, eta_out) in enumerate(owners):
        if sigma not in cache:
            # h = d sigma^-1, expressed as columns independently of source rows.
            cache[sigma] = compose(d_columns, transpose(sigma))
        h = cache[sigma]
        require(group.keys[role] == (family, transpose(h)), "physical owner composition")
        require(incoming[role] == (rows, apply(transpose(sigma), eta_in)), "entrance affine map")
        require(outgoing[role] == (d_columns, apply(h, eta_out)), "exit affine map")
    require(len(group.keys) == 704 and len(set(group.keys)) == 704, "complete distinct dispatch selectors")
    return sha(canonical((group.keys, sorted(incoming.items()), sorted(outgoing.items()))))


def transvection(normal):
    require(normal.bit_count() % 2 == 0, "orthogonal transvection normal")
    return tuple(unit ^ (normal if unit & normal else 0) for unit in IDENTITY)


def cover_controls(cover, rows, owner_rows):
    ordinals = []
    for value in (rows, owner_rows):
        label = cover.rank(value)
        require(cover.unrank(label) == value, "actual selected cover round trip")
        ordinals.append(dict(matrix_sha256=sha(canonical(value)), ordinal_sha256=sha(str(label).encode()),
                             ordinal_bits=label.bit_length()))
    return ordinals


def rejects(operation, reason):
    try:
        operation()
    except ValueError as error:
        require(reason in str(error), "wrong failure: " + str(error))
        return str(error)
    raise ValueError("mutation survived: " + reason)


def mutation_controls(raw, binding, expected, rows):
    source = raw[PREFIX + "selected_binding.py"].decode()
    first = next(i for i, event in enumerate(binding.events) if event["kind"] == "local_cover_sweep")
    staged = next(i for i, event in enumerate(binding.events) if event["kind"] == "local_cover_sweep" and
                  binding.calls[event["time"]]["stage"] == 2)
    cases = (
        ("reversed_owner_product", "multiply(g, o.sigma_columns)", "multiply(o.sigma_columns, g)", first,
         "physical owner composition"),
        ("transposed_owner_chart", "multiply(g, o.sigma_columns)", "multiply(g, transpose(o.sigma_columns))", first,
         "physical owner composition"),
        ("forward_instead_of_inverse_entrance", "mono(role, g, inverse=True)", "mono(role, g, inverse=False)", first,
         "entrance affine map"),
        ("inverse_instead_of_forward_exit", "mono(role, g)", "mono(role, g, inverse=True)", first,
         "exit affine map"),
        ("extra_cover_on_data_translation", "mono(role, self.identity, owner.entry)",
         "mono(role, self.identity, act(g, owner.entry))", staged, "entrance affine map"),
        ("data_phase_on_helper", "if owner.entry:\n                    mono(role, self.identity, owner.entry)",
         "if owner.entry or role >= 224:\n                    mono(role, self.identity, owner.entry or 1)", first,
         "entrance affine map"),
    )
    result = []
    try:
        for name, old, new, index, reason in cases:
            require(source.count(old) == 1, "unique frozen mutation site")
            changed = source.replace(old, new)
            module = execute("owner_view_mutant", changed.encode())
            mutant = object.__new__(module.SelectedBinding)
            mutant.__dict__.update(binding.__dict__)
            time = binding.events[index]["time"]
            failure = rejects(lambda: check_group(mutant, index, expected[time], rows, {}), reason)
            result.append(dict(name=name, sha256=sha(changed.encode()), detected=failure))
    finally:
        sys.modules.pop("owner_view_mutant", None)
    return result


def source_control():
    target = HERE / PREFIX / "selected_binding.py"
    original = Path.read_bytes
    def corrupt(path):
        return b"raise RuntimeError('counterfeit executed')\n" if path == target else original(path)
    with patch.object(Path, "read_bytes", corrupt):
        return rejects(authenticate, "Input changed: " + PREFIX + "selected_binding.py")


def exemplar(owners, rows):
    family, sigma, eta_in, eta_out = owners[0][224]
    require((family, eta_in, eta_out) == (13006, 0, 0), "first helper exemplar identity")
    sigma_rows = transpose(sigma)
    correct = compose(transpose(rows), sigma_rows)
    wrong = compose(sigma_rows, transpose(rows))
    require((apply(correct, 1), apply(wrong, 1)) == (602, 518), "noncommuting selected helper control")
    require(sigma != sigma_rows, "selected chart must distinguish inverse convention")
    return dict(call=0, role=224, family=family, port=14, route=[3, 4, 0],
                sigma_sha256=sha(canonical(sigma)), test_input=1, correct_owner_image=602,
                reversed_product_image=518, owner_rows=transpose(correct))


def build():
    raw, hashes = authenticate()
    corruption = source_control()
    with source_modules(raw) as modules:
        data = modules["selected_source"].load()
        binding = modules["selected_binding"].SelectedBinding(data)
        expected, inventory = owner_inventory(data, binding)
        rows = transpose(compose(transvection(15), transvection(30)))
        require(orthogonal(rows), "noncommuting selected cover")
        example = exemplar(expected, rows)
        actual_cover = binding.cover
        roundtrips = cover_controls(actual_cover, rows, example.pop("owner_rows"))
        binding.cover = MatrixCover(rows, actual_cover.size)
        digest, count, cache = hashlib.sha256(), 0, {}
        for index, event in enumerate(binding.events):
            if event["kind"] == "local_cover_sweep":
                value = check_group(binding, index, expected[event["time"]], rows, cache)
                digest.update(canonical((index, value)) + b"\n")
                count += 1
        require(count == 144, "all original local groups checked")
        controls = mutation_controls(raw, binding, expected, rows)
    return dict(status="PASS_COMPLEX_OWNER_VIEW_REFINEMENT", source_sha256=hashes,
                inventory=inventory, nonidentity_cover_sha256=sha(canonical(rows)),
                complete_groups=count, group_maps_sha256=digest.hexdigest(), helper_example=example,
                actual_ordinal_roundtrips=roundtrips, mutation_controls=controls,
                counterfeit_source_rejected=corruption,
                scope="Original R480/T16 local-cover owner/affine envelopes; symbolic cover labels for all144 groups; two actual ordinal round trips. No numerical O73 payload or T74 claim.")


def main():
    result = json.loads(json.dumps(build()))
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        require(not sys.argv[1:], "usage: verify.py [--emit]")
        require(result == json.loads((HERE / "RESULT.json").read_text()), "retained result mismatch")
        print(result["status"] + ": 101376 owner records, 144 exact affine envelopes and direction controls")


if __name__ == "__main__":
    main()
