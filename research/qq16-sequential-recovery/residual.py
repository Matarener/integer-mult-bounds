"""Narrow ordered-residual witness from Chris R / Clear1nsight PR4003.
Source mathematics/replay: ywz65 PR2707 and Arham Tahir PR2681.
Copied exact witness logic; caller authenticates canonical source before use.
OpenAI-assisted integration. Apache-2.0.
"""
from fractions import Fraction as Q
from functools import lru_cache
import hashlib,json
def need(ok,message):
    if not ok:raise ValueError(message)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
# Independent exact binary-column and sparse group-ring implementation.
def action(columns, value):
    result = 0
    for j, column in enumerate(columns):
        if value & (1 << j):
            result ^= column
    return result

@lru_cache(None)
def product(left, right):
    return tuple(action(left, v) for v in right)

def add(left, right, coefficient=Q(1)):
    out = dict(left)
    for key, value in right.items():
        out[key] = out.get(key, Q(0)) + coefficient * value
        if not out[key]:
            del out[key]
    return out

def route(columns, row):
    return {(source, product(columns, owner)): coefficient for (source, owner), coefficient in row.items()}

def query(R, routes, stage, bank, ports):
    result = [{} for _ in range(8)]
    for k in range(8):
        for p in ports:
            if R[k][p]:
                result[k] = add(result[k], route(routes[stage][p], bank[p]), R[k][p])
    return result

def serialize(rows):
    return [[[s, list(g), str(c)] for (s, g), c in sorted(row.items())] for row in rows]

def prefix_rows(word, stop, P, routes):
    rows = {s + str(p): {(s + str(p), P.AXES): Q(1)} for s in ('X', 'Y', 'Z', 'W') for p in range(112)}
    for event in word[:stop]:
        op = event[0]
        if op == 'clear':
            rows[event[1]] = {}
        elif op == 'add':
            rows[event[1]] = add(rows[event[1]], rows[event[2]], Q(event[3]))
        elif op == 'map':
            rows[event[1]] = route(routes[event[2]][event[3]], rows[event[1]])
        elif op in ('line', 'begin', 'end'):
            pass  # Native changes are frames, not logical array values.
        else:
            raise ValueError('unexpected prefix opcode: ' + op)
    return rows

def schur(R, routes, ports, bank, reverse=False):
    result = [{} for _ in range(8)]
    for p in ports:
        g = product(routes[1][p], routes[2][p]) if reverse else product(routes[2][p], routes[1][p])
        for k in range(8):
            for j in range(8):
                c = R[k][p] * R[j][p] / 4
                if c:
                    result[k] = add(result[k], route(g, bank[j]), c)
    return result

def characters(rows, character):
    result = []
    for row in rows:
        out = {}
        for (source, owner), c in row.items():
            key = (source, action(owner, character))
            out[key] = out.get(key, Q(0)) + c
            if not out[key]:
                del out[key]
        result.append(out)
    return result

