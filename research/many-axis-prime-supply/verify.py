#!/usr/bin/env python3
"""Source-bound prime supply for the newer many-axis tensor caller.

The finite constructor and Count adapter are HOST-INTEGER REFERENCES.
No encoded prime producer, production tensor, native or supplier is executed.
The uniform fixed-tape construction and cost are written in PROOF.md.
Apache-2.0. ToikY with substantial OpenAI Codex assistance.
"""
import argparse
import ast
from contextlib import contextmanager
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
PINS = {
 'PR3935-tensor_plan.py': (12079,'474730f42fcd2bd24720af4e08c71fb51cc374c3e16b8b6d7e565900f1a9e7c3','239caba2d2ccf2640c36d377949df3fb6a920cf0'),
 'PR3935-README.md': (6383,'7a7f218579ae4ff192bd4b7fdf00ba008117f6d6fbcb3a70e2d021be5bf8a209','2b665e76b4e86421bbea53b2252df8e81c91b290'),
 'PR4024-PROOF.md': (11035,'7b141475955cc372c5936118ff16e8748b589b93de2d26b76da28feec9b45de4','479a2b727b67b88efc8bdc64bde340a1c0d95ec3'),
 'PR4024-README.md': (5356,'2f179858402d1eac28b1da46139fa3198a625375532cc2c53a01c1ffc565281b','63648c961b96c6c76c305471b102e26d6b861d1b'),
 'source08-assembly.tex': (46444,'763d7945b1e1ec4ebae9b799bcefcc45fa9bae6e2ffad799868a9c3d513dbd4a','337810a1d9a58a2ecf14123420923c039ba322a6'),
}
CASES = ((8,(1,)), (12,(0,1,1)), (14,(1,0,1,1)),
         (14,(0,1,0,1,0,1)), (14,(1,0,0,1,1,0,1)))
ELL0, DIMENSION_POWER = 1 << 32, 334


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def typed(value):
    if isinstance(value, dict):
        return ('dict', tuple((k,typed(v)) for k,v in sorted(value.items())))
    if isinstance(value, list):
        return ('list', tuple(map(typed,value)))
    return type(value).__name__, value


def authenticate():
    for name,(length,sha,blob) in PINS.items():
        path = HERE/'source'/name
        need(not path.is_symlink(), 'source symlink: '+name)
        raw = path.read_bytes()
        need(len(raw)==length and hashlib.sha256(raw).hexdigest()==sha, 'source bytes: '+name)
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob, 'source blob: '+name)


class Natural:
    """Host semantic adapter for the extracted guard; no tape execution claim."""
    live = set()
    def __init__(self,value):
        value = value.value if isinstance(value,Natural) else value
        need(type(value) is int and value>=0, 'nonnegative host Count model')
        self.value,self.alive = value,True
        Natural.live.add(self)
    @classmethod
    def literal(cls,value):
        return cls(value)
    @classmethod
    def product(cls,a,b):
        need(a.alive and b.alive, 'live modeled product inputs')
        return cls(a.value*b.value)
    def multiply_small(self,value):
        need(self.alive and type(value) is int and value>=0, 'modeled small multiplication')
        self.value *= value
    def add(self,other):
        need(self.alive and other.alive, 'live modeled ADD')
        self.value += other.value
    def close(self):
        need(self.alive, 'single modeled ownership close')
        self.alive = False
        Natural.live.remove(self)


def compare(a,b):
    need(a.alive and b.alive, 'live modeled comparison')
    return (a.value>b.value)-(a.value<b.value)


def subtract(a,b):
    need(a.alive and b.alive and a.value>=b.value, 'modeled exact subtraction')
    return Natural(a.value-b.value)


@contextmanager
def owned(*values):
    try:
        yield values
    finally:
        for value in values:
            value.close()


def source_guard():
    """Authenticate first, then compile ONLY the complete selected AST method."""
    authenticate()
    source = ast.parse((HERE/'source/PR3935-tensor_plan.py').read_bytes())
    classes = [n for n in source.body if isinstance(n,ast.ClassDef) and n.name=='TensorPlan']
    need(len(classes)==1, 'unique source TensorPlan')
    methods = [n for n in classes[0].body if isinstance(n,ast.FunctionDef) and n.name=='production_axis']
    need(len(methods)==1, 'unique complete source production_axis')
    method = methods[0]
    need([a.arg for a in method.args.args]==['self','s','t'] and not method.decorator_list,
         'source guard API')
    module = ast.fix_missing_locations(ast.Module(body=[method],type_ignores=[]))
    namespace = {'Count':Natural,'owned':owned,'subtract':subtract,'compare':compare,'need':need,
                 '__builtins__':{}}
    exec(compile(module,'authenticated TensorPlan.production_axis','exec'),namespace)
    return namespace['production_axis']


