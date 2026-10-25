# SPDX-License-Identifier: Apache-2.0
"""Scope C2: the five reject(name, test) controls of PR3633's owners/independent_literal.py (kept from PR3605's
adapted owner audit) cannot detect a disabled or weakened gate; the same holds in every located copy.

Static analysis only (ast); no code of PR3605, PR3624, PR3626, PR3630, PR3633, PR3638, PR3642 or PR3653 is imported
or executed.  The file
defines `need(v, m)` (raise iff not v) and `reject(name, test)`, which runs `need(not test(), ...)`: a control
"passes" iff its lambda returns a falsy value.  analyse(source, ctx) is the main check (positive run and every
negative control):
  controls.pin          sha256 of the source is the pinned value
  controls.need_def     need's body is exactly `if not v: raise ...` (no other effect)
  controls.reject_def   reject's body is exactly `need(not test(), msg); controls.append(name)`
  controls.bindings     need and reject are bound exactly once in the module, by those defs (no later rebinding)
  controls.gate_purity  no gate (a need(...) call outside a function) binds or mutates anything by name (lambda
                        bodies included): no assignment expression, mutating method, x.at(...), out=, or in-place
                        numpy function (copyto, put, place, putmask, ...); a module function called by a gate declares
                        no global/nonlocal and mutates only its own local names (never a parameter or module name)
  controls.inventory    the reject() calls are exactly the five inherited names, each with a lambda
  controls.tautology    every lambda (i) calls no module function and no need/reject, only pure builtins/numpy
                        constructors (so its value is the same whether or not any gate exists), and (ii) matches a
                        proof pattern showing it is False on every input that reaches it:
                          irreflexive    `a < a ...` (or >), identical side-effect-free operands on numbers: no value
                          duplicate_set  `len({int(e), int(e)}) == 2`: a one-element set, for every input
                          shifted_column `array_equal(r_[X[0,k], X[:u,k]], tile(arange(M), N))`, M >= 2, X a matrix,
                                         no step: entries 0 and 1 of the first array are both X[0,k], of the second 0
                                         and 1 (or the lengths differ); for every X, u and N
                          gate_offset    `int(A[I[0]]) + d == int(B[0])`, d != 0, after an unconditional earlier gate
                                         `need(array_equal(A[I], B))`, I last bound by np.lexsort/np.argsort (an integer
                                         index array, so A[I][0] == A[I[0]])
                          gate_bump      `dict(H) == bad` with `bad = dict(P); bad[k] += d` (d != 0) after an
                                         unconditional earlier gate asserting `dict(H) == P` (a conjunct of an `and`)
                        For the two gate patterns, every statement strictly between the premise gate and the control,
                        other than reject() calls and the `bad` pair, references none of the premise names, calls no
                        module function except need, and mutates only objects built fresh inside the region (region
                        rule).
                        Verdicts when no proof is accepted (all raise controls.tautology): 'genuine' = the lambda calls
                        a gate's module function on arguments that differ syntactically from every gate call of it
                        (it feeds changed data to the gate predicate); 'gate-coupled' = it calls need/reject or a
                        module function, but only as the gates do (not certified either way); 'unproven' = no pattern.
  controls.pattern      each control is proved by the pattern expected for its name
  controls.data_*       (PR3633 file, when journal rows are given) the premises the proofs rely on, evaluated in pure
                        Python on the actual T488 values: data_pin (rows bound to PR3633 EXPECTED.json payload_sha256
                        20662cc6... by compact re-serialisation; ORDER/DISPATCH rebuilt from the pinned base
                        chronologies and bound to EXPECTED literal_files; PROVIDERS.json and the profile from PR3633's
                        head; TEMPLATE/PLAN from main), data_rows, data_identity (rows are the ordered helper
                        identities), data_window (row 0's time is inside its own source window), data_prefix (the
                        first bin's offsets are prefix sums of the provider widths), data_mass (the profile mass is
                        65088 x 488).  The predicate values are reported but carry no data content: three are
                        data-independent by their pattern, and the hole and rank1 values are reduced forms fixed by
                        the premises (H itself is not recomputed here; that is the literal-owner audit's scope).
Fairness: the gates themselves are real checks evaluated on the real data; this is a control-coverage defect (the five
controls never feed changed data to any gate, so they would also pass with that gate deleted), not evidence that the
owner journal is wrong.  The copies of the same controls in PR3605/PR3624/PR3626/PR3630/PR3633 are located (every
.py blob of main and the eight PR heads containing the control text), pinned and analysed structurally with the same
function; the cited original (SHA256 1001cb1c...) is searched among all those .py blobs by sha256.
Not mutation-controlled (fail-closed reads that must pass on the pinned bytes): controls.git, the input pins
(show_pinned, ORDER/DISPATCH/PROVIDERS/FILL file pins in build_t488/read_local_fill) and the located-copies set
(controls.copies).  The journal-payload pin and every analyser rule have negative controls.
Model and limits: names are tracked syntactically; mutation is recognised through stores, augmented assignments,
the MUTATING method names, x.at(...), out= and INPLACE_NP.  shortcut: a library call that mutates an argument outside
those lists (np.random.shuffle, setattr, ...), or mutation of a mutable element shared into a fresh container, is
not recognised; neither occurs in the located files (by inspection: their regions mutate only used, idle, H, controls
and bad), upgrade to a callee whitelist if this analyser is applied to other files.  Standard library only.
"""
import ast
import gzip
import json
import os
import re
import subprocess
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_VENDOR = os.path.join(_HERE, 'vendor', 'pr3053')
if _VENDOR not in sys.path:
    sys.path.insert(0, _VENDOR)
import audit_common as AC   # noqa: E402
import audit_lib as AL      # noqa: E402

REPO = os.path.dirname(os.path.dirname(_HERE))
SCRATCH_OWNERS = os.path.join(REPO, '.loop-scratch', 'iter22', 't488-owners')
MAIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
COMMITS = dict(PR3605='3efbb5de06a49ffeea6684482f2d3fe48cdca3fb', PR3624='515a7c4490aa32ac3ca5014feb6f7da0d6952863',
               PR3626='659fd5e7064d9466b668d7188cbb013b333a415a', PR3630='bcac7fe04b9b7f7f5d3c27d620561f96c4ae5608',
               PR3633='72c268f113368ea0387d188225e3f81ba6d6ef73', PR3638='d62e1acd7518a231440383f0d0dddf54d6edf8c1',
               PR3642='044d24f12e74f228dd462c07ae2d7f3ea35e2be9', PR3653='607a09ff441c79b215a8127a81f4cc70021d0d9b')
ORIGINAL_SHA256 = '1001cb1c8b4ee1f93c23b58b094565ec1b3931eee0ea091a23504696e380be9e'
P605 = ('5d1a7b4fd635070522e78656ccedf9bcf4bf13db', 'da897bd5cef36943b3f5b1422fe81716b4eaa6230b056d31f8c2310cf62f8580')
# label -> (pr, path, git blob, sha256)
TARGET = ('PR3633', 'research/staged-width-t488/owners/independent_literal.py',
          'e2a226950ed30e88f6c386669716b9a463dd873d', '8517c0d6c7cbe73438885135ac7fd9781dd5120113c9721002346dca603f5ed9')
