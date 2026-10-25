"""Exact census of minimum paid-call counts for small mixed-negative Q8 endpoints.

Model (unchanged from PR3570/PR3578/PR3589): work in the full formal group
algebra F2[Q8].  A word is a finite sequence of paid factors

    D_l = I + (1 + [g_l]) u_l v_l^T,   g_l in {i, j},   v_l^T u_l = 1,

acting on a roles x roles matrix over F2[Q8].  The endpoint is diagonal with
t_i copies of zi, t_j copies of zj and the identity elsewhere.  Free binary
scalar GL mixing and any finite restored dirty workspace are permitted.

This module is self-contained: it depends only on the standard library and
needs no Git objects, no network and no third-party package.
"""

import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAX_ROLES = 8
ONE, Z, ZI, ZJ = 1, 1 << 4, 1 << 5, 1 << 6


def require(ok, message):
    if not ok:
        raise ValueError(message)


def group_product(a, b):
    """Q8 multiplication in the basis 1,i,j,ij,z,zi,zj,zij."""
    ai, aj, bi, bj = a & 1, a >> 1 & 1, b & 1, b >> 1 & 1
    central = (a >> 2) ^ (b >> 2) ^ (ai & bi) ^ (aj & bj) ^ (aj & bi)
    return central << 2 | (ai ^ bi) | (aj ^ bj) << 1


def hamilton(a, b):
    """Independent signed-unit table, in the same eight basis slots."""
    axes = ((0, 1, 2, 3), (1, 0, 3, 2), (2, 3, 0, 1), (3, 2, 1, 0))
    signs = ((0, 0, 0, 0), (0, 1, 0, 1), (0, 1, 1, 0), (0, 0, 1, 1))
    x, y = a & 3, b & 3
    return axes[x][y] + 4 * ((a >> 2) ^ (b >> 2) ^ signs[x][y])


def mul(a, b):
    """Multiply two F2[Q8] masks given as eight-bit basis masks."""
    value = 0
    for i in range(8):
        if a >> i & 1:
            for j in range(8):
                if b >> j & 1:
                    value ^= 1 << group_product(i, j)
    return value


PAYED = {1: ONE | (1 << 1), 2: ONE | (1 << 2)}  # 1+i and 1+j as basis masks


def legal_calls(roles):
    """All paid factors D = I + (1+g) u v^T with v^T u = 1 over F2."""
    require(1 <= roles <= MAX_ROLES, "role capacity")
    calls = []
    for u in range(1, 1 << roles):
        for v in range(1, 1 << roles):
            if (u & v).bit_count() % 2 == 1:
                for g in (1, 2):
                    calls.append((g, u, v))
    return tuple(calls)


def apply(state, call, roles):
    """Left-multiply the roles x roles state by one paid factor."""
    g, u, v = call
    c = PAYED[g]
    selected = [0] * roles
    for a in range(roles):
        if v >> a & 1:
            row = state[a]
            for b in range(roles):
                selected[b] ^= row[b]
    change = [mul(c, value) for value in selected]
    out = [list(row) for row in state]
    for a in range(roles):
        if u >> a & 1:
            out[a] = [p ^ q for p, q in zip(out[a], change, strict=True)]
    return tuple(tuple(row) for row in out)


def endpoint(word, roles):
    """The composite map D_n ... D_1 evaluated at the identity."""
    require(1 <= roles <= MAX_ROLES, "role capacity")
    state = tuple(tuple(int(a == b) for b in range(roles)) for a in range(roles))
    for call in word:
        require(call[0] in (1, 2), "paid label")
        require(0 < call[1] < 1 << roles and 0 < call[2] < 1 << roles, "projector range")
        require((call[1] & call[2]).bit_count() % 2 == 1, "projector idempotence")
        state = apply(state, call, roles)
    return state


def wanted(roles, targets):
    """The diagonal endpoint with the requested targets on each role."""
    return tuple(
        tuple(targets[a] if a == b else 0 for b in range(roles)) for a in range(roles)
    )


