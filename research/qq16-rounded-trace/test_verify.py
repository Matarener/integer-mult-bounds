#!/usr/bin/env python3
"""Boundary, provenance and receipt controls for the rounded trace theorem."""
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
 return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}

def run(root,opt=True,extra=(),env=None):
 argv=[sys.executable,'-I']+(['-O'] if opt else [])+['-Werror','-B',str(root/'research/qq16-rounded-trace/verify.py'),*extra]
 return subprocess.run(argv,cwd=root,env=env,capture_output=True,text=True,timeout=60)

class Boundary(unittest.TestCase):
 def export(self):
  td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup);root=Path(td.name)
  shutil.copytree(HERE,root/'research/qq16-rounded-trace',ignore=shutil.ignore_patterns('__pycache__'))
  for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
   if row['usage']=='input':
    p=root/row['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['path'],p)
  return root
 def test_normal_optimized_readonly(self):
  before=snapshot(HERE)
  for opt in (False,True):
   p=run(ROOT,opt);self.assertEqual(p.returncode,0,p.stdout+p.stderr);self.assertIn('PASS_QQ16_ROUNDED_TRACE_EQUIVALENCE',p.stdout)
  self.assertEqual(before,snapshot(HERE))
 def test_git_free_readonly(self):
  root=self.export();before=snapshot(root)
  for p in root.rglob('*'):
   if p.is_file():p.chmod(0o444)
  for opt in (False,True):
   p=run(root,opt,env=dict(os.environ,PATH='/nonexistent',PYTHONDONTWRITEBYTECODE='1'));self.assertEqual(p.returncode,0,p.stdout+p.stderr)
  self.assertEqual(before,snapshot(root))
 def test_retained_words_and_proof_authenticated(self):
  for name in ('PR3985-WORD.json','PR4015-WORD.json','PR3652-PROOF.md'):
   root=self.export();p=root/'research/qq16-rounded-trace/vendor'/name;p.write_bytes(b'not valid JSON or source')
   r=run(root);self.assertNotEqual(r.returncode,0);self.assertIn('retained source hash:',r.stderr);self.assertNotIn('JSONDecodeError',r.stderr)
 def test_canonical_scope_source_authenticated(self):
  root=self.export();p=root/'research/qq16-all-depth-producer-grid/PROOF.md';p.write_text('changed scope')
  r=run(root);self.assertNotEqual(r.returncode,0);self.assertIn('source hash:',r.stderr)
 def test_mapping_and_typed_receipt(self):
  root=self.export();p=root/'research/qq16-rounded-trace/RESULT.json';original=json.loads(p.read_text())
  for mode in ('mapping','type'):
   r=json.loads(json.dumps(original))
   if mode=='mapping':r['event_mapping'][0][1]+=1
   else:r['matched_value_events']=3392.0
   p.write_text(json.dumps(r));out=run(root);self.assertNotEqual(out.returncode,0);self.assertIn('whole typed receipt mismatch',out.stderr)
 def test_refuse_overwrite(self):
  before=snapshot(HERE);r=run(ROOT,extra=('--write',));self.assertNotEqual(r.returncode,0);self.assertIn('refuse overwrite',r.stderr);self.assertEqual(before,snapshot(HERE))
if __name__=='__main__':unittest.main(verbosity=2)
