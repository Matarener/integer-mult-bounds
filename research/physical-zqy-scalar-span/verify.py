#!/usr/bin/env python3
"""Source-bound, all-width physical scalar-span audit. Default replay is read-only.

THU New Media Research Center (@thu-nmrc); substantial OpenAI Codex assistance.
Apache-2.0. See PROOF.md for the quantified theorem and its restricted grammar.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import argparse,json,sys,time
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import native as N
import monomial as M
from rational import ExactSpan
import finite as C


def authenticate():
 pins=json.loads((HERE/'SOURCES.json').read_text())
 for row in pins['files']:
  if row['usage']!='input':continue
  raw=(N.ROOT/row['path']).read_bytes()
  N.need(sha256(raw).hexdigest()==row['sha256'],'input hash '+row['path'])
 return pins


def scalar_ranks(name,versions):
 index={};V=ExactSpan();projection=ExactSpan()
 for row in versions:
  v={index.setdefault(k,len(index)):q for k,q in row.items()}
  non_y={index[k]:q for k,q in row.items() if N.role_class(k)!='y'}
  V.add(v);projection.add(non_y)
 rank=len(V.piv)
 injected=index.setdefault((('L',112),0),len(index))
 N.need(V.add({injected:F(1)}),'positive pure-y injection')
 N.need(rank==len(projection.piv),'all-width group-coordinate projection injective')
 return {'name':name,'full_frame_versions':len(versions),'group_coordinate_count':len(index),
         'exact_group_rank':rank,'exact_group_non_Y_projection_rank':len(projection.piv),
         'positive_injection_rank':len(V.piv),'max_numerator_bits':V.max_num,'max_denominator_bits':V.max_den}


def calculate():
 authenticate();source=N.read('source');provider=N.read('provider');canon=source['canonical'];N.initialize(canon)
 case_input=[('provider-backward',provider['word'],True,4891,546),
             ('source-backward',source['programs']['backward'],True,5019,554),
             ('source-forward',source['programs']['forward'],False,4968,554)]
 cases=[];retained=[]
 for name,program,backward,count,rank in case_input:
  versions,rows,frames,full=N.native_replay(canon,program,backward)
  N.need(len(versions)==count,'complete frozen full-frame version count '+name)
  result=scalar_ranks(name,versions);N.need(result['exact_group_rank']==rank,'exact frozen span rank '+name)
  cases.append(result);retained.append(versions)
  print('PASS_EXACT_GROUP_SPAN',name,count,rank,flush=True)
 # No phase is silently converted into an ordinary scalar. All products retain literal columns.
 N.need(len(N.operators)==215 and all(M.decode(op)[0]==0 for op in N.operators),'complete zero-anchored signed operator set')
 one=C.operator_rank(N.operators)
 for result,versions in zip(cases,retained):
  physical=C.physical_projection_rank(versions)
  N.need(physical['rank_lower_non_Y_projection']==result['exact_group_rank'],'width-one projection lower bound equals exact upper bound')
  N.need(physical['rank_lower_V']==result['exact_group_rank'],'width-one complete rank agrees')
  N.need(physical['positive_control_rank']==result['exact_group_rank']+1,'width-one positive control')
  result['width_one_modular_rank_bounds']=physical
 two=C.tensor_square(N.operators)
 return {'schema':'physical-zqy-scalar-span/v1',
         'status':'PASS_ALL_WIDTH_PHYSICAL_NATIVE_SCALAR_SPAN_NO_NEW_KAPPA',
         'source_payload_sha256':sha256(__import__('gzip').decompress((N.ROOT/N.INPUTS['source'][0]).read_bytes())).hexdigest(),
         'cases':cases,'operator_certificate':one,'tensor_square_gram':two,
         'widths':'all positive integers; coefficients may depend on width and be complex',
         'scope':'Scalar linear combinations of all full-frame versions of these frozen native words; excludes arbitrary independently chosen free left maps and changed words.',
         'productive_or_paid_profile_change':False,'new_kappa':False,
         'controls':['injected pure-y identity raises rank in every case','wrong absolute phase breaks exact four-term relation']}


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
 start=time.monotonic();result=calculate();encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
 if args.write:(HERE/'RESULT.json').write_text(encoded)
 else:N.need(json.loads((HERE/'RESULT.json').read_text())==result,'committed result differs from fresh computation')
 print(result['status'], 'seconds',round(time.monotonic()-start,3),flush=True)
if __name__=='__main__':main()
