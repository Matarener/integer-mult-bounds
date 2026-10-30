"""Behavioral rejection controls; no upstream files are mutated."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import phase_gram as M
import query_frame_sources as S
import verify as V
import independent_frames as I


def reject(operation):
    try:operation()
    except ValueError:return
    raise ValueError('negative control accepted')


def main():
    L,(P,R,routes,labels,_),_=S.loaded()
    expected=V.read_json(HERE/'CERTIFICATE.json')
    actual=M.certificate(L,P,R,routes,labels)
    controls=[]
    swapped={**routes,1:routes[2],2:routes[1]}
    reject(lambda:M.certificate(L,P,R,swapped,labels));controls.append('reverse ordered route composition')
    normals=list(labels);normals[P.U[0]]^=1
    reject(lambda:M.certificate(L,P,R,routes,normals));controls.append('wrong source normal')
    shorter=SimpleNamespace(**P.__dict__);shorter.U=P.U[:-1]
    reject(lambda:M.certificate(L,shorter,R,routes,labels));controls.append('missing nonzero source branch')
    original=M.outer
    def no_diagonal(q,n):
        return tuple(row&~(1<<i) for i,row in enumerate(original(q,n)))
    with patch.object(M,'outer',no_diagonal):
        reject(lambda:M.certificate(L,P,R,routes,labels))
    controls.append('omit binary polar diagonal')
    partition=V.read_json(HERE/'PARTITION.json')
    duplicated=deepcopy(partition);duplicated['groups'][0][0]=duplicated['groups'][1][0]
    reject(lambda:M.lifted_bound(actual,duplicated));controls.append('duplicate partition member')
    broken=deepcopy(partition)
    found=False
    directions={r[0]:r[2] for r in actual['records']}
    for j in range(1,len(broken['groups'])):
        for a in range(len(broken['groups'][0])):
            for b in range(len(broken['groups'][j])):
                candidate=deepcopy(partition);g=candidate['groups']
                g[0][a],g[j][b]=g[j][b],g[0][a]
                if any(M.rank(directions[p] for p in row)<len(row) for row in (g[0],g[j])):
                    broken=candidate;found=True;break
            if found:break
        if found:break
    S.need(found,'available dependent-group control')
    reject(lambda:M.lifted_bound(actual,broken));controls.append('dependent group with valid coverage')
    extra=deepcopy(partition);extra['groups'].append([extra['groups'][0].pop()])
    reject(lambda:M.lifted_bound(actual,extra));controls.append('nonoptimal partition certificate')
    result=V.compute()
    for label,mutate in (
        ('one changed cancellation direction',lambda x:x['records'][0].__setitem__(2,x['records'][0][2]^1)),
        ('bool masquerading as an integer',lambda x:x.__setitem__('max_cancellation_fiber',True)),
        ('float masquerading as an integer',lambda x:x.__setitem__('dimension',73.0)),
        ('wrong normalization allowance',lambda x:x['bill'].__setitem__('baseline_phase_moment',103)),
        ('omitted canonical source pin',lambda x:x['source_pins'].pop(next(iter(x['source_pins'])))),
    ):
        bad=deepcopy(result);mutate(bad);reject(lambda:V.validate(bad,expected));controls.append(label)
    bad=deepcopy(expected);bad['records'][0][3]^=1
    reject(lambda:I.check(bad));controls.append('independent character image mismatch')
    with tempfile.TemporaryDirectory(prefix='query-frame-source-control-') as folder:
        first=next(r for r in json.loads((HERE/'SOURCES.json').read_text())['files'] if r['usage']=='input')
        path=Path(folder)/first['path'];path.parent.mkdir(parents=True)
        body=(S.ROOT/first['path']).read_bytes();path.write_bytes(body[:-1]+bytes([body[-1]^1]))
        with patch.object(S,'ROOT',Path(folder)):
            reject(S.loaded)
    controls.append('corrupt source rejected before inherited execution')
    with tempfile.TemporaryDirectory(prefix='query-frame-manifest-control-') as folder:
        manifest=json.loads((HERE/'SOURCES.json').read_text());manifest['files'].pop()
        (Path(folder)/'SOURCES.json').write_text(json.dumps(manifest))
        with patch.object(S,'HERE',Path(folder)):
            reject(S.loaded)
    controls.append('weakened source manifest rejected before execution')
    with tempfile.TemporaryDirectory(prefix='query-frame-receipt-control-') as folder:
        p=Path(folder)/'duplicate.json';p.write_text('{"x":1,"x":2}')
        reject(lambda:V.read_json(p))
    controls.append('duplicate certificate keys')
    print('PASS_QQ16_COMMON_FRAME_CONTROLS '+json.dumps({'controls':len(controls),'cases':controls},sort_keys=True))


if __name__=='__main__':main()