def check_source_axis(s,t,d,target_halo=16,w=2,guard=None):
    need(all(type(x) is int and x>=0 for x in (s,t,d,target_halo,w)),
         'typed nonnegative source guard operands')
    need(not Natural.live, 'clean host-model entry')
    arguments = [Natural(x) for x in (s,t,d,target_halo,w)]
    protected = set(arguments)
    model = SimpleNamespace(d=arguments[2],target_halo=arguments[3],w=arguments[4])
    before = [a.value for a in arguments]
    try:
        (source_guard() if guard is None else guard)(model,*arguments[:2])
        need(Natural.live==protected and before==[a.value for a in arguments], 'source guard model preservation')
    finally:
        for argument in arguments:
            argument.close()
        need(not Natural.live, 'source guard modeled scratch restoration')
    return True


def primality_reference(n):
    """Bounded HOST reference: deliberately use all smaller trial divisors."""
    need(type(n) is int and n>=2, 'candidate domain')
    for divisor in range(2,n):
        if n % divisor == 0:
            return False
    return True


def interval(t,d):
    need(type(t) is int and type(d) is int and t>=4 and d>=2, 'interval domain')
    # a=t-t/(3d), b=t-t/(4d); search the exact open/closed integer interval.
    return t-(t+3*d-1)//(3*d)+1, t-(t+4*d-1)//(4*d)


def prime_queue(t,d,quota):
    low,high = interval(t,d)
    need(type(quota) is int and quota>=0, 'prime quota')
    result = []
    if quota:
        for candidate in range(low,high+1):
            if candidate>2 and primality_reference(candidate):
                result.append(candidate)
                if len(result)==quota:
                    break
    need(len(result)==quota, 'finite interval has insufficient prime supply')
    return result


def supplies(ell,flags,target_halo=16,w=2,guard=None):
    """Small host reference; symbolic theorem never calls this at ELL0."""
    need(type(ell) is int and 3<=ell<=20, 'bounded host-reference fixture width')
    need(isinstance(flags,(list,tuple)) and flags and
         all(type(f) is int and f in (0,1) for f in flags) and flags[-1]==1,
         'literal target flags with final full axis')
    need(type(target_halo) is int and type(w) is int and target_halo>=0 and w>=0,
         'finite guard auxiliary values')
    D,d = len(flags),len(flags)+1
    targets = [1 << (ell-1+flag) for flag in flags]
    queues = [prime_queue(1 << (ell-1+flag),d,flags.count(flag)) for flag in (0,1)]
    cursors,primes = [0,0],[]
    for flag,t in zip(flags,targets):
        s = queues[flag][cursors[flag]]
        cursors[flag] += 1
        primes.append(s)
    return validate_supplied(ell,flags,primes,target_halo,w,guard)


def validate_supplied(ell,flags,primes,target_halo=16,w=2,guard=None):
    """Validate an explicit reference return at the actual source interface."""
    need(type(ell) is int and 3<=ell<=20, 'bounded explicit supply width')
    need(isinstance(flags,(list,tuple)) and flags and
         all(type(f) is int and f in (0,1) for f in flags) and flags[-1]==1,
         'literal explicit target flags')
    need(isinstance(primes,(list,tuple)) and len(primes)==len(flags), 'one supplied prime per axis')
    need(all(type(s) is int and s>2 and s%2==1 for s in primes), 'odd supplied prime domain')
    need(type(target_halo) is int and type(w) is int and target_halo>=0 and w>=0,
         'explicit guard auxiliary values')
    D,d = len(flags),len(flags)+1
    targets = [1 << (ell-1+flag) for flag in flags]
    guard = source_guard() if guard is None else guard
    S,T = 1,1
    for s,t in zip(primes,targets):
        need(primality_reference(s), 'supplied prime primality')
        need(Fraction(3*d-1,3*d)*t < s <= Fraction(4*d-1,4*d)*t, 'exact interior band')
        check_source_axis(s,t,d,target_halo,w,guard)
        S,T = S*s,T*t
    need(len(set(primes))==D and 3*S>2*T, 'distinct primes and full volume ratio')
    source_bits = bytes((s>>bit)&1 for s in primes for bit in range(ell))
    flag_bits = bytes(flags[:-1])
    return {'ell':ell,'D':D,'d':d,'flags':list(flags),'targets':targets,'primes':primes,
            'source_bits_sha256':hashlib.sha256(source_bits).hexdigest(),
            'flag_bits_sha256':hashlib.sha256(flag_bits).hexdigest(),
            'source_bit_length':len(source_bits),'flag_bit_length':len(flag_bits),
            'S':S,'T':T,'address_bits':sum(ell-1+f for f in flags),
            'target_halo':target_halo,'w':w,'source_guard_checks':D,
            'source_guard_adapter':'host-integer Count semantics; complete authenticated AST method',
            'encoded_execution':False,'production_tensor_execution':False}


