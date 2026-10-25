#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Recompute the seven-block prefix receipt for the complete A/C word change.

This applies the explicit block-separation checker to the new actual IR.
It does not reset the coefficient norm of arbitrary dirty regular helpers.
"""
from argparse import ArgumentParser
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
SCOPE=HERE.parent
CORE=HERE/'block_prefix.py'
WORD=SCOPE/'word-search/candidate/WORD.json.gz'


def need(ok,reason):
    if not ok:raise ValueError(reason)


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,default=HERE/'pool35-word')
    parser.add_argument('--out',type=Path,default=HERE/'BLOCK-PREFIX-REVIEW-WORD.json')
    args=parser.parse_args()
    need(not args.out.exists(),'fresh receipt path required')
    template_path=args.candidate/'GLOBAL-TEMPLATE.json.gz'
    template=read(template_path);candidate=read(args.candidate/'RESULT.json')
    canonical=json.dumps(template,sort_keys=True,separators=(',',':')).encode()
    need(sha256(canonical).hexdigest()==candidate['template_content_sha256'],'changed template source binding')
    word_raw=gzip.decompress(WORD.read_bytes())
    need(sha256(word_raw).hexdigest()==candidate['word_content_sha256']=='3f7de7e1d8a6ff9da8ab7650209b559062da4cc053de2b2566b306eb4fbeffd0','definitive native word content pin')
    new_idles=args.candidate/'IDLE-INVENTORY.json.gz'
    need(read(new_idles)==read(HERE/'pool35/IDLE-INVENTORY.json.gz'),'unchanged complete absolute idle inventory')
    spec=importlib.util.spec_from_file_location('word_block_prefix_core',CORE)
    core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
    forward,cf=core.local_bound(template['local_programs']['forward'])
    backward,cb=core.local_bound(template['local_programs']['reverse'])
    need((forward,backward,cf,cb)==(49347,1113510,9,9),'new actual native IR norms and private cleanup')
    _,bridges,idles,adds=core.block_audit(template)
    per_replica=(1<<18)*forward**5*backward**4
    block=(1<<90)*forward**25*backward**20
    need(block==per_replica**5,'all45 calls and90 bridge layers per five-replica block')
    controls={}
    crossed=deepcopy(template);crossed['calls'][0]['owners'][222][0]+=4440
    try:core.block_audit(crossed)
    except ValueError as exc:controls['cross_block_owner']=str(exc)
    else:raise ValueError('cross-block owner accepted')
    unclosed=list(template['local_programs']['forward'])
    unclosed.pop(max(i for i,e in enumerate(unclosed) if e[0]==3))
    try:core.local_bound(unclosed)
    except ValueError as exc:controls['missing_private_closure']=str(exc)
    else:raise ValueError('unclean private carry accepted')
    paths=[Path(__file__),CORE,template_path,args.candidate/'RESULT.json',new_idles,
           HERE/'pool35/IDLE-INVENTORY.json.gz',WORD,core.DRIVER,core.MACRO,SCOPE/'native-catalogue/adapter.py']
    result=dict(status='PASS_NEW_WORD_SEVEN_PAYLOAD_BLOCKS_AND_CONSERVATIVE_FIVE_REPLICA_PREFIX',
        replicas=35,payload_blocks=7,replicas_per_block=5,families_per_block=4440,
        exact_local_bounds={'forward':forward,'reverse':backward},
        each_block={'forward_calls':25,'reverse_calls':20,'bridge_shear_layers':90},
        total_calls=315,total_bridge_events=bridges,total_bridge_adds=adds,absolute_idle_children=idles,
        private_COPY_ERASE_episodes=315*9,private_regular_payload_carry=False,
        coefficient_prefix_bound=str(block),prefix_bits=block.bit_length(),
        charged_prefix_bits=32*((block.bit_length()+31)//32),
        per_replica_comparison_bits=per_replica.bit_length(),
        fully_sequential_comparison_bits=(per_replica**35).bit_length(),
        controls=controls,template_content_sha256=candidate['template_content_sha256'],
        word_content_sha256=candidate['word_content_sha256'],
        proof='Regular payload families partition by floor(family/4440). All315 calls remain in their own blocks, as do all bridge rows and unary idle/exchange operations. The shared temporary payload is clean on entry and after each of nine COPY/ERASE episodes per call. Therefore the product 2^90 * 49347^25 * 1113510^20 bounds every prefix in one block. No regular dirty-helper norm reset is used. The seven blocks do not read each other; their common bound applies by maximum, not by multiplication.',
        inherited_hypotheses=[
          'The retained packet/source/recursive-D interface implements frame moves and routes as payload permutations of norm1.',
          'The existing local-cover lifting transfers the recomputed local IR norm bound to one native cover sweep, as in the predecessor finite invoice.',
          'Compiler/controller scratch is outside regular payload and obeys its separately charged cleanup and constant interface; this receipt does not prove a universal physical realization.'],
        source_sha256={str(p.relative_to(REPO)):sha256(p.read_bytes()).hexdigest() for p in paths},
        scope='Exact finite block separation and recomputed conservative coefficient prefix for the new actual word, under explicitly retained local-cover/permutation interfaces. The parent complete invoice must charge this bound and its lifted constants. The older per-replica177bit shortcut is not used.')
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'])
    print(json.dumps({k:result[k] for k in ('exact_local_bounds','prefix_bits','charged_prefix_bits','fully_sequential_comparison_bits')},sort_keys=True))


if __name__=='__main__':main()
