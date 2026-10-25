"""Finite field-collection l2 constants and structured ordinary invoice.

These bounds concern additive errors measured in l2 of entire fields, not a
coordinate rounding allocation or a Turing-machine supplier admission.
"""
import argparse,hashlib,importlib.util,json,math,sys
from fractions import Fraction as F
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def need(q,s):
 if not q:raise ValueError(s)
def canonical(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def sqrtceil(x):
 z=(x.numerator+x.denominator-1)//x.denominator;r=math.isqrt(z);return r if r*r>=z else r+1
def add(*ds):
 out={}
 for d in ds:
  for k,v in d.items():out[k]=out.get(k,0)+v
 return out
def times(n,d):return{k:n*v for k,v in d.items()}
def calculate():
 spec=importlib.util.spec_from_file_location('precision120_prefix',HERE/'inputs/prefix/check.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
 pr=p.calculate();need(pr==json.loads((HERE/'inputs/prefix/RECEIPT.json').read_bytes()),'four exact actual word prefix receipts')
 need(pr['program_canonical_sha256']=='0b526f1a38a73a82ae66e1b0182ed2fa8c14e16d703cd38fff4dc491d3b7c15b','same exact modal kernel science')
 bound=max(F(q['whole_three_axis_l2_amplification_squared_upper'])for q in pr['orientations'].values());S=sqrtceil(bound)
 need(S*S>=bound,'integer whole three-axis prefix bound')
 # A complete scalar K stage uses zero scratch, partial row accumulations,
 # SWAP, CLEAR. All partial coefficient row/column sums are <=7. Thus its
 # extended main+scratch prefix norm is <=sqrt(1+7²)<8, and so is its adjoint.
 spec=importlib.util.spec_from_file_location('precision120_modes',HERE/'modes120.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 root=m.loadgz('K-PROGRAM.json.gz',m.ROOT_PIN);rows=root['literal_scalar_K_rows'];col={};rmax=F()
 for row in rows.values():
  rmax=max(rmax,sum(abs(F(num,den))for j,num,den in row))
  for j,num,den in row:col[j]=col.get(j,F())+abs(F(num,den))
 cmax=max(col.values());need(rmax==cmax==7,'actual512 scalar K row and column l1=7')
 # Uniform bound covers E, Ei, and their primitive linear adjoints. Four
 # recoder orientations are needed because transpose reverses the row word.
 C=8*1351*S*S
 Q=2*1351*S**4
 M=16*C*C*Q
 whole=M**3*C**3
 V=120**3;h=22016;axis_batches=3*120**2
 code={'ADD':2*axis_batches*7042+76*V,'SCALE':2*axis_batches*84+h,'SWAP':2*axis_batches*91+V,'P':2*V,'D':2*V,'OWN_ZERO':V,'CLEAR':V}
 query={'ADD':4*axis_batches*7042+2*h,'SCALE':4*axis_batches*84,'SWAP':4*axis_batches*91,'P':4*V,'D':4*V,'COPY':h,'OWN_ZERO':h,'CLEAR':2*h}
 native={'ADD':77*V,'P':15*V,'D':15*V,'X':20*V,'phase':6*V,'COPY':V,'OWN_ZERO':V,'CLEAR':2*V}
 module=add(times(2,code),query,native)
 n3=add(times(3,module),times(3,code),{'SWAP':V,'SCALE':V})
 logs={name:value.bit_length()for name,value in [('three_axis_stack',S),('ordinary_code',C),('query_pair',Q),('local_module',M),('N3_with_three_positive_exit_codes',whole)]}
 r={'schema':'full120-positive-E-field-l2-and-ordinary-tariff/v1','status':'PASS_FINITE_FIELD_L2_CONSTANTS_AND_STRUCTURED_INVOICE','actual_kernel_prefix_receipt_sha256':hashlib.sha256(canonical(pr)).hexdigest(),'three_axis_recoder_squared_bound':str(bound),'three_axis_recoder_integer_norm_bound':S,'K_partial_extended_stage_norm_bound':8,'actual_K_row_l1':str(rmax),'actual_K_column_l1':str(cmax),'max_A_or_Ainverse_sector_scale':1351,'code_prefix_suffix_norm_bound':str(C),'query_gather_scatter_prefix_suffix_norm_bound':str(Q),'local_module_prefix_suffix_norm_bound':str(M),'three_modules_plus_three_positive_exit_codes_norm_bound':str(whole),'strict_power_of_two_log2_upper':logs,'error_ABI':'For any fixed emitted primitive word with L additive error injections, each of whole-field-collection l2 norm <=epsilon, output l2 error <=L*M*epsilon for a local module (or L*whole*epsilon for the N3 prefix). Paid Gaussian and signed address monomial operations are unitary at every positive width. Prefix/suffix bounds include linear adjoint orientations and owned zero/COPY/CLEAR.','ordinary_E_or_inverse_code':code,'ordinary_query_or_adjoint_upper':query,'ordinary_native_inverse_transpose_boundaries_upper':native,'ordinary_local_module_upper':module,'ordinary_N3_plus_positive_exit_upper':n3,'paid_N3':{str(r):3*V for r in[8,9,15,16]}|{'25':3*h},'owned_local_and_N3_peak_upper':V+h+512,'ordinary_normalizer_contract':'The odd3 actual constructor uses one ordinary P and one real D for each L or L inverse; the base120 normalizers can have one extra P, counted literally in MACROS120.','scope':'Bounds are finite constants independent of positive address field width, measured in l2 of the collection of whole fields. Per-coordinate rounding can incur a square-root dimension factor and requires a separate precision allocation. No all-size TM/storage theorem, negative terminal decoding, target moment or exponent admission is claimed.'}
 return r
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r=calculate()
 if a.write:(HERE/'PRECISION120.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
 else:need(json.loads((HERE/'PRECISION120.json').read_bytes())==r,'read-only precision and tariff receipt')
 print(json.dumps(r,sort_keys=True))
