#!/usr/bin/env python3
"""Compose four verified SOURCE birth-prefix rewrites and audit native output.

Apache-2.0; substantial OpenAI assistance under the user's direction.
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


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    path=HERE/'retimed444/WORD.json.gz';expected='ddc4f70ef7e0721f25bc5a2027ec09671457384aeb22b45f1a7dae33dae6482a'
    raw=gzip.decompress(path.read_bytes());assert sha256(raw).hexdigest()==expected;original=json.loads(raw);word=original
    module=load_checker(CHECKER);source_checker=module.Word(original);source_checker.full();baseline=actual_profile(original,source_checker);steps=[]
    for helper in (265,281,321,390):
        checker=module.Word(word);optimizer=Optimizer(word,checker,.001745)
        candidate,identity=build(word,helper,checker.fdim,optimizer.captures)
        regenerate_D(candidate);scalar(candidate);candidate,info=optimizer.optimize(candidate)
        native=module.Word(candidate);columns=native.full();hs,cs,_=native.interface()
        assert all(hs.values()) and all(cs.values());assert dict(actual_profile(candidate,native))==info['local_profile']
        assert info['saving']>1e-9
        assert captures(candidate)==captures(original)
        steps.append({'helper':helper,'identity':identity,'optimization':info,'content_sha256':sha256(canonical(candidate)).hexdigest()})
        word=candidate
    payload=canonical(word);word_path=args.out/'WORD.json.gz';word_path.write_bytes(gzip.compress(payload,mtime=0))
    profile=actual_profile(word,native);delta=profile.copy();delta.subtract(baseline);delta={r:c for r,c in delta.items() if c}
    assert delta=={1:4,2:-4,5:-4,6:4},delta
    controls=[]
    for section in ('D','C'):
        bad=deepcopy(word);bad[section]=original[section]
        try:module.Word(bad).full()
        except module.Reject as exc:controls.append({'name':'stale_'+section,'rejected':True,'reason':str(exc)})
        else:raise AssertionError(('stale section accepted',section))
    commands=[];parent=CHECKER.parent.parent
    for i,program_args in enumerate(((CHECKER,word_path),(parent/'vendor/export_records.py',word_path,args.out/'records'),(parent/'code/local_counter.py',args.out))):
        argv=[sys.executable,'-B']+list(map(str,program_args));t0=time.monotonic();run=subprocess.run(argv,capture_output=True,text=True)
        (args.out/f'check-{i}.log').write_text(run.stdout+run.stderr)
        commands.append({'argv':argv,'program_sha256':sha256(Path(argv[2]).read_bytes()).hexdigest(),'exit_code':run.returncode,'seconds':time.monotonic()-t0})
        assert run.returncode==0,(argv,run.stdout,run.stderr)
    pins=[path,CHECKER,HERE/'birth_prefix_resynthesis.py',HERE/'observation_repair.py',HERE/'source_quotient.py',HERE/'search_networks.py',HERE/'source_resynthesis.py',HERE/'checkpoint.py',Path(__file__)]
    result={'status':'PASS_FOUR_COMPOSED_SOURCE_PREFIX_REWRITES','source_content_sha256':expected,
            'word_content_sha256':sha256(payload).hexdigest(),'word_gzip_sha256':sha256(word_path.read_bytes()).hexdigest(),
            'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in pins},
            'construction':steps,'profile':dict(profile),'delta_from_retimed444':delta,
            'tariff_saving_at_0.001745':-sum(c*r**(1-.001745) for r,c in delta.items()),
            'counts':{s:sum(len(g[2]) for g in word[s]) for s in ('A','B','C','D')},
            'columns':columns,'hypotheses':hs,'conclusion':cs,'nine_SOURCE_captures':captures(word),
            'unchanged_interfaces':[k for k in ('R','v','h','start','final','ret','scatter') if word[k]==original[k]],
            'rejecting_controls':controls,'native_commands':commands,
            'native_legality':read(args.out/'cout/legality.json'),'native_columns':read(args.out/'cout/columns.json'),
            'scope':'All437 arbitrary dirty helpers retained with width8 endpoints. Nine SOURCE captures and frames preserved; intermediate dirty rows and actual D change. Local native arbitrary659/five-stage881 columns and integer prefix budget checked. Hosted/global caller and supplier/outer assumptions require integration.'}
    result['output_sha256']={str(p.relative_to(args.out)):sha256(p.read_bytes()).hexdigest() for p in sorted(args.out.rglob('*')) if p.is_file() and p.name!='RESULT.json'}
    (args.out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','word_content_sha256','profile','delta_from_retimed444','counts','native_columns')},indent=2))


if __name__=='__main__':main()
