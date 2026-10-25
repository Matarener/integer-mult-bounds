"""Source-bound exact rational generator and dirty-shear macro certificates.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. Numerical FFT/parity children are outside this macro replay.
"""
import argparse
import ast
import copy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from fractions import Fraction as Q

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("rational_stein", HERE / "rational.py")
rat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rat)
C, Matrix, Vector, need = rat.C, rat.Matrix, rat.Vector, rat.need
SOURCE = "research/capped-phase-fusion/evidence/inplace_algebra_ultra/"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(matrix):
    return sha256(canonical(rat.exact_record(matrix))).hexdigest()


def rejected(operation, label):
    try:
        operation()
    except ValueError:
        return label
    raise ValueError("control unexpectedly passed: " + label)


def authenticate():
    rows = [r for r in json.loads((HERE / "SOURCES.json").read_text())["files"]
            if r["usage"] == "input"]
    for row in rows:
        raw = (ROOT / row["path"]).read_bytes()
        need(sha256(raw).hexdigest() == row["sha256"], "source hash: " + row["path"])
        rejected(lambda: need(sha256(raw + b"\0").hexdigest() == row["sha256"], "source corruption"),
                 "source corruption")
    return [{"path": r["path"], "sha256": r["sha256"]} for r in rows]


def load_subject():
    path = ROOT / (SOURCE + "check_exact_algebra.py")
    namespace = {"__name__": "_retained_exact_subject", "__file__": str(path)}
    exec(compile(path.read_bytes(), str(path), "exec", optimize=0), namespace)
    return namespace


def macro_template():
    tree = ast.parse((ROOT / (SOURCE + "check_circuits.py")).read_bytes())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == "lowdisp_shear")
    loop = next(n for n in function.body if isinstance(n, ast.For))
    start = next(i for i, n in enumerate(loop.body) if isinstance(n, ast.Assign)
                 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "p")
    tail = copy.deepcopy(loop.body[start:])
    need([type(n).__name__ for n in tail] ==
         ["Assign", "AugAssign", "Assign", "AugAssign", "AugAssign", "AugAssign", "AugAssign"],
         "retained seven-statement macro tail")
    calls = [n.func.id for statement in tail for n in ast.walk(statement)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    need(calls == ["triangle_plan", "toeplitz_shear", "lower", "inverse",
                   "toeplitz_shear", "lower"], "retained child-call order")
    identity = sha256(ast.dump(ast.Module(body=tail, type_ignores=[])).encode()).hexdigest()
    function = ast.FunctionDef(
        name="emit", args=ast.arguments(posonlyargs=[], args=[ast.arg(arg=n) for n in
        ("target", "source", "g", "h", "gamma")], vararg=None, kwonlyargs=[],
        kw_defaults=[], kwarg=None, defaults=[]),
        body=[ast.Assign(targets=[ast.Name(id="result", ctx=ast.Store())],
                         value=ast.List(elts=[], ctx=ast.Load()))] + tail +
             [ast.Return(value=ast.Name(id="result", ctx=ast.Load()))],
        decorator_list=[], type_params=[])
    module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    return compile(module, "<authenticated generator macro>", "exec", optimize=0), identity


class MacroEmitter:
    def __init__(self, size, subject, code):
        self.size, self.subject = size, subject
        namespace = {"triangle_plan": self.triangle, "toeplitz_shear": self.shear,
                     "inverse": self.inverse, "lower": rat.lower}
        exec(code, namespace)
        self.emit = namespace["emit"]
        self.calls = []

    def triangle(self, indices, coefficients):
        need(len(indices) == self.size and len(set(indices)) == self.size, "ordered source indices")
        matrix = Matrix(self.subject["eye"](2 * self.size))
        lower = rat.lower(coefficients)
        for i, row in enumerate(indices):
            for j, column in enumerate(indices):
                matrix[row][column] = lower[i][j]
        self.calls.append("triangle")
        return [matrix]

    def shear(self, target, source, coefficients):
        need(len(target) == len(source) == self.size
             and len(set(target + source)) == 2 * self.size, "disjoint complete banks")
        matrix = Matrix(self.subject["eye"](2 * self.size))
        for i, row in enumerate(target):
            for j, column in enumerate(source):
                matrix[row][column] = C.wrap(coefficients[i][j])
        self.calls.append("shear")
        return [matrix]

    def inverse(self, plan):
        self.calls.append("inverse")
        return [Matrix(self.subject["inv"](a)) for a in reversed(plan)]


def collect_shears(subject):
    """Execute the retained exact producer with one read-only collection hook."""
    tree = ast.parse((ROOT / (SOURCE + "check_exact_algebra.py")).read_bytes())
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    walk = copy.deepcopy(next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == "walk"))
    index = next(i for i, node in enumerate(walk.body) if isinstance(node, ast.Assign)
                 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "S")
    walk.body.insert(index + 1, ast.Expr(value=ast.Call(func=ast.Name(id="capture", ctx=ast.Load()),
                     args=[ast.Name(id=x, ctx=ast.Load()) for x in ("K", "L", "n", "depth")],
                     keywords=[])))
    collected = []
    namespace = dict(subject)
    namespace["trace"] = []
    namespace["capture"] = lambda k, l, n, depth: collected.extend(
        [(f"source-K-n{n}-d{depth}", Matrix(k)), (f"source-L-n{n}-d{depth}", Matrix(l))])
    exec(compile(ast.fix_missing_locations(ast.Module(body=[walk], type_ignores=[])),
                 "<authenticated Schur producer with collection hook>", "exec", optimize=0), namespace)
    for size in (2, 4, 8):
        for complex_case in (False, True):
            column = [C(1)] + [C(Q((-1) ** i, 64 * size),
                                  Q(i, 128 * size) if complex_case else 0) for i in range(1, size)]
            row = [C(1)] + [C(Q(1, 64 * size),
                               Q((-1) ** j, 128 * size) if complex_case else 0) for j in range(1, size)]
            matrix = Matrix([[column[i - j] if i >= j else row[j - i]
                              for j in range(size)] for i in range(size)])
            namespace["walk"](matrix)
    # Source-admissible complex corner fixture from the row/conjugate convention check.
    matrix = Matrix(subject["eye"](4))
    matrix[0][2] = matrix[1][3] = C(Q(1, 16))
    matrix[0][3] = C(0, Q(1, 16))
    namespace["walk"](matrix)
    return collected, namespace["trace"]


