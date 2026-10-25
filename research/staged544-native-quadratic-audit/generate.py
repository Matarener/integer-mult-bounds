"""Generate finite reference recipes with the pinned predecessor compiler.
Generation is not independent verification. verify.py never imports the compiler.
"""
import json,gzip,sys
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'vendor'))
import clifford_exact as c

def kg(cols):
    G=c.transpose(cols,9);gi=c.inv(G,9);ci=c.transpose(gi,9)
    Q=tuple((1<<i)^sum(c.parity(a&b)<<j for j,b in enumerate(ci))for i,a in enumerate(ci))
    return c.perm(9,G).then(c.diag(9,Q))

def build():
    items={};coverage={}
    def add(d,label):
        key=json.dumps(d,sort_keys=True,separators=(',',':'))
        if key not in items:
            op=c.canonical_frame(9,d['entrance']).adjoint()
            if d['kind']=='warp':
                k=kg(d['G_columns']);op=op.then(k if d['sign']>0 else k.adjoint())
            op=op.then(c.canonical_frame(9,d['terminal']))
            d['recipe']=c.lower_child(op)[0];items[key]=d;coverage[key]=[]
        coverage[key].append(label)
    for tag in ['base','extra']:
        a=json.load(gzip.open(P/'frozen'/('old-WORD-'+tag+'.json.gz')));b=json.load(gzip.open(P/'frozen'/('WORD-'+tag+'.json.gz')))
        for r,terminal in b['helper_final'].items():
            if terminal==a['helper_final'][r]:continue
            for version,w in [('old',a),('new',b)]:
                add(dict(kind='residual',entrance=w['start_extra'].get(r,[]),terminal=w['helper_final'][r]),dict(provider=tag,kind='terminal',helper=int(r),version=version))
        for i,(old,new)in enumerate(zip(a['warps'],b['warps'])):
            if old[2:]==new[2:]:continue
            for version,w in [('old',old),('new',new)]:
                for sign in [1,-1]:
                    add(dict(kind='warp',G_columns=w[2],entrance=w[3] if sign>0 else w[4],terminal=w[4]if sign>0 else w[3],sign=sign),dict(provider=tag,kind='warp',index=i,register=w[1],version=version,sign=sign))
    return {'items':[dict(items[k],coverage=coverage[k])for k in sorted(items)]}
if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('explicit output path required')
    Path(sys.argv[1]).write_text(json.dumps(build(),indent=2)+'\n')
