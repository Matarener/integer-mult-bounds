"""Full inherited scientific gate and bounded native ownership/API controls."""
import gc,json,sys,weakref,importlib.util
from fractions import Fraction as F
import native_backend
import fraction_table as table
import slot_finite
from frozen import require,baseline
from compact_finite import types_of

def main():
    inherited=slot_finite.main();controls=[];native=native_backend.load()
    weights=[(F(2),F(3)),(F(5),F(7)),(F(4,2),F(6,2))];tokens=[0,1,0]
    compute=table.Contributions.compute
    def make(cap=2,fn=compute,ws=None,ts=None):return native.Cache(cap,weights if ws is None else ws,tokens if ts is None else ts,fn,F.__dict__['_numerator'],F.__dict__['_denominator'],F)
    def rejects(action,kind,label):
        try:action()
        except kind:controls.append(label)
        else:raise ValueError('accepted '+label)
    for cap in (1,2,16):
        old=table.Contributions(cap);old.certify(dict(public=1,owned_fields=0,program=[]),weights,set());new=make(cap)
        for q in (F(1),F(-1),F(1,2),F(2,4),F(2)):
            event=new.event(q)
            for k,i in enumerate((0,1,2,0,1,0,2,2,1)):
                a,v=F(k%2),F(k%3-1)
                require(event(a,v,i)==old.step(a,q,v,*weights[i]),'native value/FIFO')
                require(new.statistics()==old.statistics(),'native full counters')
    controls.append('canonical-keys-FIFO-wrap-counters')
    c=make();event=c.event(F(1));modulus=sys.hash_info.modulus
    a=event(F(0),F(1),0);b=event(F(modulus),F(1),0)
    require(a!=b and c.statistics()['misses']==2,'native full equality on integer hash collision')
    controls.append('native-hash-collision')
    log=[]
    def observed(*args):log.append(args);return compute(*args)
    c=make(fn=observed);e=c.event(F(1));a=e(F(0),F(1),0);b=e(F(0),F(1),0)
    require(a is b and len(log)==1,'hit returns owned existing tuple; no arithmetic')
    controls.append('exact-one-callback-per-miss')
    def fails(*args):raise ArithmeticError('original callback failure')
    c=make(fn=fails);e=c.event(F(1))
    for k in range(2):rejects(lambda:e(F(0),F(1),0),ArithmeticError,'uncached-native-error-'+str(k))
    require(c.statistics()['resident']==0 and c.statistics()['misses']==2,'failed callback never cached')
    gate=[False]
    def intermittent(*args):
        if gate[0]:raise ArithmeticError('full miss')
        return compute(*args)
    c=make(1,intermittent);e=c.event(F(1));e(F(0),F(1),0);gate[0]=True
    rejects(lambda:e(F(2),F(1),0),ArithmeticError,'full-cache-failure-before-eviction')
    require(c.statistics()['resident']==1 and c.statistics()['evictions']==0,'failed miss retains FIFO')
    require(e(F(0),F(1),0)==compute(F(0),F(1),F(1),*weights[0]),'existing cache hit after failure')
    controls.append('cache-survives-callback-exception')
    c=make();e=c.event(F(1))
    for cap in (0,-1,16385,True,1.5,10**100):rejects(lambda cap=cap:make(cap),(ValueError,OverflowError),'capacity-'+str(cap))
    for i in (-1,3,10**100,True,'0'):rejects(lambda i=i:e(F(0),F(1),i),(TypeError,IndexError,OverflowError),'index-'+str(i))
    rejects(lambda:e(F(0),F(1)),TypeError,'arity')
    rejects(lambda:e(F(0),F(1),0,extra=1),TypeError,'keywords')
    rejects(lambda:e(0,F(1),0),TypeError,'exact-operand')
    rejects(lambda:c.event(1),TypeError,'exact-scalar')
    rejects(lambda:type(e)(),TypeError,'event-creation')
    rejects(lambda:native.Cache(2,weights,tokens,compute,object(),F.__dict__['_denominator'],F),TypeError,'descriptor-protocol')
    rejects(lambda:make(ts=[0]),ValueError,'token-length')
    rejects(lambda:make(ts=[0,-1,1]),ValueError,'token-range')
    rejects(lambda:make(ws=[(F(1),)]),ValueError,'partial-init-length')
    rejects(lambda:make(ws=[(1,F(1))]*3),TypeError,'partial-init-weight')
    def malformed(*args):return (F(1),)*3
    e=make(fn=malformed).event(F(1));rejects(lambda:e(F(0),F(1),0),TypeError,'callback-result-shape')
    def malformed(*args):return (F(1),F(1),F(1),1)
    e=make(fn=malformed).event(F(1));rejects(lambda:e(F(0),F(1),0),TypeError,'callback-result-type')
    holder=[]
    def recursive(*args):return holder[0](F(0),F(1),0)
    c=make(fn=recursive);holder.append(c.event(F(1)))
    rejects(lambda:holder[0](F(0),F(1),0),RuntimeError,'callback-reentry')
    require(c.statistics()['calls']==1 and c.statistics()['resident']==0,'reentry cannot mutate cache')
    del holder[:]
    c=make();e=c.event(F(1));del c;gc.collect()
    require(e(F(0),F(1),0)==compute(F(0),F(1),F(1),*weights[0]),'Event owns parent/context')
    controls.append('event-owns-parent')
    def cycle():
        context=[]
        def callback(*args):return compute(*args) if context else None
        c=make(fn=callback);context.append(c);return weakref.ref(callback)
    ref=cycle();gc.collect();require(ref() is None,'callback/cache cycle collected')
    controls.append('GC-callback-cycle')
    c=make();s=c.statistics();s['calls']=-1;require(c.statistics()['calls']==0,'statistics isolated');controls.append('native-statistics-isolated')
    src={0:F(1),1:F(-1),2:F(2)};dst={0:F(1)};scores=[F(3),F(4),F(5)]
    expected=dict(dst);expected_scores=list(scores);parent=table.parent.CompactContributions(2,weights,tokens);step=parent.event(F(-1))
    for i,v in src.items():
        value,a,b,change=step(expected.get(i,F(0)),v,i)
        expected_scores[0]+=a;expected_scores[1]+=b;expected_scores[2]+=change
        if value:expected[i]=value
        else:expected.pop(i,None)
    c=make();c.event(F(-1)).apply(dst,src,scores)
    require((dst,scores)==(expected,expected_scores) and types_of((dst,scores))==types_of((expected,expected_scores)) and c.statistics()==parent.statistics(),'complete native apply values/types/counters')
    controls.append('native-coefficient-loop')
    rejects(lambda:c.event(F(1)).apply(dst,dst,scores),TypeError,'same-row-lowlevel-rejection')
    def mutate(*args):src.clear();return compute(*args)
    src={0:F(1)};e=make(fn=mutate).event(F(1))
    rejects(lambda:e.apply({},src,[F(0)]*3),RuntimeError,'dict-iterator-mutation-safe')
    scores=[F(0)]*3
    def mutate_score(*args):scores.clear();return compute(*args)
    e=make(fn=mutate_score).event(F(1))
    rejects(lambda:e.apply({}, {0:F(1)},scores),IndexError,'callback-list-mutation-safe')
    require(native_backend.source_hash()==native_backend.receipt()['source_sha256'],'compiled source remains bound')
    controls.append('native-source-authenticated')
    normal=table.Contributions.__dict__.get('compute');had='compute' in table.Contributions.__dict__;log=[]
    class ForeignCompute:
        def __get__(self,*args):log.append(True);raise RuntimeError('foreign compute must not be invoked')
    try:
        table.Contributions.compute=ForeignCompute()
        require(table.checked_compute() is None and not log,'foreign callback descriptor rejected purely')
        controls.append('callback-descriptor-is-pure')
        table.Contributions.compute=compute
        require(table.checked_compute() is None,'plain function would bind self; not staticmethod')
        controls.append('plain-callback-rejected')
    finally:
        if had:table.Contributions.compute=normal
        else:del table.Contributions.compute
    code=compute.__code__;compute.__code__=code.replace(co_consts=code.co_consts+('drift',))
    try:require(table.checked_compute() is None,'live callback executable bound')
    finally:compute.__code__=code
    controls.append('live-callback-code-drift')
    ws=[(F(2),F(3))];ts=[0]
    owned=make(ws=ws,ts=ts);event=owned.event(F(1));ws.clear();ts.clear();gc.collect()
    require(event(F(0),F(1),0)==compute(F(0),F(1),F(1),F(2),F(3)),'owned immutable packet survives caller metadata mutation')
    controls.append('owned-metadata-snapshot')
    with baseline() as package:
        sys.path.insert(0,str(package));spec=importlib.util.spec_from_file_location('native_fallback_bundle',package/'source.py')
        source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
        with source.baseline() as p:
            spec=importlib.util.spec_from_file_location('native_fallback_source',p/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
            with v.source() as (_,_,ref):
                original=ref.error_trace;fast=table.derive(ref)
                word=dict(public=1,owned_fields=0,program=[['INIT',0,0],['ADD',0,0,1,0]])
                ws=[(F(1),F(1))]*2
                require(fast(word,ws,set())==original(word,ws,set()) and not fast.compacted_selected(),'same-row literal fallback')
                controls.append('same-row-source-fallback')
                bad=object.__new__(F)
                word=dict(public=2,owned_fields=0,program=[['ADD',0,1,bad,0]])
                outcomes=[]
                for fn in (original,fast):
                    try:outcomes.append(('value',fn(word,ws,set())))
                    except Exception as error:outcomes.append((type(error).__name__,str(error)))
                require(outcomes[0]==outcomes[1] and not fast.compacted_selected(),'malformed Fraction scalar has literal source outcome')
                controls.append('malformed-scalar-literal-fallback')
    result=dict(status='PASS_NATIVE_FINITE_ONLY',inherited=inherited,native_controls=controls,native_control_count=len(controls),build=native_backend.receipt(),all_coverage_preserved=True)
    print(json.dumps(result,sort_keys=True));return result

if __name__=='__main__':main()
