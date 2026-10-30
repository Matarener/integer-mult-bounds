#!/usr/bin/env python3
"""Parent-only serial immutable-stage runner; failed attempts remain charged."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
TIMEOUT = 180
RSS_CAP = 1024 ** 3
OUTPUT_CAP = 2 * 1024 ** 2
TOTAL_CAP = 1500


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def inventory(stage):
    rows = {}
    for path in sorted(stage.rglob('*')):
        if path.is_symlink():
            raise ValueError('Symlink in immutable stage')
        if path.is_file() and path.name != 'STAGE.json':
            rows[str(path.relative_to(stage))] = {
                'sha256': digest(path.read_bytes()),
                'mode': path.stat().st_mode & 0o777,
            }
    return rows


def group_rss(group):
    total = 0
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            raw = (path / 'stat').read_text()
            fields = raw[raw.rfind(')') + 2:].split()
            if int(fields[2]) == group:
                total += int(fields[21]) * os.sysconf('SC_PAGE_SIZE')
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage')
    parser.add_argument('job')
    parser.add_argument('label')
    args = parser.parse_args()
    for value in (args.stage, args.job, args.label):
        if not value or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in value):
            raise ValueError('Simple immutable stage/job/run names required')
    (HERE / 'runtime').mkdir(exist_ok=True)
    # A single parent owns this round; never wait behind another scientific run.
    with (HERE / 'runtime/science.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        stage = HERE / 'stages' / args.stage
        stage_raw = (stage / 'STAGE.json').read_bytes()
        declared = json.loads(stage_raw)
        before = inventory(stage)
        if before != declared['files']:
            raise ValueError('Stage bytes/modes differ from declared closure')
        jobs = json.loads((stage / 'JOBS.json').read_bytes())
        job = jobs[args.job]
        phase_raw = (HERE / 'control/EXECUTION-PHASE.json').read_bytes()
        phase = json.loads(phase_raw)
        cap = min(TOTAL_CAP, phase['aggregate_cap_seconds'])
        if cap not in (600, 1500):
            raise ValueError('Unrecognized parent budget phase')
        runs = HERE / 'runtime/runs'
        runs.mkdir(exist_ok=True)
        spent = 0.0
        for run in runs.iterdir():
            if not run.is_dir():
                continue
            receipt_path = run / 'receipt.json'
            if not receipt_path.exists():
                raise ValueError('Unclosed prior attempt: preserve and reconcile before another run')
            spent += json.loads(receipt_path.read_bytes())['wall_seconds']
        if spent >= cap:
            raise ValueError('Aggregate budget consumed')
        folder = runs / args.label
        folder.mkdir()
        runner_before = Path(__file__).read_bytes()
        if digest(runner_before) != declared['runner_sha256']:
            raise ValueError('Actual runner differs from frozen runner source')
        fraction_path = Path('/usr/lib/python3.12/fractions.py')
        fractions_before = fraction_path.read_bytes()
        env = os.environ.copy()
        for name in ('PYTHONPATH', 'PYTHONOPTIMIZE', 'PYTHONINSPECT', 'PYTHONSTARTUP', 'PYTHONPYCACHEPREFIX'):
            env.pop(name, None)
        env.update(PYTHONHASHSEED='0', LC_ALL='C.UTF-8', TZ='UTC', PYTHONDONTWRITEBYTECODE='1')
        command = ['/usr/bin/python3.12', '-B']
        if job.get('optimized', False):
            command.append('-O')
        command.extend([str(stage / 'integration/full_driver.py'),
                        '--output', str(folder / 'science'),
                        '--lanes', job['lanes']])
        if job.get('finite_only', False):
            command.append('--finite-only')
        usage = folder / 'usage.json'
        timed = ['/usr/bin/time', '-f', '{"user_seconds":%U,"system_seconds":%S,"kernel_max_rss_kib":%M,"exit":%x}', '-o', str(usage), '--', *command]
        started = {'command': command, 'stage_sha256': digest(stage_raw),
                   'runner_sha256': digest(runner_before), 'fractions_sha256': digest(fractions_before),
                   'budget_phase_sha256': digest(phase_raw), 'spent_before_seconds': spent,
                   'phase_cap_seconds': cap, 'job': args.job, 'label': args.label}
        (folder / 'START.json').write_text(json.dumps(started, indent=2, sort_keys=True) + '\n')
        start = time.monotonic()
        stop = None
        peak = 0
        with (folder / 'stdout.txt').open('wb') as out, (folder / 'stderr.txt').open('wb') as err:
            process = subprocess.Popen(timed, cwd=stage, env=env, stdout=out, stderr=err, start_new_session=True)
            try:
                while process.poll() is None:
                    peak = max(peak, group_rss(process.pid))
                    elapsed = time.monotonic() - start
                    if peak > RSS_CAP:
                        stop = 'sampled_group_rss_cap'
                    elif elapsed > min(TIMEOUT, cap - spent):
                        stop = 'wall_or_aggregate_cap'
                    elif max((folder / 'stdout.txt').stat().st_size, (folder / 'stderr.txt').stat().st_size) > OUTPUT_CAP:
                        stop = 'output_cap'
                    if stop:
                        os.killpg(process.pid, signal.SIGKILL)
                        break
                    time.sleep(0.05)
                code = process.wait()
            finally:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
        elapsed = time.monotonic() - start
        stdout, stderr = (folder / 'stdout.txt').read_bytes(), (folder / 'stderr.txt').read_bytes()
        if max(len(stdout), len(stderr)) > OUTPUT_CAP:
            stop = stop or 'output_cap'
        measurement = None
        if usage.exists():
            try:
                measurement = json.loads(usage.read_bytes())
            except json.JSONDecodeError:
                measurement = {'raw': usage.read_text()}
        unchanged = (inventory(stage) == before and (stage / 'STAGE.json').read_bytes() == stage_raw and
                     Path(__file__).read_bytes() == runner_before and fraction_path.read_bytes() == fractions_before)
        receipt = dict(started, exit=code, wall_seconds=elapsed, usage=measurement,
                       termination=stop, sampled_process_group_rss_bytes=peak,
                       source_bytes_and_modes_unchanged=unchanged,
                       stdout_sha256=digest(stdout), stdout_bytes=len(stdout),
                       stderr_sha256=digest(stderr), stderr_bytes=len(stderr),
                       python=sys.version, platform=platform.platform(),
                       status='PASS' if code == 0 and stop is None and not stderr and unchanged else 'STOP')
        (folder / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
        print(json.dumps(receipt, sort_keys=True), flush=True)
        if receipt['status'] != 'PASS':
            raise SystemExit(1)


if __name__ == '__main__':
    main()
