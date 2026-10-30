"""Emit an independent G20 helper split and check its physical interface.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Retain Dugongue, ai-nanachi and the predecessor notices in prior/.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
import gzip,importlib.util,json,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R))
def need(ok,message):
    if not ok:raise ValueError(message)
def bitids(row):
    while row:
        bit=row & -row;yield bit.bit_length()-1;row^=bit
def read(path):
    raw=path.read_bytes();return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
def put(name,value):
    raw=(json.dumps(value,indent=2)+'\n').encode();path=R/name
    path.write_bytes(gzip.compress(raw,mtime=0) if path.suffix=='.gz' else raw)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
for item in read(R/'INPUTS.json'):
    need(sha256((R/item['local']).read_bytes()).hexdigest()==item['sha256'],'Frozen input '+item['local'])
PRIOR=load('split_prior_integration',R/'prior/integration.py')
SOURCE=PRIOR.SOURCE;source=PRIOR.source;S=PRIOR.S;RETIRED=PRIOR.RETIRED
sys.path.insert(0,str(R))

def check_cut(word,h):
    n=len(word['start']);es=word['records'];rows=[1<<i for i in range(n)];state=word['start'][:]
    for e in es[:h['cut']+1]:
        op,d=e[:2]
        if op=='ADD':rows[d]^=rows[e[2]]
        elif op=='ERASE':rows[d]=0
        if op in ['Q','ZERO_Q','ERASE','INIT']:state[d]=e[3] if op in ['Q','ZERO_Q'] else e[2]
    def bitmap(xs):return sum(1<<i for i in xs)
    a,b,c,d=[bitmap(h[k])for k in ['a','b','c','d']]
    value=0
    for i in h['a']:value^=rows[i]
    need(value==c,'Exact prefix functional')
    col=[int(i in h['b']) for i in range(n)]
    for e in es[h['cut']+1:]:
        if e[0]=='ADD':col[e[1]]^=col[e[2]]
        elif e[0]=='ERASE':col[e[1]]=0
    need(bitmap([i for i,v in enumerate(col)if v])==d,'Exact suffix direction')
    need((a&b).bit_count()%2==(c&d).bit_count()%2==1,'Two unit pairings')
    p=h['pivot'];f=h['frame'];u=word['start'][p];v=word['final'][p]
    group={i for i in range(222,n)if i not in word['owned'] and (word['start'][i],word['final'][i])==(u,v)}
    need(set(h['c']+h['d'])<=group and p in group,'One independent helper boundary group')
    need(all(state[i]==f for i in set(h['a']+h['b']+[p])),'Actual cut coframe')
    _,frames,_=source();g=SOURCE.Geometry(frames)
    need(h['ranks']==[g.dims[u]-g.dims[f],g.dims[f]-g.dims[v]],'Strict productive ranks')
    for s,t,k in [(u,f,h['ranks'][0]),(f,v,h['ranks'][1])]:g.nested(s,t,k)
    return dict(cut=h['cut'],frame=f,pivot=p,input_support=h['c'],output_support=h['d'],ranks=h['ranks'])

def matcher(frames):
    old=read(R/'prior/MATCHER.json');frame=frames['508'];w=[list(row)for row in zip(*[[F(v)for v in row]for row in frame['B']+frame['A']])]
    aug=[row[:]+[F(i==j)for j in range(8)]for i,row in enumerate(w)]
    for j in range(8):
        k=next(i for i in range(j,8)if aug[i][j]);aug[j],aug[k]=aug[k],aug[j];c=aug[j][j];aug[j]=[v/c for v in aug[j]]
        for i in range(8):
            if i!=j:
                c=aug[i][j];aug[i]=[x-c*y for x,y in zip(aug[i],aug[j])]
    wi=[row[8:]for row in aug]
    def mm(a,b):return [[sum(x*y for x,y in zip(row,col))for col in zip(*b)]for row in a]
    eye=[[F(i==j)for j in range(8)]for i in range(8)]
    need(mm(w,wi)==mm(wi,w)==eye,'Both target matcher directions')
    need(all(sum(F(x)*F(y)for x,y in zip(a,b))==0 for a in frame['A']for b in frame['B']),'Actual orthogonal target split')
    need(all(old['common_denominator']%v.denominator==0 for matrix in [w,wi]for row in matrix for v in row),'Actual target denominator divides the charged bound')
    coeff=sum(bool(v)for matrix in [w,wi]for row in matrix for v in row)
    old.update(new_target_frame=508,new_target_forward=[[str(v)for v in row]for row in w],new_target_inverse=[[str(v)for v in row]for row in wi],new_target_coefficient_terms=36*2*coeff,new_target_count=36)
    old['max_numerator_bits']=max(old['max_numerator_bits'],max(abs(v.numerator).bit_length()for matrix in [w,wi]for row in matrix for v in row))
    put('MATCHER.json',old);return old

def run():
    import construct as C
    import native
    old=read(R/'prior/WORD.json.gz');w=old;receipts=[]
    candidates=C.find(old);need(len(candidates)==6,'Full source cut domain has six basis witnesses')
    for h in read(R/'SPLITS.json'):
        receipts.append(check_cut(w,h));w=C.split(w,h)
    need(len(receipts)==1 and receipts[0]['ranks']==[4,4],'One maximal balanced split')
    need(not C.find(w),'No further split in the emitted common-frame domain')
    need(C.replay(w)==C.replay(old),'Every paid rank retained')
    base,frames,_=source();physical_base={'final':w['start'],'start':w['final']}
    stats=native.replay(physical_base,frames,w['records'],set(w['owned']))
    mods=[native.replay(physical_base,frames,w['records'],set(w['owned']),m)['native_modulus']for m in [101,10201]]
    need(stats['retained_originals']==637 and stats['owned_allocated']==48,'One new independent input and no new owned field')
    rejected=[]
    for label,key in [('prefix_contamination','a'),('suffix_contamination','b')]:
        h=read(R/'SPLITS.json')[0];h[key]=h[key]+[0]
        try:check_cut(old,h)
        except ValueError:rejected.append(label)
        else:raise ValueError('Invalid cut accepted')
    for label,index in [('missing_input_basis',0),('missing_output_basis',len(w['records'])-1)]:
        bad=dict(w,records=w['records'][:index]+w['records'][index+1:])
        try:C.replay(bad)
        except ValueError:rejected.append(label)
        else:raise ValueError('Missing basis accepted')
    matcher(frames);put('WORD.json.gz',w)
    out=dict(status='PASS_G20_SPLIT_ALL685_COLUMNS',stats=stats,native_moduli=mods,cuts=receipts,source_candidates=candidates,remaining_candidates=0,negative_controls=rejected)
    put('LOCAL-RESULT.json',out);return out
if __name__=='__main__':print(json.dumps(run(),indent=2))
