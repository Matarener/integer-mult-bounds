# SPDX-License-Identifier: Apache-2.0
"""Tiny runner unit tests: no Lean execution. Run: python3 -B -m unittest discover -s tests"""
from hashlib import sha256
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import types

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
check = types.ModuleType('bridge_runner_under_test')
check.__file__ = str(HERE.parent/'check.py')
exec(compile((HERE.parent/'check.py').read_bytes(), check.__file__, 'exec'), check.__dict__)

ROOT = check.DEFAULT_ROOT
BRIDGE = HERE.parent / check.BRIDGE_REL
FIXTURE = (HERE / 'fixtures' / 'prior-exact-type-all-axioms.stdout').read_text(encoding='utf-8')
GIT = shutil.which('git')


class Tmp(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='bridge-check-test-')).resolve()
        self.addCleanup(self.clean_temp)

    def clean_temp(self):
        # Never recursively remove a computed path before checking its absolute target.
        self.assertEqual(self.tmp.parent, Path(tempfile.gettempdir()).resolve())
        self.assertTrue(self.tmp.name.startswith('bridge-check-test-'))
        def clear_readonly(function, path, error):
            target = Path(path).resolve()
            self.assertTrue(target.is_relative_to(self.tmp))
            os.chmod(path, stat.S_IWRITE)
            function(path)
        shutil.rmtree(self.tmp, onexc=clear_readonly)


class Sources(unittest.TestCase):
    def test_pinned_sources_and_formal_text(self):
        pins = check.source_pins(ROOT)
        self.assertEqual(len(pins), len(check.BASE_SHA256) + 2 + len(check.PROBES))
        data = BRIDGE.read_bytes()
        self.assertEqual(sha256(data).hexdigest(), check.BRIDGE_SHA256)
        self.assertNotEqual(check.BRIDGE_SHA256, check.PRIOR_BRIDGE_SHA256)
        # Comment edits keep the formal digest; a proof-token edit changes it.
        self.assertEqual(check.formal_digest(data.replace(b'Status:', b'State:', 1)), check.BRIDGE_FORMAL_SHA256)
        self.assertNotEqual(check.formal_digest(data.replace(b'all_goals omega', b'all_goals simp', 1)),
                            check.BRIDGE_FORMAL_SHA256)

    def test_comment_stripper(self):
        self.assertEqual(check.strip_lean_comments('a /- x /- y -/ z -/ b -- c\nd "--k"'), 'a  b \nd "--k"')
        with self.assertRaises(check.CheckError):
            check.strip_lean_comments('/- open /- nested -/')

    def test_inventory_and_forbidden_tokens(self):
        code = check.strip_lean_comments(BRIDGE.read_text(encoding='utf-8'))
        check.scan_forbidden(code, 'bridge')
        self.assertEqual(sorted(check.bridge_inventory(code)), sorted(check.REQUIRED_NAMES))
        for bad in ('theorem x : True := sorry', 'theorem x : True := by native_decide', 'axiom x : False',
                    'set_option debug.skipKernelTC true', '#eval 1'):
            with self.assertRaises(check.CheckError):
                check.scan_forbidden(code + '\n' + bad, 'bridge')
        with self.assertRaises(check.CheckError):
            check.bridge_inventory(code.replace('end CompilerAudit.SourceBridge', 'theorem extra : True := trivial\nend CompilerAudit.SourceBridge'))
        with self.assertRaises(check.CheckError):
            check.bridge_inventory(code.replace('theorem fm_other', 'def fm_other'))

    def test_exact_type_file_is_prior_review_file(self):
        self.assertEqual(sha256(check.exact_type_source().encode()).hexdigest(), check.PRIOR_EXACT_TYPE_SHA256_LF)


class AxiomParser(unittest.TestCase):
    def test_prior_output_with_apostrophe_names(self):
        found = check.parse_axiom_report(FIXTURE, check.REQUIRED_NAMES)
        self.assertEqual(len(found), 27)
        self.assertEqual(found["CompilerAudit.SourceBridge.flatMap_range'_const"], ['propext', 'Quot.sound'])
        self.assertEqual(found['CompilerAudit.SourceBridge.fm_other'], [])
        self.assertEqual(sha256(FIXTURE.encode()).hexdigest(), check.PRIOR_EXACT_TYPE_STDOUT_SHA256)

    def assertRejects(self, text, names=check.REQUIRED_NAMES):
        with self.assertRaises(check.CheckError):
            check.parse_axiom_report(text, names)

    def test_rejections(self):
        line = "'CompilerAudit.SourceBridge.fm_block' does not depend on any axioms"
        self.assertIn(line, FIXTURE)
        self.assertRejects(FIXTURE.replace(line + '\n', ''))                       # missing
        self.assertRejects(FIXTURE + line + '\n')                                  # duplicate
        self.assertRejects(FIXTURE + "'Foo.bar' does not depend on any axioms\n")  # extra
        self.assertRejects(FIXTURE.replace(line, "'CompilerAudit.SourceBridge.fm_block' depends on axioms: [sorryAx]"))
        self.assertRejects(FIXTURE.replace(line, "'CompilerAudit.SourceBridge.fm_block' depends on axioms: [Lean.ofReduceBool]"))
        self.assertRejects(FIXTURE.replace(line, "'CompilerAudit.SourceBridge.fm_block' depends on axioms: [propext,\n  Quot.sound]"))
        self.assertRejects(FIXTURE + 'x.lean:1:0: warning: declaration uses sorry\n')
        self.assertRejects(FIXTURE.replace("'CompilerAudit.SourceBridge.flatMap_range'_const'", "'CompilerAudit.SourceBridge.flatMap_range'", 1))


