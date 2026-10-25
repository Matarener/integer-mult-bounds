#!/usr/bin/env python3
"""Registered replay for research/s4-mixed-tuple-tight-word-search.

Default (Python stdlib, about two minutes): recomputes the count lemma from cut values, checks
an explicit cost-21 direct word for T in exact F2[S4] arithmetic, replays the separately written
explicit-matrix pruned search (both whole r=3 sub-tuple trees, first three r=4 depths, r=5 depth
1), the unpruned group-algebra brute-force count, the exact recheck of the pruned r=2 control
words, positive and negative controls, and compares everything with RESULT.json. The default
replay does NOT re-derive the r=4/r=5 exclusion (depths 4-8): only --full does. --full also
compiles the two C++ engines (g++ with OpenMP), replays the complete r=4 and r=5 searches in both
engines (15 to 20 minutes on 3 threads) and replays the sub-tuple cut LPs (cutlp.cpp + lp.py).
--self-test checks that perturbed RESULT.json values are rejected.
Sagar Thakrar (thakrarsagar), with substantial AI assistance from Claude. Apache-2.0.
"""
import ast, copy, heapq, json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import independent, brute  # noqa: E402

TUPLE = ['2143', '3142', '4231', '2143']


def count_lemma():
    """Integer label counts (n1,n2,n3) of cost <= 20 allowed by the inv, c1, c3 cut bounds."""
    phi = {}
    for c, (mod, f) in independent.CUTH.items():
        M = independent.big(lambda i, j, mod=mod: independent.rep(independent.perm(TUPLE[i]), mod) if i == j else None,
                            4, len(independent.POINTS[mod]))
        phi[c] = independent.block_rank(M, 4, mod, f, True)
    ok = [(a, b, c) for a in range(11) for b in range(21) for c in range(11)
          if 2 * a + b + 2 * c <= 20 and a + b + c >= phi['inv'] and a >= phi['c1'] and c >= phi['c3']]
    return phi, ok


def direct_words():
    """Cheapest word over (s1,s2,s3) at prices (2,1,2) for each target (Dijkstra on S4), the r=4
    diagonal word built from them, and an exact F2[S4] check that this word equals T."""
    price = {1: 2, 2: 1, 3: 2}; e = independent.perm('1234')
    best = {e: (0, [])}; heap = [(0, [], e)]
    while heap:
        c, w, x = heapq.heappop(heap)
        if best[x][0] < c: continue
        for s in (1, 2, 3):
            y = independent.compose(x, independent.GENS[s])
            if y not in best or c + price[s] < best[y][0]:
                best[y] = (c + price[s], w + [s]); heapq.heappush(heap, (c + price[s], w + [s], y))
    r = len(TUPLE); word = [(s, 1 << i, 1 << i) for i, t in enumerate(TUPLE) for s in best[independent.perm(t)][1]]
    M = tuple(tuple(frozenset({brute.E}) if i == j else frozenset() for j in range(r)) for i in range(r))
    for g in word: M = brute.mmul(M, brute.gate(*g, r))
    T = tuple(tuple(frozenset({brute.perm(TUPLE[i])}) if i == j else frozenset() for j in range(r)) for i in range(r))
    return {t: best[independent.perm(t)][0] for t in sorted(set(TUPLE))}, sum(price[g[0]] for g in word), M == T


def exact_words(targets, words):
    """Words (peel order L_n..L_1) with T L_n ... L_1 = I exactly in F2[S4] (frozenset arithmetic)."""
    r = len(targets)
    I = tuple(tuple(frozenset({brute.E}) if i == j else frozenset() for j in range(r)) for i in range(r))
    T = tuple(tuple(frozenset({brute.perm(targets[i])}) if i == j else frozenset() for j in range(r)) for i in range(r))
    out = []
    for w in words:
        M = T
        for g in w: M = brute.mmul(M, brute.gate(*g, r))
        if M == I: out.append(w)
    return out


