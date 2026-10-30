"""Exact bounded coframe optimization and minimum-cut certificates.

The construction retains the actual source and all endpoint debits.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, defaultdict, deque
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import gzip
import json

ROOT = Path(__file__).resolve().parent
SCALE = 10**24
SAVING = Q(351, 100000)
INFINITY = 10**40


def need(ok, message):
    if not ok: raise ValueError(message)


def source():
    for item in json.loads((ROOT/'INPUTS.json').read_text()):
        need(sha256((ROOT/item['local']).read_bytes()).hexdigest() == item['sha256'], 'Frozen source '+item['local'])
    raw = gzip.decompress((ROOT/'source/INTERSECTION153-ROUND3-ACTUAL-WORD.json.gz').read_bytes())
    need(sha256(raw).hexdigest() == '7f137c4b95db519d04ad2336ef1a146fbc953124e95940d10b572a63ab958c87', 'Exact actual word payload')
    return json.loads(raw)


def power_intervals():
    out = [[0, 0], [SCALE, SCALE]]
    for r in range(2, 9):
        z = Q(r-1, r+1); term = z; lo = Q(0); count = 180
        for k in range(count):
            lo += 2*term/(2*k+1); term *= z*z
        hi = lo+2*term/((2*count+1)*(1-z*z))
        def exp_minus(x, terms):
            term = Q(1); total = term
            for j in range(1, terms+1):
                term *= -x/j; total += term
            return total
        need(0 < SAVING*hi < 1, 'Alternating exponential remainder domain')
        lower = r*exp_minus(SAVING*hi, 21)*SCALE
        upper = r*exp_minus(SAVING*lo, 20)*SCALE
        a = lower.numerator//lower.denominator
        b = -((-upper.numerator)//upper.denominator)
        need(a <= b <= a+1, 'One-unit power enclosure')
        out.append([a, b])
    return out


def general_power_interval(r, exponent):
    if r == 1: return Q(1), Q(1)
    z=Q(r-1,r+1); term=z; lo=Q(0); count=180
    for k in range(count): lo+=2*term/(2*k+1); term*=z*z
    hi=lo+2*term/((2*count+1)*(1-z*z))
    need(exponent>0, 'Positive exponent for the higher-moment enclosure')
    need(exponent*hi < 3, 'Bounded positive exponential tail')
    def exp_positive(x):
        total=term=Q(1)
        for k in range(1,61): term*=x/k; total+=term
        next_term=term*x/61
        return total,total+next_term/(1-x/62)
    return exp_positive(exponent*lo)[0], exp_positive(exponent*hi)[1]


def inventory(word):
    c = word['canonical']; programs = word['programs']; dims = list(map(len, c['frames']))
    anchored = {0}|set(c['start'][:224])|set(c['final'][:224]); used = set()
    for program in programs.values():
        for event in program:
            if event[0] == 'warp': anchored.update(event[3:5])
            elif event[0] == 'center': anchored.update(event[2:4])
            elif event[0] == 'climb': used.update(event[3:5])
    edge_counts = [Counter((e[3],e[4]) for e in program if e[0]=='climb') for program in programs.values()]
    need(all(x==edge_counts[0] for x in edge_counts), 'Same full proper-edge multiset in both orientations')
    free = sorted(used-anchored)
    span_cache={}
    def span(index):
        if index not in span_cache:
            values={0}
            for vector in c['frames'][index]: values|={x^vector for x in tuple(values)}
            span_cache[index]=values
        return span_cache[index]
    need(all(span(a)<=span(b) for a,b in zip(c['start'][224:],c['final'][224:])), 'All original helper endpoints are nested')
    branch = sorted(set(c['final'][224:]) & set(free))
    need(branch == [181, 182] and len(free) == 423, 'Complete actual binary domain')
    need(all(x in anchored or x in free for x in c['start']+c['final']), 'Every boundary frame is covered')
    for name, program in programs.items():
        need(Counter(e[5] for e in program if e[0] == 'climb') == Counter({1:2011, 2:445, 3:427, 4:112, 5:12}), 'Source proper profile '+name)
        need(Counter(e[4] for e in program if e[0] == 'center') == Counter({7:8}), 'Source centre profile')
    return dict(dims=dims, anchored=sorted(anchored), free=free, branch=branch)


def grade(a, b, folded, dims):
    if a in folded and b in folded: return 0
    if a in folded: return dims[b]
    if b in folded: return dims[a]
    return abs(dims[b]-dims[a])


def profiles(word, folded):
    c = word['canonical']; dims = list(map(len, c['frames'])); paid = {}
    for name, program in word['programs'].items():
        counts = Counter()
        for event in program:
            if event[0] == 'climb': rank = grade(event[3], event[4], folded, dims)
            elif event[0] == 'center': rank = event[4]
            else: continue
            if rank: counts[rank] += 1
        paid[name] = dict(sorted(counts.items()))
    targets = Counter(grade(a, b, folded, dims) for a, b in zip(c['start'][224:], c['final'][224:]))
    zeros = targets.pop(0, 0)
    need(paid['forward'] == paid['backward'], 'Same complete profile in both orientations')
    return dict(paid=paid['forward'], targets=dict(sorted(targets.items())), ordinary_identity_targets=zeros)


def network(word, inv, weights, branch_values):
    c = word['canonical']; dims = inv['dims']; fixed = {x:0 for x in inv['anchored']}
    fixed.update(zip(inv['branch'], branch_values)); variables = [x for x in inv['free'] if x not in fixed]
    ids = {x:i for i,x in enumerate(variables)}; start = len(ids); end = start+1
    unary = defaultdict(int); arcs = defaultdict(int); constant = 8*weights[7]
    def add_term(a, b, sign, cap):
        nonlocal constant
        def value(x, y):
            rank = grade(a, b, {k for k,v in ((a,x),(b,y)) if v}, dims)
            return INFINITY if cap and rank > 7 else sign*weights[rank]
        if a in fixed and b in fixed: constant += value(fixed[a], fixed[b])
        elif a in fixed:
            v0, v1 = value(fixed[a], 0), value(fixed[a], 1); constant += v0; unary[b] += v1-v0
        elif b in fixed:
            v0, v1 = value(0, fixed[b]), value(1, fixed[b]); constant += v0; unary[a] += v1-v0
        else:
            e00,e01,e10,e11 = (value(x,y) for x,y in ((0,0),(0,1),(1,0),(1,1)))
            capacity = e01+e10-e00-e11
            need(capacity >= 0, 'Submodular pair after the two output choices')
            constant += e00; unary[a] += e10-e00; unary[b] += e11-e10
            if a != b: arcs[ids[a], ids[b]] += capacity
    for event in word['programs']['forward']:
        if event[0] == 'climb': add_term(event[3], event[4], 1, True)
    for a,b in zip(c['start'][224:], c['final'][224:]): add_term(a,b,-1,False)
    for frame, cost in unary.items():
        if cost >= 0: arcs[start, ids[frame]] += cost
        else: constant += cost; arcs[ids[frame], end] -= cost
    edges = [[a,b,v] for (a,b),v in sorted(arcs.items()) if v]
    return dict(variables=variables, branch=list(branch_values), source=start, sink=end,
                constant=constant, edges=edges)


def maximum_flow(net):
    """Dinic's integral flow algorithm; the verifier checks a separate certificate."""
    size = net['sink']+1; graph = [[] for _ in range(size)]; refs = []
    for u,v,capacity in net['edges']:
        refs.append((u,len(graph[u])))
        graph[u].append([v,len(graph[v]),capacity])
        graph[v].append([u,len(graph[u])-1,0])
    source, sink = net['source'], net['sink']; value = 0
    while True:
        level = [-1]*size; level[source] = 0; queue = deque([source])
        while queue:
            u = queue.popleft()
            for v,rev,capacity in graph[u]:
                if capacity and level[v] < 0: level[v] = level[u]+1; queue.append(v)
        if level[sink] < 0: break
        at = [0]*size
        def send(u, amount):
            if u == sink: return amount
            while at[u] < len(graph[u]):
                edge = graph[u][at[u]]; v,rev,capacity = edge
                if capacity and level[v] == level[u]+1:
                    sent = send(v,min(amount,capacity))
                    if sent: edge[2] -= sent; graph[v][rev][2] += sent; return sent
                at[u] += 1
            return 0
        while True:
            sent = send(source,INFINITY*len(net['edges']))
            if not sent: break
            value += sent
    reachable = [i for i,l in enumerate(level) if l >= 0]
    flows = [capacity-graph[u][index][2] for (_,_,capacity),(u,index) in zip(net['edges'],refs)]
    return dict(value=value, source_side=reachable, flows=flows)


