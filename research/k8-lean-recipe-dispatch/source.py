#!/usr/bin/env python3
"""Bind complete selected k8 relabels to their serialized recipe descriptors.

Copyright 2026 Sagar Thakrar. Substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0

Authentication and unchanged PR2944 emission adapt our PR3357 source.py.
The retained translator/generator are Nick Petalas's PR2944 work; operator
conventions follow PR1964, PR1611 and the retained Lemma G/HPE lineage.
"""

from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
from types import ModuleType


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
MEMBER = "candidate/strict/global/base/providers/gauge44/"
LABEL = "research/k8-lean-label-instance/"
BINDING = "research/k8-hpe450-binding/RESULT.json"
FORWARD_SHA = "071ecdacc0bb3ac16046aad4119ed551a945cb0ed6c57002a548a3e2232503d8"
REQUIRED = {ARCHIVE, BINDING, LABEL + "translate.py", LABEL + "generate.py",
            LABEL + "RESULT.json", LABEL + "KERNEL.json"}
NAMES = ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz",
         "CLIFFORD-RECIPES.json", "RESIDUAL-ADAPTERS.json")
TAGS = ("pre", "post", "prew", "done")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def decoded(data):
    return json.loads(data, object_pairs_hook=unique)


def nat(value, bound, name):
    require(type(value) is int and 0 <= value < bound, name)
    return value


def authenticate(root=ROOT):
    """Return the authenticated bytes that all subsequent consumers read."""
    root = Path(root).resolve()
    rows = decoded((HERE / "SOURCES.json").read_bytes())["files"]
    result = {}
    for row in rows:
        if row["usage"] != "input":
            continue
        name = row["path"]
        path = (root / name).resolve()
        require(path.is_relative_to(root) and name not in result, "source inventory")
        data = path.read_bytes()
        require(digest(data) == row["sha256"], "Input changed: " + name)
        result[name] = data
    require(REQUIRED <= result.keys(), "missing required source input")
    return result


def retained_modules(inputs):
    translator = ModuleType("retained_k8_translate")
    translator.__file__ = LABEL + "translate.py"
    exec(compile(inputs[translator.__file__], translator.__file__, "exec"), translator.__dict__)
    generator = ModuleType("retained_k8_generate")
    generator.__file__ = LABEL + "generate.py"
    previous = sys.modules.get("translate")
    sys.modules["translate"] = translator
    try:
        exec(compile(inputs[generator.__file__], generator.__file__, "exec"), generator.__dict__)
    finally:
        if previous is None:
            del sys.modules["translate"]
        else:
            sys.modules["translate"] = previous
    return translator, generator


def archive_members(inputs):
    """Read four exact members without extracting or searching by basename."""
    with tarfile.open(fileobj=io.BytesIO(inputs[ARCHIVE]), mode="r:gz") as archive:
        members = archive.getmembers()
        result = {}
        for name in NAMES:
            full = MEMBER + name
            require(sum(m.name == full for m in members) == 1, "archive member multiplicity")
            member = archive.getmember(full)
            require(member.isfile(), "archive member type")
            data = archive.extractfile(member).read()
            result[name] = gzip.decompress(data) if name.endswith(".gz") else data
    return result


def translation(inputs, payloads):
    canonical = decoded(payloads[NAMES[0]])
    programs = decoded(payloads[NAMES[1]])
    binding = decoded(inputs[BINDING])
    require(digest(payloads[NAMES[0]]) == binding["canonical_content_sha256"],
            "canonical word binding")
    require(set(programs) == {"forward", "backward"}, "orientation inventory")
    forward = programs["forward"]
    require(digest(encoded(forward)) == binding["program_sha256"]["forward"] == FORWARD_SHA,
            "forward stream binding")
    require(len(forward) == 24767, "complete serialized length")
    translator, generator = retained_modules(inputs)
    start, events, indices = translator.translate(canonical, forward)
    prior = decoded(inputs[LABEL + "RESULT.json"])["orientations"]["forward"]
    require(digest(encoded([start, events])) == prior["translation_sha256"],
            "translation binding")
    require(digest(encoded(indices)) == prior["source_indices_sha256"], "source index binding")
    counts = dict(sorted(Counter(event[0] for event in events).items()))
    require(counts == prior["constructors"] and len(events) == 24757, "constructor inventory")
    receipt = {"forward_sha256": FORWARD_SHA, "serialized_events": len(forward),
               "semantic_events": len(events), "constructors": counts,
               "translation_sha256": prior["translation_sha256"],
               "source_indices_sha256": prior["source_indices_sha256"],
               "member_payload_sha256": {name: digest(data) for name, data in payloads.items()}}
    return canonical, forward, start, events, indices, receipt, generator


