# SPDX-License-Identifier: Apache-2.0
import sys,json,random,hashlib,argparse
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from sources import MACHINE,ACTUAL,PROGRAM,need,authenticate
from independent import execute as independent_execute
from bridge import assemble,capacities,ROLES,RAW,DESCRIPTORS,BLANK,LEFT

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def oracle(payload,g):
    H,A,G,S=g;Q=1<<H;out=[None]*len(payload)
    for i,x in enumerate(payload):
        a,last=divmod(i,S);a,y=divmod(a,Q);a,middle=divmod(a,G);a,first=divmod(a,Q)
        out[((((a*Q+y)*G+middle)*Q+first)*S+last)]=x
    return out

def run_history(geometry,modes,seed=19173365,full=False,payloads=None,dual=False,mutate=None):
    code,entries,points,factor=assemble(geometry)
    if mutate:code=mutate(code,points)
    tapes={r:bytearray([BLANK]) for r in ROLES};heads={r:0 for r in ROLES}
    steps=0;record=[];maxima={r:1 for r in ROLES};rng=random.Random(seed)
    def run(entry):
        nonlocal steps
        initial={r:(bytes(tapes[r]),heads[r]) for r in ROLES} if dual else None
        result=MACHINE.execute(code,tapes,heads,entries[entry],max_steps=2000000000)
        if dual:
            cells,lengths,other_heads,counts=independent_execute(code,initial,entries[entry],result['steps']+1)
            need(counts==result and other_heads==heads,'independent counts/heads')
            need(all(lengths[r]==len(tapes[r]) and cells[r]=={i:x for i,x in enumerate(tapes[r]) if x!=BLANK} for r in ROLES),'independent contents/backing')
        need(result['status']!='rejected','literal boundary admitted');steps+=result['steps'];return result
    init=run('init_descriptors')
    J=sum(max(1,x.bit_length()) for g in geometry.values() for x in g)
    need(init['steps']==6*J+65,'exact descriptor initialization tariff')
    for mode,g in geometry.items():
        for name,value in zip(DESCRIPTORS,g):
            expected=bytes([LEFT]+[(value>>i)&1 for i in range(max(1,value.bit_length()))]+[3])
            need(bytes(tapes[mode+'_'+name])==expected and heads[mode+'_'+name]==1,'exact raw descriptor source constants')
    descriptors={r:(bytes(tapes[r]),heads[r]) for r in ROLES if r.startswith(('u_','t_'))}
    for call_index,mode in enumerate(modes):
        g=geometry[mode];H,A,G,S=g;V=A*4**H*G*S
        payload=payloads[call_index] if payloads is not None else [rng.randrange(2) for _ in range(V)]
        need(len(payload)==V,'complete supplied raw payload')
        # External raw payload is supplied. This observer loading is not a codec.
        target=tapes[RAW]
        incoming=bytes([LEFT]+payload)
        if len(target)<len(incoming):target.extend([BLANK]*(len(incoming)-len(target)))
        target[:len(incoming)]=incoming
        for i in range(len(incoming),len(target)):target[i]=BLANK
        heads[RAW]=1;owner=id(target)
        before=sum(map(len,tapes.values()));result=run(mode)
        need(id(tapes[RAW])==owner and list(tapes[RAW][:V+1])==[LEFT]+oracle(payload,g) and all(x==BLANK for x in tapes[RAW][V+1:]) and heads[RAW]==1,'same raw owner/endpoint')
        need(all((bytes(tapes[r]),heads[r])==state for r,state in descriptors.items()),'borrowed raw descriptors preserved')
        for r in ROLES:
            if r.startswith('E_'):need(all(x==BLANK for x in tapes[r]) and heads[r]==0,'owned encoded banks retired')
        caps=capacities(g)
        for r,c in caps.items():maxima[r]=max(maxima[r],c);need(len(tapes[r])==maxima[r],'exact rolewise retained capacity '+r)
        I=sum(max(1,n.bit_length()) for n in g);L=H+I+8
        bound=2**23*(H+1)*(V+1)*(L+1)**2+256*(V+1)+128*(V+I+16)
        need(result['steps']<=bound,'complete instruction bound')
        record.append({'mode':mode,'geometry':g,'volume':V,'steps':result['steps'],'backing':sum(map(len,tapes.values())),'output_sha256':hashlib.sha256(bytes(tapes[RAW])).hexdigest()})
    close=run('close_descriptors')
    need(close['steps']==7*J+137,'exact descriptor retirement tariff')
    need(all(heads[r]==0 and all(x==BLANK for x in tapes[r]) for r in ROLES if r!=RAW),'complete terminal retirement')
    return {'calls':record,'init_steps':init['steps'],'close_steps':close['steps'],'instructions':len(code),'roles':len(ROLES),'control_factor':factor,'total_steps':steps}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--full',action='store_true');ap.add_argument('--write',action='store_true');args=ap.parse_args()
    cases=[({'u':(0,1,1,1),'t':(0,2,1,1)},['u','t','u']),({'u':(1,1,2,2),'t':(1,2,1,2)},['u','t','u']),({'u':(2,1,1,1),'t':(2,1,1,1)},['u','t'])]
    result={'status':'PASS_RAW_BINARY_SHUTTLE_BRIDGE','cases':[run_history(g,m,dual=True) for g,m in cases],'actual_geometry':ACTUAL}
    if not args.full:
        basis=[[int(i==j) for i in range(16)] for j in range(16)]
        result['basis']=run_history({'u':(2,1,1,1),'t':(2,1,1,1)},['u']*16,payloads=basis,dual=True)
        failures=[]
        def wrong_raw(code,points):
            out=list(code);i=next(i for i,x in enumerate(out) if x==('write','RAW',0));out[i]=('write','RAW',1);return tuple(out)
        def omit_install(code,points):
            out=list(code);i=out.index(('jump',points['u']['install']));out[i]=('jump',points['u']['close']);return tuple(out)
        for name,mutation in [('wrong_decoded_bit',wrong_raw),('omitted_child_install',omit_install)]:
            try:run_history({'u':(1,1,1,1),'t':(1,1,1,1)},['u'],payloads=[[0,1,0,0]],mutate=mutation)
            except ValueError:failures.append(name)
            else:raise ValueError('semantic mutation survived '+name)
        result['rejecting_controls']=failures
        cap_u,cap_t=capacities(ACTUAL['u']),capacities(ACTUAL['t'])
        need(sum(max(cap_u[r],cap_t[r]) for r in cap_u)>max(sum(cap_u.values()),sum(cap_t.values())),'max-of-totals falsifier')
        result['actual_bank_invoice']={'owned_u':sum(cap_u.values()),'owned_t':sum(cap_t.values()),'owned_history_ut':sum(max(cap_u[r],cap_t[r]) for r in cap_u),'borrowed_raw_payload':196609,'caller_descriptors':52}
    if args.full:result={'status':'PASS_ACTUAL_RAW_BINARY_SHUTTLE','case':run_history(ACTUAL,['u'])}
    path=HERE/('FULL.json' if args.full else 'RESULT.json')
    if args.write:need(not path.exists(),'new receipt only');path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(canonical(result)==canonical(json.loads(path.read_text())),'typed receipt')
    authenticate();print(canonical(result))
if __name__=='__main__':main()
