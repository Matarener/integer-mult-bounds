"""Build exact rejection witnesses. Verification does not import this file.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import gzip
import hashlib
import json
from pathlib import Path
import time
import nc_star as N
import search_orders as S


def main():
    N.equations=S.pair_equations
    records=[];counts={2:0,3:0};maximum=0;start=time.monotonic()
    for index,order in enumerate(S.orders()):
        result=N.certificate(3,order,2)
        if 'one' not in result['certificates']:result=N.certificate(3,order,3)
        if 'one' not in result['certificates']:raise ValueError(('Unproved order',order))
        witness=result['certificates']['one'];degree=result['degree']
        records.append([degree,witness]);counts[degree]+=1;maximum=max(maximum,len(witness))
        if (index+1)%10000==0:print(index+1,round(time.monotonic()-start,2),flush=True)
    raw=(json.dumps({'schema':1,'order_rule':'search_orders.orders; first good occurrences 0,1,2','witnesses':records},separators=(',',':'))+'\n').encode()
    payload=gzip.compress(raw,compresslevel=9,mtime=0)
    folder=Path(__file__).resolve().parent
    (folder/'ORDER-CERTIFICATES.json.gz').write_bytes(payload)
    summary={'orders':len(records),'degree_counts':counts,'largest_witness_terms':maximum,'uncompressed_bytes':len(raw),'compressed_bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()}
    (folder/'CERTIFICATE-SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
