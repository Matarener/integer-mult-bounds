"""Parent-only delivery checks charged to the existing round ledger.

This orchestration is separate from the frozen performance harness and never
creates performance samples. Jobs are exact registered package checks.
"""
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

HERE = Path(__file__).resolve().parent


def content_digest(path):
    hasher = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            hasher.update(block)
    return hasher.hexdigest()


def inventory(package):
    result = {}
    for path in sorted(package.rglob('*')):
        if path.is_symlink():
            raise RuntimeError('Symlinked publication source')
        if path.is_file():
            result[str(path.relative_to(package))] = [content_digest(path),
                                                       path.stat().st_mode & 0o777]
    return result


def descendants(root, known):
    """Track nested new sessions too; retain pid/start identity against reuse."""
    processes = {}
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            raw = (path / 'stat').read_text()
            fields = raw[raw.rfind(')') + 2:].split()
            processes[int(path.name)] = (int(fields[1]), int(fields[2]), int(fields[19]),
                                         int(fields[21]) * os.sysconf('SC_PAGE_SIZE'))
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
    active = {pid for pid, start in known.items() if pid in processes and processes[pid][2] == start}
    if root in processes and (root not in known or processes[root][2] == known[root]):
        active.add(root)
    while True:
        added = {pid for pid, row in processes.items() if row[0] in active} - active
        if not added:
            break
        active.update(added)
    for pid in active:
        known[pid] = processes[pid][2]
    groups = {processes[pid][1] for pid in active}
    return sum(processes[pid][3] for pid in active), groups


def kill_descendants(root, known, sig):
    _, groups = descendants(root, known)
    for group in groups:
        if group == os.getpgrp():
            raise RuntimeError('Refusing to signal parent process group')
        try:
            os.killpg(group, sig)
        except ProcessLookupError:
            pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job', choices=('finite', 'finite-O', 'full', 'canonical', 'registry'))
    parser.add_argument('label')
    parser.add_argument('--repository', type=Path, default=HERE / 'publication-repo')
    args = parser.parse_args()
    if not args.label or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in args.label):
        raise ValueError('Simple new run label required')
    repository = args.repository.resolve()
    package = repository / 'research/h25-bookkeeping'
    before = inventory(package)
    with (HERE / 'runtime/science.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        runs = HERE / 'runtime/runs'
        spent = 0.0
        for folder in runs.iterdir():
            if folder.is_dir():
                if not (folder / 'receipt.json').exists():
                    raise ValueError('Unclosed prior scientific attempt')
                spent += json.loads((folder / 'receipt.json').read_bytes())['wall_seconds']
        cap = min(1500, json.loads((HERE / 'control/EXECUTION-PHASE.json').read_bytes())['aggregate_cap_seconds'])
        if spent >= cap:
            raise ValueError('Round scientific budget consumed')
        folder = runs / args.label
        folder.mkdir()
        command = ['/usr/bin/python3.12', '-B']
        if args.job == 'finite-O':
            command.append('-O')
        if args.job == 'registry':
            command.extend([str(repository / 'scripts/research_package.py'), '--package', 'research/h25-bookkeeping'])
        else:
            entry = {'finite': 'verify.py', 'finite-O': 'verify.py', 'full': 'verify_full.py',
                     'canonical': 'check_artifacts.py'}[args.job]
            command.append(str(package / entry))
        env = os.environ.copy()
        for name in ('PYTHONPATH', 'PYTHONOPTIMIZE', 'PYTHONINSPECT', 'PYTHONSTARTUP', 'PYTHONPYCACHEPREFIX'):
            env.pop(name, None)
        env.update(PYTHONHASHSEED='0', LC_ALL='C.UTF-8', TZ='UTC', PYTHONDONTWRITEBYTECODE='1')
        usage_path = folder / 'usage.json'
        timed = ['/usr/bin/time', '-f', '{"user_seconds":%U,"system_seconds":%S,"kernel_max_rss_kib":%M,"exit":%x}',
                 '-o', str(usage_path), '--', *command]
        started = {'label': args.label, 'job': 'publication-' + args.job, 'command': command,
                   'stage_sha256': hashlib.sha256((package / 'payload/STAGE.json').read_bytes()).hexdigest(),
                   'publication_source_inventory_sha256': hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest(),
                   'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   'spent_before_seconds': spent, 'phase_cap_seconds': cap,
                   'performance_sample': False}
        (folder / 'START.json').write_text(json.dumps(started, indent=2, sort_keys=True) + '\n')
        start = time.monotonic()
        peak = 0
        stop = None
        known = {}
        with (folder / 'stdout.txt').open('wb') as out, (folder / 'stderr.txt').open('wb') as err:
            process = subprocess.Popen(timed, cwd=repository, env=env, stdout=out, stderr=err, start_new_session=True)
            try:
                # Capture the unreaped child generation before poll/wait can
                # release its PID, including for a very short failed command.
                descendants(process.pid, known)
                if process.pid not in known:
                    raise RuntimeError('Could not capture original publication process identity')
                while process.poll() is None:
                    rss, _ = descendants(process.pid, known)
                    peak = max(peak, rss)
                    if peak > 1024 ** 3:
                        stop = 'sampled_descendant_tree_rss_cap'
                    elif time.monotonic() - start > min(180, cap - spent):
                        stop = 'outer_wall_or_aggregate_cap'
                    elif max((folder / 'stdout.txt').stat().st_size, (folder / 'stderr.txt').stat().st_size) > 2 * 1024 ** 2:
                        stop = 'output_cap'
                    if stop:
                        kill_descendants(process.pid, known, signal.SIGTERM)
                        break
                    time.sleep(0.05)
                try:
                    code = process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    kill_descendants(process.pid, known, signal.SIGKILL)
                    code = process.wait()
            finally:
                kill_descendants(process.pid, known, signal.SIGKILL)
                process.wait()
        elapsed = time.monotonic() - start
        stdout_path, stderr_path = folder / 'stdout.txt', folder / 'stderr.txt'
        stdout_bytes, stderr_bytes = stdout_path.stat().st_size, stderr_path.stat().st_size
        if max(stdout_bytes, stderr_bytes) > 2 * 1024 ** 2:
            stop = stop or 'output_cap'
        usage = None
        if usage_path.exists():
            raw = usage_path.read_text()
            try:
                usage = json.loads(raw.strip().splitlines()[-1])
            except (ValueError, IndexError):
                usage = {'raw': raw}
        unchanged = inventory(package) == before
        receipt = dict(started, status='PASS' if code == 0 and stop is None and stderr_bytes == 0 and unchanged else 'STOP',
                       exit=code, termination=stop, wall_seconds=elapsed, usage=usage,
                       source_bytes_and_modes_unchanged=unchanged, sampled_descendant_tree_rss_bytes=peak,
                       stdout_sha256=content_digest(stdout_path), stdout_bytes=stdout_bytes,
                       stderr_sha256=content_digest(stderr_path), stderr_bytes=stderr_bytes,
                       inner_scientific_guard='Unchanged v4 runner, explicit external HERE and150s cap, each child1GiB; outer packaging envelope180s')
        (folder / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
        print(json.dumps(receipt, sort_keys=True))
        if receipt['status'] != 'PASS':
            raise SystemExit(1)


if __name__ == '__main__':
    main()
