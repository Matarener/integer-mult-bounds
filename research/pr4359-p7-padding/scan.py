"""Exact finite moment screen of declared balanced-prefix/suffix rank profiles.

This checks 209 algebraic candidate profiles, not 209 native controllers.
Only selected cases have a separate exact Laurent/physical admission.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PINS={
    'research/kappa-rebuild/architecture/mixed_target_probe.py': '011c3c9d0cf81103dc84d709a0e36793eb7c5ae3f23c85eac27650ef13afa04a',
    'research/kappa-rebuild/complex/full-identity-certificates/RESULT.json': '943d5fad2fc529f470df05a35446e07ecaef7344abfce450d2c2eb2c9b3798f6',
}


def need(ok,message):
    if not ok:
        raise ValueError(message)


def profile(p,a,H,N):
    b=p-1-a
    targets=Counter({r:(2*p+1)*count for r,count in H.items()})
    paid=Counter({r:(2*p+1)*count for r,count in N.items()})
    targets[16*p+9]+=224
    for length in (a,b):
        for j in range(length): targets[16*j+25]+=224
        for j in range(1,length+1): paid[16*j]+=224
    paid[8]+=224*(p-1)
    mask=sum(1<<i for i in list(range(1,2*p-2,2))+list(range(0,2*a,2))+list(range(3*(p-1)-b,3*(p-1))))
    return targets,paid,mask

def run(source_root,native_result=None):
    root=Path(source_root)
    for relative,expected in PINS.items():
        need(sha256((root/relative).read_bytes()).hexdigest()==expected,
             'Authenticated interval and local-invoice source: '+relative)
    engine,receipt=[root/relative for relative in PINS]
    spec=importlib.util.spec_from_file_location('followup_intervals',engine)
    E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
    local=json.loads(receipt.read_text())['providers']['THREE-base']
    H={int(k):v for k,v in local['helper_boundary']['widths'].items()}
    N={int(k):v for k,v in local['unsplit_replays']['forward']['paid_profile'].items()}
    if native_result is None:
        native_result=json.loads((HERE/'RESULT.json').read_text())['strictification']['native_inventory']
    selected_t,selected_p,selected_mask=profile(7,3,H,N)
    need((native_result['p'],native_result['keep'])==(7,selected_mask),
         'The selected profile is the admitted native p7 mask')
    need(selected_t=={int(k):v for k,v in native_result['targets'].items()}
         and selected_p=={int(k):v for k,v in native_result['paid'].items()},
         'The selected profile matches the actual current native receipt')
    candidates=[(p,a,*profile(p,a,H,N)) for p in range(2,21) for a in range(p)]
    ranks=set(r for _,_,T,P,_ in candidates for hist in (T,P) for r in hist)
    points=(Q('.00268648'),Q('.00268649'))
    # Outward rounding preserves certification while shortening denominators.
    powers={C:{r:tuple(Q(E.show(E.h_interval(r,C))[side]) for side in ('lower','upper'))
               for r in ranks} for C in points}
    rows=[]
    for p,a,T,P,mask in candidates:
        checks={}
        for C in points:
            signed={r:T[r]-P[r] for r in set(T)|set(P)}
            lo=sum(count*powers[C][r][0 if count>=0 else 1] for r,count in signed.items())
            hi=sum(count*powers[C][r][1 if count>=0 else 0] for r,count in signed.items())
            need(lo>0 or hi<0,'Every tested moment has a strict interval sign')
            checks[str(C)]={'target_minus_paid':E.show((lo,hi)),
                            'strict_moment':'PASS' if lo>0 else 'FAIL'}
        rows.append({'p':p,'prefix_initial_count':a,'suffix_terminal_count':p-1-a,
                     'keep':mask,'checks':checks})
    passing=[[row['p'],row['prefix_initial_count'],row['keep']] for row in rows
             if row['checks'][str(points[0])]['strict_moment']=='PASS']
    need(passing==[[7,3,232127]],'Only the selected p7 profile passes C=.00268648')
    need(all(row['checks'][str(points[1])]['strict_moment']=='FAIL' for row in rows),
         'All declared profiles fail C=.00268649')
    return {'schema':'finite-algebraic-balanced-profile-screen/1',
            'status':'PASS_EXACT_DECLARED_PROFILE_SCREEN','p_range':[2,20],
            'profile_count':len(rows),'only_pass_at_00268648':passing,
            'all_fail_at_00268649':True,'selected_native_profile_matched':True,
            'source_sha256':dict(PINS),
            'scope':'Finite exact arithmetic on the explicitly defined all-middle, initial-prefix, terminal-suffix rank-profile formulas. No exhaustive mask search, all-p barrier, global optimality claim, or physical admission of unverified profiles. The selected p7 profile is checked against the separate current native receipt.',
            'profiles':rows}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path,default=HERE/'source')
    parser.add_argument('--write-result',action='store_true',help='Author the checked finite receipt.')
    args=parser.parse_args()
    result=run(args.source_root)
    target=HERE/'FOLLOWUP.json'
    if args.write_result:
        target.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(result==json.loads(target.read_text()),'Exact replay agrees with checked FOLLOWUP.json')
    print(json.dumps({k:v for k,v in result.items() if k!='profiles'},sort_keys=True))
