"""Independent, read-only compact-compiler audit. Python standard library only.
No files or interpreter configuration are changed. Numerical controls are
independent integer/rational tests, rather than edited source copies.
Apache-2.0; substantial OpenAI Codex assistance. Predecessor credit retained.
"""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
import hashlib,importlib.util,json,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent
ROOT=PACKAGE.parents[1]

def need(ok,message):
    if not ok:raise ValueError(message)
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module);return module
def authenticate(records):
    need(len(records)>=10,'Full nonempty compact source closure')
    for row in records:
        relative=Path(row['path'])
        need(not relative.is_absolute() and '..' not in relative.parts,'Repository-relative owned input')
        need(digest(PACKAGE/relative)==row['sha256'],'Changed compact source: '+row['path'])

def run():
    pins=json.loads((HERE/'INPUTS.json').read_text(encoding='utf-8'))['files']
    authenticate(pins)
    module=load(PACKAGE/'arithmetic/verify.py','independent_compact_arithmetic')
    ordinary=module.run()
    frozen=json.loads((PACKAGE/'arithmetic/RESULT.json').read_text(encoding='utf-8'))
    need(ordinary==frozen,'Fresh ordinary arithmetic equals frozen receipt')
    child_code="import importlib.util,json,sys; p=sys.argv[1]; s=importlib.util.spec_from_file_location('isolated_compact',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps(m.run(),sort_keys=True))"
    child=subprocess.run([sys.executable,'-I','-O','-B','-X','utf8','-c',child_code,str(PACKAGE/'arithmetic/verify.py')],capture_output=True,text=True,encoding='utf-8',timeout=180,check=False)
    need(child.returncode==0,'Isolated optimized arithmetic failed: '+child.stderr)
    need(json.loads(child.stdout)==ordinary,'Ordinary and isolated optimized scientific receipts agree')
    need((PACKAGE/'arithmetic/controller.json').read_bytes()==(ROOT/'research/joint-helper-lattice/CONTROLLER.json').read_bytes(),'Unchanged public PR4470 controller')
    C=Q('.00302016');kappa=Q('.00302015');g=Q(1,100000001)
    d=(C-kappa-g)/6
    need(d==Q(1,60000000600000000)>0,'Exact independent outer slack')
    alpha_gap=Q(31,5*10**9);gamma=Q(98102,100000);delta=Q(959,1000)
    tail=lambda v:1/(1+v*alpha_gap)+2*gamma**v+2*delta**v
    need(tail(682)<1<tail(681),'Independent charged-tail and short-product tests')
    need(17**101<21**94,'Exact child/target logarithmic separation')
    need(2**(101-94)*(17**682)**101<=(145**682)**94,'Inherited shifted-exit factor is 128')
    eta=frozen['compiler']['eta'];eta_low=Q(eta['lower']);eta_high=Q(eta['upper']);theta=Q(94,101)
    need(theta**143<eta_low<=eta_high<theta**142,'Exact rational enclosing eta and previous-power rejection')
    need((100000001*5581+1)**143<2**5581,'Exact sufficient majorant at j=5581')
    need((100000001*5580+1)**143>=2**5580,'Previous majorant grid point rejects')
    need(100000001*5581==558100005581,'Exact uniform log-rank')
    controls={}
    for name,condition in [('short_tensor_681',tail(681)<1),('short_log_power_142',theta**142<eta_low),('zero_outer_slack',(C-kappa-Q(1,100000000))/6>0)]:
        need(not condition,'Independent numerical mutant must reject: '+name)
        controls[name]=True
    wrong={'helpers':dict(module.H),'paid':dict(module.N)};wrong['paid'][1]+=1
    try:module.run(wrong)
    except ValueError as error:
        need('Actual native replay agrees' in str(error),'Wrong-profile rejection must reach scientific binding')
        controls['wrong_actual_native_profile']=True
    else:raise ValueError('Wrong actual native profile accepted')
    badpins=deepcopy(pins);badpins[0]['sha256']='0'*64
    try:authenticate(badpins)
    except ValueError:controls['bad_source_pin']=True
    else:raise ValueError('Bad source pin accepted')
    authenticate(pins)
    return {'status':'PASS_READ_ONLY_INDEPENDENT_COMPACT_COMPILER','kappa':'0.00302015','same_predecessor_kappa':True,'uniform_N':'2^558100005581','outer_d':str(d),'normal_and_isolated_optimized_receipts_equal':True,'public_PR4470_controller_unchanged':True,'shifted_exit_factor':128,'all_independent_integer_rational_tests':True,'scientific_and_source_controls':controls,'source_sha256':{r['path']:r['sha256']for r in pins},'scope':'Smaller sufficient finite template, not a new kappa or a final integer-input threshold.'}

if __name__=='__main__':
    result=run();frozen=json.loads((HERE/'RECEIPT.json').read_text(encoding='utf-8'))
    need(result==frozen,'Deterministic independent receipt')
    print('PASS_READ_ONLY_INDEPENDENT_COMPACT_COMPILER N=2^558100005581 same_kappa=0.00302015')