def run_default():
    got = {}
    phi, ok = count_lemma()
    got['cut_values'] = phi
    got['cost_le_20_counts'] = [list(x) for x in ok]
    n3, f3, _ = independent.search(['4231', '2143', '2143'], (3, 3, 3))
    got['r3_subtuple_nodes'] = n3; got['r3_subtuple_survivors'] = len(f3)
    n3b, f3b, _ = independent.search(['2143', '3142', '4231'], (3, 4, 3))
    got['r3b_subtuple_nodes'] = n3b; got['r3b_subtuple_survivors'] = len(f3b)
    got['direct_costs'], got['direct_total'], got['direct_word_equals_T'] = direct_words()
    n4, _, g4 = independent.search(TUPLE, (4, 4, 4), maxdepth=3)
    got['r4_first3'] = n4[:3]; got['r4_gates'] = g4
    n5, _, g5 = independent.search(TUPLE + ['1234'], (4, 4, 4), maxdepth=1)
    got['r5_depth1'] = n5[0]; got['r5_gates'] = g5
    got['brute_r2_words'] = brute.count(['4231', '2143'], (3, 2, 2), 3)[0]
    _, f2, _ = independent.search(['4231', '2143'], (3, 2, 2))  # full-depth window survivors
    w2 = exact_words(['4231', '2143'], f2)
    got['r2_independent_survivors'] = len(f2); got['r2_independent_exact_words'] = len(w2)
    got['r2_mixing_words'] = sum(any(u == 3 or v == 3 for (_, u, v) in w) for w in w2)
    got['neg_4231_131_pruned'] = len(independent.search(['4231'], (1, 3, 1))[1])
    got['neg_4231_131_brute'] = brute.count(['4231'], (1, 3, 1), 2)[0]
    got['pos_4312_131_pruned'] = len(independent.search(['4312'], (1, 3, 1))[1])
    got['pos_4312_131_brute'] = brute.count(['4312'], (1, 3, 1), 2)[0]
    return got


def compare(got, res):
    exp = res['replay_expectations']
    bad = [k for k in exp if got.get(k) != exp[k]]
    r4 = res['runs']['r4_primary']['nodes_per_depth']
    if got['r4_first3'] != r4[:3]: bad.append('r4_first3 vs primary run')
    if got['r5_depth1'] != res['runs']['r5_primary']['depth1_survivors_before_symmetry']: bad.append('r5 depth1 vs primary')
    if got['brute_r2_words'] != res['controls']['r2_pruned_primary_words']: bad.append('brute vs pruned primary count')
    if got['r2_independent_exact_words'] != got['brute_r2_words']: bad.append('independent exact words vs brute count')
    if res['runs']['r4_primary']['words'] != 0 or res['runs']['r5_primary']['words'] != 0: bad.append('recorded words nonzero')
    return bad