def check(P,R,routes,labels,word,L):
    pins = {}
    stop = next(i for i, e in enumerate(word) if e[0] == 'map' and e[2] == 2)
    rows = prefix_rows(word, stop, P, routes)
    x = [rows['X' + str(p)] for p in range(112)]
    y = [rows['Y' + str(p)] for p in range(112)]
    a = query(R, routes, 1, y, range(112))
    delta = [{} for _ in range(112)]
    for p in P.U + P.T:
        if p in P.T:
            delta[p] = dict(x[p])
        for j in range(8):
            delta[p] = add(delta[p], route(routes[1][p], a[j]), -R[j][p] / 4)
        need(rows['W' + str(p)] == add(y[p], delta[p]), 'actual prefix residual at port ' + str(p))
    direct = query(R, routes, 2, delta, P.U + P.T)
    mx = schur(R, routes, P.U + P.T, a)
    tx = query(R, routes, 2, x, P.T)
    derived = [add(tx[k], mx[k], -1) for k in range(8)]
    need(direct == derived, 'ordered residual identity')
    basis = [{('a' + str(j), P.AXES): Q(1)} for j in range(8)]
    operator = schur(R, routes, P.U + P.T, basis)
    term_records = []
    for p in P.U + P.T:
        g = product(routes[2][p], routes[1][p])
        r = [int(R[k][p]) for k in range(8)]
        term_records.append({'port': p, 'q': labels[p], 'r': r, 'owner_columns': list(g), 'character_one_image': action(g, 1)})
    need(len({tuple(t['owner_columns']) for t in term_records}) == 104, 'distinct ordered products')
    need(len({t['character_one_image'] for t in term_records}) == 104, 'character separates all routes')
    need(all(sum(c * c for c in t['r']) == 4 for t in term_records), 'nonzero rank-one coefficient matrices')
    trivial = characters(operator, 0)
    scalar13 = [{('a' + str(k), 0): Q(13)} for k in range(8)]
    need(trivial == scalar13, 'trivial character Gram collapse')
    one = characters(operator, 1)
    need(one != [{('a' + str(k), 1): Q(13)} for k in range(8)], '13I must fail')
    diagonal = {v: c for (s, v), c in one[0].items() if s == 'a0'}
    need(len(diagonal) == 52 and set(diagonal.values()) == {Q(1, 4)} and 1 not in diagonal, '52-image diagonal witness')
    # Arbitrary query a is realized by actual current Y supported only on A.
    realizable_y = [{} for _ in range(112)]
    for p in P.A:
        for j in range(8):
            realizable_y[p] = add(realizable_y[p], route(routes[1][p], basis[j]), R[j][p] / 4)
    need(query(R, routes, 1, realizable_y, range(112)) == basis, 'actual current query surjection')
    # For X=0 and this Y, bypass query is zero; actual query is -M a.
    need(all(not realizable_y[p] for p in P.U + P.T), 'zero borrowed bypass input')
    # A-response is injective: undo each involutive g2 and apply R_A to recover query.
    response = [{} for _ in range(112)]
    for p in P.A:
        for j in range(8):
            response[p] = add(response[p], route(routes[2][p], operator[j]), R[j][p] / 4)
    need(query(R, routes, 2, response, P.A) == operator, 'response cannot erase residual')
    # Exactly the same full phased-owner type is available to all query terms.
    frame_checks = 0
    for p in P.U + P.T:
        g = routes[2][p]
        need(action(g, labels[p]) == labels[p], 'normal label fixed')
        shifted_hole = P.move(P.F17 + ((labels[p], -1),), g, L.bridge(P, g, labels[p]))
        need(P.phase(shifted_hole) == P.phase(L.F16), 'bypass hole frame')
        frame_checks += 1
    wrong_order = schur(R, routes, P.U + P.T, basis, reverse=True)
    need(characters(wrong_order, 1) != one, 'ordered-product control')
    need(query(R, routes, 2, delta, P.U) != direct, 'omitted T residual control')
    need(any(direct), 'zero correction control')
    result = {
        'status': 'PASS_QQ16_ORDERED_SCHUR_OBSTRUCTION', 'source_pins': pins,
        'source_future_start_event': stop, 'prefix_ports_verified': 104,
        'residual_formula': 'Q2(X_T) - (1/4) sum_p r_p r_p^T [g2,p g1,p] Q1(Y)',
        'ordered_terms': term_records,
        'operator_sha256': hashlib.sha256(canonical(serialize(operator))).hexdigest(),
        'residual_sha256': hashlib.sha256(canonical(serialize(direct))).hexdigest(),
        'trivial_character': '13I', 'separating_character': 1,
        'distinct_character_images': 104, 'one_route_branch_lower_bound': 104,
        'diagonal_00_character_witness': [[v, str(c)] for v, c in sorted(diagonal.items())],
        'query_surjection': 'Y_A=K1,A a; Y_(U+T)=0; X=0 gives Q1(Y)=a',
        'response_injective': True, 'bypass_frame_checks': frame_checks,
        'semantic_controls': ['replace M with13I', 'reverse ordered products', 'omit T residual', 'omit entire correction'],
        'scope': 'Exact logical source residual and restricted single-owner-route-per-branch lower bound. Not a native-child lower bound, circuit optimality, scalar tensor-rank bound, physical supplier or kappa improvement.'}
    return result
