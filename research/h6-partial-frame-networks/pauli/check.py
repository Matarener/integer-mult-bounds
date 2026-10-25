#!/usr/bin/env python3
"""Eight partial Pauli centres and a fully priced fixed-tiling refinement.

Exact logical/frame-contract mathematics only. No native phase compiler,
rounded supplier, full physical schedule or multiplication bound is claimed.
Apache-2.0; substantial OpenAI Codex assistance; see preserved source notices.
"""
import argparse
import ast
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import sys
import types

PINS = {
    'geometry.py':'05d23eeb09cd04785b28d5337f0c2e19de3bf1cd7e54a26c219cb10c9a3daf25',
    'frozen/partial_pauli.py':'774d876402be6066121a982f0c149b924b53c72bc53f6bfd13d96f751600b8bd',
    'frozen/PARTIAL-PAULI-RESULT.json':'048830fbb42141a07a946fc3e32f5c666100a5265a69db5600c432595bb364d0',
    'frozen/CONTINUATION.md':'7ba7f0806ea9d35912f736864d3e7696314e075faac6a6bb979789cb765151df',
    'frozen/module_tiling.py':'c7ea13441daabed63860e8ae464293f4a16af20be331941fc8edd12412e8d73d',
    'frozen/dynamic_cyclic.py':'8b97368264eff933191b05d80c78c3c72cb7d23b810303d085b194240dd818df',
    'frozen/mixed_rectangle.py':'544d6b7d4ea92134b1016ce359f01b7a33ebb2ba0d986bf5b9accc47a3ec600c',
    'frozen/pauli_partial_review.py':'01d5a2e002545de95823b220be73debc298a73c7f96ac4d4b0486e1cb578efad',
    'frozen/PARTIAL-PAULI-REVIEW.json':'0a56ac6aedc39787ef228a14354741077c44df2b33d174765a8c4478ee84301c',
    'frozen/PAULI-FIXED-SUPPORT.json':'344af488229ebc64485132bf316813c4242ddaee35a2ea5878a10b2fc5d671b9',
    'frozen/e8_sections.py':'19b05280ad59f2938c2c9a4ffef213712a65af75d7c111fa304fdc2868d13f55',
    'frozen/e8_cubed.py':'ce24f397053c0ef5b26881bb7ccfab53fb0a3d762f2de04086fed8f7b41e8234',
}
DISABLED = frozenset()


def need(ok, code):
    if not ok and code not in DISABLED:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def serial(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k):serial(v) for k,v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def load_geometry(raw):
    module = types.ModuleType('c03_authenticated_geometry')
    sys.modules[module.__name__] = module
    exec(compile(raw, '<authenticated-geometry>', 'exec',
                 dont_inherit=True, optimize=0), module.__dict__)
    return module


