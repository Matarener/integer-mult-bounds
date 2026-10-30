#!/usr/bin/env python3
"""Source-bound whole-word counterexample and sharp unit-rank fee gate for PR5270.

Prepared for zxv with substantial OpenAI Codex assistance. Apache-2.0.
Source exports retain DaysSky's and the credited controller authors' work.
Only authenticated function ASTs are executed; submitted modules are not imported.
"""
import argparse
import ast
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P, IMAG = 65537, 256


def need(ok, why):
    if not ok:
        raise ValueError(why)


@dataclass(frozen=True)
class ZI:
    """Exact Gaussian integers, independent of the address-loop residue field."""
    a: int = 0
    b: int = 0

    @staticmethod
    def of(x):
        if isinstance(x, ZI):
            return x
        q = Q(x)
        need(q.denominator == 1, 'integral specialized controller coefficient')
        return ZI(q.numerator)

    def __add__(self, other):
        x = self.of(other)
        return ZI(self.a+x.a, self.b+x.b)

    __radd__ = __add__

    def __neg__(self):
        return ZI(-self.a, -self.b)

    def __mul__(self, other):
        x = self.of(other)
        return ZI(self.a*x.a-self.b*x.b, self.a*x.b+self.b*x.a)

    __rmul__ = __mul__

    def __pow__(self, n):
        if n < 0:
            need(self.a*self.a+self.b*self.b == 1, 'inverse only of Gaussian units')
            return ZI(self.a, -self.b)**(-n)
        value, base = ZI(1), self
        while n:
            if n & 1:
                value = value*base
            n //= 2
            base = base*base
        return value

    def __bool__(self):
        return bool(self.a or self.b)

    def residue(self):
        return (self.a+IMAG*self.b) % P


UNITS = [ZI(1), ZI(0, 1), ZI(-1), ZI(0, -1)]


class EigenAlgebra:
    """Evaluate monomials on a physical Gaussian eigencharacter, over Z[i]."""
    def __init__(self, q_power, stage_powers):
        self.q = UNITS[q_power]
        self.stages = {s: UNITS[e] for s, e in stage_powers.items()}

    def plus(self, a, b, coefficient=1):
        out = dict(a)
        for key, value in b.items():
            out[key] = out.get(key, ZI())+coefficient*value
            if not out[key]:
                del out[key]
        return out

    def monomial_times(self, polynomial, exponents, coefficient=1):
        value = coefficient*(self.q**exponents[0])
        for s, exponent in enumerate(exponents[1:]):
            value = value*self.stages.get(s, ZI(1))**exponent
        return {key: v*value for key, v in polynomial.items() if v*value}


def parse(raw):
    return ast.parse(raw.decode('utf-8'))


def function(tree, name, namespace):
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    need(len(nodes) == 1, 'one authenticated definition of '+name)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<authenticated '+name+'>', 'exec'), namespace)
    return namespace[name]


def address_loop(tree, repaired=False, exact=False):
    import copy
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    loops = [n for n in main.body if isinstance(n, ast.For)
             and isinstance(n.target, ast.Name) and n.target.id == 'g'
             and isinstance(n.iter, ast.Name) and n.iter.id == 'gates']
    need(len(loops) == 1, 'unique actual address gate loop')
    loop = copy.deepcopy(loops[0])
    candidates = [n for n in ast.walk(loop) if isinstance(n, ast.For)
                  and ast.dump(n.iter) == ast.dump(ast.parse('enumerate(sel)', mode='eval').body)]
    need(len(candidates) == 1, 'actual IDLE decoder is enumerate(sel)')
    bad = candidates[0]
    need(ast.dump(bad.target) == ast.dump(ast.parse('for s, bit in []:\n pass').body[0].target),
         'IDLE decoder binds positions and literal stage numbers')
    need(len(bad.body) == 1 and isinstance(bad.body[0], ast.If)
         and ast.dump(bad.body[0].test) == ast.dump(ast.parse('bit and s in blocks', mode='eval').body),
         'actual IDLE condition')
    if repaired:
        bad.target = ast.Name(id='s', ctx=ast.Store())
        bad.iter = ast.Name(id='sel', ctx=ast.Load())
        bad.body[0].test = ast.parse('s in blocks', mode='eval').body
    if exact:
        class RemoveResidue(ast.NodeTransformer):
            def visit_BinOp(self, node):
                self.generic_visit(node)
                if isinstance(node.op, ast.Mod):
                    need(isinstance(node.right, ast.Name) and node.right.id == 'P', 'only reduce modulo P')
                    return node.left
                return node
        loop = RemoveResidue().visit(loop)
    module = ast.fix_missing_locations(ast.Module(body=[loop], type_ignores=[]))
    return compile(module, '<actual p19_bank gate loop>', 'exec')