COPIES = {
    'PR3605': ('PR3605', 'research/staged-644-660-conditional-release/owners/independent_literal.py') + P605,
    'PR3624': ('PR3624', 'research/staged-width-t450/owners/independent_literal.py',
               'd9c2450e03d9dcde39ae96f0edc835d1a67d9fe5', '68684584d3866b2ab76c254dd6d5be3a49d276a6e5f6353183dee4d8d84de4d4'),
    'PR3624-provenance': ('PR3624', 'research/staged-width-t450/provenance/pr3605/owners/independent_literal.py') + P605,
    'PR3626': ('PR3626', 'research/staged-width-t530/owners/independent_literal.py',
               '32755776c15660b939c92cb8835c71ec87c8c1d6', '36d7f4e3a611fd6b5983222887beb9a37a18bfac0d999ac5c00e3e191d1c5cc4'),
    'PR3626-provenance': ('PR3626', 'research/staged-width-t530/provenance/pr3605/owners/independent_literal.py') + P605,
    'PR3630': ('PR3630', 'research/staged-644-660-owner-successor/independent_owners.py',
               'f116cc0142b4f6d674abf6e4c844142c00fb0297', '8d02dff267938cdb373aa617a411d8e67700e130609d2714e98ccf814e32eaef'),
    'PR3633': TARGET,
    'PR3633-provenance': ('PR3633', 'research/staged-width-t488/provenance/pr3605/owners/independent_literal.py') + P605,
    'PR3638': ('PR3638', 'research/three-kappa-leads/independent_literal.py',
               '4028493716bfcf3e73831067599518c055fcd2b0', '89c27f61ae3e6d2bdd4c469ac5b99d4f955a443c5e04c74e568c12093510efbe'),
    'PR3642': ('PR3642', 'research/staged-release-retiming-t530/owner-audit/independent_literal.py',
               '86dc50768ff3fda8e265c08aa9314fe072e0c396', 'b51c36ad1ae0999547edc4726d698df369fef60daaaac4f5bbea471648c9f628'),
    'PR3642-upstream': ('PR3642', 'research/staged-release-retiming-t530/owner-audit/upstream/independent_literal.py',
                        '32755776c15660b939c92cb8835c71ec87c8c1d6',
                        '36d7f4e3a611fd6b5983222887beb9a37a18bfac0d999ac5c00e3e191d1c5cc4'),
    'PR3642-vendor': ('PR3642', 'research/staged-release-retiming-t530/full-admission/vendor/staged-width-t530/owners/'
                      'independent_literal.py', '32755776c15660b939c92cb8835c71ec87c8c1d6',
                      '36d7f4e3a611fd6b5983222887beb9a37a18bfac0d999ac5c00e3e191d1c5cc4'),
    'PR3653': ('PR3653', 'research/retimed-t488-composition/owners/independent_literal.py',
               '403a9cd104c7e68a5bd2431bb442d701f30828f5', 'caa5eb4fff4908c0891c3ee41e7e6d71bf19bb710d1d7781164f10ce84bce769'),
    'PR3653-upstream': ('PR3653', 'research/retimed-t488-composition/owners/upstream/independent_literal.py') + TARGET[2:],
    'PR3653-vendor': ('PR3653', 'research/retimed-t488-composition/full-replay/vendor/pr3642/vendor/staged-width-t530/'
                      'owners/independent_literal.py', '32755776c15660b939c92cb8835c71ec87c8c1d6',
                      '36d7f4e3a611fd6b5983222887beb9a37a18bfac0d999ac5c00e3e191d1c5cc4'),
}
EXPECTED_JSON = ('PR3633', 'research/staged-width-t488/owners/EXPECTED.json', '415eac1a2b0201beac2c3e531c6fcbd1133a819f',
                 '924493b6bbeade055af4916ac7bd6d7d7ec0600719f5c39636dc3f16d7ec14ea')
TEMPLATE = (MAIN, 'research/rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz',
            '114808c32b1799da53524bdc25cea67efb60009e', '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e')
PLAN = (MAIN, 'research/rank7-joint-endframes/allocation/vendor/PLAN.json.gz',
        '7a1db55a4d53ee99280be4f3ab7d29f7b2033adf', 'd566cfb87b71639d4138e1f89b543e2dd6a7772070226a2a14c799a6835bf21e')
NAMES = ('duplicate helper', 'strict lower endpoint used as available', 'same-call family reused',
         'unpaid chronological hole', 'one unpaid rank1 child')
PATTERN_OF = dict(zip(NAMES, ('shifted_column', 'irreflexive', 'duplicate_set', 'gate_offset', 'gate_bump')))
PURE_CALLS = {'np.array_equal', 'np.tile', 'np.arange', 'bool', 'len', 'int', 'dict'}
FRESH = {'np.zeros', 'np.ones', 'np.empty', 'np.full', 'np.repeat', 'Counter', 'dict', 'list', 'set'}
INPLACE_NP = {'np.copyto', 'np.put', 'np.place', 'np.putmask', 'np.fill_diagonal', 'np.put_along_axis'}
CONTROL_TEXT = b'strict lower endpoint used as available'
MUTATING = {'append', 'extend', 'insert', 'pop', 'remove', 'clear', 'sort', 'reverse', 'update', 'setdefault',
            'popitem', 'add', 'discard', 'fill', 'resize', 'put', 'itemset', 'partition', 'write_text', 'write_bytes'}
COLUMNS = ['time', 'helper', 'owner_replica', 'child', 'port', 'offset']
# PR3633 owners/ base chronology files (name, git blob, sha256)
BASE_ORDERS = (('ORDER37.json', '411004ab280d6468bdd9c98c01f153baed66c543',
                '94803d190b2b0506d9645e980b57cdbc3e98221f3b615292df8a94f1b174c984'),
               ('T8-ORDER.json', 'b013bdb989f7fde1b8a22ae8ed743eae3a0a62fd',
                'a1abf78fb3b88bbf4656e6ae26f148a007f744f0be4c00d480fb2424ce8766d6'),
               ('T16-ORDER.json', '470b8afb8af03fd053b6ff19bc90eb410b5c9e6b',
                '9b2106c84aed23a7c3c8b99e21d3e96c66b12f92980a42ab2f6dbbe7831ef7c4'))
BASE_DISPATCH = (('DISPATCH37.json', 'c4c016ea3f3cb7bd04c1812259246a9411ad7adc',
                  '4f78935b2ef1f6c08c9c16433d54015def1eccd767443b496a77ea8823690df6'),
                 ('T8-DISPATCH.json', 'f95b6f07bf4d9e607a7ab8fcc101cdc63a725b07',
                  '23877abbe8ec258eb1f2425137f9171d37b1a4414a25595abe75eb0738850a24'),
                 ('T16-DISPATCH.json', '40725d2abb328ba7fee1c4f74656eecd982f2f7e',
                  '282960b7163bc305675b64d1d0faee9f71b18848748326418a013626944c6488'))
PROVIDERS_PIN = ('f321d4185339244b8b004326af70e653e611d84a',
                 'd96f2798024ab83edbb8848b62c425992aec182f1f24ef46bb8286dd390618c2')


# ------------------------------------------------------------------------------------------------- inputs ---
def git(*args, **kw):
    p = subprocess.run(['git', '-C', REPO] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=AC.git_env(), **kw)
    AC.need(p.returncode == 0, 'controls.git: git %s failed: %s' % (' '.join(args)[:120], p.stderr.decode()[:200]))
    return p.stdout


def show_pinned(commit, path, blob, sha):
    data = git('show', '%s:%s' % (commit, path))
    AC.need(AC.git_blob_id(data) == blob and AC.sha256(data) == sha, 'controls.pin: %s:%s is not blob %s / sha256 %s'
            % (commit[:12], path, blob[:12], sha[:12]))
    return data


def spec_bytes(spec):
    pr, path, blob, sha = spec
    return show_pinned(COMMITS[pr], path, blob, sha)


def scan_trees():
    """Every .py blob in the trees of main and the eight PR heads (git ls-tree -r, read back with git cat-file --batch and
    re-hashed): the ones containing the control text, with blob id and sha256, must equal the pinned COPIES table;
    also returns the blobs whose sha256 is the cited original's and the number of .py blobs scanned."""
    blobs = {}
    for label, commit in [('main', MAIN)] + sorted(COMMITS.items()):
        for ent in git('ls-tree', '-r', '-z', commit).split(b'\0'):
            if ent:
                meta, path = ent.split(b'\t', 1)
                _, typ, oid = meta.split()
                if typ == b'blob' and path.endswith(b'.py'):
                    blobs.setdefault(oid.decode(), []).append((label, commit, path.decode('utf-8')))
    data = git('cat-file', '--batch', input=('\n'.join(blobs) + '\n').encode())
    found, original, i = {}, [], 0
    for oid, where in blobs.items():
        nl = data.index(b'\n', i)
        hdr = data[i:nl].split()
        n = int(hdr[2])
        body = data[nl + 1:nl + 1 + n]
        i = nl + 2 + n
        AC.need(hdr[0].decode() == oid and AC.git_blob_id(body) == oid, 'controls.git: cat-file returned %r for %s'
                % (hdr[:2], oid))
        sha = AC.sha256(body)
        if sha == ORIGINAL_SHA256:
            original += ['%s:%s' % (label, path) for label, _, path in where]
        if CONTROL_TEXT in body:
            for label, commit, path in where:
                found['%s:%s' % (label, path)] = dict(commit=commit, git_blob=oid, sha256=sha)
    AC.need(i == len(data), 'controls.git: trailing cat-file output')
    want = dict(('%s:%s' % (pr, path), (blob, sha)) for pr, path, blob, sha in COPIES.values())
    got = dict((k, (v['git_blob'], v['sha256'])) for k, v in found.items())
    AC.need(got == want, 'controls.copies: located copies %r != pinned %r' % (sorted(got), sorted(want)))
    return found, original, len(blobs)


