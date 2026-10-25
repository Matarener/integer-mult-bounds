#!/usr/bin/env python3
"""On-disk semantic/source/typed-receipt controls in a disposable export layout.

JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    with tempfile.TemporaryDirectory(prefix='partial-cache-boundary-') as name:
        root = Path(name)
        package = root/'research'/HERE.name
        package.mkdir(parents=True)
        for filename in ('verify.py', 'KERNEL.json', 'RESULT.json', 'SOURCES.json'):
            shutil.copyfile(HERE/filename, package/filename)
        source_paths = json.loads((HERE/'VERIFY.json').read_text())['inputs']
        for path in source_paths:
            destination = root/path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE.parent.parent/path, destination)
        kernel_bytes = (package/'KERNEL.json').read_bytes()
        receipt_bytes = (package/'RESULT.json').read_bytes()
        source_path = root/source_paths[0]
        source_bytes = source_path.read_bytes()
        results = []
        for case, diagnostic in [
            ('kernel-Y-sign', 'full-frame witness kernel'),
            ('vacuous-kernel', 'original input domain'),
            ('source-byte-drift', 'source drift'),
            ('missing-receipt', 'RESULT.json'),
            ('typed-receipt-bool-as-int', 'typed receipt mismatch'),
            ('wrong-receipt-count', 'typed receipt mismatch'),
        ]:
            (package/'KERNEL.json').write_bytes(kernel_bytes)
            (package/'RESULT.json').write_bytes(receipt_bytes)
            source_path.write_bytes(source_bytes)
            kernel, receipt = json.loads(kernel_bytes), json.loads(receipt_bytes)
            if case == 'kernel-Y-sign':
                row = next(row for row in kernel['original_input_displacement'] if row[0] == 113)
                row[1] = '2'
                (package/'KERNEL.json').write_text(json.dumps(kernel))
            elif case == 'vacuous-kernel':
                for row in kernel['original_input_displacement']:
                    row[1] = '0'
                (package/'KERNEL.json').write_text(json.dumps(kernel))
            elif case == 'source-byte-drift':
                source_path.write_bytes(source_bytes+b' ')
            elif case == 'missing-receipt':
                (package/'RESULT.json').unlink()
            elif case == 'typed-receipt-bool-as-int':
                receipt['current_helper_retraction_is_zero'] = 1
                if receipt != json.loads(receipt_bytes):
                    raise RuntimeError('old untyped comparison control did not match')
                (package/'RESULT.json').write_text(json.dumps(receipt))
            else:
                receipt['events'] -= 1
                (package/'RESULT.json').write_text(json.dumps(receipt))
            # The kernel controls bypass the stored receipt so an active
            # source/witness predicate, not a stale hash, must catch them.
            flags = ['--emit'] if case in ('kernel-Y-sign', 'vacuous-kernel', 'source-byte-drift') else []
            run = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py'), *flags],
                                 cwd=root, capture_output=True, text=True, timeout=20)
            if run.returncode == 0 or diagnostic not in run.stderr:
                raise RuntimeError('boundary control escaped '+case+' '+run.stderr)
            results.append({'case': case, 'rejection': diagnostic})
    print(json.dumps({'status': 'PASS_PARTIAL_CACHE_PACKAGE_BOUNDARIES',
                      'optimized_rejections': results}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
