#!/usr/bin/env python3
"""Check an opt-in streaming owner against the frozen Windows Git reader.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
Readiness/lifetime design follows JoyboyBrian's POSIX reader controls and
ywz65's native process-handle and Job Object controls; see README.md.
"""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import tempfile
import time
import types
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
TIMEOUT = 0.8
PAYLOAD = b"\0\xff\r\n"
OID = "a" * 40


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def python():
    return [sys.executable, "-I", "-W", "error", "-B"] + (["-O"] if sys.flags.optimize else [])


def write_json(path, value):
    pending = path.with_suffix(".pending")
    pending.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
    pending.replace(path)


def wait_for(predicate, seconds=20):
    until = time.monotonic() + seconds
    while not predicate():
        if time.monotonic() >= until:
            raise AssertionError("fixture readiness/completion timed out")
        time.sleep(0.01)


def load_baseline():
    source = HERE / "baseline/research_package.py"
    rows = json.loads((HERE / "SOURCES.json").read_bytes())["files"]
    expected = next(r["sha256"] for r in rows if r["path"] == "scripts/research_package.py")
    require(hashlib.sha256(source.read_bytes()).hexdigest() == expected,
            "frozen source bytes differ from the recorded Git source")
    module = types.ModuleType("frozen_reader")
    module.__file__ = str(source)
    # Compile the authenticated bytes, never a possibly stale adjacent .pyc.
    exec(compile(source.read_bytes(), str(source), "exec"), module.__dict__)
    module.subprocess = types.SimpleNamespace(**vars(subprocess))
    return module, expected


def load_adapter():
    source = HERE / "owned_pipe.py"
    module = types.ModuleType("owned_pipe")
    module.__file__ = str(source)
    exec(compile(source.read_bytes(), str(source), "exec"), module.__dict__)
    return module


class ProcessHandle:
    """Retain the actual process object, including after its PID is reused."""
    def __init__(self, pid):
        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        for name, result, args in (
            ("OpenProcess", wintypes.HANDLE, [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]),
            ("WaitForSingleObject", wintypes.DWORD, [wintypes.HANDLE, wintypes.DWORD]),
            ("TerminateProcess", wintypes.BOOL, [wintypes.HANDLE, wintypes.UINT]),
            ("CloseHandle", wintypes.BOOL, [wintypes.HANDLE]),
        ):
            fn = getattr(self.api, name)
            fn.restype, fn.argtypes = result, args
        self.handle = self.api.OpenProcess(0x00100001, False, pid)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())

    def alive(self):
        result = self.api.WaitForSingleObject(self.handle, 0)
        require(result in (0, 258), "native process observation failed")
        return result == 258

    def stop(self):
        if self.alive() and not self.api.TerminateProcess(self.handle, 1):
            require(not self.alive(), "native fixture termination failed")
        require(self.api.WaitForSingleObject(self.handle, 5000) == 0,
                "fixture process failed to terminate")

    def close(self):
        require(self.api.CloseHandle(self.handle), "native handle close failed")


def child(directory):
    write_json(directory / "child.json", {"pid": os.getpid()})
    # Self-exit is a final guard, far beyond the measured observation window.
    wait_for((directory / "release-child").exists, 60)


def leader(directory, mode, has_child):
    write_json(directory / "leader.json", {"pid": os.getpid()})
    descendant = None
    if has_child:
        # Explicit standard streams make handle inheritance part of the fixture.
        descendant = subprocess.Popen([*python(), str(HERE / "verify.py"), "--child", str(directory)],
                                      stdin=sys.stdin, stdout=sys.stdout, stderr=subprocess.DEVNULL)
        wait_for((directory / "child.json").exists)
    (directory / "ready").touch()
    wait_for((directory / "release-leader").exists)
    if mode == "write":
        os._exit(0)
    while sys.stdin.buffer.read(1) not in (b"\0", b"\n", b""):
        pass
    reply = OID.encode() + b" blob 4\n" + PAYLOAD + b"\n"
    pieces = {"header": b"", "payload": reply[:50], "terminator": reply[:-1],
              "malformed": b"bad\n"}
    sys.stdout.buffer.write(pieces.get(mode, reply))
    sys.stdout.buffer.flush()
    if mode in ("header", "payload", "terminator") and not has_child:
        time.sleep(60)  # The reader's direct-child watchdog must end this.
    if mode == "early":
        time.sleep(60)
    if mode == "suspended":
        while sys.stdin.buffer.read(1) not in (b"\0", b"\n", b""):
            pass
        sys.stdout.buffer.write(reply)
        sys.stdout.buffer.flush()
    # Intentional unjoined process exit is the behavior under investigation.
    os._exit(0)


