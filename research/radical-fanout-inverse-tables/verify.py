"""Inverse-table conformance and full-command equality, produced by Nick Petalas."""

import contextlib
import cProfile
import hashlib
import io
import json
import os
from pathlib import Path
import pstats
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    provenance = json.loads((HERE / 'UPSTREAM.json').read_text())
    require(provenance['pull_request'] == 6210, 'wrong predecessor')
    require(len(provenance['files']) == 2, 'two retained source files')
    for row in provenance['files']:
        path = HERE / row['retained']
        require(path.parent == HERE, 'local source path')
        data = path.read_bytes()
        require(len(data) == row['bytes'], 'source length changed')
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'source changed')


def observed(call, argument):
    try:
        return ('value', call(argument))
    except (IndexError, ValueError) as error:
        return (type(error).__name__, str(error))


def conformance():
    import fast
    source = fast.source
    elements = controls = 0
    for modulus, variables in ((2, 3), (3, 3), (4, 2)):
        ring = source.truncated_polynomials(modulus, variables)
        cached = fast.InverseTableRing(ring.name, ring.n, ring.one, ring.add, ring.mul)
        for x in range(-ring.n, ring.n):
            require(observed(ring.neg, x) == observed(cached.neg, x), 'negative table')
            require(observed(ring.inv, x) == observed(cached.inv, x), 'unit table')
            elements += 1
        for x in (-ring.n-1, ring.n):
            require(observed(ring.neg, x) == observed(cached.neg, x), 'neg index error')
            require(observed(ring.inv, x) == observed(cached.inv, x), 'inv index error')
            controls += 2
        require(cached._neg[cached._neg[ring.one]] == ring.one, 'negation involution')
    tiny = source.truncated_polynomials(2, 1)
    for n, add, mul in ((82, tiny.add, tiny.mul), (4, (), tiny.mul),
                        (4, tiny.add, tuple(row[:-1] for row in tiny.mul))):
        try:
            fast.InverseTableRing('invalid', n, tiny.one, add, mul)
        except ValueError:
            controls += 1
        else:
            raise ValueError('invalid table accepted')
    return elements, controls


def execute(script, cwd=HERE):
    env = dict(os.environ)
    env.pop('PYTHONOPTIMIZE', None)
    env.pop('PYTHONPATH', None)
    scratch = env.get('IMB_RUN_ROOT')
    with tempfile.TemporaryDirectory(prefix='inverse-table-bytecode-', dir=scratch) as cache:
        command = [sys.executable, '-W', 'error', '-B', '-X', 'pycache_prefix='+cache]
        if sys.flags.optimize:
            command.append('-O')
        command.append(str(script))
        return subprocess.run(command, cwd=cwd, env=env, capture_output=True, timeout=120)


def corruption_control():
    scratch = os.environ.get('IMB_RUN_ROOT')
    with tempfile.TemporaryDirectory(prefix='inverse-table-control-', dir=scratch) as directory:
        root = Path(directory)
        for name in ('fast.py', 'retained_source.py'):
            (root / name).write_bytes((HERE / name).read_bytes())
        with (root / 'retained_source.py').open('ab') as stream:
            stream.write(b'\nraise RuntimeError("executed corrupt source")\n')
        result = execute(root / 'fast.py', root)
        require(result.returncode != 0, 'changed source accepted')
        require(b'retained executable source bytes changed' in result.stderr,
                'source must reject before import')
        require(b'executed corrupt source' not in result.stderr, 'corrupt source executed')


def profiled_call(entry):
    output = io.StringIO()
    profile = cProfile.Profile()
    with contextlib.redirect_stdout(output):
        profile.runcall(entry)
    stats = pstats.Stats(profile).stats
    matches = [value[1] for key, value in stats.items()
               if key[2] == "<method 'index' of 'tuple' objects>"]
    require(len(matches) == 1, 'CPython tuple-index counter unavailable')
    return output.getvalue(), matches[0]


def search_reduction(expected):
    import fast
    original_class = fast.source.Ring
    try:
        before, before_searches = profiled_call(fast.source.main)
        after, after_searches = profiled_call(fast.main)
    finally:
        fast.source.Ring = original_class
    require(before.encode() == after.encode() == expected, 'profiled workload changed')
    require(0 < after_searches < before_searches, 'no exact search-count improvement')
    return dict(before=before_searches, after=after_searches)


def main():
    authenticate()
    elements, controls = conformance()
    baseline = execute(HERE / 'retained_source.py')
    optimized = execute(HERE / 'fast.py')
    for result in (baseline, optimized):
        require(result.returncode == 0 and not result.stderr, 'complete command failed')
    require(baseline.stdout == optimized.stdout, 'complete stdout differs')
    require(baseline.stdout.endswith(b'PASS_R16_RADICAL_TRIPLE_FANOUT no_new_kappa\n'),
            'complete workload did not finish')
    corruption_control()
    searches = search_reduction(baseline.stdout)
    files = tuple(p for p in sorted(HERE.iterdir()) if p.is_file())
    require(len(files) <= 16, 'bounded local package inventory')
    receipt = dict(status='PASS_RADICAL_FANOUT_INVERSE_TABLES', elements=elements,
                   controls=controls+1, complete_commands=2,
                   profiled_complete_workloads=2, tuple_index_searches=searches,
                   stdout_sha256=hashlib.sha256(baseline.stdout).hexdigest(),
                   package_hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in files})
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
