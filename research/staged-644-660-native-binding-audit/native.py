# SPDX-License-Identifier: Apache-2.0
"""Bind the emitted 644/660 entering wrappers, then check them with a separate exact kernel.

The retained t74-native-fast bw_transport.py/bw_emit.py and the PR458-lineage
adapter convention are producers, not independent evidence. The separately
implemented Gaussian kernel is Sagar Thakrar's retained verifier; neither is new
here. Adapted from research/rank7-group-d-native-widths-audit/native.py (Wentao
Li), itself adapted from the group-A/B/C audits, to PR3605's ordinary FULL-terminal
helpers 644/660. Unlike the restored group helpers, these have no private buffer:
they are wrapped by one residual pair and leave through one ordinary exit adapter.
The consumer words that retime the 644/660 releases (PR3642/PR3653 RETIMED, PR3682
DELAYED) go through the same binding, with PR3605's STAGED words as the control.
"""

import copy
import os
import subprocess
import sys

from common import (COMPILER, CONSUMERS, CONTAINED_LINE, DONORS, ENGINE, ENTRANCE, FULL,
                    HELPERS, KERNEL, PARENT_ENTRANCE, PROVIDERS, WRONG_ENTRANCE,
                    consumer_name, decode, digest, encoded, module, parent_name,
                    recorded_receipts, reject, require, staged_name)


def bind_program_receipts(programs, checks):
    require(set(programs) == set(checks) == {"forward", "backward"},
            "both emitted orientations")
    for orientation, events in programs.items():
        row = checks[orientation]
        require(row["events"] == len(events) and
                row["sha256"] == digest(encoded(events)[:-1]),
                "event stream digest in emitted receipt")


def generate(blobs, raw_word, work):
    """Run the unchanged producer on authenticated bytes in a fresh directory."""
    work.mkdir(exist_ok=True)
    tools = work / "tools"
    tools.mkdir()
    for name in ("bw_transport.py", "bw_emit.py"):
        (tools / name).write_bytes(blobs[ENGINE + name])
    word = work / "WORD.json.gz"
    word.write_bytes(raw_word)
    output = work / "local"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONOPTIMIZE", None)
    for script, args in (("bw_transport.py", [word, output]), ("bw_emit.py", [output])):
        run = subprocess.run([sys.executable, "-I", "-B", str(tools / script),
                              *map(str, args)], env=env, capture_output=True,
                             text=True, timeout=120, check=False)
        require(run.returncode == 0, script + ": " + run.stderr[-2000:])
    # bw_emit.py writes this receipt with write_text (CRLF on Windows); digest the
    # LF form so the receipt is platform-independent and matches recorded runs.
    checks = (output / "LOCAL-CHECKS.json").read_bytes().replace(b"\r\n", b"\n")
    canonical = decode((output / "CANONICAL-WORD.json.gz").read_bytes(), True)
    programs = decode((output / "LOCAL-PROGRAMS.json.gz").read_bytes(), True)
    bind_program_receipts(programs, decode(checks))
    return canonical, programs, digest(checks)


def adapter_file(compiler, canonical):
    """Reconstruct the serialized residual-adapter file by the PR458-lineage convention."""
    frames = canonical["frames"]
    pairs = {(canonical["start"][r], canonical["final"][r])
             for r in range(224, 632)}
    recipes, warps = {}, {}
    for e, u in sorted(pairs):
        if u == 1 and e == 0:
            continue
        entrance, terminal = frames[e], frames[u]
        op = compiler.canonical_frame(9, tuple(entrance)).adjoint().then(
            compiler.canonical_frame(9, tuple(terminal)))
        rec, _ = compiler.lower_child(op)
        row = dict(frame=e, vectors=entrance, entrance_rank=len(entrance),
                   rank=rec["rank"], left=rec["left"], right=rec["right"])
        key = str(e)
        if u != 1:
            row.update(terminal=u, terminal_vectors=terminal, terminal_rank=len(terminal))
            key = f"{e}:{u}"
        recipes[key] = row
    for w in canonical["warps"]:
        columns = tuple(w["G_columns"])
        matrix = compiler.transpose(columns, 9)
        inverse_columns = compiler.transpose(compiler.inv(matrix, 9), 9)
        q = tuple((1 << i) ^ sum(compiler.parity(a & b) << j
                  for j, b in enumerate(inverse_columns))
                  for i, a in enumerate(inverse_columns))
        op = compiler.perm(9, matrix).then(compiler.diag(9, q))
        _, rec = compiler.monomial(op)
        warps[str(w["op"])] = dict(op=w["op"], from_frame=w["from_frame"],
            to_frame=w["to_frame"], G_columns=w["G_columns"], K=rec)
    return decode(encoded(dict(status="RESIDUAL_ADAPTER_RECIPES", recipes=recipes, warps=warps)))


