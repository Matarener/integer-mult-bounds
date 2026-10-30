"""Check the contact, complete native caller and conditional kappa gain.

Source interpreters and caller are immutable PR5544 dependencies.
Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha1, sha256
import gzip
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT/'research/p104-productive-controller'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate():
    rows = json.loads((HERE/'SOURCES.json').read_bytes())['files']
    count = 0
    for row in rows:
        if row['usage'] == 'input':
            raw = (ROOT/row['path']).read_bytes()
            need(sha256(raw).hexdigest() == row['sha256'], 'Changed source: '+row['path'])
            need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'],
                 'Source Git object: '+row['path'])
            count += 1
    return count


def rejected(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('A semantic control was accepted')


def run():
    pins = authenticate()
    sys.path[:0] = [str(HERE),str(SOURCE)]
    import local as L
    import caller as C
    import construct as R
    import pricing as P
    source = L.construct()
    need(source == L.read(SOURCE/'WORD.json.gz'), 'Exact reconstructed PR5544 source')
    baseline = L.replay(source)
    word = R.construct(source)
    local = L.replay(word)
    columns = L.reverse_columns(word)
    need(local['helpers'] == baseline['helpers'], 'All helper targets retained')
    delta = Counter(local['paid'])
    delta.subtract(baseline['paid'])
    need({r:n for r,n in delta.items() if n} == {1:-1,5:-1,6:1}, 'Exact local paid delta')
    print('PASS source, scalar endpoint, dense reverse columns and H1+H5 to H6',flush=True)
    native = L.native(word)
    controller = C.construct()
    need(controller == L.read(SOURCE/'CONTROLLER.json'), 'Same literal caller')
    physical = C.physical(controller,word)
    print('PASS every native map, all productive targets and physical caller',flush=True)
    costs = P.run(local,native,controller,physical)
    controls = C.controls(controller)
    bad = deepcopy(word)
    event = next(e for e in bad['program'] if e == ['MOVE',345,739,127,False])
    event[3] = 240
    controls['one_operand_only'] = rejected(lambda:L.replay(bad))
    bad = deepcopy(word)
    event = next(e for e in bad['program'] if e == ['ADD',341,345,'-1',127])
    event[3] = '1'
    controls['wrong_contact_sign'] = rejected(lambda:L.replay(bad))
    bad = deepcopy(source)
    bad['program'][16801] = ['ADD',400,341,'1',240]
    controls['intervening_source_read'] = rejected(lambda:R.construct(bad))
    bad = deepcopy(local)
    bad['paid'][1] -= 1
    controls['uncharged_call'] = rejected(lambda:P.assemble(bad,native,controller,physical))
    result = {'status':'PASS_P104_CONTACT_COMPLETE_KAPPA_00304117',
              'source_inputs_authenticated':pins,'local_paid_delta':{1:-1,5:-1,6:1},
              'complete_paid_delta':{1:-18,5:-18,6:18},
              'local':local,'separate_columns':columns,'native':native,
              'physical_caller':physical,'complete_cost':costs,'negative_controls':controls,
              'limits':['The five framework assumptions of PR5544 remain.',
                        'The uniform compiler word and complete rounded multiplier are not materialized.',
                        'No independent human or proof-kernel acceptance is claimed.']}
    return P.encode(result),word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    result,word = run()
    for name,data in (('RESULT.json',result),('WORD.json.gz',word)):
        path = HERE/name
        if args.write:
            raw = (json.dumps(data,sort_keys=True,indent=None if name.endswith('.gz') else 2)+'\n').encode()
            path.write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)
        else:
            raw = path.read_bytes()
            need(json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw) == data,
                 'Exact saved artifact: '+name)
    print(result['status'])
    print(json.dumps({k:result['complete_cost'][k] for k in
                      ('kappa','gain','raw_root_interval','productive_fields','paid_calls')},sort_keys=True))


if __name__ == '__main__':
    main()