def address_matrix(loop, p, gates, q_power, stage_powers, exact=False):
    """Execute the submitted loop on its invariant Walsh-character subspace.

    Each row holds independent ROLE coefficients, not a truncated address array.
    Axis Gaussians act diagonally here, so no physical address is approximated.
    """
    thick = list(range(1, 2*p, 2))
    blocks = {s: k for k, s in enumerate(thick)}
    centre = 8*len(thick)
    axis_powers = {centre: q_power}
    for s, exponent in stage_powers.items():
        for j in range(exponent):
            axis_powers[8*blocks[s]+j] = 1

    def butterfly(row, axis, power=1):
        if exact:
            factor = UNITS[axis_powers.get(axis, 0)]**power
            row[:] = [v*factor for v in row]
        else:
            factor = pow(IMAG, axis_powers.get(axis, 0)*power, P)
            row[:] = [v*factor % P for v in row]

    n = 2*p
    state = [[ZI(int(i == j)) if exact else int(i == j) for j in range(n)] for i in range(n)]
    exec(loop, dict(gates=gates, state=state, butterfly=butterfly, centre=centre, blocks=blocks, P=P))
    return state


def specialized(plain, controller_tree, p, pattern, q_power, stage_powers):
    algebra = EigenAlgebra(q_power, stage_powers)
    ns = {'Q': Q, 'C': algebra}
    controller = function(controller_tree, 'controller', ns)
    keep_of = function(controller_tree, 'keep_of', ns)
    trace = function(plain, 'traced_controller', {'Q': Q})
    coupling = {s: 1 for s in range(2*p+1)}
    keep = keep_of(p, pattern)
    co, _ = controller(p, keep, coupling)
    matrix, trace_co, gates, idle = trace(algebra, p, keep, coupling)
    need(co == trace_co, 'source controller and emitted trace agree on eigencharacter')
    wanted = [[sum((ZI.of(v) for v in cell.values()), ZI()) for cell in row] for row in matrix]
    return wanted, gates, idle


def mismatch(wanted, actual):
    return [[i, j, [v.a, v.b], actual[i][j]] for i, row in enumerate(wanted)
            for j, v in enumerate(row) if v.residue() != actual[i][j]]


def authenticate():
    manifest = json.loads((HERE/'SOURCE_EXPORTS.json').read_text())
    need(manifest['source_head'] == '225a19a184296d12120203a1f43b981d55465241', 'reviewed PR head')
    raw = {}
    for item in manifest['files']:
        data = (HERE/item['path']).read_bytes()
        need(sha256(data).hexdigest() == item['sha256'], 'export source hash '+item['path'])
        raw[Path(item['source_path']).name] = data
    for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if item['usage'] == 'input':
            need(sha256((ROOT/item['path']).read_bytes()).hexdigest() == item['sha256'], 'live source hash '+item['path'])
    return raw


