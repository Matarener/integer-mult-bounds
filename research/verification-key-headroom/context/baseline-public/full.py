"""Complete frozen qualifier with one source-bound Fraction seam changed."""
import importlib.util,inspect,json,sys
from pathlib import Path
from frozen import baseline,require

ACTUAL_STATS=dict(calls=2579750,hits=2252966,misses=326784,evictions=310400,bypasses=0,resident=16384,capacity=16384)
OUTPUT='954c7448ff74d78753828e9623ad44c46da9e5ce459420b6e50a5d47294250b9'

def main(native=False):
    if native:
        import finite
        finite.main()
        # The inherited finite harness imports its own sealed temporary source.
        # Remove only expired, owned temporary modules before the fresh qualifier.
        for name in ('source','observe'):
            value=sys.modules.get(name);file=getattr(value,'__file__','')
            if file.startswith('/tmp/precision-linux-source-') and not Path(file).exists():del sys.modules[name]
    with baseline() as package:
        sys.path.insert(0,str(package))
        spec=importlib.util.spec_from_file_location('native_complete_frozen_entry',package/'candidate.py')
        entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
        if not native:
            entry.main();return
        import fraction_table,native_backend
        captures=[]
        def native_trace(reference,expected_word):
            trace=fraction_table.derive(reference)
            def call(word,weights,rounded):
                result=trace(word,weights,rounded)
                if len(word['program'])==len(expected_word['program']):
                    require(trace.compacted_selected() is True,'actual native route selected')
                    require(trace.statistics()==ACTUAL_STATS,'all actual native counters')
                    require(reference.digest(result)==OUTPUT,'complete actual native output digest')
                    captures.append(dict(statistics=trace.statistics(),output_sha256=OUTPUT,tokens=trace.token_count()))
                return result
            return call
        raw=(package/'candidate.py').read_text()
        seam='                    value = Observation(value, reference.digest, word)\n'
        require(raw.count(seam)==1,'one authenticated actual Fraction seam')
        changed=raw.replace(seam,'                    value.error_trace = _native_trace(value, word)\n'+seam)
        namespace=dict(entry.__dict__);namespace['_native_trace']=native_trace
        exec(compile(changed,str(package/'candidate.py'),'exec'),namespace)
        qualify=namespace['qualify']
        def qualified():
            result=qualify()
            require(len(captures)==1,'one complete actual native observation')
            print(json.dumps(dict(status='PASS_COMPLETE_NATIVE_COVERAGE',actual=captures[0],build=native_backend.receipt(),native_finite_included=True,compiler_children_charged=True,integer_oracle_unchanged=True),sort_keys=True))
            return result
        namespace['qualify']=qualified
        namespace['main']()

if __name__=='__main__':
    require(len(sys.argv)==2 and sys.argv[1] in ('B','C'),'complete B or C')
    main(sys.argv[1]=='C')
