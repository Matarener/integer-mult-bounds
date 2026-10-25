"""Independent end-to-end checks of literal programs, including dirty memory."""
import json,random,time,hashlib
from pathlib import Path
from ram_multiplier import build_multiplier,execute,BASE
from ntt.exact_ntt import multiply_digits,evaluate


def verify():
    rng=random.Random(20261024);records=[];total_cases=0
    for s,t in [(1,1),(1,2),(2,2),(3,5),(8,8),(16,13),(64,64),(256,256)]:
        fused=build_multiplier(s,t,True);duplicate=build_multiplier(s,t,False)
        B=fused.butterflies
        assert B==3*fused.n*(fused.n.bit_length()-1)//2
        assert len(duplicate.program)-len(fused.program)==49*B
        assert len(fused.program)<=60*B+193*fused.n+1144
        cases=[([0]*s,[0]*t),([15]*s,[15]*t),([rng.randrange(BASE) for _ in range(s)],[rng.randrange(BASE) for _ in range(t)])]
        if (s,t)==(1,1):cases=[([a],[b]) for a in range(BASE) for b in range(BASE)]
        comparisons=[]
        for a,b in cases:
            f,fd=execute(fused,a,b,True);d,dd=execute(duplicate,a,b,True)
            assert fd==dd
            assert evaluate(fd,BASE)==evaluate(multiply_digits(a,b),BASE)
            assert f.steps==sum(f.counts.values()) and f.steps<=len(fused.program)
            saving=d.steps-f.steps
            assert 33*B<=saving<=49*B
            assert d.counts.get('mul',0)-f.counts.get('mul',0)==B
            comparisons.append({'fused_steps':f.steps,'duplicate_steps':d.steps,'saved_instructions':saving,'fused_instruction_histogram':f.counts})
            total_cases+=1
        records.append({'lengths':[s,t],'n':fused.n,'butterflies':B,'fused_static_instructions':len(fused.program),'duplicate_static_instructions':len(duplicate.program),'owned_temporary_words':len(fused.temporaries),'output_words':len(fused.output),'comparisons':comparisons if s!=1 or t!=1 else {'exhaustive_256_cases':True,'minimum_steps':min(x['fused_steps'] for x in comparisons),'maximum_steps':max(x['fused_steps'] for x in comparisons)}})
    return {'status':'PASS','cases':total_cases,'models':'Literal tcslib ISA at W=64; fixed lengths and fixed modulus; interpreted program includes setup, constant synthesis, arithmetic, carry, clearing and final accept','tests':'All single-hex-digit pairs; boundary/random cases through 1024-bit operands; dirty owned memory; operand/exterior preservation; all owned temporaries zero; independent NTT and integer product oracles; same-ABI fused vs recomputation control','records':records}

if __name__=='__main__':
    started=time.perf_counter();result=verify();result['wall_seconds']=time.perf_counter()-started
    Path(__file__).with_name('integration-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':result['status'],'cases':result['cases'],'wall_seconds':result['wall_seconds'],'largest':result['records'][-1]},indent=2))