def worker(directory, mode, has_child, repaired=False):
    baseline, _ = load_baseline()
    baseline.GIT_BLOB_RESPONSE_TIMEOUT = TIMEOUT
    adapter = load_adapter()
    real_popen = ((lambda argv, **kwargs: adapter.OwnedPopen(argv, baseline._WINDOWS_GATE, **kwargs))
                  if repaired else subprocess.Popen)
    real_stop = baseline._stop_git_blob_process
    calls = []

    def start(argv, **kwargs):
        calls.append(argv)
        if mode == "fallback" and len(calls) == 1:
            return real_popen([*python(), "-c", "raise SystemExit(129)"], **kwargs)
        process = real_popen([*python(), str(HERE / "verify.py"), "--leader",
                             str(directory), mode, str(int(has_child))], **kwargs)
        write_json(directory / "launcher.json", {"pid": process.pid})
        wait_for((directory / "observed").exists)
        (directory / "release-leader").touch()
        return process

    def stop(process):
        real_stop(process)
        (directory / "watchdog-fired").touch()

    result = {}
    with patch.object(baseline.subprocess, "Popen", side_effect=start), \
            patch.object(baseline, "_stop_git_blob_process", side_effect=stop):
        try:
            specs = ["x" * 2_000_000] if mode == "write" else ["HEAD:first"]
            if mode == "suspended":
                specs.append("HEAD:second")
            rows = baseline.git_blobs(directory, specs)
            if mode in ("early", "suspended"):
                result["first_exact"] = next(rows) == (OID, PAYLOAD)
                if mode == "suspended":
                    time.sleep(1.2)  # Longer than the per-response deadline.
                    result["second_exact"] = next(rows) == (OID, PAYLOAD)
                    result["exhausted"] = list(rows) == []
                rows.close()
            else:
                result["exact"] = list(rows) == [(OID, PAYLOAD)]
        except Exception as error:
            result["error"] = type(error).__name__
        result["calls"] = len(calls)
    write_json(directory / "result.json", result)


def owned_worker(directory, mode):
    baseline, _ = load_baseline()
    argv = [*python(), str(HERE / "verify.py"), "--worker", str(directory), mode, "1"]
    result = {}
    try:
        result["code"] = baseline.run_windows_command(argv, directory, 15, os.environ.copy())
    except ValueError as error:
        result["error"] = str(error)
    write_json(directory / "owned-result.json", result)


def assignment_failure_control():
    baseline, _ = load_baseline()
    adapter = load_adapter()
    real_dll = ctypes.WinDLL
    launched = []

    def denied(*args):
        ctypes.set_last_error(5)
        return 0

    class DeniedAssignment:
        def __init__(self, *args, **kwargs):
            self.api = real_dll(*args, **kwargs)

        def __getattr__(self, name):
            return denied if name == "AssignProcessToJobObject" else getattr(self.api, name)

    def launch(*args, **kwargs):
        process = subprocess.Popen(*args, **kwargs)
        launched.append(process)
        return process

    with tempfile.TemporaryDirectory(prefix="denied stream owner ") as tmp:
        marker = Path(tmp) / "command-ran"
        argv = [*python(), "-c", "from pathlib import Path; import sys; Path(sys.argv[1]).touch()", str(marker)]
        with patch.object(ctypes, "WinDLL", DeniedAssignment), patch.object(adapter, "REAL_POPEN", launch):
            try:
                with adapter.OwnedPopen(argv, baseline._WINDOWS_GATE,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE):
                    raise AssertionError("assignment failure yielded a live reader")
            except OSError as error:
                require(error.winerror == 5, "wrong assignment error")
        require(len(launched) == 1 and launched[0].poll() is not None, "unassigned gate survived")
        require(not marker.exists(), "requested command ran before ownership")
        require(launched[0].stdin.closed and launched[0].stdout.closed, "setup leaked stream handles")
    return True


