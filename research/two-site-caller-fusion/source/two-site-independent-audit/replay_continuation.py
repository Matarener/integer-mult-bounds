#!/usr/bin/env python3
"""Authenticated read-only reproduction of the bounded isolated census.
This reuses its exact general-Clifford engine; the positive-word audit is
the separate independent oracle. Apache-2.0; substantial Codex assistance.
"""
from pathlib import Path
import argparse,hashlib,json,sys,types
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'two-site-continuation'
raw=(HERE/'audit_two_sites.py').read_bytes()
boot=types.ModuleType('independent_source_bootstrap');boot.__file__=str(HERE/'audit_two_sites.py')
exec(compile(raw,boot.__file__,'exec',dont_inherit=True,optimize=0),boot.__dict__)
sys.path.insert(0,str(SOURCE))
import continue_isolated as review


def controls():
    A=review.Algebra(5);I=A.one;n=2;m=12
    ident={'kind':'ADDRESS_OR_UNIT','bank':0,'one_coordinate_literal_circuit':[],
           'one_coordinate_tableau':[list(x)for x in review.ce.ident(m).tab],
           'extra_global_phase_exponent_by_f_mod4':[0,0,0,0]}
    for dst,src,label in((0,1,'column-only'),(1,0,'row-only')):
        P=[ident,{'kind':'ADD','dst':dst,'src':src,'coefficient':'1'},ident]
        col,row=review.pair_cols(P,0,2,n,A)
        if label=='column-only':boot.need(col==[I,{}]and row==[I,A.scale(I,-1)],'isolated column does not imply isolated row')
        else:boot.need(row==[I,{}]and col==[I,I],'isolated row does not imply isolated column')
    final=dict(ident,bank=1)
    col,row=review.pair_cols([ident,{'kind':'BANK_SWAP','banks':[0,1]},final],0,2,n,A)
    boot.need(col==row==[{},I],'a transported bank permutation is an admitted two-sided isolation')
    return ['column-only triangular transport rejected','row-only triangular transport rejected',
            'bank-permuted two-sided isolation accepted']


def run():
    saved=json.loads((SOURCE/'CONTINUED-ISOLATION-Q2.json').read_text())
    current=review.run(180)
    canonical=lambda x:{k:v for k,v in x.items()if k!='elapsed_seconds'}
    boot.need(canonical(saved)==canonical(current),'every proof-relevant census field matches frozen certificate')
    boot.need(current['completed_masks']==list(range(1,8))and not current['timed_out']and not current['cases'],
              'all seven nonempty tail subsets finished with no eligible isolated pair')
    boot.need(current['counts']=={'correction-not-one-bank':4887,'not-isolated-both-sides':34},'all4921 cut-pair cases accounted')
    return {'status':'PASS_AUTHENTICATED_BOUNDED_ISOLATION_REPLAY_AND_TWO_SIDED_CONTROLS',
            'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_sha256':hashlib.sha256((SOURCE/'CONTINUED-ISOLATION-Q2.json').read_bytes()).hexdigest(),
            'bootstrap_sha256':hashlib.sha256(raw).hexdigest(),'source_path':str(SOURCE/'CONTINUED-ISOLATION-Q2.json'),
            'counts':current['counts'],'nonempty_tail_subsets':7,'pairs_per_subset':703,
            'algorithm_controls':controls(),'executed_source_bytes':boot.EXECUTED,
            'independence':'Authenticated same-engine reproduction plus independent reviewed bank-row/column controls. This is not a second general-Clifford census implementation. The complete constructive words have a separate independent transport/physical-circuit audit.',
            'scope':'Only isolated whole-bank transported row AND column and single-unitary-Clifford bank correction in the frozen q2 prefix sites. Coupled two-bank corrections, more sites, changed source/response and endpoints are outside.',
            'no_all_q_or_global_obstruction':True,'no_new_kappa':True}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();out=json.loads(json.dumps(run()));path=HERE/'CONTINUATION-REPLAY.json'
    if a.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:boot.need(json.loads(path.read_text())==out,'saved bounded reproduction differs')
    print(out['status'])
