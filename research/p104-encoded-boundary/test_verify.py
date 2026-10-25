#!/usr/bin/env python3
"""Behavioral publication/export controls; no third-party dependencies."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def snapshot(root):
    return {str(p.relative_to(root)):(hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_mode & 0o777) for p in root.rglob('*') if p.is_file()}


class Controls(unittest.TestCase):
    def export(self,tmp):
        target=Path(tmp)/'research'/HERE.name
        shutil.copytree(HERE,target,ignore=shutil.ignore_patterns('__pycache__'))
        # Mutations belong only to private copies, even when source export is read-only.
        for copied in target.rglob('*'):
            if copied.is_file(): copied.chmod(0o644)
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if row['usage']=='input':
                q=Path(tmp)/row['path'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['path'],q)
        return target
    def run_cli(self,p,*args):
        return subprocess.run([sys.executable,'-I','-O','-B',str(p/'verify.py'),*args],capture_output=True,text=True,timeout=120,env={'PATH':'','LANG':'C.UTF-8'})
    def test_optimized_readonly_gitfree(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.export(td)
            for f in Path(td).rglob('*'):
                if f.is_file():f.chmod(0o444)
            before=snapshot(Path(td));r=self.run_cli(p)
            self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(snapshot(Path(td)),before)
            self.assertFalse((Path(td)/'.git').exists())
    def test_source_corruption(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.export(td);f=Path(td)/'notes/copied-centers-complex.tex';f.write_text(f.read_text()+'\ncorruption\n')
            r=self.run_cli(p);self.assertNotEqual(r.returncode,0);self.assertIn('input hash',r.stderr)
    def test_missing_source(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.export(td);(Path(td)/'research/p104-native-channel/inputs/P104-FIXTURE.json').unlink()
            self.assertNotEqual(self.run_cli(p).returncode,0)
    def test_false_zero_boundary_invoice(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.export(td);f=p/'RESULT.json';r=json.loads(f.read_text());r['formal_transition_invoice']['unit_add_sub']=0;f.write_text(json.dumps(r))
            out=self.run_cli(p);self.assertNotEqual(out.returncode,0);self.assertIn('result mismatch',out.stderr)
    def test_false_gate_and_identity(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.export(td);f=p/'RESULT.json';r=json.loads(f.read_text());r['conditional_gate']['excess']=0;r['physical_dc_witness']['row_extra_Y_slots']=0;f.write_text(json.dumps(r))
            self.assertNotEqual(self.run_cli(p).returncode,0)
    def test_duplicate_result_key(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.export(td);(p/'RESULT.json').write_text('{"a":1,"a":2}')
            r=self.run_cli(p);self.assertNotEqual(r.returncode,0);self.assertIn('duplicate JSON key',r.stderr)

if __name__=='__main__':unittest.main(verbosity=2)
