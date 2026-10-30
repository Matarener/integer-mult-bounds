"""All-width exact dyadic grid/size bounds from the actual whole-K streams.
No recursive-tariff, whole-caller, or new kappa claim. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import gzip,hashlib,json


def need(ok,message):
 if not ok:raise ValueError(message)


def dominated(a,b):
 """Affine a*f+b no greater than the other at every integer f>=1."""
 return a[0]<=b[0] and sum(a)<=sum(b)


def envelope(lines):
 lines=set(lines)
 return {x for x in lines if not any(y!=x and dominated(x,y) for y in lines)}


def check_monomials(stream):
 definitions=stream['definitions'];used=set()
 for event in stream['program']:
  if event[0] in ('MONOMIAL','BOUNDARY_MONOMIAL'):used.add(event[3])
  elif event[0]=='PAID_PATH':used|={event[-1]['before_monomial'],event[-1]['after_monomial']}
 need(used<=definitions.keys(),'all word definitions resolved')
 for word in (definitions[key] for key in used):
  for gate in word:
   need(gate[0] in ('P','D','X','phase'),'non-monomial hidden in a phase wrapper')
   if gate[0]=='P':need(len(gate[1])==25 and all(type(x)is int and 0<=x<1<<25 for x in gate[1]),'binary address-map shape')
   if gate[0]=='D':need(len(gate[1])==len(gate[2])==25 and all(type(x)is int for x in gate[2]),'integral Z4 phase shape')
   if gate[0] in ('X','phase'):need(type(gate[1])is int,'integral phase or XOR mask')
 for event in stream['program']:
  if event[0] in ('MONOMIAL','BOUNDARY_MONOMIAL'):need(event[3] in definitions,'resolved monomial definition')
  elif event[0]=='PAID_PATH':
   need(event[-1]['before_monomial'] in definitions and event[-1]['after_monomial'] in definitions,'resolved child wrappers')
 return len(used)

def replay(program,ports,backward):
 # Exponents measure denominator bits relative to the initial 2^-g grid.
 heights={(role,p):{(0,0)} for role in ('X','Y') for p in ports}
 # Positive polynomials in u=2^(f/2), multiplied by initial magnitude bound H.
 magnitude={(role,p):Counter({0:Q(1)}) for role in ('X','Y') for p in ports}
 peak_lines={(0,0)};peak_degree=0;peak_coefficient_sum=Q(1)
 counts=Counter();paid=Counter()
 for event in program:
  op=event[0];counts[op]+=1;target=tuple(event[1:3])
  need(target in heights,'named original owner')
  if op in ('MONOMIAL','BOUNDARY_MONOMIAL'):pass
  elif op=='PAID_PATH':
   spec=event[-1];rank=spec['rank'];need(rank==len(spec['child_axes']) and rank>0,'actual child rank')
   heights[target]={(a+rank,b) for a,b in heights[target]}
   magnitude[target]=Counter({power+rank:c for power,c in magnitude[target].items()});paid[rank]+=1
  elif op=='ADD':
   source=tuple(event[3:5]);need(source in heights and source!=target,'independent owner ADD')
   coefficient=Q(event[5],event[6]);den=coefficient.denominator;num=abs(coefficient.numerator)
   need(den&(den-1)==0 and num>0,'dyadic nonzero source coefficient')
   numerator_twos=(num&-num).bit_length()-1;extra=den.bit_length()-1-numerator_twos
   heights[target]=envelope(heights[target]|{(a,b+extra) for a,b in heights[source]})
   for power,c in magnitude[source].items():magnitude[target][power]+=abs(coefficient)*c
  else:raise ValueError('unpriced/unbound event '+op)
  peak_lines=envelope(peak_lines|heights[target])
  peak_degree=max(peak_degree,max(magnitude[target]))
  peak_coefficient_sum=max(peak_coefficient_sum,sum(magnitude[target].values()))
 # Simple all-f line certificates; backward exact envelope has one line.
 sufficient={(25,4)} if backward else {(24,0),(23,4)}
 need(all(any(dominated(line,bound) for bound in sufficient) for line in peak_lines),'universal exact grid bound')
 need(peak_degree<=(25 if backward else 24) and peak_coefficient_sum<=8,'universal amplitude bound')
 need(paid=={8:512,9:512,15:512,16:512},'complete actual cube paid profile')
 return {'events':len(program),'event_counts':dict(counts),'paid':dict(paid),
  'conservative_grid_upper_envelope':sorted(peak_lines),'sufficient_grid_envelope':sorted(sufficient),
  'magnitude_polynomial_degree':peak_degree,'magnitude_polynomial_coefficient_sum_upper':str(peak_coefficient_sum),
  'all_original_fields':len(heights),'coarse_grid_bound_samples':{str(f):max(a*f+b for a,b in peak_lines) for f in (1,2,3,4,8,16,32)},
  'scope':'All positive f symbolic sufficient dyadic grid and component magnitude, conditional only on the source stream exact native semantics; not machine/recursive cost.'}


def tight_grid(program,ports,backward,parity):
 # f=2*k+parity; k>=1 for even f, k>=0 for odd f.
 minimum_k=1-parity
 def dom(a,b):return a[0]<=b[0] and a[0]*minimum_k+a[1]<=b[0]*minimum_k+b[1]
 def env(lines):
  lines=set(lines);return {x for x in lines if not any(x!=y and dom(x,y) for y in lines)}
 heights={(role,p):{(0,0)} for role in ('X','Y') for p in ports};peak={(0,0)}
 for event in program:
  op=event[0];target=tuple(event[1:3])
  if op=='PAID_PATH':
   rank=event[-1]['rank'];heights[target]={(a+rank,b+(rank*parity+1)//2) for a,b in heights[target]}
  elif op=='ADD':
   coefficient=Q(event[5],event[6]);n,d=abs(coefficient.numerator),coefficient.denominator
   extra=d.bit_length()-1-((n&-n).bit_length()-1)
   heights[target]=env(heights[target]|{(a,b+extra) for a,b in heights[tuple(event[3:5])]})
  peak=env(peak|heights[target])
 bound={(25,4+13*parity)} if backward else ({(24,0),(23,4)} if parity==0 else {(24,13),(23,16)})
 need(all(any(dom(line,b) for b in bound) for line in peak),'tight all-width Gaussian-integer grid')
 return {'f_parity':parity,'k_minimum':minimum_k,'relative_grid_envelope_in_k':sorted(peak),'variable':'f=2*k+parity'}

def verify():
 root=Path(__file__).parent;pins=json.loads((root/'SOURCES.json').read_text(encoding='utf-8'))['files'];streams={}
 for pin in pins:
  raw=(root/pin['package_path']).read_bytes();need(hashlib.sha256(raw).hexdigest()==pin['sha256'],'immutable input source')
  payload=gzip.decompress(raw);need(hashlib.sha256(payload).hexdigest()==pin['payload_sha256'],'decompressed source')
  streams[pin['orientation']]=json.loads(payload)
 forward=streams['forward'];backward=streams['backward']
 need(forward['axis_dimension']==backward['axis_dimension']==25,'physical dimension')
 need(forward['port_order']==backward['port_order'],'same original source cube')
 nf=check_monomials(forward);nb=check_monomials(backward)
 f=replay(forward['program'],forward['port_order'],False);b=replay(backward['program'],backward['port_order'],True)
 f['phase_permutation_word_definitions_checked']=nf;b['phase_permutation_word_definitions_checked']=nb
 f['tight_gaussian_integer_grid_by_parity']=[tight_grid(forward['program'],forward['port_order'],False,p) for p in (0,1)]
 b['tight_gaussian_integer_grid_by_parity']=[tight_grid(backward['program'],backward['port_order'],True,p) for p in (0,1)]
 # Control: denominator 2^20 in a real scalar edge exceeds the claimed grid.
 import copy
 bad=copy.deepcopy(forward['program']);edge=next(e for e in bad if e[0]=='ADD');edge[6]=1<<20
 try:replay(bad,forward['port_order'],False)
 except ValueError:pass
 else:raise ValueError('increased scalar denominator was not detected')
 return {'status':'PASS_WHOLE_K_UNIVERSAL_EXACT_DYADIC_PRECISION','forward':f,'backward':b,
  'common_grid_bits':'g+ceil(25*f/2)+4','common_complex_magnitude_upper':'8*H*2^ceil(25*f/2)',
  'sufficient_signed_payload_bits':'g+2*ceil(25*f/2)+ceil(log2(H))+9, for H>=1',
  'required_rounding_error':'zero when the stated exact dyadic storage and arithmetic are used',
  'mutations':['increased actual scalar denominator rejected'],
  'not_claimed':['new kappa','all-family emitted phase replay','whole caller budget','constant 64-bit word size for growing f','unit-cost arbitrary precision','native kernel proof verification']}

if __name__=='__main__':print(json.dumps(verify(),indent=2))




