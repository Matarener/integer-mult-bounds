#!/usr/bin/env python3
"""Source-pinned launch, protocol and ownership checks.
Mihir Srivastava, substantial OpenAI Codex assistance; Apache-2.0.
Native observations follow ywz65 and the credited PR5461/PR5463 controls.
"""
import argparse
from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
import types
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
REAL_POPEN = subprocess.Popen
RESULTS = []


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def source_checks(root=HERE):
    rows = json.loads((root / 'VENDOR.json').read_bytes())
    sources = json.loads((root / 'SOURCES.json').read_bytes())
    pins = sources['files']
    require(len(rows) == 3, 'unexpected vendor inventory')
    for row in rows:
        data = (root / row['local']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row['sha256'],
                'frozen vendor byte mismatch: ' + row['local'])
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
        require(blob == row['git_blob'], 'vendored Git blob identity mismatch')
        if row['commit'] == sources['base_commit']:
            matches = [r for r in pins if r['path'] == row['path']
                       and r.get('pin') == 'head:' + row['commit'] + ':' + row['path']
                       and r['sha256'] == row['sha256'] and r['git_blob'] == blob]
            require(len(matches) == 1, 'vendor manifest/source pin mismatch')
        else:
            # Pending fork commits are not ancestors of a fresh main-based PR.
            # Retain their exact snapshot and public provenance, not an invalid
            # claim that a normal checkout has the fork's Git object graph.
            require(row['repository'] == 'mihir-s-05/integer-mult-bounds'
                    and row['commit'] == '991da9010925914ec64a5293286edb10a7910218',
                    'unexpected external source nomination')
    return rows


def py(code, *args):
    return [sys.executable, '-I', '-S', '-B'] + (['-O'] if sys.flags.optimize else []) + ['-c', code, *args]


def fingerprint(error):
    return {k: getattr(error, k, None) for k in
            ('errno', 'winerror', 'strerror', 'filename', 'filename2')} | {'type': type(error).__name__}


def caught(call, kind):
    try:
        call()
    except kind as error:
        return error
    raise AssertionError('expected ' + kind.__name__)


@contextmanager
def track(owner):
    launched = []
    def start(*args, **kwargs):
        process = REAL_POPEN(*args, **kwargs)
        launched.append(process)
        return process
    with patch.object(owner, 'REAL_POPEN', side_effect=start):
        try:
            yield launched
            for process in launched:
                require(process.poll() is not None, 'gate running before fixture cleanup')
                require(all(s is None or s.closed for s in (process.stdin, process.stdout, process.stderr)),
                        'gate stream open before fixture cleanup')
        finally:
            for process in launched:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=10)
                for stream in (process.stdin, process.stdout, process.stderr):
                    if stream is not None and not stream.closed:
                        stream.close()


def use(factory, argv, **kwargs):
    with factory(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                 stderr=subprocess.DEVNULL, **kwargs) as process:
        process.stdin.close()
        data = process.stdout.read()
        return process.wait(timeout=10), data


