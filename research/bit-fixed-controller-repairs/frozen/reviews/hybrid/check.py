#!/usr/bin/env python3
"""Independent signed hybrid-controller and selected native-route audit.

Standard library only. All scientific inputs are explicit and authenticated.
The arbitrary-input algebra is abstract; native realization stays conditional.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
import argparse
import ast
import copy
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path


PINS = {
    "recipe": "6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8",
    "matrices": "e5edb9e4e738192f98bd520ae6c1e8f1ddb19a0074ee9a1044e309b81e39c979",
    "r438": "a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022",
    "roots": "1fb726ea3818fe0837cceb0dd22a71a0814f064e5e781628104610d6468e0e55",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_source(path, name):
    raw = path.read_bytes()
    # Matrices and recipe may be losslessly compressed for portable packaging.
    if name in ("matrices", "recipe") and raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    need(digest(raw) == PINS[name], "source pin: " + name)
    return raw


def reduce_word(word):
    stack = []
    for g in word:
        if stack and stack[-1] == -g:
            stack.pop()
        else:
            stack.append(g)
    return tuple(stack)


def ident(n):
    return [{(i, ()): 1} for i in range(n)]


def matrix_product(left, right):
    result = []
    for row in left:
        out = {}
        for (middle, first), coefficient in row.items():
            for (column, second), value in right[middle].items():
                key = (column, reduce_word(first + second))
                out[key] = out.get(key, 0) + coefficient * value
        result.append({key: value for key, value in out.items() if value})
    return result


def transpose(matrix):
    # Separate starred generators; preserve exponent and reverse factor order.
    result = [{} for _ in matrix]
    for row, entries in enumerate(matrix):
        for (column, word), value in entries.items():
            starred = tuple((1 if g > 0 else -1) * (10000 + abs(g))
                            for g in reversed(word))
            result[column][(row, starred)] = value
    return result


def serialize(matrix):
    return [[[column, list(word), value]
             for (column, word), value in sorted(row.items())]
            for row in matrix]


def endpoint(n):
    return [{(i, ()): 1 if i % 2 == 0 else -1} for i in range(n)]


def primitive_matrix(event, n, inverse=False):
    kind = event["kind"]
    out = ident(n)
    if kind == "add":
        need(event["dst"] != event["src"], "ADD roles must be distinct")
        out[event["dst"]][(event["src"], ())] = (
            event["coefficient"] * (-1 if inverse else 1))
    elif kind == "code":
        g = event["generator"] * (-1 if inverse else 1)
        out[event["register"]] = {(event["register"], (g,)): 1}
    elif kind == "exchange":
        out = [{(i ^ 1, ()): 1} for i in range(n)]
    elif kind == "normalize":
        pass
    else:
        raise ValueError("unknown primitive: " + kind)
    return out


def flatten(events):
    primitives = []
    for event in events:
        kind = event["kind"]
        if kind == "local":
            x, y = 2 * event["pair"], 2 * event["pair"] + 1
            g = event["stage"] + 1
            if event["reverse"]:
                primitives.append(dict(kind="add", dst=x, src=y, coefficient=-1))
                if event.get("coded", False):
                    primitives.append(dict(kind="code", register=y, generator=-g,
                                           origin="local"))
            else:
                if event.get("coded", False):
                    primitives.append(dict(kind="code", register=x, generator=g,
                                           origin="local"))
                primitives.append(dict(kind="add", dst=y, src=x, coefficient=1))
        elif kind == "bridge":
            d, s, c = event["dst"], event["src"], event["coefficient"]
            primitives.extend([
                dict(kind="add", dst=2*d, src=2*s, coefficient=c),
                dict(kind="add", dst=2*s+1, src=2*d+1, coefficient=-c)])
        else:
            primitives.append(dict(event))
    return primitives


def evaluate(events, n, inverse=False):
    out = ident(n)
    primitives = flatten(events)
    for event in reversed(primitives) if inverse else primitives:
        out = matrix_product(primitive_matrix(event, n, inverse), out)
    return out


def independent_recipe(b):
    need(type(b) is int and b >= 1, "positive bank count")
    events = [dict(kind="local", stage=0, pair=0, reverse=False)]
    for j in range(b):
        events.append(dict(kind="local", stage=2*j+1, pair=j, reverse=True))
        if j + 1 < b:
            events.append(dict(kind="bridge", dst=j, src=j+1, coefficient=1))
        events.append(dict(kind="local", stage=2*j+2, pair=j, reverse=False))
        if j + 1 < b:
            events.append(dict(kind="bridge", dst=j, src=j+1, coefficient=-1))
    events.extend(dict(kind="bridge", dst=j+1, src=j, coefficient=1)
                  for j in range(b-2, -1, -1))
    events.append(dict(kind="exchange"))
    return events


def source_recipe(raw):
    nodes = [node for node in ast.parse(raw).body
             if isinstance(node, ast.FunctionDef) and node.name == "recipe"]
    need(len(nodes) == 1, "exactly one pinned recipe")
    env = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "<pinned recipe>",
                 "exec", dont_inherit=True, optimize=0), env)
    return env["recipe"]


def make_hybrid(events, variant):
    need(variant in ("historical", "two_code"), "known hybrid variant")
    result = []
    for event in events:
        if event["kind"] == "local":
            result.append(dict(event, coded=event["stage"] in (0, 1)))
            if variant == "historical" and event["stage"] in (0, 1):
                result.append(dict(kind="code", register=0,
                                   generator=-event["stage"]-1))
        elif event["kind"] == "exchange":
            result.append(dict(kind="normalize", register=1,
                               direction="cap_to_FULL", rank_one_children=111))
            if variant == "historical":
                result.extend([
                    dict(kind="code", register=1, generator=2),
                    dict(kind="code", register=0, generator=2),
                    dict(kind="add", dst=0, src=1, coefficient=-1),
                    dict(kind="code", register=1, generator=1),
                    dict(kind="add", dst=0, src=1, coefficient=1),
                    dict(kind="code", register=1, generator=-1)])
            else:
                result.extend([
                    dict(kind="add", dst=1, src=0, coefficient=-1),
                    dict(kind="code", register=1, generator=2),
                    dict(kind="add", dst=1, src=0, coefficient=1),
                    dict(kind="code", register=1, generator=-1)])
            result.extend([
                dict(kind="normalize", register=1, direction="FULL_to_cap",
                     rank_one_children=111),
                dict(event)])
        else:
            result.append(dict(event))
    return result


def expected_preterminal(b, variant):
    rows = []
    if variant == "historical":
        rows.extend([
            {(0, (-2,)): 1, (0, (-2, 1)): -1, (1, (-2,)): -1},
            {(0, (-2,)): 1}])
    else:
        rows.extend([
            {(1, ()): -1},
            {(1, ()): -1, (1, (-2,)): 1, (0, (-2, 1)): 1}])
    for j in range(1, b):
        rows.extend([{(2*j+1, ()): -1}, {(2*j, ()): 1}])
    return rows


def check_normalizations(word):
    actual = [e for e in word if e["kind"] == "normalize"]
    expected = [
        dict(kind="normalize", register=1, direction="cap_to_FULL", rank_one_children=111),
        dict(kind="normalize", register=1, direction="FULL_to_cap", rank_one_children=111)]
    need(actual == expected, "declared native normalization inventory")
    first = next(i for i,e in enumerate(word) if e["kind"] == "normalize")
    need(not any(e["kind"] in ("local","bridge") for e in word[first:]),
         "normalizations at terminal cut")
    need(word[-2] == expected[1] and word[-1]["kind"] == "exchange",
         "demotion immediately before terminal exchange")


def audit_word(word, b, variant):
    n = 2*b
    out = evaluate(word, n)
    need(out == endpoint(n), variant + ": all-input endpoint")
    inverse = evaluate(word, n, inverse=True)
    need(inverse == endpoint(n), variant + ": inverse endpoint")
    need(matrix_product(out, inverse) == ident(n), variant + ": right inverse")
    need(matrix_product(inverse, out) == ident(n), variant + ": left inverse")
    dual = ident(n)
    for event in flatten(word):
        dual = matrix_product(transpose(primitive_matrix(event, n, True)), dual)
    need(dual == transpose(inverse), variant + ": chronological dual")
    need(matrix_product(transpose(out), dual) == ident(n),
         variant + ": transpose-inverse identity")
    cut = next(i for i, event in enumerate(word) if event["kind"] == "normalize")
    before = evaluate(word[:cut], n)
    need(before == expected_preterminal(b, variant), variant + ": terminal pullback")
    codes = [e for e in word if e["kind"] == "code"]
    additions = [e for e in word if e["kind"] == "add"]
    need(len(codes) == (6 if variant == "historical" else 2), "code inventory")
    need(len(additions) == 2, "added scalar sweep inventory")
    check_normalizations(word)
    need(sum(e["kind"] == "local" and not e["coded"] for e in word) == 2*b-1,
         "clean local inventory")
    bridges = sum(e["kind"] == "bridge" for e in word)
    need(bridges == 3*b-3, "full inherited bridge inventory")
    locals_count = sum(e["kind"] == "local" for e in word)
    need(locals_count == 2*b+1, "full local inventory")
    need(sum(e["kind"] == "exchange" for e in word) == 1,
         "full terminal exchange inventory")
    macro_inventory = dict(
        coded_local_calls=2, clean_local_calls=2*b-1,
        inherited_bridges=bridges, inherited_scalar_bank_ADD_sweeps=2*bridges,
        additional_scalar_bank_ADD_sweeps=2,
        additional_prefix_code_applications=2 if variant=="historical" else 0,
        additional_terminal_code_applications=4 if variant=="historical" else 2,
        terminal_normalization_sweeps=2, children_per_normalization_sweep=111,
        terminal_pair_exchanges=b,
        known_nonlocal_scalar_ADDs=2*bridges*111+len(codes)*1499+222,
        local_internal_ADDs="same local words in both comparators; not repriced here",
        original_idle_owners="retained as a separate native caller premise")
    return dict(bank_pairs=b, formal_inputs=n, variant=variant,
                controller_events=len(word), word=word,
                complete_macro_inventory=macro_inventory,
                preterminal=serialize(before), endpoint=serialize(out),
                literal_inverse_endpoint=serialize(inverse),
                inverse_transpose_endpoint=serialize(dual),
                added_code_occurrences=len(codes),
                added_bank_ADD_sweeps=len(additions),
                added_scalar_ADDs=len(codes)*1499+222,
                normalization_rank_one_children=222,
                clean_replacements=2*b-1,
                extra_rank_mass_vs_fullycoded=(2*b-1)*60+222,
                net_rank_mass_saved_vs_allclean=-102)


def expect_failure(name, operation, message):
    try:
        operation()
    except ValueError as error:
        need(str(error) == message, name + ": wrong rejection: " + str(error))
        return dict(mutation=name, rejected=True, intended_message=message)
    raise ValueError(name + ": control did not reject")


def mutation_controls(events):
    controls = []
    original = make_hybrid(events, "two_code")
    n = 8
    def endpoint_gate(word):
        need(evaluate(word, n) == endpoint(n), "mutated all-input endpoint")
    code_indices = [i for i,e in enumerate(original) if e["kind"] == "code"]
    add_indices = [i for i,e in enumerate(original) if e["kind"] == "add"]
    for i in code_indices + add_indices:
        bad = copy.deepcopy(original)
        del bad[i]
        controls.append(expect_failure("omit_event_"+str(i),
                         lambda bad=bad: endpoint_gate(bad),
                         "mutated all-input endpoint"))
    for name, index, field, value in [
        ("wrong_code_direction", code_indices[0], "generator", -2),
        ("wrong_code_bank", code_indices[1], "register", 0),
        ("wrong_compensation_sign", add_indices[0], "coefficient", 1)]:
        bad = copy.deepcopy(original)
        bad[index][field] = value
        controls.append(expect_failure(name, lambda bad=bad: endpoint_gate(bad),
                                       "mutated all-input endpoint"))
    bad = copy.deepcopy(original)
    next(e for e in bad if e.get("stage") == 2)["coded"] = True
    controls.append(expect_failure("stale_coded_F2", lambda: endpoint_gate(bad),
                                   "mutated all-input endpoint"))
    # The overall signed endpoint is involutive; repeating it is not a control.
    state = evaluate(original, n)
    changed = False
    for event in reversed(flatten(original)):
        wrong = event["kind"] == "code" and not changed
        state = matrix_product(primitive_matrix(event, n, not wrong), state)
        changed = changed or wrong
    controls.append(expect_failure(
        "literal_inverse_one_code_direction",
        lambda: need(state == ident(n), "mutated literal inverse"),
        "mutated literal inverse"))
    # Frame normalization is abstractly the identity. Its absence cannot be
    # detected by this logical endpoint, so test the declared native inventory.
    normalizations = [i for i,e in enumerate(original) if e["kind"] == "normalize"]
    for omitted in normalizations:
        bad = copy.deepcopy(original)
        del bad[omitted]
        need(evaluate(bad,n) == endpoint(n),
             "omitted normalization has unchanged abstract endpoint")
        control = expect_failure(
            "omit_normalization_"+str(omitted),
            lambda bad=bad: check_normalizations(bad),
            "declared native normalization inventory")
        control["logical_endpoint_still_passes"] = True
        control["rejection_scope"] = "declared inventory, not native realization proof"
        controls.append(control)
    bad = copy.deepcopy(original)
    bad[normalizations[0]]["register"] = 0
    controls.append(expect_failure(
        "wrong_normalization_bank",lambda: check_normalizations(bad),
        "declared native normalization inventory"))
    # Independent generators really do not commute or equal their transposes.
    need(reduce_word((1,2,-1,-2)) != (), "noncommutative representation")
    need(transpose([{(0,(1,)):1}]) != [{(0,(-1,)):1}],
         "transpose must not be inverse")
    return controls


def mm(a, b):
    return [[sum(x*y for x,y in zip(row,column)) for column in zip(*b)]
            for row in a]


def tr(a):
    return [list(row) for row in zip(*a)]


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def mv(a, vector):
    return [sum(x*y for x,y in zip(row,vector)) for row in a]


def serialq(a):
    return [[str(x) for x in row] for row in a]


def route_witness(matrices, raw_word, root_word):
    mat = matrices["matrices"]
    k, r = mat["K"], mat["R"]
    need(len(k) == 111 and len(r) == 9, "actual code dimensions")
    a = []
    for p, mask in enumerate(k):
        row = 1 << p
        if p not in (0,1,2):
            for j, data in enumerate(r):
                if mask >> j & 1:
                    row ^= data
        a.append(row)
    need((a[3] & 1) == 1, "actual A[3,0]")
    full_lines = root_word["lines"]
    need(len(full_lines) == 120, "full E8 line inventory")
    p, q = 3, 0
    selected = {raw_word["ports_geom"][p], raw_word["ports_geom"][q]}
    # Reconstruct the same deterministic discovery tree, only composing routes
    # on the paths needed for the selected witness. No all-pairs claim.
    parent = {0: None}
    edge = {}
    frontier = [0]
    while not selected <= parent.keys():
        later = []
        for source in frontier:
            for target in range(120):
                dot = sum(x*y for x,y in zip(full_lines[source],full_lines[target]))
                if target in parent or abs(dot) != 2:
                    continue
                sign = 1 if dot == 2 else -1
                d = [F(x-sign*y) for x,y in zip(full_lines[source],full_lines[target])]
                norm = sum(x*x for x in d)
                reflection = [[F(i==j)-2*d[i]*d[j]/norm for j in range(8)]
                              for i in range(8)]
                parent[target] = source
                edge[target] = reflection
                later.append(target)
        need(later, "selected route labels reachable")
        frontier = later
    routes, projections, paths = {}, {}, {}
    for port in (p,q):
        label = raw_word["ports_geom"][port]
        need(raw_word["lines"][port] == full_lines[label], "selected actual root")
        path, current = [], label
        while parent[current] is not None:
            path.append(current)
            current = parent[current]
        g = eye(8)
        for target in reversed(path):
            g = mm(edge[target],g)
        root = [F(x) for x in raw_word["lines"][port]]
        cap = [row[1:] for row in g]
        projection = [[x*y/4 for y in root] for x in root]
        need(mm(tr(cap),cap) == eye(7), "selected cap orthonormal")
        need(mm(cap,tr(cap)) == [[F(i==j)-projection[i][j] for j in range(8)]
                                 for i in range(8)], "selected cap projector")
        rho = [projection[i]+cap[i] for i in range(8)]
        rho += [row+[F(0)]*7 for row in tr(cap)]
        need(tr(rho) == rho and mm(rho,rho) == eye(15),
             "selected route symmetric involution")
        routes[port], projections[port], paths[port] = rho,projection,list(reversed(path))
    vector = [F(x) for x in raw_word["lines"][q]]+[F(0)]*7
    need(mv(routes[q],vector) == vector, "source route fixes source root line")
    relative = mm(routes[p],routes[q])  # rho_p^-1 rho_q; both involutions.
    output = mv(relative,vector)
    expected = [F(0)]*15
    expected[10] = F(2)
    need(output == expected, "selected exact fresh-coordinate witness")
    target = [row+[F(0)]*7 for row in projections[p]]+[[F(0)]*15 for _ in range(7)]
    defect = [x-y for x,y in zip(output,mv(target,output))]
    need(defect == expected, "fresh output lies outside target P3")
    mod101 = [x.numerator*pow(x.denominator,-1,101)%101 for x in output]
    need(mod101[10] == 2, "odd-field fresh witness")
    # The binary function f(w)=1[w_10=0] is constant on target P3 cosets,
    # but f(T*0)=1 differs from f(T*(2e0))=0 although 2e0 is in source P0.
    # This gives an explicit quotient/pullback separator, rather than assuming
    # a point delta is admissible on an entire source-frame fiber.
    separator_at_zero, separator_at_image = 1, int(mod101[10] == 0)
    need(separator_at_zero != separator_at_image, "binary VALUE fiber separator")
    target_fiber_vector = [F(x) for x in raw_word["lines"][p]]+[F(0)]*7
    inverse_relative = mm(routes[q],routes[p])
    need(mm(relative,inverse_relative) == eye(15), "relative inverse orientation")
    inverse_image = mv(inverse_relative,target_fiber_vector)
    need(inverse_image == expected, "direct source VALUE pushforward witness")
    inverse_mod101 = [x.numerator*pow(x.denominator,-1,101)%101 for x in inverse_image]
    pushed_at_zero, pushed_at_target_shift = 1, int(inverse_mod101[10] == 0)
    need(pushed_at_zero != pushed_at_target_shift, "forward VALUE admission failure")
    need(mv(mm(routes[q],routes[q]),vector) == vector, "diagonal route control")
    zero = [[F(0)]*15 for _ in range(15)]
    need(mm(relative,zero) == mm(zero,relative) == zero, "ZERO frame control")
    controls = []
    controls.append(expect_failure(
        "omitted_relative_route",
        lambda: need(any(mv(eye(15),vector)[8:]), "fresh-coordinate witness required"),
        "fresh-coordinate witness required"))
    controls.append(expect_failure(
        "diagonal_substituted_for_offdiagonal",
        lambda: need(any(mv(mm(routes[q],routes[q]),vector)[8:]),
                     "fresh-coordinate witness required"),
        "fresh-coordinate witness required"))
    controls.append(expect_failure(
        "delete_actual_A30",
        lambda: need(((a[3]^1)&1) == 1, "actual A[3,0]"),
        "actual A[3,0]"))
    return dict(status="PASS_SELECTED_A30_EARLY_PROMOTION_COUNTEREXAMPLE",
                binary_code_rows=a, output_port=p,input_port=q,coefficient=1,
                selected_route_paths={str(i): paths[i] for i in (p,q)},
                selected_route_matrices={str(i): serialq(routes[i]) for i in (p,q)},
                input_address=list(map(str,vector)),
                output_address=list(map(str,output)),
                defect_outside_target_P3=list(map(str,defect)),
                output_mod101=mod101,
                binary_VALUE_separator=dict(
                    function="f(w)=1 if w_10=0 in F101, else 0",
                    constant_on_target_P3=True,
                    at_T_zero=separator_at_zero,at_T_source_P0_vector=separator_at_image,
                    implication="pullback along T is not constant on source P0"),
                direct_forward_VALUE_witness=dict(
                    address_push="T=rho3^-1*rho0",
                    VALUE_push="g(w)=f(T^-1*w)",
                    source_function="f(w)=1 if w_10=0 in F101, else 0",
                    source_function_constant_on_P0=True,
                    target_P3_vector=list(map(str,target_fiber_vector)),
                    inverse_address_image=list(map(str,inverse_image)),
                    g_at_zero=pushed_at_zero,g_at_target_P3_shift=pushed_at_target_shift,
                    implication="g is not constant on target P3"),
                exact_fresh_coordinates=list(map(str,output[8:])),
                selected_routes_checked=2,ordered_offdiagonal_pairs_checked=1,
                all_12210_ordered_pairs_replayed=False,
                controls=controls,
                scope="Rational ADDRESS and ADDRESS field F101; explicit binary VALUE separator",
                excluded_claim="No obstruction to all changed promoted-input factories")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in PINS:
        parser.add_argument("--"+name, required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    sources = {name: read_source(getattr(args,name),name) for name in PINS}
    recipe = source_recipe(sources["recipe"])
    cases = []
    # All-B proof is written separately. These are finite implementation fixtures.
    for b in list(range(1,13))+[16,32]:
        events = recipe(b)
        need(events == independent_recipe(b), "pinned recipe reconstruction")
        need(len(events) == 5*b-1, "recipe event count")
        need(evaluate(events,2*b) == endpoint(2*b), "all-clean signed endpoint")
        for variant in ("historical","two_code"):
            cases.append(audit_word(make_hybrid(events,variant),b,variant))
    b4 = recipe(4)
    controls = mutation_controls(b4)
    route = route_witness(json.loads(sources["matrices"]),
                          json.loads(gzip.decompress(sources["r438"])),
                          json.loads(gzip.decompress(sources["roots"])))
    # Determinant exponent certificate under a0=t, a1=u, all other a_s=1.
    prefix_exponents = [1,-1]
    terminal_exponents = [0,0]
    for event in make_hybrid(b4,"two_code"):
        if event["kind"] == "code":
            generator = event["generator"]
            terminal_exponents[abs(generator)-1] += 1 if generator>0 else -1
    need(terminal_exponents == [-1,1], "terminal determinant correction")
    need([a+b for a,b in zip(prefix_exponents,terminal_exponents)] == [0,0],
         "determinant exponents cancel")
    receipt = dict(
        status="PASS_ALL_B_PROOF_FIXTURES_TWO_CODE_HYBRID_AND_SELECTED_NATIVE_WITNESS",
        scientific_pin="20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        sources=PINS, algebra="Integral free group algebra; transpose generators independent",
        finite_bank_counts=list(range(1,13))+[16,32],cases=cases,
        word_controls=controls, early_promotion=route,
        two_code_lower_bound=dict(
            scalar_specialization="a0=t,a1=u,other generators=1 over Q(t,u)",
            prefix_determinant_exponents=prefix_exponents,
            required_added_exponents=[-1,1],attained_added_exponents=terminal_exponents,
            minimum_added_single_bank_generator_occurrences=2,
            restrictions=["same first coded F0,B1","all remaining locals clean",
                          "no extra coded local","single-bank a_s or a_s^-1 primitives",
                          "scalar determinant-neutral mixing and logical normalization",
                          "fixed all-clean signed endpoint",
                          "no free composite-code primitive or new operator-valued gate"]),
        invoice=dict(historical_code_occurrences=6,new_code_occurrences=2,
                     historical_scalar_ADDs=9216,new_scalar_ADDs=3220,
                     scalar_ADDs_saved=5996,normalization_rank_one_children=222,
                     conditional_net_rank_saving_vs_allclean=-102,
                     formula_extra_rank_vs_fullycoded="60*(2*B-1)+222",
                     historical_B4_allowances_only={"beta_002":492,"beta_003":309},
                     historical_B4_extra_rank=642),
        scope=["written proof covers every B>=1 and arbitrary 2B input banks",
               "finite replay covers listed bank counts only",
               "local arbitrary-helper restoration and copied-field cleanup are premises",
               "signed abstract local map is not an assertion about actual R429 integer target",
               "native phase, mixed owners, access, precision and full recurrence remain conditional",
               "two-code optimum is for the stated generator-occurrence alphabet only",
               "no new rank saving, physical optimum, kappa or formal-kernel proof"])
    # Output is external; no package-relative writes or hidden dependencies.
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":receipt["status"],"cases":len(cases),
                      "word_controls":len(controls),
                      "receipt_canonical_sha256":digest(canonical(receipt))},
                     sort_keys=True))


if __name__ == "__main__":
    main()