def monomial(record):
    fields = {"quadratic_rows", "linear_Z4", "matrix_rows", "offset", "phase"}
    require(type(record) is dict and set(record) == fields, "monomial fields")
    for field, bound in (("quadratic_rows", 512), ("linear_Z4", 4), ("matrix_rows", 512)):
        require(type(record[field]) is list and len(record[field]) == 9, "monomial dimensions")
        for value in record[field]:
            nat(value, bound, "monomial entry")
    nat(record["offset"], 512, "monomial offset")
    nat(record["phase"], 4, "monomial phase")
    return encoded(record)


def monomial_inventory(recipes, residual):
    records = []
    for child in recipes["children"]:
        records.extend([child["left"], child["right"]])
    records.extend(row["left"] for row in recipes["endpoint_adapters"])
    for row in residual["recipes"].values():
        records.extend([row["left"], row["right"]])
    values = sorted({monomial(record) for record in records})
    return [decoded(value) for value in values], {value: index for index, value in enumerate(values)}


def child_tables(recipes, ids):
    require(set(recipes) == {"children", "endpoint_adapters"}, "Clifford table fields")
    require(len(recipes["children"]) == 2896, "child inventory")
    children, index = [], {}
    for child_id, row in enumerate(recipes["children"]):
        require(set(row) == {"old", "new", "rank", "left", "right"}, "child fields")
        old, new = nat(row["old"], 1004, "old frame"), nat(row["new"], 1004, "new frame")
        rank = nat(row["rank"], 10, "child rank")
        key = f"{old}:{new}"
        require(old != new and rank > 0 and key not in index, "child key")
        index[key] = child_id
        children.append({"id": child_id, "old": old, "new": new, "rank": rank,
                         "left": ids[monomial(row["left"])],
                         "right": ids[monomial(row["right"])]})
    return children, index


def endpoint_tables(canonical, recipes, ids):
    result = {"source": [None] * 112, "target": [None] * 112}
    require(len(recipes["endpoint_adapters"]) == 224, "endpoint inventory")
    for row in recipes["endpoint_adapters"]:
        require(set(row) == {"frame", "left", "port", "rank", "right", "role"},
                "endpoint fields")
        role, port = row["role"], nat(row["port"], 112, "endpoint port")
        require(role in result and row["rank"] == 0 and row["right"] is None,
                "endpoint role")
        frame = canonical["start"][port] if role == "source" else canonical["final"][112 + port]
        require(row["frame"] == frame and result[role][port] is None, "endpoint frame/key")
        result[role][port] = {"frame": frame, "mono": ids[monomial(row["left"])]}
    require(all(value is not None for rows in result.values() for value in rows), "endpoint coverage")
    return result


def residual_tables(canonical, residual, ids):
    require(set(residual) == {"recipes", "status"} and
            residual["status"] == "RESIDUAL_ADAPTER_RECIPES", "residual fields")
    require(len(residual["recipes"]) == 36, "residual inventory")
    result = {}
    for key, row in residual["recipes"].items():
        entrance, terminal = row["frame"], row.get("terminal", 1)
        nat(entrance, 1004, "residual entrance")
        nat(terminal, 1004, "residual terminal")
        require(key == residual_key(entrance, terminal), "residual key")
        require(row["vectors"] == canonical["frames"][entrance] and
                row["entrance_rank"] == len(row["vectors"]), "residual entrance frame")
        require(row.get("terminal_vectors", canonical["frames"][1]) == canonical["frames"][terminal],
                "residual terminal frame")
        require(row["rank"] == len(canonical["frames"][terminal]) - row["entrance_rank"],
                "residual rank")
        result[key] = {"entrance": entrance, "terminal": terminal, "rank": row["rank"],
                       "left": ids[monomial(row["left"])], "right": ids[monomial(row["right"])]}
    return result


