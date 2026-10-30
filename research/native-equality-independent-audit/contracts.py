"""Independent exact checks of the complete-word contract in PR5588 §§4–5.

Hiroki KUMAZAKI, with substantial OpenAI Codex assistance. Apache-2.0.

This module uses its own dense Fraction arithmetic and imports no predecessor
implementation.  Its finite examples support, but do not prove, the quantified
rank inequality.  The chosen native operation is H tensor H, whose entries are
rational although the entries of the one-column normalized Hadamard are not.
"""

from fractions import Fraction as F


def need(condition, message):
    if not condition:
        raise ValueError(message)


def zeros(rows, cols):
    return [[F(0) for _ in range(cols)] for _ in range(rows)]


def eye(size):
    result = zeros(size, size)
    for i in range(size):
        result[i][i] = F(1)
    return result


def shape(matrix):
    need(bool(matrix) and bool(matrix[0]), "empty matrix")
    width = len(matrix[0])
    need(all(len(row) == width for row in matrix), "ragged matrix")
    return len(matrix), width


def multiply(left, right):
    rows, inner = shape(left)
    inner_right, cols = shape(right)
    need(inner == inner_right, "matrix product shape")
    result = zeros(rows, cols)
    for i in range(rows):
        for k, value in enumerate(left[i]):
            if value:
                for j, other in enumerate(right[k]):
                    if other:
                        result[i][j] += value * other
    return result


def transpose(matrix):
    shape(matrix)
    return [list(row) for row in zip(*matrix)]


def scale(matrix, scalar):
    return [[F(scalar) * value for value in row] for row in matrix]


