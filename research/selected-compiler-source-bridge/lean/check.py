#!/usr/bin/env python3
"""Portable, source/environment-bound Lean replay of the selected source bridge.

The runner never installs or fetches anything. It uses the exact toolchain and
an existing package cache supplied by the caller, and refuses to run when the
inputs do not match their pins:

* the seven unchanged PR3391 modules (``research/selected-compiler-visitation-
  audit/lean``) and that package's toolchain/lakefile/lake-manifest, by SHA-256;
* the candidate ``CompilerAudit/SourceBridge.lean`` by SHA-256, plus the
  SHA-256 of its comment-stripped formal text (identical to the previously
  checked source 6027af1a..., whose header comment was later corrected);
* all nine lake-manifest dependency revisions (git HEAD, clean tracked files);
  eight library roots enter LEAN_PATH, ``Cli`` is tooling-only and excluded;
* real Lean 4.34.1 binaries (commit 5045d005...), not elan shims.

The child environment is built from scratch (no inherited LEAN_*/LAKE_*/ELAN_*/
GIT_* or PATH); LEAN_PATH is explicit with the fresh build root first.
All seven baseline modules and the bridge are compiled freshly into one
``CompilerAudit`` build root under ``--output``. Then: exact main-theorem type
and the full 27-name axiom inventory, the baseline main contract, one explicit
leaf ``leanchecker --verbose CompilerAudit.SourceBridge`` replay, and small
contract probes. Imported library .olean files are trusted cached artifacts at
the pinned clean revisions; they are not rebuilt.

Usage:
  python3 -I -B check.py --output /abs/fresh/dir --toolchain TOOLCHAIN_ROOT \\
      --packages PACKAGES_ROOT [--root REPO_ROOT] [--preflight-only]
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parents[2]
PACKAGE_REL = Path('research/selected-compiler-source-bridge/lean')
BASE_REL = Path('research/selected-compiler-visitation-audit/lean')

LEAN_VERSION = 'version 4.34.1,'
LEAN_COMMIT = '5045d0056413266e57c625dcd7c365b10e377c52'
TOOLCHAIN_PIN = 'leanprover/lean4:v4.34.1'

BASE_MODULES = ['CompilerAudit.SelectedData', 'CompilerAudit.Visit', 'CompilerAudit.Retention',
                'CompilerAudit.Composition', 'CompilerAudit.Selected', 'CompilerAudit.Result',
                'CompilerAudit']
BRIDGE_MODULE = 'CompilerAudit.SourceBridge'
LEAF_MODULE = BRIDGE_MODULE
MAIN_THEOREM = 'CompilerAudit.SourceBridge.selected_source_transport'
BASE_MAIN_THEOREM = 'CompilerAudit.Result.selected_compiler_model'

BASE_SHA256 = {
    'CompilerAudit/SelectedData.lean': '7c767cf2d63aab6d46c6a2075c283eeb816781158fce90cfd13eedd1000eda88',
    'CompilerAudit/Visit.lean': '9746c2e876bcee27770fd215129cd72fc52003736cf5c088913c99d2ea1bc4d1',
    'CompilerAudit/Retention.lean': '081a35b411fe31442f727f38ab3dfdda103bd25e0c5950cf2b1733b5f426bbca',
    'CompilerAudit/Composition.lean': '022caba159e2034d9f09c92145a47caa849c46edeead5766d58a066abf47621f',
    'CompilerAudit/Selected.lean': '3b77f822e939d2d2cd3b38d92a7b73836a764eaa939aa840711bbbab7f2037e0',
    'CompilerAudit/Result.lean': 'e9499bac894329f28e9fc491ac00fd640f8e25fdf7f80ad5883954ff2bcc15d5',
    'CompilerAudit.lean': '3883991717fcfff245e90355439acb8884b3f58a943fc0fd473a037cee213dde',
    'lean-toolchain': 'd5edba4e4b8faad9c1baeadb265716d20d03be4d1a2647dc5e35b0c0325bea7b',
    'lakefile.toml': 'efacc633cf25b8f18df232bc2094a9a76813ad7676a9bf88e2df836891f9995c',
    'lake-manifest.json': 'f0e42d04edd670ffa604a770562c9dc400e21809bb5809a69c2c1cb342fe1579',
}
BRIDGE_REL = 'CompilerAudit/SourceBridge.lean'
# Candidate published bytes (header comment corrected).
BRIDGE_SHA256 = 'cb7ce5a50357fe01d4e9bf0a6c65d8767e431d3124d3e14d06e90f0bd46c38fa'
# Previously checked bytes; recorded for provenance only, not required on disk.
PRIOR_BRIDGE_SHA256 = '6027af1a083bbca309f406762dc7526e11aac6f4c4cdb90d9aa7427ad04182f9'
# SHA-256 of strip_lean_comments(source) -- equal for prior and candidate bytes.
BRIDGE_FORMAL_SHA256 = 'd1900d991547da0aa0c2f6b380ec2a60707d66907c36c39dca7eb4e3602f760a'

# name -> (rev, url, library root on LEAN_PATH)
DEPENDENCIES = {
    'mathlib': ('d13f23b723b8a846827a245b89c10fc7d3f11612', 'https://github.com/leanprover-community/mathlib4', True),
    'plausible': ('118aa17ee84656b8bd727fef7c458ee8c833385c', 'https://github.com/leanprover-community/plausible', True),
    'LeanSearchClient': ('ddf04cf3949fa556442341e87d47f9f6e6074707', 'https://github.com/leanprover-community/LeanSearchClient', True),
    'importGraph': ('e928b72544873815af278d38681b31c0293588e3', 'https://github.com/leanprover-community/import-graph', True),
    'proofwidgets': ('106ff4fafc74ef4ac99d81dbf3ab399118f497a5', 'https://github.com/leanprover-community/ProofWidgets4', True),
    'aesop': ('355695d523e41d0554926416cba2a2b3544fbbc9', 'https://github.com/leanprover-community/aesop', True),
    'Qq': ('6a489d9af5d0c47e5b259e2e8bcdfc1811b5a259', 'https://github.com/leanprover-community/quote4', True),
    'batteries': ('f2effa3d803fda822b1f97b806c47cf2adfbcbc2', 'https://github.com/leanprover-community/batteries', True),
    'Cli': ('e92c9f15fdfacc8536f31cfb3b7ad26c3c8cd204', 'https://github.com/leanprover/lean4-cli', False),
}
RESERVED_TOP = {'CompilerAudit', 'Init', 'Lean', 'Std', 'Lake', 'LeanChecker'}

REQUIRED_THEOREMS = [
    'flatMap_range\'_const', 'flatMap_range_const', 'product_map_swap', 'product_map_keep',
    'groupWord_low', 'groupWord_idle', 'map_eq_self_of', 'lows_rank', 'rank_injOn', 'lowPass_eq',
    'replicaPass_map', 'idlePass_map', 'sweep_transport', 'idle_transport', 'sourceTrace_cons',
    'trace_transport', 'mem_eventTrace_low', 'mem_sourceTrace_low', 'toFinset_map_card',
    'source_distinct', 'fm_other', 'fm_block', 'fm_seg', 'refs_emit', 'refs_length',
    'retained_emit', 'selected_source_transport']
REQUIRED_NAMES = ['CompilerAudit.SourceBridge.' + n for n in REQUIRED_THEOREMS]
ALLOWED_AXIOMS = frozenset({'propext', 'Classical.choice', 'Quot.sound'})
FORBIDDEN_TOKENS = ('sorry', 'admit', 'axiom', 'native_decide', 'unsafe', 'implemented_by', 'extern',
                    'opaque', 'partial', 'ofReduceBool', 'trustCompiler', 'set_option', 'skipKernel',
                    'debug', 'macro_rules', 'elab', 'initialize')
LEAN_FLAGS = ['-j', '1', '-M', '2048', '-DmaxRecDepth=4096', '-DmaxHeartbeats=800000']

# Byte-identical (after CRLF->LF) to integration/bridge-attempt3/ExactTypeAndAllAxioms.lean
# of the prior local review, whose LF-normalized SHA-256 is pinned below.
PRIOR_EXACT_TYPE_SHA256_LF = '1d4dcf9a9e534249c67a5a24d1135b55e09c024a9aecd3d6a7b6aace0c0b5408'
PRIOR_EXACT_TYPE_STDOUT_SHA256 = 'c72212c31417e4aa9cab684fbb5d357c528f5157d3714fa61c1392f29c741a9b'
EXACT_TYPE_HEAD = '''import CompilerAudit.SourceBridge
namespace BridgeReview
open CompilerAudit CompilerAudit.SourceBridge
example {α W : Type} [DecidableEq α] [DecidableEq W]
    (lows : List α) (rank : α → Nat) (unrank : Nat → α) (N : Nat)
    (hlows : lows = (List.range N).map unrank) (hinv : ∀ o, o < N → rank (unrank o) = o)
    (sched : List Event)
    (hsched : List.Forall₂ (Matches SelectedData.replicaCount) (residualEvents sched)
      Selected.groups)
    (blocks : Key → Nat) (segs : List (Seg W)) (tail : Nat)
    (hbud : segs.map Seg.blocks =
      (sourceTrace lows SelectedData.replicaCount sched).map fun k => blocks (rename rank k))
    (hfresh : (segs.map Seg.wrapper).Nodup) :
    (sourceTrace lows SelectedData.replicaCount sched).map (rename rank) = Selected.word N ∧
    (sourceTrace lows SelectedData.replicaCount sched).toFinset.card = 28278 * N ∧
    (srcRetained (emitSrc segs tail)).card = 904896 * N ∧
    (srcRefs (emitSrc segs tail)).length = 1809792 * N + Result.blockTotal N blocks := by
  exact CompilerAudit.SourceBridge.selected_source_transport lows rank unrank N hlows hinv
    sched hsched blocks segs tail hbud hfresh
end BridgeReview
'''
# Expected type copied from the frozen baseline check.py.
BASE_CONTRACT = '''import CompilerAudit
example (N : Nat) (blocks : CompilerAudit.Key → Nat) :
    (CompilerAudit.Selected.word N).toFinset.card = 28278 * N ∧
    (CompilerAudit.Retention.retained (CompilerAudit.Result.program N blocks)).card = 904896 * N ∧
    (CompilerAudit.Retention.refs (CompilerAudit.Result.program N blocks)).length =
      1809792 * N + CompilerAudit.Result.blockTotal N blocks :=
  CompilerAudit.Result.selected_compiler_model N blocks
#print axioms CompilerAudit.Result.selected_compiler_model
'''
# Contract probes: (file, expectation, expected error line, diagnostic signature).
PROBES = [
    ('A1_ConcreteContract.lean', 'accept', None, None),
    ('R1_FreshnessRequired.lean', 'reject', 5, 'is false'),
    ('R2_WrongRetainedCoefficient.lean', 'reject', 19, 'ype mismatch'),
]
PROTECTED_MARKERS = ('.git', 'LOCAL-MANIFEST.json', 'EXPORT-MANIFEST.json')
PASS_THROUGH_ENV = ('SYSTEMROOT', 'SystemRoot', 'WINDIR', 'SystemDrive', 'TEMP', 'TMP', 'TMPDIR',
                    'HOME', 'USERPROFILE', 'LANG', 'LC_ALL')
AMBIGUOUS_PREFIXES = ('LEAN', 'LAKE', 'ELAN', 'GIT_', 'LD_', 'DYLD_')
EXE = '.exe' if os.name == 'nt' else ''


class CheckError(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise CheckError(message)


def digest(path):
    h = sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def is_within(path, parent):
    try:
        Path(path).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False


def strip_lean_comments(text):
    """Remove nested block comments (incl. doc comments) and line comments."""
    out, i, n, depth = [], 0, len(text), 0
    while i < n:
        if depth:
            if text.startswith('/-', i):
                depth, i = depth + 1, i + 2
            elif text.startswith('-/', i):
                depth, i = depth - 1, i + 2
            else:
                i += 1
        elif text.startswith('/-', i):
            depth, i = 1, i + 2
        elif text.startswith('--', i):
            j = text.find('\n', i)
            i = n if j < 0 else j
        elif text[i] == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == '\\' else 1
            need(j < n, 'unterminated string literal')
            out.append(text[i:j + 1])
            i = j + 1
        else:
            out.append(text[i])
            i += 1
    need(depth == 0, 'unterminated block comment')
    return ''.join(out)


def formal_digest(data):
    return sha256(strip_lean_comments(data.decode('utf-8')).encode('utf-8')).hexdigest()


def scan_forbidden(code, label):
    for token in FORBIDDEN_TOKENS:
        need(not re.search(r'(?<![A-Za-z0-9_.])' + re.escape(token) + r'(?![A-Za-z0-9_\'])', code),
             'forbidden token ' + token + ' in ' + label)
    need('#eval' not in code and '#exit' not in code, 'unchecked command in ' + label)


def bridge_inventory(code):
    names = re.findall(r'\b(?:theorem|lemma)\s+([^\s({\[:]+)', code)
    namespaces = re.findall(r'^namespace\s+(\S+)\s*$', code, re.M)
    need(namespaces == ['CompilerAudit.SourceBridge'], 'bridge must use one CompilerAudit.SourceBridge namespace')
    full = ['CompilerAudit.SourceBridge.' + n for n in names]
    need(len(full) == len(set(full)), 'duplicate theorem names in bridge source')
    need(sorted(full) == sorted(REQUIRED_NAMES), 'bridge theorem inventory differs from the fixed 27 names')
    return full


def exact_type_source(names=REQUIRED_NAMES):
    return EXACT_TYPE_HEAD + ''.join('#check %s\n#print axioms %s\n' % (n, n) for n in names)


AXIOM_LINE = re.compile(r"^'(.+)' (?:depends on axioms: \[([^\[\]]*)\]|(does not depend on any axioms))$")


def parse_axiom_report(text, required, allowed=ALLOWED_AXIOMS):
    """Fail-closed parser for `#print axioms` output.

    Identifiers may contain apostrophes, so the whole quoted span up to the final
    `' depends`/`' does not` is the name. Every report-like line must match.
    """
    need('warning:' not in text and 'error:' not in text, 'Lean warning or error in axiom report')
    need('sorry' not in text, 'sorry in axiom report')
    found = {}
    for raw in text.replace('\r\n', '\n').split('\n'):
        line = raw.rstrip()
        if 'depends on axioms' not in line and 'does not depend on any axioms' not in line:
            continue
        m = AXIOM_LINE.match(line)
        need(m is not None, 'malformed axiom report line: ' + line)
        name = m.group(1)
        need(name not in found, 'duplicate axiom report: ' + name)
        deps = [] if m.group(3) else [d.strip() for d in m.group(2).split(',')]
        need(all(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.\']*', d) for d in deps), 'malformed axiom list: ' + name)
        need(len(deps) == len(set(deps)), 'duplicate axiom in list: ' + name)
        foreign = sorted(set(deps) - set(allowed))
        need(not foreign, 'foreign axioms for ' + name + ': ' + ', '.join(foreign))
        found[name] = deps
    missing = sorted(set(required) - set(found))
    extra = sorted(set(found) - set(required))
    need(not missing, 'missing axiom reports: ' + ', '.join(missing))
    need(not extra, 'unexpected axiom reports: ' + ', '.join(extra))
    return found


def leanchecker_argv(checker, target=LEAF_MODULE):
    """The only permitted leanchecker invocation (flags verified in LeanChecker.lean).

    Bare runs, unknown flags (e.g. --help, silently dropped) or a prefix target
    would replay a whole project/library. leanchecker accepts module names only.
    """
    need(target == LEAF_MODULE, 'leanchecker target must be exactly ' + LEAF_MODULE)
    return [str(checker), '--verbose', target]


def check_leaf_output(returncode, stdout, stderr):
    need(returncode == 0, 'leanchecker returned %r' % (returncode,))
    lines = [l for l in stdout.replace('\r\n', '\n').split('\n') if l.strip()]
    need(lines == ['replaying ' + LEAF_MODULE], 'leanchecker replayed an unexpected module set: %r' % lines)
    need(not stderr.strip(), 'leanchecker wrote diagnostics')


def check_manifest(manifest_path):
    need(digest(manifest_path) == BASE_SHA256['lake-manifest.json'], 'lake-manifest.json differs from pin')
    manifest = json.loads(Path(manifest_path).read_bytes())
    rows = manifest.get('packages', [])
    names = [r.get('name') for r in rows]
    need(len(names) == len(set(names)) and set(names) == set(DEPENDENCIES), 'manifest must list exactly the nine pinned packages')
    for r in rows:
        rev, url, _ = DEPENDENCIES[r['name']]
        need(r.get('rev') == rev and r.get('url') == url and r.get('type') == 'git',
             'manifest pin mismatch: ' + r['name'])
    return [r['name'] for r in rows]


def validate_output(output, protected_roots):
    need(output.is_absolute(), '--output must be absolute')
    out = output.resolve()
    need(not out.exists(), '--output must not exist (fresh directory required)')
    for root in protected_roots:
        need(not is_within(out, root) and not is_within(root, out), '--output overlaps protected input: ' + str(root))
    for p in out.parents:
        for marker in PROTECTED_MARKERS:
            need(not (p / marker).exists(), 'protected output ancestor: ' + str(p / marker))
    return out


def validate_toolchain(root):
    root = root.resolve()
    lean, checker = root / 'bin' / ('lean' + EXE), root / 'bin' / ('leanchecker' + EXE)
    need(lean.is_file() and checker.is_file(), 'toolchain bin/lean and bin/leanchecker required')
    for b in (lean, checker):
        need(is_within(b, root), 'toolchain binary resolves outside toolchain root: ' + str(b))
    need((root / 'lib' / 'lean' / 'Init.olean').is_file() and (root / 'lib' / 'lean' / 'LeanChecker.olean').is_file(),
         'not a real toolchain root (lib/lean core missing; elan shim directory?)')
    need(digest(lean) != digest(checker), 'lean and leanchecker are byte-identical (elan shim proxies)')
    hashes = {}
    for d in (root / 'bin', root / 'lib' / 'lean'):
        for p in sorted(d.iterdir()) if d.is_dir() else []:
            if p.is_file() and (p.name in (lean.name, checker.name) or p.name.startswith(
                    ('libleanshared', 'libInit_shared', 'libLake_shared'))):
                hashes[p.relative_to(root).as_posix()] = digest(p)
    return lean.resolve(), checker.resolve(), hashes


def build_env(toolchain_bin, lean_path, base=None):
    base = os.environ if base is None else base
    env = {k: base[k] for k in PASS_THROUGH_ENV if k in base}
    env['PATH'] = str(toolchain_bin)
    env['LEAN_PATH'] = os.pathsep.join(map(str, lean_path))
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    dropped = sorted(k for k in base if k.upper().startswith(AMBIGUOUS_PREFIXES) or k.upper() == 'PATH')
    return env, dropped


def git_env(git, base=None):
    base = os.environ if base is None else base
    env = {k: base[k] for k in PASS_THROUGH_ENV if k in base}
    env.update(PATH=str(Path(git).parent), GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0',
               GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1', LC_ALL='C')
    return env


def check_dependency(git, path, name, env):
    """HEAD equals the pin; the checkout is its own repository; tracked files clean."""
    rev = DEPENDENCIES[name][0]
    def g(*a):
        p = subprocess.run([str(git), '--no-replace-objects', '-c', 'core.fsmonitor=false', '-C', str(path), *a],
                           env=env, capture_output=True, timeout=120, stdin=subprocess.DEVNULL)
        need(p.returncode == 0, 'git %s failed for %s: %s' % (a[0], name, p.stderr.decode(errors='replace').strip()))
        return p.stdout.decode('utf-8', errors='replace')
    need(path.is_dir(), 'missing package checkout: ' + name)
    top = g('rev-parse', '--show-toplevel').strip()
    need(os.path.normcase(str(Path(top).resolve())) == os.path.normcase(str(path.resolve())),
         'package is not its own git checkout: ' + name)
    head = g('rev-parse', 'HEAD').strip()
    need(head == rev, 'package %s at %s, pinned %s' % (name, head, rev))
    dirty = g('status', '--porcelain=v1', '--untracked-files=no')
    need(not dirty.strip(), 'tracked files modified in ' + name)
    untracked = [l for l in g('status', '--porcelain=v1', '--untracked-files=normal').splitlines() if l.startswith('??')]
    return dict(name=name, head=head, tracked_clean=True, untracked_nonignored_entries=len(untracked))


def top_level_names(lib):
    return {p.name.split('.', 1)[0] for p in lib.iterdir()}


def check_library_roots(packages, names):
    roots, seen = [], {}
    for name in names:
        lib = packages / name / '.lake' / 'build' / 'lib' / 'lean'
        if not DEPENDENCIES[name][2]:
            continue
        need(lib.is_dir(), 'missing cached library root: ' + name)
        tops = top_level_names(lib)
        clash = sorted(tops & RESERVED_TOP)
        need(not clash, 'library root %s shadows reserved modules: %s' % (name, clash))
        for t in tops:
            need(t not in seen, 'ambiguous top-level module %s in %s and %s' % (t, seen.get(t), name))
            seen[t] = name
        roots.append(lib.resolve())
    need(len(roots) == 8, 'exactly eight library roots required')
    return roots


def artifact_inventory(lib):
    h, count, size = sha256(), 0, 0
    for dirpath, dirnames, filenames in os.walk(lib):
        dirnames.sort()
        for f in sorted(filenames):
            if f.endswith('.olean'):
                p = Path(dirpath) / f
                st = p.stat()
                rel = p.relative_to(lib).as_posix()
                h.update(('%s\0%d\n' % (rel, st.st_size)).encode())
                count, size = count + 1, size + st.st_size
    return dict(olean_files=count, olean_bytes=size, path_size_inventory_sha256=h.hexdigest())


def check_lean_output(text, expect, line=None, signature=None):
    errors = re.findall(r':(\d+):\d+: error', text)
    if expect == 'accept':
        return not errors and 'error:' not in text and 'warning:' not in text
    return errors == [str(line)] and signature in text and 'warning:' not in text


class Runner:
    def __init__(self, out, env, timeout):
        self.out, self.env, self.timeout, self.records = out, env, timeout, []
        (out / 'logs').mkdir()

    def run(self, label, argv, cwd):
        so, se = self.out / 'logs' / (label + '.stdout'), self.out / 'logs' / (label + '.stderr')
        start, timed = time.monotonic(), False
        kw = dict(creationflags=subprocess.CREATE_NEW_PROCESS_GROUP) if os.name == 'nt' else dict(start_new_session=True)
        with open(so, 'wb') as fo, open(se, 'wb') as fe:
            p = subprocess.Popen([str(a) for a in argv], cwd=str(cwd), env=self.env, stdin=subprocess.DEVNULL,
                                 stdout=fo, stderr=fe, **kw)
            try:
                p.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                timed = True
                if os.name == 'nt':
                    tk = Path(os.environ.get('SYSTEMROOT', r'C:\Windows')) / 'System32' / 'taskkill.exe'
                    subprocess.run([str(tk), '/PID', str(p.pid), '/T', '/F'], capture_output=True, timeout=60)
                else:
                    os.killpg(p.pid, signal.SIGKILL)
                p.wait(timeout=60)
        stdout, stderr = so.read_bytes().decode('utf-8', 'replace'), se.read_bytes().decode('utf-8', 'replace')
        row = dict(label=label, argv=[str(a) for a in argv], cwd=str(cwd), returncode=p.returncode,
                   timed_out=timed, seconds=round(time.monotonic() - start, 3), timeout_seconds=self.timeout,
                   stdout_sha256=digest(so), stderr_sha256=digest(se))
        self.records.append(row)
        write_json(self.out / 'RUNS.json', self.records)
        need(not timed, 'timed out: ' + label)
        return row, stdout, stderr


def write_json(path, value):
    Path(path).write_bytes((json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode('utf-8'))


def source_pins(root):
    base, pkg = root / BASE_REL, root / PACKAGE_REL
    pins = {}
    for rel, want in BASE_SHA256.items():
        got = digest(base / rel)
        need(got == want, 'baseline file differs from pin: ' + rel)
        pins[(BASE_REL / rel).as_posix()] = got
    need((base / 'lean-toolchain').read_text().strip() == TOOLCHAIN_PIN, 'toolchain pin')
    data = (pkg / BRIDGE_REL).read_bytes()
    need(sha256(data).hexdigest() == BRIDGE_SHA256, 'candidate SourceBridge.lean differs from BRIDGE_SHA256')
    need(formal_digest(data) == BRIDGE_FORMAL_SHA256, 'bridge formal text differs from the checked proof')
    code = strip_lean_comments(data.decode('utf-8'))
    scan_forbidden(code, BRIDGE_REL)
    bridge_inventory(code)
    pins[(PACKAGE_REL / BRIDGE_REL).as_posix()] = BRIDGE_SHA256
    for f, *_ in PROBES:
        pins[(PACKAGE_REL / 'probes' / f).as_posix()] = digest(pkg / 'probes' / f)
    pins[(PACKAGE_REL / 'check.py').as_posix()] = digest(pkg / 'check.py')
    return pins


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--output', required=True, type=Path, help='fresh absolute directory outside all inputs')
    ap.add_argument('--toolchain', required=True, type=Path, help='real Lean 4.34.1 toolchain root (bin/, lib/lean/)')
    ap.add_argument('--packages', required=True, type=Path, help='directory with the nine pinned lake package checkouts')
    ap.add_argument('--root', type=Path, default=DEFAULT_ROOT, help='repository root (default: this checkout)')
    ap.add_argument('--git', default=shutil.which('git'), help='git executable used for read-only pin checks')
    ap.add_argument('--timeout', type=int, default=600, help='seconds per Lean command')
    ap.add_argument('--preflight-only', action='store_true', help='pin/environment checks only, no Lean execution')
    args = ap.parse_args(argv)
    need(1 <= args.timeout <= 600, '--timeout must be in 1..600 seconds')
    sys.dont_write_bytecode = True
    root, packages = args.root.resolve(), args.packages.resolve()
    need(args.git is not None and Path(args.git).is_file(), 'git executable required for dependency pin checks')
    need((root / PACKAGE_REL / BRIDGE_REL).is_file() and (root / BASE_REL).is_dir(), '--root is not the repository root')
    lean, checker, tool_hashes = validate_toolchain(args.toolchain)
    toolchain = args.toolchain.resolve()
    out = validate_output(args.output, [root, toolchain, packages, HERE])
    pins = source_pins(root)
    names = check_manifest(root / BASE_REL / 'lake-manifest.json')
    genv = git_env(args.git)
    deps = [check_dependency(args.git, packages / n, n, genv) for n in names]
    libs = check_library_roots(packages, names)
    lib_by_name = {p.parents[3].name: p for p in libs}
    for d in deps:
        d['library_root'] = str(lib_by_name[d['name']]) if d['name'] in lib_by_name else None
        d['role'] = 'library' if d['name'] in lib_by_name else 'tooling-only (not on LEAN_PATH)'
        if d['library_root']:
            d['cached_artifacts'] = artifact_inventory(lib_by_name[d['name']])
    exact_text = exact_type_source()
    need(sha256(exact_text.encode('utf-8')).hexdigest() == PRIOR_EXACT_TYPE_SHA256_LF, 'exact-type file drifted from prior review')

    out.mkdir(parents=True)
    build, work = out / 'build', out / 'work'
    build.mkdir()
    work.mkdir()
    lean_path = [build, *libs]
    env, dropped = build_env(lean.parent, lean_path)
    preflight = dict(
        utc=datetime.now(timezone.utc).isoformat(), python=sys.version, platform=sys.platform,
        root=str(root), toolchain_root=str(toolchain), packages_root=str(packages), output=str(out),
        lean=str(lean), leanchecker=str(checker), toolchain_sha256=tool_hashes,
        source_sha256=pins, bridge=dict(candidate_sha256=BRIDGE_SHA256, prior_checked_sha256=PRIOR_BRIDGE_SHA256,
                                        formal_text_sha256=BRIDGE_FORMAL_SHA256, formal_text_matches_prior=True),
        dependencies=deps, lean_path=[str(p) for p in lean_path],
        environment=dict(passed_through=sorted(k for k in env if k not in ('PATH', 'LEAN_PATH', 'PYTHONDONTWRITEBYTECODE')),
                         path=env['PATH'], inherited_ambiguous_variables_dropped=dropped),
        artifact_trust='Dependency checkouts are at pinned, clean revisions. Cached .olean binary-to-source correspondence remains trusted; no cold rebuild; inventory is path+size only.')
    write_json(out / 'PREFLIGHT.json', preflight)
    if args.preflight_only:
        print(json.dumps(dict(status='PREFLIGHT_ONLY_NO_LEAN_EXECUTED', output=str(out)), indent=2))
        return 0

    runner = Runner(out, env, args.timeout)
    row, so, se = runner.run('toolchain-version', [lean, '--version'], work)
    need(row['returncode'] == 0 and LEAN_VERSION in so and LEAN_COMMIT in so, 'wrong Lean compiler build')
    version = so.strip()

    base_dir, pkg_dir = root / BASE_REL, root / PACKAGE_REL
    expected = []
    for module, src_root in [(m, base_dir) for m in BASE_MODULES] + [(BRIDGE_MODULE, pkg_dir)]:
        rel = module.replace('.', '/')
        obj = build / (rel + '.olean')
        obj.parent.mkdir(parents=True, exist_ok=True)
        row, so, se = runner.run('compile-' + module.replace('.', '-'),
                                 [lean, *LEAN_FLAGS, '--root=' + str(src_root), '-o', obj, src_root / (rel + '.lean')], work)
        need(row['returncode'] == 0 and check_lean_output(so + se, 'accept') and obj.is_file(), 'compilation failed: ' + module)
        expected.append(rel + '.olean')
    built = sorted(p.relative_to(build).as_posix() for p in build.rglob('*') if p.is_file())
    need(built == sorted(expected), 'unexpected files in build root: %r' % built)
    olean_sha = {r: digest(build / r) for r in built}

    exact = work / 'ExactTypeAndAllAxioms.lean'
    exact.write_bytes(exact_text.encode('utf-8'))
    row, so, se = runner.run('exact-type-all-axioms', [lean, *LEAN_FLAGS, '--root=' + str(work), exact], work)
    need(row['returncode'] == 0, 'exact main type or axiom command failed')
    exact_stdout_sha = row['stdout_sha256']
    axioms = parse_axiom_report(so + se, REQUIRED_NAMES)

    contract = work / 'BaselineContract.lean'
    contract.write_bytes(BASE_CONTRACT.encode('utf-8'))
    row, so2, se2 = runner.run('baseline-main-contract', [lean, *LEAN_FLAGS, '--root=' + str(work), contract], work)
    need(row['returncode'] == 0, 'baseline main contract failed')
    base_axioms = parse_axiom_report(so2 + se2, [BASE_MAIN_THEOREM])

    row, so3, se3 = runner.run('leaf-kernel-replay', leanchecker_argv(checker), work)
    check_leaf_output(row['returncode'], so3, se3)

    probes = []
    for f, expect, line, sig in PROBES:
        src = pkg_dir / 'probes' / f
        scan_forbidden(strip_lean_comments(src.read_text(encoding='utf-8')), f)
        row, so4, se4 = runner.run('probe-' + Path(f).stem, [lean, *LEAN_FLAGS, '--root=' + str(src.parent), src], work)
        ok = (row['returncode'] == 0) == (expect == 'accept') and check_lean_output(so4 + se4, expect, line, sig)
        probes.append(dict(file=f, expect=expect, error_line=line, signature=sig, returncode=row['returncode'], as_expected=ok))
        need(ok, 'probe not as expected: ' + f)

    need(source_pins(root) == pins, 'sources changed during replay')
    need(digest(lean) == tool_hashes['bin/' + lean.name], 'toolchain changed during replay')
    result = dict(
        status='PASS_FRESH_SOURCE_BRIDGE_REPLAY', preflight=preflight, toolchain_version=version,
        fresh_build_olean_sha256=olean_sha, theorem_axioms=axioms, theorem_count=len(axioms),
        baseline_main_contract_axioms=base_axioms, probes=probes,
        exact_type_stdout_matches_prior_review_informational=exact_stdout_sha == PRIOR_EXACT_TYPE_STDOUT_SHA256,
        coverage=dict(
            baseline_modules_compiled_fresh=BASE_MODULES, bridge_compiled_fresh=BRIDGE_MODULE,
            stale_baseline_oleans_reused=False, single_build_root=str(build),
            exact_main_type_checked=MAIN_THEOREM, baseline_main_contract_type_checked=BASE_MAIN_THEOREM,
            axiom_inventory='exactly the fixed 27 bridge theorem names; allowed axioms propext/Classical.choice/Quot.sound',
            leanchecker=dict(argv=leanchecker_argv(checker), module=LEAF_MODULE, declaration_of_interest=MAIN_THEOREM,
                             scope='Replays every constant added by module CompilerAudit.SourceBridge (including all 27 theorems) '
                                   'into the environment imported from its oleans. leanchecker accepts module names only; '
                                   'a declaration name matches no olean and is rejected. Baseline modules and libraries are '
                                   'not replayed by leanchecker (baseline declarations were kernel-checked by the fresh compile).'),
            imported_libraries='trusted cached artifacts at pinned clean revisions; not cold rebuilt',
            not_covered='Python semantics, that the bridge hypotheses hold for the pinned sources, GL64 codec inverse, '
                        'CPython realizability, native/stock/precision or multiplication theorems.'),
        records=runner.records)
    write_json(out / 'RESULT.json', result)
    print(json.dumps(dict(status=result['status'], theorems=len(axioms), probes=len(probes), output=str(out)), indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except CheckError as e:
        print('CHECK FAILED: ' + str(e), file=sys.stderr)
        sys.exit(1)