#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Assemble component invoices with exact coverage of a pinned source inventory.

Source bytes are authenticated; semantic completeness remains a declaration.
Retain signed-invoice and source-extractor credits. Ali Romman with OpenAI Codex.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
try:
    from compare_recursive_invoices import validate_invoice,require,MAX_COUNT,_pairs,_integer,_not_integer
finally:
    sys.path.pop(0)


def empty(contract):
    return {'schema':'integer-mult-recursive-invoice/v1','contract':contract,'paid':{},'targets':{}}


def validate_inventory(inventory):
    require(type(inventory) is dict and inventory.keys()=={'schema','contract','sources','items'} and
            inventory['schema']=='integer-mult-invoice-inventory/v1','invalid inventory schema')
    contract=validate_invoice(empty(inventory['contract']))['contract']
    sources=inventory['sources'];items=inventory['items'];by_id={};used=set()
    require(type(sources) is dict and len(sources)<=16,'at most 16 pinned sources')
    for name,digest in sources.items():
        require(type(name) is str and 0<len(name)<=128 and type(digest) is str and
                re.fullmatch('[0-9a-f]{64}',digest) is not None,'invalid source name or SHA-256')
    require(type(items) is list and len(items)<=16384,'at most 16384 inventory items')
    for row in items:
        require(type(row) is dict and row.keys()=={'id','source','side','rank','count'},'invalid inventory item')
        name,source,side,rank,count=(row[k] for k in ('id','source','side','rank','count'))
        require(type(name) is str and 0<len(name)<=256 and name not in by_id,'inventory IDs must be unique')
        require(type(source) is str and source in sources,'unknown item source')
        require(type(side) is str and side in ('paid','targets'),'invalid inventory side')
        require(type(rank) is int and 1<=rank<=contract['ambient_rank'],'invalid inventory rank')
        require(type(count) is int and 1<=count<=MAX_COUNT,'invalid inventory count')
        by_id[name]=row;used.add(source)
    require(used==sources.keys(),'unused pinned source')
    return contract,sources,by_id


def assemble(inventory,assignment):
    contract,sources,items=validate_inventory(inventory)
    require(type(assignment) is dict and assignment.keys()=={'schema','components'} and
            assignment['schema']=='integer-mult-invoice-assignment/v1','invalid assignment schema')
    components=assignment['components']
    require(type(components) is dict and 1<=len(components)<=128,'provide 1..128 components')
    consumed={name:0 for name in items};bills={};total=empty(contract);entries=0
    for name,claims in components.items():
        require(type(name) is str and 0<len(name)<=128 and type(claims) is list,'invalid component')
        entries+=len(claims);require(entries<=65536,'at most 65536 assignments')
        bill=empty(contract);seen=set()
        for claim in claims:
            require(type(claim) is dict and claim.keys()=={'id','count'},'invalid item assignment')
            item_id,count=claim['id'],claim['count']
            require(type(item_id) is str and item_id in items and item_id not in seen,'unknown or repeated component item')
            require(type(count) is int and 1<=count<=MAX_COUNT,'invalid assigned count')
            seen.add(item_id);consumed[item_id]+=count
            require(consumed[item_id]<=items[item_id]['count'],'over-assigned inventory item: '+item_id)
            row=items[item_id];side,rank=row['side'],str(row['rank'])
            bill[side][rank]=bill[side].get(rank,0)+count
            total[side][rank]=total[side].get(rank,0)+count
        bills[name]=validate_invoice(bill,'component '+name)
    for name,row in items.items():require(consumed[name]==row['count'],'unassigned inventory item: '+name)
    total=validate_invoice(total,'complete invoice')
    receipt={'schema':'integer-mult-invoice-assembly-receipt/v1','covered_items':len(items),
             'covered_paid_count':sum(total['paid'].values()),'covered_target_count':sum(total['targets'].values()),
             'components':bills,'assignments':entries,
             'scope':'Exact conservation of the declared inventory identities and counts. '
                     'File hashes authenticate bytes only. Physical source completeness, '
                     'correct ranks, independent targets and kappa admission are not proved.'}
    return total,receipt


def source_receipts(inventory,bindings):
    contract,expected,items=validate_inventory(inventory)
    paths={}
    for name,path in bindings:
        require(name not in paths,'duplicate source binding');paths[name]=path
    require(paths.keys()==expected.keys(),'source bindings differ from the pinned inventory')
    result={}
    for name,path in paths.items():
        digest=sha256();size=0
        with Path(path).open('rb') as stream:
            while block:=stream.read(65536):
                size+=len(block);require(size<=64*1024*1024,'source exceeds 64 MiB')
                digest.update(block)
        require(digest.hexdigest()==expected[name],'source hash differs: '+name)
        result[name]={'path':str(path),'bytes':size,'sha256':digest.hexdigest()}
    return result


def load(path):
    with Path(path).open('rb') as stream:raw=stream.read(8*1024*1024+1)
    require(len(raw)<=8*1024*1024,'input exceeds 8 MiB')
    value=json.loads(raw.decode('utf-8'),object_pairs_hook=_pairs,parse_int=_integer,
                     parse_float=_not_integer,parse_constant=_not_integer)
    return value,{'path':str(path),'bytes':len(raw),'sha256':sha256(raw).hexdigest()}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inventory');parser.add_argument('assignment')
    parser.add_argument('--source',nargs=2,action='append',default=[],metavar=('NAME','FILE'))
    args=parser.parse_args(argv)
    try:
        inventory,a=load(args.inventory);assignment,b=load(args.assignment)
        invoice,receipt=assemble(inventory,assignment)
        receipt['sources']=source_receipts(inventory,args.source)
        raw=(json.dumps(invoice,indent=2,sort_keys=True)+'\n').encode('utf-8')
        receipt['inputs']={'inventory':a,'assignment':b}
        receipt['output']={'bytes':len(raw),'sha256':sha256(raw).hexdigest()}
    except (OSError,ValueError,TypeError,RecursionError) as exc:
        print(json.dumps({'status':'INVALID_INVOICE_ASSEMBLY','error':str(exc)}),file=sys.stderr);return 2
    sys.stdout.buffer.write(raw)
    print(json.dumps(receipt,indent=2,sort_keys=True),file=sys.stderr);return 0


if __name__=='__main__':raise SystemExit(main())
