#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent endpoint certificate on the current PR3815/PR3802 construction.
Endpoint refinement by hexapode with Codex assistance. Retained engines and generic proof bodies by Dugongue, with substantial OpenAI Codex assistance. Outer integration follows
dataisfire PR3361; exact retained scientific engines keep their attribution.
"""
import argparse,ast,gzip,hashlib,json,os,subprocess,sys,tempfile,textwrap,types
from pathlib import Path
from fractions import Fraction as Q
P=Path(__file__).resolve().parent
S=P/'vendor/staged544-producer-return'
B=P/'vendor/staged544-clock-ceiling'
VENDOR_SHA='30ee97d3076de3b117c544496758d02609259f9543cf5f1e698faf70d8f89443'
PROFILE={1:7989840,2:2349000,3:749088,4:330480,5:69120,8:25920,48:137952}
DIGITS=80
PROOF_PINS={'CapCertificate.lean': 'b1ba8ad1b65eeecaddf34168456d2f9a89eed5f36212bfcfa24107aa8fbe4833', 'AnalyticCertificate.lean': '44b6c75086d95163e876563621676289f3c6348c584358106c301b6c8195ffaf'}

def need(condition,message):
 if not condition:raise ValueError(message)
def read(path):return json.loads(path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_bytes((json.dumps(value,indent=2,sort_keys=True)+'\n').encode())
def load(path,name):
 module=types.ModuleType(name);module.__file__=str(path)
 exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
 return module

def authenticate():
 need(sha(P/'VENDOR.json')==VENDOR_SHA,'vendor manifest and usage classes')
 records=read(P/'VENDOR.json')['files']
 expected={x['path']:x['sha256'] for x in records}
 actual={f.relative_to(P).as_posix():sha(f) for f in (P/'vendor').rglob('*') if f.is_file()}
 need(actual==expected,'exact complete vendor source inventory')
 need(not any(f.is_symlink() for f in (P/'vendor').rglob('*')),'regular retained inputs')

def arithmetic():
 authenticate()
 profile={int(r):n for r,n in read(B/'inputs/PROFILE.json').items()}
 need(profile==PROFILE and sum(r*n for r,n in profile.items())==65088*360,'complete fixed profile and rank mass')
 D=load(P/'dyadic_moment.py','new_dyadic');certificate=D.certify(profile,73,896*360,DIGITS)
 C=Q(certificate['lower']);high=Q(certificate['upper']);K=C-Q(1,10**102)-Q(1,10**126)
 need(sha(P/'PREDECESSOR-CLAIM.json')=='2b3a4ede0d77e4d9908f50f756559fa4a5f371f9d04a185a308641b601c8857a','pinned PR3857 claim')
 old=Q(read(P/'PREDECESSOR-CLAIM.json')['kappa'])
 need(old<K<C<high,'strict positive conditional improvement')
 R=load(S/'rational_price.py','credited_alternating_price');signed=dict(profile);signed[73]=-896*360
 below=R.interval(signed,C);above=R.interval(signed,high)
 need(below[1]<0<above[0],'unchanged alternating engine independently certifies both new signs')
 for r in (1,48):
  bad=dict(profile);bad[r]+=1
  need(D.DyadicMoment(bad,73,896*360).moment(C)[0]>1,'unpaid child must reject')
 return dict(profile=profile,complex_lower=str(C),complex_upper=str(high),kappa=str(K),previous=str(old),
             gain=str(K-old),certificate=certificate,alternating_signs=dict(accepted_upper=R.compact(below)['upper'],rejected_lower=R.compact(above)['lower']))

def finite(work):
 env=dict(os.environ,PYTHONPYCACHEPREFIX=str(work/'bytecode'));env.pop('PYTHONOPTIMIZE',None)
 run=subprocess.run([sys.executable,'-B',str(B/'verify.py')],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,timeout=180)
 need(run.returncode==0,'retained literal construction: '+run.stdout.decode('utf-8',errors='replace')[-1200:])
 baseline=json.loads(run.stdout)
 need(baseline['status']=='PASS_STAGED544_CHANGED_CLOCK_CEILING_OWNERS_AND_PRICE','actual predecessor finite status')
 need({int(r):n for r,n in baseline['profile'].items()}==PROFILE,'fresh actual owner profile')
 C=load(S/'audit_core.py','credited_arbitrary_dirty_interpreter');A=load(S/'audit_verify.py','credited_semantics_adapter')
 receipt=read(P/'vendor/native/NATIVE-RECEIPT.json');words={}
 for tag in ('base','extra'):
  path=S/'words'/('BORROW-WORD-43'+tag+'.json.gz');word=json.loads(gzip.decompress(path.read_bytes()))
  C.hygiene(word);local,widths,*_=C.frame_bill(word)
  need(local=={1:2440,2:725,3:224,4:102,5:20,8:8},'actual local paid bill')
  need(widths=={4:26,5:2,6:18,7:53,8:96,9:213} and word['cleanup']==C.derive_cleanup(word),'actual widths and literal cleanup')
  native=read(S/'evidence'/('NATIVE-'+tag+'.json'))
  need(native['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY' and native['word_sha256']==sha(path),'retained native evidence binds exact word')
  need([x['step'] for x in native['steps']]==['native','ledgers','local-replay','wrappers','phases'] and all(x['exit_code']==0 for x in native['steps']),'retained native stages')
  binding=receipt['providers'][tag]
  need(binding['word_sha256']==sha(path) and binding['complete_native_files']['local/CANONICAL-WORD.json.gz']==sha(S/'inputs'/('NATIVE-'+tag+'.json.gz')),'retained archive receipt binds actual canonical native frames')
  words[tag]=dict(semantics=A.semantics(C,word),local=local,widths=widths,word_sha256=sha(path))
 return dict(actual_clock_owners_and_ceiling=baseline,actual_dirty_words=words,
             native_scope='Authenticated retained PR3734 native evidence; no fresh native-chain rebuild or omitted cache-byte authentication')

def bootstrap(C):
 source=(P/'vendor/bootstrap/assemble.py').read_text(encoding='utf-8')
 node=next(n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.FunctionDef) and n.name=='_outer_witness_raw')
 body=textwrap.dedent('\n'.join(source.splitlines()[node.lineno-1:node.end_lineno])+'\n')
 env=dict(Q=Q,mpz=int,hashlib=hashlib,PAYLOAD=2048,c=Q('0.001733427039589844234749'),
  SPEC=dict(outer_refinement=dict(endpoint_digits=80,grid_digits=39,margin_digits=49,bootstrap_steps=12)),
  A=load(P/'vendor/bootstrap/outer.py','credited_47_row_engine'))
 exec(compile(body,'<unchanged carried bootstrap>','exec'),env)
 k,cuts,outer,controls=env['_outer_witness_raw'](C)
 need(len(outer['strict_constraints'])==47 and all(v>0 for v in outer['strict_constraints'].values()),'47 strict carried-bootstrap rows')
 need(len(cuts)==13 and len(controls)==4,'12 carried stages and four controls')
 return dict(legacy_balanced_kappa=str(k),cutoffs=cuts,controls=controls,strict_constraints={n:str(v) for n,v in outer['strict_constraints'].items()})

def outer(a,work):
 outerdir=work/'outer';outerdir.mkdir();(work/'new').mkdir()
 for name in ('check_ledger.py','independent_check.py'):
  (outerdir/name).write_bytes((S/'outer-replay/outer'/name).read_bytes())
 C=Q(a['complex_lower']);K=Q(a['kappa'])
 save(work/'new/SPEC.json',dict(geometry=dict(dimension=73,replicas=360),expected=dict(complex_lower=str(C),kappa=a['previous'],global_profile=a['profile'],live=896*360),outer_refinement=dict(endpoint_digits=80)))
 save(work/'CLAIM.json',dict(kappa=str(K),scope='Conditional fixed-supplier endpoint refinement'))
 save(outerdir/'B.json',dict(b=str(C-Q(1,10**160)),b_above_endpoint=a['complex_upper'],profile=a['profile'],live=896*360))
 for name in ('check_ledger.py','independent_check.py'):
  with (work/(name+'.log')).open('wb') as log:
   subprocess.run([sys.executable,'-B','-X','pycache_prefix='+str(work/'outer-bytecode'),str(outerdir/name)],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
 ledger=read(outerdir/'LEDGER.json');row=ledger['rows']['struct_boundary_radix_union'];balance=read(outerdir/'INDEPENDENT.json')
 need(Q(row['kappa']['rational'])==K,'derived modern endpoint')
 need(len(row['strict_checks'])==63 and all(Q(v['rational'])>0 for v in row['strict_checks'].values()),'63 strict modern rows')
 controls=ledger['rejecting_controls']['struct_boundary_radix_union']
 need(len(controls)==17 and all(v and all(Q(w['rational'])<=0 for w in v.values()) for v in controls.values()),'17 actual rejection controls')
 need(balance['status']=='PASS_INDEPENDENT_BALANCE_DERIVATION' and Q(balance['rows']['struct_boundary_radix_union']['kappa'])==K,'independent balance derivation')
 return dict(ledger=ledger,independent=balance)

def check_lean_data(a):
 for name,digest in PROOF_PINS.items():need(sha(P/'lean'/name)==digest,'checked proof bytes '+name)
 source=(P/'lean/CapCertificate.lean').read_text(encoding='utf-8');weights=a['certificate']['weights'];ranks=sorted(a['profile'])
 counts='def coefficient : Fin 7 → ℚ := !['+', '.join(str(r*a['profile'][r]) for r in ranks)+']'
 bounds='def upper : Fin 7 → ℚ := !['+', '.join('('+weights[str(r)]['upper']+' / '+weights[str(r)]['scale']+')' for r in ranks)+']'
 need(source.count(counts)==1 and source.count(bounds)==1,'concrete Lean numbers match regenerated certificate')
 need('sorry' not in source and 'native_decide' not in source,'proof placeholders or native trust shortcut')
 analytic=(P/'lean/AnalyticCertificate.lean').read_text(encoding='utf-8');endpoint=Q(a['complex_lower'])
 need(('def endpoint : ℚ := '+str(endpoint.numerator)+' / '+str(endpoint.denominator)) in analytic,'formal actual endpoint')
 data=read(P/'FORMAL-DATA.json');need(data['endpoint']==a['complex_lower'] and data['log_degree']==60 and data['exp_degree']==26,'formal data scope')
 need('sorry' not in analytic and 'native_decide' not in analytic,'analytic proof placeholder or native trust shortcut')
 for field,name in [('log_upper','logUpper'),('weight_upper','upper'),('root_upper','rootUpper')]:
  values=[Q(data[field][str(r)]) for r in ranks]
  declaration='def '+name+' : Fin 7 → ℚ := !['+', '.join('('+str(v.numerator)+' / '+str(v.denominator)+')' for v in values)+']'
  need(analytic.count(declaration)==1,'formal data declaration '+name)

def reproduce(a,work):
 return dict(status='PASS_STAGED544_CURRENT_CONDITIONAL_ENDPOINT',arithmetic=a,
  finite=finite(work),bootstrap=bootstrap(Q(a['complex_lower'])),outer=outer(a,work),
  scope='Conditional unchanged PR3815/PR3802 supplier; all inherited general realization, compiler, hosting, precision, analytic and BIT assumptions remain')

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path);args=ap.parse_args()
 need(not sys.flags.optimize,'inherited checkers require enabled assertions')
 need(not args.output or not args.output.exists(),'output must be fresh')
 a=arithmetic();check_lean_data(a);claim=read(P/'CLAIM.json')
 for key in ('complex_lower','complex_upper','kappa','previous','gain'):need(claim[key]==a[key],'public exact claim '+key)
 need(claim['endpoint_digits']==80 and claim['fresh_native_replay'] is False and claim['selected_frontier_changed'] is False,'public scope flags')
 need(claim['replicas']==360 and claim['physical']==323069 and claim['private_zero_buffers']==91,'complete fixed stock')
 with tempfile.TemporaryDirectory(prefix='staged544-endpoint-') as folder:
  result=reproduce(a,Path(folder));authenticate()
  encode=lambda x:json.dumps(json.loads(json.dumps(x)),sort_keys=True,separators=(',',':'))
  need(encode(result)==encode(read(P/'RESULT.json')),'complete regenerated scoped result')
  if args.output:save(args.output,result)
 print(result['status'],'gain',a['gain'])
if __name__=='__main__':main()
