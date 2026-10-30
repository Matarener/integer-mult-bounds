#!/usr/bin/env python3
"""Independent exact Q(i) physical width-one quotient and version-span audit.

THU New Media Research Center; substantial OpenAI Codex assistance. Apache-2.0.
No finite-field rank or nonmembership routine is called. Distinct physical
operator matrices are expanded in their literal signed columns. A checked
coordinate phase gauge makes the operator matrix rational, so exact rational
row elimination proves its rank over Q(i), and hence over C. The single real
kernel relation is then used for exact version-span elimination.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
from collections import Counter
import argparse,json,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import native as source
source.source=source.read("source")
source.provider=source.read("provider")
source.canon=source.source["canonical"]
source.initialize(source.canon)
source.actual_replay=source.native_replay
import monomial as mon

def need(ok,message):
 if not ok:raise ValueError(message)

class RationalEchelon:
 """Independent sparse fraction row elimination; ordered leading pivots."""
 def __init__(self,track=False):
  self.rows={};self.certificates={};self.track=track;self.max_numerator_bits=0;self.max_denominator_bits=0
 def reduce(self,row,certificate=None):
  row={k:F(v) for k,v in row.items() if v};certificate=dict(certificate or {})
  while row:
   pivot=min(row)
   if pivot not in self.rows:return row,certificate
   multiple=row[pivot]
   for k,value in self.rows[pivot].items():
    z=row.get(k,F(0))-multiple*value
    if z:row[k]=z
    else:row.pop(k,None)
   if self.track:
    for k,value in self.certificates[pivot].items():
     z=certificate.get(k,F(0))-multiple*value
     if z:certificate[k]=z
     else:certificate.pop(k,None)
  return row,certificate
 def insert(self,row,label=None):
  v,c=self.reduce(row,{label:F(1)} if self.track else None)
  if not v:return False,c
  pivot=min(v);den=v[pivot];v={k:x/den for k,x in v.items()}
  self.rows[pivot]=v
  if self.track:self.certificates[pivot]={k:x/den for k,x in c.items()}
  self.max_numerator_bits=max(self.max_numerator_bits,max(abs(x.numerator).bit_length() for x in v.values()))
  self.max_denominator_bits=max(self.max_denominator_bits,max(x.denominator.bit_length() for x in v.values()))
  return True,c
 def copy(self):
  out=RationalEchelon(self.track);out.rows={p:r.copy() for p,r in self.rows.items()};out.certificates={p:r.copy() for p,r in self.certificates.items()}
  out.max_numerator_bits=self.max_numerator_bits;out.max_denominator_bits=self.max_denominator_bits;return out


def materialize():
 cases=[]
 for name,program,backward in [('provider-backward',source.provider['word'],True),('source-backward',source.source['programs']['backward'],True),('source-forward',source.source['programs']['forward'],False)]:
  rows,*_=source.actual_replay(source.canon,program,backward)
  cases.append((name,rows));print('REPLAY',name,len(rows),len(source.operators),flush=True)
 need(len(source.operators)==215,'Frozen replay must generate 215 actual operators')
 return cases


def physical_operator_rank():
 tables=[tuple(mon.decode(x)) for x in source.operators]
 # For each literal matrix coordinate all nonzero entries must be a real
 # multiple of one fixed Gaussian phase. Dividing that coordinate by i^p
 # is an invertible complex coordinate change; it is a proof device, never
 # a claimed physical instruction or an owner-code tensorization.
 gauge={};counts=Counter()
 for table in tables:
  need(len(table)==512 and len({x//4 for x in table})==512,'Literal monomial bijection')
  for col,value in enumerate(table):
   row,phase=divmod(value,4);key=512*col+row;parity=phase%2;counts[phase]+=1
   if key not in gauge:gauge[key]=parity
   need(gauge[key]==parity,'Common coordinate phase gauge must be consistent')
 span=RationalEchelon(track=True);relations=[]
 for n,table in enumerate(tables):
  vector={}
  for col,value in enumerate(table):
   row,phase=divmod(value,4);key=512*col+row;difference=(phase-gauge[key])%4
   need(difference in (0,2),'Exact rational coordinate after gauge')
   vector[key]=F(1 if difference==0 else -1)
  independent,certificate=span.insert(vector,n)
  if not independent:
   need(certificate,'Nontrivial exact kernel certificate');relations.append(certificate)
  if n%50==0:print('EXACT_OPERATOR',n,len(span.rows),flush=True)
 need(len(span.rows)==214 and len(relations)==1,'Exact Q(i) operator rank214, kernel dimension1')
 expected={157:F(1),51:F(1),156:F(-1),49:F(-1)}
 certificate=relations[0];last=max(certificate);normal={k:v/certificate[last] for k,v in certificate.items()}
 need(normal==expected,'Independently recovered exact four-term real relation')
 # Verify it again on un-gauged Gaussian-integer entries, without elimination.
 def residual(relation,mutation=None):
  out={}
  for n,c in relation.items():
   for col,value in enumerate(tables[n]):
    row,phase=divmod(value,4)
    if mutation is not None and n==mutation[0] and col==mutation[1]:phase=(phase+mutation[2])%4
    a,b=[(c,F(0)),(F(0),c),(-c,F(0)),(F(0),-c)][phase];key=512*col+row;u,v=out.get(key,(F(0),F(0)));u+=a;v+=b
    if u or v:out[key]=u,v
    else:out.pop(key,None)
  return out
 need(not residual(normal),'Exact relation on original complex physical entries')
 mutation=(157,1,1);wrong=residual(normal,mutation)
 need(wrong,'Wrong complex phase at one nonzero column must break relation')
 # This control preserves the permutation and the zero-address phase anchor.
 # It must fail the checked rational-gauge shortcut as well.
 row,phase=divmod(tables[157][1],4);coordinate=512+row
 need(gauge[coordinate]!=(phase+1)%2,'Wrong phase destroys checked common gauge')
 # The phase mutation changes the gauged operator by a nonzero complex
 # multiple of this unit coordinate. Prove that coordinate is outside the
 # old rational span, hence outside its Q(i) extension. The mutated family
 # has rank 215: this is a rank-sensitive phase control, not only a checksum.
 unit_remainder,_=span.reduce({coordinate:F(1)})
 need(unit_remainder,'Wrong-phase mutation must increase the exact physical rank')
 relation_encoded={str(k):str(v) for k,v in sorted(normal.items())}
 operator_data={'operator_count':215,'exact_rank_over_Q_i':214,'exact_rank_over_C':214,'exact_kernel_dimension':1,'kernel_relation':relation_encoded,'coordinate_phase_gauge':'Every fixed physical matrix coordinate has one shared phase parity, making all 215 columns rational after invertible coordinate scaling. Rational rank is unchanged under scalar extension Q -> Q(i) -> C.','distinct_physical_matrix_coordinates':len(gauge),'phase_exponent_counts':dict(sorted(counts.items())),'exact_pivot_coordinates':[[k//512,k%512] for k in span.rows],'basis_numerator_bits':span.max_numerator_bits,'basis_denominator_bits':span.max_denominator_bits,'wrong_phase_control':{'operator':157,'input_column':1,'phase_increment_mod4':1,'permutation_preserved':True,'zero_column_phase_anchor_preserved':True,'exact_relation_rejected':True,'rational_gauge_rejected':True,'exact_mutated_rank_over_Q_i':215,'unit_coordinate_outside_original_span':True,'nonzero_residual_coordinates':len(wrong)}}
 return normal,operator_data


def quotient_row(row,relation,index):
 pivot=max(relation);coefficient=relation[pivot];substitution={j:-c/coefficient for j,c in relation.items() if j!=pivot};out={}
 for (role,op),c in row.items():
  terms=substitution if op==pivot else {op:F(1)}
  for j,d in terms.items():
   key=(role,j);index.setdefault(key,len(index));z=out.get(key,F(0))+c*d
   if z:out[key]=z
   else:out.pop(key,None)
 return {index[k]:v for k,v in out.items()}


def version_rank(name,versions,relation):
 started=time.monotonic();index={};V=RationalEchelon();N=RationalEchelon()
 for n,row in enumerate(versions):
  vector=quotient_row(row,relation,index)
  reverse={v:k for k,v in index.items()}
  non_y={k:c for k,c in vector.items() if not (reverse[k][0][0]=='L' and 112<=reverse[k][0][1]<224)}
  V.insert(vector);N.insert(non_y)
  if n%1000==0:print('EXACT_QUOTIENT',name,n,len(V.rows),len(N.rows),round(time.monotonic()-started,3),flush=True)
 rank_V,rank_N=len(V.rows),len(N.rows)
 expected=546 if name=='provider-backward' else 554
 need(rank_V==rank_N==expected,'Exact physical quotient has no pure-Y direction')
 # Add one arbitrary original Y input. It has zero non-Y projection and
 # cannot already lie in V when rank(V)=rank(non-Y projection).
 y_key=(('L',112),0);j=index.setdefault(y_key,len(index));injected=V.copy();changed,_=injected.insert({j:F(1)})
 need(changed and len(injected.rows)==rank_V+1,'Positive pure-Y injection increases exact rank')
 need(len(injected.rows)-rank_N==1,'Injected quotient intersection dimension is exactly one')
 return {'name':name,'full_frame_versions':len(versions),'quotient_coordinates':len(index),'exact_rank_V_over_Q_i':rank_V,'exact_non_Y_projection_rank_over_Q_i':rank_N,'exact_pure_Y_any_physical_operator_dimension':rank_V-rank_N,'all_scalar_coefficients_after_operator_quotient_real_rational':True,'positive_pure_Y_identity_injection':{'rank_increase':1,'pure_Y_dimension_after_injection':1},'max_basis_numerator_bits':max(V.max_numerator_bits,N.max_numerator_bits),'max_basis_denominator_bits':max(V.max_denominator_bits,N.max_denominator_bits),'seconds':time.monotonic()-started}


def main(write=False):
 started=time.monotonic();cases=materialize();relation,operators=physical_operator_rank();checks=[]
 for name,versions in cases:
  row=version_rank(name,versions,relation);checks.append(row);print('CHECK',json.dumps(row,sort_keys=True),flush=True)
 pins={name:sha256((source.ROOT/rel).read_bytes()).hexdigest() for name,(rel,expected) in source.INPUTS.items()}
 result={'status':'PASS_INDEPENDENT_EXACT_WIDTH1_PHYSICAL_QUOTIENT','arithmetic':'Exact Fraction arithmetic; no finite-field rank or nonmembership shortcut. A checked coordinate phase gauge proves the Q(i) physical-operator rank using rational row elimination.','operators':operators,'checks':checks,'source_sha256':pins,'implementation_sha256':{x:sha256((HERE/x).read_bytes()).hexdigest() for x in ('native.py','monomial.py')},'seconds':time.monotonic()-started,'scope':'Width-one scalar span of all retained full-frame versions under the source replay. All actual signed-monomial matrix relations are quotiented exactly. No closure under arbitrary free left transports, modified native history, supplied correlated observations, all-width implementation, or new kappa is asserted.'}
 result['independent_script_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
 if write:(HERE/'INDEPENDENT-WIDTH1.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('PASS_INDEPENDENT_EXACT_WIDTH1_PHYSICAL_QUOTIENT',round(result['seconds'],3),flush=True)
 return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();main(args.write)
