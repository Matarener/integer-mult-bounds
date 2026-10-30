"""Construct and check a 29-XOR realization of the fixed R420 block-4 map.

The target and wire order are the specification from Cinna Davis's PR1383.
The new word and its bidirectional reduction are produced by Nick Petalas.
Apache-2.0. No predecessor program is imported or replayed.
"""

import hashlib
import json
import random


WIDTH = 12
TARGET = (4092, 4085, 3951, 3967, 511, 1535,
          2559, 3326, 3743, 3855, 4080, 4059)
INPUT_WIRES = (23, 110, 102, 28, 46, 38, 87, 92, 55, 60, 78, 70)
WORD = ((5, 6), (7, 8), (1, 3), (1, 2), (6, 2), (3, 0), (1, 9),
        (2, 0), (0, 8), (9, 5), (9, 10), (7, 4), (0, 10), (6, 8),
        (0, 11), (9, 11), (9, 7), (8, 1), (8, 9), (1, 0), (0, 8),
        (7, 1), (6, 7), (2, 9), (3, 2), (5, 1), (11, 0), (10, 0),
        (4, 5))
OUTPUT_TO_WIRE = (3, 2, 5, 4, 0, 10, 11, 8, 7, 1, 9, 6)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(word, assignment, target):
    require(len(target) == WIDTH, "target width")
    require(all(type(x) is int and 0 <= x < 1 << WIDTH for x in target),
            "target entry")
    require(len(assignment) == WIDTH, "assignment width")
    require(all(type(x) is int for x in assignment), "assignment type")
    require(sorted(assignment) == list(range(WIDTH)), "assignment permutation")
    require(0 < len(word) <= 150, "word length")
    for gate in word:
        require(len(gate) == 2, "gate arity")
        require(all(type(x) is int and 0 <= x < WIDTH for x in gate),
                "gate index")
        require(gate[0] != gate[1], "self addition")


def columns(rows):
    return [sum(((rows[i] >> j) & 1) << i for i in range(WIDTH))
            for j in range(WIDTH)]


def next_move(rows, seen, rng):
    best = -WIDTH
    moves = []
    for side, vectors in enumerate((rows, columns(rows))):
        for dest in range(WIDTH):
            for source in range(WIDTH):
                if dest == source:
                    continue
                gain = vectors[dest].bit_count()
                gain -= (vectors[dest] ^ vectors[source]).bit_count()
                if gain > best:
                    best, moves = gain, [(side, dest, source)]
                elif gain == best:
                    moves.append((side, dest, source))
    rng.shuffle(moves)
    for side, dest, source in moves:
        changed = list(rows)
        if side == 0:
            changed[dest] ^= changed[source]
        else:
            for i in range(WIDTH):
                changed[i] ^= ((changed[i] >> source) & 1) << dest
        if tuple(changed) not in seen:
            return side, dest, source, changed
    raise ValueError("no unseen best move")


def construct():
    """Replay only the first trajectory, with at most 150 reduction moves."""
    rows = list(TARGET)
    left, right, seen = [], [], set()
    rng = random.Random(0)
    for _ in range(151):
        if sum(x.bit_count() for x in rows) == WIDTH:
            assignment = tuple(x.bit_length() - 1 for x in rows)
            require(sorted(assignment) == list(range(WIDTH)), "not a permutation")
            word = right + [(assignment[d], assignment[s])
                            for d, s in reversed(left)]
            require(len(word) <= 150, "construction budget")
            return tuple(word), assignment
        require(len(left) + len(right) < 150, "construction exhausted")
        side, dest, source, rows = next_move(rows, seen, rng)
        seen.add(tuple(rows))
        if side == 0:
            left.append((dest, source))
        else:
            right.append((source, dest))
    raise ValueError("construction exhausted")


def matrix_rows(word, assignment):
    rows = [1 << i for i in range(WIDTH)]
    for dest, source in word:
        rows[dest] ^= rows[source]
    return tuple(rows[i] for i in assignment)


