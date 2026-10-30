#!/usr/bin/env python3
"""Run the complete frozen contract through a declared exact backend."""
from contextlib import contextmanager
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
import sys
import tarfile
import tempfile
import time

P=Path(__file__).resolve().parent


def need(ok,message):
    if not ok: raise ValueError(message)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value);return value


def authenticate():
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':need(sha256((P.parent.parent/row['path']).read_bytes()).hexdigest()==row['sha256'],'source hash')


@contextmanager
def source():
    authenticate()
    with tempfile.TemporaryDirectory(prefix='p104-integer-error-') as tmp:
        root=Path(tmp)
        with tarfile.open(P/'inputs/source.tar') as archive:
            need(all(x.isfile() and not x.name.startswith('/') and '..' not in Path(x.name).parts for x in archive),'regular source archive')
            archive.extractall(root,filter='data')
        p=root/'research/p104-noisy-copy-reset'
        original=(p/'verify.py').read_text()
        for before,after in json.loads((P/'CONTRACT-EDITS.json').read_text()):
            need(original.count(before)==1,'unique backend seam');original=original.replace(before,after)
        original=original[:original.index("\nif __name__ == '__main__':")]
        need(original==(P/'contract.py').read_text(),'declared contract edits')
        reference=load('frozen_contract',p/'verify.py');reference.authenticate()
        precision=load('frozen_precision',p/'precision.py')
        yield p,reference,precision


def fixtures(reference,engine,integer):
    rng=random.Random(5826);cases=120;comparisons=0
    for case in range(cases):
        n=6;program=[]
        for _ in range(5+case%70):
            op=rng.choice(['INIT','CLEAR','MOVE','ADD','COPY','SCALE']);r=rng.randrange(n)
            if op in ('INIT','CLEAR'):event=[op,r,0]
            elif op=='MOVE':event=[op,r,0,0,False]
            else:
                q=rng.choice(['1/2','-3/8','2','-4','5/16','1','-1'])
                if op=='SCALE':event=[op,r,q,0]
                else:
                    s=rng.choice([i for i in range(n) if i!=r]);event=[op,r,s,q,0]
            program.append(event)
        word=dict(public=4,owned_fields=2,program=program)
        weights=[(F(rng.randrange(10),2**rng.randrange(8)),F(rng.randrange(10),2**rng.randrange(8))) for _ in program]
        rounded={op for op in ['INIT','CLEAR','MOVE','ADD','COPY','SCALE'] if rng.randrange(2)}
        a,wa=reference.error_trace(word,weights,rounded);b,wb=engine.error_trace(word,weights,rounded)
        need(a==b and wa==wb,'complete finite trace and signed witness equality')
        need(reference.reverse_all(word,weights,rounded)==engine.reverse_all(word,weights,rounded),'finite transpose equality')
        comparisons+=len(program)
    controls=[]
    for label,fn in [('nondyadic scalar',lambda:integer.dyadic(F(1,3))),('inexact scale division',lambda:integer.multiply(1,1,1)),('nondyadic weight',lambda:integer.scaled(F(1,3),8))]:
        try:fn()
        except ValueError:controls.append(label)
        else:raise ValueError('accepted invalid integer contract')
    return dict(cases=cases,events=comparisons,controls=controls)


def run(mode):
    started=time.perf_counter()
    with source() as (p,original,reference):
        expected=json.loads((p/'RESULT.json').read_text())
        if mode=='baseline':result=original.calculate()
        else:
            contract=load('explicit_contract',P/'contract.py');integer=load('integer_backend',P/'integer.py');engine=integer.Engine(reference)
            result=contract.calculate(p,engine)
        need(result==expected,'complete source result, including original controls')
        receipt=dict(source_result_sha256=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest(),events=result['ideal']['events'],coordinates=result['ideal']['n'],source_controls=len(result['rejected_controls']),guards=result['sufficient_guard_bits'])
        if mode=='qualify':
            baseline=original.calculate();need(result==baseline,'complete baseline/candidate output equality')
            # Compare the full witness rows, which are used but not all stored
            # in the source receipt. This is a qualification cost, not runtime.
            import gzip
            word=json.loads(gzip.decompress((p/'inputs/WORD.json.gz').read_bytes()));ideal,weights=reference.ideal(word);rounded=set(ideal['counts'])
            need(engine.ideal(word)==(ideal,weights),'full ideal metadata and exact local weights')
            a,wa=reference.error_trace(word,weights,rounded);b,wb=engine.error_trace(word,weights,rounded)
            need(a==b and wa==wb,'all actual signed witness rows')
            receipt['finite_fixtures']=fixtures(reference,engine,integer)
            receipt['coefficient_scale_bits']=integer.setup(word,weights)[2].bit_length()-1
            receipt['all_actual_witness_rows_equal']=True
    return receipt,time.perf_counter()-started


if __name__=='__main__':
    args=sys.argv[1:];mode='candidate' if not args else args[0].removeprefix('--')
    need(mode in ('candidate','baseline','qualify'),'mode')
    receipt,seconds=run(mode)
    if mode=='qualify':
        if args[1:]==['--write']:(P/'RESULT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        else:need(not args[1:] and receipt==json.loads((P/'RESULT.json').read_text()),'qualification receipt')
    else:need(len(args)<=1,'arguments')
    print('PASS_P104_INTEGER_ERROR_REPLAY')
    print(json.dumps({'mode':mode,'seconds':round(seconds,6),'receipt':receipt},sort_keys=True))
