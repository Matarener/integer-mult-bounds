#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Actual standalone CLI acceptance and fail-closed source/claim/proof controls.
Dugongue, with substantial OpenAI Codex assistance.
"""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,unittest
P=Path(__file__).resolve().parent

class CliTests(unittest.TestCase):
 def test_actual_export_and_corruptions(self):
  with tempfile.TemporaryDirectory(prefix='staged544-cli-') as folder:
   package=Path(folder)/'package';shutil.copytree(P,package,ignore=shutil.ignore_patterns('__pycache__','.lake'))
   def hashes():return {p.relative_to(package).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in package.rglob('*') if p.is_file()}
   def run(*options,extra=()):
    env=dict(os.environ,PYTHONPYCACHEPREFIX=str(Path(folder)/'bytecode'));env.pop('PYTHONOPTIMIZE',None)
    return subprocess.run([sys.executable,*options,'-B',str(package/'verify.py'),*extra],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
   original=hashes();result=run();self.assertEqual(result.returncode,0,result.stdout.decode(errors='replace'));self.assertIn(b'PASS_STAGED544_CURRENT_CONDITIONAL_ENDPOINT',result.stdout);self.assertEqual(hashes(),original)
   for name,mutator in [('CLAIM.json',lambda x:x.__setitem__('kappa','0')),('CLAIM.json',lambda x:x.__setitem__('fresh_native_replay',True)),('CLAIM.json',lambda x:x.__setitem__('physical',323068)),('RESULT.json',lambda x:x.__setitem__('scope','false scope')),('FORMAL-DATA.json',lambda x:x['log_upper'].__setitem__('1','0'))]:
    with self.subTest(file=name):
     file=package/name;before=file.read_bytes();data=json.loads(before);mutator(data)
     try:file.write_text(json.dumps(data),encoding='utf-8');self.assertNotEqual(run().returncode,0)
     finally:file.write_bytes(before)
   for file in [package/'vendor/staged544-clock-ceiling/clock.py',package/'lean/AnalyticCertificate.lean']:
    before=file.read_bytes()
    try:file.write_bytes(before+b'\n# source mutation\n');self.assertNotEqual(run().returncode,0)
    finally:file.write_bytes(before)
   self.assertNotEqual(run('-O').returncode,0,'inherited assertions must remain enabled')
   existing=Path(folder)/'existing.json';existing.write_bytes(b'preserve this')
   self.assertNotEqual(run(extra=('--output',str(existing))).returncode,0);self.assertEqual(existing.read_bytes(),b'preserve this')
   self.assertEqual(hashes(),original,'read-only source and all corruption preimages restored')
if __name__=='__main__':unittest.main(verbosity=2)
