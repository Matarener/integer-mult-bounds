#!/usr/bin/env python3
"""Open new donor windows by moving zero-tariff one-SOURCE births earlier.

This schedules283 first-contact helper writes before the original A prefix,
then considers only newly feasible whole-prefix replacements and exact frame
optimization. SOURCE rows are preserved when first observed; intermediate
dirty rows are free and D is regenerated. Apache-2.0; OpenAI assistance.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json,subprocess,sys,time
from search_networks import ROOT,HERE,CHECKER,read,canonical,scalar,load_checker,actual_profile,Optimizer
from source_quotient import regenerate_D
from birth_prefix_resynthesis import build
from checkpoint import captures


def schedule(word):
    v=word['v'];n=2*v+word['R'];rows=[1<<r if r<v else 0 for r in range(n)];seen=set();births=[]
    assert all(d>=2*v for f,d,ss in word['A'])
    for i,(f,d,ss) in enumerate(word['A']):
        inc=0
        for s in ss:inc^=rows[s]
        if d>=2*v and d not in seen and inc.bit_count()==1:
            x=inc.bit_length()-1
            if f==word['start'][x]:births.append((i,f,d,x))
        rows[d]^=inc;seen.update([d]+ss)
    out=deepcopy(word);ids={i for i,f,d,x in births}
    out['A']=[[f,d,[x]] for i,f,d,x in births]+[g for i,g in enumerate(word['A']) if i not in ids]
    regenerate_D(out);scalar(out)
    return out,births


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--passes',type=int,default=2);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    path=HERE/'prefix-composed4/WORD.json.gz';expected='06afaebe9b984873e72e31af1dc1bf00f34a97394f3cc4e13da71cf46432b796'
    raw=gzip.decompress(path.read_bytes());assert sha256(raw).hexdigest()==expected;original=json.loads(raw)
    module=load_checker(CHECKER);source_checker=module.Word(original);source_checker.full();baseline=actual_profile(original,source_checker)
    word,births=schedule(original);scheduled_checker=module.Word(word);scheduled_checker.full()
    assert actual_profile(word,scheduled_checker)==baseline and captures(word)==captures(original)
    scheduled_payload=canonical(word);(args.out/'SCHEDULED.json.gz').write_bytes(gzip.compress(scheduled_payload,mtime=0))
    static=Optimizer(original,source_checker,.001745);price=static.price;caps=static.captures
    best=sum(price[r]*c for r,c in baseline.items());steps=[];stats=Counter();cases=[];t0=time.monotonic()
    for trial in range(args.passes):
        entered=best
        for helper in range(222,659):
            if helper==469:continue
            stats['attempted']+=1
            try:candidate,identity=build(word,helper,source_checker.fdim,caps)
            except ValueError as exc:stats[str(exc.args[0][0])]+=1;continue
            stats['SOURCE_prefix_rebuilt']+=1
            regenerate_D(candidate);scalar(candidate)
            optimizer=Optimizer(word,source_checker,.001745)
            try:candidate,info=optimizer.optimize(candidate)
            except ValueError as exc:
                cases.append({'pass':trial,'helper':helper,'rejected':str(exc)});continue
            cases.append({'pass':trial,'helper':helper,'local_delta':info['delta'],'local_saving':info['saving']})
            if info['saving']<=1e-9:continue
            native=module.Word(candidate);columns=native.full();hs,cs,_=native.interface();profile=actual_profile(candidate,native)
            assert all(hs.values()) and all(cs.values());assert dict(profile)==info['local_profile'];assert captures(candidate)==captures(original)
            value=sum(price[r]*c for r,c in profile.items());assert value<best-1e-9
            best=value;word=candidate;payload=canonical(word);name=f'PASS{trial}-HELPER{helper}.json.gz'
            (args.out/name).write_bytes(gzip.compress(payload,mtime=0))
            steps.append({'pass':trial,'helper':helper,'identity':identity,'optimization':info,'word':name,'content_sha256':sha256(payload).hexdigest()})
            stats['positive']+=1
            print('FOUND',trial,helper,'local',info['saving'],'total',sum(price[r]*c for r,c in baseline.items())-best,'delta',info['delta'],flush=True)
        if best==entered:break
    payload=canonical(word);word_path=args.out/'WORD.json.gz';word_path.write_bytes(gzip.compress(payload,mtime=0))
    native=module.Word(word);columns=native.full();hs,cs,_=native.interface();profile=actual_profile(word,native);delta=profile.copy();delta.subtract(baseline);delta={r:c for r,c in delta.items() if c}
    controls=[]
    if steps:
        for section in ('D','C'):
            bad=deepcopy(word);bad[section]=original[section]
            try:module.Word(bad).full()
            except module.Reject as exc:controls.append({'name':'stale_'+section,'rejected':True,'reason':str(exc)})
            else:raise AssertionError(('stale section accepted',section))
    commands=[];parent=CHECKER.parent.parent
    for i,program_args in enumerate(((CHECKER,word_path),(parent/'vendor/export_records.py',word_path,args.out/'records'),(parent/'code/local_counter.py',args.out))):
        argv=[sys.executable,'-B']+list(map(str,program_args));t1=time.monotonic();run=subprocess.run(argv,capture_output=True,text=True)
        (args.out/f'check-{i}.log').write_text(run.stdout+run.stderr);commands.append({'argv':argv,'program_sha256':sha256(Path(argv[2]).read_bytes()).hexdigest(),'exit_code':run.returncode,'seconds':time.monotonic()-t1});assert run.returncode==0,(argv,run.stdout,run.stderr)
    pins=[path,CHECKER,HERE/'birth_prefix_resynthesis.py',HERE/'observation_repair.py',HERE/'source_quotient.py',HERE/'search_networks.py',HERE/'source_resynthesis.py',HERE/'checkpoint.py',Path(__file__)]
    result={'status':'PASS_EARLY_SOURCE_BIRTH_SCHEDULE_AND_PREFIX_SEARCH','source_content_sha256':expected,
            'word_content_sha256':sha256(payload).hexdigest(),'word_gzip_sha256':sha256(word_path.read_bytes()).hexdigest(),
            'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in pins},
            'initial_zero_tariff_birth_schedule':births,'scheduled_content_sha256':sha256(scheduled_payload).hexdigest(),
            'construction':steps,'stats':dict(stats),'cases':cases,'profile':dict(profile),'delta_from_composed4':delta,
            'tariff_saving_at_0.001745':-sum(c*price[r] for r,c in delta.items()),'counts':{s:sum(len(g[2]) for g in word[s]) for s in ('A','B','C','D')},
            'columns':columns,'hypotheses':hs,'conclusion':cs,'nine_SOURCE_captures':captures(word),
            'unchanged_interfaces':[k for k in ('R','v','h','start','final','ret','scatter') if word[k]==original[k]],
            'rejecting_controls':controls,'native_commands':commands,'native_legality':read(args.out/'cout/legality.json'),'native_columns':read(args.out/'cout/columns.json'),
            'seconds':time.monotonic()-t0,
            'scope':'Finite zero-tariff early birth schedule followed by greedy SOURCE-prefix/joint-frame search. All437 dirty helpers keep width8 endpoints; captures preserve SOURCE rows, not old dirty responses. Local native881-column/prefix admission is checked; global actual caller/owner and supplier/outer premises need separate integration.'}
    result['output_sha256']={str(p.relative_to(args.out)):sha256(p.read_bytes()).hexdigest() for p in sorted(args.out.rglob('*')) if p.is_file() and p.name!='RESULT.json'}
    (args.out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('DONE',dict(stats),'delta',delta,'seconds',time.monotonic()-t0,flush=True)


if __name__=='__main__':main()