def launch_cases(reader, owner, checked, root):
    old = lambda argv, **kw: owner.OwnedPopen(argv, reader._WINDOWS_GATE, **kw)
    new = lambda argv, **kw: checked.LaunchCheckedPopen(argv, owner, **kw)
    invalid = root / 'invalid executable.exe'
    invalid.write_bytes(b'This is not a PE executable.')
    cases = [('missing', [str(root / 'missing executable.exe')], {}),
             ('invalid-image', [str(invalid)], {}),
             ('directory-image', [str(root)], {}),
             ('missing-cwd', py('pass'), {'cwd': root / 'missing-cwd'})]
    for name, argv, kwargs in cases:
        expected = fingerprint(caught(lambda: use(REAL_POPEN, argv, **kwargs), OSError))
        with track(owner) as launched:
            if name == 'missing-cwd':
                observed_old = fingerprint(caught(lambda: use(old, argv, **kwargs), OSError))
                require(observed_old == expected, 'outer cwd behavior changed')
            else:
                observed_old = use(old, argv, **kwargs)
                require(observed_old == (1, b''), 'old launch behavior differs')
                observed_old = {'returncode': observed_old[0], 'stdout_hex': observed_old[1].hex()}
            error_new = caught(lambda: use(new, argv, **kwargs), OSError)
            observed_new = fingerprint(error_new)
            if observed_new != expected:
                raise AssertionError(
                    f'{name}: direct {expected!r} differs from repaired {observed_new!r}') from error_new
        RESULTS.append(dict(case=name, direct=expected, old=observed_old, repaired=observed_new,
                            gates=len(launched), cleanup_before_teardown=True))
    for name, argv, _ in cases[:3]:
        observations = {}
        for label, factory in [('direct', REAL_POPEN), ('old', old), ('repaired', new)]:
            calls = []
            def start(request, **kwargs):
                calls.append(request)
                return factory(argv, **kwargs)
            with track(owner), patch.object(reader.subprocess, 'Popen', side_effect=start):
                error = caught(lambda: list(reader.git_blobs(root, ['HEAD:missing'])),
                               ValueError if label == 'old' else OSError)
            require(len(calls) == 1, 'launch failure triggered compatibility retry')
            observations[label] = fingerprint(error)
        require(observations['direct'] == observations['repaired'], 'reader lost launch diagnostics')
        RESULTS.append(dict(case='actual-reader-' + name, observations=observations, attempts=1))


def protocol_cases(reader, owner, checked, root):
    new = lambda argv, **kw: checked.LaunchCheckedPopen(argv, owner, **kw)
    subprocess.run(['git', 'init', '-q', str(root)], check=True, capture_output=True)
    data = bytes([0, 255, 13, 10]) * 20000
    (root / 'blob').write_bytes(data)
    oid = subprocess.check_output(['git', '-C', str(root), 'hash-object', '-w', 'blob']).decode().strip()
    for status in (0, 1, 7, 129):
        calls = []
        def start(argv, **kwargs):
            calls.append(argv)
            return new(py('raise SystemExit(' + str(status) + ')') if len(calls) == 1 else argv, **kwargs)
        with track(owner), patch.object(reader.subprocess, 'Popen', side_effect=start):
            if status == 129:
                require(list(reader.git_blobs(root, [oid, oid])) == [(oid, data)] * 2,
                        'launched exit-129 fallback corrupted bytes')
            else:
                caught(lambda: list(reader.git_blobs(root, [oid])), ValueError)
        require(len(calls) == (2 if status == 129 else 1), 'wrong legacy retry gate')
        RESULTS.append(dict(case='launched-exit-' + str(status), attempts=len(calls), exact=True))
    with track(owner), patch.object(reader.subprocess, 'Popen', side_effect=new), \
            patch.object(reader, 'GIT_BLOB_RESPONSE_TIMEOUT', 0.25):
        rows = reader.git_blobs(root, [oid, oid])
        require(next(rows) == (oid, data), 'first raw binary mismatch')
        time.sleep(0.4)
        require(next(rows) == (oid, data), 'consumer pause counted against response')
        require(list(rows) == [], 'extra blob response')
    RESULTS.append(dict(case='binary-80000-byte-duplicate-consumer-pause', exact=True))
    unicode_root = root / 'cwd λ 🧮'
    unicode_root.mkdir()
    argument = 'quoted "value" λ 🧮'
    env = os.environ.copy()
    env['LAUNCH_DIAGNOSTIC_VALUE'] = argument
    code = "import os,sys,json; sys.stdout.buffer.write(json.dumps([sys.argv[1],os.environ['LAUNCH_DIAGNOSTIC_VALUE'],os.getcwd()],ensure_ascii=False).encode('utf-8'))"
    with track(owner):
        status, raw = use(new, py(code, argument), cwd=unicode_root, env=env)
    require(status == 0 and json.loads(raw) == [argument, argument, str(unicode_root)],
            'argv/env/cwd or stdout channel contaminated')
    RESULTS.append(dict(case='unicode-argv-env-cwd', exact=True))


