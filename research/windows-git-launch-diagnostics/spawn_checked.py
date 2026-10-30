"""Opt-in launch reporting around PR5463's unchanged Windows stream owner.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
The isolated event gate derives from ywz65's retained PR2469 implementation.
This is the Git reader's string-argv/binary-stream subset, not general Popen.
"""
from contextlib import contextmanager
import json
from pathlib import Path
import subprocess
import tempfile
import time

STARTUP_TIMEOUT = 10
MAX_REPORT_BYTES = 65536

# REPORT is inserted as a Python string literal by make_gate. The requested
# command receives its original argv/env/cwd/standard handles, not this channel.
GATE = r'''
import ctypes
from ctypes import wintypes
import json
import os
import subprocess
import sys
api = ctypes.WinDLL('kernel32', use_last_error=True)
api.OpenEventW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
api.OpenEventW.restype = wintypes.HANDLE
api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
api.WaitForSingleObject.restype = wintypes.DWORD
api.CloseHandle.argtypes = [wintypes.HANDLE]
api.CloseHandle.restype = wintypes.BOOL
event = api.OpenEventW(0x00100000, False, sys.argv[1])
if not event:
    raise ctypes.WinError(ctypes.get_last_error())
try:
    if api.WaitForSingleObject(event, 30000) != 0:
        raise RuntimeError('Git launch ownership gate was not released')
finally:
    api.CloseHandle(event)

def report(value):
    with open(REPORT + '.pending', 'x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=True)
    os.replace(REPORT + '.pending', REPORT)

# Only this OSError is reported as a requested-executable launch error. Failure
# of the gate/reporting mechanism fails closed via the parent's bounded wait.
try:
    child = subprocess.Popen(json.loads(sys.argv[2]))
except OSError as error:
    report({'status': 'oserror', 'errno': error.errno,
            'winerror': error.winerror, 'strerror': error.strerror,
            'filename': error.filename, 'filename2': error.filename2})
    raise SystemExit(1)
report({'status': 'started'})
raise SystemExit(child.wait())
'''


def make_gate(report):
    return 'REPORT = ' + repr(str(report)) + '\n' + GATE


def read_payload(path):
    with path.open('rb') as stream:
        return stream.read(MAX_REPORT_BYTES + 1)


def interpret_report(payload):
    # Truncated, oversized, malformed or unknown reports never become success,
    # and never trigger the reader's legacy retry.
    if len(payload) > MAX_REPORT_BYTES:
        raise ValueError('oversized Git launch report')
    value = json.loads(payload)
    if value == {'status': 'started'}:
        return
    fields = {'status', 'errno', 'winerror', 'strerror', 'filename', 'filename2'}
    if (not isinstance(value, dict) or set(value) != fields
            or value['status'] != 'oserror'
            or type(value['errno']) is not int or type(value['winerror']) is not int
            or not isinstance(value['strerror'], str)
            or any(value[k] is not None and not isinstance(value[k], str)
                   for k in ('filename', 'filename2'))):
        raise ValueError('invalid Git launch report')
    # Windows OSError maps the original native code to the appropriate subclass
    # and errno, just as direct CreateProcess/Popen did in the gate.
    raise OSError(value['errno'], value['strerror'], value['filename'],
                  value['winerror'], value['filename2'])


def read_report(path):
    interpret_report(read_payload(path))


def await_launch(process, report, argv, timeout):
    deadline = time.monotonic() + timeout
    while True:
        if report.exists():
            try:
                payload = read_payload(report)
            except PermissionError:
                # Windows can briefly deny opening a newly renamed report.
                # Retry only channel I/O, within the original startup bound.
                # A requested executable's PermissionError is reconstructed
                # below, outside this handler, and must propagate immediately.
                pass
            else:
                interpret_report(payload)
                return
        elif process.poll() is not None:
            # A fast process may publish between the existence check and poll.
            if not report.exists():
                raise RuntimeError('Git ownership gate exited without a launch report')
        if time.monotonic() >= deadline:
            raise subprocess.TimeoutExpired(argv, timeout)
        time.sleep(0.01)


@contextmanager
def checked_pipe(argv, owner, **kwargs):
    """Report launch before returning streams; stop the owned job on any failure.

    The trusted owner is the exact PR5463 module. Startup has its own bound;
    the existing per-response watchdog still excludes consumer pauses.
    """
    if not isinstance(argv, list) or not argv or any(type(a) is not str for a in argv):
        raise TypeError('Git launch wrapper requires a nonempty list of strings')
    with tempfile.TemporaryDirectory(prefix='git launch status ') as temporary:
        report = Path(temporary) / 'status.json'
        with owner.OwnedPopen(argv, make_gate(report), **kwargs) as process:
            await_launch(process, report, argv, STARTUP_TIMEOUT)
            yield process


class LaunchCheckedPopen:
    """Only the Popen subset consumed by the pinned blob reader, used with with."""
    def __init__(self, argv, owner, **kwargs):
        self.context = checked_pipe(argv, owner, **kwargs)
        self.process = self.context.__enter__()

    def __getattr__(self, name):
        return getattr(self.process, name)

    def __enter__(self):
        return self

    def __exit__(self, *exception):
        return self.context.__exit__(*exception)
