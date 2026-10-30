"""Added bounded controls and an optional fixed BCCB diagnostic.

SOURCE ONLY until executed by the sole serial parent runner. Invoke with the
staged extended PR5864 package path. --micro enables the declared diagnostic;
no actual-word run and no complete-performance claim are made here.
"""
from contextlib import contextmanager
from copy import deepcopy
from fractions import Fraction as F
import importlib.util
import json
import math
from pathlib import Path
import sys
import time


def need(ok,message):
    if not ok:raise ValueError(message)

def typed(value):
    if type(value) is dict:return ('dict',tuple((typed(k),typed(v)) for k,v in value.items()))
    if type(value) in (list,tuple):return (type(value).__name__,tuple(map(typed,value)))
    return type(value).__module__,type(value).__qualname__

@contextmanager
def reference_source():
    from frozen import baseline
    with baseline() as package:
        sys.path.insert(0,str(package))
        spec=importlib.util.spec_from_file_location('rational_probe_bundle',package/'source.py')
        source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
        with source.baseline() as p:
            spec=importlib.util.spec_from_file_location('rational_probe_source',p/'verify.py')
            v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
            with v.source() as (_,_,reference):yield reference

def fixture(n=32):
    # Odd denominators, negative terms, cancellation and values beyond int64.
    ws=[(F((1<<130)+i,2*i+3),F((-1)**i*(i+1),2*i+5)) for i in range(n)]
    src={i:F((-1)**i*((1<<80)+i+1),2*i+7) for i in range(n)}
    dst={i:(-src[i] if i%3==0 else F(i-9,2*i+11)) for i in range(n) if i%2==0}
    return ws,src,dst,[F(5,17),F(-7,19),F(1,23)]

