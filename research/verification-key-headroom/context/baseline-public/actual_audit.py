"""One complete frozen original/slot/native audit; compiler work charged."""
import gzip,importlib.util,json,sys,time,resource
from frozen import baseline,require
from compact_finite import types_of
from fraction_table import derive
import slot_parent,native_backend

with baseline() as package:
    sys.path.insert(0,str(package))
    spec=importlib.util.spec_from_file_location('native_actual_bundle',package/'source.py')
    source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
    with source.baseline() as p:
        spec=importlib.util.spec_from_file_location('native_actual_source',p/'verify.py')
        v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
        with v.source() as (original_path,original,reference):
            word=json.loads(gzip.decompress((original_path/'inputs/WORD.json.gz').read_bytes()))
            ideal,weights=reference.ideal(word);rounded=set(ideal['counts'])
            fingerprint=reference.digest((word,weights,sorted(rounded)))
            parent=slot_parent.derive(reference);native=derive(reference)
            observed=[];base=None
            for label,fn in [('original',reference.error_trace),('slot-parent',parent),('native-apply-cold',native)]:
                start_children=resource.getrusage(resource.RUSAGE_CHILDREN)
                cpu=time.process_time();wall=time.perf_counter();result=fn(word,weights,rounded);elapsed=time.perf_counter()-wall;used=time.process_time()-cpu
                end_children=resource.getrusage(resource.RUSAGE_CHILDREN)
                child_cpu=end_children.ru_utime+end_children.ru_stime-start_children.ru_utime-start_children.ru_stime
                if base is None:base=result
                else:require(result==base and types_of(result)==types_of(base),'all actual values/types/witnesses')
                require(reference.digest((word,weights,sorted(rounded)))==fingerprint,'all actual inputs unchanged')
                observed.append(dict(label=label,wall_seconds=elapsed,cpu_seconds=used+child_cpu,parent_cpu_seconds=used,compiler_child_cpu_seconds=child_cpu,full_output_sha256=reference.digest(result)))
            require(native.compacted_selected() is True,'actual native path used')
            require(parent.statistics()==native.statistics(),'all actual cache statistics unchanged')
            print(json.dumps(dict(status='PASS_FULL_NATIVE_ACTUAL_AUDIT',events=len(word['program']),coordinates=ideal['n'],observations=observed,all_values_types_witnesses_inputs_equal=True,table_statistics=native.statistics(),weight_tokens=native.token_count(),build=native_backend.receipt(),direct_add=False,not_complete_performance=True),sort_keys=True))
