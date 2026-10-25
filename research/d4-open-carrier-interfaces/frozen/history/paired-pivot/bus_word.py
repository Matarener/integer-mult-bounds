#!/usr/bin/env python3
"""Exact dirty D4 bus scalar maps and actualh7 frame/compiler witnesses.

The source/helper endpoint is a joint code. This program does NOT assert
that a sum of pairwise frame distances is a joint native child width.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
from d4_geometry import basis,span,dot,need,mm,tr,eye
HERE=Path(__file__).resolve().parent
REPO=Path('/Users/ross/git/math/integer-mult-bounds')

def hash_file(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def apply_rows(rows,slots,A):
    old=[rows[j][:]for j in slots]
    for i,j in enumerate(slots):rows[j]=[sum(A[i][k]*old[k][c]for k in range(len(slots)))for c in range(len(rows))]
def add(rows,dst,src,q):rows[dst]=[a+q*b for a,b in zip(rows[dst],rows[src])]

def scalar(bus,missing=None,open_end=False,reverse=False,physical=False):
    # The feature basis is optional. The identity bus only needs one physical
    # field per O-orbit, and therefore admits a literal permutation endpoint.
    H=[eye(4)for _ in range(3)]if physical else[[[F(a)for a in r]for r in bus[k]]for k in('H_A','H_B','H_C')]
    source_groups=[];labels=[]
    for g in range(3):
        slots=[]
        for j in range(4):
            if g==0 and j==missing:slots.append(None)
            else:slots.append(len(labels));labels.append((g,j))
        source_groups.append(slots)
    n=len(labels);helper=list(range(2*n,2*n+4));N=2*n+4;rows=eye(N);prefix=1;depth=0;adds=0
    def observe():
        nonlocal prefix,depth
        prefix=max(prefix,max(sum(abs(x)for x in r)for r in rows))
        depth=max(depth,max(x.denominator.bit_length()-1 for r in rows for x in r if x))
    # Formfeaturecoordinates at the actual rank3 source-group frames.
    for g in range(3):
        if g==0:continue
        apply_rows(rows,source_groups[g],H[g]);observe()
    def swap(a,b):
        nonlocal adds
        add(rows,a,b,1);observe();add(rows,b,a,-1);observe();add(rows,a,b,1);observe()
        rows[b]=[-x for x in rows[b]];observe();adds+=3
    def deliver(g):
        nonlocal adds
        # Target g is in physical/canonical rootcoordinates; helper isfeaturebasis.
        for k,src in enumerate(source_groups[g]):
            if src is None:continue
            dst=n+src
            for j in range(4):
                if H[g][j][k]:add(rows,dst,helper[j],H[g][j][k]);adds+=1;observe()
    for j,a in enumerate(source_groups[0]):
        if a is not None:swap(helper[j],a)
    deliver(0)
    middle,last=(2,1)if reverse else(1,2)
    for j,a in enumerate(source_groups[middle]):swap(helper[j],a)
    deliver(middle)
    for j,a in enumerate(source_groups[last]):swap(helper[j],a)
    deliver(last)
    if not open_end:
        for j,a in enumerate(source_groups[0]):
            if a is not None:swap(helper[j],a)
    for g in(1,2):apply_rows(rows,source_groups[g],tr(H[g]));observe()
    # The target response isI, including arbitrary target and helper columns.
    for j in range(n):
        expected=[F(int(c==n+j)+int(c==j))for c in range(N)]
        need(rows[n+j]==expected,'complete dirty bus identity target response')
    nt=list(range(n))+helper;code=[[rows[i][j]for j in nt]for i in nt]
    if not open_end:
        need(mm(mm(code,code),code)==eye(n+4),'closedbus coupled source/helper code has exactorder3')
        if missing is None:
            need(all(rows[helper[j]]==eye(N)[helper[j]]for j in range(4)),'all four arbitrary ordinaryhelpers restored')
    else:need(mm(mm(code,code),mm(code,code))==eye(n+4),'openbus coupledcode hasorder4')
    need(mm(code,tr(code))==eye(n+4),'source/helper code is exactly orthogonaldyadic')
    if physical:
        need(all(sum(x!=0 for x in r)==1 and sum(r)==1 for r in code),'physical endpoint is a literal unsigned field permutation')
    return {'n':n,'input_columns':N,'source_coordinate_order':labels,
        'source_helper_code':[[str(a)for a in r]for r in code],
        'target_response':'I; no helperdirt or changed-source terms',
        'code_order':3 if not open_end else 4,
        'helpers_canonically_restored':4 if missing is None and not open_end else 3 if missing is not None and not open_end else 0,
        'canonical_prefix_l1':str(prefix),'canonical_denominator_depth':depth,
        'scalar_complex_ADDs':adds,'scalar_complex_negations':4*(3 if open_end else 4)-(1 if missing is not None and open_end else 2 if missing is not None else 0),
        'basis':'physical O-paired root fields'if physical else'actual dyadic feature basis',
        'ordinary_helpers':4,'private_fields':0,
        'scope':'All-input scalar identity, exactsource/helper endpointcode. Doesnotadmitan independentnativewidthforanymixedcodeblock.'}

def compiler(bus):
    path=REPO/'research/kernel92-frame-composition/vendor/pr531/vendor/clifford/clifford_exact.py'
    need(hash_file(path)=='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','actualcompilerpin')
    spec=importlib.util.spec_from_file_location('bus_actual_clifford',path);ce=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ce;spec.loader.exec_module(ce)
    n=7;G=bus['groups7'];U=[basis(g)for g in G];VA=basis(list(U[1])+list(U[2]));VB=basis(list(U[0])+list(U[2]));VC=basis(list(U[0])+list(U[1]));FULL=basis(range(1,128))
    def omega7(x):
        y=0
        for j,v in enumerate(bus['O7_columns']):
            if x>>j&1:y^=v
        return y
    need(all(omega7(G[g][k])==G[(g+1)%3][k]for g in range(3)for k in range(4)),'frozen groups are physically O-paired coordinatewise')
    def distance(A,B):return len(A)+len(B)-2*((len(span(A)&span(B))).bit_length()-1)
    def actual(A,B):
        op=ce.canonical_frame(n,A).adjoint().then(ce.canonical_frame(n,B));rec,lit=ce.lower_child(op)
        need(rec['rank']==distance(A,B),'actualbinaryframeandFourierrankagree')
        need(lit.tab==op.tab and lit.zero_state()==op.zero_state(),'actualcompilerfullphase')
        return rec['rank']
    def actual_ops(A,B):
        op=A.adjoint().then(B);rec,lit=ce.lower_child(op)
        need(lit.tab==op.tab and lit.zero_state()==op.zero_state(),'positive-native exacttransitionphase')
        return rec['rank']
    routes={'closed':[U[0],U[1],U[2],U[0]],
        'open':[U[0],U[1],U[2],VB,VC],
        'punctured_missing_closed':[U[1],U[2],U[0]],
        'reverse_closed':[U[0],VA,VC,VB],
        'reverse_punctured_missing':[U[2],VC,VB],
        'dense_coupled_I':[U[2],U[1],U[0],U[1],VA,VB,VC],
        'dense_I_cleanup':[VC,VB,VA,VB,VC]}
    output={}
    for name,frames in routes.items():
        ranks=[actual(A,B)for A,B in zip(frames,frames[1:])]
        output[name]={'frames':frames,'ranks':ranks,'paid_rank':sum(ranks),'independent_E_to_U_rank':actual(frames[0],frames[-1])}
    need(output['closed']['ranks']==[2,2,2],'closeddirtybuscontactranks')
    need(output['open']['ranks']==[2,2,1,2],'opendirtybuscontactranks')
    need(output['dense_coupled_I']['paid_rank']==11 and output['dense_I_cleanup']['paid_rank']==8,'complete dense source-code and cleanupinvoice')
    # Every actualsource and target can climb its claimed common contact and cap.
    data=[];reverse_data=[];open_data=[];open_hist=Counter()
    for g in range(3):
        for k,p in enumerate(G[g]):
            q=bus['target_entrance7'][4*g+k]
            src=bus['source_terminal_caps7'][4*g+k];tgt=bus['target_terminal_caps7'][4*g+k]
            need(span(U[g])<=span(src),'sourcecommonframeinsidepairedcap')
            need(span(U[(g+1)%3])<=span(tgt),'targetcommonframeinsidepairedcap')
            sourcein=ce.cgate(n,p);targetin=ce.cgate(n,q);full=ce.fourier(n)
            sourceout=ce.cgate(n,q).adjoint().then(full)
            targetout=ce.cgate(n,p).adjoint().then(full)
            sp=[actual_ops(sourcein,ce.canonical_frame(n,U[g])),actual_ops(ce.canonical_frame(n,U[g]),sourceout)]
            tp=[actual_ops(targetin,ce.canonical_frame(n,U[(g+1)%3])),actual_ops(ce.canonical_frame(n,U[(g+1)%3]),targetout)]
            need(sp==tp==[2,3],'h7 closedbusdataentryandterminalranks')
            sg=ce.canonical_frame(n,src).adjoint().then(sourceout)
            tg=ce.canonical_frame(n,tgt).adjoint().then(targetout)
            sm,srec=ce.monomial(sg);tm,trec=ce.monomial(tg)
            need(sm.tab==sg.tab and sm.zero_state()==sg.zero_state(),'sourcecapendpoint exactmonomialgauge')
            need(tm.tab==tg.tab and tm.zero_state()==tg.zero_state(),'targetcapendpoint exactmonomialgauge')
            sr=sourcein.adjoint().then(sourceout);tt=targetin.adjoint().then(targetout)
            need(sr.tab==tt.tab and sr.zero_state()==tt.zero_state(),'actualsamepairedresidualincludingphase')
            offdiag=sourcein.adjoint().then(targetout);wantoff=ce.xgate(n,p).then(full)
            need(offdiag.tab==wantoff.tab and offdiag.zero_state()==wantoff.zero_state(),'original native target offdiagonal is exactly F7 X_p')
            data.append({'group':g,'coordinate':k,'p':p,'q':q,'source_ranks':sp,'target_ranks':tp,
                'source_entrance_events':sourcein.circuit,'target_entrance_events':targetin.circuit,
                'source_endpoint_events':sourceout.circuit,'target_endpoint_events':targetout.circuit,
                'canonical_to_actual_sourcecap':srec,'canonical_to_actual_targetcap':trec})
            # The open bus delivers C at VC, so this target must really stop
            # at that rank4 frame before reaching its rank6 actual cap.
            targetops=[targetin,ce.canonical_frame(n,U[(g+1)%3])]
            if g==2:targetops.append(ce.canonical_frame(n,VC))
            targetops.append(targetout)
            ot=[actual_ops(a,b)for a,b in zip(targetops,targetops[1:])]
            need(ot==([2,1,2]if g==2 else[2,3]),'open target visits actual late delivery contact')
            for r in sp+ot:open_hist[r]+=1
            open_data.append({'group':g,'coordinate':k,'source_ranks':sp,'target_ranks':ot,
                'target_delivery_frame':VC if g==2 else U[(g+1)%3],
                'target_contact_events':[op.circuit for op in targetops]})
            sv=(VB,VC,VA)[g];tv=(VA,VB,VC)[g]
            sranks=[actual_ops(sourcein,ce.canonical_frame(n,U[g])),actual(U[g],sv),actual_ops(ce.canonical_frame(n,sv),sourceout)]
            tranks=[actual_ops(targetin,ce.canonical_frame(n,U[(g+1)%3])),actual(U[(g+1)%3],tv),actual_ops(ce.canonical_frame(n,tv),targetout)]
            need(sranks==tranks==[2,1,2],'actualreversebusdataframesandphases')
            reverse_data.append({'group':g,'coordinate':k,'source_contact':sv,'target_contact':tv,'source_ranks':sranks,'target_ranks':tranks})
    tail=actual(U[0],FULL);need(tail==4,'h7 FULLtailrank4')
    # O3's nondegeneratecommontriple has alternatingrank4 complement in h7;
    # the full D4rootspan itself has rank5/radical2. No coordinateI4 assumption.
    rootspan=basis(sum(G,[]));rad=basis(v for v in span(rootspan)if all(not dot(v,w)for w in rootspan))
    need((len(rootspan),len(rad))==(5,2),'minimalambientcertificate')
    need(output['reverse_closed']['ranks']==[3,2,2]and actual(VB,FULL)==3,'reversehelperFULLtailinvoice')
    need(output['reverse_punctured_missing']['ranks']==[3,2],'reversepuncturedhelperpath')
    for r in output['open']['ranks']:open_hist[r]+=4
    need(open_hist==Counter({1:8,2:40,3:20}),'complete actual open bus rank histogram')
    # Pure physical-coordinate open bus: no H_B/H_C mixing. Track the value
    # owners, rather than comparing the helper output to its own input slot.
    # Each record is a genuine monomial-wrapped native Clifford, including
    # the actual output phase, not merely a subspace-distance statement.
    carrier=[]
    for k in range(4):
        incoming=[ce.canonical_frame(n,U[0])]+[ce.cgate(n,G[g][k])for g in range(3)]
        outgoing=[ce.cgate(n,omega7(G[g][k])).adjoint().then(ce.fourier(n))for g in range(3)]+[ce.canonical_frame(n,VC)]
        ranks=[];circuits=[]
        for a,b in zip(incoming,outgoing):
            op=a.adjoint().then(b);rec,lit=ce.lower_child(op)
            need(lit.tab==op.tab and lit.zero_state()==op.zero_state(),'open physical carrier full native phase')
            ranks.append(rec['rank']);circuits.append({'rank':rec['rank'],'input_events':a.circuit,'output_events':b.circuit,'lowering':rec})
        need(ranks==[3,5,5,5],'actual pure-permutation owner channel ranks')
        carrier.append({'coordinate':k,'value_routes':['helper to source A','source A to source B','source B to source C','source C to helper'],'ranks':ranks,'circuits':circuits})
    return {'compiler_sha256':hash_file(path),'h':7,'data_rows':data,'reverse_data_rows':reverse_data,'routes':output,
        'FULLtail_rank':tail,'rootspan_rank':5,'rootspan_radical_rank':2,'open_physical_carriers':carrier,
        'open_data_rows':open_data,'actual_open_rank_histogram':open_hist,'actual_open_native_rank_mass':sum(r*c for r,c in open_hist.items()),
        'exact_gauge_contract':'Positivecgate(P),positivecgate(Q)inputs; sourceendpointF7*C_Q^-1,targetendpointF7*C_P^-1. Contactframescanonical_frame(U). HelperentrancecanonicalUA/UB; helperopenendcanonicalVC; FULLtailF7.',
        'phase_scope':'ExactbinarytableauandGaussianzero-state fixes completeCliffordoperator. Actualpairedendpointsandtheircanonicalcaprankzeroadaptersareemitted,notinferredfromsubspaces. Adaptermovement/primitivesnotyetinvoiced.',
        'width_warning':'independent_E_to_U_rank appliesonlytoanunchangedcanonicalfield. Theopen/puncturedbusendpointhasacoupledsource/helpercode,soitisnotajointownerwidthcertificate.'}

def main():
    path=HERE/'D4-BUS-INPUT.json';bus=json.loads(path.read_text())
    cases={'closed12':scalar(bus),'open12':scalar(bus,open_end=True),'punctured11':scalar(bus,missing=0),
        'reverse_closed12':scalar(bus,reverse=True),'reverse_punctured11':scalar(bus,missing=0,reverse=True),
        'physical_closed12':scalar(bus,physical=True),'physical_open12':scalar(bus,open_end=True,physical=True),
        'physical_punctured11':scalar(bus,missing=0,physical=True),
        'physical_reverse_closed12':scalar(bus,reverse=True,physical=True),'physical_reverse_punctured11':scalar(bus,missing=0,reverse=True,physical=True)}
    for fwd,rev in(('closed12','reverse_closed12'),('punctured11','reverse_punctured11'),('physical_closed12','physical_reverse_closed12'),('physical_punctured11','physical_reverse_punctured11')):
        A=[[F(x)for x in r]for r in cases[fwd]['source_helper_code']];B=[[F(x)for x in r]for r in cases[rev]['source_helper_code']]
        need(mm(A,B)==mm(B,A)==eye(len(A)),'bothorientationsareactualinversecodes')
    comp=compiler(bus)
    # Observabledefectcontrols useactualclaimedmaps andgeometry.
    need(cases['closed12']['source_helper_code']!=[[str(a)for a in r]for r in eye(16)],'omittingcyclicsourcecodeisnotidentity')
    need(comp['routes']['open']['independent_E_to_U_rank']==1,'openhelperendpointcontainsentrance; wrongrank3control')
    out={'status':'PASS_ACTUAL_DIRTY_D4_BUS_TARGET_I_SOURCE_HELPER_CODE_NO_OWNER_CLAIM',
        'source_bus_sha256':hash_file(path),'cases':cases,'native_h7':comp,
        'full112_tail_model':{'present_helpers':32,'missing_helpers':8,
            'present_path_h9':[2,2,2,6],'missing_path_h9':[2,2,6],
            'individual_E_to_FULL_width':6,'extra_rank_per_call':224,
            'old_paired_arity_model_deficit':'D=2(L-1)112-L224=-224; fails atzero beforeprecision/owner.',
            'scope':'Thisisascopedoldindependent-endpointmodel. Movingowner/code-nativeadmission maychangeitandmustbeproved.'},
        'negative_controls':['discardcyclicsourcecode','claimopenendpointwidth3insteadof1'],
        'limits':['ExactdirtytargetIisproved; thejointsource/helpercodeisretainedexplicitly.',
            'The pure physical open bus has four actual carrier channel ranks3,5,5,5, without feature Hadamards. This is not yet chronological owner allocation or a routed global caller.',
            'Noactualroutedglobalcontroller,sourcerestoration,chronologicalowner,precisionortapeinvoiceisadmitted.']}
    (HERE/'D4-BUS-WORD.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']);print(json.dumps({'canonical_cases':{k:{j:v[j]for j in('n','input_columns','code_order','canonical_prefix_l1')}for k,v in cases.items()},
        'native_routes':{k:(v['paid_rank'],v['independent_E_to_U_rank'])for k,v in comp['routes'].items()}},sort_keys=True))

if __name__=='__main__':main()
