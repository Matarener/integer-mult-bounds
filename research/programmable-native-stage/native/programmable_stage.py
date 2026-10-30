#!/usr/bin/env python3
"""Literal rational-amplitude specialization of pinned whole-K native cube."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json
HERE=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise ValueError(msg)
def source():
    pins=json.loads((HERE/'SOURCE-PINS.json').read_bytes())
    for name,digest in pins['files'].items():
        need(sha256((HERE/'vendor'/name).read_bytes()).hexdigest()==digest,'source pin '+name)
    return json.loads(gzip.decompress((HERE/'vendor/K-PROGRAM.json.gz').read_bytes()))
def specialize(payload,lam):
    result=json.loads(json.dumps(payload));out=[]
    for event in result['program']:
        if event[0]=='ADD':
            q=lam*F(event[5],event[6])
            if not q:continue
            event[5:7]=[q.numerator,q.denominator]
        out.append(event)
    result['program']=out
    result['schema']='programmable-whole-K-rational-amplitude/v1'
    result['amplitude']=[lam.numerator,lam.denominator]
    # Upstream endpoint_rows describe lambda=1; never retain stale metadata.
    for row in result['logical_endpoint_rows']['reader_rows'].values():
        for term in row:
            if term[0]=='X':
                q=lam*F(term[2],term[3]);term[2:4]=[q.numerator,q.denominator]
    result['literal_scalar_K_rows']={r:[[s,(lam*F(a,b)).numerator,(lam*F(a,b)).denominator]for s,a,b in row]for r,row in result['literal_scalar_K_rows'].items()}
    return result

def verify(payload,lam):
    ports=payload['port_order'];charts={('X',p):'line:'+str(p)for p in ports}
    charts.update({('Y',p):'ground'for p in ports})
    rows={('X',p):{('X',p):F(1)}for p in ports};rows.update({('Y',p):{('Y',p):F(1)}for p in ports})
    paid=Counter();adds=0
    for e in payload['program']:
        if e[0]=='MONOMIAL':continue # Exact inherited monomial wrappers change physical frames, not the geometric u,v columns.
        if e[0]=='PAID_PATH':
            _,role,p,old,target,record=e
            need(charts[role,p]==old,'actual path chronology')
            charts[role,p]=target;paid[record['rank']]+=1
        elif e[0]=='ADD':
            _,dr,d,sr,s,a,b,chart=e
            need(dr=='Y'and sr=='X','source bank never modified')
            need(charts[dr,d]==charts[sr,s]==chart,'literal equal-frame ADD')
            q=F(a,b)
            for key,v in rows[sr,s].items():
                value=rows[dr,d].get(key,F(0))+q*v
                if value:rows[dr,d][key]=value
                else:rows[dr,d].pop(key,None)
            adds+=1
        else:raise ValueError('unknown opcode')
    need(paid=={8:512,9:512,15:512,16:512},'complete unchanged paid histogram')
    for p in ports:
        need(rows['X',p]=={('X',p):F(1)},'every independent source retained')
        expected={('Y',p):F(1)}
        for s,a,b in payload['literal_scalar_K_rows'][str(p)]:
            if a:expected['X',s]=F(a,b)
        need(rows['Y',p]==expected,'every original independent column')
        declared={(role,s):F(a,b)for role,s,a,b in payload['logical_endpoint_rows']['reader_rows'][str(p)]if a}
        need(declared==expected,'serialized endpoints match actual ADD rows')
    need(adds==(38912 if lam else 0),'actual amplitude ADD count')
    return {'amplitude':[lam.numerator,lam.denominator],'paid':dict(sorted(paid.items())),'ADD':adds,'independent_columns':1024}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--amplitude');ap.add_argument('--output');a=ap.parse_args()
    original=source();amplitudes=[F(a.amplitude)]if a.amplitude is not None else [F(0),F(1),F(-1),F(2),F(1,2)]
    records=[]
    for lam in amplitudes:
        payload=specialize(original,lam);records.append(verify(payload,lam))
        if a.output:
            need(len(amplitudes)==1,'output requires explicit amplitude')
            target=Path(a.output);need(not target.exists(),'refuse overwrite output')
            encoded=(json.dumps(payload,sort_keys=True,separators=(',',':'))+'\n').encode()
            target.write_bytes(gzip.compress(encoded,mtime=0))
    print(json.dumps({'status':'PASS','native_instances':records,'inherited_phase_scope':'vendor/PROOF.md','new_kappa':False},sort_keys=True))
if __name__=='__main__':main()
