#!/usr/bin/env python3
"""Bind the positive SOURCE-resynthesis word to independent native checks.

The source word and receipt are read-only. All replay outputs are written to
the supplied directory. Apache-2.0; OpenAI assistance under user direction.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse, gzip, json, subprocess, sys, time
from search_networks import ROOT, HERE, SOURCE, CHECKER, EXPECTED, read, load_checker, actual_profile

POSITIVE=HERE/'source-resynthesis/PASS1-SEED2.json.gz'
POSITIVE_SHA='14cd9ec8f8deb6e16364e550878a5cb4e3da3550d6969a39e94fe786957a1a48'


def paths(word):
    out=[[word['start'][r]] for r in range(word['v'])]
    for sec in ('D','A','B','C'):
        for f,d,ss in word[sec]:
            for r in {d,*ss}:
                if r<word['v'] and f!=out[r][-1]:out[r].append(f)
    for r in range(word['v']):
        if out[r][-1]!=word['final'][r]:out[r].append(word['final'][r])
    return out


def captures(word):
    n=2*word['v']+word['R'];v=word['v'];rows=[1<<r if r<v else 0 for r in range(n)];cur=list(word['start'])
    for f,d,ss in word['A']:
        for s in ss:rows[d]^=rows[s]
        for r in [d]+ss:cur[r]=f
    return [{'role':r,'frame':cur[r],'SOURCE_row':hex(rows[r])} for r in word['ret']]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    raw=gzip.decompress(POSITIVE.read_bytes());assert sha256(raw).hexdigest()==POSITIVE_SHA
    assert sha256(gzip.decompress(SOURCE.read_bytes())).hexdigest()==EXPECTED
    word=json.loads(raw);original=read(SOURCE);module=load_checker(CHECKER)
    checker=module.Word(word);local=checker.full();hypotheses,conclusion,_=checker.interface()
    assert all(hypotheses.values()) and all(conclusion.values())
    assert captures(word)==captures(original)
    invariant_keys=('R','v','h','start','final','ret','scatter')
    assert all(word[k]==original[k] for k in invariant_keys)
    controls=[]
    for name,mutate in (
        ('missing_D',lambda w:w.update(D=[])),
        ('stale_D',lambda w:w.update(D=deepcopy(original['D']))),
        ('stale_C',lambda w:w.update(C=deepcopy(original['C']))),
    ):
        bad=deepcopy(word);mutate(bad)
        try:module.Word(bad).full()
        except (AssertionError,ValueError,module.Reject) as exc:controls.append({'control':name,'rejected':True,'reason':str(exc)[:500]})
        else:raise AssertionError(('rejecting control accepted',name))
    native_word=args.out/'WORD.json.gz';native_word.write_bytes(POSITIVE.read_bytes())
    parent=CHECKER.parent.parent
    commands=[
        [sys.executable,'-B',str(CHECKER),str(native_word)],
        [sys.executable,'-B',str(parent/'vendor/export_records.py'),str(native_word),str(args.out/'records')],
        [sys.executable,'-B',str(parent/'code/local_counter.py'),str(args.out)],
    ]
    records=[]
    for i,argv in enumerate(commands):
        t0=time.monotonic();run=subprocess.run(argv,capture_output=True,text=True)
        log=args.out/f'check-{i}.log';log.write_text(run.stdout+run.stderr)
        record={'argv':argv,'exit_code':run.returncode,'seconds':time.monotonic()-t0,'program_sha256':sha256(Path(argv[2]).read_bytes()).hexdigest()}
        records.append(record);assert run.returncode==0,(record,run.stdout,run.stderr)
    pold,pnew=paths(original),paths(word)
    pins=[POSITIVE,HERE/'source-resynthesis/RESULT.json',SOURCE,CHECKER,Path(__file__)]
    result={'status':'PASS_SOURCE_RESYNTHESIS_NATIVE_CHECKPOINT','word_content_sha256':POSITIVE_SHA,
            'word_gzip_sha256':sha256(POSITIVE.read_bytes()).hexdigest(),'source_word_content_sha256':EXPECTED,
            'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in pins},
            'unchanged_interfaces':list(invariant_keys),'frame_catalogue_size':len(word['frames']),
            'profile':dict(actual_profile(word,checker)),'columns':local,'hypotheses':hypotheses,'conclusion':conclusion,
            'counts':{sec:sum(len(g[2]) for g in word[sec]) for sec in ('D','A','B','C')},
            'SOURCE_path_changes':[{'SOURCE':r,'old':a,'new':b} for r,(a,b) in enumerate(zip(pold,pnew)) if a!=b],
            'nine_SOURCE_captures':captures(word),'rejecting_controls':controls,'native_commands':records,
            'native_legality':read(args.out/'cout/legality.json'),'native_columns':read(args.out/'cout/columns.json'),
            'scope':'Complete local native word, arbitrary659 inputs, five-stage881 columns and integer norm prefixes checked. All437 helper width8 endpoints, ordered COPY roles and frames, and scatter recipients retained. SOURCE92 legitimately skips its old frame184 contact. Native parent realization and outer multiplication assumptions remain inherited; global hosted ownership and exact moment integration are separate.'}
    result['output_sha256']={str(p.relative_to(args.out)):sha256(p.read_bytes()).hexdigest() for p in sorted(args.out.rglob('*')) if p.is_file() and p.name!='RESULT.json'}
    (args.out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','word_content_sha256','profile','counts','SOURCE_path_changes','native_columns')},indent=2))


if __name__=='__main__':main()
