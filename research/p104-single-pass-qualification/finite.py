"""Pre-construction real-backend feasibility; all checks survive python -O."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
from source import baseline,require
from observe import Observation
controls=[]
def rejects(label, fn):
    try:fn()
    except ValueError:controls.append(label)
    else:raise ValueError('accepted '+label)
with baseline() as p:
    spec=importlib.util.spec_from_file_location('finite_source',p/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    with v.source() as (_,original,ref):
        integer=v.load('finite_integer',p/'integer.py')
        word=dict(public=1,owned_fields=1,initial=[0],final=[0],frames=[[]],live=[],program=[['INIT',1,0],['COPY',1,0,1,0],['SCALE',1,'1/2',0],['SCALE',1,2,0],['CLEAR',1,0]])
        for backend in (ref,integer.Engine(ref)):
            o=Observation(backend,ref.digest,word)
            ideal,weights=o.ideal(word);trace,witness=o.error_trace(word,weights,set(ideal['counts']))
            o.finish();got=o.take(word)
            require(got['ideal']==backend.ideal(word),'fresh finite ideal')
            require(got['error_trace']==backend.error_trace(word,weights,set(ideal['counts'])),'fresh finite trace/witness')
            rejects('one-use',lambda:o.take(word));rejects('closed-call',lambda:o.ideal(word))
            o=Observation(backend,ref.digest,word);rejects('missing',o.finish)
            ideal,weights=o.ideal(word)
            rejects('duplicate',lambda:o.ideal(word))
            changed=deepcopy(weights);changed[0]=(99,1)
            rejects('changed-weights',lambda:o.error_trace(word,changed,set(ideal['counts'])))
            rejects('changed-rounding',lambda:o.error_trace(word,weights,{'ADD'}))
            value=o.error_trace(word,weights,set(ideal['counts']));value[0]['sites']=-1
            o.finish();mutated=deepcopy(word);mutated['program'][2][-2]='1/4'
            rejects('changed-word',lambda:o.take(mutated))
            require(o.take(word)['error_trace'][0]['sites']>=0,'snapshot alias isolation')
            bad=deepcopy(word);bad['program'][1][2]=1
            o=Observation(backend,ref.digest,word);o.ideal(word)
            rejects('original-malformed-rejection',lambda:o.ideal(bad))
            o.error_trace(word,weights,set(ideal['counts']));o.finish();o.take(word)
            failed=Observation(backend,ref.digest,bad)
            rejects('propagated-exception',lambda:failed.ideal(bad));rejects('failed-finish',failed.finish);rejects('failed-take',lambda:failed.take(bad))
            fresh=Observation(backend,ref.digest,word);rejects('fresh-context-not-previous-pass',lambda:fresh.take(word))
            fresh.abort();rejects('aborted-take',lambda:fresh.take(word))
        class Mutating:
            def ideal(self,w):w['public']=9;return ({},[])
        changing=deepcopy(word);o=Observation(Mutating(),ref.digest,changing)
        rejects('input-mutation',lambda:o.ideal(changing))
        require(len(controls)==27,'complete finite control census')
print(json.dumps({'status':'PASS_FINITE_FEASIBILITY_ONLY','events':5,'backends':2,'controls':controls},sort_keys=True))
