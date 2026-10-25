#!/usr/bin/env python3
"""Adversarial mathematical and optimized-CLI controls for the graph audit."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('graph_audit', HERE/'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def clone(destination):
    package = destination/'research'/HERE.name
    shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
    for row in v.read_json(HERE/'SOURCES.json')['files']:
        if row['usage'] == 'input':
            p = destination/row['path']
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/row['path'], p)
    # Only files in this control's private directory are made writable.
    for p in destination.rglob('*'):
        if p.is_file():
            p.chmod(p.stat().st_mode | 0o200)
    return package


def cli(package, expected):
    result = subprocess.run([sys.executable, '-I', '-O', '-Werror', '-B', str(package/'verify.py')], capture_output=True, text=True, timeout=30)
    v.require((result.returncode == 0) == expected, 'optimized CLI acceptance control')
    return result.stdout+result.stderr


def main():
    v.require(not sys.argv[1:], 'no arguments accepted')
    # A real triangle must be found; coloring deliberately suppresses
    # repeated descriptions of one normal, not distinct normal directions.
    vertices = [(0, 1), (1, 2), (2, 4)]
    edges, triangle, _ = v.graph(vertices, 2)
    v.require(len(edges) == 3 and triangle is not None, 'triangle positive control')
    v.require((1 | 2 | 4).bit_count() > 2, 'triangle alone is not a common-cut witness')
    edges, triangle, _ = v.graph([(0, 1), (0, 2), (1, 4)], 2)
    v.require(len(edges) == 2 and triangle is None, 'same-color edge suppression')
    edges, triangle, _ = v.graph([(0, 3), (1, 5), (2, 9)], 3)
    v.require(len(edges) == 3 and triangle is not None, 'overlapping-cut triangle control')
    # Each two-dimensional annihilator has three nonzero elements and exactly
    # one sorted representative a<b<a^b; check every small independent pair.
    for n in range(2, 7):
        expected = {tuple(sorted((a, b, a ^ b))) for a in range(1, 1 << n) for b in range(1, 1 << n) if a != b}
        actual = [(a, b, a ^ b) for a in range(1, 1 << n) for b in range(a+1, 1 << n) if b < a ^ b]
        v.require(len(actual) == len(expected) and set(actual) == expected, 'annihilator orbit coverage')
    with tempfile.TemporaryDirectory(prefix='common24-graph-controls-') as name:
        package = clone(Path(name))
        v.require('PASS_COMMON24_GRAPH_AUDIT' in cli(package, True), 'positive CLI marker')
        result_path = package/'RESULT.json'
        original = result_path.read_bytes()
        result = json.loads(original)
        result['triangles'] = False
        result_path.write_text(json.dumps(result))
        v.require('receipt mismatch' in cli(package, False), 'result corruption rejected')
        result_path.write_bytes(original)
        program = package/'verify.py'
        source = program.read_text()
        old = 'if a != b and (s | t).bit_count() <= cutoff:'
        v.require(source.count(old) == 1, 'mutation anchor unique')
        program.write_text(source.replace(old, 'if False:'))
        v.require('two-direction witness missing' in cli(package, False), 'deleted compatibility edges rejected')
        program.write_text(source)
        table = Path(name)/'research/one-sided-six-multisets/data/data.txt'
        table.write_bytes(table.read_bytes()+b'\n')
        v.require('source SHA256' in cli(package, False), 'source mutation rejected')
    print('PASS_COMMON24_GRAPH_CONTROLS triangle_false_converse coloring annihilator_coverage optimized_CLI=4')


if __name__ == '__main__':
    main()
