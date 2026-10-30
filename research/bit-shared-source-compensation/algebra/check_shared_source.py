#!/usr/bin/env python3
"""Exact F2[C2*C2*C2] rows: no matrix quotient, samples, or search.

Run python3 -I -B algebra/check_shared_source.py.  Every input role is
independent; a nonzero row coefficient is retained as a reduced group word.
"""
import json


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def multiply(left, right):
    out = list(left)
    for letter in right:
        if out and out[-1] == letter:
            out.pop()
        else:
            out.append(letter)
    return tuple(out)


def execute(word, n, modulus=2):
    rows = [{(i, ()): 1} for i in range(n)]
    for gate in word:
        if gate[0] == "warp":
            _, target, letter = gate
            rows[target] = {
                (source, multiply((letter,), group_word)): coefficient
                for (source, group_word), coefficient in rows[target].items()
            }
        elif gate[0] == "add":
            _, target, source = gate[:3]
            coefficient = gate[3] if len(gate) == 4 else 1
            need(target != source, "noninvertible self-ADD")
            for term, value in list(rows[source].items()):
                value = rows[target].get(term, 0) + coefficient * value
                if modulus is not None:
                    value %= modulus
                if value == 0:
                    rows[target].pop(term, None)
                else:
                    rows[target][term] = value
        else:
            raise RuntimeError("unknown gate")
    return rows


def warp(role, letter):
    return ("warp", role, letter)


def add(target, source, coefficient=1):
    if coefficient == 1:
        return ("add", target, source)
    return ("add", target, source, coefficient)


def inverse_word(word):
    return [gate if gate[0] == "warp" else
            add(gate[1], gate[2], -(gate[3] if len(gate) == 4 else 1))
            for gate in reversed(word)]


def invoice(word, ranks):
    hist = {}
    adds = 0
    for gate in word:
        if gate[0] == "add":
            adds += 1
        else:
            rank = ranks[gate[2]]
            hist[str(rank)] = hist.get(str(rank), 0) + 1
    return {"query_rank_histogram": hist, "scalar_adds": adds,
            "clean_helpers": 0, "clear_or_erase": 0}


def encode(rows):
    return [[{"input": i, "operator": "".join(w) or "1"}
             for i, w in sorted(row)] for row in rows]


