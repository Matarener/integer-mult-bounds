#!/usr/bin/env python3
"""Actual paired D4 compensation blocks and the exact residual invoice.

This is a partial complex supplier, not an identity supplier or new kappa.
Substantial OpenAI Codex assistance. Local research only.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import gzip, hashlib, importlib.util, json, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = Path('/Users/ross/git/math/integer-mult-bounds')
OLD = Path('/Users/ross/git/math/.research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier/helper-boundary')
O = (451,454,453,31,55,47,248,440,376)
PIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'

def need(x, msg):
    if not x: raise ValueError(msg)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dot(a,b): return (a&b).bit_count() & 1
def omega(x):
    y=0
    for j,v in enumerate(O):
        if x>>j&1:y^=v
    return y
def span(vs):
    ans={0}
    for x in vs: ans|={v^x for v in ans}
    return ans
def basis(vs):
    piv={}
    for x in vs:
        while x:
            j=x.bit_length()-1
            if j in piv:x^=piv[j]
            else:piv[j]=x;break
    return tuple(piv[j] for j in sorted(piv,reverse=True))
def perp(vs):return basis(x for x in range(512) if all(not dot(x,v) for v in vs))
def rankq(rows):
    a=[list(map(F,r)) for r in rows];r=0
    for j in range(len(a[0]) if a else 0):
        k=next((k for k in range(r,len(a)) if a[k][j]),None)
        if k is None:continue
        a[r],a[k]=a[k],a[r];z=a[r][j];a[r]=[x/z for x in a[r]]
        for k in range(len(a)):
            if k!=r and a[k][j]:
                z=a[k][j];a[k]=[x-z*y for x,y in zip(a[k],a[r])]
        r+=1
    return r
def mm(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def tr(a):return list(map(list,zip(*a)))
def eye(n):return [[F(i==j) for j in range(n)]for i in range(n)]

def load():
    path=REPO/'research/kernel92-frame-composition/vendor/pr531/inputs/data-base/split-centres/CANONICAL-WORD.json.gz'
    need(sha(path)=='addf598581d2a20e13d0c18110607515ad90b06125616a2349e53a47bb5b6c80','native source pin')
    word=json.loads(gzip.decompress(path.read_bytes()));P=word['ports']
    sdpath=REPO/'research/native-source-codes/source_data.py'
    spec=importlib.util.spec_from_file_location('d4_pinned_source',sdpath);sd=importlib.util.module_from_spec(spec);spec.loader.exec_module(sd)
    local=sd.load_local(REPO);w=local['CANONICAL-WORD.json.gz'];prog=local['LOCAL-PROGRAMS.json.gz']['forward']
    need(w['ports']==P,'source ports and independent centre data agree')
    rows=sd.replay(prog,704,prog.index(['phase','centers']))
    R=[[rows[c].get(j,F(0)) for j in range(112)] for c in w['centers']]
    need(mm(R,tr(R))==[[F(56 if i==j else 0)for j in range(8)]for i in range(8)],'actual R moment')
    full=sorted(set(P)|{omega(p)for p in P}|{omega(omega(p))for p in P})
    need(len(full)==120 and all(omega(p)in full for p in full),'full 120 O-closed extension')
    roots={p:tuple(row[j] for row in R) for j,p in enumerate(P)}
    missing={}
    for p in set(full)-set(P):
        support={j for j,q in enumerate(P) if not dot(p,q)}
        choices=[i for i,row in enumerate(R) if support=={j for j,a in enumerate(row) if a}]
        need(len(choices)==1,'missing orthogonal root has a unique actual coordinate support')
        i=choices[0];roots[p]=tuple(F(2 if i==k else 0)for k in range(8));missing[p]=i
    need(len(set(missing.values()))==8,'all missing eight orthogonal coordinate roots')
    for p in full:
        need(sum(x*x for x in roots[p])==4,'root norm')
        for q in full:
            real=sum(x*y for x,y in zip(roots[p],roots[q]))
            need(real in ((4,)if p==q else ((0,)if dot(p,q)else(-2,2))),'complete actual root Gram pattern')
    X=[[roots[p][i]/2 for p in full]for i in range(8)]
    need(mm(X,tr(X))==[[F(15 if i==j else 0)for j in range(8)]for i in range(8)],'full root tight frame')
    return P,full,roots,{'pin':PIN,'native_word_sha256':sha(path),'source_data_sha256':sha(sdpath),'missing_labels_to_coordinate':missing}

def tiling(full, roots):
    index={p:j for j,p in enumerate(full)};n=len(full)
    comp=[sum(1<<j for j,q in enumerate(full)if p!=q and not dot(p,omega(q))and not dot(q,omega(p)))for p in full]
    clusters={}
    for a in range(n):
        left=comp[a]&~((1<<(a+1))-1)
        while left:
            bbit=left&-left;left^=bbit;b=bbit.bit_length()-1
            rest=left&comp[b]
            while rest:
                cbit=rest&-rest;rest^=cbit;c=cbit.bit_length()-1
                p=full[a]^full[b]^full[c]
                d=index.get(p,-1)
                if d<=c or not((comp[a]&comp[b]&comp[c])>>d&1):continue
                S=tuple(full[i]for i in(a,b,c,d));G=(S,tuple(map(omega,S)),tuple(omega(omega(x))for x in S))
                C=frozenset(sum((list(g)for g in G),[]))
                need(len(C)==12,'three disjoint four-root frames')
                if C in clusters:continue
                need(rankq([roots[p]for p in C])==4,'D4 real rank')
                need(all(sum(x*y for x,y in zip(roots[p],roots[q]))==4*int(p==q) for g in G for p in g for q in g),'three actual orthogonal root frames')
                clusters[C]=G
    blocks=list(clusters.items());byport=defaultdict(list)
    masks=[]
    for j,(C,G)in enumerate(blocks):
        mask=sum(1<<index[p]for p in C);masks.append(mask)
        for p in C:byport[index[p]].append(j)
    nodes=0
    @lru_cache(None)
    def solve(rem):
        nonlocal nodes
        nodes+=1
        if not rem:return ()
        best=None;bits=rem
        while bits:
            bit=bits&-bits;bits^=bit;v=bit.bit_length()-1
            choices=[j for j in byport[v]if masks[j]&rem==masks[j]]
            if not choices:return None
            if best is None or len(choices)<len(best):best=choices
        for j in best:
            ans=solve(rem^masks[j])
            if ans is not None:return(j,)+ans
        return None
    result=solve((1<<n)-1);need(result is not None and len(result)==10,'actual ten-D4 exact cover')
    G=[blocks[j][1]for j in result]
    need(set(sum((sum((list(g)for g in b),[])for b in G),[]))==set(full),'literal D4 tiling coverage')
    return G,{'eligible_O_invariant_D4_blocks':len(blocks),'exact_cover_states':solve.cache_info().misses}

def word(groups,roots):
    labels=sum((list(g)for g in groups),[]);at={p:j for j,p in enumerate(labels)}
    frames=[basis(g)for g in groups]
    need(all(len(u)==3 for u in frames),'four roots span rank3')
    radical=span(frames[0])&span(frames[1]);need(len(radical)==4,'common radical dimension2')
    need(all(span(frames[i])&span(frames[j])==radical for i in range(3)for j in range(i)),'all three frame intersections')
    events=[];contacts=[]
    for second in(False,True):
        for i in range(3):
            j=(i+1)%3 if second else(i+2)%3
            U=basis(list(frames[i])+list(frames[(i+2)%3]))if second else frames[i]
            need(len(U)==(4 if second else 3),'D4 contact rank')
            for s in groups[i]:
                need(all(not dot(v,omega(s))for v in U),'source cap inclusion')
            for t in groups[j]:
                need(all(not dot(v,t)for v in U),'target cap inclusion')
            for t in groups[j]:
                for s in groups[i]:
                    c=-sum(x*y for x,y in zip(roots[t],roots[s]))/4
                    need(c in(F(1,2),F(-1,2)),'all sixteen actual half-coefficients')
                    events.append((at[t],at[s],c,U))
            contacts.append({'source_group':i,'target_group':j,'frame':U,'rank':len(U)})
    C=[[F(i==j)-sum(x*y for x,y in zip(roots[t],roots[s]))/4 for j,s in enumerate(labels)]for i,t in enumerate(labels)]
    need(sum(c!=0 for row in C for c in row)==96,'complete D4 compensation support')
    K=[[F(i==j)-C[i][j]for j in range(12)]for i in range(12)]
    need(mm(K,K)==[[3*x for x in row]for row in K],'D4 Gram polynomial K^2=3K')
    need(mm(C,[[ (F(i==j)+C[i][j])/2 for j in range(12)]for i in range(12)])==eye(12),'dyadic inverse of D4 compensation')
    rows=eye(24)
    for t,s,c,U in events:rows[12+t]=[x+c*y for x,y in zip(rows[12+t],rows[s])]
    want=eye(24)
    for i in range(12):
        for j in range(12):want[12+i][j]=C[i][j]
    need(rows==want,'all arbitrary data and target columns')
    dual=eye(24)
    for t,s,c,U in events:dual[s]=[x-c*y for x,y in zip(dual[s],dual[12+t])]
    wantdual=eye(24)
    for i in range(12):
        for j in range(12):wantdual[i][12+j]=-C[j][i]
    need(dual==wantdual,'same-order inverse-transpose all columns')
    mutated=[r[:]for r in rows];t,s,c,U=events[0];mutated[12+t][s]-=c
    need(mutated!=want,'omitted actual compensation coefficient control')
    return {'labels':labels,'groups':groups,'frames':frames,'radical':basis(radical),'contact_word':contacts,
            'coefficient_matrix':[[str(x)for x in r]for r in C], 'scalar_adds':96,
            'real_component_primitives':960,'all_input_columns':24,'ordinary_helpers':0,'private_fields':0,
            'source_and_target_paths':[2,1,4],'rank_histogram':{1:24,2:24,4:24},'native_rank_mass':168,
            'canonical_prefix_l1':5,'canonical_denominator_depth':1,
            'physical_prefix_gaussian_l1_upper':80,'physical_denominator_depth_upper':8,
            'all_size_prefix_bounds':'For chunk dimension k: Gaussian l1 <=5*2^(4k), denominator depth<=7k+1, excluding scalar/address implementations of the finite monomial adapters.',
            'scope':'Exact direct C_D4 shear and dual with arbitrary sources/targets. Sources restored canonically in forward, targets restored canonically in dual. This is C_D4=I-K_D4, not identity.'}

def compile_word(w):
    cpath=REPO/'research/kernel92-frame-composition/vendor/pr531/vendor/clifford/clifford_exact.py'
    need(sha(cpath)=='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','actual compiler pin')
    spec=importlib.util.spec_from_file_location('d4_actual_clifford',cpath);ce=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ce;spec.loader.exec_module(ce)
    spec=importlib.util.spec_from_file_location('d4_old_geometry',OLD/'order3_geometry.py');geo=importlib.util.module_from_spec(spec)
    sys.path.insert(0,str(OLD));spec.loader.exec_module(geo);sys.path.pop(0)
    def chosen(axes):
        op=ce.ident(9)
        for p in axes:op=op.then(ce.cgate(9,p,1 if p.bit_count()%4==1 else-1))
        return op
    records=[]
    for is_target in(False,True):
        for p in w['labels']:
            q=omega(p);a=geo.orthonormal([1<<i for i in range(9)],(p,q));R=a[2:]
            entrance=q if is_target else p;cap=basis((q,)+R)if is_target else basis((p,)+R)
            finalop=chosen((q,)+R)if is_target else chosen((p,)+R)
            active=[]
            for e in w['contact_word']:
                group=w['groups'][e['target_group' if is_target else'source_group']]
                if p in group:active.append(tuple(e['frame']))
            need(len(active)==2,'each data row visits two contacts')
            ops=[chosen((entrance,)),ce.canonical_frame(9,active[0]),ce.canonical_frame(9,active[1]),finalop]
            frames=[(entrance,),*active,cap];ranks=[]
            for j in range(3):
                need(span(frames[j])<=span(frames[j+1]),'literal nested frame path')
                op=ops[j].adjoint().then(ops[j+1]);rec,literal=ce.lower_child(op)
                need(rec['rank']==(2,1,4)[j],'actual Fourier rank at each D4 contact jump')
                need(literal.tab==op.tab and literal.zero_state()==op.zero_state(),'literal exact phase and tableau')
                ranks.append(rec['rank'])
            residual=ops[0].adjoint().then(ops[-1]);rr,ll=ce.lower_child(residual)
            need(rr['rank']==7 and ll.tab==residual.tab and ll.zero_state()==residual.zero_state(),'chosen rank7 endpoints')
            records.append({'target':is_target,'port_label':p,'frames':frames,'ranks':ranks})
    # The partial four-feature packets have a genuine geodesic rank2+rank1 gather.
    A,B,C=w['frames'];V=basis(list(B)+list(C));pack=[]
    for U,Vv in((A,B),(B,V)):
        op=ce.canonical_frame(9,U).adjoint().then(ce.canonical_frame(9,Vv));r,lit=ce.lower_child(op)
        need(lit.tab==op.tab and lit.zero_state()==op.zero_state(),'private partial packet exact phase')
        pack.append(r['rank'])
    need(pack==[2,1],'partial feature packet geodesic')
    return {'compiler_sha256':sha(cpath),'data_rows':len(records),'exact_transition_checks':3*len(records),
            'endpoint_checks':len(records),'records':records,'partial_packet_gather_ranks':pack}

def residual(tiles,full,roots,retained):
    # X=UF in actual coordinates, with U composed of ten orthogonal4-frames.
    X=[[roots[p][i]/2 for p in full]for i in range(8)];at={p:j for j,p in enumerate(full)}
    U=[[F(0)for _ in range(40)]for _ in range(8)];features=[[F(0)for _ in full]for _ in range(40)]
    for b,G in enumerate(tiles):
        frame=G[0]
        for k,p in enumerate(frame):
            for i in range(8):U[i][4*b+k]=roots[p][i]/2
            for t in sum((list(g)for g in G),[]):features[4*b+k][at[t]]=sum(roots[p][i]*roots[t][i]for i in range(8))/4
    need(mm(U,features)==X,'actual all-column residual factor X=UF')
    need(mm(features,tr(features))==[[F(3 if i==j else 0)for j in range(40)]for i in range(40)],'all forty local feature moments')
    need(mm(U,tr(U))==[[F(5 if i==j else 0)for j in range(8)]for i in range(8)],'ten D4 embeddings form a tight frame')
    UtU=mm(tr(U),U);M=[[F(i==j)-UtU[i][j]for j in range(40)]for i in range(40)]
    Mi=[[F(i==j)-UtU[i][j]/4 for j in range(40)]for i in range(40)]
    need(mm(M,Mi)==eye(40),'dyadic middle inverse')
    Delta=mm(tr(features),mm(M,features));need(rankq(Delta)==40,'exact residual real rank40')
    support=sum(a!=0 for row in Delta for a in row)
    need(support==5760,'all uncovered cross-D4 coefficients')
    keep=[at[p]for p in retained]
    short=[[Delta[i][j]for j in keep]for i in keep]
    need(rankq(short)==40,'retained112 residual real rank40')
    need(sum(a!=0 for row in short for a in row)==4992,'retained112 exact uncovered set')
    missing=set(full)-set(retained)
    need(sum(p in missing for G in tiles for p in G[0])==8,'all removed roots placed in first coordinate frames')
    # A fully extended packet costs three actual gather ranks plus five to FULL.
    return {'identity':'K_block-K_full=F^T (I_40-U^T U) F; X=UF',
            'F_Ft':'3 I_40','U_Ut':'5 I_8','middle_eigenvalues':{'1':32,'-4':8},
            'middle_inverse':'I_40-U^T U/4','exact_residual_rank':40,'uncovered_ordered_pairs':support,
            'retained112_residual_rank':40,'retained112_uncovered_ordered_pairs':4992,
            'retained112_direct_compensation_entries':832,
            'uncovered_set':'All ordered root pairs in different listed D4 blocks with binary dot zero; coefficient -<R_t,R_s>/4 in C_full, opposite sign in K_block-K_full.',
            'partial_packets':{'fields':40,'per_packet_native_gather':[2,1],'gather_rank_charge':120,
                'terminal_frame_rank':4,'additional_FULL_extension_per_packet':5,'full_extension_total_charge':320,
                'scope':'Owned clean private packet output only. No scatter, clear, arbitrary ordinary dirt restoration, or owner closure is inherited.'},
            'retained112_partial_packets':{'fields':40,'native_rank_histogram':{1:40,2:32},
                'gather_rank_charge':104,'FULL_extension_total_charge':304,
                'entrances':{'U0_rank3':32,'U1_rank3':8},'terminal':'V=U1+U2 rank4',
                'individual_residual_widths':{'3':32,'1':8},
                'reason':'Each missing root is a coordinate in first frameA, so its feature has no x_A term and can start atU1, skippingrank2. This is an owned clean partial packet output only.'},
            'factor_rows':[[str(a)for a in r]for r in features],
            'embedding_U':[[str(a)for a in r]for r in U],
            'middle_M':[[str(a)for a in r]for r in M]}

def main():
    P,full,roots,sources=load();tiles,census=tiling(full,roots)
    missing=set(full)-set(P)
    oriented=[]
    for G in tiles:
        k=max(range(3),key=lambda j:sum(p in missing for p in G[j]))
        need(all(p not in missing for j,g in enumerate(G)if j!=k for p in g),'missing orthogonal roots occupy one D4 frame')
        oriented.append(tuple(G[(k+j)%3]for j in range(3)))
    tiles=oriented;words=[word(G,roots)for G in tiles]
    compiled=compile_word(words[0]);rem=residual(tiles,full,roots,P)
    out={'status':'PASS_TEN_D4_PAIRED_COMPENSATION_BLOCKS_RESIDUAL40_NO_SUPPLIER',
         'sources':sources,'tiling_census':census,'full_root_labels':full,'retained112_labels':P,
         'D4_tiling':tiles,'first_block':words[0],'all_blocks':words,'actual_compiler_first_block':compiled,
         'residual':rem,'negative_controls':['omit one actual half-coefficient changes full24-column map',
             'retain rank3 frame at the second contact misses one required source/target direction'],
         'limits':['Direct blocks implement C_block=diag(I-K_D4), not I and not full C=I-K_full.',
             'The120-root extension is a geometry/factor witness. Restricting to retained112 gives832direct coefficients and4992uncovered coefficients with40featurechannels; no extra eight data fields or120-port decoder is needed for that restriction.',
             'Exact scalar and compiler identities are finite; a general tensor-lift and full machine invoice remain separate.',
             'No complete residual gather/scatter/ordinary-dirt restoration word or favorable joint moment is supplied.']}
    # The second declared mutant changes an actual frame and fails incidence.
    e=words[0]['contact_word'][3];oldframe=words[0]['frames'][e['source_group']]
    need(any(q not in span(oldframe)for q in (omega(t)for t in words[0]['groups'][e['target_group']])),'missing second-contact frame direction control')
    (HERE/'D4-GEOMETRY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']);print(json.dumps({'blocks':len(tiles),'eligible':census,'first':tiles[0],
        'residual_rank':rem['exact_residual_rank'],'uncovered':rem['uncovered_ordered_pairs'],
        'partial_gather_full120':120,'extended_FULL_full120':320,
        'partial_gather_retained112':104,'extended_FULL_retained112':304},sort_keys=True))

if __name__=='__main__':main()
