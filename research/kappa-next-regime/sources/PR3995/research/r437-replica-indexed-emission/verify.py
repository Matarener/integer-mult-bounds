"""Source-bound replica-indexed emission, not physical execution.
Apache-2.0. Chris R / Clear1nsight with substantial OpenAI Codex assistance.
"""
import argparse,copy,gzip,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import compiler as c
HERE=Path(__file__).resolve().parent

def run():
    for row in json.loads((HERE/'PREDECESSORS.json').read_bytes())['files']:
        c.need(hashlib.sha256((HERE/row['local']).read_bytes()).hexdigest()==row['sha256'],'exact predecessor '+row['local'])
    raw=gzip.decompress((HERE/'inputs/template.json.gz').read_bytes());t=json.loads(raw)
    proposal=json.loads((HERE/'inputs/moves.json').read_bytes())
    c.need(hashlib.sha256(raw).hexdigest()==proposal['template_content_sha256'],'R437 template identity')
    c.retained_symmetry_check(t)
    _,old_profile,_=c.compile_owners(t,[])
    pooled,profile,idles=c.compile_owners(t,proposal['moves'])
    try:c.retained_symmetry_check(pooled)
    except ValueError as error:c.need(str(error)=='replica owner symmetry','exact retained rejection')
    else:raise ValueError('retained catalogue accepted pooled owners')
    one=copy.deepcopy(t);one['calls'][193]['owners'][643]=[209,['hosted',6,16,8]]
    try:c.retained_symmetry_check(one)
    except ValueError as error:c.need(str(error)=='replica owner symmetry','first-move rejection')
    else:raise ValueError('first move accepted by replica factorization')
    controls=[]
    def reject(name,change):
        moves=copy.deepcopy(proposal['moves']);change(moves)
        try:c.compile_owners(t,moves)
        except (ValueError,KeyError,IndexError):controls.append(name)
        else:raise ValueError('accepted mutation '+name)
    reject('stale old family',lambda m:m[0]['old'].__setitem__('family',209))
    reject('wrong logical replica',lambda m:m[0].__setitem__('call_replica',0))
    reject('overlapping destination cells',lambda m:m[1].__setitem__('new',copy.deepcopy(m[0]['new'])))
    reject('destination beyond window',lambda m:m[0]['new'].__setitem__('offset',40))
    reject('wrong destination pair',lambda m:m[0]['new'].__setitem__('family',500))
    reject('duplicate moved owner',lambda m:m.append(copy.deepcopy(m[0])))
    emitted=c.retained_emit(pooled);independent=c.independent_emit(pooled)
    c.need((emitted['emitted_program_sha256'],emitted['emitted_events'])==independent,'two retained encoders agree')
    c.need(independent[1]==7814016,'complete local event stream')
    delta={str(r):profile[r]-old_profile[r] for r in sorted(set(profile)|set(old_profile)) if profile[r]!=old_profile[r]}
    c.need(delta=={'2':13,'6':-1,'14':1,'26':-32,'42':19},'credited PR3959 profile delta')
    return dict(status='PASS_REPLICA_INDEXED_IR_NOT_PHYSICAL_EXECUTION',moves=len(proposal['moves']),cross_replica_moves=62,logical_helpers=125856,local_events=independent[1],changed_local_events=c.changed_event_count(t,pooled),pooled_emitted_program_sha256=independent[0],profile={str(r):n for r,n in sorted(profile.items())},profile_delta=delta,paid_requests=sum(profile.values()),rank_mass=sum(r*n for r,n in profile.items()),idle_records=len(idles),idle_records_sha256=hashlib.sha256((json.dumps(idles,separators=(',',':'))+'\n').encode()).hexdigest(),first_counterexample=proposal['moves'][0],retained_catalogue_rejection='replica owner symmetry',controls_rejected=controls,physical_CALL_RETURN_executed=False,new_kappa_claim=False)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write-result',action='store_true');args=parser.parse_args();result=run()
    if args.write_result:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:c.need(result==json.loads((HERE/'RESULT.json').read_bytes()),'committed exact result')
    print(json.dumps(result,sort_keys=True));print('PASS_REPLICA_INDEXED_IR_AND_FACTORISATION_COUNTEREXAMPLE')
