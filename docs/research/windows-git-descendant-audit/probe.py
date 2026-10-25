#!/usr/bin/env python3
"""Observe the shared Git blob reader's native Windows pipe/lifetime boundary.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
Builds on JoyboyBrian's POSIX descendant fixture and ywz65's retained-handle
Windows observer. This is an opt-in diagnostic, not a production repair.
"""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
RESPONSE_TIMEOUT = 0.4
OBSERVATION_SECONDS = 0.6
BOUND = 10

# Every fixture process has a bounded natural lifetime as a backup to retained
# handle cleanup. The observer captures the handles before releasing the leader.
CHILD = r'''
import ctypes,json,msvcrt,os,sys,time
from ctypes import wintypes
from pathlib import Path
directory=Path(sys.argv[1])
api=ctypes.WinDLL('kernel32',use_last_error=True)
api.GetFileType.argtypes=[wintypes.HANDLE]
api.GetFileType.restype=wintypes.DWORD
types=[api.GetFileType(msvcrt.get_osfhandle(fd)) for fd in (0,1)]
if types!=[3,3]: raise RuntimeError('descendant did not inherit two native pipes')
if sys.argv[2]=='closed':
    os.close(0)
    os.close(1)
pending=directory/'child-ready.pending'
pending.write_text(json.dumps({'pid':os.getpid(),'inherited_file_types':types,
                              'closed_before_ready':sys.argv[2]=='closed'}))
pending.replace(directory/'child-ready')
time.sleep(30)
os._exit(0)
'''

LEADER = r'''
import json,os,subprocess,sys,time
from pathlib import Path
directory=Path(sys.argv[1]);mode=sys.argv[2];pipes=sys.argv[3]
pending=directory/'leader-ready.pending'
pending.write_text(str(os.getpid()))
pending.replace(directory/'leader-ready')
child=None
if pipes!='absent':
    child=subprocess.Popen([sys.executable,'-I','-S','-c',sys.argv[4],str(directory),pipes],
        stdin=sys.stdin,stdout=sys.stdout,stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW)
end=time.monotonic()+15
while not (directory/'begin').exists():
    if time.monotonic()>end: os._exit(99)
    time.sleep(.005)
if mode=='live':
    time.sleep(15)
    os._exit(98)
if mode=='write': os._exit(0)
def request():
    while sys.stdin.buffer.read(1) not in (b'\0',b'\n',b''): pass
request()
reply=b'a'*40+b' blob 4\n'+b'\0\xff\r\n'+b'\n'
if mode=='header': os._exit(0)
if mode=='payload': reply=reply[:50]
if mode=='terminator': reply=reply[:-1]
if mode=='malformed': reply=b'bad\n'
sys.stdout.buffer.write(reply);sys.stdout.buffer.flush()
if mode=='suspended':
    request()
    sys.stdout.buffer.write(reply);sys.stdout.buffer.flush()
if mode=='early': sys.stdin.buffer.read()
os._exit(0)
'''

WORKER = r'''
import hashlib,json,subprocess,sys,time,types
from pathlib import Path
from unittest.mock import patch
reader,directory,mode,pipes,timeout,leader,child=sys.argv[1:]
directory=Path(directory)
raw=Path(reader).read_bytes()
p=types.ModuleType('observed_reader');p.__file__=reader
exec(compile(raw,reader,'exec'),p.__dict__)
p.GIT_BLOB_RESPONSE_TIMEOUT=float(timeout)
real_popen=subprocess.Popen;real_stop=p._stop_git_blob_process
calls=[]
def stop(process):
    real_stop(process)
    pending=directory/'deadline-fired.pending'
    pending.write_text(json.dumps({'leader_status':process.poll()}))
    pending.replace(directory/'deadline-fired')
def start(argv,**kwargs):
    calls.append(argv)
    if mode=='fallback' and len(calls)==1:
        rejected=real_popen([sys.executable,'-I','-S','-c','import sys;sys.exit(129)'],
                            creationflags=subprocess.CREATE_NO_WINDOW,**kwargs)
        # The synthetic option probe is already rejected before its first
        # write. Do not mistake interpreter startup for a protocol stall.
        if rejected.wait(timeout=10)!=129: raise RuntimeError('option probe did not reject')
        return rejected
    process=real_popen([sys.executable,'-I','-S','-c',leader,str(directory),mode,pipes,child],
                       creationflags=subprocess.CREATE_NO_WINDOW,**kwargs)
    end=time.monotonic()+15
    while not (directory/'begin').exists():
        if time.monotonic()>end: raise RuntimeError('observer did not release fixture')
        time.sleep(.005)
    return process
result={'calls':0,'source_sha256':hashlib.sha256(raw).hexdigest()}
try:
    with patch.object(p.subprocess,'Popen',side_effect=start), \
         patch.object(p,'_stop_git_blob_process',side_effect=stop):
        specs=['x'*2_000_000] if mode=='write' else ['HEAD:first','HEAD:second'] if mode=='suspended' else ['HEAD:first']
        rows=p.git_blobs(directory,specs)
        expected=('a'*40,b'\0\xff\r\n')
        try:
            if mode in ('early','suspended'):
                result['first_exact']=next(rows)==expected
                if mode=='suspended':
                    time.sleep(float(timeout)*2)
                    result['second_exact']=next(rows)==expected
                    result['exhausted']=list(rows)==[]
            else:
                result['exact']=list(rows)==[expected]
        finally:
            rows.close()
except Exception as error:
    result['error']=type(error).__name__
    result['message']=str(error)[:200]
result['calls']=len(calls)
pending=directory/'result.pending'
pending.write_text(json.dumps(result),encoding='utf-8')
pending.replace(directory/'result.json')
'''


