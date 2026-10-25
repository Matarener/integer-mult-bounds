#!/usr/bin/env python3
"""Actual R429 target-precode/full-target/source-decode local construction.

Exact signed integer and F2 audits of all651 input columns with full native
COPY/ERASE lifecycles. No whole caller or changed idle stock is asserted.
"""
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OLD=Path('/Users/ross/git/math/.research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier')
INPUT=OLD/'root-pruned-code/BIT-PRUNED-WORD.json.gz'
RAW=Path('/Users/ross/git/math/integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz')
sys.path.insert(0,str(OLD/'recursive'))
import bit_cap_copy_local as cap
import bit_signed_audit as scalar
def need(b,m):
    if not b:raise ValueError(m)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()

def replay(raw,base,records,back=False,initial=None,private_expected=3,add_count=17720):
    n=651;start=base['final'][:]if back else base['start'][:]
    if back:
        for p in range(111,222):start[p]=1
    frames=start+[None]
    rows=[{i:1}for i in range(n)]+[{}]if initial is None else [r.copy()for r in initial]
    dims=[cap.rank(raw['lines'][j]for j in f)for f in raw['frames']]
    masks=[sum(1<<j for j in f)for f in raw['frames']]
    live=None;profile=Counter();counts=Counter();prefix=1;copies=0
    for op,d,s,c,f,phase in reversed(records)if back else records:
        counts[op]+=1
        if op==0:
            old,new=(c,s)if back else(s,c)
            lo,hi=(new,old)if back else(old,new)
            need(frames[d]==old and not masks[lo]&~masks[hi]and dims[hi]-dims[lo]==f>0,'native MOVE frame and exact rank')
            frames[d]=new;profile[f]+=1
        elif op==1:
            need(d!=s and d<n and frames[d]==frames[s]==f and d!=live,'native common-frame ADD / immutable snapshot')
            rows[d]=scalar.add(rows[d],rows[s],-c if back else c)
            prefix=max(prefix,sum(abs(z)for z in rows[d].values()))
        elif op==(3 if back else 2):
            need(live is None and s==n and not rows[n]and frames[n]is None,'fresh private field')
            need(d<111 and frames[d]==c==1 and not masks[f]&~masks[c]and dims[c]-dims[f]==1,'actual source rank1 cap COPY')
            rows[n]=rows[d].copy();frames[n]=f;live=d;profile[1]+=1;copies+=1
        else:
            need(op==(2 if back else 3)and live==d and s==n and rows[n]==rows[d]and frames[d]==c and frames[n]==f,'immutable snapshot ERASE')
            rows[n]={};frames[n]=None;live=None
    end=base['start'][:]if back else base['final'][:]
    if not back:
        for p in range(111,222):end[p]=1
    need(frames==end+[None]and live is None and not rows[n]and copies==private_expected,'complete native/private endpoint')
    need(profile==Counter({1:1406+private_expected,2:1342,3:79,4:44,5:93,6:11,7:9}),'complete changed rank histogram')
    need(counts==Counter({0:2984,1:add_count,2:private_expected,3:private_expected}),'complete changed record counts')
    return rows,{'prefix_row_l1':prefix,'profile':dict(sorted(profile.items())),'rank_mass':sum(k*v for k,v in profile.items()),'records':dict(sorted(counts.items())),'copies':copies}

