#!/usr/bin/env python3
"""Small exhaustive graph oracle, literal witnesses, and optimized CLI failures.
Chris R / Clear1nsight with substantial OpenAI Codex assistance; Apache-2.0.
"""
from itertools import combinations
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import verify as v
import independent as other


def rejected(call,message):
    try:
        call()
    except ValueError:
        return
    raise ValueError('missing rejection: '+message)


def run():
    payloads = v.authenticate()
    roots,labels,coords,live = v.m.reconstruct(payloads[v.TABLE],payloads[v.GEOMETRY])
    result = v.load((HERE/'RESULT.json').read_bytes())
    witness = result['attaining_triple']
    cut = set(witness['cut_labels'])
    normals = witness['normals']
    gram = [[v.m.dot(a,b) for b in normals] for a in normals]
    v.m.require(len(cut)==30 and other.determinant(gram)>0, 'literal independent triple')
    for h in normals:
        residual = [labels[i] for i,r in enumerate(roots) if live>>i&1 and labels[i] not in cut and v.m.dot(r,h)]
        v.m.require(len(v.m.basis(residual))==7, 'literal triple residual ranks')
    # Every graph on five directions in a rank-three rational space. Compare
    # DFS against direct subsets having independent proper prefixes.
    vectors = [(1,0,0,0,0,0,0,0),(0,1,0,0,0,0,0,0),(1,1,0,0,0,0,0,0),
               (0,0,1,0,0,0,0,0),(1,0,1,0,0,0,0,0)]
    pairs = list(combinations(range(5),2)); checked = 0
    for bits in range(1<<len(pairs)):
        adjacent = [set() for _ in vectors]
        for bit,(i,j) in enumerate(pairs):
            if bits>>bit&1:adjacent[i].add(j);adjacent[j].add(i)
        oracle = {}
        for n in range(1,6):
            for chosen in combinations(range(5),n):
                if not all(j in adjacent[i] for i,j in combinations(chosen,2)):
                    continue
                if n>1 and v.rank_q([vectors[i] for i in chosen[:-1]])<n-1:
                    continue
                key=(n,30,v.rank_q([vectors[i] for i in chosen]))
                oracle[key]=oracle.get(key,0)+1
        maximum=max(k[2] for k in oracle)
        if maximum!=3:
            continue
        counts,_ = v.independent_prefixes(vectors,[(i,(1<<30)-1) for i in range(5)],adjacent)
        v.m.require(dict(counts)==oracle, 'complete small graph oracle')
        checked+=1
    # A genuine fourth independent direction must trip the bound, even though
    # the same routine deliberately prunes dependent triples.
    four = [tuple(int(i==j) for j in range(8)) for i in range(4)]
    rejected(lambda:v.independent_prefixes(four,[(i,(1<<30)-1) for i in range(4)],
             [set(range(4))-{i} for i in range(4)]),'independent fourth normal')
    rejected(lambda:v.load('{"x":1,"x":2}'),'duplicate JSON key')
    values=[r[0]+r[1] for i,r in enumerate(roots) if live>>i&1]
    v.m.require(any(values) and all(x%2==0 for x in values),'characteristic-two boundary')
    for kind in ['source','manifest']:
        with tempfile.TemporaryDirectory(prefix='p112-common30-control-') as temporary:
            root=Path(temporary);package=root/'research'/HERE.name
            shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__'))
            for owned in package.rglob('*'):
                if owned.is_file():owned.chmod(owned.stat().st_mode|0o200)
            for row in v.load((HERE/'SOURCES.json').read_bytes())['files']:
                if row['usage']=='input':
                    target=root/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(payloads[row['path']])
            if kind=='source':
                target=root/v.TABLE; expected='source SHA256'
            else:
                target=package/'SOURCES.json'; expected='source manifest identity'
            target.write_bytes(target.read_bytes()+b'\n')
            done=subprocess.run([sys.executable,'-I','-O','-Werror','-B',str(package/'verify.py')],
                                cwd=root,capture_output=True,text=True,timeout=30)
            v.m.require(done.returncode!=0 and expected in done.stderr,'actual optimized CLI '+kind)
    print(f'PASS_COMMON30_CONTROLS graph_oracles={checked} literal_rank3=1 fourth_rank_rejection=1 optimized_CLI_rejections=2')


if __name__=='__main__':
    v.m.require(not sys.argv[1:],'no arguments accepted')
    run()
