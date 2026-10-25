#!/usr/bin/env python3
"""Independent, source-bound review of the whole-owner runtime memory repair.

This checks preservation of the scientific audit function after removing only
its dead accumulator and diagnostic statements. It also reruns the isolation
failure fixtures in a private directory. Full physical replay is a separate
gate. Apache-2.0; substantial OpenAI Codex assistance.
"""
from argparse import ArgumentParser
from copy import deepcopy
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUNTIME = HERE.parent/'runtime-repair'
UPSTREAM = HERE.parent/'sources/PR3815/research/staged544-producer-return'
ADAPTER_SHA = '30a39a3612efde96a0db189c14053afe5e012e56de1a89863596a078a8b64381'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(node):
    return ast.dump(node, include_attributes=False)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=RUNTIME/'REVIEW-INVOICE.json')
    parser.add_argument('--work', type=Path, default=HERE/'runtime-review')
    args = parser.parse_args()
    adapter_path = RUNTIME/'audit_fast.py'
    need(sha(adapter_path) == ADAPTER_SHA, 'exact frozen runtime adapter')
    pins = json.loads((UPSTREAM/'REPLAY-INPUTS.json').read_text())
    archive_path = UPSTREAM/'REPLAY-INPUTS.tar.gz'
    need(sha(archive_path) == pins['archive_sha256'], 'complete predecessor replay archive')
    with tarfile.open(archive_path) as archive:
        raw = archive.extractfile('source/code/audit_allcold.py').read()
        emitter = archive.extractfile('source/code/emit_allcold.py').read()
    need(hashlib.sha256(raw).hexdigest() == pins['files']['source/code/audit_allcold.py'], 'original auditor archive member')
    need(hashlib.sha256(emitter).hexdigest() == pins['files']['source/code/emit_allcold.py'], 'original emitter archive member')
    spec = importlib.util.spec_from_file_location('reviewed_runtime_adapter', adapter_path)
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    need(hashlib.sha256(raw).hexdigest() == adapter.AUDIT_SHA256, 'exact scientific source pin')
    need(hashlib.sha256(emitter).hexdigest() == adapter.EMIT_SHA256, 'unchanged emitter pass-through pin')
    source = raw.decode().replace('\r\n', '\n')
    changed, transform_receipt = adapter.transform(raw)
    old_tree, new_tree = ast.parse(source), ast.parse(changed)
    old_audit = deepcopy(next(n for n in old_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'audit'))
    new_audit = deepcopy(next(n for n in new_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'audit'))

    class RemoveDeadAccumulator(ast.NodeTransformer):
        removed = 0

        def visit_Assign(self, node):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == 'touches':
                need(ast.unparse(node.value) == 'defaultdict(list)', 'only dead accumulator initialization')
                self.removed += 1
                return None
            return self.generic_visit(node)

        def visit_Expr(self, node):
            if ast.unparse(node) == 'touches[family].append((s, rep, h))':
                self.removed += 1
                return None
            return self.generic_visit(node)

    class RemoveDiagnostics(ast.NodeTransformer):
        removed = 0

        def visit_Assign(self, node):
            if ast.unparse(node) == '_runtime_call_count = 0':
                self.removed += 1
                return None
            return self.generic_visit(node)

        def visit_AugAssign(self, node):
            if ast.unparse(node) == '_runtime_call_count += 1':
                self.removed += 1
                return None
            return self.generic_visit(node)

        def visit_If(self, node):
            if ast.unparse(node.test) == '_runtime_call_count % 360 == 0':
                need(len(node.body) == 1 and not node.orelse and
                     ast.unparse(node.body[0]) == "_runtime_progress('audited-invocations', invocations=_runtime_call_count)",
                     'diagnostic branch has no scientific operation')
                self.removed += 1
                return None
            return self.generic_visit(node)

    dead, diagnostic = RemoveDeadAccumulator(), RemoveDiagnostics()
    old_normalized, new_normalized = dead.visit(old_audit), diagnostic.visit(new_audit)
    need(dead.removed == 2 and diagnostic.removed == 3, 'exact dead and diagnostic statement census')
    need(dump(old_normalized) == dump(new_normalized), 'entire scientific audit AST unchanged after dead-data and diagnostic normalization')
    # Independently check order, not merely the adapter's assertion multiset.
    assertions = lambda tree: [dump(n) for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    old_asserts, new_asserts = assertions(old_tree), assertions(new_tree)
    old_hash = next(x for x in old_asserts if "Name(id='raw'" in x)
    new_hash = next(x for x in new_asserts if "Name(id='_runtime_gzip_sha'" in x)
    need([x for x in old_asserts if x != old_hash] == [x for x in new_asserts if x != new_hash],
         'all 76 unchanged scientific assertions retain their order')
    need(source.split('\nreport=dict(', 1)[1] == changed.split('\nreport=dict(', 1)[1], 'complete scientific report and export tail unchanged')
    need(not any(isinstance(n, ast.Name) and n.id == 'ct' for n in ast.walk(old_audit)), 'audit input is its argument, not global ct')
    need(source.count("old['owners']") == 1 and "own[:(2*V)]==old['owners'][:(2*V)]" in source,
         'ancestral owners are observed only through their data prefix')
    need("assert V==112 and canon['h']==9" in source and "if k not in('owners','local_program_sha256')" in source,
         'the retained data prefix has exactly 224 entries and other ancestral metadata excludes owners')
    need("assert all(hashlib.sha256((BASE/name).read_bytes()).hexdigest()==value for name,value in summary['source_artifacts'].items())" in changed,
         'all original source artifact byte hashes still checked')
    args.work.mkdir(parents=True, exist_ok=True)
    auditor_path = args.work/'audit_allcold.py'
    auditor_path.write_bytes(raw)
    fixture_path = args.work/'FIXTURES.json'
    command = [sys.executable, '-B', str(RUNTIME/'fixtures.py'), '--audit-script', str(auditor_path), '--out', str(fixture_path)]
    with (args.work/'fixtures.log').open('w') as stream:
        process = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT,
                                 env=dict(os.environ, PYTHONOPTIMIZE='', PYTHONDONTWRITEBYTECODE='1'))
    need(process.returncode == 0, 'fresh isolation failure-mode fixtures')
    fixtures = json.loads(fixture_path.read_text())
    need(fixtures['status'] == 'PASS_RUNTIME_ADAPTER_FAILURE_MODES' and len(fixtures['checks']) == 19,
         'all 19 failure-mode fixtures')
    need(fixtures['adapter_sha256'] == ADAPTER_SHA, 'fixtures bind reviewed adapter')
    result = {
        'status': 'PASS_INDEPENDENT_RUNTIME_SOURCE_AND_CONTROL_REVIEW',
        'script_sha256': sha(Path(__file__)),
        'adapter_sha256': ADAPTER_SHA,
        'auditor_sha256': hashlib.sha256(raw).hexdigest(),
        'emitter_sha256': hashlib.sha256(emitter).hexdigest(),
        'source_archive_sha256': sha(archive_path),
        'transform_receipt': transform_receipt,
        'normalized_entire_audit_ast_equal': True,
        'scientific_assertion_order_equal_after_one_equivalent_digest': True,
        'scientific_report_and_export_tail_byte_equal': True,
        'ancestral_owner_trim': 'The pinned auditor compares only old owners[:2*V], asserts V=112, and excludes owners from its other call metadata comparison. Only the unused in-memory tail is removed; immutable source hashes still cover the original file.',
        'dead_accumulator': 'Exactly one touches initialization and one append are removed. No read exists. Removing these and diagnostics makes the complete audit function AST identical.',
        'isolation_review': 'ct is parsed separately from parent and provider registries. audit(t) reads t and expected globals, never global ct. Original mutation bodies are retained. Copy-on-write isolates mutations while preserving internal aliases. Only the original expected exceptions thrown by audit count; mutator errors, unexpected exceptions, acceptance, missing receipts, signals and nonzero child exits fail.',
        'fresh_fixture_script_sha256': sha(RUNTIME/'fixtures.py'),
        'fresh_fixture_receipt_sha256': sha(fixture_path),
        'fresh_fixture_count': len(fixtures['checks']),
        'full_physical_replay_replaced': False,
        'scope': 'Independent finite source/control review. The parent release must still complete the original whole-owner positive audit and every enabled rejection control on the full actual input, followed by its original release gates.'
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'], '19 fresh fixtures', args.out)


if __name__ == '__main__':
    main()
