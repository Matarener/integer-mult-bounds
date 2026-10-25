#!/usr/bin/env python3
"""Independently evaluate the literal3981/3943 fusion on280 dirty input columns."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import argparse,copy,hashlib,importlib.util,json
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
WIT='research/p104-native-channel/inputs/LOWRANK-WITNESS.json'
FULL=[1<<i for i in range(9)]
NAMES=[f'{p}{i}' for p,n in [('X',104),('Y',104),('Q',8),('G',32),('D',32)] for i in range(n)]
def need(ok,msg):
    if not ok:raise ValueError(msg)
def load(path):
    def pairs(items):
        d={}
        for k,v in items:
            need(k not in d,'duplicate JSON key');d[k]=v
        return d
    return json.loads(path.read_text(),object_pairs_hook=pairs)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def sha(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def span(v):
    out={0}
    for k in v:out|={x^k for x in tuple(out)}
    return frozenset(out)
def plus(a,b,c):
    out=a.copy()
    for k,v in b.items():
        out[k]=out.get(k,F(0))+c*v
        if not out[k]:del out[k]
    return out

def source_modules():
    src=load(P/'SOURCES.json')
    for f in src['files']:
        if f['usage']=='input':need(hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'],'source pin '+f['path'])
    mods=[]
    for f in src['source_exports']:
        p=P/f['path'];raw=p.read_bytes();need(hashlib.sha256(raw).hexdigest()==f['sha256'],'frozen export '+f['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==f['upstream_git_blob'],'original Git blob '+f['path'])
        spec=importlib.util.spec_from_file_location(p.stem,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);mods.append(m)
    return load(ROOT/WIT),mods

def execute(w,program):
    rows={r:{r:F(1)} for r in NAMES};frames={r:span(w['initial_frames'][r]) for r in NAMES};paid=Counter();ops=Counter()
    for e in program:
        op,r=e[:2];ops[op]+=1
        if op=='transport':
            _,r,a,b,k=e;sa,sb=span(a),span(b)
            need(frames[r]==sa and (sa<=sb or sb<=sa),'literal transport entrance/nesting')
            need(type(k)is int and k==abs(len(a)-len(b))>0 and len(sa)==2**len(a) and len(sb)==2**len(b),'positive rank tariff')
            paid[k]+=1;frames[r]=sb
        elif op=='add':
            _,r,s,c,f=e;need(r!=s and frames[r]==frames[s]==span(f),'physical common chart ADD')
            rows[r]=plus(rows[r],rows[s],F(c))
        elif op in ('half','double'):
            need(frames[r]==span(FULL),'scalar common FULL');c=F(1,2) if op=='half' else F(2);rows[r]={i:c*v for i,v in rows[r].items()}
        elif op=='zero':
            need(r=='C' and r not in rows,'owned allocation');rows[r]={};frames[r]=span(e[2])
        elif op=='copy':
            need(r=='C' and not rows[r] and frames[r]==frames[e[2]]==span(e[3]),'owned zero copy');rows[r]=rows[e[2]].copy()
        else:
            need(op=='erase' and r=='C' and frames[r]==span(e[2]),'owned private discard');del rows[r];del frames[r]
    need(set(rows)==set(NAMES),'all public roles and no private leaks')
    return rows,frames,dict(paid),dict(ops)

def tail_program(w,m):
    _,A,J,N,B=m.geometry();out=[]
    for e in m.program(J,N,B):
        op,r=e[:2];r=NAMES[r]
        if op in ('lift','drop'):
            i=int(r[1:]);h=w['final_frames'][f'Y{i}'];out.append(['transport',r,h if op=='lift' else FULL,FULL if op=='lift' else h,1])
        elif op=='add':out.append(['add',r,NAMES[e[2]],e[3],FULL])
        else:need(op in ('half','double'),'tail alphabet');out.append([op,r])
    need(out[:104]==[['transport',f'Y{i}',w['final_frames'][f'Y{i}'],FULL,1] for i in range(104)],'old lift prefix')
    return out,A,J,N,B

def invoice(program):
    c=Counter()
    for e in program:
        if e[0]=='add':
            z=abs(F(e[3]));need(z.denominator&(z.denominator-1)==0,'dyadic coefficients');c['unit_add']+=z.numerator;s=z.denominator.bit_length()-1;c['half']+=s;c['double']+=s
        elif e[0] in ('half','double'):c[e[0]]+=1
        elif e[0]=='transport':c['positive_native_mass']+=e[4]
        else:c[e[0]]+=1
    return dict(c)

def calculate():
    w,mods=source_modules();old3981,old3943,old3882,old3940=mods
    late,_,removed=old3981.compile_delivery(w);late=late['program'];suffix=w['program'][3642:]
    need(len(suffix)==416 and late[-416:]==suffix,'literal416 cleanup suffix')
    prefix=late[:-416];tail,A,J,N,B=tail_program(w,old3882);tail=tail[104:]
    D=[[F(0)]*104 for _ in range(8)]
    for e in suffix:
        need(e[0]=='add' and e[1].startswith('Q') and e[2].startswith('X') and e[4]==FULL and abs(F(e[3]))==2,'actual source cleanup alphabet')
        D[int(e[1][1:])][int(e[2][1:])]+=F(e[3])
    T=[[r[j] for j in J] for r in D]
    need(T==old3943.T and sum(c!=0 for r in T for c in r)==32,'same actual3943 cleanup factor')
    need(all(D[k][n]==sum(T[k][b]*B[b][a] for b in range(8)) for k in range(8) for a,n in enumerate(N)),'D=T[I B]')
    cleanup=[['add',r,s,c,FULL] for op,r,s,c in old3943.consumer(J)]
    need(len(cleanup)==64 and all(e[3] in (-1,1) for e in cleanup),'64 read-only unit ADDs')
    reference=late+tail;fused=prefix+tail+cleanup
    old,of,p0,c0=execute(w,reference);new,nf,p1,c1=execute(w,fused)
    need(new==old and nf==of and p1==p0,'all280 endpoint rows and exact formal frames/profile')
    need([e for e in fused if e[0]=='transport']==[e for e in reference if e[0]=='transport'],'entire native chronological subsequence unchanged')
    atcut,cf,_,_=execute(w,prefix)
    need(all(f==span(FULL) for f in cf.values()),'all280 roles FULL after late delivery')
    for i in range(104):
        need(atcut[f'X{i}']=={f'X{i}':F(1)},'literal source at late cut')
        want={f'Y{i}':F(1)};want.update({f'X{j}':x for j,x in enumerate(A[i]) if x});need(atcut[f'Y{i}']==want,'late delivery Gram endpoint')
        target=f'Y{i}' if i in J else f'X{i}';need(new[target]=={f'X{i}':F(1),f'Y{i}':F(1)},'unchanged sum slot')
    for k in range(8):
        want={f'Q{k}':F(1)};want.update({f'X{i}':-x for i,x in enumerate(D[k]) if x});need(atcut[f'Q{k}']==want,'actual Q=h-Dx at fusion cut')
    intermediate,ff,_,_=execute(w,prefix+tail)
    for b,j in enumerate(J):
        want={f'X{j}':F(1)};want.update({f'X{n}':B[b][a] for a,n in enumerate(N) if B[b][a]});need(intermediate[f'X{j}']==want and ff[f'X{j}']==span(FULL),'actual residual q donor at FULL')
    need(all(new[r]=={r:F(1)} for r in NAMES if r[0] in 'QGD'),'all72 arbitrary dirty returns')
    for i in N:
        want={f'Y{i}':F(1)};want.update({f'X{j}':x for j,x in enumerate(A[i]) if x})
        need(new[f'Y{i}']==want,'unchanged nonpivot Gram residual')
    # Optional actual inherited source-return consumer; no claim its192 tariff is new.
    adapter=[]
    for e in old3943.return_adapter(B,J,N):
        op,r=e[:2]
        if op in ('up','down'):
            h=w['final_frames'][f'Y{e[2]}'];adapter.append(['transport',r,h if op=='up' else FULL,FULL if op=='up' else h,1])
        elif op=='scale':adapter.append(['half' if F(e[2])==F(1,2) else 'double',r])
        else:need(op=='add','return alphabet');adapter.append(['add',r,e[2],e[3],FULL])
    returned,rf,_,_=execute(w,fused+adapter)
    for i in range(104):
        need(returned[f'X{i}']=={f'X{i}':F(1)} and rf[f'X{i}']==span(FULL),'source return exact')
        need(returned[f'Y{i}']=={f'X{i}':F(1),f'Y{i}':F(1)} and rf[f'Y{i}']==span(w['final_frames'][f'Y{i}']),'legacy sum and frame')
    need(all(returned[r]=={r:F(1)} for r in NAMES if r[0] in 'QGD'),'legacy72dirtyreturn')
    legacy_invoice=invoice(fused+adapter)
    need(legacy_invoice=={'unit_add':5664,'half':2720,'double':2720,'positive_native_mass':2712},'complete legacy return invoice')
    # The actual3940 fused source-preserving tail contains q only temporarily.
    sp_ops=old3940.fused(J,N,B);pre_ops=old3940.pivot_stream(J,N,B)+old3940.scatter(J,N,B,104)
    need(sp_ops[:104]==[['lift',104+i] for i in range(104)] and sp_ops[104:104+len(pre_ops)]==pre_ops,'literal3940internalcut')
    def indexed_events(ops):
        converted=[]
        for e in ops:
            op,r=e[:2];r=NAMES[r]
            if op in ('lift','drop'):
                h=w['final_frames'][f'Y{int(r[1:])}'];converted.append(['transport',r,h if op=='lift' else FULL,FULL if op=='lift' else h,1])
            elif op=='add':converted.append(['add',r,NAMES[e[2]],e[3],FULL])
            else:need(op in ('half','double'),'source-preservingtailalphabet');converted.append([op,r])
        return converted
    sp_tail=indexed_events(sp_ops[104:]);sp_cut=len(pre_ops)
    sp_reference=late+sp_tail;sp_fused=prefix+sp_tail[:sp_cut]+cleanup+sp_tail[sp_cut:]
    sp_old,sp_of,_,_=execute(w,sp_reference);sp_new,sp_nf,_,_=execute(w,sp_fused)
    need(sp_old==sp_new==returned and sp_of==sp_nf==rf,'actual3940same source-preservingendpoint')
    need([e for e in sp_reference if e[0]=='transport']==[e for e in sp_fused if e[0]=='transport'],'3940matched native subsequence')
    liveq,qframes,_,_=execute(w,prefix+sp_tail[:sp_cut])
    need(all(liveq[f'X{j}']==intermediate[f'X{j}'] and qframes[f'X{j}']==span(FULL) for j in J),'source-preservingactualqexistsFULL')
    need(all(liveq[f'Q{k}']==atcut[f'Q{k}'] for k in range(8)),'source-preservingQnot prematurelyrestored')
    spinv0,spinv1=invoice(sp_reference),invoice(sp_fused)
    need(spinv0=={'unit_add':5856,'half':2712,'double':2712,'positive_native_mass':2520},'matched3940baselineinvoice')
    need(spinv1=={'unit_add':5088,'half':2712,'double':2712,'positive_native_mass':2520},'source-preservingfusedinvoice')
    too_late=execute(w,prefix+sp_tail+cleanup)[0]
    need(sum(too_late[f'Q{k}']!=sp_new[f'Q{k}'] for k in range(8))==8,'cleanup after q-restorationmustfail8dirtyreturns')
    inv0,inv1=invoice(reference),invoice(fused)
    need(inv0=={'unit_add':5472,'half':2616,'double':2616,'positive_native_mass':2520},'exact3981 comparison invoice')
    need(inv1=={'unit_add':4704,'half':2616,'double':2616,'positive_native_mass':2520},'fused invoice')
    bads={'omit_compressed_cleanup':prefix+tail,'cleanup_before_residual':prefix+cleanup+tail,'reuse_old_cleanup_after_source_consumption':prefix+tail+suffix,'double_cleanup':prefix+suffix+tail+cleanup,'omit_one_unit':prefix+tail+cleanup[:-1]}
    # Delivery must read the live query before restoring it to arbitrary dirt.
    # Replace quartering's final doubles with nothing: this must fail as well.
    broken=copy.deepcopy(prefix);i=next(i for i,e in enumerate(broken) if e==['double','Q0']);del broken[i:i+2];bads['unrestored_late_donor']=broken+tail+cleanup
    lift0=next(i for i,e in enumerate(prefix) if e==['transport','Y0',w['final_frames']['Y0'],FULL,1])
    bads['correction_before_late_delivery']=prefix[:lift0+104]+tail+prefix[lift0+104:]+cleanup
    controls={}
    for name,program in bads.items():
        try:b,bf,_,_=execute(w,program)
        except (ValueError,KeyError):controls[name]='frame-or-owner rejection';continue
        defects=[r for r in NAMES if b[r]!=old[r]];need(defects or bf!=of,'semantic control accepted '+name);controls[name]={'changed_roles':len(defects),'changed_dirty_roles':sum(r[0] in 'QGD' for r in defects)}
    # Inherited paired/two-axis gate is numerically unchanged by scalar fusion.
    gap=208*(inv1['positive_native_mass']-2312)-10816;need(gap==32448,'same failing two-axis gate')
    return {'schema_version':1,'scope':'actual3981 late delivery plus3943 compressed cleanup; exact finite formal-frame splice','cut_after_original_event':3641,'cleanup_factor':[[int(x) for x in row] for row in T],'literal_old_cleanup_events':416,'new_cleanup_unit_adds':64,'old_cleanup_unit_adds':832,'unit_adds_saved_against3981':768,'reference_invoice':inv0,'fused_invoice':inv1,'inherited_source_preserving_return_invoice':legacy_invoice,'direct_source_preserving_reference_invoice':spinv0,'direct_source_preserving_fused_invoice':spinv1,'source_preserving_internal_cut_after_tail_ops_without_lifts':sp_cut,'source_preserving_late_cleanup_defective_dirty_roles':8,'source_preserving_fused_program_sha256':sha(sp_fused),'native_profile':p1,'fused_formal_events':len(fused),'reference_formal_events':len(reference),'fused_event_counts':c1,'all_input_columns':280,'restored_dirty_helpers':72,'full_native_subsequence_unchanged':True,'actual3981_endpoint_preserved':True,'q_cleanup_reads_from_actual_residual':True,'endpoint_sha256':sha([[str(new[r].get(k,F(0))) for k in NAMES] for r in NAMES]),'fused_program_sha256':sha(fused),'controls':controls,'two_axis_gap':gap,'native_recipe_replay':False,'all_size_admission':False,'selected_frontier_changed':False},fused

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',action='store_true');args=ap.parse_args();result,_=calculate()
    if args.write_result:(P/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(canonical(result)==canonical(load(P/'RESULT.json')),'typed result mismatch')
    print('PASS_P104_FUSED_LATE_CLEANUP inputs=280 dirty=72 unit_adds=4704 saved=768 native_mass=2520 source_preserving_adds=5088 controls=8')
if __name__=='__main__':main()
