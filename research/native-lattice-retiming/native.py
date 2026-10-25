"""One new subspace contact beyond PR4441. Apache-2.0, Codex assistance.
Retains zxv's native lineage and Cinna Davis's fresh-helper patch unchanged.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import gzip
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def need(ok, why):
    if not ok: raise ValueError(why)
def read(path):
    raw=Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
def build():
    N=load(ROOT/'research/fresh-helper-boundary/native.py','lattice_source_native')
    c=read(N.BASE/'THREE-base-FULL-IDENTITY-CANONICAL.json.gz')
    words=read(N.BASE/'THREE-base-FULL-IDENTITY-NATIVE.json.gz')
    changes=read(ROOT/'research/fresh-helper-boundary/CHANGES.json')
    patch=read(HERE/'PATCH.json')
    for key,field in [('entrances','start'),('exits','final')]:
        for role,old,new in changes[key]:
            need(c[field][role]==old,'Source helper boundary');c[field][role]=new
    maps={d:N.gates(word) for d,word in words.items()}
    need(set(maps['forward'])==set(maps['backward']),'Source dual contact inventory')
    for key in maps['forward']:
        f=words['forward'][maps['forward'][key]];b=words['backward'][maps['backward'][key]]
        need(b[1]==N.dual(f[1]) and b[2]==f[2],'Every literal dual scalar')
    for phase,ordinal,old,new in changes['gates']:
        for d in words:
            e=words[d][maps[d][phase,ordinal]];need(e[2]==old,'Source scalar frame');e[2]=new
    baseline={d:N.synthesize(c,word) for d,word in words.items()}
    need(c['frames'][patch['old_frame']]==patch['old_basis'],'Old frame basis')
    new_basis=patch['new_basis'];new=len(c['frames']);c['frames'].append(new_basis)
    need(N.span(new_basis)<N.span(patch['old_basis']),'Strict new subspace')
    key=(patch['phase'],patch['scalar_ordinal'])
    need(words['forward'][maps['forward'][key]][1]==patch['forward_gate'],'Exact changed ADD')
    for d in words:
        e=words[d][maps[d][key]];need(e[2]==patch['old_frame'],'Changed source contact');e[2]=new
    programs={d:N.synthesize(c,word) for d,word in words.items()}
    return N,c,programs,baseline

def run():
    N,c,programs,baseline=build()
    V=load(ROOT/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py','lattice_rows')
    X=load(ROOT/'research/kappa-rebuild/complex/native_extensions.py','lattice_second_rows')
    checks={};profiles={}
    for d,program in programs.items():
        rows,receipt=X.literal_replay(V,c,program,d=='backward')
        need(all(rows['L',r]==V.expected(('L',r),[],d=='backward',False) for r in range(632)),'All 632 arbitrary input endpoints')
        profile={int(k):v for k,v in receipt['paid_profile'].items()};profiles[d]=profile
        rebound=deepcopy(c);rebound['local_profile']=profile
        receipt['independent_interpreter']=V.replay(program,rebound,[],d=='backward',False)
        checks[d]=receipt
    need(profiles['forward']==profiles['backward'],'Same exact invoice in both orientations')
    H=Counter(len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]]) for r in range(224,632))
    need(dict(H)=={4:26,5:2,7:29,8:42,9:309},'Every helper retains its productive output')
    need(profiles['forward']=={1:2254,2:514,3:444,4:103,5:40,8:8},'Complete changed local paid profile')
    ce=load(ROOT/'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py','lattice_clifford')
    P=load(ROOT/'research/kappa-function-composition/complex/prune_native.py','lattice_phase_decoder')
    physical=[]
    old_edges={(e[3],e[4]) for e in baseline['forward'] if e[0]=='climb'}
    new_edges={(e[3],e[4]) for e in programs['forward'] if e[0]=='climb'}
    for a,b in sorted(new_edges-old_edges):
        op=ce.canonical_frame(9,c['frames'][a]).adjoint().then(ce.canonical_frame(9,c['frames'][b]))
        records={}
        for d in programs:
            actual=P.conjugate(ce,op) if d=='backward' else op
            rec=X.N.lower_exact(P,ce,actual)
            need(rec['rank']==len(c['frames'][b])-len(c['frames'][a]),'Exact physical child rank')
            records[d]=rec
        physical.append(dict(old_basis=c['frames'][a],new_basis=c['frames'][b],recipes=records))
    need(physical,'New physical edges must actually be checked')
    # A wrong new subspace must fail at a real scalar contact.
    bad=deepcopy(programs['forward']);site=next(i for i,e in enumerate(bad) if e[0]=='scalar' and e[1]==read(HERE/'PATCH.json')['forward_gate'] and e[2]==len(c['frames'])-1)
    bad[site][2]=732;rejected=False
    try: X.literal_replay(V,c,bad,False)
    except ValueError:rejected=True
    need(rejected,'Wrong contact frame negative control')
    rec=deepcopy(physical[0]['recipes']['forward']);original=P.monomial(ce,rec['right'],9).then(ce.fourier(9,range(rec['rank']))).then(P.monomial(ce,rec['left'],9))
    rec['left']['phase']=(rec['left']['phase']+1)%4
    corrupted=P.monomial(ce,rec['right'],9).then(ce.fourier(9,range(rec['rank']))).then(P.monomial(ce,rec['left'],9))
    need(original.tab==corrupted.tab and original.zero_state()!=corrupted.zero_state(),'Global phase corruption')
    return dict(status='PASS_NEW_LATTICE_CONTACT_BOTH_ORIENTATIONS_ALL_COLUMNS',helpers=dict(sorted(H.items())),paid=profiles['forward'],native=checks,new_physical_edges=physical,controls={'wrong_scalar_frame_rejected':True,'global_phase_only_corruption_rejected':True})
if __name__=='__main__':
    result=run();print(json.dumps({k:v for k,v in result.items() if k not in ('native','new_physical_edges')},sort_keys=True))
