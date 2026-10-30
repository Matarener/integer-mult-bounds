"""Two exact moment engines and positive-fee finite ordinary bootstrap.

Uses the retained PR4814 finite acyclic bootstrap, with the new literal
G20 nine-owned-relations invoice. No multiplication-kappa update is claimed.
"""
from fractions import Fraction as F
from pathlib import Path
import importlib.util,sys,json
import local_relations as L
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
 routes=7548+7248;scans=ops['ADD']+ops['OWNED_CLEAR']+ops['OWNED_ZERO_HEADER']+ops['WHOLE_ZERO_FRAME']+2*owned;raw=glob['expanded_event_count'];base=scans+park+routes+raw+M*(32*127**2+8*127**3)
 need(n==11238 and M==56997 and owned==11 and base<2**64,'Actual retained originals,11owned and positive complete finite fees')
 need(glob['majorant_bits']==517 and 517<1024,'Fresh positive majorant and fixed matrix height')
 need(v==1024 and 256*v>=4*v*64,'Explicit tensor count envelope')
 return{'status':'PASS_POSITIVE_NEW_FINITE_FEE_AND_STOCK_SCHEMA','base_counts':{'raw_records':raw,'all_XOR_CLEAR_INIT_zeroheader_passes':scans,'parent_parking_FIELD_passes':park,'internal_and_wholejob_routes':routes,'coarse_primitive_count_with_dimension_work':base,'strict_upper':2**64,'all_owned_allocated':11,'owned_productive_credit':0},
 'fixed_tensor_unit':{'v':v,'K':'2^262144','meaning':'Bounds fixed integer ranks, all role/round/operation inventories after tensoring, charged target completion and charged paid splitting.'},
 'finite_compiler':{'N':'2^'+str(H1),'J(n)':'(n+1)^4*K^(4*n+4)','A(1)':'K^4','A(n)':'(J(n)+2)^4*(A(n-1)+2)^(4*n+8)','counts':'Productive roles B_N, paid leaves P_N, instances and primitive descriptions <=A(N). Each compiled instance gets11distinct owned banks; C_N<=11*A(N). Denominator replication product <=A(n-1)^(n-1).'},
 'height_prime':{'base_height_bits':1024,'T':'(2*N+2)^4*(A(N)+2)^2','H':'1026*4^(T+1)','q':'Choose odd prime q>max(2^45*N^5,2^(2*H)) avoiding every finitely compiled denominator/rank witness. All QQ matrices and relative SOURCE projectors compiled before choice.'},
 'all_in_fixed_primitive_fee':{'F':'(q+2)^(32*(N+1)^2)*(A(N)+2)^8','actual_cost':'F times positive maximum of the retained stream/route/normalizer/completed-backend constants, fixed anew at each finite level. No primitive has cost0 or a claimed universal cost1.','parking':'4*(B_N+C_N) positive FIELD passes per child plus initialization/teardown, with C_N<=11*A(N); F dominates their products.','bad_classes':'<=32*N^2 ordinary calls charged separately by the retained moment/cover argument.'},
 'stock':{'reserve':'[B_N*|GL_N(F_q)|*q^(N^2*(w-1))]^D*S_completed_backend','D':'floor(log_N ceil(e/w))+1','borrowed_digits':'D*(N^2*(w-1)+ceil(log_q(B_N*|GL_N(F_q)|)))+ceil(log_q S_completed_backend)+1 =O_new(w loge)','ownership':'All11whole owned banks for EVERY compiled instance, including suspended ones, get distinct tags; full entry/exit CLEAR charged. No ancestor region is swept or external zero stock assumed.'},
 'eventual_threshold':{'K_j':'At least16 times sum of F*positive retained primitive constants, reserve/adapter bounds and already frozen backend constant completed at all widths by finite fallback.','eta_j':'min(rho-a_j,1-rho-a_j,a_j-b_j)>0','e_j':'Fresh integer dominating E_backend^(ceil(2/rho)), borrow threshold, ceil((32*K_j/eta_j)^(ceil(8/eta_j)))+2^(ceil(8/eta_j)).','scope':'Constructive finite threshold schema under retained native/compiler/ROW/precision/tape premises. Winning uniform program and decimal threshold are not materialized.'}}
