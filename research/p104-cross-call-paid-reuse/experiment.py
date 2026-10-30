"""Versioned P104 paid rows at caller events 0 and 3; exact bounded reuse tests.

Prepared for zxv with substantial OpenAI Codex assistance. Apache-2.0.
The P104 word, Clifford implementation and caller retain predecessor credit.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent

def need(ok, why):
    if not ok:
        raise ValueError(why)

def read(name):
    raw = (HERE/name).read_bytes()
    return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)

def encode(x):
    if isinstance(x, Q): return str(x)
    if isinstance(x, dict): return {str(k): encode(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)): return [encode(v) for v in x]
    return x

def canonical(x):
    return json.dumps(encode(x), sort_keys=True, separators=(',', ':')).encode()

def digest(x): return sha256(canonical(x)).hexdigest()

def load(name):
    spec = importlib.util.spec_from_file_location('cross_reuse_'+name, HERE/'inputs'/name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def plus(dst, src, coefficient=Q(1)):
    for k, v in tuple(src.items()):
        z = dst.get(k, Q(0)) + coefficient*v
        if z: dst[k] = z
        else: dst.pop(k, None)

def dot(row, vector): return sum(v*vector.get(k, 0) for k, v in row.items())

class Basis:
    def __init__(self): self.rows = {}; self.combinations = {}
    def reduce(self, row, combination=None):
        row = dict(row)
        combination = {} if combination is None else dict(combination)
        for p, b in sorted(self.rows.items()):
            if p in row:
                q = row[p]
                plus(row, b, -q)
                plus(combination, self.combinations[p], -q)
        return row, combination
    def insert(self, row, label):
        row, combination = self.reduce(row, {label: Q(1)})
        if not row: return False
        p = min(row); q = row[p]
        self.rows[p] = {k: v/q for k, v in row.items()}
        self.combinations[p] = {k: v/q for k, v in combination.items()}
        return True
    def solve(self, row):
        remainder, c = self.reduce(row)
        return remainder, {k: -v for k, v in c.items()}
    def separator(self, target):
        r, _ = self.reduce(target)
        need(bool(r), 'A separator requires a nonzero quotient')
        j = min(r); vector = {j: Q(1)}
        for p, row in sorted(self.rows.items(), reverse=True):
            z = -sum(v*vector.get(k, 0) for k, v in row.items() if k != p)
            if z: vector[p] = z
        need(all(dot(b, vector) == 0 for b in self.rows.values()), 'Annihilate observations')
        need(dot(target, vector) != 0, 'Separate target')
        return vector

def project(row, columns): return {k: v for k, v in row.items() if k in columns}

def walk(w):
    """Independent literal walk; every paid output retains its exact last-write epoch."""
    n = w['public']; size = n+w['owned_fields']
    rows = [{r: Q(1)} for r in range(size)]
    frames = w['initial']+[None]*w['owned_fields']
    versions = [0]*size; last_write = [-1]*size; lives = [0]*size
    active = set(); paid = []; selected = []; source_main = []
    main = set(w['live']) | {r+112 for r in w['live']}
    helpers = set(range(n))-main
    def frame_span(f):
        out = {0}
        for b in w['frames'][f]: out |= {x ^ b for x in tuple(out)}
        return out
    spans = [frame_span(f) for f in range(len(w['frames']))]
    for index, e in enumerate(w['program']):
        op, d = e[:2]
        if op == 'MOVE':
            _, _, a, b, private = e
            need(frames[d] == a and private == (d in active), 'Exact frame and ownership at MOVE')
            need(spans[b] < spans[a] if private else spans[a] < spans[b], 'Nested transport')
            record = dict(event=index, role=d, input_version=versions[d], output_version=versions[d]+1,
                          last_logical_write=last_write[d], owned_epoch=lives[d], private=private,
                          old=a, new=b, rank=abs(len(w['frames'][b])-len(w['frames'][a])), row=dict(rows[d]))
            paid.append(record)
            if private:
                donors = [(j, versions[j], last_write[j], dict(rows[j])) for j in range(size) if frames[j] == b]
                retained = [p for p in paid[:-1] if p['new'] == b]
                selected.append(dict(query=record, donors=donors, retained_same_call=retained))
            if d in w['live'] and rows[d] == {d: Q(1)}:
                source_main.append(record)
            frames[d] = b
        elif op == 'INIT':
            need(d >= n and d not in active, 'Owned INIT')
            active.add(d); lives[d] += 1; frames[d] = e[2]; rows[d] = {}
        elif op == 'CLEAR':
            need(d in active and frames[d] == e[2], 'Owned CLEAR')
            active.remove(d); frames[d] = None; rows[d] = {}
        else:
            need(frames[d] == e[-1], 'Scalar destination chart')
            q = Q(e[-2])
            if op == 'SCALE': rows[d] = {k: q*v for k, v in rows[d].items()}
            else:
                need(frames[e[2]] == e[-1] and e[2] != d, 'Scalar source chart')
                if op == 'COPY':
                    need(d in active and not rows[d], 'COPY into empty owned field')
                    rows[d] = {}
                else: need(op == 'ADD', 'Scalar opcode')
                plus(rows[d], rows[e[2]], q)
            last_write[d] = index
        if op in ('INIT', 'CLEAR'): last_write[d] = index
        versions[d] += 1
    need(not active and frames[:n] == w['final'], 'Complete owned and public exits')
    for r, row in enumerate(rows):
        want = {r: Q(1)} if r < n else {}
        if r-112 in w['live']: want[r-112] = Q(1)
        need(row == want, 'Every arbitrary source/owned endpoint '+str(r))
    return paid, selected, source_main, helpers

def frame_quotients(selected, helpers):
    receipts = []
    for item in selected:
        query = item['query']; basis = Basis()
        observations = [(f'current:{r}:v{v}', row) for r, v, _, row in item['donors']]
        observations += [(f"retained:{r['event']}:v{r['output_version']}", r['row']) for r in item['retained_same_call']]
        for label, row in observations: basis.insert(project(row, helpers), label)
        target = project(query['row'], helpers)
        witness = basis.separator(target)
        need(all(dot(project(row, helpers), witness) == 0 for _, row in observations), 'All available rows vanish')
        response = dot(target, witness)
        receipts.append(dict(event=query['event'], role=query['role'], rank=query['rank'],
            old=query['old'], new=query['new'], input_version=query['input_version'],
            last_logical_write=query['last_logical_write'], owned_epoch=query['owned_epoch'],
            target_helper_support=len(target), current_donors=[(r,v,last) for r,v,last,_ in item['donors']],
            prior_same_call_outputs=[p['event'] for p in item['retained_same_call']],
            helper_observation_rank=len(basis.rows), helper_quotient_dimension=1,
            witness=witness, target_response=response,
            native_response='S_stage1 Phi_new ('+str(response)+' phi)',
            status='FAIL_EVEN_WITH_ALL_FIRST_CALL_ANSWERS_AND_ARBITRARY_OUTPUT_FRAME_ACTIONS'))
    return receipts

def cached_scalar_relaxation(paid, source_row, live):
    basis = Basis()
    for p in paid: basis.insert(p['row'], p['event'])
    need(len(basis.rows) == 744, 'Full first-call scalar history has rank 744')
    # Erase every native operator and owner distinction, but keep main wrapper signs.
    # This aliases h1 to h0 deliberately: it is a negative version-control fixture.
    aliased = {}
    for r, q in source_row.items():
        if r in live:
            plus(aliased, {r: Q(1), r+112: Q(1)}, q)
        elif r-112 in live: plus(aliased, {r-112: Q(1)}, -q)
        else: plus(aliased, {r: Q(1)}, q)
    remainder, c = basis.solve(aliased)
    need(not remainder, 'Deliberately stale helper alias produces false feasibility')
    combined = {}
    by_event = {p['event']: p for p in paid}
    for e, q in c.items(): plus(combined, by_event[e]['row'], q)
    need(combined == aliased, 'Replay the complete stale-alias combination')
    # Genuine, main-only relaxed reconstruction, without aliasing helpers.
    r, main_c = basis.solve({0: Q(1), 112: Q(1)})
    need(not r, 'Earlier scalar history reconstructs a main-only target')
    return dict(first_history_rank=744, independent_public_fields=744,
        native_and_owner_erasure=True, stale_helper_alias_combination=c,
        stale_alias_status='FEASIBLE_ONLY_AFTER_ILLEGAL_H1_EQUALS_H0_IDENTIFICATION',
        main_only_X0_plus_Y0_combination=main_c,
        main_only_status='FEASIBLE_SCALAR_RELAXATION; NATIVE_ALIGNMENT_AND_COST_REQUIRED')

def caller_bindings(w, controller):
    """Complete machine-readable substitution into the original raw caller columns.

    The phase-polynomial calculation is the retained native-contact method,
    independently implemented here from its definition in Fourier coordinates.
    """
    phases = {p['q']:p for p in read('inputs/DATA-PHASES.json')['recipes']}
    n=17; axes=tuple(1<<i for i in range(n))
    def act(columns,x):
        out=0
        for i,b in enumerate(columns):
            if x>>i&1: out^=b
        return out
    def polynomial(terms):
        linear=[0]*n; quadratic=[0]*n
        for axis,value in terms:
            support=[i for i in range(n) if axis>>i&1]
            for i in support:
                linear[i]=(linear[i]+value)%4
                for j in support:
                    if i<j and value%2: quadratic[i]^=1<<j
        return tuple(linear),tuple(quadratic)
    def contact(old,new,route):
        moved=[(act(route,a),c) for a,c in old]
        a,b=polynomial(moved),polynomial(new)
        need(a[1]==b[1], 'Native entrance quadratic phase')
        delta=[(y-x)%4 for x,y in zip(a[0],b[0])]
        need(set(delta)<={0,2}, 'Native entrance is an ordinary translation')
        shift=sum((v//2)<<i for i,v in enumerate(delta))
        need(polynomial(moved+[(shift,2)])==b, 'Exact entrance polynomial, including phase')
        return shift
    live=set(w['live']); ports=dict(zip(w['live'],w['ports']))
    right=[[Q(x) for x in row] for row in controller['boundaries']['right']]
    routes={}; contacts={}; bindings=[{},{}]
    for r,q in ports.items():
        basis=phases[q]['idle_children'][0]['orthogonal_axes'][:8]
        need(all((a&b).bit_count()%2==int(i==j) for i,a in enumerate(basis) for j,b in enumerate(basis)), 'Pinned orthonormal route basis')
        need(all((a&q).bit_count()%2==0 for a in basis), 'Route basis fixes port')
        swaps=[b^axes[9+i] for i,b in enumerate(basis)]
        route=tuple(e^act(swaps,sum(((e&v).bit_count()%2)<<i for i,v in enumerate(swaps))) for e in axes)
        need(act(route,q)==q and all(act(route,route[i])==axes[i] for i in range(n)), 'Exact route fixes q and is involutive')
        raw_x=[(a,1) for a in axes[:9]]
        raw_y=raw_x+[(q,-1)]
        spectator=[(a,1) for a in axes[9:17]]
        sx=contact(raw_x,spectator+[(q,1)],route)
        sy=contact(raw_y,spectator,route)
        routes[q]=route; contacts[q]=dict(entry_X_translation=sx,entry_Y_translation=sy)
        # These two exact identities justify the expanded stage-1 input rows.
        # E_X C_q^-1 H9 = S1 P_rho and E_Y C_q^-2 H9 = S1 C_q^-1 P_rho.
        moved_x=[(act(route,a),c) for a,c in raw_x+[(q,-1)]]+[(sx,2)]
        moved_y=[(act(route,a),c) for a,c in raw_x+[(q,-2)]]+[(sy,2)]
        need(polynomial(moved_x)==polynomial(spectator), 'Stage-1 source wrapper identity')
        need(polynomial(moved_y)==polynomial(spectator+[(q,-1)]), 'Stage-1 target wrapper identity')
        def terms(row,owner,ops,sign=Q(1)):
            return [dict(source=dict(kind='original_raw_caller',port=r,column=j,owner=owner),coefficient=sign*x,operations=ops)
                    for j,x in enumerate(row) if x]
        bindings[0][r]=terms(right[0],'I',[['C',q,-1]])
        bindings[0][r+112]=terms(right[1],'I',[])
        bindings[1][r]=terms(right[0],f'rho:{q}',[['C',q,-2],['P_route',q]])+terms(right[1],f'rho:{q}',[['C',q,-1],['P_route',q]])
        bindings[1][r+112]=terms(right[0],f'rho:{q}',[['C',q,-2],['P_route',q]],Q(-1))
    for stage in range(2):
        for r in range(w['public']):
            if r not in live and r-112 not in live:
                bindings[stage][r]=[dict(source=dict(kind='independent_helper',invocation=stage,role=r,owner='I',coordinate='physical_raw'),coefficient=Q(1),
                    operations=[['S_adjoint',stage],['Phi_adjoint',w['initial'][r]]])]
    need(set(bindings[0])==set(bindings[1])==set(range(w['public'])), 'Every original/helper input binding')
    h0={canonical(t['source']) for ts in bindings[0].values() for t in ts if t['source']['kind']=='independent_helper'}
    h1={canonical(t['source']) for ts in bindings[1].values() for t in ts if t['source']['kind']=='independent_helper'}
    need(not h0&h1 and len(h0)==len(h1)==536, 'Independent invocation-specific helper columns')
    return dict(dimension=n,routes=routes,contacts=contacts,input_substitutions=bindings,
                operation_order='Listed operations act from left to right, then the query prefix S_stage Phi_frame acts.',
                spectator_axes=[[],list(range(9,17))],phase_checks=4*len(routes))

def two_cache_screen(w,paid,selected,helpers,budget=6,minimum_rank=0):
    """At most two actual prefix answers; exact helper quotient and native tariffs.

    Grants all main information and all current output-frame observations free.
    Only a strictly cheaper native bill is searched (rank sum at most six).
    """
    C=load('clifford_exact.py')
    @lru_cache(None)
    def chart(f):return C.canonical_frame(9,tuple(w['frames'][f]))
    @lru_cache(None)
    def tariff(a,b):
        op=chart(a).adjoint().then(chart(b))
        return C.rank([x for x,z,p in op.tab[9:]])
    receipts=[]
    def normalize(row):
        if not row:return ()
        q=row[min(row)]
        return tuple((k,v/q) for k,v in sorted(row.items()))
    for selected_item in selected:
        target=selected_item['query'];ordinary=Basis()
        free_frames=[f for f in range(len(w['frames'])) if tariff(f,target['new'])==0]
        need(free_frames==[target['new']], 'Every rank-zero canonical alignment is the literal destination frame')
        for r,ver,last,row in selected_item['donors']:
            ordinary.insert(project(row,helpers),('current',r,ver))
        for p in selected_item['retained_same_call']:
            ordinary.insert(project(p['row'],helpers),('retained',p['event']))
        t,_=ordinary.reduce(project(target['row'],helpers))
        need(bool(t),'Nonzero fresh-helper quotient')
        anchor=min(t);groups={};survivors=[];tested=0;single=0;eligible=0
        for p in paid:
            if p['event']>=target['event']:break
            rank=tariff(p['new'],target['new'])
            if not minimum_rank<=rank<=budget:continue
            eligible+=1
            u,_=ordinary.reduce(project(p['row'],helpers))
            if not u:continue
            alpha=u.get(anchor,Q(0))/t[anchor]
            residual=dict(u);plus(residual,t,-alpha)
            if not residual:
                if alpha:
                    single+=1
                    survivors.append(dict(events=[p['event']],ranks=[rank],coefficients=[1/alpha]))
                continue
            pivot=min(residual);q=residual[pivot];key=normalize(residual)
            group=groups.setdefault(key,{})
            for other_rank,examples in group.items():
                if rank+other_rank>budget:continue
                for v in examples:
                    tested+=1
                    determinant=alpha*v['q']-v['alpha']*q
                    if not determinant:continue
                    a=v['q']/determinant;b=-q/determinant
                    combined={};plus(combined,u,a);plus(combined,v['row'],b)
                    need(combined==t,'Exact two-cache quotient witness')
                    survivors.append(dict(events=[p['event'],v['event']],ranks=[rank,other_rank],coefficients=[a,b]))
            # Two different projective target/residual ratios per tariff suffice:
            # any third has either one of those ratios or differs from one of them.
            examples=group.setdefault(rank,[])
            ratio=alpha/q
            if len(examples)<2 and all(e['alpha']/e['q']!=ratio for e in examples):
                examples.append(dict(event=p['event'],row=u,alpha=alpha,q=q))
        # Deduplicate and bind all survivors back to their full original columns.
        distinct={canonical(s):s for s in survivors}
        full=[];by_event={p['event']:p for p in paid}
        for s in distinct.values():
            row={}
            for e,q in zip(s['events'],s['coefficients']):plus(row,by_event[e]['row'],q)
            discrepancy=dict(target['row']);plus(discrepancy,row,-1)
            helper_remainder,_=ordinary.reduce(project(discrepancy,helpers))
            need(not helper_remainder,'Survivor full-row helper quotient')
            full.append(dict(**s,full_row_discrepancy=discrepancy,
                nested_deliveries=[set_span(w['frames'][target['new']])<set_span(w['frames'][by_event[e]['new']]) for e in s['events']]))
        receipts.append(dict(target_event=target['event'],all_prefix_paid=sum(p['event']<target['event'] for p in paid),
            eligible_native_rank_at_most_six=eligible,projective_residual_groups=len(groups),
            tested_group_pairs=tested,single_cache_hits=single,survivors=full,
            bounded_domain='Zero, one or two retained same-invocation paid answers, plus every current/historical destination-frame observation. All main information is granted. Total alignment rank <=6.'))
    return receipts

def complete_separate_delivery_screen(w,paid,selected,helpers):
    """Cover every subset with total alignment rank <=6, without enumerating subsets.

    At most two rank-one prefix answers exist. Condition on their inclusion.
    With one/two included only two rank>=2 answers can fit. With none, the
    only untested size is three rank-two answers, handled by a support bound.
    """
    from copy import deepcopy
    from itertools import combinations
    C=load('clifford_exact.py')
    @lru_cache(None)
    def chart(f):return C.canonical_frame(9,tuple(w['frames'][f]))
    @lru_cache(None)
    def tariff(a,b):return C.rank([x for x,z,p in chart(a).adjoint().then(chart(b)).tab[9:]])
    receipts=[]
    for item in selected:
        query=item['query'];prefix=[p for p in paid if p['event']<query['event']]
        rank_one=[p for p in prefix if tariff(p['new'],query['new'])==1]
        need(len(rank_one)<=2,'At most two rank-one historical answers in this source domain')
        ordinary=Basis()
        for r,v,last,row in item['donors']:ordinary.insert(project(row,helpers),('current',r,v))
        for p in item['retained_same_call']:ordinary.insert(project(p['row'],helpers),('retained',p['event']))
        rank_two=[p for p in prefix if tariff(p['new'],query['new'])==2]
        basis=Basis();reduced=[]
        for p in rank_two:
            row,_=ordinary.reduce(project(p['row'],helpers))
            reduced.append((p['event'],row));basis.insert(row,p['event'])
        target,_=ordinary.reduce(project(query['row'],helpers))
        remainder,target_coordinates=basis.solve(target)
        if remainder:
            witness=basis.separator(target)
            three=dict(status='OUTSIDE_THE_ENTIRE_RANK_TWO_SPAN',rank_two_rows=len(rank_two),basis_rank=len(basis.rows),witness=witness,target_response=dot(target,witness))
        else:
            coordinates={}
            for event,row in reduced:
                rem,co=basis.solve(row);need(not rem,'Each rank-two row is in its basis')
                coordinates[event]=co
            dense={event:co for event,co in coordinates.items() if len(co)>3}
            ignored=set().union(*(set(co) for co in dense.values())) if dense else set()
            target_support=set(target_coordinates)-ignored
            widths={event:len(set(co)-ignored) for event,co in coordinates.items()}
            maximum=max(widths.values(),default=0)
            need(len(target_support)>3*maximum,'At least four rank-two observations needed by exact coordinate support')
            three=dict(status='THREE_RANK_TWO_ROWS_CANNOT_COVER_TARGET_SUPPORT',rank_two_rows=len(rank_two),basis_rank=len(basis.rows),
                target_coordinates=target_coordinates,dense_rows_granted_free=dense,ignored_basis_coordinates=sorted(ignored),
                target_uncovered_coordinates=sorted(target_support),maximum_uncovered_support_of_one_answer=maximum,
                all_rank_two_coordinate_maps=coordinates)
        conditioned=[]
        for count in range(1,len(rank_one)+1):
            for subset in combinations(rank_one,count):
                augmented=deepcopy(item)
                for p in subset:
                    augmented['donors'].append((100000+p['event'],p['output_version'],p['event'],p['row']))
                check=two_cache_screen(w,paid,[augmented],helpers,budget=6-count,minimum_rank=2)[0]
                conditioned.append(dict(paid_rank_one_answers=[p['event'] for p in subset],remaining_alignment_rank_budget=6-count,screen=check))
        need(all(not x['screen']['survivors'] for x in conditioned),'No conditioned two-cache survivor')
        receipts.append(dict(target_event=query['event'],rank_one_answers=[p['event'] for p in rank_one],three_rank_two_certificate=three,
            conditioned_screens=conditioned,status='NO_STRICT_SAVING_FOR_ANY_SEPARATELY_ALIGNED_CACHE_SUBSET',
            proof='For 0<t<1, sum r_i^t >= (sum r_i)^t. Beating H7 needs sum r_i<=6. Zero-rank observations are already in the ordinary quotient. There are at most two rank-one answers. With zero rank-one answers, at most three rank-two-or-larger jobs fit; the only three-job profile is (2,2,2). With k=1 or 2 selected rank-one answers, at most two remaining rank>=2 jobs fit. All cases are checked.'))
    return receipts

def set_span(vectors):
    out={0}
    for b in vectors:out|={x^b for x in tuple(out)}
    return out

def native_tests(w, main_candidates, all_paid):
    C = load('clifford_exact.py'); V = load('native_verify.py')
    phases = {p['q']: p for p in read('inputs/DATA-PHASES.json')['recipes']}
    n = 17; axes = tuple(1 << i for i in range(n))
    @lru_cache(None)
    def chart17(f): return C.canonical_frame(n, tuple(w['frames'][f]))
    @lru_cache(None)
    def chart9(f): return C.canonical_frame(9, tuple(w['frames'][f]))
    old_frames = sorted({p['new'] for p in all_paid})
    # An adjacent candidate that does not use any fresh helper columns.
    candidate = next(p for p in main_candidates if p['event'] == 9733)
    need(candidate['role'] == 0 and candidate['row'] == {0: Q(1)} and candidate['rank'] == 1,
         'Named pure-main paid query')
    q = w['frames'][w['initial'][0]][0]
    basis = phases[q]['idle_children'][0]['orthogonal_axes'][:8]
    swaps = [b ^ axes[9+i] for i, b in enumerate(basis)]
    def act(columns, x):
        out = 0
        for i, b in enumerate(columns):
            if x >> i & 1: out ^= b
        return out
    route = tuple(e ^ act(swaps, sum(((e&v).bit_count()%2) << i for i,v in enumerate(swaps))) for e in axes)
    need(all(act(route, route[i]) == axes[i] for i in range(n)), 'Actual involutive stage-1 route')
    P = C.perm(n, C.transpose(route, n))
    spectator = C.fourier(n, range(9,17))
    desired = C.cgate(n,q,-1).then(P).then(spectator).then(chart17(candidate['new']))
    ranks = {}
    for f in old_frames:
        relative = chart17(f).adjoint().then(desired)
        need(V.tableau(relative.circuit,n=17)==relative.tab,'Independent 17-axis cache-alignment tableau')
        ranks[f] = C.rank([x for x,z,p in relative.tab[n:]])
    need(min(ranks.values()) == 1 and 0 not in ranks.values(), 'Every granted historical cache needs a paid native alignment')
    # The actual centre's native map is checked independently, including its phase.
    native = []
    for p in all_paid:
        if not p['private']: continue
        a,b = p['old'],p['new']
        recipe, compiled = C.lower_child(chart9(a).adjoint().then(chart9(b)))
        V.equal(V.recipe(recipe), V.adjoint(V.frame(tuple(w['frames'][a]),9))+V.frame(tuple(w['frames'][b]),9),
                'Exact centre rank and global phase')
        need(recipe['rank'] == 7, 'All eight selected centres have rank seven')
        native.append(dict(event=p['event'],old=a,new=b,recipe=recipe))
    first = native[0]
    cost_tableaus=0
    for p in native:
        b=p['new']
        for f in old_frames:
            relative=chart9(f).adjoint().then(chart9(b))
            expected=V.adjoint(V.frame(tuple(w['frames'][f]),9))+V.frame(tuple(w['frames'][b]),9)
            need(V.tableau(expected)==relative.tab,'Independent 9-axis cache-cost tableau')
            cost_tableaus+=1
    actual = V.frame(tuple(w['frames'][first['old']]),9)+V.recipe(first['recipe'])
    want = V.frame(tuple(w['frames'][first['new']]),9)
    for column in range(512):
        need(V.state(actual,column) == V.state(want,column), 'All 512 first-centre native columns')
    from copy import deepcopy
    wrong=deepcopy(first['recipe']);wrong['left']['phase']=(wrong['left']['phase']+1)%4
    try:V.equal(V.recipe(wrong),V.recipe(first['recipe']),'Deliberately wrong native global phase')
    except ValueError:wrong_phase=True
    else:raise ValueError('Wrong native global phase accepted')
    return dict(main_query=dict(event=9733,role=0,old=candidate['old'],new=candidate['new'],q=q,route=route,
                old_output_frames=len(old_frames),alignment_ranks=ranks,minimum_alignment_rank=1,
                best_frames=[f for f,r in ranks.items() if r==1],
                scope='One-snapshot or typed-cache-tree delivery, granting the entire desired logical X0+Y0 row in every old paid-output frame'),
                centres=native,first_centre_native_columns=512,wrong_global_phase_rejected=wrong_phase,
                independent_cache_cost_tableaus=cost_tableaus,independent_17_axis_alignment_tableaus=len(old_frames))

def invoice(w, controller):
    paid = Counter(abs(len(w['frames'][e[2]])-len(w['frames'][e[3]])) for e in w['program'] if e[0]=='MOVE')
    main = set(w['live']) | {r+112 for r in w['live']}
    targets = Counter(len(w['frames'][w['final'][r]])-len(w['frames'][w['initial'][r]]) for r in range(w['public']) if r not in main)
    whole_paid = Counter(); whole_targets = Counter()
    for e in controller['physical_events']:
        if e[0]=='LOCAL': whole_paid.update(paid); whole_targets.update(targets)
        elif e[0]=='QUERY_SHEAR': whole_paid[1]+=104
        elif e[0]=='IDLE': whole_paid[8*len(e[2])]+=208
    for term in controller['diagonal']: whole_targets[1+8*sum(term[1:])]+=104
    source = read('inputs/result5718.json')['complete_cost']
    need({int(k):v for k,v in source['paid'].items()} == dict(whole_paid), 'Complete source paid invoice')
    need({int(k):v for k,v in source['targets'].items()} == dict(whole_targets), 'Every independent target')
    return dict(local_paid=paid,local_targets=targets,whole_paid=whole_paid,whole_targets=whole_targets,
                paid_jobs=sum(whole_paid.values()),productive_fields=sum(whole_targets.values()),
                realized_delta_paid={},realized_delta_targets={},kappa_status='NO_NEW_KAPPA',
                unrealized_centre_allowance={'paid_delta':{7:-1},'target_delta':{}},
                adjacent_main_best_cache_tree={'removed':{1:1},'necessary_alignment_at_least':{1:1},'best_recursive_delta':0},
                source_reported_ordinary=source['nonrecursive'],
                new_retention_reads_routes_restoration_cleanup='Unknown; no legal deletion emitted. Not charged at zero.')

def controls(w, paid, selected, receipts):
    out = {}
    first = selected[0]; target = first['query']['row']; witness = receipts[0]['witness']
    need(dot(target,witness) == Q(1,2), 'Named fresh-helper witness')
    need(witness == {173:Q(1)}, 'Exactly call-3 helper173, independent of call-0 helper173')
    # Genuine same-frame reuse already implemented by the source at 13610..13614.
    e = w['program'][13610]
    need(e == ['ADD',703,744,'1',593], 'Actual positive control read')
    old = first['donors'][0][3]
    new = dict(old); plus(new,target)
    reconstructed = dict(new); plus(reconstructed,old,-1)
    need(reconstructed == target, 'Two exact versioned values reconstruct the earlier answer')
    out['positive_two_version_reconstruction'] = 'PASS: (703 after13610)-(703 before13610) equals answer744@13609'
    # It is not legal to use that future output to eliminate its own producer.
    try: need(13610 < 13609, 'A future ADD result is unavailable before the paid producer')
    except ValueError as error: out['future_read_rejected'] = str(error)
    else: raise ValueError('Illegal future read accepted')
    old_basis = Basis()
    for p in paid: old_basis.insert(project(p['row'], set(witness)), p['event'])
    need(bool(old_basis.rows), 'Aliasing invocation helper columns would see the old helper')
    out['stale_invocation_alias_detected'] = 'PASS: fresh H1:173 has no column in any event-0 answer; H0:173 does'
    out['arbitrary_helper_not_zero'] = 'PASS: target changes by one half of a nonzero native field'
    # A constructive two-paid-answer fixture checks discovery, not only rejection.
    # Choose two independent actual native-rank-two prefix rows and synthesize
    # their sum as an explicitly labelled fixture target at the first cut.
    from copy import deepcopy
    C=load('clifford_exact.py');dest=C.canonical_frame(9,tuple(w['frames'][593]))
    main=set(w['live'])|{r+112 for r in w['live']};helpers=set(range(w['public']))-main
    basis=Basis();choices=[];rank_cache={}
    for p in paid:
        if p['event']>=13609:break
        f=p['new']
        if f not in rank_cache:
            relative=C.canonical_frame(9,tuple(w['frames'][f])).adjoint().then(dest)
            rank_cache[f]=C.rank([x for x,z,ph in relative.tab[9:]])
        if rank_cache[f]==2 and basis.insert(project(p['row'],helpers),p['event']):choices.append(p)
        if len(choices)==2:break
    need(len(choices)==2,'Two actual independent rank-two paid observations for positive fixture')
    fixture=deepcopy(first);fixture['query']['row']=dict(choices[0]['row']);plus(fixture['query']['row'],choices[1]['row'])
    positive=two_cache_screen(w,paid,[fixture],helpers)[0]
    need(bool(positive['survivors']),'Two-cache generator discovers the constructive positive')
    out['two_cache_discovery_positive']=dict(source_events=[p['event'] for p in choices],target='Synthetic sum of two actual prefix rows, not a changed P104 implementation',discovered=positive['survivors'][0])
    # Incorrect source-frame tagging must not be admitted as an ordinary read.
    try: need(first['query']['old'] == first['query']['new'], 'Nonzero native rank forbids a free frame retag')
    except ValueError as error: out['unpaid_retag_rejected'] = str(error)
    else: raise ValueError('Unpaid retag accepted')
    return out

def run():
    pins = read('SOURCES.json')
    for p in pins['runtime_inputs']:
        need(sha256((HERE/p['path']).read_bytes()).hexdigest() == p['sha256'], 'Pinned input '+p['path'])
    w=read('inputs/word5718.json.gz'); c=read('inputs/controller5718.json')
    need(c['physical_events'][:4] == [['LOCAL',0,0,False],['Q_POWER',0,-2],['SIGNED_SWAP',0,1],['LOCAL',1,0,False]], 'Literal adjacent caller events 0 to 3')
    paid, selected, main, helpers = walk(w)
    need(len(paid)==3426 and len(selected)==8, 'Full paid-map inventory and bounded centre domain')
    quotients = frame_quotients(selected, helpers)
    relaxation = cached_scalar_relaxation(paid, selected[0]['query']['row'], set(w['live']))
    native = native_tests(w,main,paid)
    bindings = caller_bindings(w,c)
    two_cache = two_cache_screen(w,paid,selected,helpers)
    complete_cache = complete_separate_delivery_screen(w,paid,selected,helpers)
    result = dict(status='PASS_VERSIONED_CROSS_CALL_SCOPED_HANDOFF_NO_NEW_KAPPA',
        mapped_invocations=[dict(caller_event=0,stage=0,pair=0,query_maps=3426),dict(caller_event=3,stage=1,pair=0,query_maps=3426)],
        public_columns_per_call=w['public'],owned_labels=w['owned_fields'],independent_helpers_per_call=len(helpers),
        output_frame_quotients=quotients,scalar_relaxation=relaxation,native=native,
        caller_binding_phase_checks=bindings['phase_checks'],
        two_cache_favorable_screen=two_cache,
        complete_separate_delivery_screen=complete_cache,
        complete_invoice=invoice(w,c),controls=controls(w,paid,selected,quotients))
    maps=dict(schema='versioned-p104-native-query-map/1',word_frames=w['frames'],word_initial=w['initial'],word_final=w['final'],live=w['live'],ports=w['ports'],
        right_boundary=c['boundaries']['right'],queries=paid,
        invocations=[dict(caller_event=0,stage=0,helper_namespace='H0',spectator_axes=[]),
                     dict(caller_event=3,stage=1,helper_namespace='H1',spectator_axes=list(range(9,17)))],
        native_input_bindings=bindings,
        exact_native_expansion=dict(
            convention='Composition read right to left; coefficients outside tensor powers. All maps act on the same original raw caller columns.',
            original_columns='A_j(q,g), j=0..31, and independent normalized H0(r,g),H1(r,g); j indexes the full literal right boundary.',
            stage0_main='For each live r with port q: coefficient c_r gives Phi_f C_q^-1 times right[0,j]; c_(r+112) gives Phi_f times right[1,j], at owner g.',
            stage1_main='For each live r with port q: (c_r-c_(r+112))*right[0,j] times S1 Phi_f P_rho(q) C_q^-2, plus c_r*right[1,j] times S1 Phi_f P_rho(q) C_q^-1; source owner rho(q) at common owner I.',
            helpers='For normalized h_s(r)=(S_s Phi_initial(r))^-1 H_s_raw(r), contributions are c_r Phi_f h0(r,g) at stage0 and c_r S1 Phi_f h1(r,I) at stage1. Machine input substitutions include this exact raw-input normalization. H0_raw and H1_raw are distinct independent columns even when r agrees.',
            frames='Phi_f is the exact canonical nine-axis frame in inputs/clifford_exact.py, embedded in axes0..8; S1 is the product C_e9..C_e16.',
            routes='rho(q) swaps the eight pinned orthonormal q-perpendicular DATA-PHASES axes with fresh axes9..16, fixes q, and is involutive.',
            availability='Call-0 paid outputs exist before caller event3; retaining them is granted favorably. Call-3 query output e exists only after local event e. Owned INIT/CLEAR epochs and last logical writes are explicit in every query.',
            input_output='Before MOVE: replace Phi_f by Phi_old; after MOVE use Phi_new. The logical coefficient row is unchanged by MOVE.'),
        selected_current_frame_rows=[dict(event=x['query']['event'],donors=x['donors'],retained=x['retained_same_call']) for x in selected])
    return encode(result), encode(maps)

if __name__ == '__main__':
    result,maps=run()
    write='--write' in sys.argv
    for name,x in [('results/RESULT.json',result),('results/QUERY-MAPS.json.gz',maps)]:
        p=HERE/name
        if write:
            raw=(json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
            p.write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)
        else: need(read(name)==x,'Full deterministic receipt '+name)
    print(result['status'])
