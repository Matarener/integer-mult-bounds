#!/usr/bin/env python3
"""Semantic factor, chronology, invoice and input-integrity failure controls."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import h6_inputs
from h6_inputs import need
from e8_exact import geometry
from pair_factor import factor_columns,mixed_block,product
from word import fixture,replay,factor_check,captures
from verify import read,validate


def check():
    passed=[]
    def rejected(name,fn,message):
        try:fn()
        except ValueError as error:
            need(message in str(error),'wrong rejection for '+name+': '+str(error))
            passed.append(name)
        else:raise ValueError('accepted negative control '+name)
    geo=geometry();_,(indices,old,new)=fixture(geo)
    for dual in (False,True):
        suffix='dual' if dual else 'forward'
        rejected('matched-wrong-sign-'+suffix,
                 lambda:replay(new,indices,geo,dual,wrong_sigma=True),'all data and helper-dirt columns')
        for phase in ('dirt_prefix','cleanup','K'):
            rejected('omit-'+phase+'-'+suffix,
                     lambda:replay(new,indices,geo,dual,omit=phase),
                     'helper entrance returned' if (dual and phase=='dirt_prefix') or (not dual and phase=='cleanup')
                     else 'all data and helper-dirt columns')
        rejected('premature-source-FULL-'+suffix,
                 lambda:replay(new,indices,geo,dual,early_full=True),'complete K receives actual source lines')
    full=mixed_block(2,1)
    rejected('compress-full-rank-bucket',lambda:factor_columns(full,1),'exact signed column relation')
    false_D=[[r[0]] for r in full];false_G=[[F(1),F(1)]]
    need(product(false_D,false_G)!=full,'independent full-rank DG counterexample')
    for name,mutate in (
        ('missing-D-entry',lambda row:row['D'].pop(next(iter(row['D'])))),
        ('wrong-D-coefficient',lambda row:row['D'].__setitem__(next(iter(row['D'])),F(7,16))),
    ):
        rows=deepcopy(new);mutate(rows[0])
        rejected(name,lambda:factor_check(rows,indices,indices,geo),'complete DG=C')
    mixed=next(p for p in indices if p>=2160)
    bad=[p for p in indices if p!=mixed]
    rejected('incomplete-mixed-source-fiber',lambda:list(captures(bad,indices,geo)),'complete actual mixed source pair')
    rows=deepcopy(new);row=next(r for r in rows if len(r['G'])==2)
    source=next(iter(row['G']));weight=row['G'].pop(source)
    # A pure source has a different actual label from every mixed source.
    row['G'][next(p for p in indices if p<2160)]=weight
    rejected('different-actual-source-frame',lambda:replay(rows,indices,geo),'actual same-frame operands at capture')
    receipt=read(HERE/'CERTIFICATE.json')
    for name,path,value in (
        ('false-deleted-source-read',('invoice','capture_entries_old_and_new'),123632640),
        ('wrong-helper-count',('invoice','new_helpers'),123632639),
        ('boolean-integer-receipt',('full_E8_cosets',),True),
        ('float-integer-receipt',('root_lines',),120.0),
        ('unaccounted-capture-range',('invoice','capture_range_new'),'E+X'),
    ):
        bad=deepcopy(receipt);cursor=bad
        for key in path[:-1]:cursor=cursor[key]
        cursor[path[-1]]=value
        rejected(name,lambda:validate(receipt,bad),'complete typed H6 capture certificate')
    bad=deepcopy(receipt);bad.pop('fixture')
    rejected('missing-whole-fixture',lambda:validate(receipt,bad),'complete typed H6 capture certificate')
    with tempfile.TemporaryDirectory(prefix='h6-capture-controls-') as temp:
        root=Path(temp);package=root/'research/h6-mixed-pair-capture';package.mkdir(parents=True)
        inventory=(HERE/'SOURCES.json').read_bytes();(package/'SOURCES.json').write_bytes(inventory)
        for row in json.loads(inventory)['files']:
            if row['usage']!='input':continue
            target=root/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(h6_inputs.ROOT/row['path'],target)
        saved_here,saved_root=h6_inputs.HERE,h6_inputs.ROOT
        try:
            h6_inputs.HERE,h6_inputs.ROOT=package,root
            h6_inputs.authenticate()
            target=root/'research/e8-complex-gauge-kernel/code/emit_gk.py'
            target.write_text("def primitive_bound(op):\n    raise RuntimeError('UNAUTHENTICATED_EXECUTION')\n")
            rejected('source-corruption-before-execution',h6_inputs.oracles,'source SHA256')
            manifest=json.loads(inventory)
            manifest['files']=[r for r in manifest['files'] if r['path']!='research/e8-complex-gauge-kernel/code/emit_gk.py']
            (package/'SOURCES.json').write_text(json.dumps(manifest))
            rejected('manifest-removal-before-execution',h6_inputs.oracles,'sealed source inventory')
        finally:h6_inputs.HERE,h6_inputs.ROOT=saved_here,saved_root
        duplicate=root/'duplicate.json';duplicate.write_text('{"root_lines":120,"root_lines":121}')
        rejected('duplicate-receipt-key',lambda:read(duplicate),'unique certificate keys')
    before=(HERE/'CERTIFICATE.json').read_bytes()
    proc=subprocess.run([sys.executable,'-I','-B',str(HERE/'verify.py'),'--write'],capture_output=True,text=True,timeout=10)
    need(proc.returncode!=0 and 'refuse certificate overwrite' in proc.stderr,'write refusal before recomputation')
    need((HERE/'CERTIFICATE.json').read_bytes()==before,'write refusal preserves receipt')
    passed.append('CLI-overwrite-refusal')
    print('PASS_H6_CAPTURE_CONTROLS '+json.dumps({'count':len(passed),'rejected':passed},sort_keys=True))


if __name__=='__main__':check()