def gate_failure_cases(owner, checked, root):
    new = lambda argv, **kw: checked.LaunchCheckedPopen(argv, owner, **kw)
    # These controlled gates isolate report-channel failures. No requested
    # command is launched, even when the gate itself returns exit status 129.
    bad = [
        ('missing-report-exit', lambda p: 'raise SystemExit(129)', RuntimeError),
        ('missing-report-timeout', lambda p: 'import time; time.sleep(60)', subprocess.TimeoutExpired),
        ('malformed-report', lambda p: 'from pathlib import Path; Path(' + repr(str(p)) + ').write_text("{}")', ValueError),
        ('oversized-report', lambda p: 'from pathlib import Path; Path(' + repr(str(p)) + ').write_bytes(b"x"*65537)', ValueError),
    ]
    for name, gate, error_type in bad:
        with track(owner) as launched, patch.object(checked, 'make_gate', side_effect=gate), \
                patch.object(checked, 'STARTUP_TIMEOUT', 0.4):
            error = caught(lambda: use(new, py('pass'), cwd=root), error_type)
        require(len(launched) == 1, 'setup did not retain the owned gate')
        RESULTS.append(dict(case=name, error=type(error).__name__, cleanup_before_teardown=True))
    real_dll = ctypes.WinDLL
    def denied(*args):
        ctypes.set_last_error(5)
        return 0
    class Denied:
        def __init__(self, *args, **kwargs):
            self.api = real_dll(*args, **kwargs)
        def __getattr__(self, name):
            return denied if name == 'AssignProcessToJobObject' else getattr(self.api, name)
    marker = root / 'not-launched'
    with track(owner), patch.object(ctypes, 'WinDLL', Denied):
        error = caught(lambda: use(new, py('from pathlib import Path; import sys; Path(sys.argv[1]).touch()', str(marker))), OSError)
    require(error.winerror == 5 and not marker.exists(), 'assignment denial released command')
    RESULTS.append(dict(case='assignment-denied', winerror=5, requested_command_started=False))

    real_read = checked.read_payload
    attempts = []
    def sharing_denied(path):
        attempts.append(path)
        if len(attempts) <= 2:
            raise PermissionError(13, 'injected transient sharing denial', str(path))
        return real_read(path)
    with track(owner), patch.object(checked, 'read_payload', side_effect=sharing_denied):
        require(use(new, py("import sys; sys.stdout.buffer.write(b'PAYLOAD')")) == (0, b'PAYLOAD'),
                'transient report denial changed command result')
    require(len(attempts) == 3, 'transient report denial was not retried exactly twice')
    with track(owner), patch.object(checked, 'read_payload', side_effect=PermissionError(13, 'persistent denial')), \
            patch.object(checked, 'STARTUP_TIMEOUT', .3):
        caught(lambda: use(new, py('pass')), subprocess.TimeoutExpired)
    RESULTS.append(dict(case='report-read-denial-controls', transient_attempts=3,
                        permanent_denial='TimeoutExpired', cleanup_before_teardown=True))


class Handle:
    def __init__(self, pid):
        self.api = ctypes.WinDLL('kernel32', use_last_error=True)
        for name, result, args in [
            ('OpenProcess', wintypes.HANDLE, [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]),
            ('WaitForSingleObject', wintypes.DWORD, [wintypes.HANDLE, wintypes.DWORD]),
            ('TerminateProcess', wintypes.BOOL, [wintypes.HANDLE, wintypes.UINT]),
            ('CloseHandle', wintypes.BOOL, [wintypes.HANDLE]),
        ]:
            fn = getattr(self.api, name)
            fn.restype, fn.argtypes = result, args
        self.handle = self.api.OpenProcess(0x00100001, False, pid)
        require(bool(self.handle), 'cannot retain descendant process object')
    def wait(self, ms):
        value = self.api.WaitForSingleObject(self.handle, ms)
        require(value in (0, 258), 'invalid native observer result')
        return value == 0
    def close(self):
        if not self.wait(0):
            self.api.TerminateProcess(self.handle, 1)
            require(self.wait(5000), 'fixture cleanup failed')
        require(self.api.CloseHandle(self.handle), 'process handle close failed')


