"""Explicit source-bound checks; no assertions, network, Git or file writes."""
import sys
sys.dont_write_bytecode=True
import argparse,copy,gzip,hashlib,importlib.util,itertools,json,random,time
from pathlib import Path
from fractions import Fraction as F
P=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise ValueError(msg)

def sources():
    manifest=json.loads((P/'FROZEN-SOURCES.json').read_text())
    need({x['path']for x in manifest}=={str(p.relative_to(P))for p in (P/'frozen').iterdir()if p.is_file()},'complete frozen manifest')
    for x in manifest:need(hashlib.sha256((P/x['path']).read_bytes()).hexdigest()==x['sha256'],'frozen source '+x['path'])
    return len(manifest)

def exact_recipe(v,recipe):
    import mersenne as m
    def mon(v,r):
        perm,ph=m.decode(r);out=[None]*512
        for x,y in enumerate(perm):
            a,b=v[x];out[y]=[(a,b),(-b,a),(-a,-b),(b,-a)][ph[x]]
        return out
    v=mon(v,recipe['right'])
    for j in range(recipe['rank']):
        out=[]
        for x,(a,b)in enumerate(v):
            c,d=v[x^(1<<j)];out.append((a-b+c+d,b+a+d-c))
        v=out
    return mon(v,recipe['left'])

def routing(rec):
    import mersenne as m
    perm,ph=m.decode(rec);seen=set();swaps=0
    for x in range(512):
        if x in seen:continue
        n=0;y=x
        while y not in seen:seen.add(y);n+=1;y=perm[y]
        swaps+=2*(n-1)
    return swaps+sum(p%2 for p in ph),sum((0,1,2,1)[p]for p in ph)