def conjugate(circuit):
    out = []
    for gate in circuit:
        if gate[0] == "C":
            out.append(("C", gate[1], -gate[2]))
        elif gate[0] == "D":
            out.append(("D", gate[1], [-a % 4 for a in gate[2]]))
        elif gate[0] == "PH":
            out.append(("PH", -gate[1] % 4))
        else:
            require(gate[0] in ("P", "X"), "real monomial primitive")
            out.append(gate)
    return out


def check_recipe(kernel, rec, entrance, terminal):
    width = len(terminal) - len(entrance)
    require(type(rec["rank"]) is int and rec["rank"] == width, "entrance-relative width")
    require(kernel.well_formed(rec["left"]) and
            (rec["right"] is None or kernel.well_formed(rec["right"])),
            "serialized monomials")
    left = kernel.monomial(rec["left"])
    right = [] if rec["right"] is None else kernel.monomial(rec["right"])
    reference = kernel.adjoint(kernel.canonical_frame(entrance)) + kernel.canonical_frame(terminal)
    candidate = right + kernel.fourier(width) + left
    wrapped = kernel.adjoint(right) + reference + kernel.adjoint(left)
    require(kernel.same_operator(candidate, reference), "phase-exact all-column residual")
    require(kernel.same_operator(wrapped, kernel.fourier(width)), "wrapped coordinate factor")
    require(kernel.same_operator(conjugate(wrapped), kernel.fourier(width, -1)),
            "inverse-transpose coordinate factor")
    return {"rank": width, "columns": 512, "orientations": 2,
            "spectator_axes": 9 - width, "recipe": rec}


def source_events(word, helper):
    """Reconstruct all direct scalar clocks and climbs of one ordinary helper from its word."""
    require(str(helper) not in word["helper_final"], "ordinary FULL-terminal helper")
    touched = {helper}
    for section in ("precondition", "compensation", "cut"):
        require(all(not (touched & set(g[1:3] if g[0] == "add" else g[1:2]))
                    for g in word[section]), "no uncovered direct source section")
    require(all(not (touched & {c["source"], c["target"]})
                for c in word["initial_corrections"]), "no uncovered direct correction")
    require(all(w[1] != helper for w in word["warps"]), "no direct lender warp")
    scalars, climbs = [], []
    current = word["start_extra"].get(str(helper), [])
    for section, phase in (("A", "A"), ("B", "B"), ("restore", "cleanup_tail")):
        clock = 0
        for gate in word[section]:
            regs = gate[1:3] if gate[0] == "add" else gate[1:2]
            if touched & set(regs):
                require(gate[0] in ("add", "scale"), "no direct source warp")
                if current != gate[-1]:
                    climbs.append([phase, clock, current, gate[-1], len(gate[-1]) - len(current)])
                    current = gate[-1]
                scalars.append([phase, clock, gate[:-1], gate[-1]])
            clock += gate[0] != "warp"
    if current != FULL:
        # The emitter's final phase lifts every ordinary helper to FULL before cleanup.
        climbs.append(["final", 0, current, FULL, len(FULL) - len(current)])
    clock = 0
    for gate in word["cleanup"]:
        regs = gate[1:3] if gate[0] == "add" else gate[1:2]
        if touched & set(regs):
            require(gate[0] in ("add", "scale") and gate[-1] == FULL, "FULL-frame cleanup")
            scalars.append(["full_frame_cleanup", clock, gate[:-1], gate[-1]])
        clock += gate[0] != "warp"
    return scalars, climbs