DESCENDANT = r"""
import os, subprocess, sys, time
from pathlib import Path
root, mode = Path(sys.argv[1]), sys.argv[2]
child = subprocess.Popen([sys.executable, '-I', '-S', '-c', 'import time; time.sleep(60)'], stdin=sys.stdin, stdout=sys.stdout, stderr=subprocess.DEVNULL)
(root/'child.pending').write_text(str(child.pid))
(root/'child.pending').replace(root/'child.pid')
while not (root/'observed').exists(): time.sleep(.01)
while sys.stdin.buffer.read(1) not in (bytes([0]), bytes([10]), b''): pass
if mode != 'stall':
    sys.stdout.buffer.write(b'a'*40+b' blob 4'+bytes([10,0,255,13,10,10]))
    sys.stdout.buffer.flush()
os._exit(0)
"""


def descendant_cases(reader, owner, checked, root):
    for mode in ('success', 'stall', 'early-close'):
        directory = root / mode
        directory.mkdir()
        handles = []
        def start(argv, **kwargs):
            process = checked.LaunchCheckedPopen(py(DESCENDANT, str(directory), mode), owner, **kwargs)
            try:
                deadline = time.monotonic() + 10
                while not (directory / 'child.pid').exists():
                    require(time.monotonic() < deadline, 'descendant readiness timed out')
                    time.sleep(.01)
                handles.append(Handle(int((directory / 'child.pid').read_text())))
                require(not handles[0].wait(0), 'descendant not live at readiness')
                (directory / 'observed').touch()
                return process
            except BaseException:
                process.__exit__(*sys.exc_info())
                raise
        try:
            with track(owner), patch.object(reader.subprocess, 'Popen', side_effect=start), \
                    patch.object(reader, 'GIT_BLOB_RESPONSE_TIMEOUT', 0.5):
                rows = reader.git_blobs(directory, ['HEAD:x'])
                expected = ('a' * 40, bytes([0,255,13,10]))
                if mode == 'stall':
                    caught(lambda: list(rows), subprocess.TimeoutExpired)
                elif mode == 'early-close':
                    require(next(rows) == expected, 'wrong early blob')
                    rows.close()
                else:
                    require(list(rows) == [expected], 'wrong descendant response')
            require(len(handles) == 1 and handles[0].wait(1000), 'live descendant before teardown')
            RESULTS.append(dict(case='descendant-' + mode, stopped_before_teardown=True))
        finally:
            (directory / 'observed').touch()
            for handle in handles:
                handle.close()


def portable_controls(checked):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'status'
        for value in [None, [], {}, {'status': 'started', 'extra': True},
                      {'status': 'oserror', 'errno': True, 'winerror': 2, 'strerror': 'x', 'filename': None, 'filename2': None}]:
            path.write_text(json.dumps(value), encoding='utf-8')
            caught(lambda: checked.read_report(path), ValueError)
        path.write_text('{', encoding='utf-8')
        caught(lambda: checked.read_report(path), ValueError)
        path.write_bytes(b'x' * (checked.MAX_REPORT_BYTES + 1))
        caught(lambda: checked.read_report(path), ValueError)
        path.write_text('{"status":"started"}', encoding='utf-8')
        checked.read_report(path)
    RESULTS.append(dict(case='portable-report-controls', rejected=7, accepted=1))