# ------------------------------------------------------------------------------------------- ast helpers ---
def dump(node):
    return ast.dump(node, annotate_fields=False)


def callee(call):
    return dotted(call.func)


def dotted(f):
    parts = []
    while isinstance(f, ast.Attribute):
        parts.append(f.attr)
        f = f.value
    if isinstance(f, ast.Name):
        return '.'.join([f.id] + parts[::-1])
    return None


def is_call(node, name, nargs=None):
    return isinstance(node, ast.Call) and callee(node) == name and not node.keywords and \
        (nargs is None or len(node.args) == nargs)


def is_const(node, pred=lambda v: True):
    return isinstance(node, ast.Constant) and not isinstance(node.value, bool) and pred(node.value)


def int_value(node):
    """The int of a literal like 5 or -1 (parsed as USub(5)), else None."""
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) and is_const(node.operand, lambda v: isinstance(v, int)):
        return -node.operand.value
    return node.value if is_const(node, lambda v: isinstance(v, int)) else None


def side_effect_free(node):
    """Names, constants, subscripts, slices, tuples and arithmetic/unary operators only (no call, no walrus)."""
    ok = (ast.Name, ast.Constant, ast.Subscript, ast.Slice, ast.Tuple, ast.Load, ast.UnaryOp, ast.USub, ast.BinOp,
          ast.Add, ast.Sub, ast.Mult)
    return all(isinstance(n, ok) for n in ast.walk(node))


def names_in(node):
    return set(n.id for n in ast.walk(node) if isinstance(n, ast.Name))


def bound_names(node):
    """Names (re)bound, or whose object is mutated, by a statement or expression (names are syntactic, see the module
    docstring): targets of assignments, augmented assignments (in place for numpy), for loops, walrus, with, del
    (a Subscript/Attribute target counts its base names), receivers of MUTATING methods, the first argument of x.at(...)
    and of the in-place numpy functions INPLACE_NP, and out= arguments."""
    out = set()
    for n in ast.walk(node):
        targets = []
        if isinstance(n, (ast.Assign, ast.Delete)):
            targets = n.targets
        elif isinstance(n, (ast.AugAssign, ast.AnnAssign, ast.For, ast.NamedExpr)):
            targets = [n.target]
        elif isinstance(n, ast.withitem) and n.optional_vars is not None:
            targets = [n.optional_vars]
        for t in targets:
            out |= names_in(t)
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Attribute) and n.func.attr in MUTATING:
                out |= names_in(n.func.value)
            if n.args and ((isinstance(n.func, ast.Attribute) and n.func.attr == 'at') or callee(n) in INPLACE_NP):
                out |= names_in(n.args[0])
            for kw in n.keywords:
                if kw.arg == 'out':
                    out |= names_in(kw.value)
    return out


def binding_sites(tree, name):
    """Every node of the module that binds `name`: def/class, a Name store/del, an import alias, global/nonlocal."""
    out = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == name:
            out.append(n)
        elif isinstance(n, ast.Name) and n.id == name and not isinstance(n.ctx, ast.Load):
            out.append(n)
        elif isinstance(n, ast.alias) and (n.asname or n.name.split('.')[0]) == name:
            out.append(n)
        elif isinstance(n, (ast.Global, ast.Nonlocal)) and name in n.names:
            out.append(n)
    return out


def need_calls(stmt):
    """need(...) calls in a module statement (functions and lambdas excluded)."""
    out = []

    def walk(n):
        if isinstance(n, (ast.FunctionDef, ast.Lambda)):
            return
        if is_call(n, 'need'):
            out.append(n)
        for ch in ast.iter_child_nodes(n):
            walk(ch)
    walk(stmt)
    return out


# --------------------------------------------------------------------------------------- the main check ---
def check_defs(tree):
    funcs = dict((n.name, n) for n in tree.body if isinstance(n, ast.FunctionDef))
    nd = funcs.get('need')
    AC.need(nd is not None and [a.arg for a in nd.args.args] == ['v', 'm'] and len(nd.body) == 1
            and isinstance(nd.body[0], ast.If) and not nd.body[0].orelse and len(nd.body[0].body) == 1
            and isinstance(nd.body[0].body[0], ast.Raise)
            and dump(nd.body[0].test) == dump(ast.UnaryOp(ast.Not(), ast.Name('v', ast.Load()))),
            'controls.need_def: need is not exactly "if not v: raise"')
    rj = funcs.get('reject')
    ok = rj is not None and [a.arg for a in rj.args.args] == ['name', 'test'] and len(rj.body) == 2
    if ok:
        s1, s2 = rj.body
        ok = isinstance(s1, ast.Expr) and is_call(s1.value, 'need', 2) and \
            dump(s1.value.args[0]) == dump(ast.UnaryOp(ast.Not(), ast.Call(ast.Name('test', ast.Load()), [], []))) and \
            isinstance(s2, ast.Expr) and is_call(s2.value, 'controls.append', 1) and \
            dump(s2.value.args[0]) == dump(ast.Name('name', ast.Load()))
    AC.need(ok, 'controls.reject_def: reject is not exactly "need(not test(), msg); controls.append(name)"')
    for f in ('need', 'reject'):
        sites = binding_sites(tree, f)
        AC.need(sites == [funcs[f]], 'controls.bindings: %s is bound %d times (lines %r), not only by its def'
                % (f, len(sites), [getattr(x, 'lineno', None) for x in sites]))
    return funcs


def gates_of(tree):
    """[(statement index, unconditional?, need call, message text)] for every module-level gate."""
    out = []
    for i, st in enumerate(tree.body):
        for call in need_calls(st):
            msg = call.args[1] if len(call.args) > 1 else None
            text = msg.value if is_const(msg) else (ast.unparse(msg) if msg is not None else '')
            out.append((i, isinstance(st, ast.Expr) and st.value is call, call, text))
    return out


def gate_purity(gates, funcs):
    called = set()
    for i, _, call, text in gates:
        called |= set(callee(n) for n in ast.walk(call) if isinstance(n, ast.Call)) & set(funcs)
        AC.need(not bound_names(call), 'controls.gate_purity: gate %r binds or mutates %r' % (text, sorted(bound_names(call))))
    for f in sorted(called - {'need'}):
        fn = funcs[f]
        params = set(a.arg for a in fn.args.args)
        local = set(n.id for n in ast.walk(fn) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)) - params
        AC.need(not any(isinstance(n, (ast.Global, ast.Nonlocal)) for n in ast.walk(fn))
                and bound_names(fn) <= local,
                'controls.gate_purity: gate function %s declares global/nonlocal or mutates a parameter or a module-level '
                'name (%r)'
                % (f, sorted(bound_names(fn) - local)))


def find_controls(tree):
    out = []
    for i, st in enumerate(tree.body):
        if isinstance(st, ast.Expr) and is_call(st.value, 'reject'):
            c = st.value
            AC.need(len(c.args) == 2 and is_const(c.args[0], lambda v: isinstance(v, str))
                    and isinstance(c.args[1], ast.Lambda) and not c.args[1].args.args,
                    'controls.inventory: reject call at statement %d is not reject("name", lambda: ...)' % i)
            out.append((i, c.args[0].value, c.args[1]))
        else:
            AC.need(not any(is_call(n, 'reject') for n in ast.walk(st)), 'controls.inventory: nested reject call')
    AC.need(tuple(n for _, n, _ in out) == NAMES, 'controls.inventory: %r != %r' % ([n for _, n, _ in out], NAMES))
    return out


