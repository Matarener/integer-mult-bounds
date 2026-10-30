#!/usr/bin/env python3
"""Boundary validation for authenticated read-only address audit."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PKG=Path(__file__).resolve().parent
ROOT=PKG.parents[1]
REL=PKG.relative_to(ROOT)

class Boundary(unittest.TestCase):
    def tree(self, dest):
        shutil.copytree(PKG,dest/REL)
        for x in json.loads((PKG/'SOURCES.json').read_bytes())['files']:
            if x['usage']=='input':
                q=dest/x['path'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/x['path'],q)
        return dest/REL
    def run_audit(self,p,optimized=True,extra=(),ok=True):
        r=subprocess.run([sys.executable,'-I','-B']+(['-O'] if optimized else [])+[str(p/'verify.py'),*extra],cwd=p,env={**os.environ,'PATH':'/nonexistent'},capture_output=True,text=True,timeout=120)
        self.assertEqual(r.returncode==0,ok,r.stdout+r.stderr)
        return r
    def snapshot(self,p):
        return {str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file()}
    def test_normal_optimized_git_free_readonly(self):
        before=self.snapshot(PKG)
        self.run_audit(PKG,False);self.run_audit(PKG)
        self.assertEqual(before,self.snapshot(PKG))
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=self.tree(root);before=self.snapshot(root)
            self.assertFalse((root/'.git').exists())
            self.run_audit(p);self.assertEqual(before,self.snapshot(root))
    def test_mutations_and_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=self.tree(root)
            f=p/'RESULT.json';b=f.read_bytes();v=json.loads(b);v['reserve_candidate']['explicit_top_level_conflicts']=False;f.write_text(json.dumps(v))
            self.assertIn('typed complete receipt mismatch',self.run_audit(p,ok=False).stderr);f.write_bytes(b)
            f=p/'vendor/pr4015/WORD.json';b=f.read_bytes();f.write_bytes(b+b' ')
            self.assertIn('pending data authentication',self.run_audit(p,ok=False).stderr);f.write_bytes(b)
            f=root/'research/gauge44-slots-t16/code/emit_allcold.py';b=f.read_bytes();f.write_bytes(b+b'\n')
            self.assertIn('canonical source authentication',self.run_audit(p,ok=False).stderr);f.write_bytes(b)
            before=self.snapshot(root)
            self.assertIn('refuse overwrite',self.run_audit(p,extra=['--write'],ok=False).stderr)
            self.assertEqual(before,self.snapshot(root))

if __name__=='__main__': unittest.main()
