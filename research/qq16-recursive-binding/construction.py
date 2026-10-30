"""QQ16 rank-one capsules in the retained physical recursive machine.

New source inspection and descriptor arithmetic; no retained executable imports.
The caller authenticates word and source bytes before invoking audit().
This verifies an ABI construction, not execution of the enormous selected cover.
Apache-2.0; substantial OpenAI Codex assistance.
"""
import ast
from collections import Counter
from hashlib import sha256
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def coarse_depth(e):
    need(type(e) is int and e >= 0, "nonnegative integer active width")
    n = 0
    while e >= 73:
        e = 48 * (e // 73)
        n += 1
    return n


def signed_recipe(q, sign, dimension=73):
    """Actual MonomialPackets literal inputs around a positive rank-one child.

    This is finite source geometry, independent of numerical values/depth.
    Row convention: output address bit i is parity(matrix_rows[i] & input).
    The same map is repeated at every tensor-factor position by the backend.
    """
    need(type(dimension) is int and 1 <= dimension <= 73, "native literal dimension")
    need(type(q) is int and 0 < q < (1 << dimension), "nonzero source line")
    need(type(sign) is int and sign in (-1, 1), "literal signed line")
    pivot = (q & -q).bit_length() - 1
    columns = (q,) + tuple(1 << i for i in range(dimension) if i != pivot)
    rows = [sum(((v >> i) & 1) << j for j, v in enumerate(columns)) for i in range(dimension)]
    left, inv = rows[:], [1 << i for i in range(dimension)]
    for col in range(dimension):
        at = next((j for j in range(col, dimension) if (left[j] >> col) & 1), None)
        need(at is not None, "invertible line wrapper")
        left[col], left[at] = left[at], left[col]
        inv[col], inv[at] = inv[at], inv[col]
        for j in range(dimension):
            if j != col and ((left[j] >> col) & 1):
                left[j] ^= left[col]
                inv[j] ^= inv[col]
    need(left == [1 << i for i in range(dimension)], "wrapper inverse elimination")
    def literal(matrix, offset):
        return {"matrix_rows": matrix, "offset": offset, "phase": 0,
                "linear_Z4": [0] * dimension, "quadratic_rows": [0] * dimension}
    result = {"rank": 1, "right": literal(inv, 0),
              "left": literal(rows, q if sign == -1 else 0)}
    # Algebraic checks on all generator columns establish the full linear maps.
    def act(matrix, value):
        return sum(((r & value).bit_count() & 1) << i for i, r in enumerate(matrix))
    for i in range(dimension):
        need(act(rows, act(inv, 1 << i)) == 1 << i and
             act(inv, act(rows, 1 << i)) == 1 << i, "two exact wrapper inverse orders")
    need(act(rows, 1) == q, "positive native direction maps to caller q")
    return result


def capsule(lam, spacing, before=0, after=0, root_width=None):
    """The source prepare_child rank-one descriptor, at parent width 73*lam.

    The rows exponent is a sufficient divisibility promise, not a decoded
    actual row allocation. Source prefixes/compact fields/r/global grid remain
    untouched, so volume equality only needs this active/after calculation.
    """
    need(all(type(x) is int and x >= 0 for x in (before, after)), "spectator widths")
    need(type(lam) is int and lam >= 1 and type(spacing) is int and spacing >= 1,
         "positive tensor depth and source spacing")
    parent = 73 * lam
    if root_width is None:
        root_width = parent
    need(type(root_width) is int and root_width >= parent, "parent within global root width")
    child_after = after + 72 * lam * spacing
    need(before + parent * spacing + after == before + lam * spacing + child_after,
         "same complete packet volume")
    available = coarse_depth(parent) - 1
    required = coarse_depth(lam)
    need(required <= available, "rank-one child inherits sufficient row stock")
    return {"lambda": lam, "parent_width": parent, "child_width": lam,
            "global_root_width": root_width, "spacing": spacing,
            "before": before, "parent_after": after, "child_after": child_after,
            "parent_stock_exponent": coarse_depth(parent),
            "inherited_stock_exponent": available, "required_stock_exponent": required,
            "packet_address_bits": before + parent * spacing + after,
            "child_leaf": lam < 73 or pow(lam, 1000) < root_width}


def function(tree, cls, name):
    container = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls), None)
    need(container is not None, "source class " + cls)
    node = next((n for n in container.body if isinstance(n, ast.FunctionDef) and n.name == name), None)
    need(node is not None, "source method " + cls + "." + name)
    return node


