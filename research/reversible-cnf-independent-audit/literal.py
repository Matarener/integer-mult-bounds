"""Literal rational endpoint checks for the restricted five-role CNF reduction.

Hiroki KUMAZAKI with substantial OpenAI Codex assistance. Apache-2.0.

Independent implementation: no predecessor compiler, evaluator, phase helper,
or arithmetic implementation is imported.  This interpreter accepts real
identity-affine diagonal signs, not the general native affine/quadratic
language.  A separate strict check verifies the compiler's coordinate Z
alphabet.  Every matrix column is an independent dirty input.
"""

from fractions import Fraction
import re


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rational(value):
    """Parse exact real coefficients; never silently round a JSON float."""
    if type(value) is int or isinstance(value, Fraction):
        return Fraction(value)
    if isinstance(value, str) and re.fullmatch(r"[+-]?[0-9]+(?:/[+-]?[0-9]+)?", value):
        try:
            return Fraction(value)
        except (ValueError, ZeroDivisionError) as error:
            raise ValueError("invalid rational coefficient") from error
    raise ValueError("explicit rational coefficient required")


def permutation_matrix(images):
    """Images encode destination(image[source]); columns are source inputs."""
    need(isinstance(images, (list, tuple)) and len(images) == 5,
         "five permutation images required")
    need(all(type(value) is int for value in images) and sorted(images) == list(range(5)),
         "permutation images must be exactly 0..4")
    result = [[Fraction(0) for _ in range(5)] for _ in range(5)]
    for source, destination in enumerate(images):
        result[destination][source] = Fraction(1)
    return result


