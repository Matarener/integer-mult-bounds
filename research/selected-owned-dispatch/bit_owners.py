#!/usr/bin/env python3
"""Independent typed census of the retained PR4440 BIT raw grammar.

This checks field identities/lifetimes, not projector algebra or native tapes.
No source verifier is imported. The verifier authenticates working source bytes.
Mason Hale with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import struct

COMMIT = 'de5ec2e7a6074068452f45b1a191b5c72832df4a'
PREFIX = 'research/kappa-rebuild/bit/sources/pr589-regenerated/'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def local(records, word, frames, reverse):
    n = 2*word['v']+word['R']
    current = list(word['final'] if reverse else word['start']) + [None]
    live, source, episodes = False, None, []
    paid, operations = Counter(), Counter()
    seq = list(enumerate(records))
    if reverse:
        seq.reverse()
    for idx, (op,x,y,c,f,z) in seq:
        operations[op] += 1
        need(0 <= x <= n, 'typed destination role')
        if op == 0:
            need(x < n or live, 'MOVE outside private lifetime')
            old,new = (c,y) if reverse else (y,c)
            need(current[x] == old and str(old) in frames and str(new) in frames,
                 'MOVE exact current frame')
            current[x] = new
            if f:
                paid[f] += 1
        elif op == 1:
            need(0 <= y <= n and x != y, 'ADD distinct valid roles')
            need((x < n or live) and (y < n or live), 'ADD outside private lifetime')
            need(current[x] == current[y] == f, 'ADD exact current frames')
            need(not live or x != source, 'copied source overwritten during lifetime')
        elif op == (3 if reverse else 2):
            need(not live and y == n and x < n and current[n] is None,
                 'COPY requires new private lifetime')
            need(current[x] == c and str(f) in frames, 'COPY source/current frame')
            live,source,current[n] = True,x,f
            episodes.append({'open':idx,'source':x})
            paid[abs(frames[str(c)]['dim']-frames[str(f)]['dim'])] += 1
        else:
            need(op == (2 if reverse else 3) and live and source == x and y == n,
                 'ERASE exactly matching private bank')
            episodes[-1]['close'] = idx
            live,source,current[n] = False,None,None
    need(not live and current[n] is None, 'private lifetime still live at endpoint')
    need(current[:n] == (word['start'] if reverse else word['final']),
         'public frame endpoints')
    need(len(episodes) == 9, 'all nine private lifetimes')
    return {'private_label':n,'public_fields':n,'lifetimes':episodes,
            'counts':dict(operations),'paid':dict(sorted(paid.items()))}


def global_census(controller, word, local_rows):
    v,h,p = word['v'],word['R'],controller['pairs']
    need((v,h,p)==(111,439,16), 'retained BIT family')
    main = {('main',i,j) for i in range(2*p) for j in range(v)}
    helpers, banks, calls, thin = set(),set(),[],[]
    paid = Counter()
    for site,event in enumerate(controller['physical_events']):
        op = event[0]
        if op == 'LOCAL':
            _,stage,pair,reverse = event
            need(type(reverse) is bool and 0 <= pair < p, 'LOCAL exact pair/direction')
            args = [('main',2*pair+i,j) for i in range(2) for j in range(v)]
            fresh = [('helper',site,j) for j in range(h)]
            args += fresh
            own = ('local-owned',site)
            need(len(args)==len(set(args))==2*v+h, 'local actual arguments injective')
            need(not set(fresh)&(main|helpers|banks) and own not in main|helpers|banks,
                 'local tag captures another field')
            helpers.update(fresh);banks.add(own)
            row = local_rows['reverse' if reverse else 'forward']
            paid.update({int(k):n for k,n in row['paid'].items()})
            calls.append({'site':site,'stage':stage,'pair':pair,'reverse':reverse,
                          'local_private_lifetimes':len(row['lifetimes'])})
        elif op == 'QUERY_SHEAR':
            _,stage,pair,reverse = event
            need(type(reverse) is bool and 0 <= pair < p, 'query exact pair/direction')
            for j in range(v):
                src=('main',2*pair+int(reverse),j)
                dst=('main',2*pair+1-int(reverse),j)
                own=('query-owned',j)
                need(src in main and dst in main and src != dst and own not in main|helpers,
                     'query three distinct physical fields')
                banks.add(own)
                # Expanded syntax: INIT own; COPY src->own; completed call own;
                # ADD own->dst; CLEAR own. It is sequential at each occurrence.
            thin.append({'site':site,'stage':stage,'pair':pair,'reverse':reverse,
                         'private_lifetimes':v})
            paid[1] += v
        elif op == 'IDLE':
            _,pair,stages = event
            need(0 <= pair < p and stages and len(set(stages))==len(stages),'idle owner/axes')
            paid[7*len(stages)] += 2*v
        else:
            need(op in ('ADD','SWAP') and len(event)==3, 'known controller opcode')
            _,a,b = event
            need(type(a) is int and type(b) is int and 0 <= a < 2*p and 0 <= b < 2*p and a != b,
                 'controller scalar distinct public roles')
    for side in ('left_program','right_program'):
        for op,a,b in controller['boundaries'][side]:
            need(op in ('ADD','SWAP') and 0 <= a < 2*p and 0 <= b < 2*p and a != b,
                 'scalar boundary only distinct public roles')
    invoice=controller['invoice']
    need(len(calls)==18 and len(thin)==15, 'all full/query occurrences')
    need(len(main|helpers)==invoice['productive_fields']==11454,'complete public inventory')
    need(len(banks)==129 and not banks&(main|helpers), 'safe raw private inventory')
    need(dict(paid)=={int(k):n for k,n in invoice['paid'].items()}, 'literal complete paid profile')
    return {'productive_fields':len(main|helpers),'main_fields':len(main),
            'helper_fields':len(helpers),'safe_raw_owned_banks':len(banks),
            'local_owned_banks':len(calls),'query_owned_banks':v,
            'local_private_lifetimes':18*9,'query_private_lifetimes':15*v,
            'total_private_lifetimes':18*9+15*v,'paid_calls':sum(paid.values()),
            'local_occurrences':calls,'query_occurrences':thin,
            'note':'129 is a safe deliberately overallocated raw inventory; source reuses one query stream sequentially. No final compiler inventory is asserted.'}


def run(repo):
    from hashlib import sha1
    pins={}
    def read(path):
        data=(repo/path).read_bytes()
        pins[path]={'sha256':sha256(data).hexdigest(),
                    'git_blob':sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}
        return data
    word=json.loads(gzip.decompress(read(PREFIX+'WORD.json.gz')))
    frames=json.loads(read(PREFIX+'records/frames.json'))['frames']
    records=list(struct.iter_unpack('<6i',read(PREFIX+'records/249-records.bin')))
    controller=json.loads(read('research/query-thinned-controllers/BIT-CONTROLLER.json'))
    local_rows={name:local(records,word,frames,reverse) for name,reverse in [('forward',False),('reverse',True)]}
    global_row=global_census(controller,word,local_rows)
    bad=list(records);first=next(i for i,r in enumerate(bad) if r[0]==2)
    z=list(bad[first]);z[2]=0;bad[first]=tuple(z)
    try:local(bad,word,frames,False)
    except ValueError as exc:rejected=str(exc)
    else:raise ValueError('borrowed COPY target mutant accepted')
    result={'status':'PASS_TYPED_BIT_RAW_OWNERSHIP','source_commit':COMMIT,'sources':pins,
            'local':local_rows,'global':global_row,'negative_control':rejected,
            'scope':'Finite actual source-name/lifetime/current-frame census; no independent scalar/native/cover/physical/precision theorem.'}
    return result


if __name__=='__main__':
    print(json.dumps(run(Path(__file__).resolve().parents[2]),indent=2,sort_keys=True))