def scalar_original(operation, kept, backward):
    require(operation[0] in ("add", "scale", "copy", "clear"), "known emitted scalar")
    count = 2 if operation[0] in ("add", "copy") else 1
    regs = []
    for kind, r in operation[1:1 + count]:
        require(kind in ("L", "Z", "C"), "register namespace")
        regs.append(-1 if kind == "C" else kept[r] + (704 if kind == "Z" else 0))
    row = [operation[0], *regs, *operation[1 + count:]]
    if backward and row[0] == "add":
        row[1], row[2], row[3] = row[2], row[1], -row[3]
    elif backward and row[0] == "scale":
        row[2], row[3] = row[3], row[2]
    return row, regs


def emitted_binding(word, canonical, stream, helper, backward=False):
    """Entrance wrapper pair, climbs, one FULL exit adapter and direct scalar clocks."""
    kept = [r for r in range(704) if r not in word["removed"]]
    require(canonical["helper_origin"] == kept[224:], "original-to-compact binding")
    r = kept.index(helper)
    e, u = canonical["start"][r], canonical["final"][r]
    entrance = word["start_extra"].get(str(helper), [])
    require(entrance and canonical["frames"][e] == entrance and u == 1 and
            canonical["frames"][u] == FULL, "literal entrance/FULL pair")
    require(r not in canonical["zero_buffers"], "ordinary helper has no private buffer")
    wrappers, adapters, climbs, scalars, climb_clocks, scalar_indices = [], [], [], [], [], []
    phase, clock = None, 0
    for i, event in enumerate(stream):
        if event[0] == "phase":
            phase, clock = event[1], 0
        elif event[0] == "residual_adapter" and event[2] == r:
            require(event[3:] == [e], "emitted wrapper entrance without terminal")
            wrappers.append([i, event[1], phase])
        elif event[0] == "adapter" and event[2] == r:
            adapters.append([i, event[1], event[3], phase])
        elif event[0] == "zero_buffer":
            require(event[2] != r, "no private lifetime for an ordinary helper")
        elif event[0] == "climb" and event[2] == r:
            old, new = (canonical["frames"][f] for f in event[3:5])
            require(event[5] == len(new) - len(old) > 0, "emitted climb rank")
            climbs.append({"index": i, "old": old, "new": new, "rank": event[5]})
            climb_clocks.append([phase, clock, old, new, event[5]])
        elif event[0] == "scalar":
            row, regs = scalar_original(event[1], kept, backward)
            require(["Z", r] not in event[1][1:3], "no private register use")
            if helper in regs:
                scalars.append([phase, clock, row, canonical["frames"][event[2]]])
                scalar_indices.append(i)
            clock += 1
        elif event[0] == "warp":
            require(event[1] not in (["L", r], ["Z", r]), "no unaccounted direct warp")
    expected_scalars, expected_climbs = source_events(word, helper)
    require(scalars == expected_scalars and climb_clocks == expected_climbs,
            "source-to-emission direct scalar/climb clocks")
    require([x[1:] for x in wrappers] == [["pre", "entry_adapters"], ["post", "full_frame_cleanup"]],
            "two residual wrappers")
    require([x[1:] for x in adapters] == [["new_to_old", 1, "exit_adapters"]],
            "one ordinary FULL exit adapter and no entry adapter")
    cleanup = [i for i, s in zip(scalar_indices, scalars) if s[0] == "full_frame_cleanup"]
    require(cleanup and wrappers[0][0] < climbs[0]["index"] and
            climbs[-1]["index"] < adapters[0][0] < min(cleanup) and
            max(scalar_indices) < wrappers[1][0], "wrapper, climbs, exit, cleanup order")
    current = entrance
    for climb in climbs:
        require(climb["old"] == current, "complete direct climb chain")
        current = climb["new"]
    require(current == FULL and sum(c["rank"] for c in climbs) == len(FULL) - len(entrance),
            "complete entrance-relative path")
    return {"compact_helper": r, "recipe_key": str(e), "entrance": entrance,
            "terminal": FULL, "wrappers": [x[:2] for x in wrappers],
            "exit_adapter": adapters[0][:3], "climbs": climbs,
            "direct_scalar_count": len(scalars),
            "cleanup_scalar_count": len(cleanup),
            "direct_scalar_sha256": digest(encoded(scalars))}


