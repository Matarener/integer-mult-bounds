#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticated integrated source-cost certificate and finite execution."""
from pathlib import Path
import argparse,hashlib,json,sys,types
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
STATUS='PASS_QQ16_COMPLETE_TERMINAL_COST'
NAMES=('RESULT.json','BILL.json','EXECUTION.json')
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def unique(pairs):
    out={}
    for k,v in pairs:
        need(k not in out,'duplicate key');out[k]=v
    return out
def parse(raw):return json.loads(raw,object_pairs_hook=unique)
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def typed(value):
    if isinstance(value,dict):return ('dict',tuple((k,typed(v)) for k,v in sorted(value.items())))
    if isinstance(value,list):return ('list',tuple(map(typed,value)))
    return (type(value).__name__,value)
def normalized(value):return parse(json.dumps(value,sort_keys=True,allow_nan=False))
def bootstrap():
    seals=parse((HERE/'SEALS.json').read_bytes())
    need(sha((HERE/'runtime.py').read_bytes())==seals['runtime.py'],'runtime seal')
    loader=types.ModuleType('runtime');loader.__file__=str(HERE/'runtime.py')
    sys.modules['runtime']=loader
    exec(compile((HERE/'runtime.py').read_bytes(),str(HERE/'runtime.py'),'exec'),loader.__dict__)
    pins=loader.authenticated_inputs()
    for name,digest in seals.items():
        need(sha((HERE/name).read_bytes())==digest,'local source seal:'+name)
    return loader,pins
def compute(loader,pins,execution=None):
    cohort=loader.cold()
    try:
        # Join physical monomial modules before finite recipe imports. This
        # preserves the inherited cold cohort's module-identity contract.
        cohort.monomial_api()
        connection=loader.module('cost_connection',loader._history._prior.predecessor()/'connection.py')
        data,packet,word,parent,service=connection.bindings()
        prior=loader._history.predecessor()
        ledger=loader.module('cost_prior_ledger',prior/'ledger.py')
        census=ledger.literal_census(data,parent)
        nonchild=loader.module('complete_cost_nonchild',HERE/'nonchild.py')
        cbody=loader.module('complete_cost_cbody',HERE/'cbody.py')
        gate_cover=loader.module('complete_cost_gate_cover',HERE/'gate_cover.py')
        cost=loader.module('complete_cost_evaluator',HERE/'cost.py')
        checker=loader.module('complete_cost_checker',HERE/'checker.py')
        parts=nonchild.census(parent,service)
        proof=gate_cover.source_checks(cohort)
        counted=proof['count_certificate']
        need(counted['gamma']==cost.gamma(),'literal source orthogonal cover')
        independent_gate=checker.owner_gate_cover_certificate(
            parts['owner_basis_monomials'],
            {tuple(k):v for k,v in parts['fixed_gate_deficits']})
        cases=[]
        for columns in (5,9,10,44):
            derived=cost.exclusion(columns)
            checked=checker.normalized_terminal_exclusion(columns)
            need(derived['lower_bound_RWM']==checked['lower_bound_RWM'],'independent signed evaluator')
            cases.append(derived)
        edge=cost.controls()
        checked=checker.normalized_terminal_exclusion(edge['last_positive_columns'])
        need(edge['endpoint']['lower_bound_RWM']==checked['lower_bound_RWM'],'exact normalized endpoint')
        independent=checker.check()
        need(census['retained']['calls']==510646 and census['retained_suffix']['calls']==493097,
             'complete later-root census')
        if execution is None:
            execution={'C':cbody.check(),
                       'phase':nonchild.phase_pair_calibrations(),
                       'bank':nonchild.gather_calibrations()}
        else:
            need(type(execution) is dict and set(execution)=={'C','phase','bank'},'saved execution scope')
        controls={'cost':edge,'nonchild':nonchild.controls(),
                  'independent':independent}
    finally:loader.cleanup()
    result={'status':STATUS,'scientific_main':'12fa8c5c844be21bfefb38a19503fbd867a11244',
        'priority_revision':7,'frozen_predecessor':'59b46625a8b2f0dfff3e38ba0949b4247423938a',
        'verdict':'frozen D strictly costs more than Bstar in each source R/W/M component on the proved terminal-child domain',
        'not_a_universal_QQ16_obstruction':True,'no_kappa_change':True,
        'actual_production_descriptor_family':'p=2^8500, lambda=5..44; inherited numerical/hosting/source premises; no production payload execution',
        'sources_authenticated_before_execution':len(pins),
        'cost_currency':'source reads/writes/unit moves; compiled control and historical backing separate',
        'execution_sha256':sha(canonical(normalized(execution)))}
    bill={'source_occurrence_partition':parts,'complete_root_census':census,
          'gate_cover':gate_cover.jsonable(proof),'independent_gate_check':independent_gate,
          'derived_cost_cases':cases,'controls':controls}
    return tuple(normalized(x) for x in (result,bill,execution))
def check_receipt(name,expected,folder=HERE):
    need(typed(parse((folder/name).read_bytes()))==typed(normalized(expected)),
         'whole typed receipt mismatch:'+name)
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--generate',type=Path)
    p.add_argument('--check-only',action='store_true')
    a=p.parse_args()
    if a.generate:
        need(all(not (a.generate/n).exists() for n in NAMES),'refuse receipt overwrite')
    loader,pins=bootstrap()
    execution=parse((HERE/'EXECUTION.json').read_bytes()) if a.check_only else None
    result=compute(loader,pins,execution)
    if a.generate:
        a.generate.mkdir(parents=True,exist_ok=True)
        need(all(not (a.generate/n).exists() for n in NAMES),'refuse receipt overwrite')
        for name,value in zip(NAMES,result):
            (a.generate/name).write_text(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n')
    else:
        for name,value in zip(NAMES,result):check_receipt(name,value)
    print(STATUS)
if __name__=='__main__':main()
