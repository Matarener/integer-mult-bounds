#!/usr/bin/env python3
"""Isolated integrity, semantic-boundary and read-only replay controls."""
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

def run(path,opt=False,extra=()):
    return subprocess.run([sys.executable,'-I','-B']+(['-O'] if opt else [])+[str(path/'verify.py'),*extra],capture_output=True,text=True,timeout=60,env={'PATH':'','PYTHONDONTWRITEBYTECODE':'1'})

def digest_tree(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}

class Boundaries(unittest.TestCase):
    def test_readonly_git_free_normal_and_optimized(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'package';shutil.copytree(HERE,target)
            for p in target.rglob('*'):p.chmod(0o555 if p.is_dir() else 0o444)
            target.chmod(0o555);before=digest_tree(target)
            try:
                for opt in (False,True):
                    result=run(target,opt);self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                    self.assertIn('PASS_QQ16_PHYSICAL_TRANSITION',result.stdout)
                self.assertEqual(before,digest_tree(target));self.assertFalse((Path(temp)/'.git').exists())
            finally:
                target.chmod(0o755)
                for p in target.rglob('*'):p.chmod(0o755 if p.is_dir() else 0o644)
    def test_source_receipt_manifest_and_overwrite_reject(self):
        for opt in (False,True):
            for name in ('source','manifest','typed receipt','write'):
                with self.subTest(opt=opt,name=name),tempfile.TemporaryDirectory() as temp:
                    target=Path(temp)/'package';shutil.copytree(HERE,target)
                    if name=='source':
                        p=target/'vendor/pr4015/WORD.json';p.write_bytes(p.read_bytes()+b' ')
                    elif name=='manifest':
                        p=target/'PREDECESSORS.json';p.write_bytes(p.read_bytes()+b' ')
                    elif name=='typed receipt':
                        p=target/'RESULT.json';r=json.loads(p.read_text());r['scope']['no_new_kappa']=1;p.write_text(json.dumps(r))
                    result=run(target,opt,('--write',) if name=='write' else ())
                    self.assertNotEqual(result.returncode,0,result.stdout)
                    self.assertNotIn('PASS_QQ16_PHYSICAL_TRANSITION',result.stdout)

if __name__=='__main__':unittest.main(verbosity=2)
