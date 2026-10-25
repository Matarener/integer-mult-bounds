"""Read-only exact physical-boundary comparison, standard library only.
Chris R / Clear1nsight with substantial OpenAI Codex assistance, Apache-2.0.
The independent sparse evaluator is retained and credited PR3987 code.
"""
import argparse,copy,gzip,hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P));sys.path.insert(0,str(P/'vendor'))
import circuit as c
import exact_phase as e
import scratch_schedule
need=c.need

def read(path):return json.loads(path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def authenticate():
    for row in read(P/'SOURCES.json')['external_public_inputs']:
        path=P/row['local_path'];need(not path.is_symlink(),'source symlink')
        raw=path.read_bytes();need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source bytes '+row['local_path'])
        if 'git_blob' in row:need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source Git blob')

def bind(b):
    need(b['warp_index_zero_based']==4 and b['register']==333,'named cut')
    need(b['warp']['offset']==458 and b['warp']['phase']==3,'actual affine/global phase')
    need(b['child']['rank']==1,'successor child rank');providers={}
    for tag in ['base','extra']:
        w=json.loads(gzip.decompress((P/f'frozen/WORD-{tag}.json.gz').read_bytes()))
        need(w['warps'][4]==[1081,333,b['G_columns'],b['entrance'],b['exit']],'literal native event')
        for i,dest,coef in [(1081,656,-1),(1082,657,-1),(1083,658,1)]:need(w['B'][i]==['add',dest,333,coef,1,b['exit']],'literal consumer')
        need(w['B'][1097]==['add',333,79,1,1,b['next_frame']],'next scalar boundary')
        for g in w['B'][1084:1097]:need(333 not in(g[1:3]if g[0]=='add'else g[1:2]),'intervening lender contact')
        need(not any(r==333 and 1081<p<=1097 for p,r,*_ in w['warps']),'intervening native contact')
        providers[tag]=dict(word_sha256=sha(P/f'frozen/WORD-{tag}.json.gz'),unchanged_local_profile=w['report']['local_profile'],unchanged_width_inventory=w['report']['width_inventory'])
    source=next(x for x in read(P/'frozen/RECIPES.json')['items'] if x['kind']=='warp' and x['sign']==1 and x['G_columns']==b['G_columns'] and x['entrance']==b['entrance'] and x['terminal']==b['exit'])
    need(source['recipe']==dict(rank=0,left=b['warp'],right=None),'retained exact source recipe')
    return providers

def phase_tag(cols):
    p,q=e.kernel(tuple(cols));tag=sum((((q[1<<j]-p[1<<j].bit_count()+1)%4)//2)<<j for j in range(9))
    need(all(q[x]==(p[x].bit_count()-x.bit_count()+2*((x&tag).bit_count()%2))%4 for x in range(512)),'source normalization identity')
    return tag

def compensated_frame(v,U,omit_global=False,omit_compensation=False):
    B=e.complete(U);t=phase_tag(B);p,_=e.kernel(tuple(B));J=(p,tuple((p[x].bit_count()-x.bit_count())%4 for x in range(512)))
    v=e.mono(v,J,True);den=0;flips=0
    for j in range(len(U)):
        flip=bool(t>>j&1)and not omit_compensation;v,d=e.coordinate(v,[j],flip);den+=d
        if flip:
            flips+=1
            if not omit_global:v={x:(-s,r)for x,(r,s)in v.items()}
    return e.mono(v,J),den,dict(tag=t,flipped_coordinate_axes=[j for j in range(len(U))if t>>j&1],global_i_power=flips%4)

def frames(b):
    result={}
    for label in ['entrance','exit','next_frame']:
        for x in range(512):
            a,da=e.frame({x:(1,0)},b[label]);z,dz,info=compensated_frame({x:(1,0)},b[label]);need(e.equal(a,da,z,dz),'actual compensated frame')
        result[label]=info
    return result

def exact_interfaces(b):
    warp=dict(kind='warp',entrance=b['entrance'],terminal=b['exit'],G_columns=b['G_columns'],sign=1,recipe=dict(rank=0,left=b['warp'],right=None))
    climb=dict(kind='residual',entrance=b['exit'],terminal=b['next_frame'],recipe=b['child'])
    return dict(warp=e.check_item(warp),next_climb=e.check_item(climb))

def compare(M,R,L):
    digest=hashlib.sha256();reference_bill=fused_bill=strong_bill=None
    for register in range(4):
        for column in range(512):
            data=[[(0,0)]*512 for _ in range(4)];data[register][column]=(1,0)
            a,da,ab=c.execute(data,M,R,L);b,db,bb=c.execute(data,M,R,L,True)
            z,dz,zb=c.execute(data,M,R,L,joint=True)
            need(a==b==z and da==db==dz,'complete dirty linear map')
            need(strong_bill is None or zb==strong_bill,'data-independent stronger baseline bill');strong_bill=zb
            need(reference_bill is None or ab==reference_bill,'data-independent reference bill');need(fused_bill is None or bb==fused_bill,'data-independent fused bill')
            reference_bill,fused_bill=ab,bb;digest.update(json.dumps([register,column,a],separators=(',',':')).encode())
    dirty=[[(37*x+11*r-7000,19*x-23*r+91)for x in range(512)]for r in range(4)]
    for fused in [False,True]:
        out,_,_=c.execute(dirty,M,R,L,fused);back,den,_=c.execute(out,M,R,L,fused,True)
        need(den==2 and all(z==[(a*4,b*4)for a,b in src]for z,src in zip(back,dirty)),'arbitrary dirty inverse return')
    return dict(basis_columns=2048,output_complex_coordinates=2048,operator_sha256=digest.hexdigest(),reference=reference_bill,fused=fused_bill,delta={k:fused_bill[k]-reference_bill[k]for k in reference_bill},dirty_inverse_roundtrips=2,stronger_materialized_baseline=strong_bill,delta_vs_stronger={k:fused_bill[k]-strong_bill[k]for k in strong_bill})

def controls(b,M,R,L):
    results=[];data=[[(0,0)]*512 for _ in range(4)];data[0][0]=(1,0);baseline=c.execute(data,M,R,L)[0]
    def bad(name,wrongM=None,wrongR=None,wrongL=None):
        got=c.execute(data,wrongM or M,wrongR or R,wrongL or L,True)[0];need(got!=baseline,'control accepted: '+name);results.append(name)
    mp,mq=M
    bad('omit actual affine translation',(tuple(y^458 for y in mp),mq));bad('omit all phase tags',(mp,(0,)*512));bad('omit global i cubed',(mp,tuple((q-3)%4 for q in mq)))
    bad('replace warp by adjoint',c.inverse(M));bad('reverse right-monomial composition',wrongR=c.compose(c.compose(M,R),c.inverse(M)))
    for name,kwargs in [('drop actual central compensation',dict(omit_compensation=True)),('drop actual compensated global i',dict(omit_global=True))]:
        found=False
        for label in ['entrance','exit','next_frame']:
            for x in range(512):
                good,d=e.frame({x:(1,0)},b[label]);wrong,dd,_=compensated_frame({x:(1,0)},b[label],**kwargs)
                if not e.equal(good,d,wrong,dd):found=True;break
            if found:break
        need(found,'missing actual frame rejection witness');results.append(name)
    z=copy.deepcopy(b);z['warp']['offset']=0
    try:bind(z)
    except ValueError:results.append('changed source-bound affine recipe')
    else:raise ValueError('source control accepted')
    return results

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record',action='store_true');args=parser.parse_args()
    authenticate();b=read(P/'BOUNDARY.json');providers=bind(b);M,R,L=e.decoded(b['warp']),e.decoded(b['child']['right']),e.decoded(b['child']['left'])
    interfaces=exact_interfaces(b);compensation=frames(b);physical=compare(M,R,L)
    need(physical['delta']['caller_real_reads']==-1024 and physical['delta']['caller_real_writes']==-1024,'actual traffic saving');need(physical['delta']['real_negations']==-512,'phase operations fully charged')
    need(all(physical['delta'][k]==0 for k in ['real_additions','exact_halves','private_real_words','private_word_clears','routing_entry_reads']),'unchanged physical charges')
    need(physical['delta_vs_stronger']['caller_real_reads']==0 and physical['delta_vs_stronger']['caller_real_writes']==-1024 and physical['delta_vs_stronger']['real_negations']==0,'strong comparator credit')
    result=dict(status='PASS_FINITE_PAID_NATIVE_FUSION',private_storage_schedule=scratch_schedule.check(),providers=providers,interfaces=interfaces,compensated_actual_frames=compensation,physical=physical,metadata=c.metadata(M,R,L),controls=controls(b,M,R,L),recursive_child_delta=0,owner_width_delta=0,all_size_supplier_admitted=False)
    if args.record:(P/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:need(result==read(P/'RESULT.json'),'result receipt mismatch')
    print(json.dumps(dict(status=result['status'],columns=physical['basis_columns'],caller_real_writes_saved_vs_stronger=1024,caller_real_reads_saved_vs_stronger=0,real_negations_saved_vs_stronger=0,recursive_child_delta=0,controls=len(result['controls']),scope='actual f=1 four-array interface; no native tariff or supplier admission'),sort_keys=True))
if __name__=='__main__':main()
