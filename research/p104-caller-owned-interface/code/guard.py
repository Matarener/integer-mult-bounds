"""Bound one non-spawning scientific child by elapsed time and sampled RSS.

Operational wrapper only. The caller adapter imports Python modules and does
not create descendant processes. Windows RSS uses GetProcessMemoryInfo.
"""
from pathlib import Path
import argparse
import ctypes
import hashlib
import json
import os
import subprocess
import sys
import time

def rss(proc):
    if os.name != 'nt':
        return int(Path(f'/proc/{proc.pid}/statm').read_text().split()[1])*os.sysconf('SC_PAGE_SIZE')
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_ = [('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[
            (name,ctypes.c_size_t) for name in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage',
                'QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
    info= Counters();info.cb=ctypes.sizeof(info)
    call=ctypes.windll.psapi.GetProcessMemoryInfo
    call.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
    call.restype=wintypes.BOOL
    if not call(int(proc._handle),ctypes.byref(info),info.cb):
        raise ctypes.WinError()
    return info.WorkingSetSize

if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--name',required=True)
    ap.add_argument('--seconds',type=int,default=120)
    ap.add_argument('--memory-mib',type=int,default=512)
    ap.add_argument('command',nargs=argparse.REMAINDER)
    a=ap.parse_args();command=a.command[1:] if a.command[:1]==['--'] else a.command
    root=Path(__file__).resolve().parent
    if not command or Path(a.name).name != a.name or a.seconds<=0 or a.memory_mib<=0:
        ap.error('Bounded command and local output name required')
    log=root/(a.name+'.log');receipt_path=root/(a.name+'-guard.json')
    if log.exists() or receipt_path.exists():
        ap.error('Preserve existing guard evidence')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    start=time.monotonic();peak=samples=0;cause=None
    with log.open('wb') as output:
        proc=subprocess.Popen(command,stdout=output,stderr=subprocess.STDOUT,env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        try:
            while proc.poll() is None:
                try:
                    usage=rss(proc);peak=max(peak,usage);samples+=1
                except OSError:
                    if proc.poll() is None:
                        raise
                    break
                if usage>a.memory_mib*1024**2: cause='sampled_memory_limit'
                if time.monotonic()-start>a.seconds: cause='timeout'
                if cause:
                    proc.kill();break
                time.sleep(.1)
            code=proc.wait()
        except BaseException:
            proc.kill();proc.wait();raise
    receipt=dict(command=command,exit_code=code,termination=cause,elapsed_seconds=time.monotonic()-start,
        sampled_peak_child_rss_bytes=peak,rss_samples=samples,memory_limit_mib=a.memory_mib,
        timeout_seconds=a.seconds,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),
        scope='Operational resource bounds on the non-spawning scientific child; scientific claims depend on its output.')
    receipt_path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps(receipt,sort_keys=True))
    raise SystemExit(int(code!=0 or cause is not None))
