"""Check the complete conditional P104 improvement and its immutable evidence.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from copy import deepcopy
from hashlib import sha1,sha256
import gzip
import json
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import local as L
import caller as C
import price as P


def authenticate():
    count=0
    for row in L.read(L.HERE/'SOURCES.json')['files']:
        if row['usage'] == 'input':
            raw=(L.ROOT/row['path']).read_bytes()
            L.need(sha256(raw).hexdigest() == row['sha256'], 'Changed source: '+row['path'])
            L.need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], 'Source Git object')
            count+=1
    return count


def rejected(action,label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('Control accepted: '+label)


def run():
    pins=authenticate()
    word=L.construct()
    local=L.replay(word)
    columns=L.reverse_columns(word)
    print('PASS complete source rows, reverse integer columns and owned lifetimes',flush=True)
    native=L.native(word)
    print('PASS every native paid map, productive helper and main adapter',flush=True)
    controller=C.construct()
    physical=C.physical(controller,word)
    costs=P.run(local,native,controller,physical)
    controls=C.controls(controller)
    bad=deepcopy(word)
    bad['program'].remove(next(e for e in bad['program'] if e[0] == 'COPY'))
    controls['omitted_copy']=rejected(lambda:L.replay(bad),'Rejected by full arbitrary-input endpoint')
    bad=deepcopy(word)
    e=next(e for e in bad['program'] if e[0] == 'MOVE')
    e[2]=e[3]
    controls['wrong_frame']=rejected(lambda:L.replay(bad),'Rejected by literal source-frame check')
    bad=deepcopy(local)
    bad['helpers'][9]+=1
    controls['unearned_helper']=rejected(lambda:P.assemble(bad,native,controller,physical),'Rejected by native helper census')
    result={'status':'PASS_P104_PRODUCTIVE_COMPLETE_KAPPA_00304057','source_inputs_authenticated':pins,
            'local':local,'separate_columns':columns,'native':native,'physical_caller':physical,
            'complete_cost':costs,'negative_controls':controls,
            'limits':['Conditional on the retained native all-column, owned-erasure, compiler, precision/tape and analytic-recovery framework.',
                      'The winning uniform compiler word and complete integer multiplier are not materialized.',
                      'No proof-kernel check or independent human review is claimed.']}
    return P.encode(result),word,controller


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    result,word,controller=run()
    for name,data in [('RESULT.json',result),('WORD.json.gz',word),('CONTROLLER.json',controller)]:
        path=L.HERE/name
        if args.write:
            raw=(json.dumps(data,indent=None if name.endswith('.gz') else 2,sort_keys=True)+'\n').encode()
            path.write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)
        else:
            L.need(L.read(path) == data,'Exact frozen artifact: '+name)
    print(result['status'])
    print(json.dumps({k:result['complete_cost'][k] for k in ('kappa','gain','raw_root_interval','productive_fields','paid_calls')},sort_keys=True))


if __name__ == '__main__':
    main()