def check_climb(compiler, kernel, old, new, climb_recipes):
    """Lower one climb with the source compiler and check it with the separate kernel."""
    identity = encoded([old, new]).decode().strip()
    if identity not in climb_recipes:
        op = compiler.canonical_frame(9, tuple(old)).adjoint().then(
            compiler.canonical_frame(9, tuple(new)))
        candidate, _ = compiler.lower_child(op)
        climb_recipes[identity] = check_recipe(kernel, decode(encoded(candidate)), old, new)["rank"]
    return identity


def climb_chains(word, canonical, stream):
    """Original helper id -> its emitted [old, new, rank] climbs in stream order."""
    kept = [r for r in range(704) if r not in word["removed"]]
    chains = {}
    for event in stream:
        if event[0] == "climb":
            old, new = (canonical["frames"][f] for f in event[3:5])
            chains.setdefault(kept[event[2]], []).append([old, new, event[5]])
    return chains


def recipe_classes(adapters):
    """Serialized residual recipes by literal entrance and terminal vectors."""
    return {encoded([row["vectors"], row.get("terminal_vectors", FULL)])
            for row in adapters["recipes"].values()}


def pair_inventory(canonical, word):
    """Original helper id -> literal entrance/terminal vectors for every compact helper."""
    kept = [r for r in range(704) if r not in word["removed"]]
    frames = canonical["frames"]
    return {kept[r]: (frames[canonical["start"][r]], frames[canonical["final"][r]])
            for r in range(224, 632)}