def residual_key(entrance, terminal):
    return str(entrance) if terminal == 1 else f"{entrance}:{terminal}"


def make_tables(canonical, recipes, residual):
    monos, ids = monomial_inventory(recipes, residual)
    children, index = child_tables(recipes, ids)
    endpoints = endpoint_tables(canonical, recipes, ids)
    return {"monomials": monos, "children": children, "child_index": index,
            "source": endpoints["source"], "target": endpoints["target"],
            "residual": residual_tables(canonical, residual, ids),
            "start": canonical["start"], "final": canonical["final"]}


def child_recipe(tables, old, new, rank=None):
    nat(old, 1004, "child old frame")
    nat(new, 1004, "child new frame")
    if rank is not None:
        nat(rank, 10, "child event rank")
    key = f"{old}:{new}"
    require(key in tables["child_index"], "missing child recipe")
    row = tables["children"][tables["child_index"][key]]
    require(rank is None or rank == row["rank"], "child rank mismatch")
    return ["child", row["id"], row["rank"], row["left"], row["right"]]


def raw_descriptor(event, canonical, tables):
    """Read recipe choice from source opcodes, without decoding any Nat label."""
    kind = event[0]
    if kind in ("phase", "scalar"):
        return None
    if kind in ("climb", "center"):
        require(len(event) == (6 if kind == "climb" else 5), "raw transport arity")
        register = nat(event[2], 704, "climb register") if kind == "climb" else (
            704 + nat(event[1], 8, "centre register"))
        old, new, rank = event[-3:]
        nat(rank, 10, "raw child rank")
        return register, child_recipe(tables, old, new, rank)
    if kind == "adapter":
        require(len(event) == 4, "raw adapter arity")
        _, direction, register, frame = event
        nat(register, 704, "adapter register")
        if direction == "old_to_new":
            if register < 112:
                require(frame == canonical["start"][register], "source adapter frame")
                return register, ["source", tables["source"][register]["mono"]]
            require(frame == 0, "identity entry frame")
            return register, ["identity"]
        require(direction == "new_to_old", "raw adapter direction")
        if 112 <= register < 224:
            require(frame == canonical["final"][register], "target adapter frame")
            return register, ["target", tables["target"][register - 112]["mono"]]
        require(frame == 1, "identity exit frame")
        return register, ["identity"]
    require(kind == "residual_adapter" and len(event) in (4, 5), "raw relabel kind")
    _, side, register, entrance = event[:4]
    nat(register, 704, "wrapper register")
    terminal = canonical["final"][register]
    require(register >= 224 and entrance == canonical["start"][register] and
            event[4:] == ([terminal] if terminal != 1 else []), "raw wrapper endpoint")
    key = residual_key(entrance, terminal)
    require(key in tables["residual"] and side in ("pre", "post"), "raw wrapper key/side")
    field = "right" if side == "pre" else "left"
    return register, [side, tables["residual"][key][field]]


def decode_label(value, stride=712):
    require(type(stride) is int and stride > 0, "label stride")
    nat(value, 1004 * (1 + 4 * stride), "label range")
    frame, code = value % 1004, value // 1004
    if code == 0:
        return "plain", None, frame
    tag, owner = divmod(code - 1, stride)
    require(tag < 4 and owner < 704, "label tag/owner")
    return TAGS[tag], owner, frame


