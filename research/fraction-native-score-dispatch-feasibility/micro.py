"""One fixed BCCB native score-dispatch screen, no actual-word claim."""
from fractions import Fraction as F
import json,time
import probe_backend
import runtime_binding as binding

def need(ok,message):
    if not ok:raise ValueError(message)

def main():
    kernel=binding.bind_kernel(strict=True);token=binding.state_token()
    probe=probe_backend.load();controls=[]
    positives=[(F(0),F(0),F(0)),(F(1,2),F(-1,2),F(3,8)),
               (F(2,3),F(5,7),F(-11,13)),(F(3,8),F(5,8),F(-1,8)),
               (F(2**127+1,2**61),F(-3,16),F(7,31)),
               (F(-9,17),F(11,17),F(1,2**127)),
               (F(1),F(-1),F(0)),(F(5,16),F(-7,32),F(13,64))]
    increments=tuple((F(0),*triple) for positive in positives for triple in (positive,tuple(-x for x in positive)))
    need(len(increments)==16,'sixteen frozen contribution-shaped triples')
    seed=[F(2,3),F(-5,7),F(11,13)]
    for count in range(33):
        expected=list(seed)
        for i in range(count):
            for k in range(3):expected[k]+=increments[i%16][k+1]
        a=list(seed);b=list(seed)
        generic=probe.generic(a,increments,count,F)
        direct=probe.direct(b,increments,count,F,kernel)
        need(a==b==expected and all(type(x) is F for x in a+b),'every finite prefix value/type')
        need(generic==(0,count*3) and direct==(count*3,0),'both actual native branches counted')
    controls.append('all-33-prefix-values-types-and-branches')
    calls=[]
    class Score:
        def __iadd__(self,other):calls.append(other);return self
    def forbidden(a,b):raise ValueError('nonexact direct call')
    objects=[Score(),Score(),Score()]
    need(probe.direct(objects,increments,2,F,forbidden)==(0,6) and len(calls)==6,'custom generic iadd retained')
    controls.append('nonexact-custom-score-generic-iadd')
    class Sub(F):
        def __iadd__(self,other):calls.append(other);return self
    objects=[Sub(1),Sub(2),Sub(3)];calls.clear()
    need(probe.direct(objects,increments,1,F,forbidden)==(0,3) and len(calls)==3,'Fraction subtype uses generic iadd')
    controls.append('Fraction-subtype-generic-iadd')
    integer_increments=tuple((F(0),1,2,3) for _ in range(16));scores=[F(0)]*3
    need(probe.direct(scores,integer_increments,1,F,forbidden)==(0,3) and scores==[F(1),F(2),F(3)],'nonexact increment uses generic')
    controls.append('nonexact-increment-generic')
    original_add=F.__dict__['__add__'];retry=[];invoked=[]
    def poison(self,other):retry.append(True);raise RuntimeError('unexpected generic retry')
    def failing(a,b):
        invoked.append(True)
        if len(invoked)==2:raise ArithmeticError('direct kernel failure')
        return kernel(a,b)
    scores=[F(0),F(1),F(2)];first=tuple((F(0),F(10),F(20),F(30)) for _ in range(16))
    F.__add__=poison
    try:
        try:probe.direct(scores,first,1,F,failing)
        except ArithmeticError as error:need(str(error)=='direct kernel failure','original direct error')
        else:raise ValueError('direct exception swallowed')
    finally:F.__add__=original_add
    need(len(invoked)==2 and not retry and scores==[F(10),F(1),F(2)],'no retry and exact partial update order')
    controls.append('direct-error-no-retry-partial-update-order')
    scores=[F(0)]*3
    def clears(a,b):scores.clear();return kernel(a,b)
    try:probe.direct(scores,increments,1,F,clears)
    except IndexError:pass
    else:raise ValueError('mutated score list accepted')
    controls.append('callback-score-list-mutation-safe')
    try:probe.direct([F(0)]*3,increments,1,F,object())
    except TypeError:pass
    else:raise ValueError('foreign kernel packet accepted')
    controls.append('nonfunction-kernel-packet-rejected')
    old=F.__dict__['_add'];F._add=lambda a,b:F(999)
    try:need(binding.bind_kernel() is None and not binding.still_current(token),'live kernel drift invalidates')
    finally:F._add=old
    controls.append('kernel-binding-drift')
    F.__iadd__=None
    try:need(binding.bind_kernel() is None and not binding.still_current(token),'present None iadd rejected')
    finally:del F.__iadd__
    controls.append('present-none-iadd-drift')
    need(binding.bind_kernel(strict=True) is kernel and binding.still_current(token),'all runtime controls restored before timing')
    controls.append('runtime-restored-before-timing')
    observations=[];groups=32768
    for label in 'BCCB':
        scores=list(seed)
        cpu=time.process_time();wall=time.perf_counter()
        counts=probe.generic(scores,increments,groups,F) if label=='B' else probe.direct(scores,increments,groups,F,kernel)
        elapsed=time.perf_counter()-wall;used=time.process_time()-cpu
        need(scores==seed and all(type(x) is F for x in scores),'all terminal scores/types preserved')
        need(counts==((0,groups*3) if label=='B' else (groups*3,0)),'timed native branch executed')
        row=dict(label=label,wall_seconds=elapsed,cpu_seconds=used,counts=counts,terminal_scores=list(map(str,scores)))
        observations.append(row);print(json.dumps(dict(observation=row),sort_keys=True),flush=True)
    differences={metric:[observations[0][metric]-observations[1][metric],observations[3][metric]-observations[2][metric]] for metric in ('wall_seconds','cpu_seconds')}
    both=all(min(x)>0 for x in differences.values())
    result=dict(status='MICRO_PASS_REQUIRES_FULL_INCREMENTAL_COST_BILL' if both else 'STOP_NATIVE_DIRECT_ADD_MICRO',
                no_actual_or_complete_construction=True,controls=controls,control_count=len(controls),
                fixed_order='BCCB',groups_per_arm=groups,additions_per_arm=groups*3,observations=observations,
                paired_differences=differences,
                illustrative_gross_only={k:min(v)*7739250/(groups*3) for k,v in differences.items()},
                not_a_full_trace_projection_or_improvement=True,build=probe_backend.receipt(),
                runtime_current=binding.still_current(token))
    print(json.dumps(result,sort_keys=True));return result

if __name__=='__main__':main()
