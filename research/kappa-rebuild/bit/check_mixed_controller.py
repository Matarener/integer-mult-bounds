#!/usr/bin/env python3
"""Independent regular-representation check of the strongest BIT controller.

No constructor or formal-polynomial matrix code is imported.  The literal
program is executed on every basis input of a faithful finite regular
representation, with pointwise XOR and explicit address permutations.
Apache-2.0; substantial OpenAI assistance. This is finite evidence only.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import json
import time

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def run(receipt):
    data = json.loads(receipt.read_text())
    p = data["strongest_pairs"]
    case = next(row for row in data["candidates"] if row["pairs"] == p)
    require(p == 3, "This bounded independent replay is for the seven-stage candidate")
    n = 2*p
    group_size = 1 << (case["stages"]+1)
    endpoint = case["factorization"]["diagonal_monomials"]
    before = case["factorization"]["right_program"]
    after = case["factorization"]["left_program"]
    events = case["physical_events"]

    def execute(skip_prefix=None, reverse_local=None, omitted_idle=None):
        state = [[1 << (role*group_size+address) for address in range(group_size)]
                 for role in range(n)]
        def scalar(op, d, s):
            if op == "SWAP":
                state[d], state[s] = state[s], state[d]
            else:
                require(op == "ADD", "Literal scalar opcode")
                state[d] = [a ^ b for a, b in zip(state[d], state[s])]
        for index, (op, d, s) in enumerate(before):
            if index != skip_prefix:
                scalar(op, d, s)
        for index, event in enumerate(events):
            if event[0] == "LOCAL":
                _, stage, pair, reverse = event
                if stage == reverse_local:
                    reverse = not reverse
                x, y = 2*pair, 2*pair+1
                if reverse:
                    x, y = y, x
                source = state[x]
                state[y] = [state[y][a] ^ source[a ^ 1] for a in range(group_size)]
                block = 1 << (stage+1)
                state[x] = [state[x][a ^ block] for a in range(group_size)]
                state[y] = [state[y][a ^ block] for a in range(group_size)]
            elif event[0] == "IDLE":
                if index != omitted_idle:
                    _, pair, mask = event
                    for role in (2*pair, 2*pair+1):
                        state[role] = [state[role][a ^ mask] for a in range(group_size)]
            else:
                scalar(*event)
        for op, d, s in after:
            scalar(op, d, s)
        errors = 0
        rows = 0
        for role, shift in enumerate(endpoint):
            for address, value in enumerate(state[role]):
                expected = 1 << (role*group_size+(address ^ shift))
                difference = value ^ expected
                errors += difference.bit_count()
                rows += bool(difference)
        return errors, rows

    errors, rows = execute()
    require(errors == rows == 0, "Every input column of the physical endpoint")
    controls = {}
    for index in range(len(before)):
        wrong = execute(skip_prefix=index)
        require(wrong[0] > 0, "Boundary adapter omission rejected")
        controls[f"omit_input_adapter_{index}"] = dict(wrong_coefficients=wrong[0], wrong_rows=wrong[1])
    for stage in range(case["stages"]):
        wrong = execute(reverse_local=stage)
        require(wrong[0] > 0, "Local orientation corruption rejected")
        controls[f"reverse_local_orientation_{stage}"] = dict(wrong_coefficients=wrong[0], wrong_rows=wrong[1])
    for index, event in enumerate(events):
        if event[0] == "IDLE":
            wrong = execute(omitted_idle=index)
            require(wrong[0] > 0, "Remaining idle field must be paid")
            controls[f"omit_remaining_idle_{index}"] = dict(wrong_coefficients=wrong[0], wrong_rows=wrong[1])
    local = {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}
    paid = Counter({r:case["stages"]*count for r, count in local.items()})
    targets = Counter({8:439*case["stages"]})
    for event in events:
        if event[0] == "IDLE":
            paid[7] += 2*111*(event[2] >> 1).bit_count()
    for term in endpoint:
        targets[(term & 1)+7*(term >> 1).bit_count()] += 111
    require(dict(sorted(paid.items())) == {int(k):v for k, v in case["paid"].items()}, "Literal whole paid profile")
    require(dict(sorted(targets.items())) == {int(k):v for k, v in case["targets"].items()}, "Actual endpoint job credit")
    require(max(paid) < min(targets), "Strict contraction")
    require(sum(r*n for r, n in targets.items())-sum(r*n for r, n in paid.items()) == 225,
            "Independent complete rank balance")
    return dict(schema="independent-bit-regular-representation/1", status="PASS",
                input_receipt_sha256=sha256(receipt.read_bytes()).hexdigest(),
                checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                physical_data_fields=n, regular_group_order=group_size,
                arbitrary_function_input_columns=n*group_size,
                scalar_matrix_coefficients_compared=(n*group_size)**2,
                nonzero_wrong_coefficients=0, paid=dict(sorted(paid.items())),
                targets=dict(sorted(targets.items())), controls=controls,
                interpretation="Faithful regular representation validates the exact formal operator, not a sample of characters.",
                not_checked=["Full GL cover routing", "Weighted output normalizers", "All-size recursion", "Outer multiplication"],
                new_kappa=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=HERE/"MIXED-PRODUCTIVE-BIT.json")
    parser.add_argument("--output", type=Path, default=HERE/"MIXED-CONTROLLER-INDEPENDENT.json")
    args = parser.parse_args()
    start = time.monotonic()
    result = run(args.input)
    result["seconds"] = time.monotonic()-start
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in ("status", "arbitrary_function_input_columns", "scalar_matrix_coefficients_compared", "seconds")}))


if __name__ == "__main__":
    main()
