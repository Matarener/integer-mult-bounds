"""Exact source-word/factory proof controls; optional actual recursive replay."""
import argparse
from dataclasses import replace
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
PHYSICAL='research/selected-bit-physical-caller'


def need(ok, why):
    if not ok: raise ValueError(why)


def authenticate():
    rows=json.loads((HERE/'SOURCES.json').read_text())['files']
    pins={r['path']:r['sha256'] for r in rows if r['usage']=='input'}
    for path,digest in pins.items():
        need(sha256((ROOT/path).read_bytes()).hexdigest()==digest,'source hash: '+path)
    return pins


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def rejected(action, text):
    try: action()
    except (ValueError,RuntimeError) as error:
        need(text in str(error),'wrong rejection: '+str(error));return
    raise ValueError('mutation survived: '+text)


def typed(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))


def word_checks(prior,regional,source,digest):
    import macro_code
    from residual_blocks import Cursor
    index=regional.itinerary.PlanIndex
    result=[]
    for replicas in (1,2,8):
        with prior.fixture(replicas=replicas) as (topology,binding,*_):
            for mode in (0,1):
                transcript=[]
                class Record:
                    def residual(self,*args):
                        definition=binding.residual(*args)
                        transcript.append((args,definition))
                        return definition
                original=macro_code.compile_node(topology,Record(),mode)
                calls=[]
                class Replay:
                    def residual(self,*args):
                        need(len(calls)<len(transcript),'extra factory call')
                        expected,definition=transcript[len(calls)]
                        need(args==expected,'factory order/arguments')
                        calls.append(args);return definition
                builds=[]
                build=index.build
                def counted(plan):
                    builds.append(id(plan));return build(plan)
                emit=regional.compiler(macro_code,source,digest)
                before_namespace=dict(macro_code.__dict__)
                # Compile without ever enumerating blocks or rescanning a plan.
                with patch.object(Cursor,'__init__',side_effect=RuntimeError('Cursor constructed')), \
                     patch.object(Cursor,'take',side_effect=RuntimeError('Cursor enumerated')), \
                     patch.object(index,'validate',side_effect=RuntimeError('plan rescanned')), \
                     patch.object(index,'build',side_effect=counted):
                    direct=emit(topology,Replay(),mode)
                need(len(calls)==len(transcript),'omitted factory call')
                need(len(builds)==len(set(id(d.plan) for _,d in transcript)),'not one scan per plan')
                need(all(macro_code.__dict__.get(k) is v for k,v in before_namespace.items()),'source namespace mutation')
                need(len(original.operations)==len(direct.operations),'PC length')
                for pc,wanted in enumerate(original.operations):
                    actual=direct.operations[pc]
                    need(actual==wanted,'pointwise source word')
                    if wanted[0]=='block':need(actual[1] is wanted[1],'block identity')
                    if wanted[0] in ('residual_begin','residual_end'):
                        need(actual[2] is wanted[2],'boundary identity')
                # A per-append observer must still receive every original tuple.
                calls.clear();observed=[]
                observable=regional.compiler(macro_code,source,digest,observed.append)(topology,Replay(),mode)
                need(observed==list(original.operations),'observer expansion')
                need(tuple(observable.operations)==original.operations,'observer PC word')
                counts=direct.operations.census()
                counts.update(replicas=replicas,mode=mode,factory_calls=len(calls),plan_builds=len(builds),
                              direct_cursor_calls=0,compile_plan_rescans=0,observed_appends=len(observed))
                result.append(counts)
    return result


def controls(prior,regional,source,digest):
    import macro_code
    from macro_code import Residual
    from plan import Plan,Command,Reference
    from residual_blocks import Cursor
    from itertools import product
    cases=blocks=0
    for width in range(5):
        for kinds in product(('add','sign','child'),repeat=width):
            plan=Plan(2,1,False,tuple(Command(k,0,1,Reference('unit')) for k in kinds))
            definition=Residual(0,plan,0,True,((1,0),(0,1)))
            cursor=Cursor(plan);wanted=[]
            while not cursor.done:wanted.append(cursor.take())
            sink=regional.RegionalSink([('node',)])
            sink.append(('residual_begin','idle',definition));sink.append_run(definition)
            sink.append(('residual_end','idle',definition));word=sink.finish()
            need([op[2] for op in word if op[0]=='block']==wanted,'independent Cursor grammar')
            cases+=1;blocks+=len(wanted)
    plan=Plan(2,1,True,())
    for axis in (None,0):
        definition=Residual(0,plan,0,True,((1,0),(0,1)),axis)
        sink=regional.RegionalSink([]);sink.append(('residual_begin','idle',definition));sink.append_run(definition)
        sink.append(('residual_end','idle',definition));word=sink.finish()
        wanted=[('axis',0,0)] if axis is not None else [('forward',0,0),('good',1,0),('backward',2,0)]
        need([op[2] for op in word if op[0]=='block']==wanted,'good/axis grammar');cases+=1;blocks+=len(wanted)
    definition=Residual(0,plan,0,True,((1,0),(0,1)))
    def begin():
        sink=regional.RegionalSink([]);sink.append(('residual_begin','idle',definition));return sink
    rejected(lambda:begin().append(('residual_end','idle',definition)),'missing direct run')
    rejected(lambda:begin().append_run(replace(definition)),'foreign run')
    sink=begin();sink.append_run(definition)
    rejected(lambda:sink.append_run(definition),'duplicate')
    rejected(lambda:sink.append(('residual_end','other',definition)),'end identity')
    rejected(lambda:begin().finish(),'unterminated residual')
    changed=source.replace(b'cursor.take()',b'cursor.take()[::-1]')
    rejected(lambda:regional.compiler(macro_code,changed,digest),'source hash')
    rejected(lambda:regional.compiler(macro_code,changed,sha256(changed).hexdigest()),'Cursor loop')
    sink=begin();sink.append_run(definition);sink.append(('residual_end','idle',definition));word=sink.finish()
    object.__setattr__(plan,'rank',0)
    rejected(lambda:word[1],'plan mutation')
    object.__setattr__(plan,'rank',1)
    return dict(cursor_cases=cases,cursor_labels=blocks,semantic_mutations=8)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--physical',action='store_true');ap.add_argument('--write',action='store_true');args=ap.parse_args()
    pins=authenticate()
    prior=load('prior_itinerary_verify',ROOT/'research/selected-itinerary-compression/verify.py')
    regional=load('regional_emitter',HERE/'regional.py')
    source=(ROOT/PHYSICAL/'macro_code.py').read_bytes();digest=pins[PHYSICAL+'/macro_code.py']
    with prior.original_modules(pins):
        if args.physical:
            before=prior.recursive(False,source,digest)
            with patch.object(prior,'compiler',regional.compiler):after=prior.recursive(True,source,digest)
            need(before==after,'physical continuation/endpoint refinement')
            result={'status':'PASS_DIRECT_RUN_PHYSICAL_CONTINUATIONS','recursive':after}
            target=HERE/'PHYSICAL.json'
        else:
            result={'status':'PASS_DIRECT_RESIDUAL_RUN_EMISSION','grammar':controls(prior,regional,source,digest),
                    'source_words':word_checks(prior,regional,source,digest)}
            target=HERE/'RESULT.json'
    authenticate()
    if args.write:target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(typed(json.loads(target.read_text()))==typed(result),'typed frozen receipt')
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