class Unproven(Exception):
    pass


def region_clear(tree, funcs, lo, hi, names, allowed=()):
    """Region rule: every statement strictly between lo and hi, other than reject() calls and `allowed`, references
    none of `names`, calls no module function except need, and mutates (bound_names other than a plain `name = ...`)
    only names bound earlier in the region to a fresh object (a FRESH constructor call or a list/dict/set display), so
    a view or alias of a premise object bound before the gate cannot be mutated by name."""
    fresh = set()
    for j in range(lo + 1, hi):
        st = tree.body[j]
        if j in allowed or (isinstance(st, ast.Expr) and is_call(st.value, 'reject')):
            continue
        hit = names_in(st) & set(names)
        if hit:
            raise Unproven('statement %d between the premise gate and the control references %r' % (j, sorted(hit)))
        calls = set(callee(n) for n in ast.walk(st) if isinstance(n, ast.Call)) & (set(funcs) - {'need'})
        if calls:
            raise Unproven('statement %d between the premise gate and the control calls module function(s) %r'
                           % (j, sorted(calls)))
        plain = isinstance(st, ast.Assign) and all(isinstance(t, ast.Name) for t in st.targets)
        mutated = bound_names(st) - (set(t.id for t in st.targets) if plain else set())
        if mutated - fresh:
            raise Unproven('statement %d between the premise gate and the control mutates %r, not built fresh in the '
                           'region' % (j, sorted(mutated - fresh)))
        if plain:
            new = isinstance(st.value, (ast.List, ast.Dict, ast.Set)) or (isinstance(st.value, ast.Call)
                                                                          and callee(st.value) in FRESH)
            for t in st.targets:
                (fresh.add if new else fresh.discard)(t.id)


def premise_gate(tree, gates, at, test):
    """The latest unconditional gate before statement `at` whose test satisfies test(expr)."""
    for i, uncond, call, text in reversed(gates):
        if i < at and uncond and test(call.args[0]):
            return i, text
    raise Unproven('no unconditional earlier gate supplies the premise')


def prove(tree, funcs, gates, at, body):
    """(pattern, premise gate message or None, data-independent?, argument) or raise Unproven."""
    e = body.args[0] if is_call(body, 'bool', 1) else body
    # irreflexive
    if isinstance(e, ast.Compare) and isinstance(e.ops[0], (ast.Lt, ast.Gt)) and dump(e.left) == dump(e.comparators[0]) \
            and side_effect_free(e.left):
        return ('irreflexive', None, True, 'first conjunct is %s %s itself: false for every value'
                % (ast.unparse(e.left), '<' if isinstance(e.ops[0], ast.Lt) else '>'))
    if isinstance(e, ast.Compare) and len(e.ops) == 1 and isinstance(e.ops[0], ast.Eq):
        L, R = e.left, e.comparators[0]
        # duplicate_set
        if is_call(L, 'len', 1) and isinstance(L.args[0], ast.Set) and len(L.args[0].elts) == 2 \
                and is_const(R, lambda v: v == 2):
            a, b = L.args[0].elts
            if dump(a) == dump(b) and is_call(a, 'int', 1) and side_effect_free(a.args[0]):
                return ('duplicate_set', None, True, '{%s, same} has one element for every input, so len != 2'
                        % ast.unparse(a))
    if is_call(e, 'np.array_equal', 2):
        A, B = e.args
        if isinstance(A, ast.Subscript) and dotted(A.value) == 'np.r_' \
                and isinstance(A.slice, ast.Tuple) and len(A.slice.elts) == 2 and is_call(B, 'np.tile', 2) \
                and is_call(B.args[0], 'np.arange', 1) and is_const(B.args[0].args[0], lambda v: isinstance(v, int) and v >= 2):
            first, rest = A.slice.elts
            # the slice's upper bound is free: X[:u,k] starts with X[0,k] for every u (or is empty, lengths differ)
            if isinstance(first, ast.Subscript) and isinstance(rest, ast.Subscript) and dump(first.value) == dump(rest.value) \
                    and isinstance(first.slice, ast.Tuple) and isinstance(rest.slice, ast.Tuple) \
                    and len(first.slice.elts) == len(rest.slice.elts) == 2 and is_const(first.slice.elts[0], lambda v: v == 0) \
                    and isinstance(rest.slice.elts[0], ast.Slice) and rest.slice.elts[0].lower is None \
                    and rest.slice.elts[0].step is None and dump(first.slice.elts[1]) == dump(rest.slice.elts[1]) \
                    and side_effect_free(A.slice):
                return ('shifted_column', None, True, 'entries 0 and 1 of the first array are both %s, of tile(arange(%d))'
                        ' are 0 and 1: never equal' % (ast.unparse(first), B.args[0].args[0].value))
    if isinstance(e, ast.Compare) and len(e.ops) == 1 and isinstance(e.ops[0], ast.Eq):
        L, R = e.left, e.comparators[0]
        # gate_offset: int(A[I[0]]) + d == int(B[0])
        if isinstance(L, ast.BinOp) and isinstance(L.op, ast.Add) and is_const(L.right, lambda v: isinstance(v, int) and v)\
                and is_call(L.left, 'int', 1) and is_call(R, 'int', 1):
            x, y = L.left.args[0], R.args[0]
            if isinstance(x, ast.Subscript) and isinstance(x.slice, ast.Subscript) and is_const(x.slice.slice, lambda v: v == 0) \
                    and isinstance(y, ast.Subscript) and is_const(y.slice, lambda v: v == 0) \
                    and side_effect_free(ast.Tuple([x, y], ast.Load())):
                Ad, Id, Bd = dump(x.value), dump(x.slice.value), dump(y.value)

                def gate_test(t):
                    return is_call(t, 'np.array_equal', 2) and isinstance(t.args[0], ast.Subscript) \
                        and dump(t.args[0].value) == Ad and dump(t.args[0].slice) == Id and dump(t.args[1]) == Bd
                gi, text = premise_gate(tree, gates, at, gate_test)
                I = x.slice.value
                last = [st for st in tree.body[:gi] if isinstance(I, ast.Name) and I.id in bound_names(st)][-1:]
                if not (last and isinstance(last[0], ast.Assign) and len(last[0].targets) == 1
                        and dump(last[0].targets[0]) == dump(ast.Name(I.id, ast.Store()))
                        and isinstance(last[0].value, ast.Call) and callee(last[0].value) in ('np.lexsort', 'np.argsort')):
                    raise Unproven('index %s is not last bound by np.lexsort/np.argsort before the gate' % ast.unparse(I))
                region_clear(tree, funcs, gi, at, names_in(x) | names_in(y))
                return ('gate_offset', text, False, 'gate gives %s == %s, so the predicate is v + %d == v'
                        % (ast.unparse(x), ast.unparse(y), L.right.value))
        # gate_bump: dict(H) == bad, bad = dict(P); bad[k] += d
        if is_call(L, 'dict', 1) and isinstance(L.args[0], ast.Name) and isinstance(R, ast.Name):
            H, bad = L.args[0].id, R.id
            stmts = tree.body[:at]
            asg = [j for j, s in enumerate(stmts) if bad in bound_names(s)]
            if len(asg) >= 2:   # a third binding of bad after asg[0] is rejected by the region rule below
                s1, s2 = stmts[asg[0]], stmts[asg[1]]
                if isinstance(s1, ast.Assign) and len(s1.targets) == 1 and dump(s1.targets[0]) == dump(ast.Name(bad, ast.Store())) \
                        and is_call(s1.value, 'dict', 1) and isinstance(s1.value.args[0], ast.Name) \
                        and isinstance(s2, ast.AugAssign) and isinstance(s2.op, ast.Add) \
                        and isinstance(s2.target, ast.Subscript) and dump(s2.target.value) == dump(ast.Name(bad, ast.Load())) \
                        and is_const(s2.target.slice) and is_const(s2.value, lambda v: isinstance(v, int) and v):
                    P = s1.value.args[0].id
                    want = dump(ast.Compare(ast.Call(ast.Name('dict', ast.Load()), [ast.Name(H, ast.Load())], []),
                                            [ast.Eq()], [ast.Name(P, ast.Load())]))

                    def gate_test(t):
                        parts = t.values if isinstance(t, ast.BoolOp) and isinstance(t.op, ast.And) else [t]
                        return any(dump(p) == want for p in parts)
                    gi, text = premise_gate(tree, gates, asg[0], gate_test)
                    region_clear(tree, funcs, gi, at, {H, P}, allowed=set(asg))
                    region_clear(tree, funcs, asg[0], at, {bad}, allowed={asg[1]})
                    return ('gate_bump', text, False, 'gate gives dict(%s) == %s and %s differs from %s at key %r'
                            % (H, P, bad, P, s2.target.slice.value))
    raise Unproven('no proof pattern matches')


