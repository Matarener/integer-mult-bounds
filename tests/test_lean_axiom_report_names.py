"""Lean axiom reports must retain primed names and reject extra dependencies."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('lean_axiom_report_audit', ROOT / 'scripts/check_lean_axioms.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

PRIMED = """import Init
theorem actual' : True := True.intro
theorem allowed'' (p q : Prop) (h : p ↔ q) : p = q := Classical.choice ⟨propext h⟩
#print axioms actual'
#print axioms allowed''
"""
EXTRA_PRIMED = """import Init
theorem good : True := True.intro
axiom custom : False
theorem bad' : False := custom
#print axioms good
#print axioms bad' #check Nat
"""


class ReportNames(unittest.TestCase):
    def test_primed_and_ordinary_reports(self):
        for name in ('actual', "actual'", "Namespace.lemma''", "inner'prime"):
            for report in ('does not depend on any axioms',
                           'depends on axioms: [propext,\n Classical.choice,\n Quot.sound]'):
                with self.subTest(name=name, report=report):
                    self.assertEqual(audit.check_output(f"'{name}' {report}\n", [name]), 1)

    def test_primed_reports_remain_fail_closed(self):
        good = "'actual' does not depend on any axioms\n"
        for extra in ("'extra'' does not depend on any axioms\n",
                      "'extra'' depends on axioms: [sorryAx]\n",
                      "'extra'' depends on axioms: [custom]\n",
                      "'extra'' depends on axioms: [propext,\n",
                      "'extra'' does not depend on any axioms trailing text\n"):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                audit.check_output(good + extra, ['actual'])
        for bad in ('sorryAx', 'custom', 'propext,, Classical.choice'):
            with self.subTest(axioms=bad), self.assertRaises(ValueError):
                audit.check_output(f"'actual'' depends on axioms: [{bad}]\n", ["actual'"])
        with self.assertRaises(ValueError):
            audit.check_output("'actual'' does not depend on any axioms\n" * 2, ["actual'"])
        with self.assertRaises(ValueError):
            audit.check_output("'different'' does not depend on any axioms\n", ["actual'"])

    def test_report_delimiter_and_line_boundaries(self):
        name = "contains' depends on axioms: [custom]"
        self.assertEqual(audit.check_output(f"'{name}' does not depend on any axioms\n", [name]), 1)
        for name in ("across\nlines'", "across\rlines'"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                audit.check_output(f"'{name}' does not depend on any axioms\n", [name])

    @unittest.skipUnless(os.environ.get('LEAN_AUDIT_BIN'), 'set LEAN_AUDIT_BIN for live kernel controls')
    def test_real_lean_reports_and_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / 'lakefile.lean').write_text('import Lake\nopen Lake DSL\npackage auditFixture\n')
            env = {**os.environ, 'PATH': os.environ['LEAN_AUDIT_BIN'] + os.pathsep + os.environ['PATH']}
            cases = [('Primed', PRIMED, True), ('ExtraPrimed', EXTRA_PRIMED, False),
                     ('Custom', "import Init\naxiom custom : False\n#print axioms custom\n", False),
                     ('Sorry', "import Init\ntheorem bad' : False := by sorry\n#print axioms bad'\n", False)]
            for name, source, accepted in cases:
                with self.subTest(name=name):
                    path = project / (name + '.lean')
                    path.write_text(source, encoding='utf-8')
                    lean = subprocess.run(['lake', 'env', 'lean', str(path)], cwd=project, env=env,
                                          capture_output=True, encoding='utf-8', timeout=30)
                    self.assertEqual(lean.returncode, 0, lean.stdout + lean.stderr)
                    if name == 'ExtraPrimed':
                        # Both reports come from Lean; the source-query reader
                        # deliberately remains unchanged in this output repair.
                        self.assertEqual(audit.source_queries(source), ['good'])
                        self.assertIn("'bad'' depends on axioms: [custom]", lean.stdout)
                    checked = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/check_lean_axioms.py'),
                                              '--project', str(project), '--audit', str(path)], env=env,
                                             capture_output=True, encoding='utf-8', timeout=30)
                    self.assertEqual(checked.returncode == 0, accepted, checked.stdout + checked.stderr)
                    if accepted:
                        self.assertIn('PASS 2 declarations', checked.stdout)
                    else:
                        self.assertIn('Axiom audit failed', checked.stderr)
                        self.assertNotIn('PASS ', checked.stdout)


if __name__ == '__main__':
    unittest.main()