def require(ok, message):
    if not ok:
        raise ValueError(message)


def wait_for(predicate, description, seconds=BOUND):
    end = time.monotonic() + seconds
    while not predicate():
        require(time.monotonic() < end, 'fixture timed out: ' + description)
        time.sleep(.005)


class Handles:
    """Observe process objects, never interpret a reused PID as termination."""
    def __init__(self):
        import ctypes
        from ctypes import wintypes
        self.ctypes = ctypes
        self.api = ctypes.WinDLL('kernel32', use_last_error=True)
        signatures = {
            'OpenProcess': (wintypes.HANDLE, [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]),
            'WaitForSingleObject': (wintypes.DWORD, [wintypes.HANDLE, wintypes.DWORD]),
            'TerminateProcess': (wintypes.BOOL, [wintypes.HANDLE, wintypes.UINT]),
            'CloseHandle': (wintypes.BOOL, [wintypes.HANDLE]),
        }
        for name, (result, arguments) in signatures.items():
            fn = getattr(self.api, name)
            fn.restype, fn.argtypes = result, arguments

    def checked(self, ok):
        if not ok:
            raise self.ctypes.WinError(self.ctypes.get_last_error())
        return ok

    def open(self, pid):
        return self.checked(self.api.OpenProcess(0x00100001, False, pid))

    def alive(self, handle):
        state = self.api.WaitForSingleObject(handle, 0)
        require(state in (0, 258), 'native process observation failed')
        return state == 258

    def stop(self, handle):
        if self.alive(handle):
            stopped = self.api.TerminateProcess(handle, 1)
            if not stopped and self.alive(handle):
                self.checked(stopped)
        require(self.api.WaitForSingleObject(handle, 5000) == 0,
                'fixture process did not stop')

    def cleanup(self, handle):
        try:
            self.stop(handle)
        finally:
            self.checked(self.api.CloseHandle(handle))


