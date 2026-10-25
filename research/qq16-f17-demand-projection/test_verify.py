#!/usr/bin/env python3
"""Boundary checks for the changed consumer. Chris R / Clear1nsight, OpenAI; Apache-2.0."""
import hashlib
import importlib.util
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


def imported():
    spec=importlib.util.spec_from_file_location('demand_verify',HERE/'verify.py')
    v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    return v


def inventory(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class Boundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v=imported();cls.actual=cls.v.calculate()

    def export(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        root=Path(temp.name);pkg=root/'research'/HERE.name
        shutil.copytree(HERE,pkg,ignore=shutil.ignore_patterns('__pycache__'))
        for pin in json.loads((HERE/'SOURCES.json').read_bytes())['files']:
            if pin['usage']=='input':
                target=root/pin['path'];target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(ROOT/pin['path'],target)
        return root,pkg

    def run_export(self,pkg):
        return subprocess.run([sys.executable,'-I','-O','-Werror','-B',str(pkg/'verify.py')],
                              text=True,capture_output=True,timeout=180)

    def test_complete_source_word_and_receipt(self):
        self.assertEqual(self.v.canonical(self.actual),self.v.canonical(self.v.decode((HERE/'RESULT.json').read_bytes())))
        P,_,_,_,source=self.v.load(self.v.authenticate())
        self.assertEqual(self.v.projection(P,source),self.v.decode((HERE/'WORD.json').read_bytes()))
        self.assertEqual(len(self.actual['controls']),9)

    def test_budget_conclusion_changes_with_rank8_premise(self):
        b=self.actual['budget']
        from fractions import Fraction as Q
        self.assertGreater(Q(b['centre64_retaining_eight_rank8']['lower']),1)
        self.assertLess(Q(b['centre64_waiving_eight_rank8']['upper']),1)
        self.assertEqual(b['pair_call_reduction_still_required_with_rank8_retained'],51)

    def test_git_free_read_only_export(self):
        root,pkg=self.export();before=inventory(root)
        paths=list(root.rglob('*'))
        try:
            for p in paths:p.chmod(0o555 if p.is_dir() else 0o444)
            root.chmod(0o555)
            result=self.run_export(pkg)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('PASS_QQ16_F17_DEMAND_PROJECTION',result.stdout)
            self.assertEqual(inventory(root),before)
        finally:
            root.chmod(0o755)
            for p in paths:p.chmod(0o755 if p.is_dir() else 0o644)

    def test_source_rejected_before_execution(self):
        root,pkg=self.export()
        path=root/'research/qq16-line-normalized-decoder/verify.py'
        path.write_text("raise RuntimeError('EXECUTED_CORRUPT_SOURCE')\n")
        result=self.run_export(pkg)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('source SHA256:',result.stderr)
        self.assertNotIn('RuntimeError: EXECUTED_CORRUPT_SOURCE',result.stderr)

    def test_type_sensitive_receipt_rejection(self):
        _,pkg=self.export();p=pkg/'RESULT.json';r=json.loads(p.read_bytes())
        r['invoice']['rank_one_children']='112';p.write_text(json.dumps(r))
        result=self.run_export(pkg)
        self.assertNotEqual(result.returncode,0);self.assertIn('complete RESULT mismatch',result.stderr)

    def test_missing_cleanup_word_rejection(self):
        _,pkg=self.export();p=pkg/'WORD.json';w=json.loads(p.read_bytes());w.pop();p.write_text(json.dumps(w))
        result=self.run_export(pkg)
        self.assertNotEqual(result.returncode,0);self.assertIn('complete WORD mismatch',result.stderr)

    def test_missing_receipt_is_not_regenerated(self):
        _,pkg=self.export();p=pkg/'RESULT.json';p.unlink()
        result=self.run_export(pkg)
        self.assertNotEqual(result.returncode,0);self.assertFalse(p.exists())


if __name__=='__main__':unittest.main()
