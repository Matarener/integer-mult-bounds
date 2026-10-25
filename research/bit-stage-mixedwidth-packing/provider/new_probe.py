"""Actual new SOURCE routes and optimized-safe scientific negative controls."""
from pathlib import Path
from fractions import Fraction as Q
from types import FunctionType
from copy import deepcopy
import importlib.util,json,time,tempfile,shutil,gc
H=Path(__file__).resolve().parent
def need(v,why):
    if not v:raise ValueError(why)
def module(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run():
    st=time.process_time();checker=module('new_scientific_checks',H/'verify_new_owners.py')
    owner_report,ctx,ledger=checker.verify(return_context=True);owner=ctx['owner'];failures=[]
    def reject(name,fn,expected):
        try:fn()
        except ValueError as error:
            need(expected in str(error),'wrong rejection for '+name+': '+str(error))
            failures.append(dict(defect=name,rejection=str(error)))
        else:raise ValueError('undetected scientific mutant '+name)
    missing=[a for a in ctx['slots']if not(a[4]==4 and a[5]==462-222)]
    reject('missing_stage4_partial',lambda:owner.audit(missing,ctx['children'],ctx['windows'],ctx['widths'],ctx['frames'],ctx['bases']),'missing helper')
    badbases=dict(ctx['bases']);badbases[506]=ctx['bases'][508]
    reject('wrong506_terminal_chart',lambda:checker.validate_terminal_bases(owner,ctx['geom'],badbases,ctx['terminal_source']),'terminal chart source binding')
    bad=deepcopy(next(c for c in ledger['charts']if c['terminal_frame']==506))
    i=bad['axes'][0];j=next(k for k in range(64)if k not in bad['axes'])
    bad['relative_matrix'][i],bad['relative_matrix'][j]=bad['relative_matrix'][j],bad['relative_matrix'][i]
    reject('equalrank_wrongaxis_operator',lambda:checker.validate_relative_support(bad,ctx['bases'],ctx['dims']),'exact terminal operator support')
    factors=deepcopy(ledger['factors']);target=next(a for a in factors if a[:2]==[6,202]);need(len(target[2])==14,'actual newidle14');target[2]=[]
    reject('zero_idle14_return',lambda:checker.validate_idle_return(factors,ctx['slots'],ctx['children']),'complete idle return')
    # Real source authentication before any altered source can execute.
    work=H.parent/'control-work';work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='source-mutant-',dir=work)as tmp:
        tmp=Path(tmp);shutil.copyfile(H/'owner.py',tmp/'owner.py')
        (tmp/'upstream-owner.py').write_bytes((H/'upstream-owner.py').read_bytes()+b'\n')
        reject('changed_upstream_SOURCE_byte',lambda:module('mutated_source_owner',tmp/'owner.py'),'authenticated upstream owner source')
    del ledger,ctx,factors,badbases,bad;gc.collect()
    m=module('new_actual_source_caller',H/'caller.py');c,loader,provenance=m.build_provider()
    # Mutate the real provider's census constant in memory, then instantiate
    # that same class. Production files and their frozen source pins are not
    # altered; this exercises its actual _bind guard in normal and-O modes.
    cls=type(c);original=cls._bind;const=original.__code__.co_consts
    need(const.count(901312)==1,'actual new count constant')
    broken=original.__code__.replace(co_consts=tuple(902592 if v==901312 else v for v in const))
    mutant=FunctionType(broken,original.__globals__,original.__name__,original.__defaults__,original.__closure__)
    try:
        cls._bind=mutant
        reject('wrong_new_paidcount',lambda:cls(3,'candidate'),'new complete paid catalogue')
    finally:cls._bind=original
    chosen={}
    for name,role,frame in [('stage4_partial506',462,506),('stage4_partial508',467,508),('stage4_partial509',470,509)]:
        chosen[name]=next(i for i,r in enumerate(c.requests)if r.kind=='MOVE'and r.stage==4 and r.role==role and r.new_frame==frame)
    chosen['new_window6_idle14']=next(i for i,r in enumerate(c.requests)if r.kind=='IDLE'and r.base.rank==14)
    consumers=m.consumer_probes(c,chosen)
    from driver import compile_owner,inverse_chart
    import oracle
    from sources import identity,product
    common=tuple(map(tuple,oracle.eye(64)));routes=[]
    for name,i in chosen.items():
        r=c.requests[i];matrix=c.chart_matrix(r.chart)
        need(product(matrix,tuple(zip(*matrix)))==identity(64),'actual new chart orthogonality')
        inverse=inverse_chart(matrix);need(inverse==tuple(zip(*matrix)),'actual new inverse transpose')
        native,f,b=compile_owner(matrix,common,c.codes)
        need(f.chart==matrix and b.chart==inverse and f.target_low==common and b.target_low==native,'actual new compiled route')
        routes.append(dict(name=name,request=i,kind=r.kind,stage=r.stage,role=r.role,owner_family=r.family,
            source_chart_key=r.chart.key,forward_sha256=m.digest([[str(x)for x in row]for row in f.chart]),
            inverse_sha256=m.digest([[str(x)for x in row]for row in b.chart]),exact_common_low_return=True))
    need({r['owner_family']for r in routes}=={202},'actual new cohosted DATAfamily202')
    need(len(failures)==6,'all six scientific negative controls')
    return dict(status='PASS_NEW_COHOST_CONSUMER_ROUTES_AND_SIX_MUTANTS',optimized=not __debug__,
        actual_owner_checks=owner_report,negative_controls=failures,chosen=chosen,
        actual_consumer_coefficients=consumers,actual_compiled_routes=routes,
        catalogue_binding=c.receipt(),provenance=provenance,
        complete_GL64_payload_executed=False,CPU=time.process_time()-st)
if __name__=='__main__':print(json.dumps(run(),sort_keys=True,indent=2))