def invoice_checks(raw):
    tree = parse(raw['p19_plain.py'])
    literals = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body
                if isinstance(n, ast.Assign) and len(n.targets) == 1
                and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ('H', 'PROF')}
    source_invoice = function(tree, 'invoice', dict(Counter=Counter, H=literals['H']))
    targets, paid = source_invoice(19, 'I'*9+'T'*9, set(range(1, 38, 2)), literals['PROF'])
    # Independent list census of all target banks, idle intervals and producer jobs.
    t, d = [153]*224, [1]*(20*112)
    for i, side in enumerate('I'*9+'T'*9, 1):
        length = i if side == 'I' else 19-i
        t += [1+8*length]*224
        d += [8*length]*224
    for r, n in literals['H'].items():
        t += [r]*(19*n)
    for r, n in literals['PROF'].items():
        d += [r]*(19*n)
    need(Counter(t) == targets and Counter(d) == paid, 'independent complete invoice')
    need((len(t), len(d), sum(t), sum(d)) == (12008, 68782, 265533, 263517), 'counts and rank masses')
    thresholds = sorted(set(targets)|set(paid))
    gaps = {k: 2016+sum(n*min(r, k) for r, n in paid.items())
               -sum(n*min(r, k) for r, n in targets.items()) for k in thresholds}
    need(gaps[153] == 0 and all(v > 0 for r, v in gaps.items() if r < 153), 'sharp truncated-mass certificate')
    need(sum(t)-sum(d)-2015 == 1, 'one fewer fee retains positive moment at t=1')
    path = ROOT/'research/higher-moment-strictification/verify.py'
    env = {'__name__': 'retained_intervals', '__file__': str(path)}
    exec(compile(path.read_bytes(), str(path), 'exec'), env)
    engine = SimpleNamespace(**env)

    def margin(c):
        x, y = engine.moment(targets, 1-c), engine.moment(paid, 1-c)
        return x[0]-y[1], x[1]-y[0]

    bracket = [Q('0.007578535189'), Q('0.007578535191')]
    need(margin(bracket[0])[0] > 0 and margin(bracket[1])[1] < 0, 'raw crossing bracket signs')
    bit, kappa, gap = Q('0.0034'), Q(951999, 280000000), Q(1, 1400000000)
    bit_margin = margin(bit)
    need(bit_margin[0] > 1103 and bit_margin[1] < 1104, 'sharp integer fee budget at admitted BIT cap')
    need(bit-kappa == 5*gap, 'outer endpoint is five grid steps below admitted BIT')
    controller = parse((ROOT/'research/coded-reverse-controller/verify.py').read_bytes())
    old_profile = next(ast.literal_eval(n.value) for n in controller.body if isinstance(n, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == 'P_OLD' for t in n.targets))
    old_targets, old_paid = source_invoice(19, 'I'*9+'T'*9, set(range(1, 38, 2)), old_profile)
    need(old_targets == targets, 'pre-PR4929 profile comparison keeps optimistic targets')
    def old_margin(c):
        x, y = engine.moment(old_targets, 1-c), engine.moment(old_paid, 1-c)
        return x[0]-y[1], x[1]-y[0]
    old_bracket = [Q('0.003004145206'), Q('0.003004145208')]
    need(old_margin(old_bracket[0])[0] > 0 and old_margin(old_bracket[1])[1] < 0,
         'pre-PR4929 profile raw crossing')
    need(old_margin(Q('0.003125804'))[1] < 0, 'pre-PR4929 profile misses selected kappa')
    with localcontext() as ctx:
        ctx.prec = 90
        exponent = Decimal(1)-Decimal(bit.numerator)/Decimal(bit.denominator)
        dm = sum(Decimal(n)*Decimal(r)**exponent for r, n in targets.items())
        dm -= sum(Decimal(n)*Decimal(r)**exponent for r, n in paid.items())
        need(Decimal(1103) < dm < Decimal(1104), 'independent Decimal price control')
    return {'target_count': len(t), 'paid_count': len(d), 'target_rank_mass': sum(t), 'paid_rank_mass': sum(d),
            'raw_crossing_sign_bracket': list(map(str, bracket)), 'sharp_extra_H1_threshold': 2016,
            'truncated_mass_gaps_after_2016_H1': {str(r): v for r, v in gaps.items()},
            'at_BIT_0034_extra_H1_budget': 1103, 'decimal_margin_at_BIT_0034': str(dm),
            'claimed_outer_kappa': str(kappa), 'admitted_BIT': str(bit),
            'tested_complex': str(kappa+7*gap), 'conditional_uniform_complex': str(kappa+6*gap),
            'pre_PR4929_profile_control': {'profile': old_profile,
                'raw_crossing_sign_bracket': list(map(str, old_bracket)),
                'negative_margin_at_selected_kappa_003125804': True},
            'fees_2128_and_4256_excluded_for_every_0_t_1': True}