def check_flow(net, receipt):
    """Check capacities, conservation and the matching cut; do not run the solver."""
    need(len(receipt['flows']) == len(net['edges']), 'One flow for every directed edge')
    balance = [0]*(net['sink']+1)
    for (u,v,cap),flow in zip(net['edges'],receipt['flows']):
        need(type(flow) is int and 0 <= flow <= cap, 'Integral capacity interval')
        balance[u] += flow; balance[v] -= flow
    value = receipt['value']; source,sink = net['source'],net['sink']
    need(balance[source] == value and balance[sink] == -value and
         all(x == 0 for i,x in enumerate(balance) if i not in (source,sink)), 'Exact flow conservation')
    side = set(receipt['source_side'])
    need(source in side and sink not in side and all(type(x) is int and 0 <= x <= sink for x in side), 'Declared source cut')
    cut = sum(cap for u,v,cap in net['edges'] if u in side and v not in side)
    need(cut == value, 'Flow equals cut: global grid optimum for this branch')
    return net['constant']+cut


def folded_from(net, receipt, inv):
    side = set(receipt['source_side'])
    return sorted([x for i,x in enumerate(net['variables']) if i not in side]+
                  [x for x,v in zip(inv['branch'],net['branch']) if v])


def grid_cost(profile, weights):
    return sum(weights[int(k)]*v for k,v in profile['paid'].items())-sum(weights[int(k)]*v for k,v in profile['targets'].items())


