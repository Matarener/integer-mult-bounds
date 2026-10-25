#!/usr/bin/env python3
"""Emit balanced recipe tables and checks against unchanged PR2944 blocks.

Copyright 2026 Sagar Thakrar. Substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""

from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import source  # noqa: E402


def tree(items, render=str):
    """A balanced search tree whose keys occur once, in increasing order."""
    keys = [key for key, _ in items]
    source.require(keys == sorted(keys) and len(set(keys)) == len(keys),
                   "lookup key ordering/uniqueness")
    if not items:
        return ".nil"
    middle = len(items) // 2
    key, value = items[middle]
    return f"(.node {key} {render(value)} {tree(items[:middle], render)} " + \
        f"{tree(items[middle + 1:], render)})"


def child_literal(row):
    return "⟨" + ", ".join(str(row[key]) for key in ("id", "rank", "left", "right")) + "⟩"


def recipe_literal(recipe):
    if recipe[0] == "child":
        source.require(len(recipe) == 5, "child descriptor shape")
        return "(.child ⟨" + ", ".join(map(str, recipe[1:])) + "⟩)"
    source.require(recipe[0] in ("source", "target", "pre", "post", "identity"),
                   "recipe constructor")
    if recipe[0] == "identity":
        source.require(len(recipe) == 1, "identity descriptor shape")
        return ".identity"
    source.require(len(recipe) == 2, "monomial descriptor shape")
    return f"(.{recipe[0]} {recipe[1]})"


def table_items(tables):
    used = set(tables["used_child_ids"])
    result = {"children": sorted((row["old"] * 1004 + row["new"], row)
                                  for row in tables["children"] if row["id"] in used)}
    result["source"] = [(i, row["mono"]) for i, row in enumerate(tables["source"])]
    result["target"] = [(112 + i, row["mono"]) for i, row in enumerate(tables["target"])]
    result["pre"], result["post"] = [], []
    for owner in range(224, 704):
        entrance, terminal = tables["start"][owner], tables["final"][owner]
        if entrance == 0 and terminal == 1:
            continue
        row = tables["residual"][source.residual_key(entrance, terminal)]
        result["pre"].append((owner, row["right"]))
        result["post"].append((owner, row["left"]))
    source.require({key: len(value) for key, value in result.items()} ==
                   {"children": 2888, "source": 112, "target": 112, "pre": 240, "post": 240},
                   "Lean table inventory")
    return result


def tables_module(tables):
    items = table_items(tables)
    lines = ["import K8RecipeDispatch", "import ForwardResult", "",
             "namespace K8.RecipeBinding", "open K8RecipeDispatch",
             "set_option maxRecDepth 10000", "set_option maxHeartbeats 0", "",
             "def tables : Tables := {"]
    for field, values in items.items():
        lines.append(f"  {field} := {tree(values, child_literal if field == 'children' else str)}")
    lines.extend(["}", "", "end K8.RecipeBinding", ""])
    return "\n".join(lines)


def raw_literal(row):
    _, _, register, old, new, recipe = row
    return f"({register}, {old}, {new}, {recipe_literal(recipe)})"


def checks_module(group, blocks, occurrences):
    previous = f"RecipeChecks{group - 1:02}" if group else "RecipeTables"
    lines = [f"import {previous}", "", "namespace K8.RecipeBinding",
             "open K8RecipeDispatch", "set_option maxRecDepth 10000",
             "set_option maxHeartbeats 0", ""]
    for block in range(group * 8, min((group + 1) * 8, blocks)):
        rows = [row for row in occurrences if row[1] // 256 == block]
        lines.append(f"def raw{block} : List Raw := [" +
                     ",\n".join(raw_literal(row) for row in rows) + "]")
        lines.append(f"theorem check{block} : checkBlock tables K8.Forward.block{block} " +
                     f"raw{block} = true := by decide +kernel")
    lines.extend(["", "end K8.RecipeBinding", ""])
    return "\n".join(lines)


def emit(out):
    """Return ordered new source paths and receipt; no Lean compiler is invoked."""
    data = source.load()
    artifact = {key: data[key] for key in ("receipt", "tables", "occurrences")}
    source.require(artifact == source.decoded((HERE / "SOURCE-DISPATCH.json").read_bytes()),
                   "SOURCE-DISPATCH.json mismatch")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    blocks = (len(data["events"]) + 255) // 256
    source.require(blocks == 97, "retained block inventory")
    modules = {"RecipeTables.lean": tables_module(data["tables"])}
    for group in range((blocks + 7) // 8):
        modules[f"RecipeChecks{group:02}.lean"] = checks_module(group, blocks, data["occurrences"])
    paths = []
    for name, content in modules.items():
        path = out / name
        path.write_text(content)
        paths.append(path)
    receipt = {"source_dispatch_sha256": source.digest(source.encoded(artifact)),
               "generated_sha256": {path.name: source.digest(path.read_bytes()) for path in paths},
               "blocks": blocks, "relabel_occurrences": len(data["occurrences"]),
               "used_child_identities": len(data["tables"]["used_child_ids"])}
    return paths, receipt