def run():
 invoice=L.read(R/'INVOICE.json');glob=L.read(R/'GLOBAL-RESULT.json');P={int(k):v for k,v in invoice['paid'].items()};T={int(k):v for k,v in invoice['targets'].items()}
 need(sum(T.values())==11238 and sum(P.values())==56997 and T[4]==72 and T[8]==7614 and P[7]==162,'Actual complete new target/paid bill')
 E=load('nine_credited_interval',S/'ordinary-certificate/inputs/credited_intervals.py');I=load('nine_independent_series',S/'ordinary-certificate/inputs/separate_series.py')
 tested=F('.00348398');uniform=F('.00348397');cover_gap=F(1,2**36)+F(1,10**20);rho=F(1,100);reserve=F(1,2**39);v=1024;t=1-tested;u=F(1,5)
 target=E.moment(T,t);paid=E.moment(P,t);alpha=E.divide(paid,target);gamma=E.divide(E.moment(P,t+u),E.mul(E.power(17,u),target));delta=E.divide((F(11238*18),)*2,E.mul(E.power(17,tested),target))
 need(alpha[1]<1-reserve and gamma[1]<F(31,32)and delta[1]<F(19,20),'All three actual charged compiler tails')
 # An independent rational-series engine certifies the raw crossing and tested margin.
 raw_lo=F('.0034839853304');raw_hi=F('.0034839853305');cross={}
 for label,c,sign in(('lower',raw_lo,1),('upper',raw_hi,-1),('tested',tested,1)):
  a=I.moment(T,1-c);b=I.moment(P,1-c);margin=(a[0]-b[1],a[1]-b[0]);need(margin[0]>0 if sign>0 else margin[1]<0,'Independent root sign '+label);cross[label]={'saving':c,'margin':margin}
 need(F(31,32)**128<F(1,16) and F(19,20)**128<F(1,16),'Tail block decay')
 surplus=1-F(1)/(1+v*reserve)-F(4,2**32);need(surplus>0 and 17**64<18**63 and max(T)<256,'Charged completion, separation and ambient')
 z=1-uniform;z0=(t+z)/2;gap=z0-t;h=F(1,64);H0=ceil((gap*(5+8*h)*v+1+8*v*(1-z0))/(h*gap));H1=(H0*(1-z0)/(z-z0)).__floor__()+1
 need(H0>=8*v and H0*h*gap>=gap*(5+8*h)*v+1+8*v*(1-z0)and H1*(z-z0)>H0*(1-z0),'Fresh finite integer compiler thresholds')
 C1=uniform-cover_gap;need(F(2**45)*cover_gap>256,'Cover/bad-prime gap')
 backend=F(1737729,500000000);old=backend;levels=[]
 for j in range(1,4):
  a=(1-rho)*C1+rho*backend;b=F((a*10**12).__floor__(),10**12);need(backend<b<a<C1<rho<1-a,'Finite acyclic backend/adapter/stock/rounding gaps');levels.append({'level':j,'completed_backend':backend,'ordinary_exact':a,'admitted':b});backend=b
 need(backend/old-1>F(1,1000),'New actual ordinary gain clears .1percent publication guard')
 result={'status':'PASS_CONDITIONAL_G20_NINE_RELATIONS_ORDINARY_THREE_FINITE_LEVELS','invoice':invoice,'params':{'tested':tested,'uniform':uniform,'cover_gap':cover_gap,'rho':rho,'v':v,'alpha_gap':reserve,'cutoff':17,'floor':18,'u':u},'raw_crossing_independent_exact':cross,'tail':{'alpha':alpha,'gamma':gamma,'delta':delta,'normalized_surplus':surplus,'H0':H0,'H1':H1},'C1':C1,'finite_backend_levels':levels,'admitted':backend,'comparator':old,'relative_gain':backend/old-1,'relative_gain_percent':100*(backend/old-1),'qualifies_0_1_percent':True,'uniform_signed_invoice_improvement':'Pnew-Pold=-162H1-162H7; Tnew-Told=-162H8, gain162*(1+7^t-8^t)>0 for0<t<1 by strict subadditivity.','fee_bounds':fee_bounds(invoice,glob,H1,v),'whole_kappa':None,'assumptions':'Same retained native/allcolumn arbitraryinput/ROW/spectator, mixed-target finite compiler, completed ordinary fallback, precision and fixed-tape contracts as PR4760/4814; no full theorem verification claimed.'}
 L.put('ORDINARY-RESULT.json',enc(result));return enc(result)
if __name__=='__main__':
 r=run();print(json.dumps({k:r[k]for k in('status','admitted','comparator','relative_gain_percent','qualifies_0_1_percent','tail')},indent=2))