def run():
    frozen=sources()
    import mersenne as m
    import lifecycle as l
    counts={};rng=random.Random(4017277)
    counts['adder_generalized_all_states']=0;counts['adder_elementary_all_states']=0
    for b in range(2,6):
        g=m.add_gates(list(range(b)),list(range(b,2*b)));lo=[e for gate in g for e in m.circuit.lower(gate,2*b)]
        for x in range(1<<b):
            for y in range(1<<b):
                state=x|(y<<b);want=x|(m.add(y,x,b)<<b)
                need(m.circuit.apply(state,g)==want,'generalized modular add')
                counts['adder_generalized_all_states']+=1
                if b<=4:
                    need(m.circuit.apply(state,lo)==want,'literal Toffoli modular add');counts['adder_elementary_all_states']+=1
        n=m.negate_gates(list(range(b)))
        for x in range(1<<b):need(m.circuit.apply(x,n)==m.neg(x,b),'zero-preserving modular negation')
        for e in range(2*b):
            dec=m.decode_gates(list(range(b)),e);need(len({m.circuit.apply(x,dec)for x in range(1<<b)})==1<<b,'decode total permutation')
            for x in range((1<<b)-1):need(m.circuit.apply(x,dec)==(m.centered_decode(x,b,e)&((1<<b)-1)),'literal endpoint decode')
    counts['pair_generalized_all_states']=0;counts['pair_elementary_cases']=0
    for b in [2,3]:
        M=(1<<b)-1;gs=m.pair_gates(b);lo=[e for gate in gs for e in m.circuit.lower(gate,4*b)]
        for state in range(1<<(4*b)):
            z=m.circuit.apply(state,gs);need(m.circuit.apply(z,gs[::-1])==state,'pair total inverse incl unused codes');counts['pair_generalized_all_states']+=1
            words=tuple((state>>(j*b))&M for j in range(4))
            if all(x<M for x in words):
                u,v=m.pair(words[:2],words[2:],b);want=sum(x<<(j*b)for j,x in enumerate(u+v));need(z==want,'canonical pair arithmetic')
                need(m.pair(u,v,b,True)==(words[:2],words[2:]),'canonical arithmetic inverse')
            if b==2 or state%29==0:
                need(m.circuit.apply(state,lo)==z,'literal pair borrowed bits restored');counts['pair_elementary_cases']+=1
    macro=json.loads((P/'frozen'/'PR4017-MACRO.json').read_text())['recipe'];climbs=json.loads((P/'CLIMBS.json').read_text())
    # All-column exact Gaussian oracle, including absolute phase, for the five
    # charged physical transitions; the compiler is a credited reference.
    count=0
    for c in climbs:
        op=l.ce.canonical_frame(9,tuple(c['before'])).adjoint().then(l.ce.canonical_frame(9,tuple(c['after'])))
        need(c['recipe']['rank']==c['rank']==1,'charged rank')
        for col in range(512):
            v=[(0,0)]*512;v[col]=(1,0);got=exact_recipe(v,c['recipe']);ref,d=op.zero_state(col)
            need(all((a*(1<<d),b*(1<<d))==(x*2,y*2)for(a,b),(x,y)in zip(got,ref)),'exact phase-bearing physical climb column');count+=1
    counts['exact_physical_climb_columns']=count
    terminal=l.ce.canonical_frame(9,tuple(json.loads((P/'frozen'/'PR4017-MACRO.json').read_text())['terminal']))
    for col in range(512):
        v=[(0,0)]*512;v[col]=(1,0);got=exact_recipe(v,macro);ref,d=terminal.zero_state(col)
        need(all((a*(1<<d),b*(1<<d))==(x*32,y*32)for(a,b),(x,y)in zip(got,ref)),'source terminal residual column')
    counts['exact_terminal_residual_columns']=512
    traces={};heights={}
    for tag in ['base','extra']:
        w=l.load(tag);tr=l.source_trace(w);need(tr['climbs']==[{k:v for k,v in c.items()if k!='recipe'}for c in climbs],'both-provider exact source chronology')
        traces[tag]=tr;heights[tag]=l.height_bound(w)
    # Bound every literal single-helper touch and its buffer cleanup; other
    # provider work remains inherited, not assigned zero cost here.
    lifetime_bills={}
    for b in [8,32,64]:
        pb=m.circuit.bill(m.pair_gates(b));ab=m.circuit.bill(m.add_gates(list(range(b)),list(range(b,2*b))));nb=m.circuit.bill(m.negate_gates(list(range(b))))
        sw=ng=0
        for c in climbs:
            for side in ['left','right']:
                ss,nn=routing(c['recipe'][side]);sw+=ss;ng+=nn
        physical={k:1280*pb[k]+(3*b*sw if k=='CNOT'else 0)+ng*nb[k]for k in ['X','CNOT','Toffoli']}
        scalar={k:86*1024*ab[k]+12*1024*nb[k]+(4*1024*3*(b-1)if k=='CNOT'else 0)for k in ['X','CNOT','Toffoli']}
        # Twelve negative scales; four also multiply by2 or1/2. Source reads
        # for dyadic ADD coefficients are wire permutations, explicitly free
        # only as circuit connectivity (not a locality/time claim).
        lifetime_bills[b]={'five_charged_climbs':physical,'98_scalar_touch_instructions':scalar,'sum':{k:physical[k]+scalar[k]for k in physical},'optional_endpoint_decode_1024_real_components':{k:1024*m.circuit.bill(m.decode_gates(list(range(b)),5))[k]for k in ['X','CNOT','Toffoli']},'extra_workspace_bits':0,'scope':'Only five physical climbs on277 and98 touching scalar instructions; neighboring provider work inherited and not included.'}
    # Exact source-bound completed residual numerical recovery.
    numerics=[];additivity=[]
    for b,A in [(13,1),(16,3),(20,127)]:
        M=(1<<b)-1;need(M>2048*A,'endpoint modulus bound')
        v=[(rng.randint(-A,A),rng.randint(-A,A))for _ in range(512)]
        enc=[(a%M,c%M)for a,c in v];out=m.macro(enc,b,macro);num=exact_recipe(v,macro)
        got=[(m.centered_decode(a,b,5),m.centered_decode(c,b,5))for a,c in out]
        need(got==num,'exact endpoint dyadic numerator recovery')
        need(m.macro(out,b,macro,True)==enc,'actual residual ring inverse')
        numerics.append({'b':b,'input_bound':A,'modulus':M,'denominator':32,'all1024_real_numerators_recovered':True})
        h=[(0,0)]*512;h[0]=(1,0);qh=m.macro(h,b,macro);twice=m.macro([(2*a%M,2*c%M)for a,c in h],b,macro)
        need(twice==[(2*a%M,2*c%M)for a,c in qh],'actual residue additivity witness repaired');additivity.append(b)
    # Negative controls target distinct claims, not only input schemas.
    rejects=[]
    bad=copy.deepcopy(l.load('base'));bad['B'][529][3]*=-1
    try:l.source_trace(bad)
    except (ValueError,l.a.AuditFailure):rejects.append('changed actual late helper addition')
    else:raise ValueError('accepted changed helper lifetime')
    bad=copy.deepcopy(l.load('base'));bad['cleanup'][1130][3]*=-1
    try:l.source_trace(bad)
    except (ValueError,l.a.AuditFailure):rejects.append('changed buffer981 cleanup')
    else:raise ValueError('accepted changed buffer cleanup')
    bad=copy.deepcopy(climbs[0]);bad['recipe']['left']['phase']=(bad['recipe']['left']['phase']+1)%4
    v=[(0,0)]*512;v[0]=(1,0);need(exact_recipe(v,bad['recipe'])!=exact_recipe(v,climbs[0]['recipe']),'wrong global phase rejection');rejects.append('changed physical climb global phase')
    # Centered interpretation of ring half(1) is not ordinary numerical1/2.
    b=8;M=(1<<b)-1;need(m.centered_decode(m.half(1,b),b,0)==-127,'fixed-grid counterexample');rejects.append('unscaled fixed-grid interpretation')
    need(m.centered_decode(m.half(1,b),b,1)==1,'scaled exact half numerator')
    # An even modulus cannot supply inverse2.
    try:pow(2,-1,256)
    except ValueError:rejects.append('even modulus')
    else:raise ValueError('even modulus admitted')
    # Removing the zero/unused-code swap produces wrong wrap and invalid return.
    b=3;dst=list(range(b,2*b));badinc=[(tuple([(0,1)]+[(dst[j],1)for j in range(k)]),dst[k])for k in range(b-1,-1,-1)]
    need(m.circuit.apply(1|(6<<b),badinc)!=(1|(0<<b)),'missing endpoint-swap control');rejects.append('omit modulo endpoint swap')
    return {'status':'PASS_EXACT_RESIDUE_LIFETIME_NOT_RECURSIVE_ADMISSION','frozen_source_count':frozen,'counts':counts,'traces':traces,'height_bounds':heights,'circuit_bills':{b:m.bill(b)for b in [8,32,64]},'lifetime_bills':lifetime_bills,'endpoint_numerical_cases':numerics,'actual_macro_additivity_moduli_bits':additivity,'rejected_controls':rejects}

if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('--json',action='store_true');ns=pa.parse_args();t=time.monotonic();out=json.loads(json.dumps(run()))  # JSON canonical key/list types for committed receipt comparison
    expected=P/'RESULT.json'
    if expected.exists():need(out==json.loads(expected.read_text()),'committed result differs')
    print(json.dumps(out,indent=2)if ns.json else json.dumps({'status':out['status'],'counts':out['counts'],'elapsed_seconds':round(time.monotonic()-t,3)}))
