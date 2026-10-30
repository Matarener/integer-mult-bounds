"""Literal centre-free native unit serialization with concrete global axis embedding.
No pure-shear or whole-p19 compiler claim. Apache-2.0, Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE/'vendor'
CENTER=632
PROFILE={1:2201,2:412,3:510,4:127,5:40}
HELPERS={4:28,7:7,8:47,9:326}


def need(x,message):
    if not x:raise ValueError(message)


def load_core():
    path=ROOT/'research/native-center-free-code/native_core.py'
    spec=importlib.util.spec_from_file_location('retained_native_core',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def payload():
    return json.loads(gzip.decompress((ROOT/'research/native-center-free-code/CODED-WORDS.json.gz').read_bytes()))


def embed_vector(v,unit,units=19):
    """Common axis 0, independent eight-axis unit blocks; no selected-stage powers."""
    need(type(v)is int and 0<=v<512 and 0<=unit<units,'Nine-axis embedding input')
    return (v&1)|((v>>1)<<(1+8*unit))


def role_name(role,unit):
    need(0<=role<=CENTER,'Local role range')
    if role<112:return ['MAIN',2*unit,role]
    if role<224:return ['MAIN',2*unit+1,role-112]
    if role<CENTER:return ['HELPER',unit,role-224]
    return ['OWNED_CENTER',unit]


def event_role(tag,unit):
    need(tag[0]=='L' or tag==['C',0],'Source role tag')
    return role_name(tag[1] if tag[0]=='L' else CENTER,unit)


def serialize(unit,direction,source=None,units=19):
    """Emit every actual source event; frames are locally named and explicitly embedded.
    Source adapters are retained, not replaced by their semantic specification.
    """
    need(direction in ('forward','backward') and 0<=unit<units,'Unit and direction')
    source=payload() if source is None else source
    c=source['canonical']
    frame=lambda i:['FRAME',unit,i]
    out=[{'op':'clear','target':role_name(CENTER,unit),'frame':frame(0)}]
    for e in source['programs'][direction]:
        kind=e[0]
        if kind=='scalar':
            g,f=e[1:];op=g[0]
            row={'op':op,'target':event_role(g[1],unit),'frame':frame(f)}
            if op in ('add','copy'):row['source']=event_role(g[2],unit)
            if op=='add':row['coefficient']=[g[3],g[4]]
            if op=='scale':row['coefficient']=[g[2],g[3]]
            out.append(row)
        elif kind=='climb':
            out.append({'op':'climb','target':role_name(e[2],unit),'source_frame':frame(e[3]),
                        'target_frame':frame(e[4]),'rank':e[5],'retained_tag':e[1]})
        elif kind=='center':
            out.append({'op':'center','target':role_name(CENTER+e[1],unit),'source_frame':frame(e[2]),
                        'target_frame':frame(e[3]),'rank':e[4]})
        elif kind=='warp':
            out.append({'op':'warp','target':event_role(e[1],unit),'source_frame':frame(e[3]),
                        'target_frame':frame(e[4]),'retained_native_map':[unit,e[2]]})
        elif kind=='adapter':
            out.append({'op':'adapter','retained_record':e[1:],'target':role_name(e[2],unit),'local_frame':frame(e[3]),'unit':unit,
                        'axis_map':[0]+list(range(1+8*unit,9+8*unit))})
        elif kind=='phase':out.append({'op':'phase','retained_record':e[1:]})
        else:raise ValueError('Unlowered native opcode '+kind)
    out.append({'op':'clear','target':role_name(CENTER,unit),'frame':frame(0)})
    frames=[[embed_vector(v,unit,units) for v in basis] for basis in c['frames']]
    native_maps=[]
    active=[0]+list(range(1+8*unit,9+8*unit))
    for rec in c['warps']:
        local=rec['G_columns']
        def apply(v):
            result=0
            for bit,column in enumerate(local):
                if v>>bit&1:result^=column
            return result
        inverse={apply(v):v for v in range(512)}
        need(len(inverse)==512,'Native permutation map invertible')
        invcols=[inverse[1<<j] for j in range(9)]
        full=[1<<j for j in range(1+8*units)]
        fullinv=full.copy()
        for j,axis in enumerate(active):
            full[axis]=embed_vector(local[j],unit,units)
            fullinv[axis]=embed_vector(invcols[j],unit,units)
        native_maps.append({'op':[unit,rec['op']],'columns':full,'inverse_columns':fullinv,
                            'source_frame':frame(rec['from_frame']),'target_frame':frame(rec['to_frame']),
                            'lender':role_name(rec['lender'],unit),'source_B_pos':rec['B_pos']})
    return {'unit':unit,'direction':direction,'ambient_address_axes':1+8*units,
            'active_axes':[0]+list(range(1+8*unit,9+8*unit)),
            'spectator_axes':[i for i in range(1+8*units) if i not in [0]+list(range(1+8*unit,9+8*unit))],
            'frames':frames,'native_maps':native_maps,'input_frames':[frame(i) for i in c['start']],
            'output_frames':[frame(i) for i in c['final']],
            'paid_profile':c['local_profile'],'persistent_roles':[role_name(i,unit) for i in range(CENTER)],
            'owned_roles':[role_name(CENTER,unit)],'events':out}


def rank(vectors):
    basis={}
    for v in vectors:
        while v:
            bit=v.bit_length()-1
            if bit in basis:v^=basis[bit]
            else:basis[bit]=v;break
    return len(basis)


def inspect(program,source):
    c=source['canonical'];cur={tuple(r):f for r,f in zip(program['persistent_roles'],program['input_frames'])}
    owned=tuple(program['owned_roles'][0]);cur[owned]=['UNKNOWN_DIRTY_FRAME']
    paid=Counter();scalar=Q(0)
    maps={tuple(m['op']):m for m in program['native_maps']}
    for m in maps.values():
        need(len(m['columns'])==len(m['inverse_columns'])==program['ambient_address_axes'],'Full ambient permutation columns')
        for axis in program['spectator_axes']:
            need(m['columns'][axis]==m['inverse_columns'][axis]==1<<axis,'Spectators untouched')
    for e in program['events']:
        op=e['op']
        if op in ('phase','adapter'):continue
        r=tuple(e['target'])
        if op=='clear':
            need(r==owned,'Only owned center can be erased');cur[r]=e['frame'];scalar+=2
        elif op in ('add','scale','copy'):
            need(cur[r]==e['frame'],'Scalar target frame')
            if op in ('add','copy'):need(cur[tuple(e['source'])]==e['frame'],'Scalar source frame')
            if op=='copy':need(r==owned,'Only owned center can be overwritten');scalar+=2
            else:
                q=Q(*e['coefficient']);n,d=abs(q.numerator),q.denominator
                need(n and not d&(d-1),'Dyadic coefficient')
                if op=='scale':
                    need(not n&(n-1),'Power-of-two scale')
                    scalar+=2*(abs(n.bit_length()-d.bit_length())+(q<0))
                else:scalar+=2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
        else:
            need(cur[r]==e['source_frame'],'Native source frame')
            cur[r]=e['target_frame']
            if op in ('climb','center'):
                a=e['source_frame'][2];b=e['target_frame'][2]
                need(abs(rank(program['frames'][b])-rank(program['frames'][a]))==e['rank'],'Embedded native rank')
                paid[e['rank']]+=1
            else:
                need(op=='warp','Only exact retained native maps or climbs')
                u,k=e['retained_native_map']
                need((u,abs(k)) in maps,'Serialized native map resolved by explicit columns')
                native=maps[(u,abs(k))]
                columns=native['columns'] if k>0 else native['inverse_columns']
                def apply_columns(v):
                    output=0
                    for bit,column in enumerate(columns):
                        if v>>bit&1:output^=column
                    return output
                before=program['frames'][e['source_frame'][2]]
                after=program['frames'][e['target_frame'][2]]
                image=[apply_columns(v) for v in before]
                need(rank(image)==rank(after)==rank(image+after),
                     'Actual native map sends complete source frame span to target frame span')
    need([cur[tuple(r)] for r in program['persistent_roles']]==program['output_frames'],'Every exit frame')
    need(cur[owned]==['FRAME',program['unit'],0],'Owned center returned blank ground frame')
    need(dict(paid)=={int(k):v for k,v in source['canonical']['local_profile'].items()},'Complete serialized profile')
    return {'events':len(program['events']),'paid':dict(paid),'scalar_tariff':int(scalar),
            'owned_entry_clear':True,'owned_exit_clear':True,'persistent_inputs':632,
            'helper_target_profile':HELPERS}


def verify_exports(data):
    for direction in ('forward','backward'):
        path=HERE/('UNIT0-'+direction+'.json.gz')
        need(path.is_file(),'Missing required literal export '+path.name)
        need(json.loads(gzip.decompress(path.read_bytes()))==serialize(0,direction,data),
             'Literal serialized export disagrees with source: '+path.name)


def verify(check_exports=True):
    sources=json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']
    for row in sources:need(sha256((HERE/row['package_path']).read_bytes()).hexdigest()==row['sha256'],'Changed source '+row['path'])
    data=payload();c=data['canonical'];V=load_core()
    # Independently rederive the arbitrary-input free-group endpoint, not just frames.
    original=json.loads(gzip.decompress((ROOT/'research/native-center-free-code/SOURCE-WORD.json.gz').read_bytes()))
    need(sha256(gzip.decompress((ROOT/'research/native-center-free-code/SOURCE-WORD.json.gz').read_bytes())).hexdigest()==V.SOURCE_SHA,'Original native source')
    E=V.error_kernel(original)
    EX=[[Q(0)]*112 for _ in range(112)]
    for i,j,v in E:
        if j<112:EX[i-112][j]=v
    source_A=[[Q(x) for x in row] for row in json.loads((ROOT/'research/native-center-free-code/CODE.json').read_text())['A']]
    need(len(source_A)==112 and all(len(row)==112 for row in source_A),'Actual code dimensions')
    need(all(source_A[i][j]==Q(i==j)+EX[i][j] for i in range(112) for j in range(112)),
         'All 12544 actual source code entries match the rederived endpoint')
    expected_helpers=Counter(len(c['frames'][c['final'][i]])-len(c['frames'][c['start'][i]]) for i in range(224,632))
    need(dict(expected_helpers)==HELPERS,'All 408 independent helper targets')
    logical=[]
    for direction in ('forward','backward'):
        back=direction=='backward'
        p=[['scalar',['clear',['C',0]],0]]+data['programs'][direction]+[['scalar',['clear',['C',0]],0]]
        rows,paid,mx=V.replay(c,p,back)
        for i in range(CENTER):
            expected=V.expected(i,back)
            if not back and 112<=i<224:
                for j,v in enumerate(EX[i-112]):
                    if v:V.add(expected,V.identity(j),v)
            if back and i<112:
                for j in range(112):
                    if EX[j][i]:V.add(expected,V.identity(112+j),-EX[j][i])
            need(rows[i]==expected,'Every arbitrary-input endpoint row')
        need(dict(paid)==PROFILE,'Logical replay profile')
        logical.append({'direction':direction,'max_prefix_l1':str(mx),'all_arbitrary_rows':632})
    checks=[]
    for unit in range(19):
        for direction in ('forward','backward'):
            p=serialize(unit,direction,data)
            # Embedding is linear, injective, and support-exact on all 512 local vectors.
            need(len({embed_vector(v,unit) for v in range(512)})==512,'Injective local embedding')
            need(all(embed_vector(1<<i,unit)==1<<p['active_axes'][i] for i in range(9)),'Exact axis basis image')
            checks.append({'unit':unit,'direction':direction,**inspect(p,data)})
    uncoded=[]
    for direction in ('forward','backward'):
        back=direction=='backward'
        raw=[['scalar',['clear',['C',0]],0]]+original['programs'][direction]+[['scalar',['clear',['C',0]],0]]
        rows,paid,mx=V.replay(original['canonical'],raw,back)
        need(all(rows[i]==V.expected(i,back) for i in range(CENTER)),'Actual uncoded producer endpoint')
        unit=serialize(0,direction,original)
        uncoded.append({'direction':direction,**inspect(unit,original),'all_arbitrary_rows':632,'max_prefix_l1':str(mx)})
    # Reject a real changed frame and unpaid job on serialized output.
    p=serialize(0,'forward',data)
    e=next(e for e in p['events'] if e['op']=='climb');e['rank']+=1
    try:inspect(p,data)
    except ValueError:pass
    else:raise ValueError('Accepted changed serialized rank')
    if check_exports:verify_exports(data)
    return {'status':'PASS_CENTER_FREE_NATIVE_UNIT_SERIALIZATION_NOT_P19_CHAIN',
            'authenticated_actual_code_entries':12544,
            'local_paid':PROFILE,'independent_helper_targets':HELPERS,
            'logical_endpoints':logical,'serialized_units_checked':checks,'uncoded_source_leaf':uncoded,
            'source_files_authenticated':len(sources),'new_multiplication_kappa':None,
            'p19_pure_shears_compiled':False,
            'boundary':'Native coded endpoint (X,Y,H)->(X,Y+A X,H), raw dual (X-A^T Y,Y,H), with original entrance/exit charts. Normalized full calls include D; no unpaid pure shear is inferred.'}


if __name__=='__main__':
    result=verify(check_exports='--emit' not in sys.argv)
    if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:need(json.loads((HERE/'RESULT.json').read_text())==json.loads(json.dumps(result)),'Retained unit receipt')
    if '--emit' in sys.argv:
        # Authoring only: literal actual events, not an unresolved macro.
        for direction in ('forward','backward'):
            raw=json.dumps(serialize(0,direction),sort_keys=True,separators=(',',':')).encode()
            with gzip.GzipFile(filename=str(HERE/('UNIT0-'+direction+'.json.gz')),mode='wb',mtime=0) as f:f.write(raw)
        verify_exports(payload())
    print(json.dumps({k:result[k] for k in ['status','local_paid','independent_helper_targets','source_files_authenticated','new_multiplication_kappa']}))
