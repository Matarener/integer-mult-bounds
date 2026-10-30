#!/usr/bin/env python3
"""Verify that the length-8 decoding code of the 104 P104 ports is unique over F_3 and has minimum weight 49.  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.  Python 3.12, standard library only.
usage: verify.py [--parts 0,1,2,3] [--write]

Checks: (0) pinned inputs; (1) structure: the 104 ports read from both pinned words agree, have odd weight, the
conflict graph (<q_i, q_j> = 1) is 55-regular, T_INDEX is a conflict 8-clique, and the largest numbers of ports in a
hyperplane and in a codimension-2 subspace of F_2^9 are 60 and 36; (2) the selected parts of the search certificate
(cert/part*.txt.gz, written by gen8.py) replay completely: every internal node lists all canonical consistent options of
its port, every dead node has none, no token is left over; the per-part node and solution counts equal RESULT.json and
the recorded counts over all four parts add up to exactly one solution; (3) a replayed solution has no free variable,
decodes at every port, its decoding matrix is sign-equivalent to its transpose, and the row and column spaces have
minimum weight 49 with the recorded weight distribution; (4) on both pinned words (PR5907 and the selected PR6030):
all scalars are dyadic, the Lemma-1 decomposition keeps the frame invariant and the partner endpoints, the ten
weight-52 owned deliveries span an 8-dimensional code with the decoding property whose decoding matrix is
sign-equivalent to the replayed solution (when the solution is in the selected parts) and passes the model equations;
(5) controls: one trit changed in that code breaks the model equations; a certificate whose first internal node below
the root is marked dead (its port has options) is rejected, and so is one whose first dead node is replaced by a
solution leaf; (6) the receipt equals RESULT.json.
"""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import itertools
import json
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from code8 import Model, T_INDEX, dot  # noqa: E402
from replay import (code_basis, decoding_rows, max_ports_in_codim, replay, rref3, sign_equivalent,  # noqa: E402
                    tokens, weight_distribution)
from wordcode import decompose, dyadic, load, m3  # noqa: E402

WORDS = {'pr5907': 'research/p104-helper468-rung-removal/WORD.json.gz',
         'pr6030': 'research/p104-helper470-twin-rung-removal/WORD.json.gz'}
NPARTS = 4


def need(ok, why):
    if not ok:
        raise ValueError(why)


def e8_root(q):
    """the E8 root (A8 coordinates) of an odd port: weight 7 -> e_i - e_j at its zeros, weight 3 -> 2/3 on it, -1/3 off"""
    c = [(q >> k) & 1 for k in range(9)]
    if sum(c) == 7:
        i, j = [k for k in range(9) if not c[k]]
        return [Fraction(1) if k == i else Fraction(-1) if k == j else Fraction(0) for k in range(9)]
    need(sum(c) == 3, 'ports have weight 3 or 7')
    return [Fraction(2, 3) if c[k] else Fraction(-1, 3) for k in range(9)]


def cert(p):
    return str(HERE / 'cert' / ('part%d.txt.gz' % p))


def wd_json(d):
    return {str(k): d[k] for k in sorted(d)}


def model_fixture(ports, rows):
    """push a code given by its decoding rows through the model equations (after the sign gauge c_{j,first} = 1)"""
    M = Model(ports)
    d = [1] * M.N
    for j in M.others:
        first = next(t for t in M.Tj[j] if rows[j][t])
        d[j] = rows[j][first]                          # D^-1 M D with d_t = 1 on T makes the first coefficient 1
    g = [[(pow(d[l], -1, 3) * rows[l][m] * d[m]) % 3 for m in range(M.N)] for l in range(M.N)]
    for (t, m), v in M.var.items():
        row = (1 << v) | (M.RHS if g[t][m] == 1 else 0), (M.RHS if g[t][m] == 2 else 0)
        if not M.push(row):
            return False
    for j in M.others:
        c = tuple(g[j][t] for t in M.Tj[j])
        if c not in M.OPT or not M.apply(j, c):
            return False
    return len(M.pivots) == M.NV