def threshold_certificate():
    """Only small integer/rational log bounds; never form 2**ELL0."""
    z0 = 1 << 16
    need(z0*z0==ELL0, 'threshold square')
    # y=log(t) lies between ell/4 and ell. d<=ell^334.
    polynomial_power = 2*DIMENSION_POWER+3
    first_log_bound = 7+polynomial_power*16
    first_exponential_bound = z0//4
    need(first_log_bound<first_exponential_bound and 4*polynomial_power<z0,
         'uniform decreasing error comparison')
    # t >= exp(ell/4), while 24*d*D*y <=24*ell^669.
    volume_power = 2*DIMENSION_POWER+1
    second_log_bound = 5+volume_power*32
    need(second_log_bound<ELL0//4 and 4*volume_power<ELL0, 'uniform volume comparison')
    need(Fraction(8476,10000)**2>Fraction(1,2) and Fraction(92211,10000)<10,
         'weakened analytic constants')
    return {'ell0':ELL0,'dimension_power':DIMENSION_POWER,'z0':z0,
            'error_log_upper':first_log_bound,'error_exponential_lower':first_exponential_bound,
            'volume_log_upper':second_log_bound,'volume_exponential_lower':ELL0//4,
            'FKS_reference':'arXiv:2206.12557v2 Corollary22; weaker decay coefficient0.8476',
            'period_premise':'K=target_halo+2*w <= 2^(ell-3); separate from prime abundance',
            'analytic_input_imported':True,'analytic_input_reproved':False,
            'giant_power_constructed':False}


def controls(guard):
    count = 0
    def reject(call):
        nonlocal count
        try:
            call()
        except ValueError:
            count += 1
            return
        raise ValueError('semantic negative control escaped')
    reject(lambda:supplies(4,(0,1,1),guard=guard))
    reject(lambda:supplies(12,(0,True,1),guard=guard))
    reject(lambda:supplies(12,(1,0),guard=guard))
    reject(lambda:supplies(ELL0,(1,),guard=guard))
    reject(lambda:check_source_axis(1023,1024,4,guard=guard))
    reject(lambda:check_source_axis(513,1024,4,guard=guard))
    reject(lambda:check_source_axis(953,1024,4,target_halo=512,guard=guard))
    reject(lambda:need(primality_reference(221),'composite must not be supplied'))
    return count


def compute():
    guard = source_guard()
    return {'schema_version':1,'mode':'host-reference','encoded_execution':False,
            'cases':[supplies(ell,flags,guard=guard) for ell,flags in CASES],
            'threshold':threshold_certificate(),'semantic_controls':controls(guard),
            'new_kappa':False,'full_multiplication_theorem':False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    if args.write:
        need(not (HERE/'RESULT.json').exists(),'refuse existing receipt overwrite')
    result = compute()
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:
        expected = json.loads((HERE/'RESULT.json').read_bytes(),object_pairs_hook=unique)
        need(typed(result)==typed(expected),'complete typed receipt')
    print('PASS_MANY_AXIS_PRIME_SUPPLY cases='+str(len(result['cases']))
          +' host_reference_only symbolic_effective_threshold no_full_supplier_no_new_kappa')


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        import sys
        print('FAIL_MANY_AXIS_PRIME_SUPPLY '+str(error),file=sys.stderr)
        raise SystemExit(1)
