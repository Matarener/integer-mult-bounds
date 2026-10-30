"""Two exact moment engines and positive-fee finite ordinary bootstrap.

Adapted from ai-nanachi PR5512 ordinary.py for Dugongue PR5657 refinements and the audited PR5662 word.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

Uses the retained PR4814 finite acyclic bootstrap, with the new literal
G20 refined-source invoice. No multiplication-kappa update is claimed.
"""
from fractions import Fraction as F
from pathlib import Path
import importlib.util,sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import integration as L
from strict_margins import tensor_degree, compiler_cutoffs, below_grid, controls
R=L.R;S=L.S
def need(c,m):
 if not c:raise ValueError(m)
def load(n,p):
 spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);sys.modules[n]=m;spec.loader.exec_module(m);return m
def enc(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {str(k):enc(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [enc(v)for v in x]
 return x
def ceil(q):return -((-q.numerator)//q.denominator)
def fee_bounds(invoice,glob,H1,v):
 n=invoice['originals'];M=invoice['QUERYs'];owned=invoice['owned_allocated'];ops=glob['operation_counts'];park=4*(n+owned)*M
 routes=7548+7248;scans=ops['ADD']+ops['OWNED_CLEAR']+ops['OWNED_ZERO_HEADER']+ops['WHOLE_ZERO_FRAME']+2*owned;raw=glob['expanded_event_count'];matcher=L.read(R/'MATCHER.json');matcher_terms=matcher['global_occurrences']*matcher['paired_address_coefficient_terms_per_call'];base=scans+park+routes+raw+M*(32*127**2+8*127**3)+matcher_terms
 need(n==11166 and M==56547 and owned==39 and base<2**64,'Actual retained originals,39owned and positive complete finite fees')
 need(glob['majorant_bits']<1024 and matcher['max_numerator_bits']<1024,'Fresh positive majorant and fixed matrix height')
 need(v>=1024 and v%1024==0 and 256*v>=4*v*64,'Explicit tensor count envelope')
 return{'status':'PASS_POSITIVE_NEW_FINITE_FEE_AND_STOCK_SCHEMA','base_counts':{'raw_records':raw,'new_matcher_coefficient_terms':matcher_terms,'all_XOR_CLEAR_INIT_zeroheader_passes':scans,'parent_parking_FIELD_passes':park,'internal_and_wholejob_routes':routes,'coarse_primitive_count_with_dimension_work':base,'strict_upper':2**64,'all_owned_allocated':owned,'owned_productive_credit':0},
 'fixed_tensor_unit':{'v':v,'K':'2^'+str(256*v),'meaning':'Bounds fixed integer ranks, all role/round/operation inventories after tensoring, charged target completion and charged paid splitting.'},
 'finite_compiler':{'N':'2^'+str(H1),'J(n)':'(n+1)^4*K^(4*n+4)','A(1)':'K^4','A(n)':'(J(n)+2)^4*(A(n-1)+2)^(4*n+8)','counts':'Productive roles B_N, paid leaves P_N, instances and primitive descriptions <=A(N). Each compiled instance gets39distinct owned banks; C_N<=39*A(N). Denominator replication product <=A(n-1)^(n-1).'},
 'height_prime':{'base_height_bits':1024,'T':'(2*N+2)^4*(A(N)+2)^2','H':'1026*4^(T+1)','q':'Choose odd prime q>max(2^60*N^5,2^(2*H)) avoiding every finitely compiled denominator/rank witness. All QQ matrices and relative SOURCE projectors compiled before choice.'},
 'all_in_fixed_primitive_fee':{'F':'39*(q+2)^(32*(N+1)^2)*(A(N)+2)^8','actual_cost':'F times positive maximum of the retained stream/route/normalizer/completed-backend constants, fixed anew at each finite level. No primitive has cost0 or a claimed universal cost1.','parking':'4*(B_N+C_N) positive FIELD passes per child plus initialization/teardown, with C_N<=39*A(N); F dominates their products.','bad_classes':'<=32*N^2 ordinary calls charged separately by the retained moment/cover argument.'},
 'stock':{'reserve':'[B_N*|GL_N(F_q)|*q^(N^2*(w-1))]^D*S_completed_backend','D':'floor(log_N ceil(e/w))+1','borrowed_digits':'D*(N^2*(w-1)+ceil(log_q(B_N*|GL_N(F_q)|)))+ceil(log_q S_completed_backend)+1 =O_new(w loge)','ownership':'All39whole owned banks for EVERY compiled instance, including suspended ones, get distinct tags; full entry/exit CLEAR charged. No ancestor region is swept or external zero stock assumed.'},
 'eventual_threshold':{'K_j':'At least16 times sum of F*positive retained primitive constants, reserve/adapter bounds and already frozen backend constant completed at all widths by finite fallback.','eta_j':'min(rho-a_j,1-rho-a_j,a_j-b_j)>0','e_j':'Fresh integer dominating E_backend^(ceil(2/rho)), borrow threshold, ceil((32*K_j/eta_j)^(ceil(8/eta_j)))+2^(ceil(8/eta_j)).','scope':'Constructive finite threshold schema under retained native/compiler/ROW/precision/tape premises. Winning uniform program and decimal threshold are not materialized.'}}
def run():
 invoice=L.read(R/'INVOICE.json');glob=L.read(R/'GLOBAL-RESULT.json');P={int(k):v for k,v in invoice['paid'].items()};T={int(k):v for k,v in invoice['targets'].items()}
 need(sum(T.values())==11166 and sum(P.values())==56547 and T.get(4,0)==0 and T[8]==7614 and P[7]==162,'Actual complete new target/paid bill')
 E=load('nine_credited_interval',S/'ordinary-certificate/inputs/credited_intervals.py');I=load('nine_independent_series',S/'ordinary-certificate/inputs/separate_series.py')
 tested=F('.00349780457954');uniform=F('.00349780457953');cover_gap=F(1,10**14);rho=F(1,100);reserve=F(1,2**48);v=tensor_degree(reserve);t=1-tested;u=F(1,5)
 target=E.moment(T,t);paid=E.moment(P,t);alpha=E.divide(paid,target);gamma=E.divide(E.moment(P,t+u),E.mul(E.power(17,u),target));delta=E.divide((F(11166*18),)*2,E.mul(E.power(17,tested),target))
 need(alpha[1]<1-reserve and gamma[1]<F(31,32)and delta[1]<F(19,20),'All three actual charged compiler tails')
 # An independent rational-series engine certifies the raw crossing and tested margin.
 raw_lo=F('.00349780457955');raw_hi=F('.00349780457965');cross={}
 for label,c,sign in(('lower',raw_lo,1),('upper',raw_hi,-1),('tested',tested,1)):
  a=I.moment(T,1-c);b=I.moment(P,1-c);margin=(a[0]-b[1],a[1]-b[0]);need(margin[0]>0 if sign>0 else margin[1]<0,'Independent root sign '+label);cross[label]={'saving':c,'margin':margin}
 need(F(31,32)**128<F(1,16) and F(19,20)**128<F(1,16),'Tail block decay')
 surplus=1-F(1)/(1+v*reserve)-F(4,2**(v//32));need(surplus>0 and 17**64<18**63 and max(T)<256,'Charged completion, separation and ambient')
 z=1-uniform;z0=(t+z)/2;gap=z0-t;h=F(1,64);H0,H1=compiler_cutoffs(tested,uniform,v)
 need(H0>=8*v and H0*h*gap>gap*(5+8*h)*v+1+8*v*(1-z0)and H1*(z-z0)>H0*(1-z0),'Fresh finite integer compiler thresholds')
 C1=uniform-cover_gap;need(F(2**60)*cover_gap>256,'Cover/bad-prime gap')
 backend=F(L.read(R/'predecessor/ORDINARY-RESULT.json')['admitted']);old=backend;levels=[]
 for j in range(1,6):
  a=(1-rho)*C1+rho*backend;b=below_grid(a,10**15);need(backend<b<a<C1<rho<1-a,'Finite acyclic backend/adapter/stock/rounding gaps');levels.append({'level':j,'completed_backend':backend,'ordinary_exact':a,'admitted':b});backend=b
 need(backend==F(3497804579519,10**15) and backend>old,'New complete ordinary component saving')
 cmin=F(L.read(R/'predecessor/ORDINARY-RESULT.json')['admitted']);cmax=F('.0035')
 worst_target=E.moment(T,1-cmax)
 worst_gamma=E.divide(E.moment(P,1-cmin+u),E.mul(E.power(17,u),worst_target))
 worst_delta=E.divide((F(11166*18),)*2,E.mul(E.power(17,cmin),worst_target))
 need(worst_gamma[1]<F(31,32) and worst_delta[1]<F(19,20),'Uniform tail guards on the entire approach interval')
 tails=[sum(k*n for k,n in T.items() if k>=a)-sum(k*n for k,n in P.items() if k>=a) for a in range(1,129)]
 need(min(tails)>=0 and tails[0]==753,'Strict first-moment monotonicity from rank-mass tails')
 range_certificate={'C_min':cmin,'C_max':cmax,'gamma_upper_bound':worst_gamma,'delta_upper_bound':worst_delta,
                    'rank_mass_tails':tails,'tensor_reserve_controls':controls(),
                    'claim':'Under the retained framework, every ordinary saving strictly below this invoice raw crossing is attainable with fresh finite margins. This is not a global optimality claim.'}

 result={'status':'PASS_CONDITIONAL_G20_REFINEMENT_ORDINARY_FIVE_FINITE_LEVELS','invoice':invoice,'params':{'tested':tested,'uniform':uniform,'cover_gap':cover_gap,'rho':rho,'v':v,'alpha_gap':reserve,'grid_denominator':10**15,'prime_multiplier':2**60,'cutoff':17,'floor':18,'u':u},'raw_crossing_independent_exact':cross,'tail':{'alpha':alpha,'gamma':gamma,'delta':delta,'normalized_surplus':surplus,'H0':H0,'H1':H1},'C1':C1,'finite_backend_levels':levels,'admitted':backend,'comparator':old,'relative_gain':backend/old-1,'relative_gain_percent':100*(backend/old-1),'uniform_signed_invoice_improvement':'Relative to PR5653: Pnew-Pold=-252H1-252H3+252H4; targets unchanged. Gain252*(1+3^t-4^t)>0 for0<t<1.','fee_bounds':fee_bounds(invoice,glob,H1,v),'strict_margin_range':range_certificate,'whole_kappa':None,'assumptions':'Same retained native/allcolumn arbitraryinput/ROW/spectator, mixed-target finite compiler, completed ordinary fallback, precision and fixed-tape contracts as PR4760/4814; no full theorem verification claimed.'}
 L.put('ORDINARY-RESULT.json',enc(result));return enc(result)
if __name__=='__main__':
 r=run();print(json.dumps({k:r[k]for k in('status','admitted','comparator','relative_gain_percent','tail')},indent=2))