def provider(blobs, tag, work, compiler, kernel, climb_recipes):
    raw = blobs[staged_name(tag)]
    word = decode(raw, True)
    canonical, programs, checks_sha = generate(blobs, raw, work / "staged")
    adapters = adapter_file(compiler, canonical)
    bindings, residuals = {}, {}
    for h in HELPERS:
        bindings[str(h)] = {orientation: emitted_binding(word, canonical, stream, h,
                                                         orientation == "backward")
                            for orientation, stream in programs.items()}
        forward, backward = bindings[str(h)]["forward"], bindings[str(h)]["backward"]
        require(forward["entrance"] == ENTRANCE and
                [c["rank"] for c in forward["climbs"]] == [c["rank"] for c in backward["climbs"]],
                "staged entrance in both orientations")
        key = forward["recipe_key"]
        row = adapters["recipes"][key]
        require(row["vectors"] == ENTRANCE and "terminal" not in row, "serialized FULL recipe row")
        if key not in residuals:
            residuals[key] = check_recipe(kernel, row, ENTRANCE, FULL)
        for climb in forward["climbs"]:
            check_climb(compiler, kernel, climb["old"], climb["new"], climb_recipes)
    require(len(residuals) == 1, "one shared entering residual class")

    # Single-change control: the parent PR3133 word through the same producer.
    raw_parent = blobs[parent_name(tag)]
    parent = decode(raw_parent, True)
    canonical_parent, programs_parent, parent_checks_sha = generate(blobs, raw_parent, work / "parent")
    parent_bindings = {}
    for h in HELPERS:
        rows = {orientation: emitted_binding(parent, canonical_parent, stream, h,
                                             orientation == "backward")
                for orientation, stream in programs_parent.items()}
        require(rows["forward"]["entrance"] == PARENT_ENTRANCE, "parent entrance span(30)")
        old_climbs, new_climbs = rows["forward"]["climbs"], bindings[str(h)]["forward"]["climbs"]
        # Every climb ends at the same frame; only the first climb's start differs.
        require(len(old_climbs) == len(new_climbs) and
                [c["new"] for c in old_climbs] == [c["new"] for c in new_climbs] and
                [c["old"] for c in old_climbs[1:]] == [c["old"] for c in new_climbs[1:]],
                "parent and staged climb frames")
        parent_bindings[str(h)] = {"entrance": PARENT_ENTRANCE,
                                   "climb_ranks": [c["rank"] for c in old_climbs],
                                   "direct_scalar_count": rows["forward"]["direct_scalar_count"]}
    op = compiler.canonical_frame(9, tuple(PARENT_ENTRANCE)).adjoint().then(
        compiler.canonical_frame(9, tuple(FULL)))
    parent_recipe, _ = compiler.lower_child(op)
    parent_recipe = decode(encoded(parent_recipe))
    parent_check = check_recipe(kernel, parent_recipe, PARENT_ENTRANCE, FULL)
    old, new = pair_inventory(canonical_parent, parent), pair_inventory(canonical, word)
    require(set(old) == set(new), "same helper names")
    changed = sorted(h for h in old if old[h] != new[h])
    require(changed == list(HELPERS) and
            all(old[h] == (PARENT_ENTRANCE, FULL) and new[h] == (ENTRANCE, FULL) for h in changed),
            "only the two staged entrances change")
    classes_old, classes_new = set(map(str, old.values())), set(map(str, new.values()))
    require(classes_new - classes_old == {str((ENTRANCE, FULL))}, "one new entrance/terminal class")
    # The pair classes include the unwrapped cold class ([], FULL), which has no recipe.
    parent_adapters = adapter_file(compiler, canonical_parent)
    recipes_old, recipes_new = recipe_classes(parent_adapters), recipe_classes(adapters)
    require(recipes_new - recipes_old == {encoded([ENTRANCE, FULL])} and
            len(recipes_new) == len(recipes_old) + 1, "one new serialized residual recipe")

    key = bindings["644"]["forward"]["recipe_key"]
    rec = adapters["recipes"][key]
    controls = {}
    controls["omitted_entrance"] = reject(lambda: check_recipe(kernel, rec, [], FULL), "entrance")
    controls["contained_line"] = reject(lambda: check_recipe(kernel, rec, CONTAINED_LINE, FULL),
                                        "contained line")
    controls["old_entrance"] = reject(lambda: check_recipe(kernel, rec, PARENT_ENTRANCE, FULL),
                                      "parent entrance")
    bad = copy.deepcopy(rec); bad["left"]["phase"] = (bad["left"]["phase"] + 1) % 4
    controls["phase"] = reject(lambda: check_recipe(kernel, bad, ENTRANCE, FULL), "phase")
    require(parent_recipe["right"] != rec["right"], "distinct parent right wrapper")
    bad = copy.deepcopy(rec); bad["right"] = parent_recipe["right"]
    controls["parent_wrapper_alias"] = reject(lambda: check_recipe(kernel, bad, ENTRANCE, FULL),
                                              "parent alias")
    # Same dimension, different plane: the check is operator-level, not metadata.
    controls["wrong_entrance_plane"] = reject(
        lambda: check_recipe(kernel, rec, WRONG_ENTRANCE, FULL), "wrong plane")
    controls["parent_recipe_at_new_entrance"] = reject(
        lambda: check_recipe(kernel, parent_recipe, ENTRANCE, FULL), "parent recipe")
    record = {"word_sha256": digest(raw), "parent_word_sha256": digest(raw_parent),
              "local_checks_sha256": checks_sha, "parent_local_checks_sha256": parent_checks_sha,
              "adapter_sha256": digest(encoded(adapters)), "bindings": bindings,
              "residuals": residuals, "parent_bindings": parent_bindings,
              "parent_residual": parent_check, "changed_helpers": changed,
              "pair_classes": {"parent": len(classes_old), "staged": len(classes_new)},
              "residual_recipes": {"parent": len(recipes_old), "staged": len(recipes_new)},
              "warp_records": len(canonical["warps"]),
              "controls": controls}
    return record, (word, canonical, programs, adapters, bindings)


def consumer(blobs, stem, tag, work, compiler, kernel, donor_recipes, staged, receipt):
    """Bind a consumer word that retimes the 644/660 releases; the STAGED word is the control."""
    raw = blobs[consumer_name(stem, tag)]
    canonical, programs, checks_sha = generate(blobs, raw, work / stem)
    require(checks_sha == receipt, "recorded consumer native receipt")
    record = compare(staged, decode(raw, True), canonical, programs, compiler, kernel, donor_recipes)
    return {"word_sha256": digest(raw), "local_checks_sha256": checks_sha, **record}


