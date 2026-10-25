#!/usr/bin/env python3
"""Literal asymmetric U9 K-word spliced into the H6 edge compensation word.

All-column finite logical/frame replay; inherited native recipes are explicit
premises. The full bucket network remains far above its helper budget.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import argparse, importlib.util, json, sys
import numpy as np
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
OLD = HERE.parent.parent / 'kappa-major-20261018T1330Z'
REPO = Path('/Users/ross/git/math/integer-mult-bounds')

def need(v, s):
    if not v:
        raise ValueError(s)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

a = load('h6_asymmetric_source', OLD/'bulk-partial/asymmetric.py')
FULL = a.FULL
ZERO = ()
SCALE = 8192

def make_fixture(ports, packed, indices, Us):
    selected = ports[indices]
    A, B, E, weights = a.factors(selected)
    K = (E*weights[None,:]) @ E.T
    pair = selected @ selected.T
    need(not (pair % 4).any(), 'actual integral pairings')
    pair //= 4
    need(np.array_equal(48*K, SCALE*(pair**3-4*pair)), 'actual K matrix')
    C = SCALE*np.eye(len(indices), dtype=np.int64)-K
    edges = [(t,s,int(C[t,s])) for t in range(len(indices))
             for s in range(len(indices)) if C[t,s]]
    for t,s,q in edges:
        need((int(packed[indices[t]]) & int(packed[indices[s]])).bit_count()%2 == 0,
             'every compensation edge has source line inside target cap')
        need(Q(q,SCALE).denominator <= 16, 'dyadic compensation coefficient')
    return A,B,K,edges

def replay(ports, packed, indices, Us, dual=False, defect=None):
    A,B,K,edges = make_fixture(ports,packed,indices,Us)
    n = len(indices); nc = 816; nh = len(edges); count = 2*n+nc+nh
    center = lambda j: 2*n+j
    helper = lambda j: 2*n+nc+j
    rows = np.eye(count+1, count, dtype=np.int64)*SCALE
    frames = [a.m.basis((int(packed[p]),)) for p in indices] + [ZERO]*(count-n+1)
    paths = [[] for _ in range(count+1)]
    counts = Counter(); transcript = sha256(); private_live=False
    private_rank = 0; peak = SCALE
    def record(item):
        transcript.update((json.dumps(item,separators=(',',':'))+'\n').encode())
        counts[item[0]] += 1
    def climb(r,U,phase,private=False):
        need(a.m.basis(U)==U,'canonical frame')
        if not private:
            need(len(a.m.basis(frames[r]+U))==len(U),'nested ordinary climb '+phase)
        d=abs(len(U)-len(frames[r]))
        if d: paths[r].append(d)
        frames[r]=U; record(('climb',r,list(U),phase))
    def add(d,s,num,den,phase):
        nonlocal peak
        if num == 0: return
        need(frames[d]==frames[s],'common physical representative at '+phase)
        need(abs(int(num))*int(np.max(np.abs(rows[s]))) < 2**62,
             'pre-multiplication int64 guard')
        v=num*rows[s]
        need(not (v%den).any(),'exact common-grid scalar division '+phase)
        rows[d] += v//den
        peak=max(peak,int(np.max(np.abs(rows[d]))))
        need(peak < 2**50,'conservative exact int64 guard')
        record(('add',d,s,int(num),int(den),phase))
    def orient(d,s,num,den,phase):
        if dual:d,s,num=s,d,-num
        add(d,s,num,den,phase)
    # Full compensation dirt prefix and source capture precede every K climb.
    for e,(t,s,q) in enumerate(edges):
        if defect != 'omit_compensation_dirt':
            orient(n+t,helper(e),-q,SCALE,'compensation_dirt')
    for e,(t,s,q) in enumerate(edges):
        climb(helper(e),frames[s],'capture_line')
        orient(helper(e),s,1,1,'capture_source')
    if defect == 'premature_FULL':
        for i in range(n):climb(i,FULL,'wrong_old_outer_source_FULL')
    # Exact asymmetric K chronology, including all 816 ordinary centres.
    for c in range(nc):
        for t in range(n):orient(n+t,center(c),-int(B[t,c]),SCALE,'K_dirt')
    for i,p in enumerate(indices):
        if p < 2160:climb(i,Us[p//1080],'source_U')
    for c in a.GIDS:
        U=Us[(c-112)//352]
        climb(center(c),U,'centre_U')
        for s in range(n):orient(center(c),s,int(A[s,c]),1,'partial_gather')
    for i in range(n):climb(i,FULL,'source_FULL')
    for c in range(nc):
        if c in a.GIDS:continue
        climb(center(c),FULL,'centre_FULL')
        for s in range(n):orient(center(c),s,int(A[s,c]),1,'full_gather')
    for c in range(nc):
        need(not private_live and not rows[-1].any(),'private slot clear at entry')
        private_live=True
        U=frames[center(c)]
        private_rank += len(U)
        if not dual:
            frames[-1]=U;rows[-1]=rows[center(c)].copy()
            record(('copy',center(c),count,'K_snapshot'))
            climb(count,ZERO,'private_descent',private=True)
            for t in range(n):add(n+t,count,int(B[t,c]),SCALE,'private_scatter')
            need(np.array_equal(rows[-1],rows[center(c)]),'immutable forward snapshot at ERASE')
        else:
            frames[-1]=ZERO
            for t in range(n):add(count,n+t,int(B[t,c]),SCALE,'dual_private_gather')
            climb(count,U,'dual_private_ascent',private=True)
            add(center(c),count,-1,1,'dual_private_subtract')
        # The copied-total interface erases its own immutable copied/gathered
        # stream. It is not an arbitrary destructive ordinary CLEAR.
        record(('erase',count,c,'paid_copied_total_interface'))
        rows[-1]=0;frames[-1]=ZERO;private_live=False
    for c in a.GIDS:climb(center(c),FULL,'centre_tail')
    for c in range(nc):
        for s in range(n):orient(center(c),s,-int(A[s,c]),1,'K_cleanup')
    for t,p in enumerate(indices):climb(n+t,a.m.perp((int(packed[p]),)),'target_cap')
    # Complete compensation delivery and literal source undo.
    for e,(t,s,q) in enumerate(edges):
        climb(helper(e),frames[n+t],'compensation_cap')
        orient(n+t,helper(e),q,SCALE,'compensation_deliver')
    for e,(t,s,q) in enumerate(edges):climb(helper(e),FULL,'compensation_tail')
    for e,(t,s,q) in enumerate(edges):
        if defect != 'omit_helper_undo':orient(helper(e),s,-1,1,'compensation_cleanup')
    want=np.eye(count,dtype=np.int64)*SCALE
    for i in range(n):
        if dual:want[i,n+i]-=SCALE
        else:want[n+i,i]+=SCALE
    need(np.array_equal(rows[:-1],want),'every arbitrary source target centre and helper column')
    need(not private_live and not rows[-1].any(),'private stream erased')
    need(all(frames[r]==FULL for r in list(range(n))+list(range(2*n,count))),
         'ordinary helper logical restoration at physical FULL')
    H=Counter(r for path in paths for r in path)
    pure=sum(p<2160 for p in indices)
    need(H == Counter({1:2*nh,15:nh,8:2*pure+16,9:32,
                       16:2*n-pure,17:1600}), 'complete fixture histogram')
    need(private_rank==13744,'all 816 private episodes charged')
    return {'dual':dual,'ports':n,'columns':count,'compensation_helpers':nh,
            'ordinary_centres':nc,'private_episodes':nc,'private_rank_mass':private_rank,
            'event_counts':dict(sorted(counts.items())),'logical_transcript_sha256':transcript.hexdigest(),
            'rank_histogram':dict(sorted(H.items())),'peak_abs_scaled_coefficient':peak,
            'all_column_result':'x,y -> x,y+x' if not dual else 'x,y -> x-y,y',
            'all_ordinary_dirt_restored_logically':True}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    asym=json.loads((OLD/'bulk-partial/ASYMMETRIC.json').read_text())
    native=OLD/'partial-native/RECIPES.json'
    need(sha256(native.read_bytes()).hexdigest()=='e5aac49fd8a63ade87637622749a8f3a468c027570a163cdfac6178ed8717b3f',
         'frozen phase-aware U9 recipe binding')
    roots,fourth,ports,packed=a.m.setup()
    indices=asym['arbitrary_input_fixtures']['actual_port_indices']
    Us=[tuple(g['U']) for g in asym['pure_bank_geometries']]
    fixtures=[replay(ports,packed,indices,Us,dual) for dual in (False,True)]
    controls=[]
    # Small all-column fixtures make each defect cheap and decisive.
    small=indices[:2]+indices[9:11]+indices[-2:]
    for dual in (False,True):
        for defect in ('premature_FULL','omit_compensation_dirt','omit_helper_undo'):
            try:replay(ports,packed,small,Us,dual,defect)
            except ValueError as e:controls.append({'dual':dual,'defect':defect,'rejection':str(e)})
            else:raise ValueError('defect escaped '+defect)
    bucket=227312640;ports_count=30960
    H={1:2*bucket,15:bucket,8:4336,9:32,16:2*ports_count-2160,17:1600}
    mass=sum(r*v for r,v in H.items())
    need(mass==17*(bucket+816)+32*ports_count+13744,'full bucket rank-mass identity')
    sources=[Path(__file__),OLD/'bulk-partial/asymmetric.py',OLD/'bulk-partial/ASYMMETRIC.json',
             native,REPO/'research/h6-compensation-network/contract/THEOREM.md',
             REPO/'research/h6-compensation-network/README.md',
             REPO/'research/h6-compensation-network/routes/BUCKETED-SCHEMA.json']
    result={'status':'PASS_ASYMMETRIC_H6_K_LITERAL_COMPENSATION_SPLICE_NO_NEW_KAPPA',
      'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','no_new_kappa':True,
      'source_sha256':{str(x):sha256(x.read_bytes()).hexdigest() for x in sources},
      'actual_fixture_port_indices':indices,'fixtures':fixtures,'controls':controls,
      'full_bucket_histogram':H,'full_bucket_rank_mass':mass,'full_bucket_helpers':bucket,
      'full_private_rank_mass':13744,'full_local_mass_change':-128,
      'native_premises':['Frozen all548 phase-aware U9 recipes plus old272 baseline checks are reused, not replayed here.',
        'Unchanged edge line-to-cap transitions use the upstream universal exact phase theorem.',
        'The paid copied-total interface remains a premise; no finite-tape implementation is supplied.'],
      'scope':'Literal finite all-column scalar/frame composition in both orientations, with every816 K centre and each fixture edge helper. The full all-port bucket composition follows phasewise from the retained K coefficient identity and unchanged bucket endpoint contract; no multi-billion-event execution is claimed.',
      'remaining':['Full network still has227312640 compensation helpers, far above the published selected-target allowance. This closes a chronology gate, not that obstruction.',
        'A much smaller fused compensation network, chronological owner/native-wrapper placement, complete approximate-child precision, finite tape/source costs, matching BIT and joint moment remain missing.'],
      'attribution':'Dominik Scholz PR606, DreamingOfClouds H6 proposal, retained h6-compensation-network and previous local asymmetric U9 construction. Root supplies the explicit complete K splice and independent-column integration replay.'}
    result=json.loads(json.dumps(result));dest=HERE/'COMPOSITION.json'
    if args.write:dest.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(dest.read_text())==result,'stored composition receipt differs')
    print(result['status']);print([(f['columns'],f['event_counts']) for f in fixtures])

if __name__=='__main__':main()