def source_contract(sources):
    """Pin actual source mechanisms without treating their text as execution."""
    need(set(sources) >= {"machine", "root_plan", "selected_binding", "bank_packets", "physical_proof"},
         "complete actual-machine documentary inputs")
    trees = {key: ast.parse(sources[key]) for key in
             ("machine", "root_plan", "selected_binding", "bank_packets")}
    methods = {}
    for key, cls, names in (
        ("machine", "Machine", ("prepare_child", "enter_child", "return_node", "primitive_boundary", "node", "run")),
        ("bank_packets", "BankPackets", ("gather", "scatter", "commit")),
        ("selected_binding", "SelectedBinding", ("group",)),
    ):
        for name in names:
            node = function(trees[key], cls, name)
            methods[key + "." + name] = sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()
    selected = next(n for n in trees["selected_binding"].body
                    if isinstance(n, ast.ClassDef) and n.name == "SelectedBinding")
    constants = {}
    for node in selected.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                constants[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
    need({k: constants[k] for k in ("dimension", "maximum_rank", "families", "slots", "private")} ==
         {"dimension": 73, "maximum_rank": 48, "families": 14336, "slots": 704, "private": 8},
         "actual selected machine dimensions and inventory")
    # These are source-binding guards; the capsule induction is in NATIVE.md.
    required = {
        "machine": [
            'width = Count(self.c("columns"))',
            'tail.multiply_small(self.binding.dimension - rank)',
            'after = Count.product(tail, self.c("spacing"))',
            'value = self.c("unused") if name == "rows" else width if name == "width" else after if name == "after" else self.c(name)',
            'self.parking.park()', 'self.parking.restore()',
            'self.group.code[self.pc - 1][2:] == (target, rank)',
            'need(remainder.zero() and not unused.zero(), "complete fresh row divisor at node")',
        ],
        "root_plan": ['self.fast = compare(selected, Q0) > 0',
                      'stock.multiply_small(self.level_divisor)',
                      'save("padded_rows", times(multiples, stock))'],
        "bank_packets": ['Layout: prefix, family, cover, unused row, complete within-row packet.',
                         'copy_bits(source, self.packets[slot], extent)'],
        "selected_binding": ['code.extend(self.codes[call["orientation"]])',
                             'keys = tuple((o.family, self.cover.rank(multiply(g, o.sigma_columns))) for o in owners)'],
        "physical_proof": ['D0(e)=0 for e<73, otherwise 1+D0(48 floor(e/73))',
                           'I keep d,K,G,H and the coefficient grid global.'],
    }
    for key, needles in required.items():
        for needle in needles:
            need(needle in sources[key], "actual physical source anchor: " + key + ": " + needle)
    return {"class_constants": {k: constants[k] for k in
             ("dimension", "maximum_rank", "families", "slots", "private")},
            "method_ast_sha256": methods,
            "source_sha256": {k: sha256(sources[k].encode()).hexdigest() for k in sorted(required)},
            "retained_execution_rerun": False}


def events(word):
    need(type(word) is list and all(type(e) is list and e for e in word), "literal event word")
    lines = [(i, e) for i, e in enumerate(word) if e[0] == "line"]
    need(lines and lines[0] == (4, ["line", "W0", 0, 1]), "actual first H1 event")
    need(word[2:4] == [["clear", "W0", "hole0"], ["add", "W0", "Y0", "1"]],
         "first child reads owned current-Y copy")
    inventory = Counter()
    scope = []
    covered = []
    for i, e in enumerate(word):
        if e[0] == "begin":
            scope.append(e[1])
        elif e[0] == "end":
            need(scope and scope.pop() == e[1], "balanced caller private lifetime")
        elif e[0] == "line":
            need(not scope and len(e) == 4 and type(e[2]) is int and 0 <= e[2] < 112
                 and type(e[3]) is int and e[3] in (-1, 1), "isolated rank-one native call")
            typ = "initial_positive" if e[1].startswith("W") and e[3] == 1 else \
                  "query_negative" if e[1] in ("Z10", "Z11") and e[3] == -1 else \
                  "response_positive" if e[1] == "Z10" and e[3] == 1 else None
            need(typ is not None, "known actual event variant")
            inventory[typ] += 1
            covered.append({"event": i, "target": e[1], "port": e[2], "sign": e[3], "variant": typ,
                            "child_rank": 1, "wrapper_count": 2})
    need(not scope, "closed caller lifetimes")
    need(inventory == {"initial_positive": 112, "query_negative": 104, "response_positive": 8},
         "all 224 actual signed variants")
    need({e["port"] for e in covered[:112]} == set(range(112)), "all initial ports")
    return {"count": len(covered), "inventory": dict(sorted(inventory.items())),
            "events": covered, "events_sha256": digest(covered), "first_event": covered[0],
            "native_inside_scalar_private_scope": False}


def audit(word, source_texts):
    bound = source_contract(source_texts)
    covered = events(word)
    fixtures = [capsule(lam, spacing, 3, 5, 73 * lam + 19)
                for lam, spacing in ((1, 1), (2, 2), (72, 73), (73, 100000),
                                     (74, 19), (1000, 4096), (1000000, 200000))]
    need(all(x["child_width"] < x["parent_width"] for x in fixtures), "strict source descent")
    controls = {}
    for name, fn in (
        ("first_child_borrowed_target", lambda: events(word[:4] + [["line", "Y0", 0, 1]] + word[5:])),
        ("missing_line", lambda: events(word[:4] + word[5:])),
        ("parent_too_narrow", lambda: capsule(73, 1, root_width=73)),
        ("zero_spacing", lambda: capsule(73, 0)),
        ("source_row_contract_changed", lambda: source_contract({**source_texts, "machine": source_texts["machine"].replace(
            'value = self.c("unused") if name == "rows"', 'value = self.c("rows") if name == "rows"')})),
    ):
        try:
            fn()
        except ValueError:
            controls[name] = "rejected"
        else:
            raise ValueError("ineffective control " + name)
    return {"schema": "qq16-physical-recursive-capsule-v1", "source_binding": bound,
            "literal_coverage": covered, "descriptor_fixtures": fixtures, "controls": controls,
            "quantified_claim": "For every admitted physical parent e=73*lambda, R divisible by L^D0(e), and positive lambda: each of the 224 rank-one events can use the existing prepare_child descriptor with width lambda, rows R/L and after increased by 72*lambda*K; its required recursive stock divides R/L and its complete packet volume is unchanged.",
            "scope": "Descriptor and source-contract composition. The retained selected program does not contain the new recovery word. Output allocation, chronological caller connection, new program registration, precision and complete tariff are separate integration obligations."}
