"""Full current topology/controller and authenticated old/new record delta.

Compiler/controller are explicitly reused predecessor code, not independent
reimplementations. Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import types
import adapter


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))


def run():
    current,topology = adapter.load()
    from control import LocalState
    counts=Counter()
    for stage in range(9):
        for replica in range(32):
            call=topology.call(stage,replica)
            state=LocalState(call)
            for position,event in enumerate(call.events):
                op,role=state.accept(position);counts[op]+=1
                if op in (0,2):
                    request=current.requests[call.requests[position]]
                    adapter.require((request.stage,request.position,request.role)==(stage,position,role),
                                    'actual literal request and controller site')
            state.finish()
    adapter.require(sum(counts.values())==7814016 and counts[2]==counts[3]==2592,
                    'complete current chronology and COPY/disposal census')
    # Same retained compiler with the exact old source data/digest, never a
    # disabled guard. This is a source comparison, not an independent compiler.
    source=Path(adapter.__file__).read_text()
    source=adapter.replacement(source,adapter.REQUEST_DIGEST,
                              '0fb70d6838583f2f439a8704eb5dba84ce9dbd231d91f140da13440b680d73aa',1)
    source=adapter.replacement(source,"'inputs/EXPECTED.json'","'inputs/old-EXPECTED.json'",1)
    source=adapter.replacement(source,"('inputs/' + name + '.json.gz')",
                              "('inputs/old-template.json.gz' if name == 'template' else 'inputs/' + name + '.json.gz')",1)
    source=adapter.replacement(source,"expected['profile'].get('26') == 32 and '34' not in expected['profile']",
                              "expected['profile'].get('34') == 64 and '26' not in expected['profile']",1)
    module=types.ModuleType('authenticated_old_adapter');module.__file__=adapter.__file__
    sys.modules[module.__name__]=module
    exec(compile(source,'<PR3690 old-data positive control>','exec'),module.__dict__)
    old,_=module.load()
    adapter.require(len(old.requests)==len(current.requests)==28233,'stable source ordinal extent')
    changes=[]
    for i,(a,b) in enumerate(zip(old.requests,current.requests)):
        adapter.require(old.semantic_key(a)==current.semantic_key(b),'stable exact source ordinal labels')
        if canonical(a.record())!=canonical(b.record()):
            changes.append({'identifier':i,'old':a.record(),'current':b.record()})
    rank_delta={str(r):current.profile[r]-old.profile[r] for r in sorted(set(old.profile)|set(current.profile))
                if current.profile[r]!=old.profile[r]}
    adapter.require(rank_delta=={'26':32,'34':-64,'42':32},'exact OQ4 rank-profile delta')
    adapter.require(sum(r*n for r,n in current.profile.items())==1808352==sum(r*n for r,n in old.profile.items()),
                    'unchanged full rank mass')
    old_digest=adapter.REQUEST_DIGEST
    try:
        adapter.REQUEST_DIGEST='0fb70d6838583f2f439a8704eb5dba84ce9dbd231d91f140da13440b680d73aa'
        try:adapter.load()
        except ValueError as error:
            adapter.require(str(error)=='exact ordered PR2234 request records','old digest rejects current OQ4 data')
        else:raise ValueError('stale ordered request digest accepted')
    finally:adapter.REQUEST_DIGEST=old_digest
    return {'status':'PASS_FULL_OQ4_SOURCE_TOPOLOGY_AND_CHRONOLOGY',
            'current':current.receipt(),'old':old.receipt(),'literal_opcode_counts':dict(counts),
            'changed_request_count':len(changes),'changed_requests':changes,
            'rank_profile_delta':rank_delta,'stale_digest_control':'REJECTED',
            'full_GL64_low_classes_executed':False,
            'scope':'Every literal source/controller site; all-low numerical emitter remains a quantified dependency'}


if __name__=='__main__':print(json.dumps(run(),sort_keys=True,indent=2))
