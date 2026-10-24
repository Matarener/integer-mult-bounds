#!/usr/bin/env python3
"""Part 2: the complete #5413 runtime body with the #5402 provider expanded, and the controller level.

Standard library only; well under a minute.  Inputs, pinned by SHA256 in SOURCES.json (all on main inside the #5413
package capsule): NEUTRAL-BACKWARD-v16c.json (the only runtime local direction: 18 backward bodies, no forward macro
calls), NEUTRAL-CALLER-v16c.json (controller), the #5402 PROVIDER.json and its WORD.json.gz; the eight-relation
WORD.json.gz supplies the canonical frames (same nine-axis chart system) for Fourier ranks.

Body: execute the body operations in order; PROVIDER_5402 expands per PROVIDER.json ordered_schedule (main input
wrappers, mode input_K and scalar 2, input_basis_program, provider word, output_basis_program, cache scalar / output_N
/ SWAP / CLEAR, main output wrappers). Every monomial map, GAUSSIAN and native warp is kept as a symbol in the term's
word, so terms through different operator paths never merge (merging could only lower 2-adic exponents: the census
is an upper bound). Checks: no odd denominator; all 17 owned fields zero at exit; S = max v2 = 6, attained by the
part-1 witness (provider word event 19465, input 470 once, coefficient -1/64, one alias monomial, Fourier rank 9).
Exact body guard ceil(9 lambda/2) + 6. By input class: helper terms v2 <= 6 with local rank <= 9; main terms have
Pareto front {(3,9),(4,0)} in (v2, local rank), with single-occurrence witnesses.

Controller: all bank-level coefficients are integers (ADD +-1, SCALE -1, SWAP, 0/1 boundaries); each of the 18 body
calls receives fresh independent helper fields; 224 productive targets have rank 145 on the 145-axis global
geometry. Rigorous bracket for one controller level: 73 <= guard <= 77 (rank-145 targets with unit coefficient need
ceil(145/2) = 73; main-data terms have v2 <= 4 and rank <= 145; fresh helper terms need at most 6 + ceil(9/2) = 11).
The exact value inside the bracket needs the global 145-axis charts and is left open.
Usage: python3 -I -B caller.py [--write]
"""
import argparse, collections, gzip, hashlib, importlib.util, json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CAP = ROOT / 'research' / 'coupled-helper-neutral-completion' / 'capsule' / 'workspace'
BODY = CAP / 'swarm-coupled-caller-sol-high-20261024' / 'agents' / 'caller' / 'NEUTRAL-BACKWARD-v16c.json'
CALLER = CAP / 'swarm-coupled-caller-sol-high-20261024' / 'agents' / 'caller' / 'NEUTRAL-CALLER-v16c.json'
PROV = CAP / 'swarm-provider-audit-sol-high-20261024' / 'repository' / 'research' / 'native-rank8-helper-provider'
EIGHT = ROOT / 'research' / 'eight-owned-relations' / 'WORD.json.gz'
CLIFFORD = ROOT / 'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py'


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


def pinned_inputs():
    rows = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))['files']
    for row in rows:
        if row['usage'] == 'input':
            data = (ROOT / row['path']).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row['sha256'], 'input drift: ' + row['path'])


def v2(n):
    n = abs(n)
    return (n & -n).bit_length() - 1


