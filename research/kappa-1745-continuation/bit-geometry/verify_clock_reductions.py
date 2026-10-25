#!/usr/bin/env python3
"""Check the quotient mechanism against every small GL basis and B4 natively.

The coefficient-space GL enumeration is independent of the search's split
construction. This verifies its orbit reduction, not a second full K4 search.
The positive controller and omission controls use exact integer matrices.
Apache-2.0; substantial OpenAI assistance; predecessor credit in the proof.
"""
from collections import Counter
from hashlib import sha256
from itertools import product
from pathlib import Path
import ast
import importlib.util
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SEARCH = HERE/'controller_clock_orbits.py'
RECIPE = REPO/'research/kappa-next-regime/sources/PR3647/research/bit-p111-r437-gl464-470-20261018/vendor/global_k.py'


def span(rows):
    out = {0}
    for row in rows:
        out |= {x^row for x in tuple(out)}
    return frozenset(out)


def all_bases(k):
    def visit(rows,space):
        if len(rows) == k:
            yield tuple(rows); return
        for row in range(1,1 << k):
            if row not in space:
                yield from visit(rows+[row],space | {x^row for x in space})
    yield from visit([],{0})


def main():
    spec = importlib.util.spec_from_file_location('actual_clock_search',SEARCH)
    orbit = importlib.util.module_from_spec(spec); spec.loader.exec_module(orbit)
    rows = []
    for k in range(1,5):
        expected = set(); bases = 0
        for A in all_bases(k):
            bases += 1
            # Column i of A inverse is the unique vector b with A*b=e_i;
            # these columns are rows of A inverse transpose.
            dual = tuple(next(b for b in range(1,1 << k)
                              if tuple((a&b).bit_count()%2 for a in A)
                              == tuple(int(i == j) for j in range(k)))
                         for i in range(k))
            expected.add((A[0],dual[0],span(A[1:]),span(dual[1:])))
        orbit.K = k; orbit.canonical.cache_clear(); orbit.split_pairs.cache_clear()
        top = tuple(1 << i for i in range(k))
        bottom = tuple(1 << (k+i) for i in range(k))
        actual = {(x,y >> k,span(xt),frozenset(z >> k for z in span(yt)))
                  for x,y,xt,yt in orbit.split_pairs(top,bottom)}
        assert actual == expected
        assert len(expected) == ((1 << k)-1)*(1 << (k-1))
        assert bases == __import__('math').prod((1 << k)-(1 << j) for j in range(k))
        rows.append({'dimension':k,'all_GL_matrices':bases,'paired_split_orbits':len(expected),
                     'independent_full_GL_enumeration_equals_search_splits':True})
    # Extract the frozen integer recipe without importing its execution tree.
    node = next(n for n in ast.parse(RECIPE.read_text()).body if isinstance(n,ast.FunctionDef) and n.name == 'recipe')
    ns = {}; exec(compile(ast.Module(body=[node],type_ignores=[]),str(RECIPE),'exec'),ns)
    events = ns['recipe'](4)
    identity = [[int(i == j) for j in range(8)] for i in range(8)]
    def replay(skip=None,bad_dual=False):
        matrix = [row[:] for row in identity]
        def add(d,s,c):
            matrix[d] = [x+c*y for x,y in zip(matrix[d],matrix[s])]
        for j,event in enumerate(events):
            if j == skip:
                continue
            if event['kind'] == 'local':
                p = event['pair']; reverse = event['reverse']
                add(2*p,2*p+1,-1) if reverse else add(2*p+1,2*p,1)
            elif event['kind'] == 'bridge':
                d,s,c = event['dst'],event['src'],event['coefficient']
                add(2*d,2*s,c); add(2*s+1,2*d+1,c if bad_dual else -c)
                bad_dual = False
            else:
                for p in range(4):
                    matrix[2*p],matrix[2*p+1] = matrix[2*p+1],[-x for x in matrix[2*p]]
        return matrix
    assert replay() == identity
    controls = []
    for i,event in enumerate(events):
        if event['kind'] in ('local','bridge'):
            assert replay(skip=i) != identity
            controls.append({'omit_event':i,'kind':event['kind'],'rejected':True})
    assert replay(bad_dual=True) != identity
    controls.append({'wrong_first_bridge_dual_sign':True,'rejected':True})
    levels = [-1]*4; advances = []
    def advance(pair,to):
        if levels[pair] < to:
            advances.append((pair,levels[pair],to)); levels[pair] = to
    for event in events:
        if event['kind'] == 'local':
            p,s = event['pair'],event['stage']; advance(p,s-1); levels[p] = s
        elif event['kind'] == 'bridge':
            d,s = event['dst'],event['src']; to = max(levels[d],levels[s])
            advance(d,to); advance(s,to)
        else:
            for p in range(4):
                advance(p,8)
    ds = sorted(y-x for _,x,y in advances)
    assert ds == [1,1,1,2,2,4,4,6,6]
    source = json.loads((HERE/'controller-orbits/K4.json').read_text())
    assert source['status'] == 'EXACT_FINITE_CLOCK_ORBIT_SEARCH_COMPLETE'
    assert source['minimum_final_idle_segments_found'] == 9
    assert source['budget_before_final'] == 6 and source['maximum_idle_jump'] is None
    assert source['script_sha256'] == sha256(SEARCH.read_bytes()).hexdigest()
    proof = HERE/'CLOCK-MODEL-PROOF.md'
    result = {'status':'INDEPENDENT_GL_QUOTIENT_ENUMERATION_AND_INTEGER_B4_CONTROLS_PASS',
              'GL_checks':rows,'integer_B4_identity':True,'B4_idle_advances':advances,'B4_Delta_partition':ds,
              'rejecting_controls':controls,'K4_finite_result_source_bound':True,
              'scope':'Independent complete coefficient-space GL orbit check in dimensions1..4 and integer incumbent replay. Does not constitute a second full K4 state enumeration or verification of native hosting/all-size machinery.',
              'source_sha256':{str(p.relative_to(REPO)):sha256(p.read_bytes()).hexdigest()
                               for p in (SEARCH,RECIPE,proof,HERE/'controller-orbits/K4.json',Path(__file__))}}
    (HERE/'CLOCK-REDUCTIONS-CHECK.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],sum(row['all_GL_matrices'] for row in rows),'GL bases,',len(controls),'controls')


if __name__ == '__main__':
    main()
