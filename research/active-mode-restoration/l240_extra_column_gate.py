"""Exact scalar fixed-vector quotient for one granted active injection.

All native address operators are evaluated on their common fixed vector.
No assertion of physical availability of the missing mode at the injection
frame is made. Original rows and unit-injection response are replayed together.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import gzip,json,time

HERE=Path(__file__).resolve().parent
SOURCE = ORIGINAL = RP = None

def need(ok,msg):
    if not ok:raise ValueError(msg)

def axpy(a,b,c):
    out=dict(a)
    for k,v in b.items():
        value=out.get(k,F(0))+c*v
        if value:out[k]=value
        else:out.pop(k,None)
    return out

def scaled(a,c):return {k:v*c for k,v in a.items() if v*c}
def idx(ref):return ref[1]+632*(ref[0]=='C')

def main():
    began=time.monotonic()
    w=json.loads(gzip.decompress(SOURCE.read_bytes()))
    original=json.loads(gzip.decompress(ORIGINAL.read_bytes()))
    canonical=w['canonical'];R=[[F(v) for v in row] for row in json.loads(RP.read_bytes())]
    es=[(i,e) for i,e in enumerate(w['programs']['backward']) if e[0]!='physical_add']
    selected=['climb','scalar_refactor',240,280,1,1]
    hits=[(j,i) for j,(i,e) in enumerate(es) if e==selected]
    need(len(hits)==1,'Unique exact late L240 paid climb')
    event_index,word_index=hits[0]
    need(word_index==17978 and original['programs']['backward'][17155]==selected,
         'Exact original/new paid event binding')
    need(w['source_sha256']==sha256(ORIGINAL.read_bytes()).hexdigest(),'Source packet hash binding')
    owned=1+w['owned_extra_slots_by_direction']['backward']
    rows=[{i:F(1)} for i in range(632)]+[{} for _ in range(owned)]
    responses=[F(0)]*len(rows);cur=canonical['start'][:]+[None]*owned
    observations=[];seen=set();basis={};witness=None
    endpoint_impulse=None

    def save(d,pos):
        nonlocal witness
        if cur[d]!=1 or not rows[d]:return
        key=(tuple(sorted(rows[d].items())),responses[d])
        if key in seen:return
        seen.add(key)
        oi=len(observations)
        observations.append({'owner':d,'after_event':pos,'row':dict(rows[d]),'v':responses[d]})
        row=dict(rows[d]);beta=responses[d];recipe={oi:F(1)}
        while row:
            pivot=min(row)
            if pivot not in basis:
                z=1/row[pivot]
                basis[pivot]=(scaled(row,z),beta*z,scaled(recipe,z))
                return
            b,v,rec=basis[pivot];z=row[pivot]
            row=axpy(row,b,-z);beta-=z*v;recipe=axpy(recipe,rec,-z)
        if beta and witness is None:
            witness=(scaled(recipe,1/beta),beta)

    for d in range(632):save(d,-1)
    for pos,(rawpos,e) in enumerate(es):
        if pos==event_index:
            need(cur[240]==280,'Granted injection is at actual rank-eight frame')
            responses[240]+=1
        typ=e[0];d=None
        if typ=='scalar':
            a,f=e[1:];d=idx(a[1])
            if a[0]=='clear':
                need(d>=632,'Only owned clearing')
                rows[d]={};responses[d]=F(0);cur[d]=f
            elif a[0] in ('add','copy'):
                s=idx(a[2]);need(cur[s]==cur[d]==f,'Literal scalar coframing')
                if a[0]=='copy':
                    need(d>=632,'Copy only into owned scratch')
                    rows[d]=dict(rows[s]);responses[d]=responses[s]
                else:
                    coef=F(a[3],a[4]);rows[d]=axpy(rows[d],rows[s],coef)
                    responses[d]+=coef*responses[s]
            else:
                need(a[0]=='scale' and cur[d]==f,'Literal scalar scale')
                coef=F(a[2],a[3]);rows[d]=scaled(rows[d],coef);responses[d]*=coef
        elif typ=='warp':
            d=idx(e[1]);need(cur[d]==e[3],'Warp entrance frame');cur[d]=e[4]
        elif typ=='climb':
            d=e[2];need(cur[d]==e[3],'Paid entrance frame');cur[d]=e[4]
        else:need(typ in ('phase','adapter'),'Known center-free event type')
        if d is not None:save(d,rawpos)
        need(time.monotonic()-began<60,'Bounded lightweight quotient runtime')
    need(cur[:632]==canonical['final'] and all(not r for r in rows[632:]),'Baseline final frames and owned return')
    need(all(v==0 for v in responses[632:]),'Granted injection leaves no final owned residue')
    for i in range(632):
        expected={i:F(1)}
        if i<112:
            expected[i+112]=F(-1)
            for r in R:
                if r[i]:
                    for j,a in enumerate(r):
                        if a:expected[j+112]=expected.get(j+112,F(0))+r[i]*a/4
        need(rows[i]=={k:v for k,v in expected.items() if v},'All632 baseline arbitrary-input endpoint rows')

    def reduce_target(row):
        residual=dict(row);value=F(0);recipe={}
        while residual:
            p=min(residual)
            if p not in basis:break
            b,beta,rec=basis[p];z=residual[p]
            residual=axpy(residual,b,-z);value+=z*beta;recipe=axpy(recipe,rec,z)
        return residual,value,recipe

    modes=[{112+i:a for i,a in enumerate(r) if a} for r in R]
    need(all(reduce_target(m)[0] for m in modes),'All eight source modes outside old full-frame span')
    cert=None
    if witness is not None:
        q,_=witness;check={};checkv=F(0)
        for i,coef in q.items():
            check=axpy(check,observations[i]['row'],coef);checkv+=coef*observations[i]['v']
        need(not check and checkv==1,'Direct exact qM=0, qv=1 certificate')
        cert=[{'observation':i,'owner':observations[i]['owner'],
               'after_event':observations[i]['after_event'],'coefficient':str(coef)} for i,coef in sorted(q.items())]
    hres,hvalue,hrecipe=reduce_target({240:F(1)})
    need(not hres,'Baseline L240 independent endpoint available in full-frame span')
    negative=None
    if witness is None:
        # A directly checked certificate that the response is a function of
        # the old observations, rather than a new independent observation.
        z={}
        for p,(row,beta,_) in sorted(basis.items(),reverse=True):
            val=beta-sum(a*z.get(k,F(0)) for k,a in row.items() if k!=p)
            if val:z[p]=val
        need(all(sum(a*z.get(k,F(0)) for k,a in o['row'].items())==o['v']
                 for o in observations),'Direct Mz=v certificate for every observation')
        target=modes[5];residual,_,_=reduce_target(target)
        u={min(residual):F(1)}
        for p,(row,_,_) in sorted(basis.items(),reverse=True):
            val=-sum(a*u.get(k,F(0)) for k,a in row.items() if k!=p)
            if val:u[p]=val
            else:u.pop(p,None)
        pairing=sum(a*u.get(k,F(0)) for k,a in target.items())
        need(pairing!=0,'Missing mode has nonzero dual pairing')
        u=scaled(u,1/pairing)
        need(all(sum(a*u.get(k,F(0)) for k,a in o['row'].items())==0
                 for o in observations),'Direct Mu=0 certificate for every observation')
        mz=sum(a*z.get(k,F(0)) for k,a in target.items())
        dual=axpy(scaled(u,1+mz),z,F(-1))
        need(sum(a*dual.get(k,F(0)) for k,a in target.items())==1,'Mode5 dual pairing one')
        need(all(sum(a*dual.get(k,F(0)) for k,a in o['row'].items())+o['v']==0
                 for o in observations),'Direct (M+v mode5)dual=0 for every changed observation')
        need(dual.get(240,F(0))==-hvalue!=0,'Same dual separates original helper240')
        # Meaningful witness controls: removing an actual nonzero coordinate
        # from z must fail Mz=v; an independent dirty baseline paired with an
        # injected copy admits cancellation, a single dirty copy does not.
        badz=dict(z);first=min(z);badz.pop(first)
        need(any(sum(a*badz.get(k,F(0)) for k,a in o['row'].items())!=o['v']
                 for o in observations),'Dropped restoration-certificate coordinate rejects')
        toyM=[{0:F(1)},{0:F(1)}];toyv=[F(0),F(1)];toyq=[F(-1),F(1)]
        need(sum(toyq[i]*toyv[i] for i in range(2))==1 and
             sum(toyq[i]*toyM[i][0] for i in range(2))==0,'Distinct before/after dirty observation positive control')
        need(toyv[1]!=0 and toyM[1][0]!=0,'One dirty response cannot be treated as clean')
        negative={'Mz_equals_v':[[k,str(a)] for k,a in sorted(z.items())],
                  'Mu_equals0_mode5_u_equals1':[[k,str(a)] for k,a in sorted(u.items())],
                  'changed_observation_annihilator':[[k,str(a)] for k,a in sorted(dual.items())],
                  'mode5_pairing':'1','helper240_pairing':str(dual.get(240,F(0))),
                  'mode5_dot_z':str(mz),'all4868_rows_checked_directly':True,
                  'dropped_z_coordinate_rejected':first,'before_after_dirty_positive_control':True}
    record={'status':'EXACT_L240_GRANTED_ACTIVE_INJECTION_QUOTIENT',
        'source_sha256':sha256(SOURCE.read_bytes()).hexdigest(),
        'original_sha256':sha256(ORIGINAL.read_bytes()).hexdigest(),
        'R_sha256':sha256(RP.read_bytes()).hexdigest(),
        'direction':'backward','original_event':17155,'word_event':word_index,
        'filtered_event':event_index,'paid_event':selected,'injection':'Unit independent marker into L240 immediately before selected paid climb',
        'injection_frame':280,'injection_frame_rank':8,
        'all632_baseline_inputs_and408_helpers_verified':True,
        'full_frame_observations':len(observations),'baseline_full_rank':len(basis),
        'augmented_rank':len(basis)+(witness is not None),'all8_modes_missing_before_injection':True,
        'pure_granted_mode_recoverable':witness is not None,
        'witness_qM0_qv1':cert,
        'negative_certificate':negative,
        'baseline_helper240_graph_coefficient':str(hvalue),
        'final_impulse_main':[[i,str(v)] for i,v in enumerate(responses[:224]) if v],
        'final_impulse_helpers':[[i,str(v)] for i,v in enumerate(responses[:632]) if i>=224 and v],
        'no_free_helper_erasure':True,'physical_mode_availability_proved':False,
        'scope':'Exact necessary common-fixed-vector quotient only; grants all chronological full-frame snapshots and missing-mode injection at rank8. Captures, storage, phase-aware maps, legal source availability, actual main target restoration and complete invoice remain unproved.',
        'elapsed_seconds':time.monotonic()-began}
    (HERE/'l240-extra-column-gate.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    payload=[{'owner':o['owner'],'after_event':o['after_event'],
              'row':[[k,str(v)] for k,v in sorted(o['row'].items())],'v':str(o['v'])} for o in observations]
    (HERE/'l240-full-observations.json.gz').write_bytes(gzip.compress(json.dumps(payload,separators=(',',':')).encode(),mtime=0))
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()