def discover():
    word = source(); inv = inventory(word); bounds = power_intervals(); weights = [x[0] for x in bounds]; branches = []
    for values in product((0,1),repeat=2):
        net = network(word,inv,weights,values); flow = maximum_flow(net); optimum = check_flow(net,flow)
        folded = folded_from(net,flow,inv); profile = profiles(word,set(folded))
        feasible = max(profile['paid']) <= 7
        if feasible: need(grid_cost(profile,weights) == optimum, 'Literal profile equals its cut objective')
        else: need(optimum > INFINITY//2, 'Certified branch is infeasible under the child cap')
        branches.append(dict(branch=list(values),flow=flow,objective=optimum,folded=folded,profile=profile,feasible=feasible))
        print('PASS_OPTIMIZATION_BRANCH',values,len(folded),profile,flush=True)
    best = min(range(4),key=lambda i:branches[i]['objective'])
    headroom = sum(count*(bounds[rank][1]-bounds[rank][0]) for rank,count in branches[best]['profile']['paid'].items())+408
    return dict(schema='restricted-coframe-mincut/1',saving=str(SAVING),scale=SCALE,power_intervals=bounds,
                free_frames=inv['free'],branch_frames=inv['branch'],best_branch=best,branches=branches,
                objective_headroom_upper=str(Q(headroom,SCALE)))


if __name__ == '__main__':
    result = discover(); (ROOT/'CUTS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('BEST', result['best_branch'],result['branches'][result['best_branch']]['profile'])
