"""Independent composed659-column/frame/native-COPY audit. Apache-2.0."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import json,gzip,hashlib,importlib.util,time,sys
H=Path(sys.argv[1]).resolve();PKG=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 with (H/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')
def canon(w):return json.dumps(w,sort_keys=True,separators=(',',':')).encode()
def matmul(A,B):return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]
def ident(n):return [[F(i==j) for j in range(n)] for i in range(n)]
def inverse(A):
    n=len(A);a=[[F(x) for x in row]+e for row,e in zip(A,ident(n))]
    for j in range(n):
        k=next(i for i in range(j,n) if a[i][j]);a[j],a[k]=a[k],a[j];v=a[j][j];a[j]=[x/v for x in a[j]]
        for i in range(n):
            if i!=j:
                v=a[i][j];a[i]=[x-v*y for x,y in zip(a[i],a[j])]
    return [row[n:] for row in a]
def projector(rows,basis):
    b=[list(row) for _,row in basis(rows)]
    if not b:return [[F(0)]*8 for _ in range(8)]
    bt=list(map(list,zip(*b)));return matmul(matmul(bt,inverse(matmul(b,bt))),b)
def subtract(A,B):return [[x-y for x,y in zip(r,s)] for r,s in zip(A,B)]
def native(Q):
    C=subtract(ident(len(Q)),Q)
    return [r+s for r,s in zip(C,Q)]+[r+s for r,s in zip(Q,C)]
def dropcol(x,k):return (x&((1<<k)-1))|((x>>(k+1))<<k)

def main():
    cpu=time.process_time();wordpath=H/'WORD.json.gz';raw=gzip.decompress(wordpath.read_bytes());w=json.loads(raw)
    old=json.loads(gzip.decompress((PKG/'data/r0028/FINAL-R438-WORD.json.gz').read_bytes()))
    selected=json.loads(gzip.decompress((PKG/'data/SELECTED589.json.gz').read_bytes()))
    assert w['R']==437 and old['R']==438
    assert hashlib.sha256(canon(w)).hexdigest()=='da77deaf11368d016622348227657b98404b6afbc7e4f3d6fe9a246baae0dcce'
    spec=importlib.util.spec_from_file_location('independent438',PKG/'code/ancestor_word_engine.py')
    own=importlib.util.module_from_spec(spec);spec.loader.exec_module(own)
    dims,frames=own.geometry(w,selected)
    removed=469;source=77;receiver=444;birth=229;read=1999;newframe=186
    remap=lambda r:r-int(r>removed)
    def remapg(gs):return [[f,remap(d),[remap(s) for s in ss]] for f,d,ss in gs]
    uses=[(sec,i) for sec in ['A','B'] for i,(f,d,ss) in enumerate(old[sec]) if removed in [d]+ss]
    assert uses==[('A',birth),('A',read)] and old['A'][birth]==[79,removed,[source]] and old['A'][read]==[79,receiver,[removed]]
    changed=[g if i!=read else [newframe,receiver,[source]] for i,g in enumerate(old['A']) if i!=birth]
    assert w['A']==remapg(changed) and w['B']==remapg(old['B'])
    assert w['ret']==[remap(r) for r in old['ret']] and w['scatter']==old['scatter']
    assert w['start']==[f for i,f in enumerate(old['start']) if i!=removed] and w['final']==[f for i,f in enumerate(old['final']) if i!=removed]
    # Fresh exact dirty compensation and literal full cleanup, not copied receipt.
    n=659;v=111;rawrows,_=own.raw(w);expectedD=[]
    for t in range(v):
        assert rawrows[v+t]&((1<<222)-1)==(1<<t)^(1<<(v+t))
        ss=[r for r in range(222,n) if rawrows[v+t]>>r&1]
        if ss:expectedD.append([0,v+t,ss])
    assert w['D']==expectedD
    assert w['C']==[[1,d,ss] for f,d,ss in reversed(w['A']+w['B']) if not v<=d<2*v]
    # H1-H5 independently on original grouped gates.
    is_y=lambda r:v<=r<2*v
    hypotheses={
      'H1_no_target_feeds_z':all(not is_y(s) for sec in ['D','A','B','C'] for f,d,ss in w[sec] if not is_y(d) for s in ss),
      'H2_D0_helpers_to_targets':all(f==0 and is_y(d) and all(s>=222 for s in ss) for f,d,ss in w['D']),
      'H3_A_z_only_B_split':all(not is_y(d) for f,d,ss in w['A']) and all(is_y(d) or all(not is_y(s) for s in ss) for f,d,ss in w['B']),
      'H4_literal_C_full':all(f==1 and not is_y(d) for f,d,ss in w['C']),
      'H5_Y_identity':all(rawrows[v+t]&(((1<<v)-1)<<v)==1<<(v+t) for t in range(v))}
    assert all(hypotheses.values())
    rows,cap,paths,history,info=own.ledger(w,dims,frames)
    orows,ocap,opaths,ohistory,oinfo=own.ledger(old,dims,frames)
    expected=[(1<<r)^((1<<(r-v)) if is_y(r) else 0) for r in range(n)]
    assert rows==own.whole(w)==expected
    literal_ops=own.column_engine(w)
    want={1:1320,2:1344,3:77,4:43,5:102,6:11,7:18};assert info['profile']==want and info['mass']==5113
    delta=Counter(info['profile']);delta.subtract(oinfo['profile']);assert {r:c for r,c in delta.items() if c}=={1:-2,2:2,3:-1,7:-1}
    assert len(info['COPY'])==9 and [x['SOURCE_row_hex'] for x in info['COPY']]==[x['SOURCE_row_hex'] for x in oinfo['COPY']]
    assert [x['frame'] for x in info['COPY']]==[x['frame'] for x in oinfo['COPY']]
    assert history==ohistory  # SOURCE clean write histories identical.
    changedpaths=[]
    for r in range(660):
        if r==removed:continue
        if paths[remap(r)]!=opaths[r]:changedpaths.append(r)
    assert changedpaths==[receiver]
    assert paths[receiver]==[0,186,509,392,513,1] and opaths[receiver]==[0,79,509,392,513,1]
    assert opaths[removed]==[0,79,1] and paths[source]==opaths[source]
    # Full SOURCE write rows after deleting the removed DIRTY input column.
    def source_writes(word):
        z=[1<<r for r in range(222+word['R'])];out=[]
        for sec in ['A','B','C']:
            for f,d,ss in word[sec]:
                for s in ss:z[d]^=z[s]
                if d<111:out.append((sec,f,d,tuple(ss),z[d]))
        return out
    nh=source_writes(w);oh=source_writes(old)
    assert len(nh)==len(oh)==966
    for a,b in zip(nh,oh):assert a[:3]==b[:3] and a[3]==tuple(remap(s) for s in b[3]) and a[4]==dropcol(b[4],removed)
    # Literal availability of SOURCE77 at the changed read, including full row.
    z=[1<<r for r in range(660)];cur=old['start'][:]
    for f,d,ss in old['A'][:read]:
        for r in [d]+ss:cur[r]=f
        for s in ss:z[d]^=z[s]
    assert cur[source]==186 and cur[receiver]==0 and z[source]==1<<source and z[removed]==(1<<source)^(1<<removed)
    # Exact Q native subset proof for the ACTUAL changed frames. No mod-p-only
    # coincidence; general gauge transport then handles every DATA/DIRTY input.
    projectors={f:projector([w['lines'][r] for r in w['frames'][f]],own.basis) for f in [0,79,186,509]}
    for a,b in [(0,79),(79,186),(186,509)]:
        A=projectors[a];B=projectors[b]
        assert matmul(A,B)==matmul(B,A)==A
        D=subtract(B,A);assert matmul(D,D)==D
        assert matmul(native(D),native(A))==native(B)
    P0=projectors[0];P79=projectors[79];P186=projectors[186];P509=projectors[509]
    assert matmul(native(subtract(P509,P186)),native(P186))==native(P509)
    assert matmul(native(subtract(P509,P79)),native(P79))==native(P509)
    # Meaningful distinction: forcing the late direct READ at old line79 is a
    # SOURCE descent and must fail even if the scalar addition is unchanged.
    bad=json.loads(json.dumps(w));bad['A'][read-1][0]=79
    try:own.ledger(bad,dims,frames)
    except AssertionError:wrong_frame_reject=True
    else:raise AssertionError('SOURCE descending frame mutant passed')
    missingC=dict(w);missingC['C']=w['C'][:-1];assert own.whole(missingC)!=expected
    missingD=dict(w);missingD['D']=w['D'][1:];assert own.whole(missingD)!=expected
    result={'status':'PASS_INDEPENDENT_R437_659_RAW_TYPED_SOURCE_COPY_AND_EXACT_NATIVE_GAUGE_GLOBAL_OPEN',
      'word_gzip_sha256':sha(wordpath),'canonical_sha256':hashlib.sha256(raw).hexdigest(),
      'SOURCE':111,'Y':111,'DIRTY':437,'RAW_columns':659,'frames':636,'frame_closure_checks':636*111,
      'independent_H1_H5':hypotheses,'literal_column_ops':literal_ops,'ledger':info,'delta_from_R438':{r:c for r,c in delta.items() if c},
      'derivation':{'credited_old_helper470_in_selected589':'public1043 canonicalmerge20ecf... sourcebytes pin; originalPRheadcomparison UNKNOWN',
        'removed_in_R438_numbering':469,'SOURCE':77,'receiver':444,'birth_A':229,'old_read_A':1999,'new_read_A':1998,'new_frame':186,
        'full_SOURCE_row_before_late_read':'exact RAW input77','changed_surviving_paths_only':[444],
        'source_query_paths_unchanged':True,'SOURCE_READ_delta':'Delete early LOAD into removed helper; add late direct SOURCE77 READ at already-current frame186',
        'all966_SOURCE_write_full_rows_equal_after_removed_column':True,'nine_COPY_source_rows_and_frames_same':True},
      'native':'Exact rational D_(B-A)D_A=D_B for actual nested frames0,79,186,509. General common-frame gauge lemma plus independent J=I/D0/C gives unchanged endpoint interface for every remaining arbitrary RAW VALUE function and ADDRESS, under retained realization contract.',
      'COPY_accounting':'One paid rank7 transform per capture plus retained linear fullstream CLEAR; no mandatory second uncompute QUERY or new COPY window permission.',
      'negative_controls':['missing D0','missing C','late SOURCE READ at descending frame79'],
      'not_verified':['actualR437 globalmatching/owners/cover/INDEX/ROW/price','new physical generic SOURCE realization beyond unchanged inherited conditional scope','supplier/publication admission'],
      'old_R438_package_unchanged':True,'CPU_seconds':time.process_time()-cpu}

    save('RESULT.json',result)
    print(json.dumps({'status':result['status'],'RAW':659,'mass':5113}))
if __name__=='__main__':main()
