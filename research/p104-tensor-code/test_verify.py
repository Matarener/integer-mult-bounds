#!/usr/bin/env python3
"""Publication and behavioral controls for the scalar tensor-code contract."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]


def snap(root):return {str(p.relative_to(root)):(hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_mode&0o777) for p in root.rglob('*') if p.is_file()}


class Controls(unittest.TestCase):
    def export(self,tmp):
        target=Path(tmp)/'research'/HERE.name
        shutil.copytree(HERE,target,ignore=shutil.ignore_patterns('__pycache__'))
        for f in target.rglob('*'):
            if f.is_file():f.chmod(0o644)
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if row['usage']=='input':
                q=Path(tmp)/row['path'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['path'],q)
        return target
    def cli(self,p,script='verify.py'):
        return subprocess.run([sys.executable,'-I','-O','-B',str(p/script)],env={'PATH':'','LANG':'C.UTF-8'},capture_output=True,text=True,timeout=120)
    def test_readonly_gitfree_optimized(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.export(td)
            for f in Path(td).rglob('*'):
                if f.is_file():f.chmod(0o444)
            before=snap(Path(td))
            for script in ('verify.py','independent.py'):
                r=self.cli(p,script);self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(before,snap(Path(td)));self.assertFalse((Path(td)/'.git').exists())
    def test_corrupt_source(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.export(td);f=Path(td)/'notes/copied-centers-complex.tex';f.write_text(f.read_text()+'\ncorruption\n')
            r=self.cli(p);self.assertNotEqual(r.returncode,0);self.assertIn('input hash',r.stderr)
    def test_missing_source(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.export(td);(Path(td)/'research/p104-native-channel/inputs/P104-FIXTURE.json').unlink();self.assertNotEqual(self.cli(p).returncode,0)
    def test_typed_receipt_rejects_float_integer(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.export(td);f=p/'RESULT.json';x=json.loads(f.read_text());x['first_add_break_even_integer']=2.0;f.write_text(json.dumps(x));r=self.cli(p)
            self.assertNotEqual(r.returncode,0);self.assertIn('typed result mismatch',r.stderr)
    def test_false_fullcaller_claim_and_free_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.export(td);f=p/'RESULT.json';x=json.loads(f.read_text());x['boundary_invoice']['add']=0;x['full_identity_side_rank']=0;f.write_text(json.dumps(x));self.assertNotEqual(self.cli(p).returncode,0)
    def test_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.export(td);(p/'RESULT.json').write_text('{"a":1,"a":2}');r=self.cli(p);self.assertNotEqual(r.returncode,0);self.assertIn('duplicate JSON key',r.stderr)
    def test_donor_restoration_and_alphabet(self):
        spec=importlib.util.spec_from_file_location('primary_words',HERE/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
        word=list(v.code_word([[1,-1]]));bad=list(word);bad.pop(next(i for i,o in enumerate(bad) if o[0]=='double'))
        data=[(j+1)*4096 for j in range(18)]
        self.assertNotEqual(v.evaluate(bad,data),v.evaluate(word,data))
        with self.assertRaisesRegex(ValueError,'unknown operation'):v.evaluate([('divide13',0)],data)

if __name__=='__main__':unittest.main(verbosity=2)
