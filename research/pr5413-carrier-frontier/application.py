#!/usr/bin/env python3
"""Explicit changed-tuple adapters for the frozen PR5413 application checks.

Apache-2.0. Richard Hoekstra with OpenAI Codex assistance. The frozen checker,
written application and conjunction are Chris R/Clear1nsight's, with zxv's
compiler/precision and the retained native/controller lineage. No original
source or frozen manifest is changed: these adapters run only in scratch.
"""
import ast
import copy
import hashlib
import json
import os
import subprocess
import sys
from fractions import Fraction as Q
from pathlib import Path


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_bytes())


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')


def substitute(text, pairs):
    for old, new in pairs:
        need(text.count(old) == 1, 'unique source substitution: '+old)
        text = text.replace(old, new)
    return text


def decimal(x):
    x = Q(x)
    for digits in range(32):
        n = x*10**digits
        if n.denominator == 1:
            return str(n.numerator) if not digits else '.'+str(n.numerator).rjust(digits, '0')
    return str(x)


def precision_source(original):
    return substitute(original, [
        ('q=1024;ambient_log=8192',
         "q=data['funding']['tuple']['tensor_power'];ambient_log=8*q\n"
         "    need(type(q)is int and 1<=q<=1024,'compiler product domain')"),
        ("need(gap==(Q(fund['tested'])-Q(fund['kappa']))/7==Q(1,700000000000),'actual strict compiler gap')",
         "need(gap==(Q(fund['tested'])-Q(fund['kappa']))/7 and gap>0,'actual strict compiler gap')"),
        ("need(H==j*gap.denominator and (H+1)**1000<2**j,'actual funded carrier rank')",
         "power=fund['tuple']['logarithm_power']\n"
         "    need(type(power)is int and power>0 and type(j)is int and j>1, 'positive carrier parameters')\n"
         "    need(H==-((-j*gap.denominator)//gap.numerator) and H>8*q and (H+1)**power<2**j, 'actual funded carrier rank')\n"
         "    need((-((-(j-1)*gap.denominator)//gap.numerator)+1)**power>=2**(j-1), 'preceding carrier grid')"),
    ])


def proof_instance(original, case, funding):
    v, H = case['v'], funding['H']
    d = Q(funding['gap'])
    strictified = 2*(v*(2+2*128)+10+2*(8*v))+6+3*(8*v+1)
    need(strictified < 1048576, 'new expanded unit fits retained D0')
    pairs = [
        ('At q=1024 and raw maximum145,', f'At q={v} and raw maximum145,'),
        ('2*(1024*(2+2*128)+10+2*8192)+6+3*8193=585757<1048576.',
         f'2*({v}*(2+2*128)+10+2*{8*v})+6+3*{8*v+1}={strictified}<1048576.'),
        ('H=38569300000000000, N=2^H,', f'H={H}, N=2^H,'),
        ('The fresh strict tested/claim gap is1/700000000000.',
         f'The fresh strict tested/claim gap is {d}.'),
        ('log2D0=1048576, while H*gap=55099 and H*r0=5509.9.',
         f'log2D0=1048576, while H*gap={H*d} and H*r0={H*d/10}.'),
        ('The independent funding file uses K=.003027288235 and tested C=.003027288245,',
         f'The independent funding file uses K={decimal(case["k"])} and tested C={decimal(case["s"])},'),
        ('reserve10^-12, cutoff20/floor21, offset1/5, product1024, ambient145,\n'
         'theta63/64 and logarithm power1000.',
         f'the complete higher-moment paid sum, cutoff{case["c"]}/floor{case["b"]}, offset{case["u"]}, '
         f'product{v}, ambient145,\ntheta{case["theta"]} and logarithm power{case["p"]}.'),
    ]
    result = substitute(original, pairs)
    section = '''## Changed-tuple numerical application

This instance retains all raw native, owner, field-ID and route bindings.
The admitted higher-moment strictification theorem charges original paid
calls, the last incomplete split block, and completion of each actual owner.
Writing t=1-tested, u>=tested, J=cutoff^q and L=floor^q, its full normalized
paid-moment upper bound is alpha^q+2*gamma_u^q+2*delta^q. Each factor two
includes the residual split block. The exact directed certificate pays all
three terms and verifies their sum is strictly below one. The old .97 tail
envelope and Bernoulli/reserve debit were sufficient bounds on these same
jobs; they are replaced, not added as separate physical work.

The logarithmic compiler uses the new rational theta and positive integer
logarithm power, checking the true and shifted exit contractions, eta and
the full ordinary initial range. The carrier grid is H=ceil(j/gap), so
2^j<=2^(gap*H); the strict comparison (H+1)^power<2^j funds the same uniform
exponent. The unchanged four parameter layers use positive rational gap,
not a requirement that its numerator equal one. All 54+4 outer inequalities
are freshly checked. No old precision constant is reused from a smaller
raw template: the same fixed D0=2^1048576 dominates this new unit's explicit
count/height overestimate, and the source F16(N), stock and eventual outer
absorption arguments are reapplied at the new N. The five original
framework assumptions remain premises.

'''
    result = result.replace('## 6. D0 is not absorbed at the fixed carrier rank',
                            section+'## 6. D0 is not absorbed at the fixed carrier rank', 1)
    return result, pairs


