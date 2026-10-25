#!/usr/bin/env python3
"""Complete replica-indexed symbolic Driver/compiler refinement.

Reuses ChrisR's PR3986 free-term semantics and unchanged physical dispatch.
The source-bound idle lookup is the only production AST substitution. The
append-only compiler operation list is streamed solely to bound verifier RAM.
Native request/chart validity is a separate prerequisite in REVIEW.json.
This does not enumerate GL64 or prove numerical primitive/CALL contracts.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace as NS
import time

import adapter
import compiler_binding

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT/'research/kappa-next-regime/sources/PR3986/research/r437-whole-word-refinement/check.py'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_harness():
    spec = importlib.util.spec_from_file_location('retained_whole_word', SOURCE)
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    harness.CALLER = compiler_binding.CALLER
    harness.PRE = harness.CALLER/'inputs/pr2753/predecessor'
    original_extract = harness.extract

    def extract(path, name, namespace, stream=False, mutation=None):
        if name in ('Driver', 'compile_node'):
            need(Path(path) == compiler_binding.SOURCES[name], 'exact retained component path')
            def revised(node):
                node = compiler_binding.rewrite_idle_lookup(node)
                return mutation(node) if mutation is not None else node
            return original_extract(path, name, namespace, stream, revised)
        return original_extract(path, name, namespace, stream, mutation)

    harness.extract = extract
    original_tiny = harness.tiny
    def tiny():
        t = original_tiny()
        t.idles_for = lambda child, replica: t.idles[child] if replica == 0 else ()
        return t
    harness.tiny = tiny
    return harness


class SymbolicTopology:
    """Faithful native topology projection at one formal arbitrary low label."""
    def __init__(self, actual):
        self.actual = actual
        self.catalogue = NS(low_classes=lambda: iter(('alpha',)), codes=None)
    def __getattr__(self, name):
        return getattr(self.actual, name)
    def matrix(self, chart):
        return chart.key


def run(args):
    started = time.monotonic()
    harness = load_harness()
    controls = harness.controls()
    controls['duplicate_owner_guard_gap'] = harness.guard_gap()
    run_controls = harness.run_control()
    result = {'status':'PASS_REPLICA_INDEXED_SYMBOLIC_CONTROLS',
              'AST_binding':compiler_binding.receipt(), 'controls':controls,
              'run_loop_contract_checks':run_controls}
    if not args.controls_only:
        kwargs = {}
        if args.word:
            kwargs.update(word_path=args.word, word_content_sha256=args.word_content_sha256)
        if args.template:
            kwargs['template_path'] = args.template
        catalogue, topology = adapter.load(**kwargs)
        print('Native replica catalogue built; executing complete symbolic word.', flush=True)
        complete = harness.check_word(SymbolicTopology(topology))
        need(complete['residuals'] == len(catalogue.requests), 'one residual per complete native request')
        need(complete['staged_roles'] == 660, '659 arbitrary dirty roles plus private COPY')
        need(complete['checkpoints'] == 29, 'all complete global checkpoints')
        result.update(status='PASS_REPLICA_INDEXED_COMPLETE_SYMBOLIC_WORD', complete=complete,
            native_binding=catalogue.receipt(), local_calls=9*catalogue.replicas,
            formal_low_labels=1,
            symbolic_low_scope='One formal arbitrary low; the all-low statement is the retained loop induction, not physical GL64 enumeration.',
            physical_payload_executed=False, primitive_contracts_proved=False)
    result['source_sha256'] = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (SOURCE, Path(__file__), HERE/'adapter.py', HERE/'compiler_binding.py',
                  compiler_binding.CALLER/'macro_machine.py', compiler_binding.CALLER/'residual_blocks.py')}
    result['elapsed_seconds'] = time.monotonic()-started
    return result


if __name__ == '__main__':
    need(__debug__, 'assertions must remain enabled')
    p = argparse.ArgumentParser()
    p.add_argument('--controls-only', action='store_true')
    p.add_argument('--word', type=Path)
    p.add_argument('--word-content-sha256')
    p.add_argument('--template', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'], 'elapsed_seconds':result['elapsed_seconds'],
                      'complete':result.get('complete')}))
