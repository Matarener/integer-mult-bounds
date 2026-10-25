#!/usr/bin/env python3
"""Compose the five exact partial releases and recount literal native paths.

No native restoration or kappa improvement is asserted. Apache-2.0;
substantial OpenAI assistance and retained PR3734 source credit.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import gzip,json
from pathlib import Path
import sys

from retime_return import read
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'entry-retiming'))
import complete_candidate as c

SPECS=[
    dict(h=484,native=482,read=33,cut=564,frame=[384,51],release={616:Q(-1),620:Q(-1,2)}),
    dict(h=508,native=503,read=37,cut=616,frame=[384,30],release={632:Q(-1),636:Q(-1,2)}),
    dict(h=532,native=526,read=41,cut=666,frame=[384,30],release={648:Q(1,2),652:Q(-1,2)}),
    dict(h=556,native=550,read=44,cut=250,frame=[384,51],release={664:Q(1,2),668:Q(-1,2)}),
    dict(h=584,native=578,read=47,cut=748,frame=[384,51],release={616:Q(1),618:Q(-1)}),
]


def compose(source,mask):
    w=deepcopy(source)
    specs=[s for i,s in enumerate(SPECS) if mask>>i&1]
    insert={}
    for s in specs:
        h=s['h'];w['start_extra'][str(h)]=s['frame']
        e=w['B'][s['read']]
        assert e[0]=='add' and e[2]==h
        w['B'][s['read']]=['scale',e[1],1,1,e[-1]]
        insert.setdefault(s['cut'],[]).extend(
            ['add',r,h,q.numerator,q.denominator,s['frame']]
            for r,q in sorted(s['release'].items()))
    w['B']=[e for p in range(len(w['B'])+1)
            for e in insert.get(p,[])+([w['B'][p]] if p<len(w['B']) else [])]
    for e in w['warps']:
        e[0]+=sum(len(gates) for pos,gates in insert.items() if pos<=e[0])
    pp,wi=c.profile(w)
    w['report']['local_profile']=pp;w['report']['width_inventory']=wi
    for s in specs:
        expected={s['h']:{():Q(1)}}
        expected.update({r:{():q} for r,q in s['release'].items()})
        assert c.column(w,s['h'])==expected
    return w,pp,wi,specs


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--followup',type=Path,required=True)
    ap.add_argument('--out',type=Path,default=HERE/'combined-subsets')
    ap.add_argument('--emit-mask',type=int)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    sources={}
    for tag in ('base','extra'):
        path=a.followup/f'artifact/live-source/research/staged544-producer-return/words/BORROW-WORD-43{tag}.json.gz'
        sources[tag]=(read(path),sha256(path.read_bytes()).hexdigest())
    results=[]
    for mask in range(1,32):
        variants={}
        for tag,(source,pin) in sources.items():
            w,pp,wi,specs=compose(source,mask)
            payload=json.dumps(w,sort_keys=True,separators=(',',':')).encode()
            variants[tag]=dict(source_sha256=pin,word_payload_sha256=sha256(payload).hexdigest(),
                local_profile=pp,width_inventory=wi,checked_arbitrary_input_columns=[s['h'] for s in specs],
                protected_outputs_unchanged=203,owned_zero_residuals=0)
            if tag=='extra':
                assert variants['base']['local_profile']==pp
                assert variants['base']['width_inventory']==wi
            if a.emit_mask==mask:
                path=a.out/f'COMBINED-{mask}-{tag}.json.gz'
                path.write_bytes(gzip.compress(payload,mtime=0));variants[tag]['word']=path.name
        results.append(dict(mask=mask,helpers=[s['h'] for s in specs],
            native_helpers=[s['native'] for s in specs],width_decrements={str(s['native']):1 for s in specs},
            local_profile=pp,width_inventory=wi,local_rank_mass=sum(r*n for r,n in pp.items()),
            providers=variants,completed_consumer=False,
            obligations=['Restore the displayed FULL donor dirt from HPE-ended input helpers using a literal native word.','Charge completion and replay the complete physical owner allocation before claiming kappa.']))
    result=dict(status='PASS_31_EXACT_COMPOSED_PARTIAL_WORDS_BOTH_PROVIDERS',specs=[dict(s,release={str(r):str(q) for r,q in s['release'].items()}) for s in SPECS],candidates=results,completed_consumers=0)
    (a.out/'COMBINED-SUBSETS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status=result['status'],cases=len(results),receipt=str(a.out/'COMBINED-SUBSETS.json'))))


if __name__=='__main__':main()