def closure_source(original, case, funding, proof_sha):
    k, s, gap, H, j, power = case['k'], case['s'], Q(funding['gap']), funding['H'], funding['j'], case['p']
    replacements = {
        'exact_new_positive_endpoint_gap': f'''gate('exact_new_positive_endpoint_gap',
            F['case']=={case['name']!r} and k==Q({str(k)!r}) and c==Q({str(s)!r})
            and gap==(c-k)/7==Q({str(gap)!r}))''',
        'fresh_alpha_both_tails_completion_eta': '''gate('fresh_alpha_both_tails_completion_eta',
            verify_funding(root,F) and all(F['predicates'].values())
            and Q(F['alpha_upper'])<1-Q(F['reserve'])
            and Q(F['completion_slack'])>0)''',
        'strict_minimum_rounding_reserve': f'''gate('complete_paid_split_and_completion_bill',
            F['charging_model']=='complete-higher-moment-sum-with-both-partial-block-tails'
            and Q(F['original_paid_upper'])>=Q(F['alpha_upper'])**{case['v']}
            and Q(F['higher_tail_upper'])>=2*Q(F['gamma_upper'])**{case['v']}
            and Q(F['completion_tail_upper'])>=2*Q(F['delta_upper'])**{case['v']}
            and Q(F['normalized_paid_upper'])==sum(Q(F[x])for x in
              ['original_paid_upper','higher_tail_upper','completion_tail_upper'])<1)''',
        'fresh_height_and_preceding_height_grid': f'''gate('fresh_height_and_preceding_height_grid',
            H=={H} and j=={j} and H==ceilq(Q(j)/gap) and H>{8*case['v']}
            and (H+1)**{power}<2**j
            and (ceilq(Q(j-1)/gap)+1)**{power}>=2**(j-1))''',
        'fresh_constructive_F16_semantic_stock_bound': f'''gate('fresh_constructive_F16_semantic_stock_bound',
            expanded['strictified_log_upper']=={572*case['v']+29}<1048576
            and expanded['D0']=='2^1048576' and expanded['M']==f'F16(2^{{H}})'
            and expanded['N']==f'2^{{H}}' and expanded['actual_counts_bound']=='W,P,U,O,R,G <= M'
            and expanded['recursion']=='F16(0)=D0; X_n=(n+1)*(D0+1)*(F16(n-1)+1); F16(n)=X_n^(16*(n+1)^2)')''',
        'accepted_written_source_specialization': f'''gate('accepted_written_source_specialization',
            digest('precision_proof')=={proof_sha!r}
            and all(P['mathematical_application'][name].startswith('PROVED')for name in
              ['ordinary_class_specialization','expanded_construction','precision_stock_tape','recovery_class']))''',
    }
    tree = ast.parse(original)
    calls = {node.args[0].value: node for node in ast.walk(tree)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'gate'
             and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)}
    need(len(calls) == 25 and set(replacements) <= set(calls), 'original 25-premise inventory')
    lines = original.splitlines(keepends=True)
    for name in sorted(replacements, key=lambda name: calls[name].lineno, reverse=True):
        node = calls[name]
        replacement = '\n'.join('    '+line for line in replacements[name].splitlines())+'\n'
        lines[node.lineno-1:node.end_lineno] = [replacement]
    adapted = ''.join(lines)
    adapted = adapted.replace('def conjunction(root,manifest):',
        'from carrier_frontier import verify_funding, ceilq\n\ndef conjunction(root,manifest):', 1)
    adapted = adapted.replace("'gain_type':'tiny compiler/outer headroom; zero recursive economic gain'",
        "'gain_type':'smaller carrier; unchanged or explicitly weaker exponent; zero recursive economic gain'", 1)
    other_calls = {node.args[0].value: node for node in ast.walk(ast.parse(adapted))
                   if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'gate'
                   and node.args and isinstance(node.args[0], ast.Constant)}
    unchanged = sorted(set(calls)-set(replacements))
    need(len(other_calls) == 25 and len(unchanged) == 19, 'changed conjunction inventory')
    for name in unchanged:
        need(ast.dump(calls[name], include_attributes=False) == ast.dump(other_calls[name], include_attributes=False),
             'unchanged physical/source premise: '+name)
    return adapted, unchanged


def run_engine(package, workspace, engine, arguments):
    env = {k: v for k, v in os.environ.items() if not k.startswith('PYTHON')}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    run = subprocess.run([sys.executable, '-I', '-B', str(package/'engine_adapter.py'),
                          str(workspace), engine, *arguments], cwd=workspace,
                         env=env, capture_output=True, timeout=120)
    return run.returncode, run.stderr.decode(errors='replace')


def manifest(original, changes, workspace):
    result = copy.deepcopy(original)
    for row in result['rows']:
        if row['id'] in changes:
            row['path'] = changes[row['id']]
            row['sha256'] = sha(workspace/row['path'])
    if 'by_id' in result:
        result['by_id'].update(changes)
    return result
