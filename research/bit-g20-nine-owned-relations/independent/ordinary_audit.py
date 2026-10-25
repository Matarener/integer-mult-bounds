"""Separate positive-series interval and literal fee/finite-bootstrap review."""
from local_audit import *
import importlib.util
def ceil(x):return -((-x.numerator)//x.denominator)
def main():
 r=read(CAND/'ORDINARY-RESULT.json');inv=read(CAND/'INVOICE.json');g=read(CAND/'GLOBAL-RESULT.json')
 spec=importlib.util.spec_from_file_location('frozen_positive_series',SRC/'ordinary-certificate/inputs/separate_series.py');I=importlib.util.module_from_spec(spec);spec.loader.exec_module(I)
 p={int(k):v for k,v in inv['paid'].items()};tgt={int(k):v for k,v in inv['targets'].items()};c=F('0.00348398');uniform=F('0.00348397');t=1-c;v=1024;gap=F(1,2**39);u=F(1,5)
 target=I.moment(tgt,t);alpha=I.div(I.moment(p,t),target);gamma=I.div(I.moment(p,t+u),I.mul(I.power(17,u),target));delta=I.div((F(11238*18),)*2,I.mul(I.power(17,c),target))
 need(alpha[1]<1-gap and gamma[1]<F(31,32)and delta[1]<F(19,20),'All three independently recomputed compiler tails')
 need(F(31,32)**128<F(1,16)and F(19,20)**128<F(1,16),'Tail block decay')
 need(1-F(1)/(1+v*gap)-F(4,2**32)>0,'Full normalized completion surplus')
 need(17**64<18**63 and max(tgt)<256,'Proper postcompletion separation')
 z=1-uniform;z0=(t+z)/2;d=z0-t;h=F(1,64)
 h0=ceil((d*(5+8*h)*v+1+8*v*(1-z0))/(h*d));h1=(h0*(1-z0)/(z-z0)).__floor__()+1
 need(h0==378121592832 and h1==263473235277373441,'Fresh exact rank compiler thresholds')
 need(h0>=8*v and h0*h*d>=d*(5+8*h)*v+1+8*v*(1-z0)and h1*(z-z0)>h0*(1-z0),'Both strict compiler gaps')
 cover=F(1,2**36)+F(1,10**20);need(2**45*cover>256,'Charged prime/cover surcharge')
 c1=uniform-cover;backend=F(1737729,500000000);old=backend;levels=[]
 for j in range(3):
  a=F(99,100)*c1+F(1,100)*backend;b=F((a*10**12).__floor__(),10**12)
  need(backend<b<a<c1<F(1,100)<1-a,'Finite completed-backend, adapter, stock and rounding gaps')
  levels.append((str(backend),str(a),str(b)));backend=b
 need(backend==F(435496247,125000000000)and backend/old-1>F(1,1000),'Same-axis publication gain >=0.1 percent')
 # Independently recount every finite positive base charge from literal proof data.
 ops=g['operation_counts'];scans=sum(ops[k]for k in('ADD','OWNED_CLEAR','OWNED_ZERO_HEADER','WHOLE_ZERO_FRAME'))+22
 park=4*(11238+11)*56997;routes=7548+7248;base=scans+park+routes+g['expanded_event_count']+56997*(32*127**2+8*127**3)
 need(scans==391709 and park==2564637012 and base==965996734173 and base<2**64,'All positive scalar/park/route/dimension fees')
 need(g['majorant_bits']==517 and 517<1024,'Fresh precision majorant')
 fee=r['fee_bounds'];need(fee['base_counts']['all_owned_allocated']==11 and fee['base_counts']['owned_productive_credit']==0,'No owned productive credit')
 need(fee['finite_compiler']['N']=='2^'+str(h1),'Fresh finite uniform dimension')
 # Semantic failure controls use the mathematical predicates, not echoed outputs.
 failures={'unfunded_alpha':not(alpha[1]<1-F(1,1000)),'old_tiny_H0':not(F(171012)*h*d>=d*(5+8*h)*v+1+8*v*(1-z0)), 'insufficient_prime':not(2**20*cover>256),'raw_as_ordinary':not(F('.0034839853304')<c1)}
 need(all(failures.values()),'All pricing failure controls reject')
 out={'status':'PASS_INDEPENDENT_SERIES_THREE_TAILS_COMPILER_FEES_ORDINARY','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'admitted':str(backend),'relative_gain':str(backend/old-1),'relative_gain_percent':str(100*(backend/old-1)),'H0':h0,'H1':h1,'finite_levels':levels,'alpha':[str(x)for x in alpha],'gamma':[str(x)for x in gamma],'delta':[str(x)for x in delta],'positive_base_fee':base,'owned_per_compiled_instance':11,'majorant_bits':517,'failure_controls':failures,
 'scope':'Same retained finite mixed-target compiler, delayed cover, completed ordinary backend, native/ROW/tape/precision assumptions as frozen G20/4814 proof. Fresh positive finite fee/stock/threshold schemas are instantiated, not numeric decimal materializations of the enormous program. No whole kappa claim or external audit.'}
 (HERE/'ORDINARY-REVIEW.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps({k:out[k]for k in('status','admitted','relative_gain_percent','H0','H1','failure_controls')}))
if __name__=='__main__':main()