def rank(matrix):
    rows, cols = shape(matrix)
    work = [[F(value) for value in row] for row in matrix]
    pivot_row = 0
    for col in range(cols):
        pivot = next((i for i in range(pivot_row, rows)
                      if work[i][col]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][col]
        work[pivot_row] = [value / divisor for value in work[pivot_row]]
        for i in range(pivot_row + 1, rows):
            factor = work[i][col]
            if factor:
                work[i] = [value - factor * base for value, base
                           in zip(work[i], work[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def tensor(left, right):
    return [[a * b for a in row_left for b in row_right]
            for row_left in left for row_right in right]


def equality_cut(registers):
    # Two binary columns, ordered 00, 01, 10, 11 in every register.
    return [i % 4 in (0, 3) for i in range(4 * registers)]


def cut_rank(matrix, output_cut, input_cut):
    rows, cols = shape(matrix)
    need((rows, cols) == (len(output_cut), len(input_cut)), "cut shape")
    block = [[matrix[i][j] for j in range(cols) if input_cut[j]]
             for i in range(rows) if not output_cut[i]]
    return rank(block)


def install_block(matrix, output_register, input_register, block):
    need(shape(block) == (4, 4), "field block shape")
    for i in range(4):
        for j in range(4):
            matrix[4 * output_register + i][4 * input_register + j] = block[i][j]


def register_gate(kind, dst, src=None, coefficient=1, native=None):
    """Four registers: x, y, independent dirty d, owned temporary t."""
    result = eye(16)
    need(0 <= dst < 4, "destination")
    if kind in ("copy", "add"):
        need(src is not None and 0 <= src < 4 and src != dst, "source")
    if kind in ("copy", "clear", "native"):
        for row in range(4 * dst, 4 * dst + 4):
            result[row] = [F(0)] * 16
    if kind == "copy":
        install_block(result, dst, src, eye(4))
    elif kind == "add":
        install_block(result, dst, src, scale(eye(4), coefficient))
    elif kind == "native":
        install_block(result, dst, dst, native)
    else:
        need(kind == "clear", "unknown gate")
    return result


def chronological(native):
    # Implement y += T x, then x += T y, using an arbitrary dirty d.
    # In each shear the temporary first queries source+d; a second query
    # removes T d.  Thus the third paid input depends on the first response.
    operations = []
    for dst, src in ((1, 0), (0, 1)):
        operations.extend([
            ("copy", 3, src, 1),
            ("add", 3, 2, 1),
            ("native", 3, None, 1),
            ("add", dst, 3, 1),
            ("clear", 3, None, 1),
            ("copy", 3, 2, 1),
            ("native", 3, None, 1),
            ("add", dst, 3, -1),
            ("clear", 3, None, 1),
        ])
    initial = zeros(16, 12)
    for i in range(12):
        initial[i][i] = F(1)
    state = initial
    in_cut, out_cut = equality_cut(3), equality_cut(4)
    initial_rank = cut_rank(initial, out_cut, in_cut)
    need(initial_rank == 0, "ordinary independent initial state")
    charged = 0
    prefix_ranks = [initial_rank]
    prefix_bounds = [initial_rank]
    gate_ranks = []
    paid_inputs = []
    dirty_omitted = initial
    dirty_control_removed = False
    for index, (kind, dst, src, coefficient) in enumerate(operations):
        gate = register_gate(kind, dst, src, coefficient, native)
        gate_rank = cut_rank(gate, out_cut, out_cut)
        gate_ranks.append(gate_rank)
        need(gate_rank == (1 if kind == "native" else 0), "gate crossing rank")
        if kind == "native":
            paid_inputs.append([row[:] for row in state[12:16]])
        before_rank = cut_rank(state, out_cut, in_cut)
        state = multiply(gate, state)
        after_rank = cut_rank(state, out_cut, in_cut)
        need(after_rank <= before_rank + gate_rank, "one-step subadditivity")
        charged += gate_rank
        need(after_rank <= initial_rank + charged, "complete prefix bound")
        prefix_ranks.append(after_rank)
        prefix_bounds.append(initial_rank + charged)
        # Omit exactly the first dirty-response subtraction, leaving all
        # later gates unchanged; endpoint comparison must catch its leakage.
        if index == 7:
            dirty_control_removed = True
        else:
            dirty_omitted = multiply(gate, dirty_omitted)
    expected = zeros(16, 12)
    for dst, src, block in ((0, 0, scale(eye(4), 2)), (0, 1, native),
                            (1, 0, native), (1, 1, eye(4)),
                            (2, 2, eye(4))):
        install_block(expected, dst, src, block)
    need(state == expected, "literal complete endpoint")
    need(dirty_control_removed and dirty_omitted != expected,
         "missing dirty uncompute was undetected")
    need(any(dirty_omitted[i][j] for i in range(8) for j in range(8, 12)),
         "dirty mutation must leak an independent dirty coordinate")
    # The third query input is y_original + T*x_original + d_original.
    expected_feedback = [native[i] + eye(4)[i] + eye(4)[i] for i in range(4)]
    need(paid_inputs[2] == expected_feedback, "paid response feedback")
    need(prefix_ranks[3] == 1, "first paid overwrite must cross the cut")
    mutant_prefix_budget = initial_rank + sum(gate_ranks[:2])
    need(mutant_prefix_budget == 0 and prefix_ranks[3] > mutant_prefix_budget,
         "omitting the first paid charge must fail the prefix bound")
    need(cut_rank(state, out_cut, in_cut) == 2, "complete two-shear rank")
    # CLEAR is substantive: omitting the final one retains T*d in t.
    before_last = initial
    for kind, dst, src, coefficient in operations[:-1]:
        before_last = multiply(register_gate(kind, dst, src, coefficient, native),
                               before_last)
    need(before_last != expected and before_last[12:16] != zeros(4, 12),
         "missing final CLEAR was undetected")
    return {
        "field_dimension": 4, "original_and_dirty_input_columns": 12,
        "owned_zero_registers": 1, "operations": len(operations),
        "paid_overwrites": len(paid_inputs), "feedback_paid_input_index": 3,
        "prefix_cut_ranks": prefix_ranks, "prefix_bounds": prefix_bounds,
        "endpoint": ["2*x + T*y", "T*x + y", "d", "0"],
        "endpoint_cut_rank": 2,
        "missing_first_charge": {"observed_prefix_rank": prefix_ranks[3],
                                 "mutant_prefix_budget": mutant_prefix_budget},
        "rejected_controls": ["omit dirty-response subtraction",
                              "omit final CLEAR", "omit first paid crossing charge"],
    }


def paid_update_controls(native):
    """Check overwrite-independent additive queries, including singular updates."""
    coefficients = (F(0), F(1), F(-1), F(1, 2), F(-3, 2))
    results = []
    for coefficient in coefficients:
        gate = eye(8)
        install_block(gate, 1, 0, scale(native, coefficient))
        # Literal all-column semantics: the original destination is retained,
        # while only the source contributes through the paid operator.
        expected = [[F(i == j) + (coefficient * native[i - 4][j]
                                 if i >= 4 and j < 4 else F(0))
                     for j in range(8)] for i in range(8)]
        need(gate == expected, "two-bank additive query endpoint")
        cross = cut_rank(gate, equality_cut(2), equality_cut(2))
        need(cross == int(bool(coefficient)), "scaled additive query cut rank")
        need(rank(gate) == 8, "additive query retains both independent banks")
        # Same-register updates may be singular.  The identity has no crossing
        # block, so their crossing rank is still that of c*T.
        self_update = [[F(i == j) + coefficient * native[i][j]
                        for j in range(4)] for i in range(4)]
        self_cross = cut_rank(self_update, equality_cut(1), equality_cut(1))
        need(self_cross == int(bool(coefficient)), "self-update cut rank")
        full_rank = rank(self_update)
        need(full_rank == (2 if coefficient in (F(1), F(-1)) else 4),
             "self-update invertibility boundary")
        results.append({"coefficient": str(coefficient),
                        "two_bank_cut_rank": cross,
                        "self_update_cut_rank": self_cross,
                        "self_update_full_rank": full_rank})
    return {"two_bank_cases": len(coefficients),
            "self_update_cases": len(coefficients),
            "two_bank_independent_input_columns_per_case": 8,
            "cases": results}


def cached_history(native):
    # Available fields are x, T*x, T*x, all from the same independent x.
    joined = eye(4) + [row[:] for row in native] + [row[:] for row in native]
    cuts_in, cuts_out = equality_cut(1), equality_cut(3)
    joint = cut_rank(joined, cuts_out, cuts_in)
    separate = [cut_rank(block, cuts_in, cuts_in) for block in (eye(4), native, native)]
    need(joint == 1 and sum(separate) == 2, "dependent cached rows")
    select = zeros(4, 12)
    install_block(select, 0, 1, eye(4))
    need(cut_rank(select, cuts_in, cuts_out) == 0, "ordinary cache selection")
    endpoint = multiply(select, joined)
    need(endpoint == native, "cache alone supplies the exact native target")
    target_rank = cut_rank(endpoint, cuts_in, cuts_in)
    need(target_rank <= joint and target_rank > 0,
         "omitting initial crossing rank must give a false obstruction")
    return {"available_rows": ["x", "T*x", "T*x"],
            "joint_cut_rank": joint, "sum_individual_cut_ranks": sum(separate),
            "additional_paid_calls": 0, "exact_target_cut_rank": target_rank,
            "rejected_control": "omit initial availability map J"}


def endpoint_codes(native):
    # Independently invertible register codes commute with the equality cut.
    left = tensor([[F(1), F(1)], [F(0), F(2)]], eye(4))
    right = tensor([[F(1), F(0)], [F(1, 2), F(1)]], eye(4))
    target = tensor(eye(2), native)
    cut = equality_cut(2)
    need(rank(left) == 8 and rank(right) == 8, "invertible ordinary codes")
    need(cut_rank(left, cut, cut) == cut_rank(right, cut, cut) == 0,
         "ordinary codes cross the cut")
    need(cut_rank(target, cut, cut) == 2, "uncoded independent targets")
    need(cut_rank(multiply(multiply(left, target), right), cut, cut) == 2,
         "ordinary codes change cut rank")
    small = scale(native, F(1, 8))
    need(multiply(transpose(small), small) == scale(eye(4), F(1, 64)),
         "exact scaled-target singular values")
    need(cut_rank(small, equality_cut(1), equality_cut(1)) == 1,
         "nonunitary scalar code changes rank")
    return {"coded_target_cut_rank": 2, "left_and_right_code_ranks": [8, 8],
            "scaled_target_cut_rank": 1, "zero_program_paid_calls": 0,
            "zero_program_operator_error": "1/8",
            "rejected_control": "retain unit error floor after nonunitary scaling"}


def changed_alphabet():
    # CNOT between the two tensor columns is monomial on the four-coordinate
    # field, but is not an allowed repeated one-column map M tensor M.
    permutation = [0, 1, 3, 2]
    cnot = zeros(4, 4)
    for source, destination in enumerate(permutation):
        cnot[destination][source] = F(1)
    cut = equality_cut(1)
    need(multiply(transpose(cnot), cnot) == eye(4), "CNOT permutation")
    need(cut_rank(cnot, cut, cut) == 1, "inter-column map crossing")
    swap = tensor([[F(0), F(1)], [F(1), F(0)]],
                  [[F(0), F(1)], [F(1), F(0)]])
    diagonal = tensor([[F(1), F(0)], [F(0), F(2)]],
                      [[F(1), F(0)], [F(0), F(2)]])
    need(cut_rank(swap, cut, cut) == cut_rank(diagonal, cut, cut) == 0,
         "one-column monomial positive controls")
    return {"inter_column_permutation": permutation, "crossing_rank": 1,
            "repeated_one_column_positive_controls": 2,
            "rejected_control": "grant inter-column CNOT as a zero-rank free map"}


def run():
    native = [[F((-1) ** ((i & j).bit_count()), 2) for j in range(4)]
              for i in range(4)]
    need(multiply(native, native) == eye(4), "Hadamard tensor square")
    need(multiply(transpose(native), native) == eye(4), "native unitarity")
    return {"chronological": chronological(native),
            "paid_updates": paid_update_controls(native),
            "cached_history": cached_history(native),
            "endpoint_codes": endpoint_codes(native),
            "changed_alphabet": changed_alphabet()}


if __name__ == "__main__":
    import json
    print(json.dumps(run(), sort_keys=True, indent=2))