class Leanchecker(unittest.TestCase):
    def test_only_leaf_module_invocation(self):
        self.assertEqual(check.leanchecker_argv('lc'), ['lc', '--verbose', 'CompilerAudit.SourceBridge'])
        for target in ('', 'CompilerAudit', 'CompilerAudit.SourceBridge.selected_source_transport', '--help'):
            with self.assertRaises(check.CheckError):
                check.leanchecker_argv('lc', target)

    def test_leaf_output(self):
        check.check_leaf_output(0, 'replaying CompilerAudit.SourceBridge\r\n', '')
        for rc, out, err in ((1, 'replaying CompilerAudit.SourceBridge\n', ''),
                             (0, 'replaying CompilerAudit.SourceBridge\nreplaying CompilerAudit.Result\n', ''),
                             (0, '', ''), (0, 'replaying CompilerAudit.SourceBridge\n', 'leanchecker found a problem')):
            with self.assertRaises(check.CheckError):
                check.check_leaf_output(rc, out, err)


class Environment(Tmp):
    def test_env_is_constructed_not_inherited(self):
        base = {'LEAN_PATH': '/evil', 'LEAN_SYSROOT': '/evil', 'LAKE_HOME': '/evil', 'ELAN_TOOLCHAIN': 'x',
                'GIT_DIR': '/evil', 'PATH': '/usr/bin', 'LD_PRELOAD': 'x', 'SYSTEMROOT': 'C:\\Windows', 'HOME': '/h'}
        build = self.tmp / 'build'
        env, dropped = check.build_env(self.tmp / 'bin', [build, self.tmp / 'lib1'], base)
        self.assertEqual(env['LEAN_PATH'].split(os.pathsep), [str(build), str(self.tmp / 'lib1')])
        self.assertEqual(env['PATH'], str(self.tmp / 'bin'))
        self.assertEqual(set(env), {'LEAN_PATH', 'PATH', 'PYTHONDONTWRITEBYTECODE', 'SYSTEMROOT', 'HOME'})
        self.assertEqual(set(dropped), {'LEAN_PATH', 'LEAN_SYSROOT', 'LAKE_HOME', 'ELAN_TOOLCHAIN', 'GIT_DIR', 'PATH', 'LD_PRELOAD'})

    def test_output_validation(self):
        ok = check.validate_output(self.tmp / 'fresh', [ROOT])
        self.assertEqual(ok, (self.tmp / 'fresh').resolve())
        (self.tmp / 'exists').mkdir()
        (self.tmp / 'guarded' / '.git').mkdir(parents=True)
        for bad, roots in ((Path('relative/out'), [ROOT]), (self.tmp / 'exists', [ROOT]),
                           (ROOT / 'out-inside-repo', [ROOT]), (self.tmp / 'guarded' / 'out', [ROOT]),
                           (self.tmp / 'in' / 'out', [self.tmp / 'in'])):
            with self.assertRaises(check.CheckError):
                check.validate_output(bad, roots)

    def make_toolchain(self, same=False, core=True):
        root = self.tmp / ('tc%d%d' % (same, core))
        (root / 'bin').mkdir(parents=True)
        (root / 'bin' / ('lean' + check.EXE)).write_bytes(b'lean')
        (root / 'bin' / ('leanchecker' + check.EXE)).write_bytes(b'lean' if same else b'checker')
        if core:
            (root / 'lib' / 'lean').mkdir(parents=True)
            (root / 'lib' / 'lean' / 'Init.olean').write_bytes(b'')
            (root / 'lib' / 'lean' / 'LeanChecker.olean').write_bytes(b'')
        return root

    def test_toolchain_validation(self):
        lean, checker, hashes = check.validate_toolchain(self.make_toolchain())
        self.assertEqual(set(hashes), {'bin/lean' + check.EXE, 'bin/leanchecker' + check.EXE})
        for kw in (dict(same=True), dict(core=False)):
            with self.assertRaises(check.CheckError):
                check.validate_toolchain(self.make_toolchain(**kw))