def args_key(call):
    return dump(ast.Tuple(list(call.args), ast.Load())) + repr([(k.arg, dump(k.value)) for k in call.keywords])


def classify(tree, funcs, gates, at, name, lam):
    gate_args = {}   # module function (need excluded) -> argument dumps of its calls inside gates
    for _, _, call, _ in gates:
        for n in ast.walk(call):
            if isinstance(n, ast.Call) and callee(n) in set(funcs) - {'need'}:
                gate_args.setdefault(callee(n), set()).add(args_key(n))
    lam_calls = [n for n in ast.walk(lam.body) if isinstance(n, ast.Call)]
    calls = sorted(set(callee(n) for n in lam_calls))

    def fail(verdict, why):
        e = AC.AuditFail('controls.tautology: control %r is %s: %s' % (name, verdict, why))
        e.verdict = verdict
        raise e
    changed = sorted(set(callee(n) for n in lam_calls if callee(n) in gate_args and args_key(n) not in gate_args[callee(n)]))
    if changed:
        fail('genuine', 'calls gate function(s) %r on arguments that differ from every gate call' % changed)
    coupled = [f for f in calls if f in funcs or f in ('need', 'reject')]
    if coupled:
        fail('gate-coupled', 'calls module function(s) %r, only on the gates\' own arguments' % coupled)
    other = [f for f in calls if f not in PURE_CALLS]
    if other:
        fail('unproven', 'calls %r outside the pure builtin/numpy constructors' % other)
    for n in ast.walk(lam.body):
        if isinstance(n, ast.NamedExpr):
            fail('unproven', 'assignment expression in the lambda')
    try:
        pattern, premise, independent, argument = prove(tree, funcs, gates, at, lam.body)
    except Unproven as u:
        fail('unproven', str(u))
    return dict(name=name, source=None, pattern=pattern, premise_gate=premise, data_independent=independent,
                argument=argument, calls=calls, free_names=sorted(names_in(lam.body) - {'np'}),
                calls_a_gate=False, verdict='tautological')


def analyse(source, ctx):
    """The main check: pin, defs, gate purity, inventory, one tautology proof per control, optional T488 data."""
    AC.need(AC.sha256(source) == ctx['sha256'], 'controls.pin: source sha256 %s' % AC.sha256(source))
    text = source.decode('utf-8')
    tree = ast.parse(text)
    funcs = check_defs(tree)
    gates = gates_of(tree)
    gate_purity(gates, funcs)
    ctrls = find_controls(tree)
    first = ctrls[0][0]
    res = []
    for at, name, lam in ctrls:
        r = classify(tree, funcs, gates, at, name, lam)
        AC.need(r['pattern'] == PATTERN_OF[name], 'controls.pattern: %r proved by %s, expected %s'
                % (name, r['pattern'], PATTERN_OF[name]))
        r['source'] = ast.get_source_segment(text, lam)
        res.append(r)
    pre = [g for g in gates if g[0] < first]
    out = dict(sha256=AC.sha256(source), controls=res, gates_before_controls=len(pre),
               unconditional_gates_before_controls=sum(1 for g in pre if g[1]),
               gate_messages=sorted(set(g[3] for g in gates)),
               original_sha256_claimed=(re.findall(r'Original SHA256 ([0-9a-f]{64})', text) or [None])[0])
    if ctx.get('data') is not None:
        out['t488'] = evaluate(res, ctx['data'])
    return out


# ------------------------------------------------------------------------------------ actual T488 values ---
def owners_file(name, blob, sha):
    return show_pinned(COMMITS['PR3633'], 'research/staged-width-t488/owners/' + name, blob, sha)


def compact_sha(obj):
    """sha256 of the compact JSON text plus newline (the byte format of PR3633's literal files)."""
    return AC.sha256(json.dumps(obj, separators=(',', ':')).encode() + b'\n')


def payload_sha(rows):
    return compact_sha(dict(columns=COLUMNS, dispatch_overrides=[], rows=rows))


def build_t488(rows):
    """T488 data for the evaluation, from git-pinned inputs only, plus the journal rows.  ORDER/DISPATCH are rebuilt
    as 8 copies of the 61 base replicas (ORDER37 + T8 at +37 + T16 at +45, copy cp at +61*cp) and must hash to
    PR3633's EXPECTED.json literal_files pins; the rows are bound to its payload_sha256 inside evaluate()."""
    exp = json.loads(spec_bytes(EXPECTED_JSON))
    base, bdisp = [], {}
    for (oname, ob, osha), (dname, db, dsha), off in zip(BASE_ORDERS, BASE_DISPATCH, (0, 37, 45)):
        base += [[s, r + off] for s, r in json.loads(owners_file(oname, ob, osha))]
        bdisp.update(((s, r + off), q) for s, r, q in json.loads(owners_file(dname, db, dsha)))
    order = [[s, r + 61 * cp] for s, r in base for cp in range(8)]
    dispatch = [[s, r + 61 * cp, bdisp[(s, r)]] for s, r in base for cp in range(8)]
    lit = exp['literal_files']
    AC.need(compact_sha(order) == lit['ORDER.json'], 'controls.data_pin: rebuilt ORDER != EXPECTED pin')
    AC.need(compact_sha(dispatch) == lit['DISPATCH.json'], 'controls.data_pin: rebuilt DISPATCH != EXPECTED pin')
    prov = owners_file('PROVIDERS.json', *PROVIDERS_PIN)
    AC.need(AC.sha256(prov) == lit['PROVIDERS.json'], 'controls.data_pin: PROVIDERS.json != EXPECTED pin')
    return dict(rows=rows, payload_sha256=exp['payload_sha256'], order=order, dispatch=dispatch,
                providers=json.loads(prov), replicas=exp['replicas'],
                profile=dict((int(k), v) for k, v in exp['profile'].items()),
                template=json.loads(gzip.decompress(show_pinned(*TEMPLATE))),
                plan=json.loads(gzip.decompress(show_pinned(*PLAN))))


def read_local_fill(owners_dir):
    """Rows of the locally regenerated FILL.json.gz (file sha256 = PR3633 EXPECTED literal_files pin)."""
    raw = open(os.path.join(owners_dir, 'FILL.json.gz'), 'rb').read()
    AC.need(AC.sha256(raw) == json.loads(spec_bytes(EXPECTED_JSON))['literal_files']['FILL.json.gz'],
            'controls.data_pin: FILL.json.gz sha256')
    j = json.loads(gzip.decompress(raw))
    AC.need(j['columns'] == COLUMNS and j['dispatch_overrides'] == [], 'controls.data_pin: journal schema')
    return j['rows']


def source_window(template, clock, r, child):
    """(lo, hi) of idle child `child` in replica r: hi = time of the replica's latest local sweep when the child's idle
    sweep runs, lo = latest time the sweep's pair was touched (local sweep or bridge) before it, else -1."""
    pair_of_stage = dict((x['stage'], x['pair']) for x in template['recipe'] if x['kind'] == 'local')
    last, now = {}, None
    for ev in template['execution_schedule']:
        if ev['kind'] == 'local_cover_sweep':
            now = clock[(ev['stage'], r)]
            last[pair_of_stage[ev['stage']]] = now
        elif ev['kind'] == 'bridge':
            last[ev['src']] = last[ev['dst']] = now
        elif ev['kind'] == 'idle_cover_sweep' and child in ev['child_indices']:
            return last.get(ev['pair'], -1), now
    raise AC.AuditFail('controls.data_window: child %d has no source window' % child)


