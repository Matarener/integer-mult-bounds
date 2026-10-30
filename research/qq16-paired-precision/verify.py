#!/usr/bin/env python3
"""Complete common-format audit of frozen QQ16 recovery words. Apache-2.0.
Chris R / Clear1nsight with substantial OpenAI Codex assistance.
No predecessor executable is imported. Source semantics are inherited with pins.
"""
import argparse,hashlib,json,types
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
STATUS='PASS_QQ16_PAIRED_PRECISION_CONDITIONAL'
def need(ok,why):
 if not ok:raise ValueError(why)
def unique(pairs):
 out={}
 for k,v in pairs:
  need(k not in out,'duplicate JSON key:'+k);out[k]=v
 return out
def parse(raw):return json.loads(raw,object_pairs_hook=unique)
def typed(v):
 if isinstance(v,dict):return ('dict',tuple((k,typed(x)) for k,x in sorted(v.items())))
 if isinstance(v,list):return ('list',tuple(map(typed,v)))
 return (type(v).__name__,v)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def module(name):
 path=HERE/name;m=types.ModuleType(name.replace('.','_'));m.__file__=str(path)
 exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
def authenticate():
 raw=(HERE/'SOURCES.json').read_bytes()
 need(sha(raw)=='ebb8c000a803b2a39f7bea7b206bad36bdbfd265081934affbba04fbb6b2a703','source manifest integrity')
 inputs={}
 for r in parse(raw)['files']:
  if r['usage']!='input':continue
  data=(ROOT/r['path']).read_bytes()
  need(sha(data)==r['sha256'] and blob(data)==r['git_blob'],'source integrity:'+r['path'])
  inputs[r['path']]=r['sha256']
 need(len(inputs)==5,'complete declared canonical input set')
 raw=(HERE/'PREDECESSORS.json').read_bytes()
 need(sha(raw)=='72fe4f1f3c56e07407e1bd37a3a075baf95f9c046f5251dceb2dbf75ee684b88','predecessor manifest integrity')
 retained={}
 for r in parse(raw)['files']:
  data=(HERE/r['local']).read_bytes()
  need(sha(data)==r['sha256'] and blob(data)==r['git_blob'],'retained source integrity:'+r['local'])
  retained[r['local']]={'head':r['head'],'sha256':r['sha256']}
 need(len(retained)==5,'complete retained set')
 return inputs,retained