def exercise(mode, has_child=True, owned=False, repaired=False):
    handles = []
    with tempfile.TemporaryDirectory(prefix="git lifetime ") as tmp:
        directory = Path(tmp)
        args = (["--owned-worker", tmp, mode] if owned else
                ["--worker", tmp, mode, str(int(has_child)), str(int(repaired))])
        with (directory / "worker.log").open("wb") as log:
            process = subprocess.Popen([*python(), str(HERE / "verify.py"), *args], stdout=log, stderr=log)
            try:
                wait_for(lambda: (directory / "ready").exists() or process.poll() is not None)
                require((directory / "ready").exists(),
                        "worker exited before readiness: " + (directory / "worker.log").read_text())
                if sys.platform == "win32":
                    for filename in (["leader.json", "child.json"] if has_child else ["leader.json"]):
                        pid = json.loads((directory / filename).read_bytes())["pid"]
                        handles.append(ProcessHandle(pid))
                    if repaired:
                        handles.append(ProcessHandle(json.loads((directory / "launcher.json").read_bytes())["pid"]))
                    require(all(h.alive() for h in handles), "process exited before retained observation")
                (directory / "observed").touch()
                stall = mode in ("header", "payload", "terminator", "write")
                if stall and has_child and not owned and not repaired:
                    wait_for((directory / "watchdog-fired").exists)
                    wait_for(lambda: not handles[0].alive())
                    time.sleep(1.2)  # Reader still blocked after its watchdog has fired.
                    evidence = {"leader_exited": not handles[0].alive(),
                                "child_alive_before_cleanup": handles[1].alive(),
                                "reader_pending_after_watchdog": process.poll() is None,
                                "no_result_before_cleanup": not (directory / "result.json").exists()}
                    require(all(evidence.values()), "expected descendant-held-pipe gap was not observed")
                    # Only now release the pipe and check the deferred exception.
                    handles[1].stop()
                else:
                    process.wait(timeout=22)
                    evidence = {}
                process.wait(timeout=5)
                require(process.returncode == 0, "worker failed: " + (directory / "worker.log").read_text())
                if owned:
                    wait_for(lambda: not any(h.alive() for h in handles))
                    result = json.loads((directory / "owned-result.json").read_bytes())
                    expected = {"error": "verification timed out"} if stall else {"code": 0}
                    require(result == expected, "whole-command control returned the wrong status")
                    evidence["all_handles_stopped_before_cleanup"] = True
                    if stall:
                        require(not (directory / "result.json").exists(), "reader unexpectedly returned before owner timeout")
                else:
                    result = json.loads((directory / "result.json").read_bytes())
                    expected = ({"error": "TimeoutExpired", "calls": 1} if stall else
                                {"error": "ValueError", "calls": 1} if mode == "malformed" else
                                {"first_exact": True, "calls": 1} if mode == "early" else
                                {"first_exact": True, "second_exact": True, "exhausted": True, "calls": 1}
                                if mode == "suspended" else
                                {"exact": True, "calls": 2 if mode == "fallback" else 1})
                    require(result == expected, "reader result differs: " + repr(result))
                    if repaired:
                        wait_for(lambda: not any(h.alive() for h in handles))
                        evidence["all_handles_stopped_before_cleanup"] = True
                    elif has_child and not stall:
                        require(not handles[0].alive(), "leader was not reaped")
                        require(handles[1].alive(), "expected post-return descendant leak was not observed")
                        evidence.update(leader_exited=True, child_alive_before_cleanup=True)
                return {"mode": mode, "has_child": has_child, "owned_command": owned, "stream_adapter": repaired,
                        "observation": evidence, "result": result}
            finally:
                # Failure containment is never counted as successful reader cleanup.
                (directory / "release-child").touch()
                (directory / "observed").touch()
                for handle in reversed(handles):
                    try:
                        handle.stop()
                    finally:
                        handle.close()
                if os.name == "posix" and (directory / "leader.json").exists():
                    pid = json.loads((directory / "leader.json").read_bytes())["pid"]
                    try:
                        os.killpg(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-windows", action="store_true",
                        help="fail rather than run only portable controls on another OS")
    args = parser.parse_args()
    require(not args.require_windows or sys.platform == "win32", "native Windows execution required")
    baseline, source_hash = load_baseline()
    rows = [exercise(mode, has_child=False) for mode in
            ("header", "payload", "terminator", "success", "malformed", "suspended")]
    with tempfile.TemporaryDirectory(prefix="real git blobs ") as tmp:
        root = Path(tmp)
        baseline.git(root, "init", "-q")
        (root / "data").write_bytes(PAYLOAD)
        oid = baseline.git(root, "hash-object", "-w", "--", "data").decode().strip()
        require(list(baseline.git_blobs(root, [oid, oid])) == [(oid, PAYLOAD)] * 2,
                "real Git exact binary/duplicate control failed")
    if sys.platform == "win32":
        rows += [exercise(mode) for mode in
                 ("header", "payload", "terminator", "write", "success", "malformed", "early", "fallback")]
        rows += [exercise(mode, owned=True) for mode in ("header", "success")]
        rows += [exercise(mode, repaired=True) for mode in
                 ("header", "payload", "terminator", "write", "success", "malformed", "early", "fallback", "suspended")]
        assignment_failure_control()
        adapter = load_adapter()
        baseline.subprocess.Popen = lambda argv, **kw: adapter.OwnedPopen(argv, baseline._WINDOWS_GATE, **kw)
        with tempfile.TemporaryDirectory(prefix="owned real Git ") as tmp:
            root = Path(tmp)
            baseline.git(root, "init", "-q")
            (root / "data").write_bytes(PAYLOAD)
            oid = baseline.git(root, "hash-object", "-w", "--", "data").decode().strip()
            require(list(baseline.git_blobs(root, [oid, oid])) == [(oid, PAYLOAD)] * 2,
                    "owned real Git binary/duplicate control failed")
    result = {"status": ("PASS_WINDOWS_GIT_STREAM_OWNERSHIP" if sys.platform == "win32" else
                         "PASS_PORTABLE_CONTROLS_WINDOWS_NOT_RUN"), "source_sha256": source_hash,
              "implementation_hashes": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                                        for name in ("verify.py", "owned_pipe.py")},
              "platform": platform.platform(), "python": sys.version,
              "optimized_driver_and_workers": bool(sys.flags.optimize), "response_timeout_seconds": TIMEOUT,
              "windows_observations_executed": sys.platform == "win32",
              "assignment_failure_control_executed": sys.platform == "win32",
              "real_git_binary_duplicate_control": True, "cases": rows}
    if args.output:
        write_json(args.output, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        child(Path(sys.argv[2]))
    elif len(sys.argv) > 1 and sys.argv[1] == "--leader":
        leader(Path(sys.argv[2]), sys.argv[3], bool(int(sys.argv[4])))
    elif len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(Path(sys.argv[2]), sys.argv[3], bool(int(sys.argv[4])),
               bool(int(sys.argv[5])) if len(sys.argv) > 5 else False)
    elif len(sys.argv) > 1 and sys.argv[1] == "--owned-worker":
        owned_worker(Path(sys.argv[2]), sys.argv[3])
    else:
        main()
