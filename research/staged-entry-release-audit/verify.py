"""Source-bound rank-two staging defect and projected cleanup audit."""
import gzip,hashlib,json,sys
from pathlib import Path
from fractions import Fraction as Q
import algebra as A
P=Path(__file__).resolve().parent

def authenticate(raw,pin,name):
    A.need(hashlib.sha256(raw).hexdigest()==pin["sha256"],"input SHA256 "+name)
    A.need(hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()==pin["git_blob"],"input blob "+name)

def load():
    pins=json.loads((P/'PINS.json').read_text());out={}
    A.need(set(pins)=={f'{kind}-{tag}.json.gz' for kind in ('OLD','NEW') for tag in ('base','extra')},'pin inventory')
    for name,pin in pins.items():
        raw=(P/'inputs'/name).read_bytes()
        authenticate(raw,pin,name)
        out[name]=json.loads(gzip.decompress(raw))
    return out

def expected(mask):
    d={}
    if mask&1:d.update({565:{((),600):Q(1,2)},602:{((),600):Q(-1)}})
    for bit,h in ((2,608),(4,609)):
        if mask&bit:
            d.setdefault(417,{})[(),h]=Q(1,2)
            d.setdefault(610,{})[(),h]=Q(-1)
    return d

def reject(fn,label):
    try:fn()
    except ValueError as e:return {'name':label,'reason':str(e)}
    raise ValueError('accepted negative control '+label)

def audit(words):
    results={};controls=[]
    for tag in ('base','extra'):
        o,n=[words[k+'-'+tag+'.json.gz'] for k in ('OLD','NEW')]
        variants,deleted,releases=A.plans(o,n)
        for w in (o,n):A.need(A.inverse_tail(w,A.body(w))==A.section(w,'cleanup'),'literal cleanup differs')
        boundaries={};summaries=[]
        for mask,B in variants.items():
            b,end=A.run(n,B);A.endpoint(end);boundaries[mask]=b
            delta=A.difference(b,boundaries[0]);A.need(delta==expected(mask),'sparse boundary defect '+tag+':'+str(mask))
            # Every restored helper is unchanged before its private-buffer cleanup.
            for r in map(int,n['helper_final']):A.need(b[r]=={((),r):Q(1)},'dirty helper boundary')
            restored=set(map(int,n['helper_final']))
            A.need(all(not any(v in restored for _,v in row) for r,row in b.items() if r<704 and r not in restored),'restored helper leak at boundary')
            summaries.append({'subset_mask':mask,'delta':A.serial(delta),'endpoint_registers':len(end),'private_buffers':len(n['helper_final'])})
        # Recompute every linear combination, rather than trusting singleton signatures.
        for mask in range(8):
            total={r:dict(v) for r,v in boundaries[0].items()}
            for k in (1,2,4):
                if mask&k:
                    for r,row in A.difference(boundaries[k],boundaries[0]).items():total[r]=A.plus(total[r],row)
            A.need(total==boundaries[mask],'nonzero subset cross term')
        for release in releases:
            index=variants[7].index(release)
            for defect in ('omit','flip'):
                bad=list(variants[7])
                if defect=='omit':bad.pop(index)
                else:bad[index]=release[:-1]+(-release[-1],)
                # Tail regenerated from bad word: rejection cannot be stale inverse.
                controls.append(reject(lambda:A.endpoint(A.run(n,bad)[1]),tag+':'+defect+':'+str(release[1:3])))
        pins=json.loads((P/'PINS.json').read_text())
        name='NEW-'+tag+'.json.gz';raw=(P/'inputs'/name).read_bytes()
        damaged=raw[:10]+bytes([raw[10]^1])+raw[11:]
        controls.append(reject(lambda:authenticate(damaged,pins[name],name),'corrupt_source:'+tag))
        swapped=(P/'inputs'/('NEW-'+('extra' if tag=='base' else 'base')+'.json.gz')).read_bytes()
        controls.append(reject(lambda:authenticate(swapped,pins[name],name),'swapped_provider:'+tag))
        results[tag]={'subsets':summaries,'deleted_reads':len(deleted),'releases':[[*r[:3],str(r[3])] for r in releases],
                      'native_interfaces_unchanged':len(n['warps']),'rank_of_combined_defect':2}
    return {'status':'PASS_STAGED_ENTRY_RANK_TWO_DEFECT','providers':results,'rejected_controls':controls,
            'scope':'Exact finite free-group linear identity, eight algebraic subsets/provider; partial subsets have no frame/owner admission.'}

def main():
    result=audit(load());target=P/'CERTIFICATE.json'
    if '--write' in sys.argv:target.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:A.need(result==json.loads(target.read_text()),'certificate mismatch')
    print(result['status']+' providers=2 subsets=16 full_state_blocks=723 rank=2 controls='+str(len(result['rejected_controls'])))
if __name__=='__main__':main()
