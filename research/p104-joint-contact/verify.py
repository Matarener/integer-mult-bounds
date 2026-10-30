"""Complete conditional P104 successor; the selected record is not changed.

Prepared for thu-nmrc with substantial OpenAI Codex assistance. Apache-2.0.
Predecessor construction, native, caller, interval and outer proofs retain credit.
"""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import gzip,json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import supplier,need
import construct

def rejected(fn):
    try:
        fn()
    except ValueError as error:
        return str(error)
    raise ValueError('Semantic mutant was accepted')

def run():
    with supplier()as(root,L,C,R):
        P=L.load(HERE/'pricing.py','p104_joint_pricing')
        base=L.construct()
        need(base==L.read(root/'research/p104-productive-controller/WORD.json.gz'),'Reconstructed full credited source')
        source=R.construct(base)
        need(source==L.read(root/'research/p104-full-frame-contact/WORD.json.gz'),'Reconstructed exact PR5545 source')
        baseline=L.replay(source)
        word=construct.construct(source)
        local=L.replay(word);columns=L.reverse_columns(word)
        need(local['helpers']==baseline['helpers'],'All 527 productive helper targets retained')
        delta=Counter(local['paid']);delta.subtract(baseline['paid'])
        delta={r:n for r,n in delta.items()if n}
        need(delta=={1:2,2:-3,3:1,4:-1,5:1},'Exact coupled contact invoice')
        need(sum(delta.values())==sum(r*n for r,n in delta.items())==0,'Call count and rank mass retained')
        peer=L.load(HERE/'peer/check.py','p104_joint_independent_peer')
        peer_result=json.loads(json.dumps(peer.calculate(),sort_keys=True))
        need(peer_result==L.read(HERE/'peer/RECEIPT.json'),'Independent exact scalar/frame receipt')
        need(peer.read('SOURCE-WORD.json.gz')==source and peer.read('CANDIDATE-WORD.json.gz')==word,'Independent checker audits this exact pair of words')
        print('PASS source reconstruction, all743 rows, reverse columns, independent integer peer and both coupled invoices',flush=True)
        native=L.native(word)
        controller=C.construct()
        need(controller==L.read(root/'research/p104-productive-controller/CONTROLLER.json'),'Exact complete caller')
        physical=C.physical(controller,word)
        print('PASS every native map and phase, all527 helpers, all104 ports and complete265-axis caller',flush=True)
        costs=P.run(local,native,controller,physical)
        controls=C.controls(controller)
        bad=deepcopy(word)
        event=next(e for e in bad['program']if e==['ADD',297,303,'1',17]);event[-1]=335
        controls['one_operand_or_contact_left_at_old_chart']=rejected(lambda:L.replay(bad))
        bad=deepcopy(word)
        event=next(e for e in bad['program']if e==['ADD',297,303,'1',17]);event[3]='2'
        controls['wrong_butterfly_coefficient']=rejected(lambda:L.replay(bad))
        bad=deepcopy(local);bad['paid'][1]-=1
        controls['uncharged_recursive_call']=rejected(lambda:P.assemble(bad,native,controller,physical))
        bad=deepcopy(source);bad['program'][10461][3]='2'
        controls['stale_source_or_changed_read']=rejected(lambda:construct.construct(bad))
        result={'status':'PASS_P104_JOINT_CONTACT_COMPLETE_KAPPA_00304153',
                'source_commit':'18968423711fd902aaee1099979497d55603e1dc',
                'retained_source_files':33,'local_paid_delta':delta,
                'complete_paid_delta':{r:18*n for r,n in delta.items()},
                'local':local,'separate_columns':columns,'native':native,
                'independent_peer_science_sha256':sha256(json.dumps(peer_result,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                'physical_caller':physical,'complete_cost':costs,'negative_controls':controls,
                'limits':['The five framework assumptions retained by PR5544/5545 remain.',
                          'The uniform compiler word and complete rounded multiplier are not materialized.',
                          'No independent human or proof-kernel acceptance, selected promotion, or core-contributor status is claimed.']}
        return P.encode(result),word

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result,word=run()
    for name,data in [('RESULT.json',result),('WORD.json.gz',word)]:
        path=HERE/name
        if args.write:
            raw=(json.dumps(data,sort_keys=True,indent=None if name.endswith('.gz')else 2)+'\n').encode()
            path.write_bytes(gzip.compress(raw,mtime=0)if name.endswith('.gz')else raw)
        else:
            raw=path.read_bytes()
            need(json.loads(gzip.decompress(raw)if name.endswith('.gz')else raw)==data,'Saved semantic artifact '+name)
    print(result['status'],flush=True)
    print(json.dumps({k:result['complete_cost'][k]for k in ('kappa','gain','raw_root_interval','productive_fields','paid_calls')},sort_keys=True),flush=True)

if __name__=='__main__':
    main()
