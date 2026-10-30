"""Exact reconstruction, arbitrary-dirty semantics and native source bindings.

New integration: Cinna Davis with OpenAI Codex assistance, Apache-2.0.
Retained interpreters and literal applier are credited in NOTICE.md.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
from copy import deepcopy
import gzip,hashlib,json,sys
P=Path(__file__).resolve().parent
sys.path[:0]=[str(P/'vendor'),str(P/'checks')]
import audit_core as C
from audit_verify import semantics
import staged_entries_applier as S
import inherited_frames as I

THREE={1:2487,2:713,3:224,4:102,5:20,8:8}
FOUR={1:2489,2:713,3:227,4:99,5:20,8:8}

def read(p):
    raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,msg):
    if not ok:raise ValueError(msg)
def pins():
    for rel,digest in read(P/'MANIFEST.json').items():need(sha(P/rel)==digest,'file pin: '+rel)
    for rel,source in read(P/'EXPORTED-SOURCES.json').items():need(sha(P/rel)==source['sha256'],'export pin: '+rel)
def reject(name,fn):
    try:fn()
    except (ValueError,C.AuditFailure):return name
    raise ValueError('accepted mutant: '+name)
def inspect(w,profile):
    C.hygiene(w);bill,widths,*_=C.frame_bill(w,lagrangian=True)
    need(bill==profile,'local profile')
    need({str(k):v for k,v in bill.items()}==w['report']['local_profile'],'declared bill')
    need({str(k):v for k,v in widths.items()}==w['report']['width_inventory'],'declared widths')
    need(w['cleanup']==C.derive_cleanup(w),'derived cleanup')
    independent,inventory=I.ledger(w)
    need(dict(independent)==bill and dict(inventory)==widths,'independent basis ledger')
    return semantics(C,w)
def scalar(g):return tuple(g[:-1])
def contract(old,new):
    need(set(old)==set(new),'word fields')
    for field in old:
        if field not in {'A','B','restore','start_extra','warps','report','cleanup'}:
            need(old[field]==new[field],'fixed field '+field)
    for sec in ['A','restore']:need(list(map(scalar,old[sec]))==list(map(scalar,new[sec])),'fixed scalar '+sec)
    need([r[1:] for r in old['warps']]==[r[1:] for r in new['warps']],'native maps and frames')
    starts=deepcopy(old['start_extra']);starts['601']=[127,45]
    need(starts==new['start_extra'],'only helper601 entrance changes')
    before,after=Counter(map(scalar,old['B'])),Counter(map(scalar,new['B']))
    deleted=[g for g in before.elements() if g[0]=='add' and g[2]==601 and Q(g[3],g[4])==Q(1,4)]
    need(len(deleted)==4 and {g[1] for g in deleted}=={183,202,175,123},'four quarter reads')
    need(before-after==Counter(deleted),'deleted opcode inventory')
    need(after-before==Counter([('add',602,601,-1,1),('add',123,601,1,2)]),'two exact releases')
def prefix_certificate(old):
    gates,_=C.program(old);v={601:Q(1),602:Q(-1)}
    for g in gates[:10515]:
        if g[0]=='corr':need(not v.get(g[2],0),'prefix correction sees vector')
        elif g[0]=='warp':need(not v.get(g[1],0),'prefix native sees vector')
        elif g[0]=='add':
            z=v.get(g[1],0)+Q(g[3],g[4])*v.get(g[2],0)
            if z:v[g[1]]=z
            else:v.pop(g[1],None)
        elif g[0]=='scale' and g[1] in v:v[g[1]]*=Q(g[2],g[3])
    need(v=={601:Q(1),602:Q(-1),123:Q(1,2)},'exact prefix release vector')
    for g in gates[10515:11161]:
        if g[0]=='add':need(g[2]!=602 and g[1]!=601,'release commutation')
        elif g[0]=='scale':need(g[1] not in (601,602) or g[2]==g[3],'release scale')
        elif g[0]=='warp':need(g[1] not in (601,602),'release warp')
        elif g[0]=='corr':need(g[2]!=602 and g[1]!=601,'release correction')
def controls(old,new,record):
    out=[]
    for target in [602,123]:
        i=next(i for i,g in enumerate(new['B']) if g[:3]==['add',target,601])
        for kind in ['omit','flip']:
            bad=deepcopy(new)
            if kind=='omit':
                bad['B'].pop(i)
                for r in bad['warps']:
                    if r[0]>i:r[0]-=1
            else:bad['B'][i][3]*=-1
            bad['cleanup']=C.derive_cleanup(bad)
            out.append(reject(f'{kind}_release_{target}',lambda:semantics(C,bad)))
    bad=deepcopy(new);bad['start_extra']['601']=old['start_extra']['601']
    out.append(reject('old_entrance',lambda:inspect(bad,FOUR)))
    rec=deepcopy(record);rec['source_canonical_sha256']='0'*64
    out.append(reject('wrong_source',lambda:S.apply(old,rec)))
    return out

def main():
    pins();rows={}
    native={p.relative_to(P/'native/vendor').as_posix():sha(p) for p in (P/'native/vendor').rglob('*') if p.is_file() and '__pycache__' not in str(p)}
    for tag in ['base','extra']:
        old=read(P/f'inputs/THREE-{tag}.json.gz');new=read(P/f'inputs/FOUR-{tag}.json.gz');rec=read(P/f'recipe/RECORD-{tag}.json')
        need(S.apply(old,rec)==new,'literal reconstruction');contract(old,new);prefix_certificate(old)
        old_check=inspect(old,THREE);new_check=inspect(new,FOUR)
        old_receipt=read(P/f'evidence/THREE-NATIVE-{tag}.json')
        need(old_receipt['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY','inherited three-entry native status')
        need(old_receipt['word_sha256']==sha(P/f'inputs/THREE-{tag}.json.gz'),'inherited native input binding')
        need([s['step'] for s in old_receipt['steps']]==['native','ledgers','local-replay','wrappers','phases'] and all(s['exit_code']==0 for s in old_receipt['steps']),'inherited five native stages')
        need(read(P/f'evidence/THREE-LOCAL-{tag}.json')['forward']['paid_profile']==old['report']['local_profile'],'inherited native bill')
        for phase_name,canonical_name in [('THREE-PHASES','THREE-CANONICAL'),('NATIVE-PHASES','NATIVE-CANONICAL')]:
            phases=read(P/f'evidence/{phase_name}-{tag}.json')
            canonical_path=P/f'evidence/{canonical_name}-{tag}.json.gz'
            need(phases['status']=='PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES','native exact phase recipes')
            need(phases['canonical_word_sha256']==sha(canonical_path),'native phase word binding')
        receipt=read(P/f'evidence/NATIVE-{tag}.json')
        need(receipt['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY','native status')
        need(receipt['word_sha256']==sha(P/f'inputs/FOUR-{tag}.json.gz'),'native word pin')
        need(receipt['source_sha256']==native,'native source closure')
        need([s['step'] for s in receipt['steps']]==['native','ledgers','local-replay','wrappers','phases'] and all(s['exit_code']==0 for s in receipt['steps']),'native stages')
        actual=read(P/f'evidence/NATIVE-LOCAL-{tag}.json')['forward']['paid_profile']
        need(actual==new['report']['local_profile'],'native paid profile')
        canonical=read(P/f'evidence/NATIVE-CANONICAL-{tag}.json.gz')
        origin=read(P/f'owner/old-NATIVE-{tag}.json.gz')['helper_origin']
        need(canonical['helper_origin']==origin,'fresh native helper order')
        nw=[len(I.b(canonical['frames'][canonical['final'][r]]))-len(I.b(canonical['frames'][canonical['start'][r]])) for r in range(224,632)]
        ww=[len(I.b(new['helper_final'].get(str(r),I.FULL)))-len(I.b(new['start_extra'].get(str(r),[]))) for r in origin]
        need(nw==ww,'fresh native width invoice')
        rows[tag]={'three':old_check,'four':new_check,'controls':controls(old,new,rec) if '--controls' in sys.argv else []}
    print(json.dumps({'status':'PASS_MIXED_FOURTH_WORDS','providers':rows},sort_keys=True))
if __name__=='__main__':main()