def _signs(problem, addresses):
    n = problem["axes"]
    need(type(n) is int and n >= 1, "positive integral axis count")
    need(isinstance(addresses, (tuple, list)) and len(addresses) >= 1,
         "positive-width tensor address tuple required")
    need(all(type(address) is int and 0 <= address < 2**n for address in addresses),
         "tensor address outside the declared axes")
    generators = problem["generators"]
    need(isinstance(generators, dict), "native generator dictionary required")
    recipe_fields = {"matrix_rows", "offset", "phase", "linear_Z4", "quadratic_rows"}
    result = {}
    for name, recipe in generators.items():
        need(isinstance(name, str) and bool(name), "opaque generator name")
        need(isinstance(recipe, dict) and set(recipe) == recipe_fields,
             "exact native recipe fields required")
        for field in ("matrix_rows", "linear_Z4", "quadratic_rows"):
            need(isinstance(recipe[field], list) and len(recipe[field]) == n
                 and all(type(value) is int for value in recipe[field]),
                 "integral native recipe dimension")
        need(recipe["matrix_rows"] == [2**i for i in range(n)]
             and type(recipe["offset"]) is int and recipe["offset"] == 0,
             "diagonal sign generator must have the identity affine map")
        need(type(recipe["phase"]) is int and recipe["phase"] in (0, 2),
             "real diagonal sign requires an even constant phase")
        need(recipe["quadratic_rows"] == [0] * n,
             "CNF generator must have zero quadratic phase")
        linear = recipe["linear_Z4"]
        need(all(value in (0, 2) for value in linear),
             "real diagonal sign requires even linear phases")

        # Evaluate the recipe on each literal address.  Neither the generator
        # name nor a claimed Boolean variable index is used to choose the sign.
        exponent = 0
        for address in addresses:
            bits = [(address // (2**i)) % 2 for i in range(n)]
            phase = recipe["phase"] + sum(linear[i] * bits[i] for i in range(n))
            for i in range(n):
                for j in range(i + 1, n):
                    phase += 2 * bits[i] * bits[j] * ((recipe["quadratic_rows"][i] // (2**j)) % 2)
            exponent += phase
        exponent %= 4
        need(exponent in (0, 2), "non-real native sign outside this interpreter")
        result[name] = Fraction(1 if exponent == 0 else -1)
    return result


def strict_standard_generators(problem):
    """Verify the unmutated compiler emits every primitive coordinate Z once.

    Generator names remain opaque.  This is deliberately separate from the
    endpoint interpreter, which also evaluates constant or multiplied signs
    so a changed recipe can produce a literal incorrect endpoint.
    """
    need(isinstance(problem, dict) and {"axes", "generators"} <= set(problem),
         "standard-generator problem fields")
    _signs(problem, (0,))
    n = problem["axes"]
    need(len(problem["generators"]) == n, "one standard generator per axis")
    represented_axes = []
    for recipe in problem["generators"].values():
        need(recipe["phase"] == 0, "standard Z has zero constant phase")
        linear = recipe["linear_Z4"]
        need(linear.count(2) == 1, "standard Z has exactly one nonzero linear phase")
        represented_axes.append(linear.index(2))
    need(sorted(represented_axes) == list(range(n)), "standard Z recipes cover every axis once")
    return True


def endpoint(problem, tuple_of_addresses):
    """Return the complete five-by-five dirty endpoint on one tensor address.

    Reference instructions are not subtracted: callers can evaluate them by
    copying the problem and placing its reference list in the program field.
    Accepted diagonal generators preserve every address, so distinct tensor
    addresses form independent invariant blocks of the complete operator.
    """
    need(isinstance(problem, dict)
         and set(problem) == {"axes", "roles", "generators", "program", "reference"},
         "exact reduction problem fields required")
    need(type(problem["roles"]) is int and problem["roles"] == 5, "exactly five dirty roles")
    need(isinstance(problem["program"], list) and isinstance(problem["reference"], list),
         "program and reference instruction lists required")
    signs = _signs(problem, tuple_of_addresses)
    matrix = permutation_matrix((0, 1, 2, 3, 4))
    for instruction in problem["program"]:
        need(isinstance(instruction, dict), "instruction object required")
        op = instruction.get("op")
        if op == "apply":
            need(set(instruction) == {"op", "dst", "generator"}, "unary apply fields")
        elif op == "swap":
            need(set(instruction) == {"op", "src", "dst"}, "swap fields")
        elif op in ("add", "query"):
            required = {"op", "src", "dst"} | ({"generator"} if op == "query" else set())
            need(required <= set(instruction) <= required | {"coefficient"},
                 "additive instruction fields")
        else:
            raise ValueError("operation outside the reversible CNF alphabet")
        dst = instruction["dst"]
        need(type(dst) is int and 0 <= dst < 5, "destination role extent")
        if op != "apply":
            src = instruction["src"]
            need(type(src) is int and 0 <= src < 5 and src != dst,
                 "binary instruction requires distinct roles")
        if op in ("query", "apply"):
            name = instruction["generator"]
            need(isinstance(name, str) and name in signs, "unknown native generator")
            sign = signs[name]
        if op == "swap":
            matrix[src], matrix[dst] = matrix[dst], matrix[src]
        elif op == "apply":
            matrix[dst] = [sign * value for value in matrix[dst]]
        else:
            coefficient = rational(instruction.get("coefficient", 1))
            if op == "query":
                coefficient *= sign
            matrix[dst] = [destination + coefficient * source
                           for destination, source in zip(matrix[dst], matrix[src])]
    return matrix


def direct_clauses(clauses, assignment):
    """Ordinary CNF truth evaluation on the bits of a nonnegative integer."""
    need(type(assignment) is int and assignment >= 0, "nonnegative Boolean assignment")
    need(isinstance(clauses, (list, tuple)), "clause sequence required")
    answer = True
    for clause in clauses:
        need(isinstance(clause, (list, tuple)) and len(clause) <= 3,
             "at most three literals per clause")
        satisfied = False
        for literal in clause:
            need(type(literal) is int and literal != 0, "nonzero integral literal")
            bit = bool((assignment // (2 ** (abs(literal) - 1))) % 2)
            satisfied = satisfied or (bit if literal > 0 else not bit)
        answer = answer and satisfied
    return answer


def run_local_controls():
    """Finite complete-input controlled-swap checks, separate from CNF tests."""
    recipe = {"matrix_rows": [1], "offset": 0, "phase": 0,
              "linear_Z4": [2], "quadratic_rows": [0]}
    # Opaque name deliberately disagrees with the source's Z1 spelling.
    generator = "literal-phase-recipe"
    tuples = ((0,), (1,), (1, 1), (0, 1), (1, 1, 1), (1, 0, 1))
    cases = 0
    for i in range(5):
        for j in range(5):
            if i == j:
                continue
            program = [{"op": "add", "src": j, "dst": i, "coefficient": -1},
                       {"op": "add", "src": i, "dst": j, "coefficient": "1/2"},
                       {"op": "query", "src": i, "dst": j, "generator": generator,
                        "coefficient": "-1/2"},
                       {"op": "apply", "dst": i, "generator": generator},
                       {"op": "add", "src": j, "dst": i}]
            problem = {"axes": 1, "roles": 5, "generators": {generator: recipe},
                       "program": program, "reference": []}
            strict_standard_generators(problem)
            for addresses in tuples:
                images = list(range(5))
                if sum(addresses) % 2:
                    images[i], images[j] = images[j], images[i]
                need(endpoint(problem, addresses) == permutation_matrix(images),
                     "complete dirty controlled swap endpoint")
                cases += 1
    need(direct_clauses([], 0), "empty conjunction must be true")
    need(not direct_clauses([[]], 0), "empty clause must be false")
    need(all(direct_clauses([[1, -1]], x) for x in range(2)), "tautological clause")
    need(not any(direct_clauses([[1], [-1]], x) for x in range(2)), "contradictory clauses")
    return {"ordered_role_pairs": 20, "tensor_tuples_per_pair": len(tuples),
            "complete_five_column_endpoints": cases, "tensor_widths": [1, 2, 3],
            "opaque_generator_name_control": True, "Boolean_boundary_controls": 4}


if __name__ == "__main__":
    import json
    print(json.dumps(run_local_controls(), sort_keys=True))