class Manifest(Tmp):
    def test_manifest_pins(self):
        manifest = ROOT / check.BASE_REL / 'lake-manifest.json'
        self.assertEqual(sorted(check.check_manifest(manifest)), sorted(check.DEPENDENCIES))
        self.assertEqual(sum(1 for v in check.DEPENDENCIES.values() if v[2]), 8)
        bad = self.tmp / 'lake-manifest.json'
        bad.write_bytes(manifest.read_bytes().replace(b'f2effa3d803fda822b1f97b806c47cf2adfbcbc2', b'0' * 40))
        with self.assertRaises(check.CheckError):
            check.check_manifest(bad)

    def make_packages(self, extra=None):
        pk = self.tmp / 'packages'
        for name, (_, _, lib) in check.DEPENDENCIES.items():
            d = pk / name / '.lake' / 'build' / 'lib' / 'lean'
            d.mkdir(parents=True)
            (d / (name.capitalize() + 'Top.olean')).write_bytes(b'')
        if extra:
            target, entry = extra
            p = pk / target / '.lake' / 'build' / 'lib' / 'lean' / entry
            p.mkdir()
        return pk

    def test_library_roots(self):
        roots = check.check_library_roots(self.make_packages(), list(check.DEPENDENCIES))
        self.assertEqual(len(roots), 8)
        self.assertFalse(any(r.parents[3].name == 'Cli' for r in roots))

    def test_shadowing_rejected(self):
        with self.assertRaises(check.CheckError):
            check.check_library_roots(self.make_packages(('mathlib', 'CompilerAudit')), list(check.DEPENDENCIES))

    def test_collision_rejected(self):
        with self.assertRaises(check.CheckError):
            check.check_library_roots(self.make_packages(('aesop', 'MathlibTop')), list(check.DEPENDENCIES))


@unittest.skipIf(GIT is None, 'git unavailable')
class Dependencies(Tmp):
    def git(self, path, *a):
        subprocess.run([GIT, '-C', str(path), *a], check=True, capture_output=True,
                       env={**check.git_env(GIT), 'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@t',
                            'GIT_COMMITTER_NAME': 't', 'GIT_COMMITTER_EMAIL': 't@t'})

    def repo(self, name):
        p = self.tmp / name
        p.mkdir()
        self.git(p, 'init', '-q')
        (p / 'a.lean').write_text('x\n')
        self.git(p, 'add', 'a.lean')
        self.git(p, 'commit', '-q', '-m', 'x')
        head = subprocess.run([GIT, '-C', str(p), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
        return p, head

    def test_dependency_checks(self):
        p, head = self.repo('dep')
        env = check.git_env(GIT)
        saved = dict(check.DEPENDENCIES)
        self.addCleanup(lambda: (check.DEPENDENCIES.clear(), check.DEPENDENCIES.update(saved)))
        check.DEPENDENCIES['dep'] = (head, 'u', True)
        self.assertTrue(check.check_dependency(GIT, p, 'dep', env)['tracked_clean'])
        (p / 'new.txt').write_text('u\n')
        self.assertEqual(check.check_dependency(GIT, p, 'dep', env)['untracked_nonignored_entries'], 1)
        check.DEPENDENCIES['dep'] = ('0' * 40, 'u', True)
        with self.assertRaises(check.CheckError):
            check.check_dependency(GIT, p, 'dep', env)                      # wrong pin
        check.DEPENDENCIES['dep'] = (head, 'u', True)
        (p / 'a.lean').write_text('changed\n')
        with self.assertRaises(check.CheckError):
            check.check_dependency(GIT, p, 'dep', env)                      # dirty tracked file
        (p / 'sub').mkdir()
        check.DEPENDENCIES['sub'] = (head, 'u', True)
        with self.assertRaises(check.CheckError):
            check.check_dependency(GIT, p / 'sub', 'sub', env)              # not its own checkout


class Probes(unittest.TestCase):
    def test_probe_sources_and_expectations(self):
        for f, expect, line, sig in check.PROBES:
            text = (HERE.parent / 'probes' / f).read_text(encoding='utf-8')
            check.scan_forbidden(check.strip_lean_comments(text), f)
            if expect == 'reject':
                self.assertRegex(text.splitlines()[line - 1], r'by decide$|^  exact ')
        self.assertTrue(check.check_lean_output('f.lean:5:62: error: Tactic `decide` proved that the proposition\n x\nis false', 'reject', 5, 'is false'))
        self.assertFalse(check.check_lean_output('f.lean:4:0: error: is false', 'reject', 5, 'is false'))
        self.assertFalse(check.check_lean_output('f.lean:3:0: warning: unused', 'accept'))


if __name__ == '__main__':
    unittest.main()