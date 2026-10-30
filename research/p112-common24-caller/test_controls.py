#!/usr/bin/env python3
"""Behavioral, mathematical and actual optimized CLI controls; owned copies only.

Chris R / Clear1nsight, substantial OpenAI Codex assistance; Apache-2.0.
"""
import ast
from itertools import combinations_with_replacement, product
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


def rejection(call, message):
    try:
        call()
    except (ValueError,KeyError):
        return
    raise ValueError('failed rejection: '+message)


def run():
    payloads = v.authenticate()
    roots,labels,coords,live = v.m.reconstruct(payloads[v.TABLE],payloads[v.GEOMETRY])
    # Complete generating-subset oracle, independent of any RREF convention.
    oracle = set()
    for word in range(1<<16):
        values = {0}
        for x in range(16):
            if word>>x&1:
                values |= {a^x for a in tuple(values)}
        oracle.add(sum(1<<x for x in values))
    ker = v.m.kernels(list(range(16)),[1<<j for j in range(4)])
    dual = {mask for d in range(5) for mask in v.m.masks(ker,v.m.annihilators(4,d))}
    v.m.require(len(oracle)==67 and oracle==dual, 'complete small-space oracle')
    # Actual original necessary filter, explicitly retained and authenticated.
    source = ast.parse(payloads[v.FILTER])
    nodes = [n for n in source.body if isinstance(n,(ast.ImportFrom,ast.Assign,ast.FunctionDef))]
    namespace = {}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<authenticated PR3154 filter>','exec'),namespace)
    examined,survivors = 0,0
    for n in range(5,12):
        for weights in combinations_with_replacement(range(2,8),n):
            retained = (sum(w-2 for w in weights)<30 and namespace['feasible'](weights,5)
                        and not namespace['killed'](weights,5))
            v.m.require(retained==v.historical(weights,5), 'original filter disagreement')
            examined += 1
            survivors += retained
    v.m.require(survivors==77, 'historical (5,6) count')
    # Independent false-bound-one control from literal receipt.
    receipt = v.load((HERE/'RESULT.json').read_bytes())
    witness = receipt['analysis']['attaining_pair']
    cut = set(witness['cut_labels'])
    normals = [tuple(r) for r in witness['normals']]
    v.m.require(len(cut)==24 and other.determinant([[v.m.dot(a,b) for a in normals] for b in normals])>0,
                'literal independent pair')
    for a in normals:
        remaining = [labels[i] for i,r in enumerate(roots) if live>>i&1
                     and v.m.dot(a,r) and labels[i] not in cut]
        v.m.require(len(v.m.basis(remaining))==7, 'literal residual rank seven')
    # Five independent directions pass separate21 cuts. Exhaust all3^5 common unions.
    flats = list(v.m.masks(v.m.kernels(labels,[1<<j for j in range(9)]),v.m.annihilators(9,7)))
    records,_,_ = v.cut_records(roots,live,flats)
    selected,options = [],[]
    for i,r in enumerate(roots):
        if not live>>i&1:
            continue
        trial = selected+[r]
        gram = [[v.m.dot(a,b) for a in trial] for b in trial]
        if other.determinant(gram)==0:
            continue
        selected.append(r)
        choices = sorted({c for a,_,c in records if a==i and c.bit_count()==21})
        v.m.require(len(choices)==3, 'separate-cut completion options')
        options.append(choices)
        if len(selected)==5:
            break
    minimum = 113
    for chosen in product(*options):
        union = 0
        for c in chosen:
            union |= c
        minimum = min(minimum,union.bit_count())
    v.m.require(len(selected)==5 and minimum>24, 'separate/common quantifier control')
    # Wrong label association is rejected after direct parsing, independent of hashes.
    lines = payloads[v.TABLE].decode().splitlines()
    original = lines[0].split()
    original[0],original[1] = original[1],original[0]
    lines[0] = ' '.join(original)
    rejection(lambda:v.m.reconstruct(('\n'.join(lines)+'\n').encode(),payloads[v.GEOMETRY]),'label association')
    rejection(lambda:v.load('{"x":1,"x":2}'),'duplicate JSON keys')
    # Characteristic zero is a real hypothesis: this nonzero rational word vanishes mod2.
    values = [r[0]+r[1] for i,r in enumerate(roots) if live>>i&1]
    v.m.require(any(values) and all(x%2==0 for x in values), 'characteristic-two boundary')
    # Three actual isolated optimized CLI corruptions, with source-only owned exports.
    for kind in ['source','manifest','Boolean receipt']:
        with tempfile.TemporaryDirectory(prefix='p112-common24-control-') as temporary:
            root = Path(temporary)
            package = root/'research'/HERE.name
            shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__'))
            for owned in package.rglob('*'):
                if owned.is_file():
                    owned.chmod(owned.stat().st_mode | 0o200)
            for row in v.load((HERE/'SOURCES.json').read_bytes())['files']:
                if row['usage']=='input':
                    target = root/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(payloads[row['path']])
            if kind=='source':
                path = root/v.TABLE;path.write_bytes(path.read_bytes()+b'changed\n')
                expected = 'source SHA256'
            elif kind=='manifest':
                path = package/'SOURCES.json';path.write_bytes(path.read_bytes()+b'\n')
                expected = 'source manifest identity'
            else:
                path = package/'RESULT.json'
                data = json.loads(path.read_bytes());data['callers'][0]['strict_excess_deficit']=True
                path.write_text(json.dumps(data))
                expected = 'result receipt mismatch'
            completed = subprocess.run([sys.executable,'-I','-O','-Werror','-B',str(package/'verify.py')],
                                       cwd=root,capture_output=True,text=True,timeout=180)
            v.m.require(completed.returncode!=0 and expected in completed.stderr,
                        'optimized CLI did not reject '+kind)
    print(f'PASS_COMMON24_CONTROLS spaces4=67 original_multisets={examined} survivors=77 '
          f'separate21_minimum_common={minimum} semantic_rejections=2 CLI_rejections=3')


if __name__=='__main__':
    v.m.require(not sys.argv[1:], 'no arguments accepted')
    run()
