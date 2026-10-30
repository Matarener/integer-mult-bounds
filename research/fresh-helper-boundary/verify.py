"""Replay the changed native unit and its conditional multiplication endpoint.

Standard library only. Apache-2.0; substantial OpenAI Codex assistance.
"""
import argparse
import gzip
from copy import deepcopy
from hashlib import sha256, sha1
import json
from pathlib import Path
import native
import arithmetic

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, why):
    if not ok:
        raise ValueError(why)

def authenticate():
    manifest = native.read(HERE/'SOURCES.json')
    seen = set()
    for row in manifest['files']:
        if row['usage'] != 'input':
            continue
        path = Path(row['path'])
        need(not path.is_absolute() and '..' not in path.parts and str(path) not in seen, 'Canonical unique input')
        seen.add(str(path))
        actual = ROOT
        for part in path.parts:
            actual /= part
            need(not actual.is_symlink(), 'No source alias')
        data = actual.read_bytes()
        need(sha256(data).hexdigest() == row['sha256'], 'Changed source: '+str(path))
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == row['git_blob'], 'Changed source Git blob')
    return len(seen)

def controls(result, c, programs):
    # This is a literal original-word control, not a second mathematical review.
    baseline, _, _ = native.run({'entrances':[], 'exits':[], 'gates':[]}, phase_check=False)
    need(baseline['helpers'] == {5:28,6:18,7:56,8:93,9:213}, 'Recover the actual predecessor helper profile')
    need(baseline['paid'] == {1:2487,2:713,3:224,4:102,5:20,8:8}, 'Recover the actual predecessor paid profile')
    V = native.load(ROOT/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py','boundary_control_rows')
    rebound = deepcopy(c); rebound['local_profile'] = result['paid']
    bad = deepcopy(programs['forward'])
    bad.pop(next(i for i, e in enumerate(bad) if e[0] == 'center'))
    rejected = False
    try:
        V.replay(bad, rebound, [], False, False)
    except (ValueError, AssertionError):
        rejected = True
    need(rejected, 'A missing paid center is rejected at the actual frame contact')
    # A pure global-phase corruption has an unchanged Pauli tableau.
    ce = native.load(ROOT/'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py','boundary_control_phase')
    P = native.load(ROOT/'research/kappa-function-composition/complex/prune_native.py','boundary_control_decode')
    row = result['new_physical_edges_and_boundaries'][0]
    rec = deepcopy(row['recipes']['forward'])
    def decode(r):
        left = P.monomial(ce, r['left'],9)
        if r['rank']:
            return P.monomial(ce,r['right'],9).then(ce.fourier(9,range(r['rank']))).then(left)
        return left
    original = decode(rec)
    rec['left']['phase'] = (rec['left']['phase']+1)%4
    changed = decode(rec)
    need(changed.tab == original.tab and changed.zero_state() != original.zero_state(), 'Absolute phase corruption is detected beyond tableau equality')
    return {'predecessor_recovered':True,'omitted_center_rejected':True,'global_phase_only_corruption_rejected':True}

def verify(write=False):
    count = authenticate()
    result, c, programs = native.run()
    math = arithmetic.run(result)
    checks = controls(result,c,programs)
    artifacts = {'NATIVE-RESULT.json.gz': result, 'ARITHMETIC-RESULT.json': math}
    for name, value in artifacts.items():
        normalized = json.loads(json.dumps(value))
        if write:
            data = (json.dumps(normalized,indent=2,sort_keys=True)+'\n').encode()
            (HERE/name).write_bytes(gzip.compress(data,mtime=0) if name.endswith('.gz') else data)
        else:
            need(normalized == native.read(HERE/name), 'Exact receipt replay: '+name)
    receipt = {'status':'PASS_FRESH_HELPER_BOUNDARY_CONDITIONAL_KAPPA',
               'kappa_decimal':'0.00272124', 'source_inputs':count,
               'physical_edges_and_boundaries':len(result['new_physical_edges_and_boundaries']),
               'changed_entrances':result['changed_entrances'], 'changed_exits':result['changed_exits'],
               'changed_scalar_frames':result['changed_scalar_frames'],
               'controls':checks, 'scientific_receipts':{name:sha256(gzip.decompress((HERE/name).read_bytes()) if name.endswith('.gz') else (HERE/name).read_bytes()).hexdigest() for name in artifacts}}
    if write:
        (HERE/'RESULT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    else:
        need(receipt == native.read(HERE/'RESULT.json'), 'Final checked receipt')
    return receipt

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-receipts', action='store_true', help='Author receipts explicitly; ordinary replay does not write.')
    args = parser.parse_args()
    print(json.dumps(verify(args.write_receipts),sort_keys=True))
