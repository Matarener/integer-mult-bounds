#!/usr/bin/env python3
"""Read-only, source-bound portable replay of the shared-source packet.

Apache-2.0; substantial OpenAI Codex assistance. No third-party dependencies.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SUITES = {
    'source': ('source-audit/check_source_packet.py', 'source-audit/SOURCE-AUDIT.json'),
    'algebra': ('algebra/check_shared_source.py', 'algebra/RESULT.json'),
    'invoice': ('check_invoice.py', 'INVOICE.json'),
    'independent': ('independent/check_independent.py', 'independent/RESULT.json'),
}
BOOTSTRAP = '''from pathlib import Path
from hashlib import sha256
import sys
path, expected = sys.argv[1:]
source = Path(path).read_bytes()
if sha256(source).hexdigest() != expected:
    raise ValueError('child source hash mismatch')
sys.argv = [path]
exec(compile(source, path, 'exec'), {'__name__':'__main__', '__file__':path, '__package__':None})
'''


def need(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate():
    entries = json.loads((ROOT/'MANIFEST.json').read_text())['files']
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()
              and p.name != 'MANIFEST.json'}
    need(actual == set(entries), 'exact package file coverage')
    for relative, wanted in entries.items():
        p = ROOT/relative
        need(not p.is_symlink() and p.resolve().is_relative_to(ROOT), 'regular contained input')
        need(sha256(p.read_bytes()).hexdigest() == wanted, 'source hash: '+relative)
    return len(entries)


def canonical(result):
    return {k:v for k,v in result.items() if k not in ('python','optimized')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', choices=tuple(SUITES))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    count = authenticate()
    sources = json.loads((ROOT/'MANIFEST.json').read_text())['files']
    checks = {}
    for name in ([args.suite] if args.suite else SUITES):
        script, receipt = SUITES[name]
        cmd = [sys.executable, '-I'] + ([] if __debug__ else ['-O']) + [
            '-B', '-c', BOOTSTRAP, str(ROOT/script), sources[script]]
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=180)
        need(result.returncode == 0, name+' failed:\n'+result.stdout+result.stderr)
        observed = json.loads(result.stdout)
        expected = json.loads((ROOT/receipt).read_text())
        need(canonical(observed) == canonical(expected), name+' complete semantic receipt mismatch')
        checks[name] = {'status':observed['status'],
                        'semantic_sha256':sha256(json.dumps(canonical(observed),sort_keys=True).encode()).hexdigest()}
    need(authenticate() == count, 'sources stable after execution')
    output = {'status':'PASS_SHARED_SOURCE_COMPENSATION_PACKAGE', 'checks':checks,
              'authenticated_files':count, 'optimized':not __debug__,
              'python':sys.version.split()[0], 'no_positive_query_saving':True,
              'no_new_kappa':True}
    encoded = json.dumps(output,indent=2,sort_keys=True)+'\n'
    if args.output:
        need(not args.output.resolve().is_relative_to(ROOT), 'receipt must be outside immutable package')
        args.output.write_text(encoded)
    print(encoded,end='')


if __name__ == '__main__':
    main()