def run_full(res):
    out = {}
    with tempfile.TemporaryDirectory() as td:
        for src in ('search.cpp', 'indep.cpp'):
            subprocess.run(['g++', '-O2', '-fopenmp', '-o', os.path.join(td, src[:-4]), os.path.join(HERE, src)], check=True)
        env = dict(os.environ, OMP_NUM_THREADS=os.environ.get('OMP_NUM_THREADS', '3'))
        r = subprocess.run([os.path.join(td, 'search'), '4', '0', '12', '4', '4', '4'] + TUPLE + ['10'], capture_output=True, text=True, env=env, check=True)
        out['r4_primary'] = [l for l in r.stdout.splitlines() if l.startswith('RESULT')][0]
        envs = dict(env, SYM='1', SYM_A='0', SYM_B='3', SYM_D='1')
        r = subprocess.run([os.path.join(td, 'search'), '5', '0', '12', '4', '4', '4'] + TUPLE + ['1234', '10'], capture_output=True, text=True, env=envs, check=True)
        out['r5_primary'] = [l for l in r.stdout.splitlines() if l.startswith('RESULT')][0]
        r = subprocess.run([os.path.join(td, 'indep'), '4', '4', '4', '4'] + TUPLE + ['all'], capture_output=True, text=True, env=env, check=True)
        out['r4_indep'] = r.stdout.splitlines()[-1]
        reps = ','.join(map(str, res['runs']['r5_primary']['orbit_representatives_searched']))
        r = subprocess.run([os.path.join(td, 'indep'), '5', '4', '4', '4'] + TUPLE + ['1234', reps], capture_output=True, text=True, env=env, check=True)
        out['r5_indep'] = r.stdout.splitlines()[-1]
        subprocess.run(['g++', '-O2', '-o', os.path.join(td, 'cutlp'), os.path.join(HERE, 'cutlp.cpp')], check=True)
        cuts = os.path.join(td, 'cuts.txt')
        with open(cuts, 'w') as fh: subprocess.run([os.path.join(td, 'cutlp')], stdout=fh, check=True)
        r = subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, 'lp.py'), cuts], capture_output=True, text=True, check=True)
        lps = {}
        for line in r.stdout.splitlines():
            name = line.split()[0]; lp = re.search(r'LP=(\S+)', line).group(1)
            n = [str(x) for x in ast.literal_eval(re.search(r'dual_y=(\(.*?\))', line).group(1))]
            lps[name] = (lp, n)
    exp = res['full_replay_expectations']
    bad = [k for k in exp if out.get(k) != exp[k]]
    for key, rec in res['lp_subtuples'].items():
        if key == 'method': continue
        lp, n = lps.get(key, (None, None))
        if lp != rec['lp'] or ('optimal_label_counts_n' in rec and n != [str(x) for x in rec['optimal_label_counts_n']]):
            bad.append('lp ' + key)
    out['lp_subtuples'] = {k: v[0] for k, v in lps.items()}
    return out, bad


def main():
    res = json.load(open(os.path.join(HERE, 'RESULT.json')))
    if '--self-test' in sys.argv:
        got = run_default()
        assert compare(got, res) == [], compare(got, res)
        bad = copy.deepcopy(res); bad['replay_expectations']['r3_subtuple_nodes'][3] += 1
        assert compare(got, bad), 'perturbed expectation was not rejected'
        bad = copy.deepcopy(res); bad['runs']['r4_primary']['nodes_per_depth'][1] -= 1
        assert compare(got, bad), 'perturbed primary run was not rejected'
        bad = copy.deepcopy(res); bad['controls']['r2_pruned_primary_words'] += 1
        assert compare(got, bad), 'perturbed control count was not rejected'
        print('PASS_SELF_TEST perturbed RESULT values rejected'); return
    got = run_default()
    bad = compare(got, res)
    if bad:
        print('FAIL', bad, json.dumps(got)); raise SystemExit(1)
    print('cost<=20 counts allowed by inv/c1/c3 cuts:', got['cost_le_20_counts'])
    print('direct word: costs', got['direct_costs'], 'total', got['direct_total'], 'equals T exactly:', got['direct_word_equals_T'])
    print('r=3 sub-tuple trees (independent): (4231,2143,2143)', got['r3_subtuple_nodes'], 'survivors', got['r3_subtuple_survivors'],
          '; (2143,3142,4231)', got['r3b_subtuple_nodes'], 'survivors', got['r3b_subtuple_survivors'])
    print('r=4 first three depths (independent):', got['r4_first3'], 'r=5 depth-1 survivors:', got['r5_depth1'])
    print('unpruned brute-force words (r=2 control):', got['brute_r2_words'], '= pruned primary', res['controls']['r2_pruned_primary_words'],
          '= exact-checked independent survivors', got['r2_independent_exact_words'], 'of', got['r2_independent_survivors'], '(mixing:', got['r2_mixing_words'], ')')
    if '--full' in sys.argv:
        out, badf = run_full(res)
        if badf:
            print('FAIL_FULL', badf, json.dumps(out)); raise SystemExit(1)
        print('full replay:', json.dumps(out))
    print('PASS_S4_MIXED_TUPLE_WINDOW_SEARCH no cost-20 word on r=4 or r=5 roles (recorded searches); r=6+ not searched')


if __name__ == '__main__':
    main()
