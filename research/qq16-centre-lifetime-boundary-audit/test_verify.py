#!/usr/bin/env python3
"""Behavioral export/integrity tests; Chris R / Clear1nsight, OpenAI; Apache-2.0."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def snapshot(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        s=importlib.util.spec_from_file_location('audit',HERE/'verify.py')
        cls.v=importlib.util.module_from_spec(s);s.loader.exec_module(cls.v)
        cls.result=cls.v.calculate()

    def export(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        root=Path(tmp.name);pkg=root/'research'/HERE.name
        shutil.copytree(HERE,pkg,ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_bytes())['files']:
            if row['usage']=='input':
                target=root/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(ROOT/row['path'],target)
        return root,pkg

    def execute(self,pkg,opt=True):
        flags=['-I','-Werror','-B']+(['-O'] if opt else [])
        return subprocess.run([sys.executable,*flags,str(pkg/'verify.py')],capture_output=True,text=True,timeout=240)

    def test_complete_typed_receipt(self):
        self.assertEqual(self.v.canonical(self.result),self.v.canonical(self.v.decode((HERE/'RESULT.json').read_bytes())))
        self.assertEqual(self.result['centre_provenance_and_lifetimes']['actual_QQ16_calls']['F_0']['literal_H8'],0)
        self.assertEqual(self.result['actual_recovery_continuation']['entry_missing_count'],128)

    def test_read_only_git_free_export(self):
        root,pkg=self.export();before=snapshot(root);paths=list(root.rglob('*'))
        try:
            for p in paths:p.chmod(0o555 if p.is_dir() else 0o444)
            root.chmod(0o555)
            done=self.execute(pkg)
            self.assertEqual(done.returncode,0,done.stderr)
            self.assertIn('PASS_QQ16_CENTRE_LIFETIME_BOUNDARY_AUDIT',done.stdout)
            self.assertEqual(snapshot(root),before)
        finally:
            root.chmod(0o755)
            for p in paths:p.chmod(0o755 if p.is_dir() else 0o644)

    def test_source_rejected_before_parsing(self):
        root,pkg=self.export()
        (root/'research/joint-query/certificate.json.gz').write_bytes(b'NOT_GZIP_NOT_JSON')
        done=self.execute(pkg)
        self.assertNotEqual(done.returncode,0)
        self.assertIn('source SHA256:',done.stderr)
        self.assertNotIn('BadGzipFile',done.stderr)

    def test_retained_predecessor_word_corruption(self):
        _,pkg=self.export();path=pkg/'vendor/pr3952/WORD.json'
        path.write_bytes(path.read_bytes()+b' ')
        done=self.execute(pkg)
        self.assertNotEqual(done.returncode,0);self.assertIn('retained PR3952 word',done.stderr)

    def test_typed_result_corruption(self):
        _,pkg=self.export();path=pkg/'RESULT.json';r=json.loads(path.read_bytes())
        r['actual_outer_boundary']['independent_missing_query_directions']='8';path.write_text(json.dumps(r))
        done=self.execute(pkg)
        self.assertNotEqual(done.returncode,0);self.assertIn('complete RESULT mismatch',done.stderr)

    def test_missing_receipt_not_recreated(self):
        _,pkg=self.export();path=pkg/'RESULT.json';path.unlink()
        done=self.execute(pkg)
        self.assertNotEqual(done.returncode,0);self.assertFalse(path.exists())

    def test_conditional_budget_and_full_completion_have_different_decisions(self):
        budget=self.result['conditional_budget']
        self.assertEqual(budget['fixed_total_h8_pair']['0']['decision'],'strict_pass')
        self.assertEqual(budget['restored_full_consumer336_pair_h8_waived']['decision'],'strict_fail')
        self.assertEqual(budget['fixed_total_h8_pair']['2']['decision'],'strict_pass')
        self.assertEqual(budget['fixed_total_h8_pair']['3']['decision'],'strict_fail')


if __name__=='__main__':unittest.main()