def boolean_run(bits, word):
    state = list(bits)
    for dest, source in word:
        state[dest] = (state[dest] + state[source]) % 2
    return state


def exhaustive_inputs():
    checked = 0
    for mask in range(1 << WIDTH):
        bits = [(mask >> i) & 1 for i in range(WIDTH)]
        expected = [sum(bits[j] for j in range(WIDTH) if (row >> j) & 1) % 2
                    for row in TARGET]
        state = boolean_run(bits, WORD)
        actual = [state[i] for i in OUTPUT_TO_WIRE]
        require(actual == expected, f"Boolean endpoint {mask}")
        # Load logical outputs on their assigned physical wires before inversion.
        inverse_input = [0] * WIDTH
        for i, wire in enumerate(OUTPUT_TO_WIRE):
            inverse_input[wire] = expected[i]
        require(boolean_run(inverse_input, reversed(WORD)) == bits,
                f"inverse endpoint {mask}")
        checked += 1
    return checked


def corruption_controls():
    deletions = reversals = 0
    for i, (dest, source) in enumerate(WORD):
        omitted = WORD[:i] + WORD[i + 1:]
        require(matrix_rows(omitted, OUTPUT_TO_WIRE) != TARGET, "deleted gate")
        deletions += 1
        reversed_gate = WORD[:i] + ((source, dest),) + WORD[i + 1:]
        require(matrix_rows(reversed_gate, OUTPUT_TO_WIRE) != TARGET,
                "reversed gate")
        reversals += 1
    identity_assignment = tuple(range(WIDTH))
    require(matrix_rows(WORD, identity_assignment) != TARGET, "missing assignment")
    changed = TARGET[:-1] + (TARGET[-1] ^ 1,)
    require(matrix_rows(WORD, OUTPUT_TO_WIRE) != changed, "changed target")
    return deletions, reversals, 2


def malformed_controls():
    cases = (
        ((), OUTPUT_TO_WIRE, TARGET),
        (WORD * 6, OUTPUT_TO_WIRE, TARGET),
        (((0,),), OUTPUT_TO_WIRE, TARGET),
        (((True, 1),), OUTPUT_TO_WIRE, TARGET),
        (((0, WIDTH),), OUTPUT_TO_WIRE, TARGET),
        (((1, 1),), OUTPUT_TO_WIRE, TARGET),
        (WORD, OUTPUT_TO_WIRE[:-1], TARGET),
        (WORD, (0,) * WIDTH, TARGET),
        (WORD, (True,) + OUTPUT_TO_WIRE[1:], TARGET),
        (WORD, OUTPUT_TO_WIRE, TARGET[:-1]),
        (WORD, OUTPUT_TO_WIRE, (1 << WIDTH,) + TARGET[1:]),
    )
    rejected = 0
    for word, assignment, target in cases:
        try:
            validate(word, assignment, target)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("malformed fixture accepted")
    return rejected


def main():
    validate(WORD, OUTPUT_TO_WIRE, TARGET)
    word, assignment = construct()
    require((word, assignment) == (WORD, OUTPUT_TO_WIRE), "construction drift")
    require(len(WORD) == 29 and len(WORD) < 51, "strict shortening")
    require(matrix_rows(WORD, OUTPUT_TO_WIRE) == TARGET, "matrix endpoint")
    checked = exhaustive_inputs()
    deletions, reversals, endpoint_controls = corruption_controls()
    malformed = malformed_controls()
    payload = {"target_rows": TARGET, "input_wires": INPUT_WIRES,
               "operations": WORD, "output_to_wire": OUTPUT_TO_WIRE}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    print("PASS_R420_BLOCK4_SHORT_WORD")
    print(f"gates={len(WORD)} cited_predecessor=51 local_saving={51 - len(WORD)} "
          f"inputs={checked} inverses={checked} workspace=0")
    print(f"deletions_rejected={deletions} directions_rejected={reversals} "
          f"endpoint_controls={endpoint_controls} malformed_rejected={malformed}")
    print(f"witness_sha256={digest} no_new_kappa")


if __name__ == "__main__":
    main()
