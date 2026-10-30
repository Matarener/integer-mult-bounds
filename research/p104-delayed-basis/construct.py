"""Compose only Ali Romman's PR5602 helper341 paid-boundary change.

PR5602 head6c224aa720203c4f4615e6538d8038a275387db8 supplied the exact
boundary relation. Adapted and independently checked for flyingviper by
OpenAI Codex. Apache-2.0. This is a composition, not a new basis identity.
"""
from copy import deepcopy
from hashlib import sha256
import json

SOURCE_CANONICAL_SHA256='df44a24231edd04954ebf066b1efb311441e5d9d48b64d03e555cbea087b25c6'
CUT=11285
MARKER=['ADD',346,341,'1',240]
REMOVED=[['SCALE',341,'-1',240],['ADD',341,339,'-1',240],
         ['ADD',341,337,'1',240],['MOVE',341,240,127,False],
         ['ADD',341,744,'-1',127],['SCALE',341,'-1',127],
         ['ADD',341,712,'4',127],['ADD',341,744,'1',127]]

def need(ok,why):
    if not ok:raise ValueError(why)

def construct(source):
    digest=sha256(json.dumps(source,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    need(digest==SOURCE_CANONICAL_SHA256,'Exact final delayed/prepared source payload')
    program=source['program']
    need(program[CUT]==MARKER,'Pinned final helper341 source read')
    need(source['initial'][341]==3 and source['final'][341]==127,'Original helper341 interface')
    need(all(source['initial'][r]==3 for r in [93,339,341,351]),'Initial helper basis at common zero chart')
    tail=program[CUT+1:]
    need(not any(e[0] in ('ADD','COPY') and e[2]==341 for e in tail),'No later helper341 source read')
    need([e for e in tail if e[1]==341]==REMOVED,'Exact retired suffix, including one rank5 transport')
    before=[['ADD',341,93,'2',3],['ADD',341,339,'2',3],['ADD',341,351,'-2',3]]
    middle=[['ADD',341,337,'-2',240]]
    out=deepcopy(source)
    out['program']=before+deepcopy(program[:CUT+1])+middle+[deepcopy(e) for e in tail if e[1]!=341]
    out['final'][341]=240
    need(len(out['program'])==25525,'Four added basis operations replace eight suffix operations')
    return out