def exercise(reader, mode, pipes):
    native = Handles()
    with tempfile.TemporaryDirectory(prefix='git descendant audit ') as tmp, ExitStack() as stack:
        directory = Path(tmp)
        # Files avoid making observer output depend on inherited capture pipes.
        with (directory / 'worker.log').open('wb') as log:
            argv = [sys.executable, '-I', '-B', '-W', 'error']
            if sys.flags.optimize:
                argv.append('-O')
            argv += ['-c', WORKER, str(reader), tmp, mode, pipes,
                     str(RESPONSE_TIMEOUT), LEADER, CHILD]
            process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            # Registered first, hence cleaned last after descendants.
            stack.callback(process.wait, timeout=5)
            stack.callback(native.cleanup, native.open(process.pid))
            def leader_ready():
                if (directory / 'result.json').exists():
                    raise ValueError('reader returned before fixture readiness: '
                                     + (directory / 'result.json').read_text())
                if process.poll() is not None:
                    raise ValueError('worker exited before fixture readiness: '
                                     + (directory / 'worker.log').read_text(encoding='utf-8'))
                return (directory / 'leader-ready').exists()

            wait_for(leader_ready, 'leader readiness')
            leader = native.open(int((directory / 'leader-ready').read_text()))
            stack.callback(native.cleanup, leader)
            child = None
            child_ready = None
            if pipes != 'absent':
                wait_for(lambda: (directory / 'child-ready').exists(), 'descendant readiness')
                child_ready = json.loads((directory / 'child-ready').read_text())
                require(child_ready['inherited_file_types'] == [3, 3], 'missing pipe inheritance')
                require(child_ready['closed_before_ready'] == (pipes == 'closed'), 'wrong pipe control')
                child = native.open(child_ready['pid'])
                stack.callback(native.cleanup, child)
                require(native.alive(child), 'descendant not alive before leader release')
            require(native.alive(leader), 'leader exited before handle capture')
            start = time.monotonic()
            (directory / 'begin').touch()
            row = {'mode': mode, 'pipes': pipes, 'ready_handles_retained': True}
            if child_ready:
                row['inherited_file_types'] = child_ready['inherited_file_types']
                row['closed_before_ready'] = child_ready['closed_before_ready']
            stall = mode in ('header', 'payload', 'terminator', 'write') and pipes == 'held'
            if stall:
                wait_for(lambda: not native.alive(leader), 'leader exit')
                wait_for(lambda: (directory / 'deadline-fired').exists(), 'watchdog callback')
                deadline = json.loads((directory / 'deadline-fired').read_text())
                require(deadline['leader_status'] == 0, 'deadline did not see exited leader')
                end = time.monotonic() + OBSERVATION_SECONDS
                while time.monotonic() < end:
                    require(process.poll() is None and not (directory / 'result.json').exists(),
                            'expected gap absent: reader returned while descendant held pipes')
                    require(native.alive(child), 'descendant stopped during observation')
                    time.sleep(.005)
                row.update(leader_exited=True, watchdog_fired=True,
                           reader_blocked_after_watchdog=True,
                           child_alive_before_intervention=True,
                           observed_after_watchdog_seconds=OBSERVATION_SECONDS)
                # Deliberate causal intervention, AFTER the recorded failure.
                native.stop(child)
                row['intervention'] = 'terminate retained descendant handle'
            wait_for(lambda: (directory / 'result.json').exists(), 'reader result')
            process.wait(timeout=5)
            require(process.returncode == 0, 'worker failed: ' + (directory / 'worker.log').read_text())
            result = json.loads((directory / 'result.json').read_text())
            row['result'] = result
            row['elapsed_seconds'] = round(time.monotonic() - start, 4)
            require(result['calls'] == (2 if mode == 'fallback' else 1), 'unexpected retry')
            require(not native.alive(leader), 'leader still alive after reader returned')
            if stall or mode == 'live':
                require(result.get('error') == 'TimeoutExpired', 'expected timeout after EOF/stop')
            elif mode in ('header', 'payload', 'terminator', 'write', 'malformed'):
                require(result.get('error') == 'ValueError', 'expected protocol rejection')
                require(not (directory / 'deadline-fired').exists(), 'unexpected response timeout')
            else:
                require('error' not in result, 'valid reply failed')
                expected_flags = ('first_exact', 'second_exact', 'exhausted') if mode == 'suspended' else ('first_exact',) if mode == 'early' else ('exact',)
                require(all(result.get(flag) is True for flag in expected_flags), 'binary reply changed')
                require(not (directory / 'deadline-fired').exists(), 'consumer time charged to response')
            if child is not None:
                row['child_alive_at_reader_return'] = native.alive(child)
                require(row['child_alive_at_reader_return'] == (not stall),
                        'unexpected descendant lifetime at reader return')
            row['fixture_log'] = (directory / 'worker.log').read_text(encoding='utf-8')
            require(not row['fixture_log'], 'worker emitted warnings/errors: ' + row['fixture_log'])
    # ExitStack has now stopped and closed every retained fixture handle. A
    # cleanup failure raises before a row can become successful evidence.
    row['fixture_cleanup_confirmed'] = True
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reader', type=Path, default=ROOT / 'scripts/research_package.py')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(os.name == 'nt', 'native Windows is required; no platform emulation or passing skip')
    reader = args.reader.resolve()
    source_hash = hashlib.sha256(reader.read_bytes()).hexdigest()
    cases = [(mode, pipes) for mode in ('header', 'payload', 'terminator', 'write')
             for pipes in ('held', 'closed')]
    cases += [(mode, 'held') for mode in ('success', 'malformed', 'early', 'suspended', 'fallback')]
    cases += [('live', 'absent')]
    rows = []
    for mode, pipes in cases:
        row = exercise(reader, mode, pipes)
        require(row['result']['source_sha256'] == source_hash, 'reader bytes changed during probe')
        rows.append(row)
        print('OBSERVED', mode, pipes, flush=True)
    report = {
        'status': 'CONFIRMED_WINDOWS_GIT_DESCENDANT_GAP',
        'completed_at_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Controlled native subprocess boundary, not spontaneous installed-Git behavior or a repair.',
        'source_sha256': source_hash,
        'probe_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'environment': {'python': sys.version, 'windows': platform.platform(),
                        'optimized': sys.flags.optimize},
        'response_timeout_seconds': RESPONSE_TIMEOUT,
        'cases': rows,
    }
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(report['status'])


if __name__ == '__main__':
    main()
