#!/usr/bin/env python3
"""Reprice every feasible prefix reconstruction with joint frame optimization.

This closes the concrete risk that a tied/lossy fixed-frame reconstruction
creates a favorable subsequent frame assignment. Apache-2.0; OpenAI assistance.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json,time
from search_networks import ROOT,HERE,CHECKER,read,canonical,load_checker,actual_profile,Optimizer,scalar
from source_quotient import regenerate_D
from birth_prefix_resynthesis import build as early
from late_prefix_resynthesis import build as late


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    path=HERE/'retimed444/WORD.json.gz';expected='ddc4f70ef7e0721f25bc5a2027ec09671457384aeb22b45f1a7dae33dae6482a'
    raw=gzip.decompress(path.read_bytes());assert sha256(raw).hexdigest()==expected;word=json.loads(raw)
    module=load_checker(CHECKER);checker=module.Word(word);checker.full();optimizer=Optimizer(word,checker,.001745)
    stats=Counter();cases=[];t0=time.monotonic()
    for kind,build in (('last_write',early),('first_observer',late)):
        for helper in range(222,659):
            if helper==469:continue
            try:out,identity=build(word,helper,checker.fdim,optimizer.captures)
            except ValueError:continue
            stats[kind+'_feasible']+=1;regenerate_D(out);scalar(out)
            try:optimized,info=optimizer.optimize(out)
            except ValueError as exc:
                cases.append({'kind':kind,'helper':helper,'reject':str(exc)});continue
            native=module.Word(optimized)
            try:
                native.full();profile=actual_profile(optimized,native)
                assert dict(profile)==info['local_profile']
            except (module.Reject,AssertionError) as exc:
                cases.append({'kind':kind,'helper':helper,'reject':'actual frame/interface: '+str(exc)});continue
            case={'kind':kind,'helper':helper,'identity':identity,'optimization':info}
            if info['saving']>1e-9:
                payload=canonical(optimized);name=f'{kind}-{helper}.json.gz';(args.out/name).write_bytes(gzip.compress(payload,mtime=0))
                case.update(word=name,content_sha256=sha256(payload).hexdigest());stats['positive']+=1
            cases.append(case);print('CASE',kind,helper,'saving',info['saving'],'delta',info['delta'],flush=True)
    pins=[path,CHECKER,HERE/'birth_prefix_resynthesis.py',HERE/'late_prefix_resynthesis.py',HERE/'observation_repair.py',HERE/'source_quotient.py',HERE/'source_resynthesis.py',HERE/'search_networks.py',Path(__file__)]
    result={'status':'FINITE_FEASIBLE_PREFIX_JOINT_FRAME_FOLLOWUP','source_content_sha256':expected,
            'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in pins},
            'stats':dict(stats),'cases':cases,'seconds':time.monotonic()-t0,
            'scope':'Every compatible greedy SOURCE-prefix reconstruction at last write or first observer is repriced over the758-frame joint optimizer; source-span rejected graphs remain outside this followup.'}
    (args.out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('DONE',dict(stats),time.monotonic()-t0,flush=True)


if __name__=='__main__':main()
