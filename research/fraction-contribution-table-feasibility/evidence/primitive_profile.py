"""Profile only one complete frozen Fraction trace inside unchanged qualification."""
import cProfile
import fractions
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import profile as profile_support
import pstats
import runpy
import sys
import time
from frozen import baseline, require

require(Path(profile_support.__file__).name=='profile.py' and 'primitive-profile' not in str(profile_support.__file__),'stdlib profiling support')
rows=[]
with baseline() as package:
    sys.path.insert(0,str(package))
    native_spec=importlib.util.spec_from_file_location
    def spec(name,path,*args,**kwargs):
        value=native_spec(name,path,*args,**kwargs)
        if name=='single_pass_source':
            execute=value.loader.exec_module
            def observed_execute(module):
                execute(module)
                load=module.load
                def observed_load(n,p):
                    m=load(n,p)
                    if n=='frozen_contract':
                        factory=m.module
                        def observed_factory(n2,p2):
                            a=factory(n2,p2)
                            if n2=='noisy_precision':
                                original=a.error_trace
                                def profiled(*args,**kwargs):
                                    require(not rows,'one actual Fraction trace')
                                    profiler=cProfile.Profile()
                                    started=time.perf_counter()
                                    result=profiler.runcall(original,*args,**kwargs)
                                    elapsed=time.perf_counter()-started
                                    profiler.dump_stats(str(Path(__file__).with_name('fraction-trace.pstats')))
                                    stats=pstats.Stats(profiler)
                                    for (file,line,function),(primitive,total,self_seconds,cumulative,callers) in stats.stats.items():
                                        rows.append(dict(file=file,line=line,function=function,primitive_calls=primitive,total_calls=total,self_seconds=self_seconds,cumulative_seconds=cumulative))
                                    rows.sort(key=lambda x:x['self_seconds'],reverse=True)
                                    Path(__file__).with_name('PRIMITIVES.json').write_text(json.dumps(dict(profiled_trace_seconds=elapsed,total_calls=stats.total_calls,primitive_calls=stats.prim_calls,total_profile_self_seconds=stats.total_tt,functions=rows),indent=2,sort_keys=True)+'\n')
                                    return result
                                a.error_trace=profiled
                            return a
                        m.module=observed_factory
                    return m
                module.load=observed_load
            value.loader.exec_module=observed_execute
        return value
    started=time.perf_counter()
    importlib.util.spec_from_file_location=spec
    try:
        sys.argv=[str(package/'verify.py')]
        runpy.run_path(sys.argv[0],run_name='__main__')
    finally:
        importlib.util.spec_from_file_location=native_spec
    print(json.dumps(dict(status='PASS_FULL_QUALIFICATION_PRIMITIVE_PROFILE',whole_profiled_seconds=time.perf_counter()-started,profile_not_a_benchmark=True,fraction_source_sha256=sha256(Path(fractions.__file__).read_bytes()).hexdigest(),python=sys.version,top_self_functions=rows[:20]),sort_keys=True))
