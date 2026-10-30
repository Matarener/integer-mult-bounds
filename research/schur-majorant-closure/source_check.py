"""Authenticated source-arithmetic probe; callbacks do NOT execute gates.

Only the source's floating diagnostic is replaced by a node collector.
The determinant oracle is an integration dependency, not new independence.
"""
import argparse
import ast
import copy
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
import types

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
PINS = {
    "original": "06d1861bfe8af543908e26557ffda7e451ff176bceb9bacfaf0f04f234b336d5",
    "exact": "270044fc9fd1203a7eee45ec68a7ebb6b6fab668a109ec956434b8a6cbb483ff",
    "triangular": "322e5b821e0db6c97d39ffb65e5e108755a91d91255ef47f7a63ad30c3ef8413",
    "oracle": "716bb5e5c7ffb0d2ef44951a13fec49bb875a138e07503de8b6e652276e1f8ab",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticated(path, key):
    data = path.read_bytes()
    need(sha256(data).hexdigest() == PINS[key], "authenticated source: " + key)
    return data


def module(name, path, data):
    result = types.ModuleType(name)
    result.__file__ = str(path)
    sys.modules[name] = result
    exec(compile(data, str(path), "exec", dont_inherit=True, optimize=0), result.__dict__)
    return result


def selected_tree(data):
    wanted = {"toep", "lower", "invseries", "conv", "triangle_plan"}
    tree = ast.parse(data)
    tree.body = [copy.deepcopy(node) for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name in wanted]
    need({node.name for node in tree.body} == wanted, "complete selected source functions")
    return tree


class Diagnostic(ast.NodeTransformer):
    def __init__(self, wrong_sign=False):
        self.diagnostic_changes = self.sign_changes = 0
        self.wrong_sign = wrong_sign

    def visit_Assign(self, node):
        target = node.targets[0] if len(node.targets) == 1 else None
        if (isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name)
                and target.value.id == "STATS" and isinstance(target.slice, ast.Constant)
                and target.slice.value == "max_triangle_coefficient"):
            self.diagnostic_changes += 1
            return ast.copy_location(ast.Expr(ast.Call(ast.Name("trace_node", ast.Load()),
                                                      [ast.Name("indices", ast.Load()), ast.Name("f", ast.Load())], [])), node)
        if (self.wrong_sign and isinstance(target, ast.Name) and target.id == "s"
                and isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.Sub)):
            node.value.op = ast.Add()
            self.sign_changes += 1
        return node


def run_source(original, exact, indices, symbol, wrong_sign=False):
    nodes, shears, leaves = {}, [], []

    def trace_node(ids, values):
        need(tuple(ids) not in nodes, "one source node per wire subset")
        nodes[tuple(ids)] = exact.Vec(values)

    def convolution(left, right):
        return exact.Vec(sum((left[j]*right[k-j] for j in range(len(left))
                              if 0 <= k-j < len(right)), exact.C())
                         for k in range(len(left)+len(right)-1))

    class Concatenate:
        def __getitem__(self, parts):
            values = []
            for part in parts:
                values.extend(part if isinstance(part, (list, tuple)) else [part])
            return exact.Vec(values)

    def shear(target, source, matrix):
        shears.append((tuple(target), tuple(source), exact.Mat(matrix)))
        return []

    def diagonal(ids, values):
        leaves.append((tuple(ids), exact.Vec(values)))
        return []

    facade = types.SimpleNamespace(asarray=lambda values, dtype=None: exact.Vec(values),
                                   array=lambda rows, dtype=None: exact.Mat(rows),
                                   zeros=lambda n, dtype=None: exact.Vec([0]*n),
                                   convolve=convolution, r_=Concatenate())
    tree = selected_tree(original)
    before = sha256(ast.dump(tree).encode()).hexdigest()
    adapter = Diagnostic(wrong_sign)
    tree = ast.fix_missing_locations(adapter.visit(tree))
    need(adapter.diagnostic_changes == 1 and adapter.sign_changes == int(wrong_sign),
         "only declared diagnostic/source mutation adaptations")
    scope = dict(np=facade, STATS={"triangle_nodes": 0}, trace_node=trace_node,
                 diag=diagonal, parallel=lambda left, right: [], toeplitz_shear=shear)
    exec(compile(tree, "<authenticated selected source algebra>", "exec", dont_inherit=True, optimize=0), scope)
    plan = scope["triangle_plan"](list(indices), exact.Vec(symbol))
    need(plan == [] and scope["STATS"]["triangle_nodes"] == len(nodes), "algebra-only callbacks, complete source node trace")
    return nodes, shears, leaves, scope, before, sha256(ast.dump(tree).encode()).hexdigest()