def check():
    raw = authenticate()
    plain, bank = parse(raw['p19_plain.py']), parse(raw['p19_bank.py'])
    controller = parse((ROOT/'research/coded-reverse-controller/verify.py').read_bytes())
    original, repaired = address_loop(bank), address_loop(bank, repaired=True)
    integral_loop = address_loop(bank, exact=True)
    need(pow(IMAG, 2, P) == P-1, 'Gaussian integer residue homomorphism')
    grid = {}
    for pattern in ('I', 'T'):
        failures = fixed = 0
        for q in range(2):
            for e1 in range(4):
                for e3 in range(4):
                    wanted, gates, _ = specialized(plain, controller, 2, pattern, q, {1: e1, 3: e3})
                    failures += bool(mismatch(wanted, address_matrix(original, 2, gates, q, {1: e1, 3: e3})))
                    fixed += bool(mismatch(wanted, address_matrix(repaired, 2, gates, q, {1: e1, 3: e3})))
        need(failures == (0 if pattern == 'I' else 24) and fixed == 0, 'p2 Gaussian eigenvalue triples')
        grid[pattern] = {'triples': 32, 'submitted_loop_failures': failures, 'repaired_loop_failures': fixed}
    witnesses = {}
    for p, pattern, active, count in [(2, 'T', 3, 4), (3, 'IT', 5, 8), (19, 'I'*9+'T'*9, 37, 72)]:
        wanted, gates, idle = specialized(plain, controller, p, pattern, 0, {active: 1})
        physical = address_matrix(original, p, gates, 0, {active: 1})
        integral = address_matrix(integral_loop, p, gates, 0, {active: 1}, exact=True)
        need(all(v.residue() == physical[i][j] for i, row in enumerate(integral) for j, v in enumerate(row)),
             'independent exact Gaussian-integer and submitted residue-loop agreement')
        bad = mismatch(wanted, physical)
        need(len(bad) == count, 'whole-word eigencharacter mismatch p='+str(p))
        need(not mismatch(wanted, address_matrix(repaired, p, gates, 0, {active: 1})), 'protocol repair positive control')
        witnesses[str(p)] = {'pattern': pattern, 'central_eigenvalue': [1, 0], 'active_stage': active,
                            'active_eigenvalue': [0, 1], 'all_other_stage_eigenvalues': [1, 0],
                            'gate_count': len(gates), 'mismatches': bad,
                            'pulse_input_role': 2*p-2, 'pulse_output_role': 0,
                            'pulse_expected': [wanted[0][2*p-2].a, wanted[0][2*p-2].b],
                            'pulse_actual': [integral[0][2*p-2].a, integral[0][2*p-2].b],
                            'retained_terminal_events': [r for r in idle if r['retained'] and r['kind'] == 'terminal']}
    A = [[Q(v) for v in row] for row in json.loads((ROOT/'research/coded-native-caller/CODE.json').read_text())['A']]
    need(len(A) == 112 and all(len(row) == 112 and row[j] == 0 for j, row in enumerate(A)), '112 zero native diagonal blocks')
    return {'status': 'PASS_P19_CURRENT_HEAD_BINDING_AUDIT', 'source_head': '225a19a184296d12120203a1f43b981d55465241',
            'p2_eigenvalue_grid': grid, 'whole_word_witnesses': witnesses, 'native_same_owner_zero_blocks': 112,
            'price': invoice_checks(raw), 'scope': 'Exact source-bound counterexamples and fixed-invoice fee theorem; no new supplier, admission, global decoder lower bound or kappa.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = check()
    encoded = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.write:
        (HERE/'RESULT.json').write_text(encoded)
    else:
        need((HERE/'RESULT.json').read_text() == encoded, 'fresh result equals committed mathematical receipt')
    print(result['status']+' head='+result['source_head']+' p19_mismatches=72 sharp_H1_fee=2016 no_new_kappa')


if __name__ == '__main__':
    main()