def mutation_controls(reader, owner, checked, root):
    new = lambda argv, **kw: checked.LaunchCheckedPopen(argv, owner, **kw)
    # Omitting the handshake must fail the diagnostic-equivalence assertion.
    with track(owner), patch.object(checked, 'await_launch', return_value=None):
        caught(lambda: caught(lambda: use(new, [str(root / 'absent.exe')]), OSError), AssertionError)
    # An out-of-band handshake is essential: a banner on stdout changes the
    # literal bytes delivered by the requested command.
    polluted = checked.GATE.replace("report({'status': 'started'})",
                                    "sys.stdout.buffer.write(b'BANNER'); sys.stdout.buffer.flush(); report({'status': 'started'})")
    with track(owner), patch.object(checked, 'GATE', polluted):
        code, raw = use(new, py("import sys; sys.stdout.buffer.write(b'PAYLOAD')"))
    require(code == 0 and b'BANNER' in raw and raw != b'PAYLOAD', 'stdout mutation escaped detection')
    # Source-byte controls reject a disposable copy before importing native code.
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp)
        (copy / 'vendor').mkdir()
        for name in ('VENDOR.json', 'SOURCES.json', 'vendor/research_package.py', 'vendor/owned_pipe.py', 'vendor/NOTICE'):
            (copy / name).write_bytes((HERE / name).read_bytes())
        with (copy / 'vendor/owned_pipe.py').open('ab') as stream:
            stream.write(b'\n# deliberate corruption\n')
        caught(lambda: source_checks(copy), AssertionError)
    RESULTS.append(dict(case='mutation-controls', omitted_handshake_detected=True,
                        stdout_contamination_detected=True, source_corruption_detected=True))


def started_without_report(owner, checked, root):
    marker = root / 'unreported-child.pid'
    handles = []
    original_gate = checked.GATE
    stalled_gate = original_gate.replace("report({'status': 'started'})", 'import time; time.sleep(60)')
    original_wait = checked.await_launch
    def observe_then_wait(process, report, argv, timeout):
        deadline = time.monotonic() + 10
        while not marker.exists():
            require(time.monotonic() < deadline, 'unreported child not ready')
            time.sleep(.01)
        handles.append(Handle(int(marker.read_text())))
        require(not handles[0].wait(0), 'unreported child not alive')
        original_wait(process, report, argv, .2)
    code = 'from pathlib import Path; import os,sys,time; p=Path(sys.argv[1]); q=p.with_suffix(".pending"); q.write_text(str(os.getpid())); q.replace(p); time.sleep(60)'
    try:
        with track(owner), patch.object(checked, 'GATE', stalled_gate), \
                patch.object(checked, 'await_launch', side_effect=observe_then_wait):
            caught(lambda: use(lambda argv, **kw: checked.LaunchCheckedPopen(argv, owner, **kw),
                               py(code, str(marker))), subprocess.TimeoutExpired)
        require(handles[0].wait(1000), 'unreported child survived startup failure')
        RESULTS.append(dict(case='started-child-without-report', stopped_before_teardown=True))
    finally:
        for handle in handles:
            handle.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--require-windows', action='store_true')
    args = parser.parse_args()
    require(not args.require_windows or sys.platform == 'win32', 'native Windows execution required')
    sources = source_checks()
    checked = load(HERE / 'spawn_checked.py', 'checked_launch')
    portable_controls(checked)
    if sys.platform == 'win32':
        reader = load(HERE / 'vendor/research_package.py', 'frozen_reader')
        reader.subprocess = types.SimpleNamespace(**vars(subprocess))
        owner = load(HERE / 'vendor/owned_pipe.py', 'frozen_owner')
        with tempfile.TemporaryDirectory(prefix='launch diagnostic fixture ') as tmp:
            root = Path(tmp)
            launch_cases(reader, owner, checked, root)
            protocol_cases(reader, owner, checked, root)
            gate_failure_cases(owner, checked, root)
            descendant_cases(reader, owner, checked, root)
            started_without_report(owner, checked, root)
            mutation_controls(reader, owner, checked, root)
    result = dict(status='PASS_WINDOWS_GIT_LAUNCH_DIAGNOSTICS' if sys.platform == 'win32'
                  else 'PASS_PORTABLE_CONTROLS_WINDOWS_NOT_RUN',
                  platform=platform.platform(), python=sys.version, optimized=bool(sys.flags.optimize),
                  native_windows_executed=sys.platform == 'win32', sources=sources, cases=RESULTS,
                  implementation_hashes={n: hashlib.sha256((HERE / n).read_bytes()).hexdigest()
                                         for n in ('verify.py', 'spawn_checked.py')})
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == '__main__':
    main()