class Body:
    def __init__(self, body, prov, word, canonical, ce):
        self.body, self.prov, self.word, self.c, self.ce = body, prov, word, canonical, ce
        self.bind = body['physical_field_bindings']
        nf = body['physical_field_count']
        self.rows = {i: {(i, ()): Q(1)} for i in range(nf)}
        self.sym = 0; self.S = 0; self.S_at = None; self.odd = 0; self.l1 = Q(0)
        self.cls = {}; self.main = {}; self.frames = {}; self.inword = False
        self.charts = {}; self.ranks = {}; self.witness = None

    def rank(self, F, I):
        if (F, I) not in self.ranks:
            for f in (F, I):
                if f not in self.charts:
                    self.charts[f] = self.ce.canonical_frame(9, self.c['frames'][f])
            op = self.charts[I].adjoint().then(self.charts[F])
            self.ranks[(F, I)] = self.ce.rank([x for x, z, p in op.tab[9:]])
        return self.ranks[(F, I)]

    def newsym(self, tag):
        self.sym += 1
        return (tag, self.sym)

    def apply(self, f, s):
        self.rows[f] = {(inp, wd + (s,)): q for (inp, wd), q in self.rows[f].items()}

    def stat(self, where, f):
        r = self.rows[f]
        if not r:
            return
        occ = collections.Counter(inp for inp, wd in r)
        self.l1 = max(self.l1, sum(abs(q) for q in r.values()))
        for (inp, wd), q in r.items():
            e = v2(q.denominator)
            if q.denominator >> e != 1:
                self.odd += 1
            if e > self.S:
                self.S, self.S_at = e, [str(where), f]
            cl = 'main' if inp < 224 else 'helper' if inp < 632 else 'owned'
            self.cls[cl] = max(self.cls.get(cl, 0), e)
            if self.inword and self.frames.get(f) is not None and inp < 632:
                single = occ[inp] == 1 and not any(s[0] == 'W' for s in wd)
                r_loc = self.rank(self.frames[f], self.c['start'][inp])
                if cl == 'main':
                    key = (e, r_loc)
                    if key not in self.main or (single and not self.main[key][0]):
                        self.main[key] = (single, str(where), f, inp, str(q))
                elif e == 6 and single and r_loc == 9 and self.witness is None:
                    self.witness = [str(where), f, inp, str(q), r_loc]

    def add(self, dst, src, q, where):
        d = self.rows[dst]
        for k, v in self.rows[src].items():
            nv = d.get(k, 0) + q * v
            if nv:
                d[k] = nv
            else:
                d.pop(k, None)
        self.stat(where, dst)

    def scale(self, f, q, where):
        self.rows[f] = {k: q * v for k, v in self.rows[f].items()}
        self.stat(where, f)

    @staticmethod
    def role(r):
        if isinstance(r, int):
            return r
        return r[1] if r[0] == 'L' else 632 + r[1]

    def provider(self):
        p = self.prov
        for f in range(224):
            self.apply(f, self.newsym('Nin'))
        for m in p['mode_boundaries']:
            self.apply(m['owner'], self.newsym('K')); self.scale(m['owner'], Q(2), 'mode_scalar')
        for ins in p['input_basis_program']:
            if ins[0] == 'add':
                self.add(ins[1], ins[2], Q(ins[3]), 'input_basis')
            else:
                self.scale(ins[1], Q(ins[2]), 'input_basis')
        self.inword = True
        self.frames = {i: self.c['start'][i] for i in range(632)}
        for t, e in enumerate(self.word['word']):
            k = e[0]
            if k == 'warp':
                self.apply(self.role(e[1]), ('W', e[2]))
                if e[1][0] == 'L':
                    self.frames[e[1][1]] = e[4]
            elif k == 'climb':
                self.frames[e[2]] = e[4]
            elif k == 'scalar':
                g = e[1]; d_ = self.role(g[1])
                if g[1][0] == 'L' and e[2] is not None:
                    self.frames[g[1][1]] = e[2]
                if g[0] == 'clear':
                    self.rows[d_] = {}
                elif g[0] == 'copy':
                    self.rows[d_] = dict(self.rows[self.role(g[2])]); self.stat(('word', t), d_)
                elif g[0] == 'add':
                    self.add(d_, self.role(g[2]), Q(g[3], g[4]), ('word', t))
                elif g[0] == 'scale':
                    self.scale(d_, Q(g[2], g[3]), ('word', t))
                else:
                    require(False, 'unknown provider scalar')
            elif k == 'zero_retag':
                require(not self.rows[self.role(e[1])], 'provider zero retag on a zero row')
            else:
                require(k in ('center', 'adapter', 'phase'), 'unknown provider event')
        self.inword = False
        for ins in p['output_basis_program']:
            if ins[0] == 'add':
                self.add(ins[1], ins[2], Q(ins[3]), 'output_basis')
            else:
                self.scale(ins[1], Q(ins[2]), 'output_basis')
        for m in p['mode_boundaries']:
            cs, o = m['cache_slot'], m['owner']
            self.scale(cs, Q(m['cache_scalar']), 'cache_scalar'); self.apply(cs, self.newsym('N'))
            require(not self.rows[o], 'mode owner zero before the cache SWAP')
            self.rows[cs], self.rows[o] = self.rows[o], {}
        for f in range(224):
            self.apply(f, self.newsym('Nout'))

    def run(self):
        b = self.bind
        for n, o in enumerate(self.body['operations']):
            k = o['op']
            if k == 'MONOMIAL':
                self.apply(b[o['field']], self.newsym('M'))
            elif k == 'GAUSSIAN':
                self.apply(b[o['field']], self.newsym('G'))
            elif k == 'ADD':
                self.add(b[o['dst']], b[o['src']], Q(o['coefficient']), ('body', n))
            elif k == 'CLEAR':
                self.rows[b[o['field']]] = {}
            elif k == 'ZERO_RETAG':
                require(not self.rows[b[o['field']]], 'body zero retag on a zero row')
            elif k == 'SWAP':
                x, y = (b[f] for f in o['fields']); self.rows[x], self.rows[y] = self.rows[y], self.rows[x]
            elif k == 'PROVIDER_5402':
                self.provider()
            else:
                require(False, 'unknown body operation ' + k)
        owned = [b[f] for f in b if f[0] in 'ct']
        require(len(owned) == 17 and all(not self.rows[f] for f in owned), 'all 17 owned fields zero at exit')