def one_case(label, matrix, subject, code):
    size = len(matrix)
    z = subject["shift"](size)
    displacement = Matrix(subject["add"](matrix, subject["mm"](
        subject["mm"](z, matrix), rat.transpose(z)), -1))
    generators, heights = rat.generators(displacement)
    rank = subject["rank"](displacement)
    need(len(generators) == rank, "exact generator rank")
    reconstructed_e = Matrix(subject["zeros"](size))
    reconstructed_t = Matrix(subject["zeros"](size))
    bound_e = rat.norm_bound(displacement)
    emitter = MacroEmitter(size, subject, code)
    plan = []
    summaries = []
    for item in generators:
        g, row, gamma = item["g"], item["row"], item["gamma"]
        need(rat.norm2(g) <= 1 and rat.norm2(row) < 4 * bound_e ** 2,
             "bounded rational generator norms")
        reconstructed_e = Matrix(subject["add"](reconstructed_e, [[x * y for y in row] for x in g]))
        reconstructed_t = Matrix(subject["add"](reconstructed_t,
            subject["mm"](rat.lower(g), rat.transpose(rat.lower(row)))))
        before = list(row)
        plan.extend(emitter.emit(list(range(size, 2 * size)), list(range(size)), g, row, gamma))
        need(before == row, "source vector division preserves original coefficient row")
        summaries.append({"column": item["column"], "scale": str(item["scale"]),
                          "scale_exponent": item["scale_exponent"], "gamma": str(gamma),
                          "g": [x.record() for x in g], "row": [x.record() for x in row]})
    need(reconstructed_e == displacement and reconstructed_t == matrix, "exact Stein and Toeplitz-product reconstruction")
    need(emitter.calls == ["triangle", "shear", "inverse", "shear"] * rank, "actual macro call sequence")
    expected = Matrix(subject["block"](subject["eye"](size), subject["zeros"](size),
                                      matrix, subject["eye"](size)))
    prefix = Matrix(subject["eye"](2 * size))
    inverse_prefix = Matrix(subject["eye"](2 * size))
    identity = Matrix(subject["eye"](2 * size))
    prefix_bound = 2 + 4 * size + 4 * rank * size * bound_e + 32 * size * bound_e
    peak = rat.frobenius2(prefix)
    for gate in plan:
        prefix = Matrix(subject["mm"](gate, prefix))
        inverse_prefix = Matrix(subject["mm"](inverse_prefix, subject["inv"](gate)))
        need(subject["mm"](prefix, inverse_prefix) == identity, "exact macro inverse-prefix identity")
        peak = max(peak, rat.frobenius2(prefix), rat.frobenius2(inverse_prefix))
        need(peak <= prefix_bound ** 2, "certified macro norm envelope")
    need(prefix == expected, "actual source macro endpoint and dirty-source restoration")
    polynomial_height = 4096 * (size + 1) ** 6 * (heights["input_height"] + 1)
    need(heights["max_observed_height"] <= polynomial_height, "polynomial generator height envelope")
    return {"label": label, "size": size, "rank": rank, "input_sha256": digest(matrix),
            "stein_sha256": digest(displacement), "generators": summaries, "heights": heights,
            "declared_height_bound": polynomial_height, "macro_stages": len(plan),
            "prefix_norm_bound": str(prefix_bound), "observed_frobenius_squared": str(peak),
            "endpoint_sha256": digest(prefix)}, plan, expected


