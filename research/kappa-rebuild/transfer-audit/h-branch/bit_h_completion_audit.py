#!/usr/bin/env python3
"""Independent actual PR589 H-completion replay and owned-stream audit.

No producer geometry or replay routines are imported. The rational matrix
operations come from our separately implemented stable BIT bridge audit.
Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

HERE=Path(__file__).resolve().parent
AUDIT=HERE.parent
ROOT=AUDIT.parents[2]
BIT=AUDIT.parent/'bit'
sys.path.insert(0,str(AUDIT))
from bit_bridge_audit import eye,transpose,mul,inverse,sub,D,kron


def need(value,message):
    if not value:
        raise AssertionError(message)


def read(path):
    path=Path(path);raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def mm(a,b):
    out=[]
    for row in a:
        result=0
        while row:
            bit=row&-row;result^=b[bit.bit_length()-1];row^=bit
        out.append(result)
    return out


def rank(rows):
    basis={}
    for row in rows:
        while row:
            pivot=row.bit_length()-1
            if pivot not in basis:
                basis[pivot]=row;break
            row^=basis[pivot]
    return len(basis)


def inv(a):
    n=len(a);out=[row|(1<<(n+i)) for i,row in enumerate(a)]
    for col in range(n):
        pivot=next(i for i in range(col,n) if out[i]>>col&1)
        out[col],out[pivot]=out[pivot],out[col]
        for i in range(n):
            if i!=col and out[i]>>col&1:
                out[i]^=out[col]
    result=[row>>n for row in out]
    need(mm(a,result)==[1<<i for i in range(n)],'Independent binary inverse')
    return result


def native_geometry(word,claimed):
    v=word['v'];n=2*v+word['R'];identity=[1<<i for i in range(v)]
    rows=[1<<i for i in range(n)]
    for _,target,sources in word['A']:
        for source in sources:
            rows[target]^=rows[source]
    V=[rows[index]&((1<<v)-1) for index in word['ret']]
    U=[sum(1<<index for index in row) for row in word['scatter']]
    need(len(V)==rank(V)==9,'Nine independent native producer signals')
    selected=[];columns=[]
    for j in range(v):
        column=sum(((row>>j)&1)<<i for i,row in enumerate(V))
        if rank(columns+[column])>len(columns):
            selected.append(j);columns.append(column)
        if len(selected)==9:
            break
    minor=[sum(((row>>a)&1)<<j for j,a in enumerate(selected)) for row in V]
    VU=mm(V,U);M=mm(inv(minor),VU);correction=mm(M,V)
    Uprime=list(U)
    for a,row in zip(selected,M):
        Uprime[a]^=row
    need(not any(mm(V,Uprime)),'Completed producer/consumer defect is square-zero')
    J=[x^y for x,y in zip(identity,mm(U,V))]
    H=[x^y for x,y in zip(identity,mm(Uprime,V))]
    need(mm(H,H)==identity,'All111 columns: H is an involution')
    need(mm(J,J)!=identity and H!=J,'Original J is a genuine non-involution control')
    need([i for i,(x,y) in enumerate(zip(H,J)) if x!=y]==selected,
         'Only the nine declared target rows change')
    exact={'V_rows':V,'U_rows':U,'VU_rows':VU,'selected':selected,
           'selected_minor_rows':minor,'M_rows':M,'correction_rows':correction,
           'Uprime_rows':Uprime,'J_rows':J,'H_rows':H}
    need(all(claimed[key]==value for key,value in exact.items()),'Independent exact geometry equals producer artifact')
    common=list(identity)
    for event in claimed['H_constant_program']:
        op,d,s=event
        need(op=='ADD' and d!=s and 0<=d<v and 0<=s<v,'Literal common-frame XOR instruction')
        common[d]^=common[s]
    need(common==H and len(claimed['H_constant_program'])==1452,'Exact1452-ADD common-frame H')
    broken=list(identity)
    for _,d,s in claimed['H_constant_program'][1:]:
        broken[d]^=broken[s]
    need(broken!=H,'Missing one common-frame ADD must fail')
    raw=[1<<i for i in range(n)]
    for section in ('A','B'):
        for _,d,sources in word[section]:
            for s in sources:
                raw[d]^=raw[s]
    dirt=[]
    for i in range(v):
        need(raw[v+i]&((1<<(2*v))-1)==(1<<(v+i))|J[i],
             'Actual no-scatter raw A/B endpoint has J and unchanged targets')
        sources=[s for s in range(2*v,n) if raw[v+i]>>s&1]
        if sources:
            dirt.append([0,v+i,sources])
    return exact,dirt


def frame_geometry(word):
    metadata=read(BIT/'sources/pr589-regenerated/records/frames.json')['frames']
    projectors={};dimensions={}
    for key,frame in metadata.items():
        basis=[[F(x) for x in row] for row in frame['B']]
        if basis:
            bt=transpose(basis);p=mul(mul(bt,inverse(mul(basis,bt))),basis)
        else:
            p=[[F(0)]*8 for _ in range(8)]
        need(mul(p,p)==p and sum(p[i][i] for i in range(8))==frame['dim'],
             'Independent exact rational frame projector')
        projectors[int(key)]=p;dimensions[int(key)]=frame['dim']
    need(len(projectors)==636 and projectors[0]==[[F(0)]*8 for _ in range(8)] and projectors[1]==eye(8),
         'Native zero/full frame identity')
    for port in range(word['v']):
        line=projectors[word['start'][port]]
        hole=projectors[word['final'][word['v']+port]]
        vector=list(map(F,word['lines'][port]));norm=sum(x*x for x in vector)
        need(norm==4 and line==[[x*y/norm for y in vector] for x in vector],
             'Each exact port has its native rational line')
        need(sub(eye(8),line)==hole,'All111 source lines complement actual final target holes')
    return projectors,dimensions


def expected_body(word,dirt):
    current=list(word['start']);events=[]
    def move(role,frame):
        old=current[role]
        if old!=frame:
            events.append(('MOVE',role,old,frame));current[role]=frame
    for gates in (dirt,word['A'],word['B'],word['C']):
        for frame,d,sources in gates:
            for role in [d]+sources:
                move(role,frame)
            events.extend(('ADD',d,s,frame) for s in sources)
    for role,frame in enumerate(word['final']):
        move(role,frame)
    return events


def strip_rank(event):
    return tuple(event[:4]) if event[0]=='MOVE' else tuple(event)


def replay(word,artifact,geo,projectors,dims,forward):
    v=word['v'];n=2*v+word['R'];owned=n
    values=[1<<i for i in range(n)]+[0]
    current=list(word['start'] if forward else word['final'])+[None]
    invoice=Counter();counts=Counter();move_pairs=set();episodes=[];active=None
    events=artifact['forward' if forward else 'reverse']
    for position,event in enumerate(events):
        op=event[0];counts[op]+=1
        if op=='MOVE':
            _,role,old,new,paid=event
            need(current[role]==old,'MOVE uses the actual current frame')
            low,high=(old,new) if dims[old]<dims[new] else (new,old)
            a,b=projectors[low],projectors[high]
            need(dims[high]-dims[low]==paid and mul(a,b)==a and mul(b,a)==a,
                 'Every paid MOVE is the exact nested rational projector residual')
            current[role]=new;invoice[paid]+=1;move_pairs.add((low,high,paid))
            if role==owned:
                need(active is not None and active['moved'] is False and old==1 and paid==1,
                     'Each owned completion pays one full-to-hole rank-one descent')
                active['moved']=True;active['hole']=new
        elif op=='ADD':
            _,d,s,frame=event
            need(d!=s and current[d]==current[s]==frame,'Every XOR is at the literal shared physical frame')
            if active is not None:
                need(not (0<=d<v),'Every completed source remains immutable throughout the owned episode')
                if d==owned:
                    need(not active['moved'] and 0<=s<v and frame==1,'Only completed X sources enter the gather')
                    active['gather_sources'].append(s)
                else:
                    need(s==owned and active['moved'] and v<=d<2*v,'Only a target reads the transformed owned stream')
                    active['reads'].append(d-v)
            values[d]^=values[s]
        elif op=='OWNED_CLEAR':
            _,role,frame=event
            need(role==owned and active is None and current[role] is None and values[role]==0,
                 'Owned stream has no independent input column or productive credit')
            need(frame==1,'A zero stream can be born at the completed full frame')
            active={'start':position,'moved':False,'gather_sources':[],'reads':[]}
            current[role]=frame
        else:
            need(op=='OWNED_ERASE','No undeclared native primitive')
            _,role,frame=event
            need(role==owned and active is not None and active['moved'] and current[role]==frame,
                 'Only the actual private completed workstream is discarded')
            need(len(active['reads'])==1 and values[role]!=0,'Discard occurs after exactly one useful nonzero correction read')
            target=active['reads'][0];index=geo['selected'].index(target)
            need(sum(1<<s for s in active['gather_sources'])==geo['correction_rows'][index],
                 'Every exact correction row is gathered once from the declared immutable sources')
            need(frame==word['final'][v+target],'Owned descent reaches the exact target hole')
            active['finish']=position;active['port']=target
            active['nonzero_discard_is_paid_linear_stream_work']=True
            episodes.append(active);active=None;values[role]=0;current[role]=None
    expected=[(1<<i)^(geo['H_rows'][i-v] if v<=i<2*v else 0) for i in range(n)]+[0]
    need(values==expected,'All661 independent productive input columns, including439 arbitrary dirty helpers')
    need(current==list(word['final'] if forward else word['start'])+[None] and active is None,
         'Every original endpoint and owned lifetime closes')
    expected_bill=Counter({1:1332,2:1342,3:79,4:44,5:102,6:11,7:10})
    need(invoice==expected_bill,'Complete invoice, including all nine owned line requests')
    need(len(episodes)==9 and [x['port'] for x in episodes]==geo['selected'],'All nine declared correction episodes')
    need(counts==Counter(ADD=11955,MOVE=2920,OWNED_CLEAR=9,OWNED_ERASE=9),'Actual chronological primitive bill')
    return {'direction':'forward' if forward else 'reverse','arbitrary_columns':n,
            'arbitrary_helpers':word['R'],'paid':dict(sorted(invoice.items())),
            'paid_rank_mass':sum(r*c for r,c in invoice.items()),'primitive_counts':dict(counts),
            'distinct_nested_residuals':len(move_pairs),'owned_episodes':episodes}


def physical_completions(word,geo,projectors):
    records=[]
    for port in geo['selected']:
        line=projectors[word['start'][port]];hole=projectors[word['final'][word['v']+port]]
        need(sub(eye(8),hole)==line,'The actual final hole has the exact original port-line complement')
        for f in (1,2):
            full=eye(8*f);line_f=kron(line,eye(f));hole_f=kron(hole,eye(f))
            need(mul(D(hole_f),D(full))==D(line_f),
                 'Physical full-to-hole quotient equals the paid column-lifted rank-one line request')
            need(mul(D(line_f),D(line_f))==eye(16*f),'Exact residual involution at the actual reversed column pairing')
        wrong=projectors[word['start'][(port+1)%word['v']]]
        need(wrong!=line,'Neighboring-line substitution is a failing physical control')
        records.append({'port':port,'native_source_line':word['start'][port],
                        'native_target_hole':word['final'][word['v']+port],
                        'rank':1,'tested_column_counts':[1,2],
                        'universal_column_identity':'D_(P_hole tensor I_f) D_I = D_(P_line tensor I_f), with full C_(8f) tail reversal'})
    return records


def main():
    receipt=read(BIT/'PR589-H-COMPLETION.json');artifact_path=BIT/'PR589-H-NATIVE.json.gz'
    artifact=read(artifact_path);original_path=BIT/'sources/pr589-regenerated/WORD.json.gz'
    need(digest(artifact_path)==receipt['artifact_sha256'],'Exact new native artifact source binding')
    need(digest(original_path)==receipt['source_word_sha256']==artifact['source_sha256'],
         'Exact retained PR589 source binding')
    word=read(original_path);geo,dirt=native_geometry(word,artifact['geometry'])
    need(dirt==artifact['new_D'],'Independent arbitrary-dirty compensation')
    projectors,dims=frame_geometry(word)
    first_owned=next(i for i,event in enumerate(artifact['forward']) if event[0]=='OWNED_CLEAR')
    actual_body=[strip_rank(e) for e in artifact['forward'][:first_owned]]
    need(actual_body==expected_body(word,dirt),'Exact native A/B/C and new compensation placement')
    complete=artifact['forward'][first_owned:]
    need(artifact['reverse'][:len(complete)]==complete,'Backward direction consumes completed Xs before reversing the body')
    reversed_body=[('MOVE',e[1],e[3],e[2]) if e[0]=='MOVE' else e for e in reversed(actual_body)]
    need([strip_rank(e) for e in artifact['reverse'][len(complete):]]==reversed_body,
         'Backward body is exactly the reversed native word')
    replays=[replay(word,artifact,geo,projectors,dims,True),replay(word,artifact,geo,projectors,dims,False)]
    contacts=physical_completions(word,geo,projectors)
    lemma=ROOT/'notes/copied-centers-lemma.tex'
    text=lemma.read_text()
    need('copy/transform/read/discard' in text and 'Copying, pointwise reads and erasure are linear' in text,
         'Retained native ownership model explicitly permits charged nonzero private erasure')
    sources=[Path(__file__),AUDIT/'bit_bridge_audit.py',artifact_path,BIT/'PR589-H-COMPLETION.json',
             BIT/'pr589_h_completion.py',original_path,BIT/'sources/pr589-regenerated/records/frames.json',lemma]
    result={'schema':'independent-native-PR589-H-completion-audit/1',
            'status':'PASS_EXACT_ALL661_COLUMNS_PHYSICAL_CONTACTS_AND_OWNED_ERASURE',
            'source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in sources},
            'geometry':{'ports':111,'selected':geo['selected'],'defect_rank':rank(geo['V_rows']),
                        'VU_rank_before':rank(geo['VU_rows']),'VUprime_rank_after':0,
                        'H_squared_identity':True,'common_frame_H_ADDs':1452},
            'full_native_replays':replays,'physical_completion_contacts':contacts,
            'local_rank_mass_saved':54,'additional_owned_fields':1,
            'owned_erasure_contract':'Complete private gathered stream, linear erasure cost, all contributing original sources immutable; never a productive source.',
            'negative_controls':['The original J is not involutive.','Omitting completion changes exactly nine response rows.',
                                 'Deleting one H-factor ADD changes the operator.','Replacing a paid line by the neighboring line changes the physical request.'],
            'not_proved':['The global H-stage controller monodromy closes.','A new complete mixed tariff or kappa follows from this local result.']}
    out=HERE/'BIT-H-COMPLETION-AUDIT.json';out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'paid':replays[0]['paid'],'rank_mass':replays[0]['paid_rank_mass'],
                      'all_columns':661,'line_contacts':len(contacts),'owned_fields':1}))


if __name__=='__main__':
    main()
