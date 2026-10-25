#!/usr/bin/env python3
"""Centre lifetime and outer interface audit. Apache-2.0.
Chris R / Clear1nsight with substantial OpenAI assistance and three separately
assigned AI agents. Checkers import no predecessor executable. See REVIEWS.json.
"""
from hashlib import sha1,sha256
from fractions import Fraction as Q
import json
from pathlib import Path
import types

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DEMAND_PIN='f513d235b8206211a4716d013a6dacf34aaebda6839da721b0231981cb8b905e'


def need(ok,why):
    if not ok:raise ValueError(why)


def decode(raw):
    def unique(items):
        result={}
        for k,v in items:
            need(k not in result,'duplicate JSON key');result[k]=v
        return result
    return json.loads(raw,object_pairs_hook=unique)


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()


def authenticate():
    pins=decode((HERE/'SOURCES.json').read_bytes())
    need(pins['base_commit']=='20ecf2891d80b5acf18d980b2164fb44ea7faa90','scientific base')
    raw={}
    for pin in pins['files']:
        if pin['usage']!='input':continue
        data=(ROOT/pin['path']).read_bytes()
        need(sha256(data).hexdigest()==pin['sha256'],'source SHA256: '+pin['path'])
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==pin['git_blob'],'source Git blob: '+pin['path'])
        raw[pin['path']]=data
    need(sha256((HERE/'vendor/pr3952/WORD.json').read_bytes()).hexdigest()==DEMAND_PIN,'retained PR3952 word')
    return raw


def load(name):
    path=HERE/(name+'.py');module=types.ModuleType(name);module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


def calculate():
    raw=authenticate()
    centres=load('centres').run(ROOT)
    outer=load('outer').run(ROOT)
    continuation=load('continuation').run(ROOT,HERE/'vendor/pr3952')
    budget=load('budget')
    arithmetic=budget.calculate()
    profiles=centres['actual_QQ16_calls']
    f=profiles['F_0']['total_literal_child_profile']
    b=profiles['B_1_2']['total_literal_child_profile']
    need(budget.BASE=={r:Q(f.get(r,0)+b.get(r,0),2) for r in set(f)|set(b)},'arithmetic producer profile binding')
    selected=decode(raw['certificates/selected-result.json'])
    need(selected['kappa']=='836330098538459/500000000000000000','selected target pin')
    kappa=Q(selected['kappa'])
    need(budget.A==kappa/(1-kappa),'arithmetic selected exponent binding')
    ceiling=decode(raw['research/complex-local-word-ceiling/RESULT.json'])
    need(ceiling['model']['m']==73 and ceiling['model']['live_families_per_call']=='896/9' and ceiling['model']['centre_per_call']==64,'conditional coverage context')
    need(ceiling['selected']['local_profile_per_call']['8']==8,'historical eight-H8 premise')
    legacy=decode(raw['research/joint-query/evidence/CLEAN-J-CHECKS.json'])
    for side in ('forward','backward'):
        need(legacy['orientations'][side]['removed_centre_rank_mass']==64,'already removed rank64')
        need(legacy['orientations'][side]['primitive_bound_real_components']==202138,'existing paid clean-core scalar allowance')
    need(continuation['full_decoder_invoice']['line']==336 and continuation['projected_invoice']['line']==112,'consumer native bill binding')
    need(arithmetic['restored_full_consumer336_pair_h8_waived']['decision']=='strict_fail','complete fallback obstruction')
    need(outer['independent_missing_query_directions']==8,'outer missing-query witness')
    return {'status':'PASS_QQ16_CENTRE_LIFETIME_BOUNDARY_AUDIT no_new_kappa',
        'centre_provenance_and_lifetimes':centres,'actual_outer_boundary':outer,
        'actual_recovery_continuation':continuation,'conditional_budget':arithmetic,
        'decision':'No remaining literal H8 centre retirement exists in the QQ16 core. The projected96-output endpoint does not replace either pinned outer boundary alone. Existing full-decoder fallback is priced and fails the unchanged pair screen even with H8 absent. No new physical/global schedule admitted.'}


def main():
    result=calculate()
    need(canonical(result)==canonical(decode((HERE/'RESULT.json').read_bytes())),'complete RESULT mismatch')
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':main()