def controller(caller):
    c = caller['controller']; ev = c['physical_events']
    require(c['ambient_rank'] == 145 and c['kind'] == 'complex', '145-axis complex controller')
    require(caller['runtime_local_directions'] == {'backward': 18, 'forward_macro_calls': 0}, 'only backward bodies run')
    adds = [e for e in ev if e[0] == 'ADD']
    require(all(e[3] in (1, -1) for e in adds), 'bank ADD coefficients are +-1')
    progs = c['boundaries']['left_program'] + c['boundaries']['right_program']
    require(all(str(x[-1]) in ('1', '-1') for x in progs if x[0] in ('ADD', 'SCALE')), 'boundary program coefficients +-1')
    require(all(x[0] in ('ADD', 'SCALE', 'SWAP') for x in progs), 'boundary programs use ADD, SCALE, SWAP only')
    require(set(v for r in c['diagonal'] for v in r) <= {-1, 0, 1}, 'diagonal entries in {-1,0,1}')
    calls = [o for o in caller['typed_emission'] if o['op'] == 'CALL_NEUTRAL_BACKWARD']
    fresh = [f for o in calls for f in o['original_independent_helper_fields']]
    require(len(calls) == 18 and len(fresh) == len(set(fresh)) == 18 * 408, 'eighteen calls with fresh helper fields')
    main_targets = sorted(int(r) for r in caller['productive_profile'] if int(r) > 9)
    require(max(main_targets) == 145 and caller['productive_profile']['145'] == 224, '224 productive targets of rank 145')
    return dict(bank_events=dict(collections.Counter(e[0] for e in ev)), main_target_ranks=main_targets,
                fresh_helper_fields=len(fresh), integer_controller_coefficients=True)


def build():
    pinned_inputs()
    spec = importlib.util.spec_from_file_location('selected_grid_clifford_exact_caller', CLIFFORD)
    ce = importlib.util.module_from_spec(spec); spec.loader.exec_module(ce)
    body = json.loads(BODY.read_text(encoding='utf-8'))
    caller = json.loads(CALLER.read_text(encoding='utf-8'))
    require(caller['local_backward_sha256'] == hashlib.sha256(BODY.read_bytes()).hexdigest(), 'controller binds this body')
    prov = json.loads((PROV / 'PROVIDER.json').read_text(encoding='utf-8'))
    word = json.loads(gzip.decompress((PROV / 'WORD.json.gz').read_bytes()))
    require(word['direction'] == 'backward', 'backward provider word')
    canonical = json.loads(gzip.decompress(EIGHT.read_bytes()))['canonical']
    B = Body(body, prov, word, canonical, ce)
    B.run()
    require(B.odd == 0, 'every coefficient of the complete body is dyadic')
    require(B.S == 6 and B.witness is not None, 'body maximum v2 = 6 with a single-occurrence rank-9 helper witness')
    keys = list(B.main)
    front = sorted(k for k in keys if not any(o != k and o[0] >= k[0] and o[1] >= k[1] for o in keys))
    require(front == [(3, 9), (4, 0)], 'main-data Pareto front {(3,9),(4,0)}')
    require(B.main[(3, 9)][0] and B.main[(4, 0)][0], 'single-occurrence main witnesses')
    require(B.cls['main'] == 4 and B.cls['helper'] == 6, 'class maxima: main 4, helper 6')
    ctl = controller(caller)
    ceil = lambda r: -(-r // 2)
    require((ceil(145), max(4 + ceil(145), 6 + ceil(9))) == (73, 77), 'controller bracket')
    return dict(body=dict(max_v2=B.S, max_v2_at=B.S_at, witness=B.witness, odd_denominators=0, max_l1=str(B.l1),
                          class_max_v2=B.cls, main_front=[list(k) for k in front],
                          main_witnesses={str(list(k)): B.main[k] for k in front},
                          guard='ceil(9 lambda/2) + 6 (attained)'),
                controller=dict(ctl, rigorous_bracket=[73, 77],
                                bracket_reason='lower: rank-145 targets with unit coefficient; upper: main-data v2 <= 4 with rank <= 145, fresh helper terms <= 6 + ceil(9/2)'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    result = build()
    path = HERE / 'RESULT-CALLER.json'
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if args.write:
        path.write_bytes(text.encode('utf-8'))
    require(path.exists() and json.loads(path.read_text(encoding='utf-8')) == json.loads(text), 'stored RESULT-CALLER.json equals the rebuild')
    print('PASS_SELECTED_CALLER_BODY_GRID_6_CONTROLLER_73_TO_77')


if __name__ == '__main__':
    main()
