#!/usr/bin/env python3
"""Eight changed local query returns, exact Gaussian operators including phase."""
import argparse,gzip,hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1];NATIVE=ROOT/'research/p104-native-channel'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def sources():
    pins=json.loads((P/'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage']=='input':need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'native source pin')
    return json.loads(gzip.decompress((NATIVE/'NATIVE-RECIPES.json.gz').read_bytes()))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--generate',action='store_true');args=ap.parse_args()
    cert=sources();word=json.loads((NATIVE/'inputs/LOWRANK-WITNESS.json').read_text());N=module('copy_native_independent',NATIVE/'vendor/native_verify.py')
    drops=[r for r in cert['transports'] if any(word['program'][i][1]=='C' for i in r['events'])]
    need(len(drops)==8,'eight native private drops')
    if args.generate:
        C=module('copy_native_compiler',NATIVE/'vendor/clifford_exact.py');reverses=[]
        for d in drops:
            op=C.canonical_frame(9,tuple(d['new'])).adjoint().then(C.canonical_frame(9,tuple(d['old'])))
            recipe,_=C.lower_child(op);reverses.append({'event':d['events'][0],'recipe':recipe})
        (P/'RETURN-RECIPES.json').write_text(json.dumps(reverses,sort_keys=True,indent=2)+'\n')
    recipes=json.loads((P/'RETURN-RECIPES.json').read_text());by={r['event']:r['recipe'] for r in recipes};need(len(by)==8,'eight unique returns')
    iso=cert['label_isometry'];dual=iso['compressed_dual_gram'];orth=iso['orthonormal_basis_compressed']
    mv=lambda rows,x:sum(((r&x).bit_count()&1)<<i for i,r in enumerate(rows))
    dot=lambda a,b:(a&mv(dual,b)).bit_count()&1
    need(all(dot(a,b)==int(i==j) for i,a in enumerate(orth) for j,b in enumerate(orth)),'isometry basis')
    convert=lambda x:sum(dot(x,v)<<j for j,v in enumerate(orth))
    def span(vs):
        out={0}
        for v in vs:out|={x^v for x in tuple(out)}
        return out
    columns=0
    for d in drops:
        i=d['events'][0];event=word['program'][i];old,new=d['old'],d['new'];reverse=by[i]
        need(event[0:2]==['transport','C'] and event[4]==7,'literal private descent')
        need(span(map(convert,event[2]))==span(old) and span(map(convert,event[3]))==span(new),'physical event binding')
        need(len(old)==8 and len(new)==1 and span(new)<=span(old),'nested eight-to-one')
        need(d['rank']==d['recipe']['rank']==reverse['rank']==7,'both paid positive children rank7')
        forward=N.recipe(d['recipe']);back=N.recipe(reverse)
        expected=N.adjoint(N.frame(old,9))+N.frame(new,9)
        expected_back=N.adjoint(N.frame(new,9))+N.frame(old,9)
        N.equal(forward,expected,'exact descent');N.equal(back,expected_back,'exact return')
        N.equal(forward+back,(),'query restored including global phase')
        for col in range(512):
            need(N.state(forward,col)==N.state(expected,col),'descent Gaussian column')
            need(N.state(back,col)==N.state(expected_back,col),'return Gaussian column')
            columns+=2
    need(columns==8192,'complete columns')
    bad=json.loads(json.dumps(recipes[0]['recipe']));bad['left']['phase']=(bad['left']['phase']+1)%4
    try:N.equal(N.recipe(bad),N.recipe(recipes[0]['recipe']),'phase mutation')
    except (ValueError,AssertionError):pass
    else:raise ValueError('phase control accepted')
    print('PASS_P104_COPY_NATIVE_RETURN rank7=8 gaussian_columns=8192 phase_control=1')
if __name__=='__main__':main()
