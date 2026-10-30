#!/usr/bin/env python3
"""Reject three disposable reader mutations with the native audit observer.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import types


def main():
    path = Path(__file__).with_name('probe.py')
    probe = types.ModuleType('probe')
    probe.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), probe.__dict__)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reader', type=Path, default=probe.ROOT / 'scripts/research_package.py')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    probe.require(os.name == 'nt', 'native Windows is required')
    raw = args.reader.read_bytes()
    changes = [
        ('no-watchdog', b'    timer.start()\n', b'    pass  # controlled removed watchdog\n',
         'header', 'fixture timed out: watchdog callback'),
        ('wrong-timeout-class',
         b'raise subprocess.TimeoutExpired("git cat-file blob response", GIT_BLOB_RESPONSE_TIMEOUT)',
         b'raise ValueError("controlled wrong timeout class")',
         'header', 'expected timeout after EOF/stop'),
        ('changed-binary-payload', b'yield fields[0].decode("ascii"), pinned\n',
         b'yield fields[0].decode("ascii"), pinned + b"!"\n',
         'success', 'binary reply changed'),
    ]
    results = []
    with tempfile.TemporaryDirectory(prefix='git pipe control ') as tmp:
        reader = Path(tmp) / 'reader.py'
        for name, before, after, mode, expected in changes:
            probe.require(raw.count(before) == 1, 'mutation anchor changed: ' + name)
            mutated = raw.replace(before, after)
            reader.write_bytes(mutated)
            try:
                probe.exercise(reader, mode, 'held')
            except ValueError as exc:
                probe.require(str(exc) == expected, 'wrong rejection for ' + name + ': ' + str(exc))
                results.append({'name': name, 'rejection': str(exc),
                                'mutant_sha256': hashlib.sha256(mutated).hexdigest()})
            else:
                raise ValueError('mutation was not rejected: ' + name)
    report = {'status': 'REJECTED_ALL_THREE_MUTATIONS', 'optimized': sys.flags.optimize,
              'completed_at_utc': datetime.now(timezone.utc).isoformat(),
              'source_sha256': hashlib.sha256(raw).hexdigest(),
              'controls_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'probe_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'controls': results}
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(report['status'])


if __name__ == '__main__':
    main()