def gaussian_checks():
 """Independent two-site rational Cq oracle against integer exact halves."""
 count=0;norm_witness=None;grid_witness=None
 for a,b,c,d in product(range(-2,3),repeat=4):
  for sign in (1,-1):
   # Physical real/imaginary component formulas; stored quantum is h/2.
   s=(2*(a+c),2*(b+d));delta=(2*(a-c),2*(b-d))
   numerators=(s[0]-sign*delta[1],s[1]+sign*delta[0],s[0]+sign*delta[1],s[1]-sign*delta[0])
   need(all(n%2==0 for n in numerators),'exact native divisibility')
   got=tuple(Q(n//2,2) for n in numerators)
   expected=(Q(a+c-sign*(b-d),2),Q(b+d+sign*(a-c),2),Q(a+c+sign*(b-d),2),Q(b+d-sign*(a-c),2))
   need(got==expected,'signed native numeric kernel')
   L=max(abs(v) for v in (a,b,c,d))
   need(all(abs(v)<=4*L for v in (Q(n,2) for n in numerators)),'cross numerator bound')
   need(all(abs(v)<=2*L for v in got),'native output bound')
   if (a,b,c,d,sign)==(1,1,1,-1,1):norm_witness=got
   if (a,b,c,d,sign)==(1,0,0,0,1):grid_witness=got
   count+=1
 need(any(v.denominator==2 for v in grid_witness),'halving seed')
 # Attained local values refute tempting but invalid componentwise norm-one
 # and an unchanged coarse h grid, without claiming global format minimality.
 need(norm_witness==(Q(0),Q(0),Q(2),Q(0)) and max(map(abs,norm_witness))>1,'norm-one control')
 return {'signed_two_site_cases':count,'native_component_output_factor':2,'cross_numerator_factor':4,
         'controls':['x=1+i,y=1-i gives a component2: norm-one assumption fails','x=1,y=0 gives half-integers: unrefined unit grid is not closed'],
         'scope':'Elementary signed Gaussian reference. Tensor/cover/native recipe semantics inherited; this is not an implementation of a recursive child tariff.'}

def reject_controls(R,E,C,B,candidate,baseline,construction):
 controls=[]
 def reject(label,call):
  try:call()
  except (ValueError,KeyError):controls.append(label);return
  raise ValueError('accepted control:'+label)
 w=deepcopy(candidate);w.pop(w.index(['clear','Z11','current']))
 reject('dirty E read',lambda:R.audit(w))
 w=deepcopy(candidate);w[w.index(['add','Z10','Z11','1'])][3]='2'
 reject('unsupported scalar',lambda:R.audit(w))
 w=deepcopy(candidate);w.insert(next(i for i,e in enumerate(w) if e[0]=='line'),['begin','illegal',8])
 reject('native inside private scope',lambda:R.audit(w))
 w=deepcopy(candidate);w[w.index(['add','Z10','Z11','1'])][3]='-1'
 reject('changed shared sum',lambda:E.audit(baseline,w,construction))
 w=deepcopy(candidate);w.pop(next(i for i,e in enumerate(w) if e[0]=='line'))
 reject('missing native error/cost contribution',lambda:C.audit(baseline,w))
 w=deepcopy(candidate);i=w.index(['map','Z11',2,87,False]) if ['map','Z11',2,87,False] in w else next(i for i,e in enumerate(w) if e[0]=='map' and i>1700);w[i][3]+=1
 reject('changed captured-source recipe',lambda:B.audit(baseline,w))
 w=deepcopy(candidate);_,_,i=B.cut(w);w.pop(i+18)
 reject('missing paid tenth restoration',lambda:B.audit(baseline,w))
 return controls

def compute():
 inputs,retained=authenticate() # Before any numerical analyzer executes.
 candidate=parse((HERE/'vendor/PR4106-WORD.json').read_text())
 baseline=parse((HERE/'vendor/PR4015-WORD.json').read_text())
 construction=parse((HERE/'vendor/PR4106-CONSTRUCTION.json').read_text())
 R=module('range.py');E=module('rounding.py');C=module('numeric-cost.py');I=module('independent.py');B=module('binding.py')
 ranges=R.compare(candidate,baseline)
 need(typed(parse((HERE/'RANGE.json').read_text()))==typed(ranges),'range receipt mismatch')
 rounding=E.audit(baseline,candidate,construction)
 need(typed(parse((HERE/'ROUNDING.json').read_text()))==typed(rounding),'rounding receipt mismatch')
 costs=C.audit(baseline,candidate);poly=I.compare(candidate,baseline);binding=B.audit(baseline,candidate)
 need(ranges['same_sufficient_quantum'] and ranges['same_sufficient_width'] and ranges['same_final_component_envelopes'],'common format')
 for r in (ranges['candidate'],ranges['baseline']):
  need((r['max_M'],r['max_g'],r['max_a'],r['max_b'])==('171043',9,3,3),'all-depth constants')
  need(r['signed_width']=={'P_coefficient':1,'constant':28,'t_coefficient':6},'signed width')
 need(rounding['all_224_endpoint_envelopes_equal'],'rounded envelope')
 # Inspect the exact coefficient enclosure, keeping x=2^lambda distinct from
 # the independent range certificate's x=2^(lambda-1).
 at_one={'entry':Q(0),'scalar':Q(0),'native':Q(0)}
 for kind,degree,c in rounding['whole_word_logical_cut_coefficient_envelope']:
  at_one[kind]+=Q(c)*2**degree
 need(at_one=={'entry':182803,'scalar':263970,'native':91185},'lambda1 error headroom gate')
 headroom=2**18-171043;need(headroom==91101,'range headroom')
 primitives=gaussian_checks()
 controls=reject_controls(R,E,C,B,candidate,baseline,construction)
 result={'status':STATUS,'source_inputs':inputs,'retained':retained,
 'question':'Does the frozen paired word require extra precision that repays800 scalar allowance?',
 'answer':'No extra width in the declared common sufficient exact-reference format. Actual recursive-child/caller/physical implementation remains conditional, not admitted.',
 'exact_format':{'input':'h=2^z,z integer;P>=0 integer;each borrowed real/imaginary component in hZ,abs<2^P*h;owned/private dirt unread untilCLEAR;lambda>=1 integer',
                 't':'lambda-1','q':'h*2^(-9-3t)','signed_component_bits':'P+28+6t','new_minus_baseline_bits':0,'arithmetic_residual':'zero for permitted pair-first exact numerical reference',
                 'optimality':'Sufficient uniform format; no minimality or optimized variable-precision dominance claim'},
 'same_width_costs':{'logical_allowance_before':26944,'logical_allowance_after':26144,'logical_difference':800,
                    'numeric_before':'(12352+2240lambda)N','numeric_after':'(12152+2240lambda)N','numeric_difference':'200N real-component additions/subtractions at common W',
                    'N':'2^(73lambda) complex coordinates per owner','actual_recursive_child_tariff':'unknown; pair-first numerical reference is not free substitution'},
 'conditional_producer_composition':{'inherited_producer_q':'h*2^(-71-19t)','inherited_producer_width':'P+215+38t','decoder_entry_P':'P+214+38t',
                                    'joint_q':'h*2^(-80-22t)','joint_width':'P+242+44t',
                                    'scope':'Algebraic substitution of source producer sufficient format into new decoder entry theorem. Producer theorem/source semantics inherited, not rerun; actual selected provider/caller linkage and conversion costs unestablished.'},
 'rounded_logical_cut_headroom':{'general':'E_entry(lambda)*epsilon+E_scalar(lambda)*eta+E_native(lambda)*nu < 91101*(2^P*h)*2^(3*(lambda-1))',
                               'lambda1':'182803epsilon+263970eta+91185nu < 91101*(2^P*h)',
                               'scope':'Sufficient common-width logical-cut nonoverflow margin only. Actual eta/nu and native interiors/private cleanup remain separate premises.'},
 'fixed_point_word_binding':binding,
 'fixed_point_relative_identity':'Exact changed unitADDs,nooverflow,common q,deterministic isolated bank-independent native/map/quarter callbacks imply identical captured sources,queries and downstream outputs. Existing common defects do not become accuracy guarantees.',
 'floating_countermodel':rounding['rounded_query_witness'],
 'checks':{'range_observations':ranges['candidate']['observation_count'],'independent_polynomial_observations':poly['candidate']['observations'],
           'explicit_coordinate_depths':[1,2,3,8],'all224_endpoint_error_polynomials_equal':True,'integer_query_regressions':rounding['fixed_point_query_regression_cases'],
           'Gaussian_reference':primitives,'negative_controls':controls},
 'scope':'Exact/common-grid reference plus conditional error/bit-cost comparisons; endpoint/frame identity inherited from frozen4106/4015. No predecessor executable imported. No actual recursive supplier admission, physical gain, human/formal proof or newkappa.'}
 return result,costs,poly

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args()
 names=('RESULT.json','COST.json','POLYNOMIAL.json')
 if a.write:need(not any((HERE/n).exists() for n in names),'refuse overwrite')
 objects=compute()
 for n,obj in zip(names,objects):
  if a.write:
   with (HERE/n).open('x') as f:f.write(json.dumps(obj,indent=2,sort_keys=True)+'\n')
  else:need(typed(parse((HERE/n).read_text()))==typed(obj),'whole typed receipt mismatch:'+n)
 print(STATUS);print('same_q=h2^(-9-3t) same_W=P+28+6t logical_saving800 numeric_saving200N conditional_no_new_kappa')
if __name__=='__main__':main()
