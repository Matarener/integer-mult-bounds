#!/usr/bin/env python3
"""Replay the row-model witnesses for the depth-four unsigned chain connector.

The chain calls are z_l += B_l z_{l-1} for l = 1..4 (z_0 = x immutable,
z_4 = y). A word over {1,2,3,4} is correct for c in characteristic m when it
restores z_1, z_2, z_3 and adds c B_4 B_3 B_2 B_1 x to y. Each witness is
stored as row-model data (lambda, rho, beta) from README Lemma 2. The verifier
evaluates the six congruences of Lemma 2, builds the word, and checks the word
directly, so a witness passes only if the lemma's prediction and the word agree.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
DEPTH = 4
M_MIN, M_MAX = 33, 64
INPUTS = ("research/universal-connector-boundary/README.md",)
PACKAGE_FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json",
                 "verify.py", "witnesses.json")
SEED = 4263
LEMMA_TRIALS = 4000


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parse(m: int, data: dict) -> tuple:
    """Validate one (lambda, rho, beta) record and pad it to m rows."""
    rows, rho = list(data["rows"]), list(data["rho"])
    beta = {int(b): int(k) for b, k in data["beta"].items()}
    require(len(rows) == len(rho) <= m, "row and rho lengths")
    rows += [0] * (m - len(rows))
    rho += [0] * (m - len(rho))
    require(all(m >= rows[i] >= rows[i + 1] >= 0 for i in range(m - 1)), "lambda shape")
    require(all(m >= rho[i] >= rho[i + 1] >= 0 for i in range(m - 1)), "rho shape")
    require(all(1 <= b <= m and k > 0 for b, k in beta.items()), "beta levels")
    require(sum(beta.values()) <= m, "beta budget")
    return rows, rho, beta


def beta_profile(m: int, beta: dict) -> list:
    """beta(p) = number of calls 4 with at least p calls 3 before them, p = 1..m."""
    return [sum(k for b, k in beta.items() if b >= p) for p in range(1, m + 1)]


def lemma_conditions(m: int, rows: list, rho: list, beta: dict) -> tuple:
    """README Lemma 2: the five vanishing sums and the predicted coefficient."""
    prof = beta_profile(m, beta)
    cum = [0]
    for v in prof:
        cum.append(cum[-1] + v)
    vanish = (sum(rows) % m, sum(rho) % m, sum(prof) % m,
              sum(r * l for r, l in zip(rho, rows)) % m,
              sum(cum[l] for l in rows) % m)
    coefficient = (-sum(r * cum[l] for r, l in zip(rho, rows))) % m
    return vanish, coefficient


def build_word(m: int, rows: list, rho: list, beta: dict) -> str:
    """Lemma 2's word: a 2/3 path below lambda, calls 1 and 4 at their levels."""
    col = [sum(1 for l in rows if l >= p) for p in range(1, m + 1)]
    twos_before = [m - h for h in col]  # f(p): calls 2 before the p-th call 3
    ones_at = {}  # a-level -> calls 1 with exactly a calls 2 before them
    for q in range(1, m + 1):
        k = rho[q - 1] - (rho[q] if q < m else 0)
        if k:
            ones_at[m - q] = ones_at.get(m - q, 0) + k
    ones_at[m] = ones_at.get(m, 0) + m - rho[0]
    fours_at = dict(beta)
    fours_at[0] = fours_at.get(0, 0) + m - sum(beta.values())
    out = ["1" * ones_at.get(0, 0), "4" * fours_at.get(0, 0)]
    n2 = 0
    for p in range(1, m + 1):
        while n2 < twos_before[p - 1]:
            n2 += 1
            out.append("2" + "1" * ones_at.get(n2, 0))
        out.append("3" + "4" * fours_at.get(p, 0))
    while n2 < m:
        n2 += 1
        out.append("2" + "1" * ones_at.get(n2, 0))
    return "".join(out)


def interval_counts(word: str, modulus: int) -> dict:
    """N[i..j] mod m: scattered occurrences of the subword i(i+1)...j."""
    count = {(i, j): 0 for i in range(1, DEPTH + 1) for j in range(i, DEPTH + 1)}
    for event in word:
        letter = int(event)
        require(1 <= letter <= DEPTH, "unknown letter")
        for i in range(letter, 0, -1):
            gain = 1 if i == letter else count[(i, letter - 1)]
            count[(i, letter)] = (count[(i, letter)] + gain) % modulus
    return count