def tampered(p, mode):
    """token stream of part p with one defect near its start: 'sol' turns the first dead node into a solution leaf,
    'dead' turns the first internal node below the root into a dead node (its port has options)"""
    src = tokens(cert(p)); yield next(src); done = False
    for x in src:
        if not done and mode == 'sol' and x.startswith('d '):
            done = True; yield 's'; continue
        if not done and mode == 'dead' and x.startswith('n '):
            done = True; yield 'd' + x[1:]; continue
        yield x


def expect_failure(fn, text):
    try:
        fn()
    except ValueError as ex:
        need(text in str(ex), 'expected rejection "%s", got "%s"' % (text, ex))
        return str(ex)
    raise ValueError('control accepted: ' + text)


def main(argv):
    t0 = time.time()
    parts = list(range(NPARTS)); write = '--write' in argv
    if '--parts' in argv:
        parts = sorted({int(x) for x in argv[argv.index('--parts') + 1].split(',')})
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], 'source pin ' + row['path'])
    print('pins ok', flush=True)
    R = {'parts': {}}

    # (1) structure
    words = {k: load(ROOT / v) for k, v in WORDS.items()}
    port_lists = {}
    for k, w in words.items():
        ports, W, D = decompose(w)
        port_lists[k] = ports
    ports = port_lists['pr5907']
    need(port_lists['pr6030'] == ports, 'the two words have the same ports in the same live order')
    need(len(set(ports)) == 104 and all(bin(q).count('1') & 1 for q in ports), 'ports: 104 distinct odd vectors')
    degrees = {sum(1 for m in ports if m != q and dot(q, m)) for q in ports}
    need(degrees == {55}, 'conflict graph is 55-regular')
    need(all(dot(ports[a], ports[b]) for a in T_INDEX for b in T_INDEX if a != b), 'T is a conflict clique')
    f8, f7 = max_ports_in_codim(ports, 1), max_ports_in_codim(ports, 2)
    need((f8, f7) == (60, 36), 'f(8) = 60 and f(7) = 36')
    roots = [e8_root(q) for q in ports]
    G = [[sum(x * y for x, y in zip(a, b)) for b in roots] for a in roots]
    need(all(G[i][i] == 2 for i in range(104)), 'E8 roots have norm 2')
    need(all((G[i][j] == 0) == bool(dot(ports[i], ports[j])) for i in range(104) for j in range(104) if i != j),
         'conflict is orthogonality of E8 roots')
    e8_half = [[m3(x / 2) for x in r] for r in G]
    R['structure'] = {'ports': 104, 'conflict_degree': 55, 'clique': T_INDEX, 'f8_hyperplane': f8, 'f7_codim2': f7,
                      'e8_root_lines': 104, 'conflict_is_e8_orthogonality': True}
    print('structure', R['structure'], flush=True)

    # (4) the words
    R['words'] = {}; word_rows = {}
    for k, w in words.items():
        need(dyadic(w), k + ': all scalars dyadic')
        _, W, D = decompose(w)
        W3 = [[m3(x) for x in r] for r in W]
        heavy = sorted(v for v, s in D.items() if s == 52)
        B = rref3(heavy); rows = decoding_rows(B, ports)
        need(len(B) == 8 and rows is not None, k + ': weight-52 deliveries span an 8-dim decoding code')
        need(model_fixture(ports, rows), k + ': the code passes the model equations')
        word_rows[k] = rows
        R['words'][k] = {'path': WORDS[k], 'dyadic': True, 'owned_deliveries': len(D),
                         'delivery_supports': sorted(D.values()), 'weight52_deliveries': len(heavy),
                         'weight52_rank': len(B), 'all_deliveries_rank_mod3': len(rref3(list(D))),
                         'partner_owned_parts_rank_mod3': len(rref3(W3)),
                         'partner_owned_parts_inside_code': len(rref3(B + W3)) == 8,
                         'code_weight_distribution': wd_json(weight_distribution(B))}
        print(k, R['words'][k], flush=True)
    need(sign_equivalent(word_rows['pr5907'], word_rows['pr6030']), 'the two words carry sign-equivalent codes')
    need(sign_equivalent(e8_half, word_rows['pr5907']), 'the word code is the E8 Gram matrix / 2 mod 3, up to signs')
    R['words']['e8_gram_half_sign_equivalent'] = True

    # (5) controls that do not need the certificate
    bad = [r[:] for r in word_rows['pr5907']]
    t = T_INDEX[0]; m = next(m for m in range(104) if m != t and not dot(ports[t], ports[m]))
    bad[t][m] = (bad[t][m] + 1) % 3
    need(not model_fixture(ports, bad), 'control: one changed trit breaks the model equations')
    R['controls'] = {'changed_trit_rejected': True}

    # (2) certificate replay
    M, root, st, sols = replay(ports, {p: tokens(cert(p)) for p in parts}, NPARTS)
    R['root'] = root
    for p in parts:
        R['parts'][str(p)] = st[p]
    print('replayed parts', parts, R['parts'], '%.0fs' % (time.time() - t0), flush=True)

    # (3) the solution
    if sols:
        need(len(sols) == 1, 'one solution')
        basis = code_basis(M, sols[0]); rows = decoding_rows(basis, ports)
        need(rows is not None, 'the solution decodes at every port')
        cols = [[rows[l][m] for l in range(104)] for m in range(104)]
        need(sign_equivalent(rows, cols), 'decoding matrix is sign-equivalent to its transpose')
        wr, wc = weight_distribution(rref3(rows)), weight_distribution(rref3(cols))
        need(min(wr) == 49 and wr == wc and len(rref3(cols)) == 8, 'row and column codes: dim 8, minimum weight 49')
        for k in WORDS:
            need(sign_equivalent(rows, word_rows[k]), k + ': word code is sign-equivalent to the solution')
        R['solution'] = {'free_variables': 0,  # replay rejects a leaf with free variables
                         'decodes': True, 'symmetric_up_to_signs': True,
                         'weight_distribution': wd_json(wr), 'min_weight': min(wr),
                         'sign_equivalent_to': sorted(WORDS)}
        print('solution', R['solution'], flush=True)

    # (5) certificate controls on the first selected part
    p = parts[0]
    R['controls']['dead_node_with_options_rejected'] = bool(expect_failure(
        lambda: replay(ports, {p: tampered(p, 'dead')}, NPARTS), 'options'))
    R['controls']['early_solution_leaf_rejected'] = bool(expect_failure(
        lambda: replay(ports, {p: tampered(p, 'sol')}, NPARTS), 'unassigned ports'))

    # (6) receipt
    path = HERE / 'RESULT.json'
    old = json.loads(path.read_text()) if path.exists() else {}
    if write:
        merged = dict(old); merged.update({k: v for k, v in R.items() if k != 'parts'})
        merged['parts'] = dict(old.get('parts', {})); merged['parts'].update(R['parts'])
        path.write_text(json.dumps(merged, indent=1, sort_keys=True) + '\n'); old = merged
    for k, v in R.items():
        if k == 'parts':
            for p, s in v.items():
                need(old['parts'].get(p) == s, 'RESULT.json part ' + p)
        else:
            need(old.get(k) == v, 'RESULT.json section ' + k)
    need(sorted(old['parts']) == [str(p) for p in range(NPARTS)], 'RESULT.json records all parts')
    need(sum(s['solutions'] for s in old['parts'].values()) == 1, 'exactly one solution over all parts')
    need(sum(s['root_options'] for s in old['parts'].values()) == old['root']['options'], 'root options covered')
    print('PASS_P104_CARRIER_CODE_UNIQUENESS parts %s, %.0fs' % (parts, time.time() - t0), flush=True)


if __name__ == '__main__':
    main(sys.argv[1:])
