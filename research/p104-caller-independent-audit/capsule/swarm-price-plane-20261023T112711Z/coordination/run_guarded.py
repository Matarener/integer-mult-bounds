#!/usr/bin/env python3
"""Serial local research executor with sampled descendant RSS and timeout."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def tree_memory(root_pid):
    records = {}
    for p in Path('/proc').iterdir():
        if not p.name.isdecimal():
            continue
        try:
            info = (p/'stat').read_text().rsplit(')', 1)[1].split()
            records[int(p.name)] = (int(info[1]), int(info[21]) * os.sysconf('SC_PAGE_SIZE'))
        except (OSError, ValueError, IndexError):
            continue
    todo = [root_pid]
    seen = set()
    while todo:
        pid = todo.pop()
        if pid in seen:
            continue
        seen.add(pid)
        todo.extend(p for p,(parent,_) in records.items() if parent == pid)
    return sum(records.get(p,(0,0))[1] for p in seen), len(seen)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--name', required=True)
    ap.add_argument('--seconds', type=float, default=150)
    ap.add_argument('--memory-mib', type=int, default=1024)
    ap.add_argument('--cwd', type=Path)
    ap.add_argument('command', nargs=argparse.REMAINDER)
    args = ap.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command or args.seconds <= 0 or not (0 < args.memory_mib <= 1024):
        ap.error('command, positive timeout, and memory <= 1024 MiB required')
    workspace = Path(__file__).resolve().parents[1]
    out = workspace/'runs'/args.name
    out.mkdir(exist_ok=False)
    cwd = (args.cwd or workspace).resolve()
    lock = (workspace/'coordination'/'heavy.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    started = time.monotonic()
    env = dict(os.environ)
    env.update(PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    peak = 0
    samples = 0
    cause = None
    with (out/'stdout.log').open('wb') as log:
        proc = subprocess.Popen(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True)
        try:
            while proc.poll() is None:
                rss, count = tree_memory(proc.pid)
                peak = max(peak, rss)
                samples += 1
                if rss > args.memory_mib * 1024**2:
                    cause = 'memory_limit'
                elif time.monotonic() - started > args.seconds:
                    cause = 'timeout'
                if cause:
                    os.killpg(proc.pid, signal.SIGTERM)
                    try:
                        proc.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid, signal.SIGKILL)
                    break
                time.sleep(0.1)
            code = proc.wait()
        except BaseException:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
            raise
    receipt = {'schema':'serial-research-run/v1','command':command,'cwd':str(cwd),
               'exit_code':code,'termination':cause,'elapsed_seconds':time.monotonic()-started,
               'sampled_peak_descendant_rss_bytes':peak,'rss_samples':samples,
               'memory_limit_mib':args.memory_mib,'timeout_seconds':args.seconds,
               'python':sys.version,'log_sha256':hashlib.sha256((out/'stdout.log').read_bytes()).hexdigest(),
               'scope':'Fresh command execution only; scientific claim determined by reviewed output.'}
    (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))
    return 0 if code == 0 and not cause else 1


if __name__ == '__main__':
    raise SystemExit(main())
