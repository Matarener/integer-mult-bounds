#!/usr/bin/env python3
"""Optimize integer signs of the same47 binary quotient gates.

The native rank profile and F2 source code are fixed. This is a new integer
lift, not the already published frozen local word or an admitted precision law.
"""
from pathlib import Path
import gzip
import hashlib
import json
import random
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'recursive'))
import bit_signed_audit as sa
import bit_prune_audit as pa
import bit_cap_copy_local as cap


def score(gates, signs):
    maxima=[]
    endpoints=[]
    for inverse in (False,True):
        rows=[[int(i==j) for j in range(9)] for i in range(9)]
        m=1
        seq=list(zip(gates,signs))
        for (d,s),c in reversed(seq) if inverse else seq:
            c=-c if inverse else c
            rows[d]=[x+c*y for x,y in zip(rows[d],rows[s])]
            m=max(m,sum(map(abs,rows[d])))
        maxima.append(m)
        endpoints.append(max(sum(map(abs,row)) for row in rows))
    return (max(maxima),maxima[0]*maxima[1],sum(maxima),sum(endpoints))


def main():
    packed=(HERE/'BIT-PRUNED-WORD.json.gz').read_bytes()
    cap.need(hashlib.sha256(packed).hexdigest()=='1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870','fixed ancestry')
    program=json.loads(gzip.decompress(packed))
    records=program['records']
    positions=[i for i,r in enumerate(records) if r[0]==1 and r[5]==23]
    pivots=sorted({records[i][j] for i in positions for j in (1,2)})
    index={p:i for i,p in enumerate(pivots)}
    gates=[(index[records[i][1]],index[records[i][2]]) for i in positions]
    cap.need(len(gates)==47 and len(pivots)==9,'quotient alphabet')
    start=[1]*47
    best=(score(gates,start),start)
    rng=random.Random(3605)
    for restart in range(24):
        signs=start[:] if restart==0 else [rng.choice((-1,1)) for _ in start]
        current=score(gates,signs)
        for sweep in range(8):
            changed=False
            order=list(range(47));rng.shuffle(order)
            for i in order:
                signs[i]*=-1
                value=score(gates,signs)
                if value<current:
                    current=value;changed=True
                else:signs[i]*=-1
            if not changed:break
        if current<best[0]:best=(current,signs[:])
    changed=[r[:] for r in records]
    for i,c in zip(positions,best[1]):changed[i][3]=c
    raw=json.loads(gzip.decompress(cap.RAW.read_bytes()))
    keep=[i for i in range(660) if i not in range(471,480)]
    f,fs=pa.execute(raw,keep,changed)
    r,rs=pa.execute(raw,keep,changed,True)
    rt,_=pa.execute(raw,keep,changed,True,f)
    cap.need(rt==sa.identity(651),'new signed roundtrip')
    oldf,_=pa.execute(raw,keep,records)
    oldr,_=pa.execute(raw,keep,records,True)
    cap.need(sa.parity(f)==sa.parity(oldf) and sa.parity(r)==sa.parity(oldr),'same complete binary endpoints')
    for i in range(222,651):cap.need(f[i]==r[i]=={i:1},'new signed helper restoration')
    changed_word=dict(program,format='coded-r429-signed-quotient-variant-v1',records=changed)
    payload=json.dumps(changed_word,sort_keys=True,separators=(',',':')).encode()
    output=gzip.compress(payload,mtime=0)
    (HERE/'BIT-SIGNED-QUOTIENT-WORD.json.gz').write_bytes(output)
    result={'status':'PASS_LOCAL_INTEGER_SIGN_VARIANT_SAME_F2_AND_RANK_NO_PRECISION_ADMISSION',
            'parent_sha256':hashlib.sha256(packed).hexdigest(),
            'word_sha256':hashlib.sha256(output).hexdigest(),
            'word_canonical_sha256':hashlib.sha256(payload).hexdigest(),
            'original_small_score':score(gates,start),'new_small_score':best[0],
            'quotient_signs':best[1],'changed_gates':sum(c==-1 for c in best[1]),
            'forward':fs,'inverse':rs,
            'scope':'47fixedbinaryquotientgates only; all651integer/F2columns andhelpers. Notthepublishedword; no globalprecision/stock/controller/tape or kappa.'}
    (HERE/'SIGNED-QUOTIENT-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
