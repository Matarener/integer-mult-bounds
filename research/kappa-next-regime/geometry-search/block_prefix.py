#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound separation of the seven5-replica payload blocks.

The prefix bound permits arbitrary coefficient growth across all45 calls in
one block. It uses no per-call semantic reset for regular dirty helpers.
Retained routing/recursive-D norm-one contracts stay explicit hypotheses.
"""
from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
POOL=HERE/'pool35/GLOBAL-TEMPLATE.json.gz'
DRIVER=REPO/'research/selected-bit-physical-caller/inputs/pr2753/predecessor/driver.py'
MACRO=REPO/'research/selected-bit-physical-caller/macro_code.py'


def need(ok,reason):
    if not ok:raise ValueError(reason)


def local_bound(program):
    values=[1<<i for i in range(659)]+[0]
    sizes=[1]*659+[0]
    open_source=None;maximum=1;copies=erases=0
    for event in program:
        op,dst=event[:2]
        if op==0:
            need(dst<659 and open_source is None,'frame MOVE outside private lifetime')
        elif op==1:
            src,c=event[2:4]
            need(0<=dst<659 and 0<=src<=659 and dst!=open_source,
                 'ordinary local ADD and immutable COPY source')
            need(src<659 or open_source is not None,'private payload not read after closure')
            if c%2:values[dst]^=values[src]
            sizes[dst]+=abs(c)*sizes[src]
            maximum=max(maximum,sizes[dst])
        elif op==2:
            need(open_source is None and event[2]==659 and values[659]==0 and sizes[659]==0,
                 'COPY opens a clean shared private field')
            open_source=dst;values[659]=values[dst];sizes[659]=sizes[dst];copies+=1
        else:
            need(op==3 and event[2]==659 and open_source==dst and values[659]==values[dst],
                 'exact Boolean private erasure guard')
            values[659]=sizes[659]=0;open_source=None;erases+=1
    need(open_source is None and values[659]==sizes[659]==0 and copies==erases==9,
         'all nine private episodes return clean')
    return maximum,copies


def block_audit(template):
    T,W=template['replicas'],template['live']
    need((T,W)==(35,31080),'literal seven-block domain')
    groups=[Counter() for _ in range(7)]
    known=set()
    for call in template['calls']:
        rep=call['replica'];block=rep//5
        need(0<=rep<35 and (call['stage'],rep) not in known,'unique stage replica')
        known.add((call['stage'],rep))
        need(len(call['owners'])==659,'complete payload owner inventory')
        for family,route in call['owners']:
            need(0<=family<W and family//4440==block,'every regular local owner remains in its five-replica block')
        groups[block][call['orientation']]+=1
    need(known=={(s,r) for s in range(9) for r in range(35)},'all315 literal calls')
    for g in groups:need(g=={'forward':25,'reverse':20},'all45 calls in each payload block')
    bridges=0;bridge_adds=0;exchanges=0
    for event in template['schedule']:
        if event['kind']=='bridge':
            dst,src,c=event['dst'],event['src'],event['coefficient']
            need(dst!=src and 0<=dst<4 and 0<=src<4 and c in (-1,1),'same-replica bridge grammar')
            bridges+=1
            for rep in range(35):
                for side in (0,1):
                    destinations=set();sources=set()
                    for port in range(111):
                        dp,sp=(dst,src) if side==0 else (src,dst)
                        df=888*rep+(2*dp+side)*111+port
                        sf=888*rep+(2*sp+side)*111+port
                        need(df//4440==sf//4440==rep//5,'bridge stays inside a payload block')
                        destinations.add(df);sources.add(sf);bridge_adds+=1
                    need(len(destinations)==len(sources)==111 and not destinations.intersection(sources),
                         '111 independent rows in each bridge shear layer')
        elif event['kind']=='exchange':exchanges+=1
    need(bridges==9 and exchanges==1 and bridge_adds==69930,'all9bridgeevents andterminalexchange')
    # Every idle record is unary on one ordinary family. Its exact axis
    # extent is covered by the independent owner/idle receipt.
    idles=json.loads(gzip.decompress((HERE/'pool35/IDLE-INVENTORY.json.gz').read_bytes()))
    for child,rep,cp,family,used,rank in idles:
        need(family//4440==rep//5 and 0<=family<W,'unary idle remains in the same block')
    return groups,bridges,len(idles),bridge_adds


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=HERE/'BLOCK-PREFIX-REVIEW.json')
    args=parser.parse_args()
    need(not args.out.exists(),'fresh receipt path required')
    template=json.loads(gzip.decompress(POOL.read_bytes()))
    candidate=json.loads((HERE/'pool35/RESULT.json').read_bytes())
    raw=json.dumps(template,sort_keys=True,separators=(',',':')).encode()
    need(sha256(raw).hexdigest()==candidate['template_content_sha256'],'candidate source binding')
    forward,cf=local_bound(template['local_programs']['forward'])
    backward,cb=local_bound(template['local_programs']['reverse'])
    need((forward,backward,cf,cb)==(49347,1113998,9,9),'recomputed exact native IR norms and private cleanup')
    groups,bridges,idles,adds=block_audit(template)
    per_replica=(1<<18)*forward**5*backward**4
    block=(1<<90)*forward**25*backward**20
    need(block==per_replica**5 and block.bit_length()==882,'conservative product over one full five-replica block')
    sequential=per_replica**35
    controls={}
    changed=deepcopy(template);changed['calls'][0]['owners'][222][0]+=4440
    try:block_audit(changed)
    except ValueError as exc:controls['cross_block_owner']=str(exc)
    else:raise ValueError('cross-block payload read accepted')
    changed_program=[e for e in template['local_programs']['forward']]
    last=max(i for i,e in enumerate(changed_program) if e[0]==3)
    changed_program.pop(last)
    try:local_bound(changed_program)
    except ValueError as exc:controls['missing_private_closure']=str(exc)
    else:raise ValueError('private carry between calls accepted')
    result=dict(status='PASS_SEVEN_PAYLOAD_BLOCKS_AND_CONSERVATIVE_FIVE_REPLICA_PREFIX',
        replicas=35,payload_blocks=7,replicas_per_block=5,families_per_block=4440,
        exact_local_bounds={'forward':forward,'reverse':backward},
        each_block={'forward_calls':25,'reverse_calls':20,'bridge_shear_layers':90},
        total_calls=315,total_bridge_adds=adds,absolute_idle_children=idles,
        private_COPY_ERASE_episodes=315*9,private_regular_payload_carry=False,
        coefficient_prefix_bound=str(block),prefix_bits=block.bit_length(),charged_prefix_bits=896,
        fully_sequential_comparison_bits=sequential.bit_length(),controls=controls,
        proof='Regular payload families partition by floor(family/4440). Every call touches only its own block; all bridge rows and unary idle/exchange operations remain in that block. Shared temporary payload is clean on entry and return for all9COPY/ERASE episodes percall. Therefore otherblocks cannot increase a block input norm. The product of all25forward and20reverse local bounds and90binary bridge shear bounds controls everyprefix of thatblock, without resetting regular dirty-helper norms between itscalls. The maximum of7suchblockbounds is the same882bitbound, rather than theirproduct.',
        inherited_hypotheses=['The retained packet/source/recursive-D interface implements frame moves and routes as payload permutations of norm1.',
          'The existing local-cover lifting transfers the recomputed local IR norm bound to one native cover sweep, as in the predecessor finite invoice.',
          'Compiler/controller scratch is outside the regular payload and obeys its separately charged cleanup/constant interface; this receipt does not prove a universal physical realization.'],
        source_sha256={str(p.relative_to(REPO)):sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),POOL,HERE/'pool35/IDLE-INVENTORY.json.gz',DRIVER,MACRO)},
        scope='Exact block separation and a conservative fixed coefficient prefix under explicitly retained local-cover/permutation interfaces. Does not justify the older177bit perreplica shortcut, change the paid histogram, or independently admit the all-size supplier.')
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],'prefix882bits;7disjointblocks;2rejectioncontrols')


if __name__=='__main__':main()
