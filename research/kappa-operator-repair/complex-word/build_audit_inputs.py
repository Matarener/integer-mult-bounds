#!/usr/bin/env python3
"""Build the portable input closure for the declared complex-word experiments."""
from hashlib import sha256
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PRIMARY=[
 'singles','pairs','source-singles','delayed-singles-v2','delayed-spans-v2','delayed-joint',
 'intervals','intervals-source','response-routes','multi-response-v2','equal-g-pairs','monomial-response',
 'all-helper-response-targets','all-helper-multi','global-response','permanent-shears-v2','timed-shears',
 'warm-edge-shears','a-window-shears-v2']
COMMON=[
 'research/kappa-1745-continuation/complex-birth/commute_birth.py',
 'research/kappa-1745-continuation/complex-birth/exact_rows.py',
 'research/kappa-1745-continuation/complex_projection_screen.py',
 'research/kappa-adaptive-continuation/native-alternatives/fanout_search.py',
 'research/kappa-adaptive-continuation/native-alternatives/opt_frames.py',
 'research/kappa-adaptive-continuation/native-alternatives/candidate/BORROW-WORD-43base.json.gz',
 'research/kappa-adaptive-continuation/native-alternatives/native-base/source/native/new/code/borrow/bw_gauss.py']


def digest(path):return sha256(path.read_bytes()).hexdigest()


def embedded_pins(value):
    out={}
    if isinstance(value,dict):
        for key,item in value.items():
            if key=='source_sha256':
                for path,pin in item.items():
                    if path in out:assert out[path]==pin
                    out[path]=pin
            elif isinstance(item,(dict,list)):out.update(embedded_pins(item))
    elif isinstance(value,list):
        for item in value:out.update(embedded_pins(item))
    return out


def main():
    scripts={str(p.relative_to(ROOT)) for p in HERE.glob('*.py')}
    shared=set(COMMON)|scripts;files=set(shared);receipts={};summary=[]
    paths=[HERE/name/'RESULT.json' for name in PRIMARY]+[HERE/'OPERATOR-RANK.json']
    for path in paths:
        result=json.loads(path.read_text());pins=embedded_pins(result)
        for relative,pin in pins.items():assert digest(ROOT/relative)==pin,(relative,'source pin changed')
        assert not result.get('positives'),('unexpected positive requires separate admission',path)
        dependencies=shared|set(pins);files|=dependencies;files.add(str(path.relative_to(ROOT)))
        phase=path.parent/'OPERATOR-QUOTIENT.json'
        if phase.is_file():
            files.add(str(phase.relative_to(ROOT)));dependencies.add(str(phase.relative_to(ROOT)))
            assert result['operator_quotient_certificate_sha256']==digest(phase)
        relative=str(path.relative_to(ROOT))
        receipts[relative]={'sha256':digest(path),'inputs':{p:digest(ROOT/p) for p in sorted(dependencies)},
                            'comparison_omit_only':['seconds'],'native_or_global_admission':False}
        summary.append({'receipt':relative,'sha256':digest(path),'status':result['status'],'census':result.get('census'),
                        'apparent_saving':result.get('saving'),'rejection':result.get('rejected')})
    files.add(str((HERE/'README.md').relative_to(ROOT)))
    result={'schema':1,'status':'NO_NEW_ADMITTED_COMPLEX_WORD','requirements':{'ordinary_searches':'Python3 standard library',
            'operator_quotient_and_rank':'Python3 plus NumPy; no package installation is performed'},
            'source_bound_receipts':receipts,'files':{p:{'sha256':digest(ROOT/p),'bytes':(ROOT/p).stat().st_size} for p in sorted(files)},
            'excluded_from_scientific_coverage':['multi-response/RESULT.json (superseded own-donor response formula)',
              'interrupted preliminary logs/directories without final RESULT.json, including permanent-shears and a-window-shears',
              'failed preliminary delayed-query logs before TARGET-observation barriers were implemented'],
            'scope':'All primary claims bind the pinned adaptive base word, before the separately integrated PR3945 terminal refit. No new native/global supplier is admitted by these experiments.'}
    (HERE/'AUDIT-INPUTS.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    (HERE/'SEARCH-SUMMARY.json').write_text(json.dumps({'status':result['status'],'experiments':summary},sort_keys=True,indent=2)+'\n')
    print('PASS',len(paths),'receipts',len(files),'files',flush=True)


if __name__=='__main__':main()
