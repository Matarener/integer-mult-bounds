#!/usr/bin/env python3
"""Source-preserving R429 bulk with direct nine-total compensation at FULL.

No source code, target precode, private field or terminal gauge is retained.
The full111-target lift is explicit and the complete local mass is zero-loss.
"""
from pathlib import Path
from collections import Counter
import gzip
import hashlib
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import bit_full_targets as b
def need(z,m):
    if not z:raise ValueError(m)
def bits(z):
    while z:
        v=z&-z;yield v.bit_length()-1;z^=v
def main():
    packed=b.INPUT.read_bytes();need(hashlib.sha256(packed).hexdigest()=='1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870','R429 pin')
    base=json.loads(gzip.decompress(packed));raw=json.loads(gzip.decompress(b.RAW.read_bytes()))
    address_projectors=b.cap.address_identities(raw)
    ident=b.cap.identity(8);full_address=b.cap.exchange(ident);new_lift_hashes=[]
    for root in raw['lines']:
        P=[[b.cap.Q(x*y,4)for y in root]for x in root]
        Q=[[ident[i][j]-P[i][j]for j in range(8)]for i in range(8)]
        actual=b.cap.multiply(full_address,b.cap.exchange(Q))
        need(actual==b.cap.exchange(P)and b.cap.rank(P)==1,'actual cap-to-FULL ADDRESS operator is rank1 D_P')
        serial=[[[x.numerator,x.denominator]for x in row]for row in actual]
        new_lift_hashes.append(hashlib.sha256(b.canonical(serial)).hexdigest())
    rows=[1<<i for i in range(660)]
    for phase in('D','A'):
        for _,d,srcs in raw[phase]:
            for s in srcs:rows[d]^=rows[s]
    R=[rows[h]&((1<<111)-1)for h in raw['ret']]
    K=[sum(1<<j for j in js)for js in raw['scatter']]
    need(len(R)==9 and len(K)==111,'actual nine quotient rows')
    correction_rows=[]
    for p,mask in enumerate(K):
        z=0
        for j in bits(mask):z^=R[j]
        need(mask and z>>p&1 and z!=(1<<p),'every actual correction row has own source and a distinct source')
        dim=b.cap.rank(raw['lines'][q]for q in bits(z))
        need(dim==8,'every physical-output correction query needs a FULL source-span in the common-frame gather alphabet')
        correction_rows.append({'physical_target':p,'K_mask':mask,'source_support_size':z.bit_count(),'source_root_span':dim})
    bulk=[r for r in base['records']if r[0]not in(2,3)and r[-1]not in(21,22,23,24,31,32,33)]
    lifts=[[0,d,base['final'][d],1,1,42]for d in range(111,222)]
    correction=[];queries=[]
    for j,row in enumerate(R):
        support=list(bits(row));pivot=support[0];other=support[1:]
        correction.extend([1,pivot,s,1,1,51]for s in other)
        dsts=[p for p,mask in enumerate(K)if mask>>j&1]
        correction.extend([1,111+p,pivot,1,1,52]for p in dsts)
        correction.extend([1,pivot,s,-1,1,53]for s in reversed(other))
        queries.append({'R_index':j,'pivot':pivot,'source_support':support,'target_support':dsts})
    records=bulk+lifts+correction;adds=sum(r[0]==1 for r in records)
    outputs=[];receipts=[]
    for back in(False,True):
        out,rec=b.replay(raw,base,records,back,private_expected=0,add_count=adds)
        for p in range(111):need(out[p]=={p:1},'source exactZ identity')
        for p in range(222,651):need(out[p]=={p:1},'all429 arbitrary helper dirt exactZ identity')
        expected=[1<<p for p in range(651)]+[0]
        for p in range(111):expected[111+p]^=1<<p
        need(b.scalar.parity(out)==expected,'all651 F2 clean-shear columns')
        for p in range(111,222):
            need(out[p].get(p)==1 and all(j<111 or j==p or j>=222 for j in out[p]),'old target y exactZ identity')
            need(all(not(c&1)for j,c in out[p].items()if j>=222),'target integer dirty leakage even')
        outputs.append(out);receipts.append(rec)
    inv,_=b.replay(raw,base,records,True,outputs[0],private_expected=0,add_count=adds)
    need(inv==[{i:1}for i in range(651)]+[{}],'literal inverse roundtrip every integer input column')
    missing=next(i for i,r in enumerate(records)if r[-1]==52)
    corrupted,_=b.replay(raw,base,records[:missing]+records[missing+1:],private_expected=0,add_count=adds-1)
    need(b.scalar.parity(corrupted)!=b.scalar.parity(outputs[0]),'missing actual compensation scatter rejected')
    bad=[r[:]for r in records];which=next(i for i,r in enumerate(bad)if r[-1]==53);bad[which][3]*=-1
    corrupted,_=b.replay(raw,base,bad,private_expected=0,add_count=adds)
    need(corrupted[:111]!=outputs[0][:111]and b.scalar.parity(corrupted)==b.scalar.parity(outputs[0]),'wrong integer unprepare sign rejected while parity unchanged')
    which=next(i for i,r in enumerate(records)if r[0]==0 and r[1]==111 and r[-1]==42)
    try:b.replay(raw,base,records[:which]+records[which+1:],private_expected=0,add_count=adds)
    except ValueError as e:missing_lift=str(e)
    else:raise ValueError('missing target-FULL lift escaped native frame checks')
    program=dict(base);program['records']=records;program['final']=base['final'][:]
    for p in range(111,222):program['final'][p]=1
    program['private_register']=None;program['format']='R429-full-nine-total-compensation-no-source-code-v1'
    body=b.canonical(program);path=HERE/'BIT-FULL-COMPENSATION-WORD.json.gz';path.write_bytes(gzip.compress(body,mtime=0))
    out={'status':'PASS_R429_FULL_NINE_TOTAL_COMPENSATION_NO_SOURCE_CODE_NO_PRIVATE',
      'sources':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in(b.INPUT,b.RAW,HERE/'bit_full_targets.py',Path(__file__),b.OLD/'recursive/bit_cap_copy_local.py',b.OLD/'recursive/bit_signed_audit.py')},
      'word_gzip_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'word_canonical_sha256':hashlib.sha256(body).hexdigest(),
      'R':R,'K':K,'queries':queries,'forward':receipts[0],'literal_inverse':receipts[1],
      'all111_physical_correction_rows':correction_rows,
      'all_arbitrary_integer_columns':651,'helpers_restored_over_Z':429,'private_fields':0,
      'actual_address_projectors':address_projectors,'exact_ADDRESS_identity_columns':3552,
      'new_target_lift_ADDRESS_sha256':new_lift_hashes,'new_target_lift_ADDRESS_columns':1776,
      'executed_controls':{'missing_one_actual_scatter_changes_F2_endpoint':True,'wrong_unprepare_changes_Z_source_but_not_F2':True,'omitted_target_lift_rejected':missing_lift},
      'new_target_rank1_lifts':111,'source_codes':0,'scalar_ADDs':adds,'rank_mass':5097,'native_progress':5097,'private_excess':0,
      'endpoint':'Source x and429helpers unchanged exactly overZ. Target y unchanged exactly; target updatex modulo2; helper targetleakageeven. Both data banks atFULL. Exact literal integer inverse returns all inputs.',
      'physical_block':'For arbitrary physical inputs, raw F=[[S,0],[S,T]], S=F8 D_P native7,T=F8 native8. An extra111 commonFULL ADDs diagonalizes toS/T; those ADDs are not included in the emitted shear word.',
      'allsize_lift':'Every scalar ADD is at actual commonZERO or commonFULL; nine pure source-pivot totals are prepared and unprepared atFULL without retained snapshots. Actual native MOVE frames and containment are replayed on651 ordinaryroles. AllSIZE rounded/tape implementation remains a separate obligation.',
      'global_accounting':'Direct n=L diagonal-call topology hasD0, not LN. The111 rank1 target lifts percall are counted here and cannot be omitted from an old common-axis invoice.',
      'partial_target_gate':'All111Krows are nonzero. Every KR row includes its own source and at least one other source, and its actual E8 source-line span has rank8. For this physical-output gather alphabet, no row can be prepared at target cap K_p, which omits own P_p. A FULL pure-query pivot needs one rank1 immutable COPY to a cap target, or a source descent+return costs2. Those bills do not beat the one target lift. A changed multi-output factor/native source-consumption word is not excluded by this census.',
      'remaining':['Actual changed global caller, chronological owners and complete moment.','New rounded precision/suffix-error and physical source/tape bill.','No positive kappa or new selected bound.'],
      'no_new_kappa':True}
    (HERE/'BIT-FULL-COMPENSATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']);print('651cols,429helperZ restoration,0private,9totals; ADD',adds,'mass5097')
if __name__=='__main__':main()