def main():
    # Valid but nonqualifying positive control: two actual requested shears,
    # first by p and second by qp, on one temporarily mutable source.
    prefix = [warp(0, "p"), add(1, 0), warp(0, "q"), add(2, 0),
              warp(0, "q"), warp(0, "p")]
    separate = [warp(0, "p"), add(1, 0), warp(0, "p"),
                warp(0, "p"), warp(0, "q"), add(2, 0),
                warp(0, "q"), warp(0, "p")]
    expected = [{(0, ()): 1}, {(1, ()): 1, (0, ("p",)): 1},
                {(2, ()): 1, (0, ("q", "p")): 1}]
    need(execute(prefix, 3) == expected, "prefix endpoint")
    need(execute(separate, 3) == expected, "separate endpoint")
    need(execute(prefix + list(reversed(prefix)), 3) == execute([], 3),
         "prefix literal reverse-inverse")
    wrong_cleanup = prefix[:-2] + [warp(0, "p"), warp(0, "q")]
    need(execute(wrong_cleanup, 3) != expected, "cleanup mutation undetected")

    # Immutable public source: arbitrary dirty helper 3. Copy source into h,
    # tour h, uncopy source, tour h again to echo away entering helper dirt.
    helper_tour = [(g[0], 3 if g[1] == 0 else g[1],
                    3 if g[0] == "add" and g[2] == 0 else g[2])
                   for g in prefix]
    echo = [add(3, 0)] + helper_tour + [add(3, 0)] + helper_tour
    need(execute(echo, 4) == expected + [{(3, ()): 1}], "dirty helper echo")
    need(execute(echo[:-1], 4) != expected + [{(3, ()): 1}],
         "missing literal inverse mutation undetected")

    # Audited scalar fanout L for records 23325..23338. Role map is explicit.
    # 0:x17, 1:h444, 2:h413, 3:271, 4:293, 5:352, 6:468, 7:470,
    # 8:371, 9:605. p is 509->390; q is 509->392; r is 390->517.
    l_word = [add(1, 0), add(1, 3), add(1, 4), add(1, 5), add(1, 2),
              add(1, 6), add(1, 7), add(2, 0), add(2, 3), add(2, 4),
              add(2, 5), add(2, 8), add(2, 7)]
    reduced_l = [g for g in l_word if g not in [add(1, 0), add(2, 0)]]
    # r and read605 preserve the immediate delivery demand of h413.
    tail = [warp(2, "p"), add(2, 9), warp(2, "r"), warp(1, "q")]
    original = l_word + tail
    repair = reduced_l + [warp(2, "p"), warp(0, "p"), add(2, 0),
                          warp(0, "p"), add(2, 9), warp(2, "r"),
                          warp(1, "q"), warp(0, "q"), add(1, 0),
                          warp(0, "q")]
    need(execute(repair, 10) == execute(original, 10), "packet compensation")
    # Independent cut just after h413 query, before source605 read.
    original_cut = l_word + [warp(2, "p")]
    repair_cut = reduced_l + [warp(2, "p"), warp(0, "p"), add(2, 0),
                             warp(0, "p")]
    original_cut_rows, repaired_cut_rows = execute(original_cut, 10), execute(repair_cut, 10)
    # h444's x contribution is pending until its own delivery; all others match.
    need(all(original_cut_rows[i] == repaired_cut_rows[i] for i in range(10) if i != 1),
         "h413 delivery or spectator endpoint")
    need(execute(repair + list(reversed(repair)), 10) == execute([], 10),
         "packet literal reverse-inverse")
    # Delete both original helper queries: source transport alone cannot move dirt.
    omitted_dirt = repair.copy()
    omitted_dirt.remove(warp(2, "p"))
    omitted_dirt.remove(warp(1, "q"))
    need(execute(omitted_dirt, 10) != execute(original, 10), "dirty defect undetected")
    # Late compensation after the next h413 warp uses stale pullback p, not rp.
    late = reduced_l + [warp(2, "p"), add(2, 9), warp(2, "r"),
                        warp(0, "p"), add(2, 0), warp(0, "p"),
                        warp(1, "q"), warp(0, "q"), add(1, 0), warp(0, "q")]
    need(execute(late, 10) != execute(original, 10), "stale cut pullback undetected")
    # Scalar fanout is invertible, so the correct full packet has the diagonal
    # query endpoint after its L prelude is uncomputed at the INPUT.
    diagonal = l_word + [warp(2, "p"), warp(1, "q")]
    need(execute(list(reversed(l_word)) + diagonal, 10) ==
         execute([warp(2, "p"), warp(1, "q")], 10), "F L^-1 reduction")
    need(execute([warp(0, "p"), warp(0, "q")], 1) !=
         execute([warp(0, "q"), warp(0, "p")], 1), "commuting quotient used")

    # A separate actual scalar sharing control: compute b first and use its
    # current row, including independent dirt and v, then compensate v in a.
    # The source audit must separately license moving v371's frame arrival.
    shared_l = [add(2, 0), add(2, 3), add(2, 4), add(2, 5), add(2, 7),
                add(2, 8), add(1, 2), add(1, 6), add(1, 8, -1)]
    scalar_shared = shared_l + tail
    need(execute(shared_l, 10, None) == execute(l_word, 10, None),
         "integer scalar-sharing identity")
    need(execute(scalar_shared, 10) == execute(original, 10),
         "combined scalar sharing and query endpoint")
    need(execute(scalar_shared + inverse_word(scalar_shared), 10, None) ==
         execute([], 10, None), "integer literal reverse-inverse")
    sign_mutant = shared_l[:-1] + [add(1, 8)]
    need(execute(sign_mutant, 10, None) != execute(l_word, 10, None),
         "integer sign control undetected")
    need(execute(sign_mutant, 10) == execute(l_word, 10),
         "sign control must illustrate Boolean lift blind spot")

    report = {
        "status": "PASS",
        "coefficient_domain": "F2[C2*C2*C2], complete reduced-word normal forms",
        "claim": "exact shared-source repair; positive surcharge on audited cut contract",
        "prefix_control": {"qualifies_as_actual_demand": False,
                           "shared": invoice(prefix, {"p": 2, "q": 2}),
                           "separate": invoice(separate, {"p": 2, "q": 2}),
                           "dirty_echo": invoice(echo, {"p": 2, "q": 2})},
        "actual_packet_algebra": {
            "original": invoice(original, {"p": 2, "q": 2, "r": 1}),
            "repair": invoice(repair, {"p": 2, "q": 2, "r": 1}),
            "delta": {"rank2_queries": 4, "scalar_adds": 0, "new_helpers": 0},
            "endpoint": encode(execute(original, 10)),
            "required_cut_h413": encode([original_cut_rows[2]])},
        "scalar_sharing_control": {
            "old_prelude_adds": len(l_word), "new_prelude_adds": len(shared_l),
            "combined_subword_invoice": invoice(scalar_shared, {"p": 2, "q": 2, "r": 1}),
            "forward_delta": {"queries": 0, "scalar_adds": -4},
            "additional_delta_only_if_separate_full_literal_inverse_is_executed": {
                "queries": 0, "scalar_adds": -4},
            "frozen_existing_cleanup_delta": {"queries": 0, "scalar_adds": 0},
            "integer_group_algebra_equality": True,
            "qualification": "requires source-audited earlier arrival of v371; no query saving"},
        "negative_controls": ["wrong_noncommuting_reverse_inverse", "missing_dirty_echo_inverse",
                              "omitted_independent_dirt_queries", "late_stale_pullback",
                              "scalar_fanout_integer_compensation_sign"],
        "coverage": "algebraic template only; literal embedding requires source audit windows",
        "no_new_kappa": True
    }
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
