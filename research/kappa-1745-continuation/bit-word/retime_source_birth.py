#!/usr/bin/env python3
"""Chronologically retime the unobserved SOURCE77 birth of helper444.

PR4067 (Chris R / Clear1nsight, with Codex assistance) supplied the useful
chronological/rank-split lead. This is a separate minimal construction on the
current SOURCE-resynthesis checkpoint: commute one SOURCE read to A entrance;
no debt helper, extra ADD or changed D is needed. Apache-2.0; OpenAI assistance.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json,subprocess,sys,time
from search_networks import ROOT,HERE,CHECKER,read,canonical,cleanup,scalar,load_checker,actual_profile

SOURCE=HERE/'checkpoint/WORD.json.gz'
EXPECTED='14cd9ec8f8deb6e16364e550878a5cb4e3da3550d6969a39e94fe786957a1a48'


def raw(word):
    n=2*word['v']+word['R'];v=word['v'];rows=[1<<r for r in range(n)]
    for f,d,ss in word['A']:
        for s in ss:rows[d]^=rows[s]
    cap=[rows[r] for r in word['ret']]
    for t,indices in enumerate(word['scatter']):
        for k in indices:rows[v+t]^=cap[k]
    for f,d,ss in word['B']:
        for s in ss:rows[d]^=rows[s]
    return rows,cap


def build(word):
    assert all(d>=2*word['v'] for f,d,ss in word['A'])
    matches=[i for i,g in enumerate(word['A']) if g==[186,444,[77]]]
    assert len(matches)==1;index=matches[0]
    assert all(444 not in [d]+ss for f,d,ss in word['A'][:index])
    assert word['start'][444]==0 and word['start'][77]==79
    out=deepcopy(word);out['A']=[[79,444,[77]]]+word['A'][:index]+word['A'][index+1:]
    cleanup(out)
    assert out['D']==word['D'] and raw(out)==raw(word)
    scalar(out)
    return out,index


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    data=gzip.decompress(SOURCE.read_bytes());assert sha256(data).hexdigest()==EXPECTED
    source=json.loads(data);word,index=build(source);payload=canonical(word)
    word_path=args.out/'WORD.json.gz';word_path.write_bytes(gzip.compress(payload,mtime=0))
    module=load_checker(CHECKER);old=module.Word(source);native=module.Word(word)
    old.full();columns=native.full();hs,cs,_=native.interface();assert all(hs.values()) and all(cs.values())
    profile=actual_profile(word,native);delta=profile.copy();delta.subtract(actual_profile(source,old))
    delta={r:c for r,c in delta.items() if c};assert delta=={1:1,2:-2,3:1}
    controls=[]
    bad=deepcopy(word);bad['C']=source['C']
    try:
        bh,_,_=module.Word(bad).interface()
        assert not bh['H4_C_literal_reverse_at_full']
        controls.append({'name':'stale_literal_C','rejected':True,'gate':'H4_C_literal_reverse_at_full'})
    except module.Reject as exc:controls.append({'name':'stale_literal_C','rejected':True,'reason':str(exc)})
    bad=deepcopy(word);bad['A'][0][0]=0
    try:module.Word(bad).full()
    except module.Reject as exc:controls.append({'name':'underpaid_zero_birth_frame','rejected':True,'reason':str(exc)})
    else:raise AssertionError('underpaid birth accepted')
    parent=CHECKER.parent.parent;commands=[]
    for i,program_args in enumerate(((CHECKER,word_path),(parent/'vendor/export_records.py',word_path,args.out/'records'),(parent/'code/local_counter.py',args.out))):
        argv=[sys.executable,'-B']+list(map(str,program_args));t0=time.monotonic()
        run=subprocess.run(argv,capture_output=True,text=True);(args.out/f'check-{i}.log').write_text(run.stdout+run.stderr)
        commands.append({'argv':argv,'program_sha256':sha256(Path(argv[2]).read_bytes()).hexdigest(),'exit_code':run.returncode,'seconds':time.monotonic()-t0})
        assert run.returncode==0,(argv,run.stdout,run.stderr)
    lead=ROOT/'research/kappa-1745-continuation/sources/PR4067-BODY.md'
    pins=[SOURCE,CHECKER,HERE/'search_networks.py',Path(__file__),lead]
    result={'status':'PASS_CHRONOLOGICAL_SOURCE77_BIRTH_RETIMING','source_content_sha256':EXPECTED,
            'word_content_sha256':sha256(payload).hexdigest(),'word_gzip_sha256':sha256(word_path.read_bytes()).hexdigest(),
            'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in pins},
            'construction':{'removed_A_group_index':index,'removed':[186,444,[77]],'prepended':[79,444,[77]],
                            'proof':'A never writes any SOURCE. Helper444 has no earlier A contact. The read commutes left through the entire preceding A prefix, and its entrance frame is the exact SOURCE77 line. D, B, all raw dirty/SOURCE capture rows and raw final rows remain identical to the input checkpoint. C is regenerated in the new literal inverse order.'},
            'attribution':'PR4067, Chris R / Clear1nsight with Codex assistance, exposed the chronological receiver444 (2,2) to (1,3) rank split. The present early77-read construction on our checkpoint is separately derived and uses no467/469 debt route.',
            'profile':dict(profile),'delta_from_checkpoint':delta,'tariff_saving_at_0.001745':-sum(c*r**(1-.001745) for r,c in delta.items()),
            'columns':columns,'hypotheses':hs,'conclusion':cs,'counts':{s:sum(len(g[2]) for g in word[s]) for s in ('A','B','C','D')},
            'unchanged_keys':[k for k in source if source[k]==word[k]],'rejecting_controls':controls,
            'native_commands':commands,'native_legality':read(args.out/'cout/legality.json'),'native_columns':read(args.out/'cout/columns.json'),
            'scope':'Full local native word and arbitrary659/five-stage881 columns checked. All437 width8 helper owners and nine COPY roles/frames stay unchanged. Complete pooled owner, actual caller, coefficient/stock and outer supplier assumptions require integration.'}
    result['output_sha256']={str(p.relative_to(args.out)):sha256(p.read_bytes()).hexdigest() for p in sorted(args.out.rglob('*')) if p.is_file() and p.name!='RESULT.json'}
    (args.out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','word_content_sha256','profile','delta_from_checkpoint','counts','native_columns')},indent=2))


if __name__=='__main__':main()