def main():
    packed=INPUT.read_bytes();need(hashlib.sha256(packed).hexdigest()=='1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870','frozen R429 word')
    base=json.loads(gzip.decompress(packed));rawbytes=RAW.read_bytes()
    need(hashlib.sha256(rawbytes).hexdigest()=='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','native geometry pin')
    raw=json.loads(gzip.decompress(rawbytes))
    code=[r for r in base['records']if r[0]==1 and r[-1]in(21,22,23,24)]
    need(len(code)==1499 and all(d<111 and s<111 and f==1 for op,d,s,c,f,p in code),'literal common-FULL source code')
    need(all(f==0 for f in base['start'][111:222]),'all target precode inputs are at ZERO')
    pre=[[1,d+111,s+111,c,0,41]for _,d,s,c,f,p in code]
    moves=[[0,d,base['final'][d],1,1,42]for d in range(111,222)]
    post=[]
    for offset,phase in((0,43),(111,44)):
        post.extend([1,d+offset,s+offset,-c,1,phase]for _,d,s,c,f,p in reversed(code))
    records=pre+base['records']+moves+post
    outputs=[];receipts=[]
    identity=[{i:1}for i in range(651)]+[{}]
    for back in(False,True):
        rows,receipt=replay(raw,base,records,back)
        for p in range(111):need(rows[p]=={p:1},'exact integer source restoration')
        for p in range(222,651):need(rows[p]=={p:1},'all429 arbitrary helpers restored overZ')
        expected=[1<<p for p in range(651)]+[0]
        for p in range(111):expected[111+p]^=1<<p
        need(scalar.parity(rows)==expected,'all651 F2 clean shear columns')
        for p in range(111,222):
            need(rows[p].get(p)==1 and all(j<111 or j==p or j>=222 for j in rows[p]),'integer target arbitrary old y restored exactly')
            need(all(not(z&1)for j,z in rows[p].items()if j>=222),'integer target dirty leakage is even')
        outputs.append(rows);receipts.append(receipt)
    closed,_=replay(raw,base,records,True,outputs[0]);need(closed==identity,'literal inverse roundtrip all651 integer columns')
    # Omit the target precode but retain the inverse target output code.
    # An independent scalar propagation of A on y certifies the necessary
    # orientation. A^-1 precode would leave A^-2 y rather than y.
    arows=[{i:1}for i in range(111)]
    for _,d,s,c,_,_ in code:arows[d]=scalar.add(arows[d],arows[s],c)
    need(scalar.parity(arows)!=[1<<p for p in range(111)],'omitted-precode mutation is nontrivial')
    program=dict(base);program['records']=records;program['final']=base['final'][:]
    for p in range(111,222):program['final'][p]=1
    program['format']='R429-target-precode-A-both-postcode-Ainv-FULL-targets-v1'
    body=canonical(program);wp=HERE/'BIT-FULL-TARGET-WORD.json.gz';wp.write_bytes(gzip.compress(body,mtime=0))
    out={'status':'PASS_R429_PRECODE_TARGET_A_POSTCODE_BOTH_AINV_ALL_FULL_TARGETS',
      'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
      'sources':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in(INPUT,RAW,Path(__file__),OLD/'recursive/bit_signed_audit.py',OLD/'recursive/bit_cap_copy_local.py')},
      'word_gzip_sha256':hashlib.sha256(wp.read_bytes()).hexdigest(),'word_canonical_sha256':hashlib.sha256(body).hexdigest(),
      'forward':receipts[0],'literal_inverse':receipts[1],
      'all_integer_columns':651,'all_arbitrary_helpers_restored':429,'max_private_live':1,
      'boundary':'At scalar frames: pre-A on arbitrary target y, old (Ax,y+Ax), target caps→FULL, literal A_Z^-1 on both FULL data banks. Source exactly x overZ; target y+x modulo2 with even helper leakage. Literal inverse restores every integer input.',
      'native_widths':{'source_entrance':1,'source_exit':8,'target_entrance':0,'target_exit':8,'source_residual':7,'target_residual':8,'helpers_residual':8},
      'local_raw_operators':'With D_P ordinary ADDRESS interchange, source S=F8 D_P, target T=F8, cross S. On a common seed p and fresh7 G_s: F=G_s[[1,0],[1,N]], B=G_s[[N,-1],[0,1]], N=D_p, N²=I.',
      'local_mass':5100,'useful_native_coverage':111*15+429*8,'private_mass_excess':3,
      'new_scalar_ADDs':4497,'new_rank1_children':111,'source_code_ADDs':1499,
      'chart_scope':'Target ZERO and source/target FULL are invariant under the actual local orthogonal rho charts; target A atZERO and both A^-1 atFULL use the same paid rho-adapted code as the original source. A global past factor supported outside the active8 commutes these rho adapters. This is a local/cut conjugation statement, not a global matched-bank caller.',
      'controls':['omitting target pre-A leaves a nonidentity A^-1 on arbitrary old y','using pre-A^-1 instead ofA would generally leave A^-2 on y','all COPY sources immutable through ERASE','all651 integer inverse roundtrip'],
      'remaining':['Construct a whole caller over N²=I with all common-axis N events and actual parent endpoint charged. Standalone N has native rank1 at either typed cut, not rankzero.','New target progress may change arity, idle windows, helper capacity and complete moment. Cprivate3 alone does not transfer the old deficit.','17720 exact signed ADDs require a new full precision/suffix-error and physical/tape invoice.','No complete global supplier or new kappa is asserted.'],
      'no_new_kappa':True}
    (HERE/'BIT-FULL-TARGET.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']);print('651 integer/F2 columns,429 helpers,3 private copies; mass5100; ADD17720; Cprivate3')

if __name__=='__main__':main()
