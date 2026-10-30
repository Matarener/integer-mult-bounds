# SPDX-License-Identifier: Apache-2.0
from fractions import Fraction as F
from pathlib import Path
from itertools import permutations
import tempfile,shutil,subprocess,sys,json
from cache import *
from fixtures import source_fixture,cyclic_fixture
from reference import inverse as oracle_inverse,determinant
ROOT=Path(__file__).resolve().parent

def reject(fn):
    try:fn()
    except (ValueError,ZeroDivisionError):return
    raise RuntimeError('invalid operation accepted')

def main():
    H=source_fixture();checks=0
    # All label permutations, both orientations, and a nonconstant incoming diagonal.
    for labels in permutations(range(3),2):
        incoming=next(i for i in range(3) if i not in labels)
        for method in ('schur','woodbury'):
            cache=WindowCache(H,labels);cache.slide(incoming,method=method)
            A=principal(H,cache.labels);Q=cache.inverse
            need(Q==tuple(map(tuple,oracle_inverse(A))),'permuted source order')
            det=determinant(A)
            for i in range(2):
                for j in range(2):
                    cofactor=(-1)**(i+j)*determinant([[A[r][c] for c in range(2) if c!=i] for r in range(2) if r!=j])
                    need(Q[i][j]==cofactor/det,'separate cofactor identity')
            checks+=1
    cache=WindowCache(H,[0,1]);saved=cache.inverse,cache.labels
    reject(lambda:cache.slide(2,'wrong-source'))
    need((cache.inverse,cache.labels)==saved,'rejected source preserves checkpoint')
    reject(lambda:cache.slide(1));reject(lambda:cache.slide(-1));reject(lambda:cache.slide(2,method='other'))
    reject(lambda:WindowCache(H,[0,0]));reject(lambda:WindowCache([[1,2],[2,1]],[0,1]))
    reject(lambda:WindowCache(H,[0,1],[1,0,1]));reject(lambda:residual_certificate(H,[0,1],[1,1,1],[[0,0],[0,0]]))
    # Omitting diagonal overlap correction is a real semantic error on the upstream fixture.
    old=principal(H,[1,0]);new=principal(H,[1,2]);delta=[[new[i][j]-old[i][j] for j in range(2)] for i in range(2)]
    naive=[[delta[i][1]*F(j==1)+F(i==1)*delta[1][j] for j in range(2)] for i in range(2)]
    need(naive!=delta and delta[1][1]!=0,'double-counted diagonal mutant exposed')
    # Do not replace the old nonsymmetric global model by a transposed or dense local model.
    wrong=[list(r) for r in zip(*H)]
    need(oracle_inverse(principal(wrong,[0,1]))!=oracle_inverse(principal(H,[0,1])),'wrong old-H model exposed')
    # Arbitrary dirty exterior is preserved by injective finite output ports.
    memory={i:('dirty',i,i*i) for i in range(-8,25)};ports=[2,7]
    value=publish_owned(memory,ports,[F(5),F(-2)])
    need(all(value[i]==memory[i] for i in memory if i not in ports),'exterior frame')
    need(memory[2]==('dirty',2,4),'input memory immutable')
    reject(lambda:publish_owned(memory,[2,2],[1,2]))
    cache=WindowCache(H,[0,1]);memory[2]=F(3);memory[7]=F(-4)
    once=apply_owned(cache,memory,ports);twice=apply_owned(cache,once,ports)
    vector=cache.apply(cache.apply([memory[i] for i in ports]))
    need([twice[i] for i in ports]==list(vector),'fixed-port word embedding')
    need(all(twice[i]==memory[i] for i in memory if i not in ports),'word exterior frame')
    # Correlated blocks have no statistical-independence premise.
    blocks=[(cache,[F(3),F(-4)]),(cache,[F(6),F(-8)])]
    before=after=F(0);factor=F(0)
    for item,vector in blocks:
        depth,bound=block_energy_factor(len(item.labels),item.gap);factor=max(factor,bound)
        before+=sum(v*v for v in vector);after+=sum(v*v for v in item.apply(vector))
    need(after<=factor*before,'direct-sum block energy bound')
    # Tensor flattening is a permutation, so correlated squared energy is invariant.
    tensor=[[[F(i+2*j-3*k) for k in range(3)] for j in range(2)] for i in range(2)]
    first=[tensor[i][j][k] for i in range(2) for j in range(2) for k in range(3)]
    second=[tensor[i][j][k] for k in range(3) for i in range(2) for j in range(2)]
    need(sum(v*v for v in first)==sum(v*v for v in second),'pack norm and frame invariance')
    reject(lambda:recover_known_integer([F(1,2)],F(1,2)))
    reject(lambda:recover_known_integer([F(0)],F(-1)))
    # Actual export/CLI must reject changed immutable sources and changed claims.
    with tempfile.TemporaryDirectory() as temporary:
        target=Path(temporary)/'package';shutil.copytree(ROOT,target,ignore=shutil.ignore_patterns('__pycache__'))
        command=[sys.executable,'-B',str(target/'verify.py')]
        need(subprocess.run(command,capture_output=True,timeout=60).returncode==0,'export positive')
        file=target/'inputs/gaussian_check_setup.py';raw=file.read_bytes();file.write_bytes(raw+b' ')
        need(subprocess.run(command,capture_output=True,timeout=60).returncode!=0,'source drift accepted');file.write_bytes(raw)
        file=target/'RESULT.json';data=json.loads(file.read_text());data['slides']+=1;file.write_text(json.dumps(data))
        need(subprocess.run(command,capture_output=True,timeout=60).returncode!=0,'false receipt accepted')
    print('PASS_WINDOW_CONTROLS',checks,'permuted independent/cofactor cases; source, alias, residual, diagonal, model, exterior, tensor and CLI controls')
if __name__=='__main__':main()
