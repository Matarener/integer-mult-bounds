"""Metadata-only full-frame sink certificate for the frozen scalar quotient."""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
from collections import Counter
import gzip,json,time,copy
from l240_extra_column_gate import SOURCE,RP,need,idx

HERE=Path(__file__).resolve().parent

def check(w,events):
    c=w['canonical'];full=1
    need(len(c['frames'][full])==9 and sum(len(f)==9 for f in c['frames'])==1,'Unique full-frame chart')
    n=633+w['owned_extra_slots_by_direction']['backward'];cur=c['start'][:]+[None]*(n-632)
    entered={i for i,f in enumerate(cur) if f==full};census=Counter();arrival=[]
    need(not entered,'No initial full-frame roles')
    for pos,e in enumerate(events):
        typ=e[0]
        if typ=='scalar':
            a,f=e[1:];d=idx(a[1])
            if a[0]=='clear':
                need(d>=632 and f!=full,'No persistent clear or owned full-frame creation')
                cur[d]=f
            else:
                need(cur[d]==f,'Scalar destination frame')
                if a[0] in ('add','copy'):
                    s=idx(a[2]);need(cur[s]==f,'Scalar source frame')
                    if a[0]=='copy':need(d>=632 and f!=full,'No public copying or full owned data')
                    else:
                        need(d!=s,'All ADDs non-aliasing')
                        F(a[3],a[4])
                else:need(a[0]=='scale' and F(a[2],a[3])!=0,'Invertible scalar scale')
            if f==full:
                need(d<632 and a[0] in ('add','scale'),'Full updates only persistent invertible scalar operations')
                if a[0]=='add':need(idx(a[2])<632,'No owned or external source into full subsystem')
                census['full_'+a[0]]+=1
        elif typ in ('warp','climb'):
            d=idx(e[1]) if typ=='warp' else e[2];old,new=e[3:5]
            need(cur[d]==old,'Transport entrance')
            need(old!=full or new==full,'Full roles never leave full chart')
            if new==full:
                need(d<632,'No owned transport into full chart')
                if old!=full:
                    need(d not in entered,'Each persistent role arrives full once')
                    entered.add(d);arrival.append([pos,d,old,typ])
                else:census['full_'+typ]+=1
            cur[d]=new
        else:need(typ in ('phase','adapter'),'Only retained quotient-neutral metadata')
    need(cur[:632]==c['final'],'All final frames')
    need(entered=={i for i,f in enumerate(c['final']) if f==full},'All full roles persist to endpoint')
    need(all(f!=full for f in cur[632:]),'No final owned full source')
    return {'full_persistent_roles':len(entered),'arrivals':arrival,'full_event_counts':dict(census)}

def main():
    start=time.monotonic();raw=SOURCE.read_bytes();w=json.loads(gzip.decompress(raw))
    events=[e for e in w['programs']['backward'] if e[0]!='physical_add']
    result=check(w,events);need(result['full_persistent_roles']==482,'Exact source full-frame bank size')
    R=[[F(a) for a in r] for r in json.loads(RP.read_bytes())]
    gram=[[sum(a*b for a,b in zip(r,s)) for s in R] for r in R]
    need(gram==[[F(56) if i==j else F(0) for j in range(8)] for i in range(8)],'R modes independent with Gram56I')
    fullroles={i for i,f in enumerate(w['canonical']['final']) if f==1}
    need(set(range(112))<=fullroles and not(fullroles&set(range(112,224))),
         'Original full targets have distinct X/helper pivots and no Y pivots')
    # The prior exact 632-row replay binds the baseline endpoint to these
    # source rows: X-A*Y and identity helper outputs. Distinct X/H pivots
    # give rank482; the eight Y-only R rows add eight independent dimensions.
    prior=json.loads((HERE/'l240-extra-column-gate.json').read_text())
    need(prior['source_sha256']==sha256(raw).hexdigest() and prior['all632_baseline_inputs_and408_helpers_verified'],
         'Exact arbitrary-input baseline receipt bound')
    controls={}
    mutants={
        'public_full_clear':events+[['scalar',['clear',['L',0]],1]],
        'full_departure':events+[['climb','mutant',0,1,0,9]],
        'owned_full_observer':events+[['scalar',['clear',['C',0]],1]],
        'external_nonfull_input':events+[['scalar',['add',['L',0],['L',112],1,1],1]],
        'singular_full_update':events+[['scalar',['scale',['L',0],0,1],1]],
    }
    for name,mutant in mutants.items():
        try:check(w,mutant)
        except ValueError as ex:controls[name]=str(ex)
        else:raise ValueError('Mutant accepted: '+name)
    out={'status':'PASS_FIXED_VECTOR_FULL_SINK_RESTORATION_CEILING',
         'source_sha256':sha256(raw).hexdigest(),'direction':'backward','physical_add_omitted':True,
         'baseline_full_target_rank':482,'full_arrival_coordinates':482,
         'R_Gram':'56I8','baseline_full_targets_plus_R_rank':490,
         'full_event_counts':result['full_event_counts'],'semantic_controls_rejected':controls,
         'theorem':'Every existing full-frame snapshot is a fixed linear combination of the482 final full rows, independently of changes confined to lower-frame histories before first full arrival. Captured missing R modes cannot be separately decoded while preserving all482 original full targets in this scalar fixed-vector observer interface.',
         'fixed_mode_stronger_statement':'For changes whose final effect is V*R, Fprime=F+V*R. Since row(F) intersects row(R) trivially and F has482 independent rows, no nonzero pure R combination belongs to row(Fprime).',
         'limits':'No universal physical-feedback impossibility. New full-frame ingress/owned transport, arbitrary new address maps or provider relations, altered target inventory, and direct repair of the prescribed endpoint without a separate pure-mode observer are outside scope.',
         'elapsed_seconds':time.monotonic()-start}
    (HERE/'full-sink-gate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