def parity_lower_bound(targets):
    """The PR3589 bound 5n >= 11t with the inherited trace parity n = t mod 2."""
    counts = {ZI: 0, ZJ: 0}
    for value in targets:
        require(value in counts, "endpoint target")
        counts[value] += 1
    t = counts[ZI] + counts[ZJ]
    require(t > 0, "empty target")
    n = -(-11 * t // 5)  # ceil(11t/5)
    if n % 2 != t % 2:
        n += 1
    return n, t, counts[ZI], counts[ZJ]


def complete_census(roles, targets, max_length, state_cap=8_000_000):
    """Exhaustive breadth-first search over every word on exactly `roles` roles.

    Returns a receipt with the first length that reaches the target, the
    witness, the number of distinct states seen and whether the search really
    exhausted all words of length at most `max_length`.
    """
    calls = legal_calls(roles)
    goal = wanted(roles, targets)
    start = tuple(tuple(int(a == b) for b in range(roles)) for a in range(roles))
    seen = {start: None}
    frontier = [start]
    for depth in range(1, max_length + 1):
        nxt = []
        for state in frontier:
            for call in calls:
                nxt_state = apply(state, call, roles)
                if nxt_state in seen:
                    continue
                seen[nxt_state] = (state, call)
                if nxt_state == goal:
                    chain, cur = [], nxt_state
                    while seen[cur] is not None:
                        prev, call_used = seen[cur]
                        chain.append(list(call_used))
                        cur = prev
                    chain.reverse()
                    return {
                        "roles": roles,
                        "targets": list(targets),
                        "searched_length": depth,
                        "witness": chain,
                        "states": len(seen),
                        "exhausted": True,
                        "cap_reached": False,
                    }
                nxt.append(nxt_state)
        frontier = nxt
        if len(seen) > state_cap:
            return {
                "roles": roles,
                "targets": list(targets),
                "searched_length": None,
                "witness": None,
                "states": len(seen),
                "exhausted": False,
                "cap_reached": True,
            }
    return {
        "roles": roles,
        "targets": list(targets),
        "searched_length": None,
        "witness": None,
        "states": len(seen),
        "exhausted": True,
        "cap_reached": False,
    }


# ---------------------------------------------------------------- certificates

# Three calls on one role multiply that role by the cube of its label:
# i^3 = zi and j^3 = zj. `spine(label, role)` is that three-call block.
def spine(label, role):
    return [(label, 1 << role, 1 << role)] * 3


SINGLE = spine(1, 0)
WITNESSES = {
    "t1-zi": (1, (ZI,), spine(1, 0)),
    "t1-zj": (1, (ZJ,), [(1, 1, 1)] * 2 + [(2, 1, 1)]),
    "t2-zi-zj": (2, (ZI, ZJ), spine(1, 0) + spine(2, 1)),
    "t2-zi-zi": (2, (ZI, ZI), spine(1, 0) + spine(1, 1)),
    "t2-zj-zj": (2, (ZJ, ZJ), spine(2, 0) + spine(2, 1)),
    "t3-zi-zi-zj": (3, (ZI, ZI, ZJ), spine(1, 0) + spine(1, 1) + spine(2, 2)),
    "t3-zi-zi-zi": (3, (ZI, ZI, ZI), spine(1, 0) + spine(1, 1) + spine(1, 2)),
    "t4-balanced": (4, (ZI, ZI, ZJ, ZJ),
     spine(1, 0) + spine(1, 1) + spine(2, 2) + spine(2, 3)),
}

# Complete breadth-first receipts. Each search ran to its limit and found no
# word of that length or shorter on exactly `roles` roles. For t = 1 and
# t = 2 the PR3589 bound already excludes every shorter length at every role
# count, so these receipts are a complete independent cross-check rather than
# the source of the lower bound.
CENSUS_CASES = [
    ("t1-zi", 1, (ZI,), 2),
    ("t1-zj", 1, (ZJ,), 2),
    ("t2-zi-zj", 2, (ZI, ZJ), 5),
    ("t2-zi-zi", 2, (ZI, ZI), 5),
    ("t2-zj-zj", 2, (ZJ, ZJ), 5),
]


def verify():
    receipt = {"algebra": {}, "witnesses": {}, "census": {}}

    # 1. The signed-unit table and the mask product agree on all 64 products.
    products = sum(
        group_product(a, b) == hamilton(a, b)
        for a, b in itertools.product(range(8), repeat=2)
    )
    require(products == 64, "Hamilton table disagreement")
    receipt["algebra"]["q8_products"] = 64

    # 2. The single-role generator really produces zi and zj in three calls.
    require(mul(1 << 1, mul(1 << 1, 1 << 1)) == ZI, "i^3 is not zi")
    require(mul(1 << 2, mul(1 << 2, 1 << 2)) == ZJ, "j^3 is not zj")
    require(mul(Z, Z) == ONE, "z is not an involution")
    receipt["algebra"]["i3_zi"] = True
    receipt["algebra"]["j3_zj"] = True

    # 3. Every retained witness reaches its diagonal endpoint exactly.
    for name, (roles, targets, word) in sorted(WITNESSES.items()):
        require(endpoint(tuple(word), roles) == wanted(roles, targets),
                "witness does not reach its endpoint: " + name)
        bound, t, ti, tj = parity_lower_bound(targets)
        receipt["witnesses"][name] = {
            "roles": roles,
            "targets": [targets[a] for a in range(roles)],
            "calls": len(word),
            "parity_bound": bound,
            "t": t,
            "t_i": ti,
            "t_j": tj,
            "attains_parity_bound": len(word) == bound,
        }

    # 4. The complete breadth-first receipts are replayed from scratch.
    for name, roles, targets, limit in CENSUS_CASES:
        found = complete_census(roles, targets, limit)
        receipt["census"][name] = found
        require(found["exhausted"] and not found["cap_reached"],
                "census did not exhaust: " + name)
        require(found["searched_length"] is None,
                "unexpected short word: " + name)
        # The retained witness must sit exactly on the parity-rounded bound.
        bound, _t, _ti, _tj = parity_lower_bound(targets)
        require(len(WITNESSES[name][2]) == bound,
                "witness misses the parity bound: " + name)

    return receipt


def main():
    receipt = verify()
    text = json.dumps(receipt, indent=1, sort_keys=True)
    (ROOT / "RESULT.json").write_text(text + "\n")
    for name, row in sorted(receipt["witnesses"].items()):
        print(
            f"{name:16s} t={row['t']} calls={row['calls']:2d} "
            f"bound={row['parity_bound']:2d} attained={row['attains_parity_bound']}"
        )
    for name, row in sorted(receipt["census"].items()):
        print(
            f"census {name:16s} roles={row['roles']} "
            f"min={row['searched_length']} exhausted={row['exhausted']} "
            f"states={row['states']}"
        )
    print("PASS mixed-negative Q8 minimum-length census")


if __name__ == "__main__":
    main()