def as_oracle(matrix, oracle):
    return tuple(tuple(oracle.G(value.re, value.im) for value in row) for row in matrix)


def envelope(matrix, oracle):
    n = len(matrix)
    return max(max(sum((oracle.mu(x) for x in row), Q(0)) for row in matrix),
               max(sum((oracle.mu(matrix[i][j]) for i in range(n)), Q(0)) for j in range(n)))


def defect(matrix, oracle):
    return tuple(tuple(value-(oracle.ONE if i == j else oracle.ZERO)
                       for j, value in enumerate(row)) for i, row in enumerate(matrix))


def inspect_trace(trace, exact, oracle):
    nodes, shears, leaves, scope, before, after = trace
    node_count = schur_count = cramer_entries = shear_count = 0
    rho = Q(1, 2)
    lookup = {(target, source): as_oracle(matrix, oracle) for target, source, matrix in shears}
    for ids, symbol in nodes.items():
        matrix = as_oracle(scope["lower"](symbol), oracle)
        need(envelope(defect(matrix, oracle), oracle) <= rho, "actual source descendant component bound")
        node_count += 1
        n = len(ids)
        if n == 1:
            continue
        ev, od = ids[::2], ids[1::2]
        local_ev, local_od = tuple(range(0, n, 2)), tuple(range(1, n, 2))
        E = as_oracle(scope["lower"](nodes[ev]), oracle)
        S = as_oracle(scope["lower"](nodes[od]), oracle)
        need(E == oracle.principal(matrix, local_ev), "actual E is principal restriction")
        need(S == oracle.schur(matrix, local_ev, local_od), "actual S equals bordered-determinant Schur")
        schur_count += 1
        O = tuple(tuple(matrix[i][j] for j in local_ev) for i in local_od)
        K, ZK = lookup[(od, ev)], lookup[(ev, od)]
        for i in range(len(E)):
            for j in range(len(E)):
                need(E[i][j] == (E[i-j][0] if i >= j else oracle.ZERO)
                     and O[i][j] == (O[i-j][0] if i >= j else oracle.ZERO),
                     "actual E/O are lower Toeplitz")
                need(sum((E[i][k]*O[k][j] for k in range(len(E))), oracle.ZERO)
                     == sum((O[i][k]*E[k][j] for k in range(len(E))), oracle.ZERO),
                     "actual E/O Toeplitz commutation")
        pivot = oracle.determinant(E)
        need(bool(pivot), "source E determinant nonzero")
        m = len(E)
        for column in range(m):
            for row in range(m):
                replaced = tuple(tuple(O[i][column] if j == row else E[i][j]
                                       for j in range(m)) for i in range(m))
                need(K[row][column] == oracle.determinant(replaced)/pivot,
                     "actual K equals Cramer solution E*K=O in commuting Toeplitz algebra")
                cramer_entries += 1
        shifted = tuple(tuple(K[i-1][j] if i else oracle.ZERO for j in range(m)) for i in range(m))
        need(ZK == shifted, "actual ZK is one lower shift")
        need(envelope(O, oracle) <= rho and envelope(K, oracle) <= 1 and envelope(ZK, oracle) <= 1,
             "actual source local O/K/ZK component bounds")
        for kernel in (K, ZK):
            shear = tuple(tuple((oracle.ONE if i == j else
                                kernel[i-m][j] if i >= m and j < m else oracle.ZERO)
                                for j in range(2*m)) for i in range(2*m))
            inverse = tuple(tuple((oracle.ONE if i == j else
                                  -kernel[i-m][j] if i >= m and j < m else oracle.ZERO)
                                  for j in range(2*m)) for i in range(2*m))
            need(envelope(shear, oracle) <= 2 and envelope(inverse, oracle) <= 2, "actual kernel completed shear/inverse bounds")
            shear_count += 1
    need(len(shears) == 2*schur_count and len(leaves) == (len(nodes)+1)//2, "complete source callback census")
    return {"nodes": node_count, "schur_nodes": schur_count, "cramer_entries": cramer_entries,
            "Toeplitz_commutation_checks": schur_count,
            "completed_shear_checks": shear_count, "source_ast": before, "adapted_ast": after}


def static_admission(data):
    tree = ast.parse(data)
    triangle = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Triangle")
    plan = next(node for node in triangle.body if isinstance(node, ast.FunctionDef) and node.name == "plan")
    admission = False
    for node in ast.walk(plan):
        if (isinstance(node, ast.Compare) and isinstance(node.left, ast.Call)
                and isinstance(node.left.func, ast.Name) and node.left.func.id == "component_l1"
                and len(node.ops) == 1 and isinstance(node.ops[0], ast.LtE)):
            bound = node.comparators[0]
            admission = (isinstance(bound, ast.Call) and isinstance(bound.func, ast.Name)
                         and bound.func.id == "Q" and [x.value for x in bound.args if isinstance(x, ast.Constant)] == [1, 2])
    text = ast.unparse(plan)
    need(admission and "sorted(indices) == list(range(n))" in text, "source component admission and full wire permutation located")
    return {"component_l1_half_admission_located": True, "complete_wire_permutation_check_located": True,
            "Triangle_plan_factory_executed": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=P/"source")
    parser.add_argument("--original-path", type=Path, default=ROOT/"research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_circuits.py")
    parser.add_argument("--oracle-path", type=Path, default=P/"independent_oracle.py")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    original = authenticated(args.original_path, "original")
    exact_path = args.source_dir/"predecessor_exact.py"
    exact = module("source_probe_exact", exact_path, authenticated(exact_path, "exact"))
    oracle = module("source_probe_oracle", args.oracle_path, authenticated(args.oracle_path, "oracle"))
    triangular = authenticated(args.source_dir/"PR4205-triangular.py.txt", "triangular")
    rows = []
    cases = [(n, 0, reverse) for n in (1, 2, 4, 8) for reverse in (False, True)] + [(4, 1, False), (8, 1, False)]
    for n, seed, reverse in cases:
        scale = Q(1, (4 if seed == 0 else 8)*n)
        symbol = exact.Vec(exact.C((1 if i == 0 else 0) + (scale if (i+seed)%2 == 0 else -scale),
                                   scale if (2*i+seed)%3 else -scale) for i in range(n))
        need(sum((abs(x.re-(1 if i == 0 else 0))+abs(x.im) for i, x in enumerate(symbol)), Q(0)) <= Q(1, 2), "own mathematical source admission")
        ids = list(reversed(range(n))) if reverse else list(range(n))
        trace = run_source(original, exact, ids, symbol)
        rows.append({"n": n, "seed": seed, "reversed_ids": reverse, **inspect_trace(trace, exact, oracle)})
    # A wrong Schur sign can preserve every tested norm; exact identity is
    # the semantic control, rather than treating norm success as correctness.
    symbol = exact.Vec([1, Q(1, 4), 0, 0])
    wrong = run_source(original, exact, [0, 1, 2, 3], symbol, True)
    nodes, shears, leaves, scope, before, after = wrong
    base = as_oracle(scope["lower"](symbol), oracle)
    actual_wrong = as_oracle(scope["lower"](nodes[(1, 3)]), oracle)
    expected = oracle.schur(base, (0, 2), (1, 3))
    need(actual_wrong != expected, "wrong source Schur sign must fail exact identity")
    need(all(envelope(defect(as_oracle(scope["lower"](values), oracle), oracle), oracle) <= Q(1, 2)
             for values in nodes.values()), "wrong sign norm-only positive control")
    result = {"status": "PASS_AUTHENTICATED_SOURCE_SCHUR_ARITHMETIC_ONLY_NO_GATE_REPLAY",
              "logical_source_ids": {"original": "research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_circuits.py",
                                     "exact": "source/predecessor_exact.py", "triangular": "source/PR4205-triangular.py.txt",
                                     "oracle": "independent_oracle.py"},
              "source_sha256": PINS, "static_admission": static_admission(triangular),
              "cases": rows, "root_cases": len(rows),
              "source_nodes": sum(x["nodes"] for x in rows),
              "source_schur_nodes": sum(x["schur_nodes"] for x in rows),
              "cramer_entries": sum(x["cramer_entries"] for x in rows),
              "completed_shear_checks": sum(x["completed_shear_checks"] for x in rows),
              "wrong_sign_control": {"exact_identity_rejected": True, "all_descendant_norms_still_admitted": True},
              "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "scope": "Authenticated original five source functions; only floating diagnostic replaced by collector. Exact array/convolution facade and diag/parallel/shear callbacks are algebra-only and return empty plans. No FFT, stored gates, rounding, full Triangle.plan factory or physical program executed. Frozen determinant oracle is reused integration evidence, not a second independent oracle."}
    if args.output is not None:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(result["status"])


if __name__ == "__main__":
    main()