def controls(subject, code):
    controls = []
    tiny = Matrix([[C(Q(1, 2 ** 200)), C()], [C(), C(Q(1, 2 ** 200))]])
    row, plan, wanted = one_case("tiny-control", tiny, subject, code)
    need(row["rank"] == 1 and Q(1, 2 ** 200) < Q(1, 10 ** 11), "tiny exact pivot below source SVD cutoff")
    need(Matrix(subject["eye"](4)) != wanted, "dropping tiny term changes exact endpoint")
    controls.append("tiny-nonzero-rank")
    complex_matrix = Matrix([[C(Q(1, 16)), C(0, Q(1, 16))], [C(), C(Q(1, 16))]])
    record, plan, wanted = one_case("complex-control", complex_matrix, subject, code)
    item = record["generators"][0]
    g = Vector(C(Q(x[0]), Q(x[1])) for x in item["g"])
    wrong_row = Vector(C(Q(x[0]), -Q(x[1])) for x in item["row"])
    emitter = MacroEmitter(2, subject, code)
    wrong = emitter.emit([2, 3], [0, 1], g, wrong_row, Q(item["gamma"]))
    actual = Matrix(subject["eye"](4))
    for step in wrong:
        actual = Matrix(subject["mm"](step, actual))
    need(actual != wanted, "conjugated coefficient row rejects")
    for label, altered in (("omitted-compensation", plan[:-1]),
                           ("omitted-source-restoration", plan[:2] + plan[3:])):
        actual = Matrix(subject["eye"](4))
        for step in altered:
            actual = Matrix(subject["mm"](step, actual))
        need(actual != wanted, label)
        controls.append(label)
    controls.append("complex-row-conjugation")
    controls.append(rejected(lambda: rat.norm_scale(Q(0)), "zero residual normalization"))
    controls.append(rejected(lambda: C(0.5), "floating input"))
    need(canonical({"rank": 1}) != canonical({"rank": True}), "typed receipt comparison")
    return controls + ["typed-receipt"]


def run():
    sources = authenticate()
    subject = load_subject()
    code, ast_hash = macro_template()
    cases, source_trace = collect_shears(subject)
    epsilon = Q(1, 2 ** 200)
    cases += [("zero", Matrix([[C(), C()], [C(), C()]])),
              ("scalar", Matrix([[C(Q(1, 32))]])),
              ("tiny-diagonal", Matrix([[C(epsilon), C()], [C(), C(epsilon)]])),
              ("near-dependent-columns", Matrix([[C(1), C(1)], [C(), C(1 + epsilon)]])),
              ("complex-row", Matrix([[C(Q(1, 16)), C(0, Q(1, 16))], [C(), C(Q(1, 16))]])),
              ("large-scale", Matrix([[C(2 ** 80), C(2 ** 80)], [C(), C(2 ** 80)]]))]
    records = [one_case(label, matrix, subject, code)[0] for label, matrix in cases]
    return {"schema_version": 1, "scope": "rational coefficient generation and exact source macro replay",
            "sources": sources, "macro_ast_sha256": ast_hash, "source_schur_trace": source_trace,
            "cases": records, "controls": controls(subject, code),
            "fft_or_parity_gate_execution": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = run()
    path = HERE / "RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), "complete typed receipt")
    print(json.dumps({"status": "PASS_RATIONAL_STEIN_GENERATORS", "cases": len(result["cases"]),
                      "generators": sum(x["rank"] for x in result["cases"]),
                      "macro_stages": sum(x["macro_stages"] for x in result["cases"]),
                      "result_sha256": sha256(canonical(result)).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