def counts_correct(word: str, modulus: int, coefficient: int) -> bool:
    count = interval_counts(word, modulus)
    return all(v == (coefficient % modulus if iv == (1, DEPTH) else 0)
               for iv, v in count.items())


def matrix_correct(word: str, modulus: int, coefficient: int) -> bool:
    """Product of I + e_{l,l+1} in UT5(Z/m) by explicit row updates."""
    n = DEPTH + 1
    acc = [[int(r == c) for c in range(n)] for r in range(n)]
    for event in word:
        l = int(event)
        for r in range(n):  # right-multiplying by I + e_{l-1,l} adds column l-1 to column l
            acc[r][l] = (acc[r][l] + acc[r][l - 1]) % modulus
    want = [[int(r == c) for c in range(n)] for r in range(n)]
    want[0][DEPTH] = coefficient % modulus
    return acc == want


def matmul(a, b, m):
    return [[sum(a[i][k] * b[k][j] for k in range(2)) % m for j in range(2)]
            for i in range(2)]


def matvec(a, v, m):
    return [sum(a[i][k] * v[k] for k in range(2)) % m for i in range(2)]


def literal_replay(word: str, modulus: int, coefficient: int, rng) -> bool:
    """Dirty registers in (Z/m)^2 and random (generally noncommuting) 2x2 maps."""
    maps = [[[rng.randrange(modulus) for _ in range(2)] for _ in range(2)]
            for _ in range(DEPTH)]
    start = [[rng.randrange(modulus) for _ in range(2)] for _ in range(DEPTH + 1)]
    regs = [row[:] for row in start]
    for event in word:
        letter = int(event)
        gain = matvec(maps[letter - 1], regs[letter - 1], modulus)
        regs[letter] = [(u + g) % modulus for u, g in zip(regs[letter], gain)]
    chain = maps[0]
    for b in maps[1:]:
        chain = matmul(b, chain, modulus)
    target = [(u + coefficient * g) % modulus
              for u, g in zip(start[DEPTH], matvec(chain, start[0], modulus))]
    return regs[:DEPTH] == start[:DEPTH] and regs[DEPTH] == target


def load_witnesses() -> dict:
    data = json.loads((PACKAGE / "witnesses.json").read_text(encoding="utf-8"))
    require(data.get("schema_version") == 1, "witness schema")
    table = {int(m): {int(c): rec for c, rec in row.items()}
             for m, row in data["witnesses"].items()}
    require(sorted(table) == list(range(M_MIN, M_MAX + 1)), "modulus range")
    for m, row in table.items():
        require(sorted(row) == list(range(1, m)), f"residues at m={m}")
    return table


def check_witnesses(table: dict) -> int:
    rng = random.Random(SEED)
    checked = 0
    for m, row in sorted(table.items()):
        for c, rec in sorted(row.items()):
            rows, rho, beta = parse(m, rec)
            vanish, predicted = lemma_conditions(m, rows, rho, beta)
            require(vanish == (0, 0, 0, 0, 0) and predicted == c, f"Lemma 2 sums at {(m, c)}")
            word = build_word(m, rows, rho, beta)
            require(len(word) == DEPTH * m, f"length at {(m, c)}")
            for letter in "1234":
                require(word.count(letter) == m, f"count of {letter} at {(m, c)}")
            require(counts_correct(word, m, c), f"interval counts at {(m, c)}")
            require(matrix_correct(word, m, c), f"UT5 product at {(m, c)}")
            require(literal_replay(word, m, c, rng), f"dirty replay at {(m, c)}")
            checked += 1
    return checked


def random_record(m: int, rng, partial_rows: int = -1) -> tuple:
    if partial_rows < 0:
        rows = sorted((rng.randint(0, m) for _ in range(rng.randint(0, m))), reverse=True)
    else:
        full = rng.randint(0, m - partial_rows)
        first = rng.randint(1, m - 1)
        partial = {0: [], 1: [first], 2: [first, m - first]}[partial_rows]
        rows = [m] * full + sorted(partial, reverse=True)
    rho = sorted((rng.randint(0, m) for _ in range(len(rows))), reverse=True)
    beta = {}
    for _ in range(rng.randint(0, 3)):
        b = rng.randint(1, m)
        beta[b] = beta.get(b, 0) + rng.randint(1, 3)
    if sum(beta.values()) > m:
        beta = {}
    return parse(m, {"rows": rows, "rho": rho, "beta": {str(b): k for b, k in beta.items()}})


