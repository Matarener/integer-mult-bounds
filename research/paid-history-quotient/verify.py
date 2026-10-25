#!/usr/bin/env python3
"""Check exact history bounds and full chronological examples.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from itertools import combinations
import json
import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit import audit, algebra, multiply


def require(condition, message):
    if not condition:
        raise ValueError(message)


def block(a, position, n):
    return [[a[i][j % 2] if j // 2 == position else 0 for j in range(2*n)]
            for i in range(2)]


def encode(a):
    return [[str(x) for x in row] for row in a]


def main():
    I, X, Z = [[1,0],[0,1]], [[0,1],[1,0]], [[1,0],[0,-1]]
    cases = 0
    for n in range(1, 6):
        for k in range(n+1):
            for cached in combinations(range(n), k):
                data = {'dimension':2,'inputs':[f'v{i}@now' for i in range(n)],
                        'ordinary_generators':[],
                        'initial':[block(I,i,n) for i in range(n)] + [block(Z,i,n) for i in cached],
                        'targets':[block(Z,i,n) for i in range(n)]}
                result = audit(data)
                require(result['target_quotient_dimension'] == n-k, 'cached quotient')
                require(result['additional_return_lower_bound'] == n-k, 'cached lower bound')
                cases += 1
    E12, E21 = [[0,1],[0,0]], [[0,0],[1,0]]
    require(len(algebra(2,[tuple(map(tuple,E12)),tuple(map(tuple,E21))])) == 4,
            'products must be included')
    base = {'dimension':2,'inputs':['old','new'],'ordinary_generators':[],
            'initial':[block(I,i,2) for i in range(2)] + [block(Z,0,2)],
            'targets':[block(Z,1,2)]}
    require(audit(base)['additional_return_lower_bound'] == 1, 'stale version')
    good = deepcopy(base); good['initial'].append(block(Z,1,2))
    require(audit(good)['additional_return_lower_bound'] == 0, 'current observation')
    closure = deepcopy(base); closure['ordinary_generators'] = [E12,E21]
    require(audit(closure)['additional_return_lower_bound'] == 0, 'ordinary closure')
    controls = 3
    for key, value in [('dimension',True), ('inputs',['same','same']),
                       ('ordinary_generators',[[[1.0,0],[0,1]]]),
                       ('targets',[[[1,0],[0,1]]]),
                       ('ordinary_generators',[[['1/0',0],[0,1]]])]:
        bad=deepcopy(base); bad[key]=value
        try: audit(bad)
        except (ValueError, ZeroDivisionError): controls += 1
        else: raise ValueError('accepted invalid input: '+key)
    rng=random.Random(7301)
    programs=prefixes=0
    for generators in ([],[Z],[E12],[E12,E21]):
        for _ in range(24):
            rows=[block(I,0,2),block(I,1,2),[[0]*4 for _ in range(2)]]
            initial=deepcopy(rows); paid=0
            for step in range(12):
                dst,src=rng.sample(range(3),2)
                if step % 3 == 0:
                    operator=[[rng.randrange(-2,3) for _ in range(2)] for _ in range(2)]
                    rows[dst]=[list(r) for r in multiply(operator,rows[dst])]; paid+=1
                elif step % 3 == 1:
                    rows[dst]=[[x+y for x,y in zip(a,b)] for a,b in zip(rows[dst],rows[src])]
                elif generators:
                    rows[dst]=[list(r) for r in multiply(rng.choice(generators),rows[dst])]
                else:
                    rows[dst]=deepcopy(rows[src])
                data={'dimension':2,'inputs':['x','y'],'ordinary_generators':generators,
                      'initial':initial,'targets':[encode(a) for a in rows]}
                require(audit(data)['additional_return_lower_bound'] <= paid,
                        'history bound exceeds literal paid returns')
                prefixes+=1
            programs+=1
    print('PASS_PAID_HISTORY_QUOTIENT '+json.dumps(
        {'cache_cases':cases,'literal_programs':programs,'prefixes':prefixes,'controls':controls},sort_keys=True))


if __name__ == '__main__':
    main()