def compare(staged, word, canonical, programs, compiler, kernel, donor_recipes):
    """Consumer emission against the STAGED control: entrance side, 644/660, donors."""
    s_word, s_canonical, s_programs, s_adapters, s_bindings = staged
    # Entrance side: every serialized recipe and warp record, and every helper's
    # entrance/terminal pair, equal the STAGED word's.
    adapters = adapter_file(compiler, canonical)
    require(adapters == s_adapters, "unchanged serialized residual adapters")
    require(pair_inventory(canonical, word) == pair_inventory(s_canonical, s_word),
            "unchanged entrance/terminal pairs")
    frames = lambda row: [[c["old"], c["new"], c["rank"]] for c in row["climbs"]]
    bindings, keys, ranks, clocks, scalars, controls = {}, {}, {}, {}, {}, {}
    for h in HELPERS:
        rows = {orientation: emitted_binding(word, canonical, stream, h, orientation == "backward")
                for orientation, stream in programs.items()}
        before, forward = s_bindings[str(h)]["forward"], rows["forward"]
        require(forward["entrance"] == ENTRANCE and forward["recipe_key"] == before["recipe_key"] and
                frames(forward) == frames(before) and
                [c["rank"] for c in rows["backward"]["climbs"]] == [c["rank"] for c in forward["climbs"]],
                "unchanged entrance, recipe key and climb frames")
        ranks[str(h)] = check_recipe(kernel, adapters["recipes"][forward["recipe_key"]],
                                     ENTRANCE, FULL)["rank"]
        (old_scalars, old_climbs), (new_scalars, new_climbs) = (source_events(w, h)
                                                                for w in (s_word, word))
        clocks[str(h)] = {"staged": [c[:2] for c in old_climbs], "consumer": [c[:2] for c in new_climbs]}
        scalars[str(h)] = sum(row not in old_scalars for row in new_scalars)
        # The binding sees the retiming: the STAGED word does not describe this program.
        controls[str(h)] = reject(lambda h=h: emitted_binding(s_word, canonical, programs["forward"], h),
                                  "staged word on consumer program")
        keys[str(h)] = forward["recipe_key"]
        bindings[str(h)] = {orientation: digest(encoded(row)) for orientation, row in rows.items()}
    # Only the two release donors change climbs: one direct climb replaces their first
    # two (H1 + H2 -> H3), and the separate kernel checks that new climb recipe.
    old, new = climb_chains(s_word, s_canonical, s_programs["forward"]), climb_chains(
        word, canonical, programs["forward"])
    require(sorted(h for h in old.keys() | new.keys() if old.get(h) != new.get(h)) == list(DONORS),
            "only the donors' climb chains change")
    merged = {}
    for h in DONORS:
        before, after = old[h], new[h]
        require([c[2] for c in before[:2]] == [1, 2] and after[1:] == before[2:] and
                after[0] == [before[0][0], before[1][1], 3], "one merged donor climb")
        merged[str(h)] = check_climb(compiler, kernel, after[0][0], after[0][1], donor_recipes)
    return {"adapter_sha256": digest(encoded(adapters)), "binding_sha256": bindings,
            "recipe_keys": keys, "residual_ranks": ranks, "climb_clocks": clocks,
            "changed_scalar_clocks": scalars,
            "donor_climb_ranks": {str(h): [[c[2] for c in old[h]], [c[2] for c in new[h]]]
                                  for h in DONORS},
            "merged_donor_climbs": merged, "events": {o: len(p) for o, p in programs.items()},
            "controls": controls}


def audit(blobs, work):
    compiler = module(blobs[COMPILER], "staged_pair_source_compiler")
    kernel = module(blobs[KERNEL], "staged_pair_independent_kernel")
    receipts = recorded_receipts()
    climb_recipes, donor_recipes, providers, consumers = {}, {}, {}, {}
    for tag in PROVIDERS:
        (work / tag).mkdir()
        providers[tag], staged = provider(blobs, tag, work / tag, compiler, kernel, climb_recipes)
        for stem in CONSUMERS:
            consumers.setdefault(stem, {})[tag] = consumer(
                blobs, stem, tag, work / tag, compiler, kernel, donor_recipes, staged,
                receipts[stem][tag])
    return {"providers": providers, "consumers": consumers, "climb_recipes": climb_recipes,
            "donor_climb_recipes": donor_recipes}
