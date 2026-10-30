#!/usr/bin/env python3
"""Global common-E compensation-kernel entrances for the old CLEAN R438 word.

All nine nested copied totals and all changed target caps remain priced.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import argparse
import gzip
import json
from global_kernel_boost import HERE,RAW,basis,contains,frames,native_charts,matkey,eye
from cold_cosets import bits,need
from helper_tail_retime import plus
from kernel_entrances import parity

N=660

def old_word(raw):
    B=[basis(raw['lines'][p]for p in f)for f in raw['frames']]
    current=raw['start'][:];records=[]
    def move(r,f):
        old=current[r]
        if old!=f:
            need(all(contains(B[f],q)for q in B[old]),'old original climb nested')
            records.append([0,r,old,f,len(B[f])-len(B[old]),0]);current[r]=f
    def phase(name,ph,c=1):
        for f,d,ss in raw[name]:
            for r in[d]+ss:move(r,f)
            for s in ss:records.append([1,d,s,c,f,ph])
    phase('D',10);phase('A',2)
    for i,h in enumerate(raw['ret']):
        f=current[h];records.append([2,h,N,f,0,3])
        for p,ss in enumerate(raw['scatter']):
            if i in ss:
                need(current[111+p]==0,'old totals scatter at actualZERO')
                records.append([1,111+p,N,1,0,3])
        records.append([3,h,N,f,0,3])
    phase('B',4);phase('C',5,-1)
    for r,f in enumerate(raw['final']):move(r,f)
    return {'start':raw['start'][:],'final':raw['final'][:],'records':records}

def replay(program,geom,initial=None,back=False):
    B=[basis(geom['lines'][p]for p in f)for f in geom['frames']]
    current=(program['final']if back else program['start'])[:]+[None]
    rows=[{j:1}for j in range(N)]+[{}]if initial is None else[r.copy()for r in initial]
    H=Counter();adds=copies=0;peak=1;opened=None;copyrows=[]
    for op,d,s,c,f,ph in reversed(program['records'])if back else program['records']:
        if op==0:
            a,b=(c,s)if back else(s,c)
            lo,hi=(b,a)if back else(a,b)
            need(current[d]==a and len(B[hi])-len(B[lo])==f>0 and all(contains(B[hi],v)for v in B[lo]),'actual old/new MOVE')
            current[d]=b;H[f]+=1
        elif op==1:
            need(d!=s and current[d]==current[s]==f,'actual common-frame ADD including copied scatter')
            need(opened is None or d!=opened,'copied total immutable untilERASE')
            rows[d]=plus(rows[d],rows[s],-c if back else c);adds+=1
            peak=max(peak,sum(abs(x)for x in rows[d].values()))
        elif op==(3 if back else 2):
            need(opened is None and s==N and not rows[N] and current[N]is None and current[d]==c,'fresh zero private COPY actual source frame')
            need(all(contains(B[c],v)for v in B[f]),'nested paid COPY target')
            tariff=len(B[c])-len(B[f]);need(tariff>0,'positive COPY tariff')
            rows[N]=rows[d].copy();current[N]=f;opened=d;H[tariff]+=1;copies+=1
            copyrows.append({'source_helper':d,'source_frame':c,'private_frame':f,'query_rank':tariff})
        else:
            need(op==(2 if back else 3)and opened==d and s==N and rows[N]==rows[d]and current[d]==c and current[N]==f,'literal ERASE original unchanged snapshot')
            rows[N]={};current[N]=None;opened=None
    need(current[:-1]==(program['start']if back else program['final'])and current[N]is None and opened is None,'every old/new endpoint')
    return rows,{'H':dict(sorted(H.items())),'mass':sum(k*v for k,v in H.items()),'ADDs':adds,'COPYs':copies,'private_fields':1,'COPY_records':copyrows,'prefix_row_L1':peak}

def dirty_factor(base,geom):
    noD=dict(base);noD['records']=[r for r in base['records']if r[-1]!=10]
    rows,_=replay(noD,geom)
    cols={h:sum((rows[111+p].get(h,0)&1)<<p for p in range(111))for h in range(222,N)}
    syntactic={h:0 for h in range(222,N)}
    for op,d,s,c,f,ph in base['records']:
        if op==1 and ph==10:syntactic[s]^=1<<(d-111)
    need(cols==syntactic,'semantic dirty columns independently match actual original compensation')
    B={};piv=[];dep=[];setup=[];witness=[]
    for h,v in cols.items():
        z=v;a=0
        while z:
            j=z.bit_length()-1
            if j not in B:B[j]=(z,a^(1<<len(piv)));piv.append(h);break
            w,c=B[j];z^=w;a^=c
        if not z:
            used=[piv[i]for i in bits(a)];x=cols[h]
            for k in used:x^=cols[k]
            need(x==0,'semantic kernel direction')
            dep.append(h);setup.extend((k,h)for k in used);witness.append({'helper':h,'pivot_helpers':used})
    need(len(piv)==111 and len(dep)==327,'old semantic dirty rank111/kernel327')
    return piv,dep,setup,witness

def build(base,raw,d):
    geom,E,joins,B=frames(raw,d);piv,dep,setup,witness=dirty_factor(base,raw);deps=set(dep)
    start=base['start'][:]
    for h in deps:start[h]=E
    current=start[:];records=[]
    def move(r,f,ph):
        old=current[r]
        if old!=f:
            need(all(contains(B[f],q)for q in B[old]),'new old-clean climb nested')
            tariff=len(B[f])-len(B[old]);need(tariff>0,'strict old-clean climb')
            records.append([0,r,old,f,tariff,ph]);current[r]=f
    records.extend(r[:]for r in base['records']if r[-1]==10 and r[2]not in deps)
    for r,f in enumerate(base['start']):move(r,joins[f],80)
    need(all(current[h]==E for h in range(222,N)),'actual commonE helper setup')
    records.extend([1,k,h,1,E,81]for k,h in setup)
    for op,r,s,c,f,ph in base['records']:
        if ph==10:continue
        if op==0:move(r,joins[c],ph)
        elif op==1:
            nf=E if s==N else joins[f]
            need(current[r]==nf and(s==N or current[s]==nf),'joined old-clean common scalar frame')
            records.append([1,r,s,c,nf,ph])
        else:
            need(op in(2,3)and current[r]==joins[c],'actual joined copied-total cut')
            records.append([op,r,s,joins[c],E,ph])
    need(all(current[h]==1 for h in range(222,N)),'old helperFULL inverse setup')
    records.extend([1,k,h,-1,1,82]for k,h in reversed(setup))
    final=[joins[f]for f in base['final']]
    new={'start':start,'final':final,'records':records,'format':'R438-global-coordinate-E-kernel-entrances-hybrid-v1'}
    return new,geom,E,joins,B,piv,dep,setup,witness

def receipt(d,write=False):
    need(sha256(RAW.read_bytes()).hexdigest()=='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','old R438 exact source')
    raw=json.loads(gzip.decompress(RAW.read_bytes()));base=old_word(raw)
    oldrows,oldrec=replay(base,raw)
    need(oldrec['H']=={1:1322,2:1342,3:79,4:44,5:102,6:11,7:18}and oldrec['mass']==5121,'entire retained clean profile')
    expected=[1<<j for j in range(N)]+[0]
    for p in range(111):expected[111+p]^=1<<p
    need(parity(oldrows)==expected,'all660 original signed lift columns modulo2')
    new,geom,E,joins,B,piv,dep,setup,witness=build(base,raw,d)
    rows,rec=replay(new,geom)
    need(all(rows[h]=={h:1}for h in list(range(111))+list(range(222,N)))and not rows[N],'all660 non-target Z rows and private exact restoration')
    need(parity(rows)==expected,'all660 changed hybrid binary VALUE columns')
    closed,invrec=replay(new,geom,rows,True)
    need(closed==[{j:1}for j in range(N)]+[{}],'literal signed inverse660 columns')
    lifts=[p for p in range(111)if new['final'][111+p]!=base['final'][111+p]]
    need(all(new['final'][111+p]==1 for p in lifts),'each changed cap is genuinelyFULL')
    copycost=sum(c['query_rank']for c in rec['COPY_records'])
    need(rec['mass']==5121-327*d+len(lifts)+copycost-63,'all changed coverage, COPY and entrance mass')
    # Include actual nested COPY query pairs in the full ADDRESS chart census.
    chartword=dict(new);chartword['records']=[r for r in new['records']if r[0]in(0,1)]
    chartword['records']+= [[0,0,c['private_frame'],c['source_frame'],c['query_rank'],84]for c in rec['COPY_records']]
    fs,charts,bad,odd=native_charts(chartword,geom,B)
    publicpaths=[]
    for r in range(222):
        path=[new['start'][r]]+[z[3]for z in new['records']if z[0]==0 and z[1]==r]
        publicpaths.append({'role':r,'path':path,'ranks':[len(B[f])for f in path]})
    badword=dict(new);badword['records']=[r for r in new['records']if r[-1]!=82]
    br,_=replay(badword,geom)
    need(any(br[h]!={h:1}for h in range(222,N)),'missing inverse kernel basis fails dirty restoration')
    canonical=json.dumps(new,sort_keys=True,separators=(',',':')).encode();gbytes=json.dumps(geom,sort_keys=True,separators=(',',':')).encode()
    out={'status':'PASS_LITERAL_OLD_R438_GLOBAL_E_KERNEL_HYBRID_WITH_NINE_PAID_TOTALS','no_new_kappa':True,
         'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','source':{str(RAW):sha256(RAW.read_bytes()).hexdigest()},
         'E_rank':d,'E_axes':list(range(d)),'E_frame':E,'semantic_dirty_rank':111,'kernel_witnesses':witness,
         'pivot_helpers':piv,'selected_helpers':dep,'ordinary_helpers':438,'private_fields':1,'private_COPY_rank_sum':copycost,
         'helper_inventory_by_residual_width':{8-d:327,8:111},'old_cap_targets_enlarged_toFULL':lifts,
         'old_cap_target_lift_count':len(lifts),'all_public_role_paths':publicpaths,
         'old_profile':oldrec,'profile':rec,'literal_inverse':invrec,'new_basis_ADDs':2*len(setup),
         'ADDRESS_frames':fs,'ADDRESS_MOVE_and_COPY_charts':charts,'finite_bad_prime_factors':bad,
         'joined_frames_with_odd_projector_denominators':odd,'word_canonical_sha256':sha256(canonical).hexdigest(),
         'geometry_canonical_sha256':sha256(gbytes).hexdigest(),
         'contract':'327 arbitrary dirty helpers enter at coordinate E and leaveFULL;111 pivot helpers enterZERO and leaveFULL. Sources retain their rank1 entrances and FULL exits. Targets enterZERO, and each old capKp exitsKp+E, FULL exactly at the listed ports. Every source/helper integer row is restored and all660 binary VALUE columns retain y+x; all nine zero private copied totals are explicitly restored.',
         'native_hybrid':'Let epsilon_p=1 iff E is not contained in Kp, N=D_Pp and G=D_Kp after the actual port chart. The normalized box at portp is [[I,0],[N^(1-epsilon_p),N^epsilon_p]] times diag(G,G). Every epsilon1 cap lift is paid in the complete profile. The old uniform CLEAN caller cannot be imported without a hybrid operator proof.',
         'COPY_contract':'Each original total at U is now at U+E. Its fresh zero private field is declared at E; the exact nested COPY tariff is dim(U+E)-dim(E), listed for all nine snapshots. Scatter occurs at the genuine common E, source is immutable until literalERASE. This is common-E conjugation of the retained nested COPY interface, not nine free copied fields.',
         'native_query_scope':'Each changed MOVE and copied-total residual has a complete rational projector and explicit GL ADDRESS conjugation of the corresponding coordinate interchange. Finite bad primes are listed. Compatibility with a narrower orthogonal/dyadic recursive query alphabet and scalar route lowering remains a separate admission gate.',
         'owner_gate':'Each physical helper u may be interpreted as logical h=D_E^-1u, because all public dirty dependence cancels. The physical residual D_FULL D_E^-1 is an actual coordinate complement of width8-d with a coordinate-permutation bank route. No executed E entrance query is inherently required. Adding327*d entrance progress is necessary only when preserving the old ZERO logical-dirt identification; chronological paired owner routing remains open.',
         'limits':['No hybrid all-input caller or chronological whole-owner allocation.','No outer moment, rounded-suffix/tape proof or improved conditional exponent.'],
         'controls':{'omitted_inverse_kernel_basis_fails_Z_helpers':True},
         'attribution':'R438 word, copied totals and nested COPY interface are pinned predecessor work. This lane constructs semantic dirty-kernel extraction, common-E paths, paired entrances and complete copied-total native residual charts.'}
    out=json.loads(json.dumps(out));stem=f'OLD-KERNEL-E{d}'
    for suffix,data in[('-WORD.json.gz',canonical),('-GEOMETRY.json.gz',gbytes)]:
        p=HERE/(stem+suffix)
        if write:p.write_bytes(gzip.compress(data,mtime=0))
        else:need(gzip.decompress(p.read_bytes())==data,'saved old kernel artifact differs')
    p=HERE/(stem+'.json')
    if write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==out,'saved old kernel receipt differs')
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--rank',type=int,choices=range(1,8),default=2);ap.add_argument('--write',action='store_true');a=ap.parse_args()
    o=receipt(a.rank,a.write);print(o['status']);print('E',a.rank,'H',o['profile']['H'],'mass',o['profile']['mass'],'copy',o['private_COPY_rank_sum'],'helper widths',o['helper_inventory_by_residual_width'],'targetFULL',o['old_cap_target_lift_count'])

if __name__=='__main__':main()
