"""Check exact source-bound cuts and the declared caller price bound.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The verifier does not run an optimizer.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import copy
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(value, message):
    if not value:
        raise ValueError(message)


def authenticate():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row.get('usage') == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'Source bytes: '+row['path'])
    for row in json.loads((HERE/'INPUTS.json').read_text()):
        need(sha256((HERE/row['local']).read_bytes()).hexdigest() == row['sha256'],
             'Retained proposal bytes')


def inventory():
    raw = (ROOT/'research/native-center-free-code/CODED-WORDS.json.gz').read_bytes()
    word = json.loads(gzip.decompress(raw)); c = word['canonical']
    need(c['v'] == 112 and c['h'] == 9 and len(c['start']) == 632,
         'Actual port, ambient and independent input counts')
    edges = []
    for program in word['programs'].values():
        need(not any(e[0] == 'center' for e in program), 'All eight centers are removed')
        edges.append(Counter(tuple(sorted(e[3:5])) for e in program
                             if e[0] in ('climb', 'warp')))
    need(len(edges) == 2 and edges[0] == edges[1], 'Both full orientation graphs')
    targets = Counter(tuple(sorted((a,b))) for a,b in zip(c['start'][224:],c['final'][224:]))
    need(sum(targets.values()) == 408, 'Every helper endpoint is charged')
    used = sorted({x for edge in list(edges[0])+list(targets) for x in edge})
    need(len(used) == 1002, 'All used source frame vertices')
    return word, edges[0], targets, used


def network(c, edges, targets, used, central, branch):
    fixed = {}
    def pin(frame, bit):
        need(frame not in fixed or fixed[frame] == bit, 'Compatible main boundaries')
        fixed[frame] = bit
    pin(0, 0); pin(1, 1)
    for frame in c['start'][:112]: pin(frame, int(central))
    for frame in c['start'][112:224]: pin(frame, 0)
    for frame in c['final'][:112]: pin(frame, 1)
    for frame in c['final'][112:224]: pin(frame, int(not central))
    pairs = [(a,b) for a,b in targets if a != b and a not in fixed and b not in fixed]
    branch_nodes = sorted({a for a,b in pairs})
    need(branch_nodes == [114,115], 'All negative edges have a fixed end after two branches')
    for frame,bit in zip(branch_nodes,branch): fixed[frame] = bit
    variables = sorted(set(used)-set(fixed)); ids = {a:i for i,a in enumerate(variables)}
    source = len(ids); sink = source+1
    arcs = Counter(); unary = Counter(); constant = 0
    def term(a,b,weight):
        nonlocal constant
        if a == b: return
        if a in fixed and b in fixed:
            constant += weight*(fixed[a] != fixed[b])
        elif a in fixed or b in fixed:
            if b in fixed: a,b = b,a
            constant += weight*fixed[a]
            unary[b] += weight*(1-2*fixed[a])
        else:
            need(weight >= 0, 'No unbranched negative pair')
            arcs[ids[a],ids[b]] += weight; arcs[ids[b],ids[a]] += weight
    for (a,b),count in edges.items(): term(a,b,count)
    for (a,b),count in targets.items(): term(a,b,-count)
    for frame,weight in unary.items():
        if weight >= 0: arcs[source,ids[frame]] += weight
        else: arcs[ids[frame],sink] -= weight; constant += weight
    net = dict(source=source,sink=sink,variables=variables,constant=constant,
               edges=[[a,b,w] for (a,b),w in sorted(arcs.items()) if w])
    return net,fixed


def flow_cut(net, receipt):
    """Use capacity, conservation and a matching cut as the proof."""
    flows = receipt['flows']; value = receipt['value']
    need(type(value) is int and len(flows) == len(net['edges']), 'Integer flow inventory')
    balance = [0]*(net['sink']+1)
    for (a,b,capacity),flow in zip(net['edges'],flows):
        need(type(flow) is int and 0 <= flow <= capacity, 'Flow capacity')
        balance[a] += flow; balance[b] -= flow
    need(balance[net['source']] == value and balance[net['sink']] == -value,
         'Source and sink balance')
    need(all(v == 0 for i,v in enumerate(balance) if i not in (net['source'],net['sink'])),
         'Interior flow conservation')
    raw_side = receipt['source_side']; side = set(raw_side)
    need(len(raw_side) == len(side) and
         all(type(x) is int and 0 <= x <= net['sink'] for x in side), 'Cut vertices')
    need(net['source'] in side and net['sink'] not in side, 'Cut terminals')
    cut = sum(w for a,b,w in net['edges'] if a in side and b not in side)
    need(value == cut, 'Flow equals cut')
    return net['constant']+value


def check_certificates(word, edges, targets, used, cuts):
    expected = [(central,list(branch)) for central in (False,True)
                for branch in product((0,1),repeat=2)]
    need([(r['central'],r['branch']) for r in cuts['branches']] == expected, 'Eight complete branches')
    labels = {}; objectives = []
    for row in cuts['branches']:
        need(type(row['central']) is bool and all(type(b) is int and b in (0,1) for b in row['branch']),
             'Exact branch types')
        net,fixed = network(word['canonical'],edges,targets,used,row['central'],row['branch'])
        value = flow_cut(net,row['flow']); objectives.append(value)
        need(type(row['objective']) is int and value == row['objective'], 'Stored branch objective')
        expected_value = 672 if row['central'] else 224
        need(value == expected_value, 'Exact one-axis minimum')
        side = set(row['flow']['source_side'])
        assignment = fixed | {a:int(i not in side) for i,a in enumerate(net['variables'])}
        literal = sum(n*(assignment[a] != assignment[b]) for (a,b),n in edges.items())
        literal -= sum(n*(assignment[a] != assignment[b]) for (a,b),n in targets.items())
        need(literal == value, 'Literal signed edge objective')
        if row['branch'] == [0,0]: labels[row['central']] = assignment
    mask = {a:labels[True][a]+510*labels[False][a] for a in used}
    paid = []; changed_warps = []
    for program in word['programs'].values():
        counts = Counter(); moved = 0
        for e in program:
            if e[0] in ('climb','warp'):
                rank = (mask[e[3]]^mask[e[4]]).bit_count()
                if rank: counts[rank] += 1
                if e[0] == 'warp' and rank: moved += 1
        paid.append(counts); changed_warps.append(moved)
    helper = Counter((mask[a]^mask[b]).bit_count() for a,b in
                     zip(word['canonical']['start'][224:],word['canonical']['final'][224:]))
    need(paid == [Counter({1:796,8:348,9:281})]*2, 'Attaining literal paid profile')
    need(helper == Counter({9:405,0:3}), 'Attaining independent helper profile')
    need(changed_warps == [0,0], 'The relaxed optimum also keeps all warps ordinary')
    need(sum(r*n for r,n in paid[0].items())-sum(r*n for r,n in helper.items()) == 2464,
         'Attained nine-axis minimum')
    return objectives


def caller_bound():
    # The positive Taylor partial sum proves exp(11/5)>9, hence log(9)<11/5.
    term = total = Q(1)
    for j in range(1,19): term *= Q(11,5*j); total += term
    need(total > 9, 'Exact logarithm upper bound')
    deficit = Q(2464); helper_mass = Q(408*9); ceiling = Q(1,100)
    local_lower = deficit-ceiling*Q(11,5)*(deficit+helper_mass)
    need(local_lower == Q(291126,125) and local_lower > 1904, 'Uniform local moment lower bound')
    # Source controller inventory: one long output and p-1 shorter paired outputs.
    for p in range(1,101):
        for prefix in range(p):
            suffix = p-1-prefix
            idle_lengths = list(range(2,prefix+2))+list(range(2,suffix+2))
            need(len(idle_lengths) == p-1, 'All IDLE histories')
            main = 224*(sum(8*k+1 for k in idle_lengths)+8*(p+2)+1)
            idle = 224*sum(8*k for k in idle_lengths)
            thin = 112*(p-1)
            need(main-idle-thin-2464*(p+2) == -560*p-1232, 'Rank-mass caller identity')
    return dict(saving_interval=['0','1/100'],local_moment_lower=str(local_lower),
                caller_moment_upper='-(53126/125)*(p+2)-112',
                p16_rank_surplus=-10192,scope='All p>=1 and every prefix split in the stated query-thinned family')


def rejects(function, message):
    try: function()
    except (ValueError,KeyError,IndexError): return
    raise ValueError('Accepted mutation: '+message)


def main():
    authenticate(); word,edges,targets,used = inventory()
    cuts = json.loads((HERE/'CUTS.json').read_text())
    objectives = check_certificates(word,edges,targets,used,cuts)
    first = cuts['branches'][0]; net,_ = network(word['canonical'],edges,targets,used,False,[0,0])
    bad = copy.deepcopy(first['flow']); bad['flows'][0] = net['edges'][0][2]+1
    rejects(lambda:flow_cut(net,bad),'capacity')
    bad = copy.deepcopy(first['flow']); bad['value'] += 1
    rejects(lambda:flow_cut(net,bad),'flow value')
    bad = copy.deepcopy(first['flow']); bad['source_side'].append(net['sink'])
    rejects(lambda:flow_cut(net,bad),'cut sink')
    bad = copy.deepcopy(cuts); bad['branches'].pop()
    rejects(lambda:check_certificates(word,edges,targets,used,bad),'missing branch')
    bad = copy.deepcopy(cuts); bad['branches'][0]['objective'] -= 1
    rejects(lambda:check_certificates(word,edges,targets,used,bad),'invented better objective')
    bad = copy.deepcopy(first['flow']); bad['flows'][0] = True
    rejects(lambda:flow_cut(net,bad),'Boolean flow')
    result = dict(frame_vertices=len(used),branch_objectives=objectives,rank_mass_floor=2464,
                  paid={'1':796,'8':348,'9':281},helpers={'9':405},ordinary_helpers=3,
                  changed_warps=0,caller=caller_bound(),rejected_controls=6,new_kappa=False)
    need(result == json.loads((HERE/'RESULT.json').read_text()), 'Frozen result')
    print(json.dumps(result,sort_keys=True))
    print('PASS_COMMON_COFRAME_COORDINATE_CUT no_new_kappa')


if __name__ == '__main__':
    main()