def main(package,micro=False):
    sys.path.insert(0,str(Path(package).resolve()))
    import arithmetic_binding as binding
    import bulk_backend as bulk
    import fraction_table as predecessor
    import native_backend
    native=native_backend.load()
    token=binding.bind();need(token is not None and binding.fresh(token),'supported pinned arithmetic binder')
    controls=[]
    compute=predecessor.Contributions.compute
    ws,src,start,scores=fixture()
    def make(weights=ws,capacity=16,callback=compute):
        return native.Cache(capacity,weights,list(range(len(weights))),callback,
                            F.__dict__['_numerator'],F.__dict__['_denominator'],F)
    # Every source coefficient prefix, plus every event prefix below.
    comparisons=0
    for q in (F(1),F(-1),F(1,2),F(7,11),F(-37,13)):
        for cut in range(len(src)+1):
            subset=dict(list(src.items())[:cut])
            expected=dict(start);expected_scores=list(scores)
            for i,v in subset.items():
                old=expected.get(i,F(0));value=old+q*v;change=abs(value)-abs(old)
                expected_scores[0]+=change*ws[i][0]
                expected_scores[1]+=change*ws[i][1]
                expected_scores[2]+=change
                if value:expected[i]=value
                else:expected.pop(i,None)
            outputs=[];stats=[]
            for method in ('apply','apply_rational'):
                c=make();d=dict(start);s=list(scores);e=c.event(q)
                if method=='apply':e.apply(d,subset,s)
                else:e.apply_rational(d,subset,s,math.gcd)
                outputs.append((d,s));stats.append(c.statistics())
            need(outputs[0]==outputs[1]==(expected,expected_scores),'literal, cache, rational coefficient prefix')
            need(typed(outputs[0])==typed(outputs[1])==typed((expected,expected_scores)),'exact coefficient-prefix types')
            need(stats[0]==stats[1],'all counters at coefficient prefix')
            comparisons+=1
    controls.append('165-general-rational-coefficient-prefixes')
    # Repeated hits and full FIFO wraps share no cache across implementations.
    caches=[make(capacity=2),make(capacity=2)]
    for q in (F(1),F(-1),F(7,11),F(1),F(-1)):
        outputs=[]
        for k,c in enumerate(caches):
            d=dict(start);s=list(scores);e=c.event(q)
            if k:e.apply_rational(d,src,s,math.gcd)
            else:e.apply(d,src,s)
            outputs.append((d,s))
        need(outputs[0]==outputs[1] and caches[0].statistics()==caches[1].statistics(),'FIFO exact after batch')
    controls.append('batch-FIFO-and-full-counters')
    def rejects(fn,kind,label):
        try:fn()
        except kind:controls.append(label)
        else:raise ValueError('accepted '+label)
    rejects(lambda:make().event(F(1)).apply_rational({},src,[0,F(0),F(0)],math.gcd),TypeError,'exact-score-type')
    class ForeignFraction(F):pass
    rejects(lambda:make().event(F(1)).apply_rational({},src,[ForeignFraction(0),F(0),F(0)],math.gcd),TypeError,'score-subclass')
    bad=object.__new__(F);bad._numerator=1;bad._denominator=-3
    rejects(lambda:make().event(F(1)).apply_rational({},src,[bad,F(0),F(0)],math.gcd),ValueError,'negative-score-denominator')
    rejects(lambda:make().event(F(1)).apply_rational(src,src,list(scores),math.gcd),TypeError,'same-row')
    rejects(lambda:make().event(F(1)).apply_rational({},src,list(scores),lambda a,b:1),TypeError,'nonbuiltin-gcd')
    # Low-level malformed callback tests check safety, not arbitrary callback equivalence.
    moving={0:F(1)}
    def mutate_source(*args):moving.clear();return compute(*args)
    rejects(lambda:make(callback=mutate_source).event(F(1)).apply_rational({},moving,[F(0)]*3,math.gcd),RuntimeError,'source-iterator-mutation')
    changing=[F(0)]*3
    def mutate_scores(*args):changing.clear();return compute(*args)
    rejects(lambda:make(callback=mutate_scores).event(F(1)).apply_rational({}, {0:F(1)},changing,math.gcd),IndexError,'score-list-mutation')
    changing=[F(0)]*3
    def replace_score(*args):changing[0]=F(9);return compute(*args)
    rejects(lambda:make(callback=replace_score).event(F(1)).apply_rational({}, {0:F(1)},changing,math.gcd),RuntimeError,'score-value-mutation')
    outcomes=[]
    for method in ('apply','apply_rational'):
        calls=[0]
        def intermittent(*args):
            calls[0]+=1
            if calls[0]==2:raise ArithmeticError('fixed callback failure')
            return compute(*args)
        c=make(callback=intermittent);d={};s=[F(0)]*3;e=c.event(F(1))
        try:
            if method=='apply':e.apply(d,{0:F(1),1:F(1)},s)
            else:e.apply_rational(d,{0:F(1),1:F(1)},s,math.gcd)
        except ArithmeticError as error:outcomes.append((type(error).__name__,str(error),d,s,c.statistics()))
        else:raise ValueError('missing callback exception')
    need(outcomes[0]==outcomes[1],'completed score state before callback failure')
    controls.append('callback-failure-publishes-completed-prefix')
    # Every changed operation must force fresh() false and bind() rejection.
    code=F._add.__code__
    try:
        F._add.__code__=code.replace(co_consts=code.co_consts+('drift',))
        need(not binding.fresh(token) and binding.bind() is None,'live arithmetic code drift')
    finally:F._add.__code__=code
    controls.append('arithmetic-code-drift')
    try:
        F.__iadd__=lambda self,other:self
        need(not binding.fresh(token) and binding.bind() is None,'added in-place operation')
    finally:del F.__iadd__
    controls.append('inplace-protocol-drift')
    factory=F.__dict__['_from_coprime_ints'];code=factory.__func__.__code__
    try:
        factory.__func__.__code__=code.replace(co_consts=code.co_consts+('drift',))
        need(not binding.fresh(token) and binding.bind() is None,'factory code drift')
    finally:factory.__func__.__code__=code
    controls.append('materialization-source-drift')
    gcd=math.gcd
    try:
        math.gcd=math.lcm
        need(not binding.fresh(token) and binding.bind() is None,'gcd identity drift')
    finally:math.gcd=gcd
    controls.append('gcd-drift')
    fn=F.__add__;position=fn.__code__.co_freevars.index('monomorphic_operator');cell=fn.__closure__[position];saved=cell.cell_contents
    try:
        cell.cell_contents=F._sub
        need(not binding.fresh(token) and binding.bind() is None,'operator closure drift')
    finally:cell.cell_contents=saved
    controls.append('operator-closure-drift')
    with reference_source() as reference:
        word=dict(public=2,owned_fields=1,program=[['INIT',2,0],['MOVE',0,0,0,False],
             ['ADD',1,0,'1/3',0],['COPY',2,1,1,0],['SCALE',1,'-5/7',0],
             ['ADD',1,2,'-1',0],['CLEAR',2,0],['INIT',2,0],['ADD',2,0,'2',0],
             ['SCALE',0,'1/2',0],['ADD',0,1,'3/5',0],['CLEAR',2,0]])
        weights=[(F(j+1,2*j+3),F(j+2,2*j+5)) for j in range(len(word['program']))]
        rounded={'INIT','MOVE','ADD','COPY','SCALE','CLEAR'}
        before=reference.digest((word,weights,sorted(rounded)))
        fast=bulk.derive(reference);prior=predecessor.derive(reference)
        for cut in range(len(word['program'])+1):
            prefix=dict(word,program=word['program'][:cut]);w=weights[:cut]
            literal=reference.error_trace(prefix,w,rounded);old=prior(prefix,w,rounded);new=fast(prefix,w,rounded)
            need(literal==old==new and typed(literal)==typed(old)==typed(new),'complete event prefix values/types')
            need(reference.digest(literal)==reference.digest(new),'event prefix witnesses and hashes')
            need(fast.rational_selected(),'general non-dyadic rational route selected')
            need(prior.statistics()==fast.statistics(),'event prefix counters')
            comparisons+=1
        need(reference.digest((word,weights,sorted(rounded)))==before,'all inputs unchanged')
        controls.append('13-complete-event-prefixes-with-nondyadic-weights-and-scalars')
        # Unsupported exact-Fraction slot states retain the predecessor outcome.
        malformed=object.__new__(F);malformed._numerator=2;malformed._denominator=4
        ws2=list(weights);ws2[0]=(malformed,F(1))
        old=prior(word,ws2,rounded);new=fast(word,ws2,rounded)
        need(old==new and not fast.rational_selected(),'noncanonical slot fallback')
        controls.append('noncanonical-weight-fallback')
        # A changed __add__ that remains semantically equivalent is observable
        # through selection: no rational arithmetic bypass is permitted.
        add=F.__add__
        try:
            F.__add__=lambda self,other:add(self,other)
            literal=reference.error_trace(word,weights,rounded);new=fast(word,weights,rounded)
            need(literal==new and not fast.rational_selected(),'changed arithmetic literal fallback')
        finally:F.__add__=add
        controls.append('changed-arithmetic-fallback')
    result=dict(status='PASS_BOUNDED_RATIONAL_PROTOTYPE_ONLY',comparisons=comparisons,
                added_controls=controls,control_count=len(controls),build=native_backend.receipt(),
                independent_literal_oracle_used=True,actual_word_run=False,complete_performance=False)
    if micro:
        # One declared BCCB sequence, no retries and no projected complete gain.
        samples=[]
        for label in ('B1','C1','C2','B2'):
            wall=time.perf_counter();cpu=time.process_time();c=make(capacity=16384)
            check=None
            for repeat in range(512):
                d=dict(start);s=list(scores);e=c.event(F(7,11))
                if label.startswith('B'):e.apply(d,src,s)
                else:e.apply_rational(d,src,s,math.gcd)
                if check is None:check=(d,s)
                else:need((d,s)==check,'micro every repeated result')
            samples.append(dict(label=label,wall_seconds=time.perf_counter()-wall,
                                cpu_seconds=time.process_time()-cpu,statistics=c.statistics()))
        result['micro']=dict(sequence='BCCB',samples=samples,batches=512,coefficients=32,
                             cold_build_excluded_from_micro=True,illustrative_only=True,
                             complete_oracle_restoration_unpriced=True)
    print(json.dumps(result,sort_keys=True));return result

if __name__=='__main__':
    need(len(sys.argv) in (2,3),'finite_probe.py STAGED_PACKAGE [--micro]')
    need(len(sys.argv)==2 or sys.argv[2]=='--micro','known diagnostic option')
    main(sys.argv[1],len(sys.argv)==3)