def dispatch(old_label, new_label, tables, stride=712):
    """Select a recipe from labels and canonical tables, without raw events."""
    a, owner_a, old = decode_label(old_label, stride)
    b, owner_b, new = decode_label(new_label, stride)
    if a == b == "plain":
        return ["identity"] if old == new else child_recipe(tables, old, new)
    require(old == new, "tag transition frame")
    if a == "pre" and b == "plain":
        require(owner_a < 112 and tables["source"][owner_a]["frame"] == old,
                "source dispatch owner/frame")
        return ["source", tables["source"][owner_a]["mono"]]
    if a == "plain" and b == "post":
        require(112 <= owner_b < 224 and tables["target"][owner_b - 112]["frame"] == old,
                "target dispatch owner/frame")
        return ["target", tables["target"][owner_b - 112]["mono"]]
    require((a == "prew" and b == "plain") or (a == "plain" and b == "done"),
            "unsupported tag transition")
    owner = owner_a if a == "prew" else owner_b
    require(owner >= 224, "wrapper dispatch owner")
    entrance, terminal = tables["start"][owner], tables["final"][owner]
    side = "pre" if a == "prew" else "post"
    require(old == (entrance if side == "pre" else terminal), "wrapper dispatch frame")
    key = residual_key(entrance, terminal)
    require(key in tables["residual"], "wrapper dispatch key")
    return [side, tables["residual"][key]["right" if side == "pre" else "left"]]


def occurrences(forward, canonical, tables, events, indices):
    expected_indices = [i for i, event in enumerate(forward) if event[0] != "phase"]
    require(indices == expected_indices and len(events) == len(indices), "complete source index order")
    result = []
    for semantic, (event, source_index) in enumerate(zip(events, indices)):
        raw = raw_descriptor(forward[source_index], canonical, tables)
        require((raw is not None) == (event[0] == "relabel"), "relabel occurrence coverage")
        if raw is None:
            continue
        register, recipe = raw
        require(register == event[1], "raw relabel register")
        require(dispatch(event[2], event[3], tables) == recipe, "raw/label dispatch disagreement")
        result.append([source_index, semantic, register, event[2], event[3], recipe])
    return result


def load(root=ROOT):
    inputs = authenticate(root)
    payloads = archive_members(inputs)
    canonical, forward, start, events, indices, receipt, _ = translation(inputs, payloads)
    tables = make_tables(canonical, decoded(payloads[NAMES[2]]), decoded(payloads[NAMES[3]]))
    rows = occurrences(forward, canonical, tables, events, indices)
    used = sorted({row[5][1] for row in rows if row[5][0] == "child"})
    counts = dict(sorted(Counter(row[5][0] for row in rows).items()))
    require(len(rows) == 5064 and len(used) == 2888, "dispatch inventory")
    require(counts == {"child": 3494, "identity": 866, "post": 240, "pre": 240,
                       "source": 112, "target": 112}, "recipe-kind inventory")
    tables["used_child_ids"] = used
    receipt.update({"schema_version": 1, "status": "PASS_K8_RECIPE_DISPATCH_SOURCE",
                    "label_frame_radix": 1004, "label_owner_stride": 712,
                    "typed_register_capacity": 1024, "relabel_occurrences": len(rows),
                    "used_child_identities": len(used), "recipe_kinds": counts,
                    "tables_sha256": digest(encoded(tables)),
                    "occurrences_sha256": digest(encoded(rows))})
    return {"canonical": canonical, "forward": forward, "events": events,
            "start": start, "indices": indices, "tables": tables,
            "occurrences": rows, "receipt": receipt}


def build(root=ROOT):
    data = load(root)
    return {"receipt": data["receipt"], "tables": data["tables"],
            "occurrences": data["occurrences"]}


def emit_existing(out, root=ROOT):
    """Emit the same fourteen PR2944 Forward sources, checked byte for byte."""
    inputs = authenticate(root)
    _, _, start, events, _, receipt, generator = translation(inputs, archive_members(inputs))
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    paths = generator.emit(out, "Forward", start, events)
    expected = decoded(inputs[LABEL + "KERNEL.json"])["generated_sha256"]
    actual = {path.name: digest(path.read_bytes()) for path in paths}
    require(actual == {name: sha for name, sha in expected.items() if name.startswith("Forward")},
            "retained generated source binding")
    return paths, dict(receipt, generated_sha256=actual)


if __name__ == "__main__":
    require(build() == decoded((HERE / "SOURCE-DISPATCH.json").read_bytes()),
            "SOURCE-DISPATCH.json mismatch")
    print("PASS_K8_RECIPE_DISPATCH_SOURCE")
