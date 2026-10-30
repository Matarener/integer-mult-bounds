#!/usr/bin/env python3
"""Constructive joint frame assignment over a finite rational frame catalogue.

No frame or gate is licensed by its numerical price.  The returned word is
replayed by the independent rational/F2 checker before it can be a candidate.
The finite frame domain is the current word's catalogue, not every rational
subspace.  Generalized frame-graph method credits Nick Petalas; R437 sources and
the independent checker retain their original attribution. Apache-2.0.
"""
from collections import Counter, defaultdict, OrderedDict
from copy import deepcopy
from itertools import product
from math import prod
from bit_pair_search import flatten, actual_profile


class Optimizer:
    def __init__(self, word, checker, endpoint=0.001736738651088946):
        self.masks = [sum(1 << i for i in f) for f in word['frames']]
        self.dim = checker.fdim
        self.inc = [[not (a & ~b) for b in self.masks] for a in self.masks]
        self.price = [r ** (1-endpoint) if r else 0.0 for r in range(word['h']+1)]
        self.original_profile = actual_profile(word, checker)
        # COPY frames are fixed at the source word's exact output boundary.
        current = list(word['start'])
        for sec in ('D', 'A'):
            for f, d, ss in word[sec]:
                for r in [d] + ss:
                    current[r] = f
        self.captures = {r: current[r] for r in word['ret']}
        self.cache = OrderedDict()
        self.domain_cache = {}
        self.stats = Counter()

    def graph(self, word):
        sections = flatten(word)
        n = 2 * word['v'] + word['R']
        cur = {r: (-1, word['start'][r]) for r in range(n)}
        edges, nodes, frames = [], [], []
        def anchor(r, f):
            a, af = cur[r]
            edges.append((a, af, -1, f))
            cur[r] = (-1, f)
        for name in ('A', 'B'):
            for p, e in enumerate(sections[name]):
                i = len(nodes)
                nodes.append((name, p))
                frames.append(e[-1])
                for r in e[1:3]:
                    a, af = cur[r]
                    edges.append((a, af, i, e[-1]))
                    cur[r] = (i, e[-1])
            if name == 'A':
                for r, f in self.captures.items():
                    anchor(r, f)
                for r in range(word['v'], 2 * word['v']):
                    anchor(r, 0)
        for r, f in enumerate(word['final']):
            anchor(r, f)
        incoming, outgoing = defaultdict(list), defaultdict(list)
        for a, af, b, bf in edges:
            incoming[b].append((a, af))
            outgoing[a].append((b, bf))
        lo, hi = [], [self.masks[1]] * len(nodes)
        for i in range(len(nodes)):
            required = 0
            for a, af in incoming[i]:
                required |= lo[a] if a >= 0 else self.masks[af]
            lo.append(required)
        for i in reversed(range(len(nodes))):
            for b, bf in outgoing[i]:
                hi[i] &= hi[b] if b >= 0 else self.masks[bf]
            if lo[i] & ~hi[i]:
                raise ValueError('infeasible rational catalogue bounds')
        self.last_bounds = lo, hi
        domains = []
        for i in range(len(nodes)):
            key = lo[i], hi[i]
            if key not in self.domain_cache:
                self.domain_cache[key] = tuple(f for f, mask in enumerate(self.masks)
                           if not lo[i] & ~mask and not mask & ~hi[i])
            ds = self.domain_cache[key]
            if not ds:
                raise ValueError('empty rational catalogue domain')
            domains.append(ds)
        variable = {i for i, ds in enumerate(domains) if len(ds) > 1}
        adj = {i: set() for i in variable}
        for a, _, b, _ in edges:
            if a in variable and b in variable:
                adj[a].add(b)
                adj[b].add(a)
        comps, seen = [], set()
        for root in sorted(variable):
            if root in seen:
                continue
            todo, comp = [root], []
            seen.add(root)
            while todo:
                i = todo.pop()
                comp.append(i)
                for j in adj[i] - seen:
                    todo.append(j)
                    seen.add(j)
            comps.append(tuple(sorted(comp)))
        # Build component-owned edges once, avoiding a full graph scan per solve.
        owner = {node: k for k, comp in enumerate(comps) for node in comp}
        owned = [[] for _ in comps]
        for e in edges:
            touched = {owner[node] for node in (e[0], e[2]) if node in owner}
            assert len(touched) <= 1
            for k in touched:
                owned[k].append(e)
        return sections, nodes, frames, edges, domains, comps, owned

    def solve(self, comp, owned, domains, max_bucket):
        labels = {node: j for j, node in enumerate(comp)}
        def endpoint(node, frame):
            return (labels[node], -1) if node in labels else (-1, domains[node][0] if node >= 0 else frame)
        key = (max_bucket, tuple(domains[i] for i in comp),
               tuple(sorted((endpoint(a, af), endpoint(b, bf)) for a, af, b, bf in owned)))
        if key in self.cache:
            self.stats['hits'] += 1
            assignment, attempts = self.cache[key]
            return {node: assignment[j] for j, node in enumerate(comp)}, attempts
        self.stats['misses'] += 1
        choices = {i: domains[i] for i in comp}
        factors = []
        for a, af, b, bf in owned:
            scope = tuple(node for node in (a, b) if node in labels)
            table = {}
            for vals in product(*(range(len(choices[i])) for i in scope)):
                assignment = {node: choices[node][v] for node, v in zip(scope, vals)}
                before = assignment.get(a, domains[a][0] if a >= 0 else af)
                after = assignment.get(b, domains[b][0] if b >= 0 else bf)
                if self.inc[before][after]:
                    table[vals] = self.price[self.dim[after]-self.dim[before]]
            factors.append((scope, table))
        adj = {i: set() for i in comp}
        for scope, _ in factors:
            for node in scope:
                adj[node].update(set(scope)-{node})
        trace, attempts = [], 0
        while adj:
            var = min(adj, key=lambda i: (prod(len(choices[j]) for j in adj[i]|{i}),len(adj[i]),i))
            neighbors = tuple(sorted(adj[var]))
            variables = (var,) + neighbors
            cap = prod(len(choices[i]) for i in variables)
            if cap > max_bucket:
                raise ValueError(('bucket capacity', cap, len(comp)))
            used = [f for f in factors if var in f[0]]
            factors = [f for f in factors if var not in f[0]]
            indexes = [tuple(variables.index(i) for i in scope) for scope,_ in used]
            table, back = {}, {}
            attempts += cap
            for vals in product(*(range(len(choices[i])) for i in variables)):
                costs = [f[1].get(tuple(vals[j] for j in pos)) for f,pos in zip(used,indexes)]
                if any(c is None for c in costs):
                    continue
                total = sum(costs)
                key_ = vals[1:]
                if key_ not in table or total < table[key_]-1e-11:
                    table[key_] = total
                    back[key_] = vals[0]
            if not table:
                raise ValueError('empty factor')
            factors.append((neighbors,table))
            trace.append((var,neighbors,back))
            for j in neighbors:
                adj[j].update(set(neighbors)-{j})
                adj[j].remove(var)
            del adj[var]
        assignment = {}
        for var,neighbors,back in reversed(trace):
            assignment[var] = back[tuple(assignment[j] for j in neighbors)]
        answer = {i: choices[i][v] for i,v in assignment.items()}
        self.cache[key] = tuple(answer[node] for node in comp), attempts
        if len(self.cache)>10000:
            self.cache.popitem(last=False)
        return answer, attempts

    def optimize(self, word, max_bucket=100000):
        sections, nodes, frames, edges, domains, comps, owned = self.graph(word)
        assignment = {i: ds[0] for i, ds in enumerate(domains)}
        attempts = 0
        for comp, es in zip(comps, owned):
            solved, count = self.solve(comp, es, domains, max_bucket)
            assignment.update(solved)
            attempts += count
        out = deepcopy(word)
        out['A'], out['B'] = [], []
        for i, (name, p) in enumerate(nodes):
            e = sections[name][p]
            out[name].append([assignment[i], e[1], [e[2]]])
        v = word['v']
        out['C'] = [[1, d, list(ss)] for sec in ('A', 'B')
                    for _, d, ss in out[sec] if not v <= d < 2*v][::-1]
        paid = Counter(self.dim[f] for f in self.captures.values())
        for a, af, b, bf in edges:
            before = assignment[a] if a >= 0 else af
            after = assignment[b] if b >= 0 else bf
            assert self.inc[before][after]
            jump = self.dim[after] - self.dim[before]
            if jump:
                paid[jump] += 1
        delta = paid.copy()
        delta.subtract(self.original_profile)
        return out, dict(delta={r:n for r,n in delta.items() if n},
                         saving=-sum(n*self.price[r] for r,n in delta.items()),
                         attempts=attempts, components=len(comps),
                         variable_nodes=sum(map(len,comps)),
                         changed_frames=sum(f != assignment[i] for i,f in enumerate(frames)),
                         local_profile=dict(paid))