def rational_rank(rows):
    work = [list(map(F, row)) for row in rows]
    if not work:
        return 0
    rank = 0
    for column in range(len(work[0])):
        pivot = next((i for i in range(rank, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        work[rank] = [v / scale for v in work[rank]]
        for i in range(rank + 1, len(work)):
            scale = work[i][column]
            if scale:
                work[i] = [a - scale*b for a,b in zip(work[i], work[rank])]
        rank += 1
        if rank == len(work):
            break
    return rank


def setup(historical):
    roots = m.canonical_roots()
    packed = m.packed_root_pairs(roots)
    q = [sum((-1 if j & 1 else 1)*x*x for j,x in enumerate(a)) for a in roots]
    selected = [j for j,value in enumerate(q) if value]
    need(len(selected) == 24 and {q[j] for j in selected} == {-8,8}, 'Pauli support24')
    support = [(i,j) for i in range(120) for j in selected]
    U = m.basis(packed[i][j] for i,j in support)
    W = m.basis(w for w in range(1 << 17)
                if all(not ((w & u).bit_count() & 1) for u in U))
    need(len(U) == 15 and len(W) == 2 and m.included(W,U), 'U15 radical2')
    need(list(U) == historical['source_support_U'] and
         list(W) == historical['radical_U_perp'] and
         selected == historical['support_b_lines'], 'historical exact geometry binding')
    features = [[roots[i][c]*q[j] for c in range(8)] for i,j in support]
    individual = []
    for c in range(8):
        incidence = Counter(abs(row[c]) for row in features if row[c])
        need(incidence == {8:1536,16:336}, 'half support incidence')
        frame = m.basis(packed[i][j] for i,j in support if roots[i][c])
        need(frame == U, 'all eight individual feature spans equal U')
        individual.append({'coordinate':c, 'frame':frame, 'signed_nonzeros':3744,
                           'signed_abs8':3072, 'signed_abs16':672})
    need(all(m.included(W,m.perp(packed[i][j])) for i,j in support), 'all supported target caps contain W')
    need(rational_rank(roots) == 8, 'actual eight linear feature dimensions')
    chosen = []; frame = ()
    for i,j in support:
        grown = m.basis(frame + (packed[i][j],))
        if len(grown) > len(frame):
            chosen.append((i,j)); frame = grown
        if len(frame) == 15:
            break
    linears = []
    for i in range(120):
        if rational_rank([roots[j] for j in linears] + [roots[i]]) > len(linears):
            linears.append(i)
        if len(linears) == 8:
            break
    chosen += [(i,selected[0]) for i in linears]
    chosen += [(105,j) for j in selected[:2]]
    chosen += [(0,j) for j in range(120) if not q[j]][:2]
    chosen = list(dict.fromkeys(chosen))
    need([list(x) for x in chosen] == historical['fixture_actual_ports'], 'historical actual fixture binding')
    # The same 35-column symmetric traceless Pauli family as the pinned evaluator.
    parameters = [(a,b) for a in range(8) for b in range(8)
                  if (a,b) != (0,0) and not ((a&b).bit_count() & 1)]
    quadratics = [[sum((-1 if (x&b).bit_count() & 1 else 1)*r[x]*r[x^a]
                       for x in range(8)) for a,b in parameters] for r in roots]
    outside = [row for j,row in enumerate(quadratics) if not q[j]]
    need(len(parameters) == 35 and len(outside) == 96, 'complete fixed quadratic support domain')
    need(rational_rank(quadratics) == 35 and rational_rank(outside) == 34,
         'fixed support exactly one quadratic direction')
    need(parameters[0] == (0,1) and all(row[0] == value for row,value in zip(quadratics,q)),
         'selected evaluator Pauli column')
    return roots,packed,q,support,U,W,chosen,individual,{
        'parameters':parameters,'quadratic_values':quadratics,'outside_rank':34,
        'full_rank':35,'supported_dimension':1,'outside_rows':96}


def accept_nested_path(path, code):
    need(all(m.included(a,b) for a,b in zip(path,path[1:])), code)


def path_bill(path):
    return [len(b)-len(a) for a,b in zip(path,path[1:]) if len(b)>len(a)]


def compatibility(roots, packed, q, U, W, triples):
    need(sorted(i for row in triples for i in row) == list(range(120)), 'complete acute triple partition')
    pairs = m.orthogonal_involution(roots)
    signs = []
    for row in triples:
        sigma = [1] + [m.dot(roots[row[0]],roots[i]) for i in row[1:]]
        need(all(abs(s) == 1 for s in sigma) and
             all(sigma[i]*sigma[j]*m.dot(roots[row[i]],roots[row[j]]) == 1
                 for i in range(3) for j in range(i)), 'actual triple signs')
        signs.append(sigma)
    frames = []; selected = []; census = Counter()
    bills = {key:Counter() for key in ('source','target','reader')}
    full = m.FULL
    for ti,aa in enumerate(triples):
        for bi,bb in enumerate(pairs):
            labels = [packed[a][b] for a in aa for b in bb]
            planes = [m.basis(labels[2*g:2*g+2]) for g in range(3)]
            arcs = [m.basis(planes[g]+planes[(g+1)%3]) for g in range(3)]
            need(all(len(x)==2 for x in planes) and all(len(x)==3 for x in arcs), 'r3 actual frame dimensions')
            need(all(m.included(arcs[g],m.perp(labels[2*((g-1)%3)+z]))
                     for g in range(3) for z in range(2)), 'r3 actual target caps')
            need(bool(q[bb[0]]) == bool(q[bb[1]]), 'tiling pairs preserve Pauli support')
            frames.append({'triple_index':ti,'b_pair_index':bi,'labels':labels,
                           'planes':planes,'final_arcs':arcs})
            if not q[bb[0]]:
                continue
            for group in range(3):
                source_arc = arcs[(group-1)%3]
                target_arc = arcs[(group+1)%3]
                join = m.basis(target_arc+W)
                need(m.included(source_arc,U), 'source final arc inside U')
                intersection = len(W)+len(target_arc)-len(join)
                need(intersection==1 and len(join)==4 and not m.included(W,target_arc),
                     'target W intersection one and join four')
                for z in range(2):
                    source_path = [m.basis((labels[2*group+z],)),planes[group],source_arc,U,full]
                    target_path = [(),W,join,m.perp(labels[2*group+z])]
                    # The reader delivering to group has origin group+1.
                    reader_path = [(),planes[(group+1)%3],target_arc,join,full]
                    for key,path in (('source',source_path),('target',target_path),('reader',reader_path)):
                        accept_nested_path(path, key+' refined path nested')
                        bills[key].update({r:2*n for r,n in Counter(path_bill(path)).items()})
                selected.append({'triple_index':ti,'b_pair_index':bi,'group':group,
                                 'source_arc':source_arc,'target_arc':target_arc,
                                 'join':join,'intersection_dimension':intersection,
                                 'signed_port_multiplicity':4})
                census['supported_ports'] += 4
                census['source_arc_inside_U'] += 4
                census['target_arc_does_not_contain_W'] += 4
                census['join_rank4'] += 4
    need(len(frames)==2400 and len(selected)==1440 and census['supported_ports']==5760,
         'complete tiling compatibility census')
    need(bills == {'source':Counter({1:11520,12:5760,2:5760}),
                   'target':Counter({2:11520,12:5760}),
                   'reader':Counter({2:5760,1:11520,13:5760})}, 'actual complete refined visit invoice')
    return {'a_triples':triples,'b_pairs':pairs,'gauge_signs':signs,
            'frame_cases':frames,'frame_cases_sha256':sha(canonical(frames)),
            'selected_joins':selected,'census':dict(census),
            'selected_signed_modules':960,'unchanged_signed_modules':3840,
            'actual_refined_histograms':{k:dict(v) for k,v in bills.items()}}


def delta_paths(changes):
    delta = Counter()
    for count,before,after in changes:
        for r in before:
            delta[r] -= count
        for r in after:
            delta[r] += count
    return {r:n for r,n in sorted(delta.items()) if n}


def profile(radical, model):
    private = 13 if radical else 15
    changes = [(8,[17],[15,2]),(8,[17],[private])]
    if model == 'standalone':
        changes.append((5760,[16],[14,2]))
        if radical:
            changes.append((5760,[16],[2,14]))
    elif model == 'cyclic_refinement':
        changes.append((5760,[1,1,14],[1,1,12,2]))
        if radical:
            changes += [(5760,[3,13],[2,2,12]),(5760,[2,1,14],[2,1,1,13])]
    else:
        need(model == 'already_paid_identical_visits','known profile model')
    delta = delta_paths(changes)
    need(sum(r*n for r,n in delta.items()) == (-32 if radical else -16), 'complete differential rank mass')
    return delta


SCALE = 10**35


@lru_cache(None)
def rational_power(r, exponent):
    numerator, degree = exponent.numerator, exponent.denominator
    target = r**numerator * SCALE**degree
    # The float is only an initial speed hint. Exact integer inequalities bind
    # both endpoints, so it is not part of the proof of the enclosure.
    x = int(r**float(exponent)*SCALE)+SCALE//10**12
    while x**degree < target:
        x *= 2
    while True:
        y = ((degree-1)*x + target//x**(degree-1))//degree
        if y >= x:
            break
        x = y
    while x**degree > target:
        x -= 1
    while (x+1)**degree <= target:
        x += 1
    need(x**degree <= target < (x+1)**degree, 'exact rational power enclosure')
    return F(x,SCALE),F(x+1,SCALE)


def moment(delta,beta):
    lo=hi=F(0)
    for r,n in delta.items():
        a,b=rational_power(r,1-beta)
        lo += n*(a if n>=0 else b)
        hi += n*(b if n>=0 else a)
    perturbation=F(3*sum(abs(n)*r for r,n in delta.items()),10**24)
    ml,mh=rational_power(49,beta)
    scaled=(lo*(ml if lo>=0 else mh),hi*(mh if hi>=0 else ml))
    return {'beta':str(beta),'profile_delta':delta,'coefficient_interval':[str(lo),str(hi)],
            'm49_interval':[str(x) for x in scaled],
            'beta_plus_1e_minus24_coefficient_error_bound':str(perturbation),
            'sign':('positive' if lo>perturbation else 'negative' if hi < -perturbation else 'unresolved')}


def sharing_threshold(radical,beta):
    fixed=moment(profile(radical,'already_paid_identical_visits'),beta)
    visit=moment({14:1,2:1,16:-1},beta)
    gl,gu=map(F,fixed['coefficient_interval']);dl,du=map(F,visit['coefficient_interval'])
    need(gu<0 and dl>0,'threshold fixed saving and visit cost')
    lower,upper=-gu/du,-gl/dl
    maximum=lower.numerator//lower.denominator
    need(maximum==upper.numerator//upper.denominator,'threshold unique integer boundary')
    error=F(fixed['beta_plus_1e_minus24_coefficient_error_bound'])+(maximum+1)*F(visit['beta_plus_1e_minus24_coefficient_error_bound'])
    need(gu+maximum*du < -error and gl+(maximum+1)*dl>error,'strict threshold on both neighboring integers')
    total=11520 if radical else 5760
    return {'beta':str(beta),'total_candidate_data_visits':total,
            'maximum_new_visits_for_improvement':maximum,
            'minimum_already_paid_identical_visits':total-maximum,
            'strict_real_break_even_interval':[str(lower),str(upper)],
            'premise':'Only exactly the stated U/W data visits can be marked already paid; no compatibility or free transport is assumed.'}


def rejection(name, thunk, code):
    global DISABLED
    try:
        thunk()
    except ValueError as error:
        need(str(error)==code,'intended control rejection: '+name)
    else:
        raise ValueError('mutation survived: '+name)
    prior=DISABLED
    try:
        DISABLED=prior|{code}
        thunk()
    finally:
        DISABLED=prior
    return {'name':name,'rejected_by':code,'named_guard_deletion':'ACCEPTED',
            'scope':'Sensitivity of this production semantic gate; other independent invoice/source checks remain separate.'}


def fixture(roots,packed,q,U,W,chosen):
    n=len(chosen)
    E=[[F(roots[i][c]*q[j]) for c in range(8)] for i,j in chosen]
    labels=[packed[i][j] for i,j in chosen]
    K=[[sum(E[i][c]*E[j][c] for c in range(8))/8192
        for j in range(n)] for i in range(n)]
    starts={f'x{i}':m.basis([labels[i]]) for i in range(n)}
    starts.update({f'y{i}':() for i in range(n)})
    starts.update({f'c{c}':() for c in range(8)})
    ends={a:m.FULL for a in starts}
    ends.update({f'y{i}':m.perp(labels[i]) for i in range(n)})
    events=[]
    def add(dst,src,v,tag):
        if v:events.append({'op':'add','dst':dst,'src':src,'q':str(v),'tag':tag})
    def climb(reg,frame,tag):
        events.append({'op':'climb','register':reg,'frame':list(frame),'tag':tag})
    for i in range(n):
        for c in range(8):add(f'y{i}',f'c{c}',-E[i][c]/8192,'dirt_prefix')
    for i in range(n):
        if any(E[i]):climb(f'x{i}',U,'source_U')
    for c in range(8):
        climb(f'c{c}',U,'centre_U')
        for i in range(n):add(f'c{c}',f'x{i}',E[i][c],'gather')
    for i in range(n):climb(f'x{i}',m.FULL,'source_FULL')
    for i in range(n):
        if any(E[i]):climb(f'y{i}',W,'target_W')
    for c in range(8):
        events.append({'op':'private','center':f'c{c}','from':list(U),'to':list(W),
                       'targets':[(f'y{i}',str(E[i][c]/8192)) for i in range(n) if E[i][c]],
                       'tag':'private_scatter'})
    for c in range(8):
        climb(f'c{c}',m.FULL,'centre_FULL')
        for i in range(n):add(f'c{c}',f'x{i}',-E[i][c],'cleanup')
    for i in range(n):climb(f'y{i}',m.perp(labels[i]),'target_cap')
    return {'N':n,'ports':chosen,'E':E,'K':K,'starts':starts,'ends':ends,'events':events}

def replay(fix,dual=False,omit=None):
    cols=list(fix['starts']);width=len(cols)
    rows={r:[F(int(i==j)) for j in range(width)] for i,r in enumerate(cols)}
    frames=dict(fix['starts']);paths={r:[] for r in cols}
    private_rank=0;primitive=0;peak=F(1);depth=0
    def add(dst,src,v):
        nonlocal primitive,peak,depth
        need(frames[dst]==frames[src],'literal equal common frame')
        rows[dst]=[x+v*y for x,y in zip(rows[dst],rows[src])]
        peak=max(peak,sum(map(abs,rows[dst])))
        depth=max(depth,max(x.denominator.bit_length()-1 for x in rows[dst]))
        a=abs(v.numerator)
        primitive+=3+a.bit_length()-1+a.bit_count()+v.denominator.bit_length()-1
    for event in fix['events']:
        if event['tag']==omit:continue
        if event['op']=='climb':
            r=event['register'];frame=tuple(event['frame'])
            need(frame==m.basis(frame) and m.included(frames[r],frame),'ordinary monotone frame')
            if len(frame)>len(frames[r]):paths[r].append(len(frame)-len(frames[r]))
            frames[r]=frame
        elif event['op']=='add':
            dst,src,v=event['dst'],event['src'],F(event['q'])
            if dual:dst,src,v=src,dst,-v
            add(dst,src,v)
        else:
            c=event['center'];U,W=tuple(event['from']),tuple(event['to'])
            targets=[(y,F(v)) for y,v in event['targets']]
            need(frames[c]==U and all(frames[y]==W for y,v in targets),'literal equal common frame')
            need(m.included(W,U),'private nested partial frame')
            private_rank+=len(U)-len(W)
            rows['p']=[F(0)]*width;frames['p']=W if dual else U;primitive+=1
            if dual:
                for y,v in targets:add('p',y,v)
                private_readout=list(rows['p']);frames['p']=U;add(c,'p',-F(1))
            else:
                rows['p']=list(rows[c]);primitive+=1
                peak=max(peak,sum(map(abs,rows['p'])))
                frames['p']=W
                for y,v in targets:add(y,'p',v)
            need(rows['p']==(rows[c] if not dual else private_readout), 'private immutable snapshot/readout');primitive+=1;del rows['p'];del frames['p']
    need(frames==fix['ends'],'every source,target,centre endpoint frame')
    for i,r in enumerate(cols):
        expected=[F(int(i==j)) for j in range(width)]
        if r.startswith('x') and dual:
            s=int(r[1:])
            for target in range(fix['N']):expected[cols.index(f'y{target}')]-=fix['K'][target][s]
        if r.startswith('y') and not dual:
            target=int(r[1:])
            for source in range(fix['N']):expected[cols.index(f'x{source}')]+=fix['K'][target][source]
        need(rows[r]==expected,'all arbitrary input and dirty centre columns')
    return {'final_rows':{r:[str(v) for v in rows[r]] for r in cols},'orientation':'dual' if dual else 'forward','paths':paths,'private_rank':private_rank,
            'primitive_before_real_doubling':primitive,'logical_prefix_row_l1':str(peak),
            'logical_prefix_denominator_depth':depth,'ordinary_columns':width,
            'ordinary_column_order':cols}


def accept_delta(actual, expected):
    need({r:n for r,n in actual.items() if n} == {r:n for r,n in expected.items() if n},
         'complete refined source target reader centre private invoice')


def main():
    global m
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    need(args.output.is_absolute(),'output must be absolute')
    output=args.output.resolve()
    for protected in (Path(__file__).resolve().parent,args.inputs.resolve()):
        need(not output.is_relative_to(protected),'output must be external to code and inputs')
    need(not args.output.exists() and not args.output.is_symlink(),'output must be new')
    raw={name:(args.inputs/name).read_bytes() for name in PINS}
    need({name:sha(value) for name,value in raw.items()}==PINS,'authenticated source bytes')
    m=load_geometry(raw['geometry.py'])
    historical=json.loads(raw['frozen/PARTIAL-PAULI-RESULT.json'])
    tree=ast.parse(raw['frozen/module_tiling.py'])
    triple_assignments=[node.value for node in tree.body if isinstance(node,ast.Assign)
                        and any(isinstance(x,ast.Name) and x.id=='TRIPLES' for x in node.targets)]
    need(len(triple_assignments)==1,'unique frozen TRIPLES assignment')
    triples=ast.literal_eval(triple_assignments[0])
    roots,packed,q,support,U,W,chosen,individual,fixed_support=setup(historical)
    tiling=compatibility(roots,packed,q,U,W,triples)
    cases=[];controls=[]
    for name,out_frame in (('ZERO',()),('radical2',W)):
        fix=fixture(roots,packed,q,U,out_frame,chosen)
        forward,dual=replay(fix),replay(fix,True)
        for tag in ('dirt_prefix','gather','private_scatter','cleanup','source_U','centre_U'):
            code=('literal equal common frame' if tag in ('source_U','centre_U')
                  else 'all arbitrary input and dirty centre columns')
            for orientation in (False,True):
                controls.append(rejection(name+':'+tag+':'+str(orientation),
                    lambda fix=fix,orientation=orientation,tag=tag:replay(fix,orientation,tag),code))
        if out_frame:
            for orientation in (False,True):
                controls.append(rejection(name+':target_W:'+str(orientation),
                    lambda fix=fix,orientation=orientation:replay(fix,orientation,'target_W'),
                    'literal equal common frame'))
        radical=bool(out_frame)
        deltas={model:profile(radical,model) for model in
                ('standalone','already_paid_identical_visits','cyclic_refinement')}
        # Independent direct regrouping of every separately named role.
        expected=Counter({15:8,2:8,17:-16})
        expected[13 if radical else 15]+=8
        for r,n in ((12,5760),(2,5760),(14,-5760)):
            expected[r]+=n
        if radical:
            for r,n in ((2,11520),(12,5760),(3,-5760),(13,-5760),
                        (1,5760),(13,5760),(14,-5760)):
                expected[r]+=n
        accept_delta(deltas['cyclic_refinement'],expected)
        costs=[]
        for beta in map(F,('.002','.003','.005')):
            for model,delta in deltas.items():
                result=moment(delta,beta)
                need(result['sign']==('negative' if model=='already_paid_identical_visits' else 'positive'),
                     'complete all-arity differential sign')
                costs.append({'model':model,**result})
        cases.append({'name':name,'output_frame':out_frame,'fixture':serial(fix),
                      'forward':forward,'dual':dual,'full_private_rank':8*(15-len(out_frame)),
                      'full_K_private_C':13872-8*(17-(15-len(out_frame))),
                      'selected_centre_path':[15,2],
                      'standalone_source_path':[14,2],
                      'standalone_target_path':[2,14] if radical else [16],
                      'cyclic_source_path':[1,1,12,2],
                      'cyclic_target_path':[2,2,12] if radical else [3,13],
                      'cyclic_reader_path':[2,1,1,13] if radical else [2,1,14],
                      'profile_deltas':deltas,'costs':costs,
                      'sharing_thresholds':[sharing_threshold(radical,beta)
                                           for beta in map(F,('.002','.003','.005'))]})
    selected=tiling['selected_joins'][0]
    controls.append(rejection('false_free_target_W_visit',
        lambda:accept_nested_path([(),W,tuple(selected['target_arc'])], 'target refined path nested'),
        'target refined path nested'))
    correct=profile(True,'cyclic_refinement')
    omitted=Counter(correct)
    for rank,count in ((1,5760),(13,5760),(14,-5760)):
        omitted[rank]-=count
    controls.append(rejection('omit_added_module_reader_invoice',
                               lambda:accept_delta(omitted,correct),
                               'complete refined source target reader centre private invoice'))
    need(len(controls)==28,'complete Pauli control inventory')
    primitives=8*(2*(3072*7+672*8)+2*(3072*14+672*13)+3)
    dual_prefix=max(F(1)+8*sum(abs(x) for x in a[:k])
                    +F(3,8)*sum(abs(sum(a[i]*z[i] for i in range(k))) for z in roots)
                    for a in roots for k in range(9))
    need(primitives==1258008 and dual_prefix==152,'full support scalar and logical prefix census')
    need(1+3072*8+672*16==35329,'full forward logical prefix')
    need(2*56+16*(1+7+35+1)==816 and
         [2*56+i*(1+7+35+1)+1+7 for i in range(8)]==[120+44*i for i in range(8)],
         'pinned evaluator column order translation')
    physical_support=[{'a':i,'b':j,'sign':sign,
                       'source_id':2160+240*i+2*j+int(sign<0),
                       'label':packed[i][j],'features':[roots[i][c]*q[j] for c in range(8)]}
                      for i,j in support for sign in (-1,1)]
    result={'status':'PASS_PARTIAL_PAULI_AND_PAID_TILING_REFINEMENT_NO_NEW_KAPPA',
        'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
        'input_sha256':PINS,'canonical_roots':roots,'packed_root_pairs':packed,
        'selected_b_lines':[j for j,v in enumerate(q) if v],
        'quadratic_values':q,'source_support_U':U,'radical_U_perp':W,
        'physical_supported_ports':physical_support,'feature_specific_spans':individual,
        'source_columns':[120+44*i for i in range(8)],'feature_weight':1,'denominator':8192,
        'fixed_support_quadratic_audit':fixed_support,
        'cases':cases,'tiling_a_triples':tiling['a_triples'],
        'tiling_b_pairs':tiling['b_pairs'],'tiling_gauge_signs':tiling['gauge_signs'],
        'tiling_frame_cases':tiling['frame_cases'],
        'tiling_frame_cases_sha256':tiling['frame_cases_sha256'],
        'compatibility':{k:v for k,v in tiling.items() if k not in
                         ('a_triples','b_pairs','gauge_signs','frame_cases','frame_cases_sha256')},
        'component_primitives_forward':primitives,'component_primitives_dual':primitives+24,
        'arity_scope':{'fixed_profile_sign':'m^beta is positive for every m>0',
                       'H6_admitted_invoice':'odd L>=3, m>=49, half-width cap>=34; no rank17 event is split',
                       'L1_capped_invoice_checked':False},
        'full_K_component_primitives_unchanged':[247217040,247219488],
        'full_K_bill_status':'Inherited unchanged background; only selected eight-centre scalar arithmetic recomputed.',
        'logical_subword_prefix':{'forward':35329,'dual':str(dual_prefix),'dyadic_depth':10,
                                  'physical_precision_claim':False},
        'controls':controls,'production_rejections':28,'executed_guard_deletions':28,
        'limits':['Ordinary centres are logically restored at FULL, not physically restored to their ZERO entrance values.',
                  'COPY/descent/ERASE and same-order dual readout are explicitly assumed private interfaces; no native primitive implementation is emitted.',
                  'Degenerate U15 and W2 use the inherited dimension-difference tariff; no Clifford phase/rank compiler claim is made.',
                  'The 19-port 46-column diagnostic is exact; the full5760-input identity is the written factor law, not dense matrix replay.',
                  'The new compatible cyclic refinement is fully charged and worsens the tested moment at every admissible arity of this fixed profile.',
                  'No full supplier, shared stock admission, approximate precision, physical controller or new kappa claim.',
                  'Published noncubic-rank and Smith theorem scopes are not expanded or reasserted.']}
    with args.output.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(serial(result),sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'ports':len(physical_support),
                      'frame_cases':len(tiling['frame_cases']),'controls':len(controls),
                      'output_sha256':sha(args.output.read_bytes())}))


if __name__=='__main__':
    main()