def first_role(rows):
    """Index of the first role in (owner, child, port, time) order: the first entry of the gate's z[idx]."""
    return min(range(len(rows)), key=lambda i: (rows[i][2], rows[i][3], rows[i][4], rows[i][0], i))


def evaluate(res, d):
    """The premises the proofs use, checked on the actual T488 values (each with its own rule id), and the predicate
    values, which are fixed by each predicate's form once the premises hold (reported with their basis)."""
    rows, order = d['rows'], d['order']
    AC.need(payload_sha(rows) == d['payload_sha256'], 'controls.data_pin: journal rows do not re-serialise to the '
            'pinned FILL payload sha256')
    N, M = len(order), 408
    AC.need(len(rows) == N * M, 'controls.data_rows: %d rows != %d calls x 408' % (len(rows), N))
    t0, h0, o0, c0, p0, z0 = rows[0]
    prem, val = {}, {}
    # duplicate helper: the gate 'complete literal ordered helper identities' (time, helper) == (i // 408, i % 408)
    AC.need(all(r[0] == i // M and r[1] == i % M for i, r in enumerate(rows)),
            'controls.data_identity: helper/time columns are not the ordered identities')
    prem['duplicate helper'] = 'rows are the ordered (call, helper) identities'
    helper = [r[1] for r in rows]
    shifted = [helper[0]] + helper[:-1]
    val['duplicate helper'] = dict(value=shifted == [i % M for i in range(len(rows))],
                                   basis='data-independent (shifted_column: entries 0 and 1 are equal)')
    # strict lower endpoint: the window gate on row 0, lo < t <= hi
    clock = dict(((s, r), t) for t, (s, r) in enumerate(order))
    lo, hi = source_window(d['template'], clock, o0, c0)
    AC.need(lo < t0 <= hi, 'controls.data_window: row 0 time %d outside its window (%d, %d]' % (t0, lo, hi))
    prem['strict lower endpoint used as available'] = dict(lo=lo, hi=hi, t=t0, holds='lo < t <= hi')
    val['strict lower endpoint used as available'] = dict(value=bool(lo < lo <= hi), basis='data-independent (lo < lo)')
    # same-call family reused: the physical family of row 0
    fam = 2 * d['plan']['pairs'][str(c0)] + d['plan']['sides'][str(c0)]
    f = o0 * 896 + fam * 112 + p0
    val['same-call family reused'] = dict(value=len({int(f), int(f)}) == 2, family=f,
                                          basis='data-independent (one-element set)')
    # unpaid chronological hole: the first sorted role's bin has prefix-sum offsets (the gate z[idx] == expected)
    prov = dict(((s, r), p) for s, r, p in d['dispatch'])
    width = lambda t, h: d['providers'][prov[tuple(order[t])]]['widths'][h]   # noqa: E731
    k0 = first_role(rows)
    b = rows[k0][2:5]
    members = sorted((r[0], i) for i, r in enumerate(rows) if r[2:5] == b)
    acc = 0
    for t, i in members:
        AC.need(rows[i][5] == acc, 'controls.data_prefix: bin %r offset at time %d is %d, prefix %d'
                % (b, t, rows[i][5], acc))
        acc += width(t, rows[i][1])
    prem['unpaid chronological hole'] = dict(bin=b, bin_roles=len(members), holds='offsets are prefix sums of widths')
    val['unpaid chronological hole'] = dict(value=rows[k0][5] + 1 == 0, z=rows[k0][5], expected=0,
                                            basis='reduced form: expected[0] = 0 (first role of its bin) and the '
                                                  'premise gives z = 0')
    # one unpaid rank1 child: with the gate dict(H) == profile the predicate is profile == bad
    AC.need(sum(k * v for k, v in d['profile'].items()) == 65088 * d['replicas'],
            'controls.data_mass: profile mass != 65088 x replicas (second conjunct of the same gate)')
    prem['one unpaid rank1 child'] = dict(rank1=d['profile'][1], holds='profile mass = 65088 x 488; H not recomputed')
    bad = dict(d['profile'])
    bad[1] += 1
    val['one unpaid rank1 child'] = dict(value=d['profile'] == bad, basis='reduced form: profile == profile + {1: 1}')
    return dict(premises=prem, predicate_values=val)


# -------------------------------------------------------------------------------------------- controls ---
def controls(source, ctx, out):
    """Negative controls, all through analyse(): source edits (re-pinned, so only the named rule can reject them) and,
    with T488 data, data mutants (re-pinned payload unless the pin itself is the target)."""
    text = source.decode()

    def through(src, data='keep', repin=True):
        b = src.encode() if isinstance(src, str) else src
        c = dict(ctx, sha256=AC.sha256(b) if repin else ctx['sha256'])
        if data != 'keep':
            c['data'] = data
        return lambda: analyse(b, c)

    def sub(old, new, base=None):
        base = text if base is None else base
        AC.need(base.count(old) == 1, 'controls.harness: anchor %r found %d times' % (old[:40], base.count(old)))
        return base.replace(old, new)

    def taut(name, src, verdict):
        AL.expect(out, name, 'controls.tautology', through(src, None), attrs=dict(verdict=verdict))

    gate109 = "need(np.array_equal(z[idx],expected),'every chronological pending mask is a compact prefix')"
    hist = "need(dict(H)==profile and sum(r*n for r,n in H.items())==65088*T,'independent complete histogram')"
    hole = 'lambda: int(z[idx[0]])+1==int(expected[0])'
    region = 'controls=[]\n'          # first statement after the last premise gate, before every control
    b = bytearray(source)
    b[100] ^= 1
    AL.expect(out, 'source byte flipped, pin kept', 'controls.pin', through(bytes(b), None, repin=False))
    # verdicts other than tautological
    scaffold = sub(gate109, "def prefix_ok(zz,ee):return bool(np.array_equal(zz,ee))\n"
                            "need(prefix_ok(z[idx],expected),'every chronological pending mask is a compact prefix')")
    taut('genuine control: the hole lambda feeds a shifted journal to the gate predicate prefix_ok',
         sub(hole, 'lambda: prefix_ok(np.r_[z[idx][:1]+1,z[idx][1:]],expected)', scaffold), 'genuine')
    taut('gate-coupled lambda: not prefix_ok(z[idx],expected), the gate call itself (not genuine)',
         sub(hole, 'lambda: not prefix_ok(z[idx],expected)', scaffold), 'gate-coupled')
    # each proof-pattern condition: a satisfiable (or unsupported) edit must not be certified
    lower = 'lo[o[0],c[0]]<lo[o[0],c[0]]<=hi'
    taut('irreflexive: satisfiable lo < t[0] <= hi', sub(lower, 'lo[o[0],c[0]]<t[0]<=hi'), 'unproven')
    taut('duplicate_set: two different families {family[0], family[1]}',
         sub('len({int(family[0]),int(family[0])})==2', 'len({int(family[0]),int(family[1])})==2'), 'unproven')
    taut('shifted_column: unshifted column rows[1:,1] (equals the tile on the real data)',
         sub('np.r_[rows[0,1],rows[:-1,1]]', 'np.r_[rows[0,1],rows[1:,1]]'), 'unproven')
    taut('shifted_column: tile(arange(1)) (M = 1)', sub('np.tile(np.arange(408),N)))', 'np.tile(np.arange(1),N)))'),
         'unproven')
    taut('shifted_column: first entry rows[407,1] (satisfiable rotation)',
         sub('np.r_[rows[0,1],rows[:-1,1]]', 'np.r_[rows[407,1],rows[:-1,1]]'), 'unproven')
    taut('shifted_column: different column rows[:-1,2] (satisfiable)',
         sub('np.r_[rows[0,1],rows[:-1,1]]', 'np.r_[rows[0,1],rows[:-1,2]]'), 'unproven')
    taut('shifted_column: different matrix cols[:-1,1] (satisfiable)',
         sub('np.r_[rows[0,1],rows[:-1,1]]', 'np.r_[rows[0,1],cols[:-1,1]]'), 'unproven')
    taut('shifted_column: reversed column rows[::-1,1] (step -1, satisfiable)',
         sub('np.r_[rows[0,1],rows[:-1,1]]', 'np.r_[rows[0,1],rows[::-1,1]]'), 'unproven')
    taut('shifted_column: attribute access rows.T in the operands (may have effects)',
         sub('np.r_[rows[0,1],rows[:-1,1]]', 'np.r_[rows.T[0,1],rows.T[:-1,1]]'), 'unproven')
    taut('irreflexive: lo <= lo (reflexive, true)', sub(lower, 'lo[o[0],c[0]]<=lo[o[0],c[0]]<=hi'), 'unproven')
    taut('duplicate_set: compared with 1 (true)', sub('len({int(family[0]),int(family[0])})==2',
                                                  'len({int(family[0]),int(family[0])})==1'), 'unproven')
    taut('duplicate_set: three elements {f[0], f[0], f[1]} (satisfiable)',
         sub('len({int(family[0]),int(family[0])})==2', 'len({int(family[0]),int(family[0]),int(family[1])})==2'),
         'unproven')
    taut('duplicate_set: elements without int() (two NaN scalars give two elements)',
         sub('len({int(family[0]),int(family[0])})==2', 'len({family[0],family[0]})==2'), 'unproven')
    taut('irreflexive: attribute access lo.T in the operands (may have effects)',
         sub(lower, 'lo.T[o[0],c[0]]<lo.T[o[0],c[0]]<=hi'), 'unproven')
    taut('duplicate_set: attribute access family.flat in the elements (may have effects)',
         sub('len({int(family[0]),int(family[0])})==2', 'len({int(family.flat[0]),int(family.flat[0])})==2'), 'unproven')
    taut('walrus in the lambda (tile count (n:=N))', sub('np.tile(np.arange(408),N)))', 'np.tile(np.arange(408),(n:=N))))'),
         'unproven')
    taut('impure call z.sort() in the tile count', sub('np.tile(np.arange(408),N)))',
                                                       'np.tile(np.arange(408),N+(z.sort() or 0))))'), 'unproven')
    taut('gate_offset: offset +0 (true after the gate)', sub(hole, 'lambda: int(z[idx[0]])+0==int(expected[0])'),
         'unproven')
    taut('gate_offset: second role z[idx[1]] (satisfiable)', sub(hole, 'lambda: int(z[idx[1]])+1==int(expected[0])'),
         'unproven')
    taut('gate_offset: second expected entry expected[1] (satisfiable)',
         sub(hole, 'lambda: int(z[idx[0]])+1==int(expected[1])'), 'unproven')
    taut('gate_offset: attribute access z.base in gate and lambda (may have effects)',
         sub(hole, 'lambda: int(z.base[idx[0]])+1==int(expected[0])',
             sub(gate109, gate109.replace('z[idx]', 'z.base[idx]'))), 'unproven')
    taut('gate_offset: gate on expected-1 (the predicate is then true)',
         sub(gate109, gate109.replace(',expected)', ',expected-1)')), 'unproven')
    taut('gate_offset: gate on (z+0)[idx] (another array)', sub(gate109, gate109.replace('z[idx]', '(z+0)[idx]')),
         'unproven')
    taut('gate_offset: gate on z[idx[::-1]] (another index)', sub(gate109, gate109.replace('z[idx]', 'z[idx[::-1]]')),
         'unproven')
    taut('gate_offset: premise gate deleted', sub(gate109 + '\n', ''), 'unproven')
    taut('gate_offset: premise gate moved after the controls',
         sub("need(all(sha(Path(p))", gate109 + "\nneed(all(sha(Path(p))", sub(gate109 + '\n', '')), 'unproven')
    taut('gate_offset: premise gate made conditional (if False:)', sub(gate109, 'if False:' + gate109), 'unproven')
    taut('gate_offset: index rebound to a boolean mask before the gate', sub(gate109, 'idx=idx>=0\n' + gate109),
         'unproven')
    taut('gate_offset: index rebound by a with statement before the gate',
         sub(gate109, "with open('/dev/null') as idx:pass\n" + gate109), 'unproven')
    taut('region: expected=expected+1 between gate and control', sub(region, region + 'expected=expected+1\n'),
         'unproven')
    taut('region: np.copyto(z,z-1) between gate and control', sub(region, region + 'np.copyto(z,z-1)\n'), 'unproven')
    taut('region: alias e=expected[:]; e[0]+=1 between gate and control',
         sub(region, region + 'e=expected[:];e[0]+=1\n'), 'unproven')
    taut('region: rows[0,5]-=1 between gate and control (z is a view of rows; no premise name)',
         sub(region, region + 'rows[0,5]-=1\n'), 'unproven')
    taut('region: alias r2=rows; r2[0,5]-=1 between gate and control (alias bound in the region, not fresh)',
         sub(region, region + 'r2=rows\nr2[0,5]-=1\n'), 'unproven')
    taut('region: module function (mutating z, defined before the gate) called between gate and control',
         sub(region, region + 'f()\n', sub(gate109, 'def f():\n z[0]=1\n' + gate109)), 'unproven')
    taut('gate_bump: bad[1]+=0 (bad == profile)', sub('bad[1]+=1', 'bad[1]+=0'), 'unproven')
    taut('gate_bump: bad[1]*=1 (bad == profile)', sub('bad[1]+=1', 'bad[1]*=1'), 'unproven')
    taut('gate_bump: histogram gate with "or" instead of "and"', sub(hist, hist.replace(' and ', ' or ')), 'unproven')
    taut('gate_bump: histogram gate without its dict(H)==profile conjunct',
         sub(hist, "need(sum(r*n for r,n in H.items())==65088*T,'independent complete histogram')"), 'unproven')
    taut('gate_bump: H[1]+=1 between the histogram gate and the control', sub(region, region + 'H[1]+=1\n'),
         'unproven')
    taut('gate_bump: bad.__setitem__(1,bad[1]-1) inside the bad pair (bad == profile after the bump)',
         sub('bad=dict(profile);bad[1]+=1;', 'bad=dict(profile);bad.__setitem__(1,bad[1]-1);bad[1]+=1;'), 'unproven')
    lam_lower = 'lambda: bool(lo[o[0],c[0]]<lo[o[0],c[0]]<=hi[o[0],c[0]])'
    lam_family = 'lambda: len({int(family[0]),int(family[0])})==2'
    AL.expect(out, 'lambdas of "strict lower endpoint" and "same-call family" swapped', 'controls.pattern',
              through(sub(lam_family, lam_lower, sub(lam_lower, 'LAMBDA_FAMILY')).replace('LAMBDA_FAMILY', lam_family),
                      None))
    # definitions, bindings, gate purity, inventory
    AL.expect(out, 'reject inverted to need(test(), ...)', 'controls.reject_def',
              through(sub("need(not test(), 'control accepted '+name)", "need(test(), 'control accepted '+name)"), None))
    AL.expect(out, 'need with an extra statement', 'controls.need_def',
              through(sub(' if not v:raise ValueError(m)\n', ' if not v:raise ValueError(m)\n m=v\n'), None))
    AL.expect(out, 'need rebound to a no-op after its def', 'controls.bindings',
              through(sub(' if not v:raise ValueError(m)\n', ' if not v:raise ValueError(m)\nneed=lambda v,m: None\n'),
                      None))
    AL.expect(out, 'gate that sorts a control input', 'controls.gate_purity',
              through(sub(region, "need(z.sort() is None,'sorted')\n" + region), None))
    AL.expect(out, 'gate with an in-place np.copyto', 'controls.gate_purity',
              through(sub(region, "need(np.copyto(z,z-1) is None,'copy')\n" + region), None))
    AL.expect(out, 'gate with out=z', 'controls.gate_purity',
              through(sub(region, "need(np.negative(z,out=z) is not None,'out')\n" + region), None))
    AL.expect(out, 'gate with np.add.at(z, ...)', 'controls.gate_purity',
              through(sub(region, "need(np.add.at(z,0,1) is None,'at')\n" + region), None))
    AL.expect(out, 'gate with an assignment expression', 'controls.gate_purity',
              through(sub(region, "need((q:=1)==1,'walrus')\n" + region), None))
    AL.expect(out, 'gate calling a module function that sorts its argument', 'controls.gate_purity',
              through(sub(region, "def touch(a):\n a.sort();return True\nneed(touch(z),'touched')\n" + region), None))
    AL.expect(out, 'gate calling a module function that stores into the global z', 'controls.gate_purity',
              through(sub(region, "def touch():\n z[0]=5;return True\nneed(touch(),'touched')\n" + region), None))
    AL.expect(out, 'gate calling a module function that rebinds the global z', 'controls.gate_purity',
              through(sub(region, "def touch():\n global z\n z=z-1\n return True\nneed(touch(),'touched')\n" + region),
                      None))
    AL.expect(out, 'reject call nested in an if statement', 'controls.inventory',
              through(sub("need(all(sha(Path(p))", "if True:reject('extra',lambda: False)\nneed(all(sha(Path(p))"), None))
    AL.expect(out, 'reject called with a function name instead of a lambda', 'controls.inventory',
              through(sub(lam_lower, 'lower_test'), None))
    AL.expect(out, 'sixth reject call', 'controls.inventory',
              through(sub("need(all(sha(Path(p))", "reject('extra',lambda: False)\nneed(all(sha(Path(p))"), None))
    d = ctx.get('data')
    if d is None:
        return
    # data mutants re-pinned (payload sha of the mutant), so only the premise checks can reject them
    rows = list(d['rows'])
    rows[0], rows[1] = list(rows[0]), list(rows[1])
    rows[0][1], rows[1][1] = rows[1][1], rows[0][1]
    AL.expect(out, 'T488 rows 0/1 helper ids swapped (re-pinned)', 'controls.data_identity',
              through(source, dict(d, rows=rows, payload_sha256=payload_sha(rows)), False))
    AL.expect(out, 'T488 rows 0/1 helper ids swapped, payload pin kept', 'controls.data_pin',
              through(source, dict(d, rows=rows), False))
    rows = d['rows'][:-1]
    AL.expect(out, 'T488 journal without its last row (re-pinned)', 'controls.data_rows',
              through(source, dict(d, rows=rows, payload_sha256=payload_sha(rows)), False))
    rows = list(d['rows'])
    clock = dict(((s, r), t) for t, (s, r) in enumerate(d['order']))
    t0, _, o0, c0 = rows[0][:4]
    kids = sorted(set(c for ev in d['template']['execution_schedule'] if ev['kind'] == 'idle_cover_sweep'
                      for c in ev['child_indices']))
    c1 = next(c for c in kids if not (lambda w: w[0] < t0 <= w[1])(source_window(d['template'], clock, o0, c)))
    rows[0] = rows[0][:3] + [c1] + rows[0][4:]
    AL.expect(out, 'T488 row 0 child %d -> %d, whose source window excludes time %d (re-pinned)' % (c0, c1, t0),
              'controls.data_window', through(source, dict(d, rows=rows, payload_sha256=payload_sha(rows)), False))
    rows = list(d['rows'])
    k0 = first_role(rows)
    rows[k0] = rows[k0][:5] + [rows[k0][5] + 1]
    AL.expect(out, 'T488 first-bin role offset +1, an unpaid hole (re-pinned)', 'controls.data_prefix',
              through(source, dict(d, rows=rows, payload_sha256=payload_sha(rows)), False))
    prof = dict(d['profile'])
    prof[1] += 1
    AL.expect(out, 'T488 profile rank-1 count +1', 'controls.data_mass', through(source, dict(d, profile=prof), False))


# ------------------------------------------------------------------------------------------------ main ---
def run_integrated(I=None, owners_rows=None, with_controls=True):
    """Structural analysis of PR3633's auditor and its located copies; with owners_rows (the journal rows [t, h, o, c, p, z]
    in journal order) also the T488 premises, the rows bound to PR3633's payload sha256 by re-serialisation.  I is
    accepted for the integration interface; inputs are read with this module's own pinned git reads."""
    t0 = time.time()
    copies, original_found, scanned = scan_trees()
    source = spec_bytes(TARGET)
    ctx = dict(sha256=TARGET[3], data=None if owners_rows is None else build_t488(owners_rows))
    target = analyse(source, ctx)
    per_copy = {}
    for label, spec in sorted(COPIES.items()):
        r = analyse(spec_bytes(spec), dict(sha256=spec[3], data=None))
        per_copy[label] = dict(path=spec[1], commit=COMMITS[spec[0]], git_blob=spec[2], sha256=spec[3],
                               patterns=[c['pattern'] for c in r['controls']],
                               all_tautological=all(c['verdict'] == 'tautological' for c in r['controls']),
                               gates_before_controls=r['gates_before_controls'],
                               original_sha256_claimed=r['original_sha256_claimed'],
                               gates_only_here_vs_PR3633=sorted(set(r['gate_messages']) - set(target['gate_messages'])),
                               gates_missing_here_vs_PR3633=sorted(set(target['gate_messages']) - set(r['gate_messages'])))
    out = []
    attempted = 0
    if with_controls:
        AL.harness_selftest()
        n0 = len(AC.ATTEMPTED)
        controls(source, ctx, out)
        attempted = len(AC.ATTEMPTED) - n0
    finding = ('All five reject() controls of PR3633 owners/independent_literal.py (and of its %d located copies) are '
               'tautological: three are unsatisfiable for every input (irreflexive a<a, a one-element set compared '
               'with length 2, a shifted column whose entries 0 and 1 are equal compared with tile(arange(408)), '
               'whose entries 0 and 1 differ) and two are the negation '
               'of an earlier unconditional gate restated with an off-by-one (z[idx[0]]+1 == expected[0] after '
               'z[idx]==expected; dict(H) == profile+{1:1} after dict(H)==profile).  No control calls a gate or any '
               'module function ("duplicate helper" builds a shifted helper column but compares it inline with the '
               'tile, a copy of half the gate expression, so the gate itself is never exercised), and no gate binds or '
               'mutates anything by name, so every control passes unchanged when any gate is deleted or weakened: the '
               'controls cannot detect a disabled gate (names tracked syntactically; aliasing excluded by inspection '
               'of these files).') % (len(per_copy) - 1)
    fairness = ('The gates themselves are real checks evaluated on the real T488 data, and the premises the two '
                'gate-based proofs use hold on that data; this is a control-coverage defect, not a correctness defect '
                'of the owner journal or of its gates.')
    return dict(scope='C2 inherited reject() controls of PR3633 owners/independent_literal.py', finding=finding,
                fairness=fairness, target=target, copies=per_copy, located=copies, original_sha256=ORIGINAL_SHA256,
                original_located=original_found,
                original_search='sha256 of every .py blob (%d) in the trees of main and the eight PR heads' % scanned,
                t488_evaluated=owners_rows is not None, controls=out, controls_attempted=attempted,
                controls_killed=len(out), runtime_seconds=round(time.time() - t0, 1))


def run(owners_dir=SCRATCH_OWNERS, with_controls=True):
    """Standalone: the rows of the locally regenerated FILL.json.gz (local-only input) through run_integrated."""
    return run_integrated(None, read_local_fill(owners_dir), with_controls)


if __name__ == '__main__':
    res = run(with_controls='--no-controls' not in sys.argv)
    tgt = res['target']
    print(json.dumps(dict(
        controls=[dict((k, c[k]) for k in ('name', 'source', 'pattern', 'premise_gate', 'data_independent', 'argument'))
                  for c in tgt['controls']],
        t488=tgt['t488'], gates_before_controls=tgt['gates_before_controls'],
        copies=res['copies'], original_located=res['original_located'], original_search=res['original_search'],
        negative_controls=[(c['control'], c['expected'], c['rejected_by'] == c['expected']) for c in res['controls']],
        runtime_seconds=res['runtime_seconds']), indent=1, sort_keys=True, default=str))
    print('PASS C2: 5 inherited controls tautological in %d files; %d of %d negative controls killed (%.1fs)'
          % (len(res['copies']), res['controls_killed'], res['controls_attempted'], res['runtime_seconds']))