def check_lemma2() -> tuple:
    """Lemma 2 on random data: the sums predict correctness and c exactly."""
    rng = random.Random(SEED + 1)
    hits = 0
    for _ in range(LEMMA_TRIALS):
        m = rng.randint(2, 9)
        rows, rho, beta = random_record(m, rng)
        vanish, predicted = lemma_conditions(m, rows, rho, beta)
        word = build_word(m, rows, rho, beta)
        require(all(word.count(l) == m for l in "1234"), "Lemma 2 word balance")
        count = interval_counts(word, m)
        actual = all(v == 0 for iv, v in count.items() if iv != (1, DEPTH))
        require(actual == (vanish == (0, 0, 0, 0, 0)), "Lemma 2 criterion mismatch")
        require(not actual or count[(1, DEPTH)] == predicted, "Lemma 2 coefficient mismatch")
        hits += actual
    require(0 < hits < LEMMA_TRIALS, "Lemma 2 random trials did not exercise both outcomes")
    return LEMMA_TRIALS, hits


def check_lemma3() -> int:
    """Lemma 3: at most two partial rows and prime m force c = 0."""
    rng = random.Random(SEED + 2)
    seen = 0
    for _ in range(LEMMA_TRIALS):
        m = rng.choice((5, 7, 11, 13))
        rows, rho, beta = random_record(m, rng, rng.randint(0, 2))
        vanish, predicted = lemma_conditions(m, rows, rho, beta)
        if vanish == (0, 0, 0, 0, 0):
            require(predicted == 0, "Lemma 3 counterexample")
            seen += 1
    require(seen > 0, "Lemma 3 random trials were vacuous")
    return seen


def controls(table: dict) -> list:
    """Each mutation must be rejected by the Lemma 2 sums or by the word checks."""
    m, c = 37, 5
    rec = table[m][c]
    names = []

    def rejected(name: str, mutated: dict, coeff: int = c) -> None:
        rows, rho, beta = parse(m, mutated)
        vanish, predicted = lemma_conditions(m, rows, rho, beta)
        require(vanish != (0, 0, 0, 0, 0) or predicted != coeff, f"control {name}: sums")
        word = build_word(m, rows, rho, beta)
        require(not counts_correct(word, m, coeff), f"control {name}: counts")
        require(not matrix_correct(word, m, coeff), f"control {name}: matrix")
        names.append(name)

    rejected("wrong_coefficient", rec, c + 1)
    bumped = dict(rec, rho=list(rec["rho"]))
    bumped["rho"][0] -= 1  # the witness has rho(1) > rho(2), so the shape stays legal
    rejected("rho_first_row_changed", bumped)
    shorter = dict(rec, rows=list(rec["rows"]))
    shorter["rows"][1] -= 1
    rejected("lambda_row_shortened", shorter)
    moved = dict(rec, beta={str(int(b) + 1) if int(b) > 1 else b: k for b, k in rec["beta"].items()})
    rejected("beta_level_moved", moved)
    word = build_word(m, *parse(m, rec))
    require(counts_correct(word, m, c) and not counts_correct(word[:-1], m, c),
            "control dropped call")
    names.append("dropped_last_call")
    return names


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    require(sys.argv[1:] == [], "usage: verify.py")
    table = load_witnesses()
    checked = check_witnesses(table)
    require(checked == sum(m - 1 for m in range(M_MIN, M_MAX + 1)), "witness total")
    names = controls(table)
    trials, hits = check_lemma2()
    lemma3 = check_lemma3()
    receipt = {
        "schema_version": 1,
        "claim": "shortest unsigned depth-four dirty chain connector = 4m calls "
                 f"for every m in [{M_MIN}, {M_MAX}] and every nonzero c (mod m)",
        "witnesses_checked": checked,
        "literal_replays": checked,
        "controls": names,
        "lemma2_random_records": trials,
        "lemma2_random_correct_words": hits,
        "lemma3_nonvacuous_trials": lemma3,
        "package_sha256": {f: sha256(PACKAGE / f) for f in PACKAGE_FILES},
        "input_sha256": {p: sha256(ROOT / p) for p in INPUTS},
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    print(f"PASS_DEPTH4_CHAIN_ROWMODEL moduli={M_MAX - M_MIN + 1} witnesses={checked}")


if __name__ == "__main__":
    main()
