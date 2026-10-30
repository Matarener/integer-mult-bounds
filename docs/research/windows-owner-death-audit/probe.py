#!/usr/bin/env python3
"""Observe abrupt owner death at pinned Windows gated-launch boundaries.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
Credits and the distinction between source execution and instrumentation are
in README.md. This audit does not repair or adopt either launcher.
"""
import argparse
import base64
import ctypes
from ctypes import wintypes
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
import types

HERE = Path(__file__).resolve().parent
PINS = {
    "research_package.py": "84a45190a6a96c20993a0d4a1045fbf24de660d2e6fef8f8a447bb3d1aa78db6",
    "owned_pipe.py": "01f597c8ecb955b2ef7faa8f0650e67c0eca5c0d5f6a817a181c536bef9c37aa",
}


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def load_sources():
    modules = []
    for name, expected in PINS.items():
        path = HERE / "sources" / name
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == expected, "source drift: " + name)
        module = types.ModuleType(name[:-3])
        module.__file__ = str(path)
        exec(compile(raw, str(path), "exec"), module.__dict__)
        modules.append(module)
    return modules


def publish(directory, name, **values):
    path = directory / (name + ".json")
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps({"pid": os.getpid(), "time": time.monotonic(),
                                     **values}), encoding="utf-8")
    os.replace(temporary, path)


def read_event(directory, name, timeout=15):
    path = directory / (name + ".json")
    deadline = time.monotonic() + timeout
    while not path.exists():
        require(time.monotonic() < deadline, "readiness timeout: " + name)
        time.sleep(0.01)
    return json.loads(path.read_text(encoding="utf-8"))


def wait_release(directory, name):
    deadline = time.monotonic() + 65
    while not (directory / name).exists():
        require(time.monotonic() < deadline, "fixture release timeout: " + name)
        time.sleep(0.01)


def python_argv():
    return [sys.executable, "-I", "-S", "-B", *(["-O"] if sys.flags.optimize else []),
            str(Path(__file__).resolve())]


class FunctionProxy:
    """Forward ctypes prototypes as well as calls; never truncate native handles."""
    def __init__(self, function, before=None, after=None):
        object.__setattr__(self, "function", function)
        object.__setattr__(self, "before", before)
        object.__setattr__(self, "after", after)

    def __getattr__(self, name):
        return getattr(self.function, name)

    def __setattr__(self, name, value):
        setattr(self.function, name, value)

    def __call__(self, *args):
        if self.before:
            self.before(args)
        result = self.function(*args)
        # A marker write can itself call Windows APIs. Preserve the native
        # thread-local error for the frozen caller, including failed OpenEvent.
        error = ctypes.get_last_error()
        try:
            if self.after:
                self.after(result, args)
        finally:
            ctypes.set_last_error(error)
        return result


def instrument_kernel(hooks):
    original = ctypes.WinDLL

    class Proxy:
        def __init__(self, api):
            self.api, self.cache = api, {}

        def __getattr__(self, name):
            if name not in self.cache:
                function = getattr(self.api, name)
                self.cache[name] = FunctionProxy(function, *hooks.get(name, (None, None)))
            return self.cache[name]

    ctypes.WinDLL = lambda *args, **kwargs: Proxy(original(*args, **kwargs))


def gate_worker(args):
    directory = Path(args.directory)

    def before_open(_):
        if args.phase == "before_event_open":
            publish(directory, "gate-before-open")
            wait_release(directory, "gate-continue")

    def after_open(result, _):
        publish(directory, "gate-open", succeeded=bool(result))

    def before_wait(call):
        publish(directory, "gate-wait", timeout_ms=call[1])

    instrument_kernel({"OpenEventW": (before_open, after_open),
                       "WaitForSingleObject": (before_wait, None)})
    code = base64.b64decode(args.gate_code, validate=True)
    sys.argv = ["-c", args.event, args.payload]
    # The original gate bytes execute after installing observation hooks.
    # The bypass control alone executes the explicitly recorded one-line mutant.
    exec(compile(code, "<pinned-or-labelled-mutant-gate>", "exec"), {"__name__": "__main__"})


def owner_worker(args):
    directory = Path(args.directory)
    shared, stream = load_sources()
    gate = shared._WINDOWS_GATE
    if args.mutation == "bypass-gate":
        needle = "if api.WaitForSingleObject(event, 30000) != 0:"
        require(gate.count(needle) == 1, "gate mutation no longer applies")
        gate = gate.replace(needle, "if False:  # deliberate gate-bypass control")
    shared._WINDOWS_GATE = gate
    real_popen = subprocess.Popen

    def interpose(argv, **kwargs):
        index = argv.index("-c")
        require(argv[index + 1] == gate, "unexpected gated launch")
        wrapped = [*python_argv(), "--internal", "gate", "--directory", str(directory),
                   "--phase", args.phase, "--gate-code",
                   base64.b64encode(gate.encode("utf-8")).decode("ascii"),
                   "--event", argv[index + 2], "--payload", argv[index + 3]]
        process = real_popen(wrapped, **kwargs)
        publish(directory, "gate-process", process_pid=process.pid,
                gate_sha256=hashlib.sha256(gate.encode("utf-8")).hexdigest())
        return process

    def before_assign(_):
        if args.phase in ("before_event_open", "before_assign", "resume"):
            publish(directory, "checkpoint", phase=args.phase)
            wait_release(directory, "owner-continue")

    def after_assign(result, _):
        require(result, "native assignment failed in fixture")
        publish(directory, "assignment", succeeded=True)
        if args.phase == "assigned":
            publish(directory, "checkpoint", phase=args.phase)
            wait_release(directory, "owner-continue")

    def after_release(result, _):
        require(result, "native gate release failed in fixture")
        publish(directory, "gate-release", succeeded=True)
        if args.phase == "released":
            publish(directory, "checkpoint", phase=args.phase)
            wait_release(directory, "owner-continue")

    def before_limits(call):
        if args.mutation == "no-kill-on-close":
            limits = call[2]._obj
            require(limits.Basic.Flags == 0x2000, "limit mutation no longer applies")
            limits.Basic.Flags = 0
            publish(directory, "mutated-limit", flags=0)

    instrument_kernel({"AssignProcessToJobObject": (before_assign, after_assign),
                       "SetEvent": (None, after_release),
                       "SetInformationJobObject": (before_limits, None)})
    shared.subprocess = types.SimpleNamespace(Popen=interpose,
                                              TimeoutExpired=subprocess.TimeoutExpired)
    stream.REAL_POPEN = interpose
    publish(directory, "owner-ready", target=args.target, phase=args.phase,
            mutation=args.mutation)
    command = [*python_argv(), "--internal", "workload", "--directory", str(directory)]
    if args.target == "shared":
        code = shared.run_windows_command(command, directory, 60, os.environ.copy())
    else:
        with stream.OwnedPopen(command, gate, cwd=directory,
                              stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL) as process:
            code = process.wait(timeout=60)
    require(code == 0, "joined workload failed")
    publish(directory, "owner-finished", returncode=code)


def workload_worker(args):
    directory = Path(args.directory)
    publish(directory, "workload-start")
    with subprocess.Popen([*python_argv(), "--internal", "leaf", "--directory", str(directory)],
                          stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL) as leaf:
        read_event(directory, "leaf-ready")
        publish(directory, "workload-ready", leaf_pid=leaf.pid)
        wait_release(directory, "finish")
        require(leaf.wait(timeout=10) == 0, "joined leaf failed")


class ProcessHandle:
    def __init__(self, pid):
        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        for name, result, arguments in (
            ("OpenProcess", wintypes.HANDLE, [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]),
            ("WaitForSingleObject", wintypes.DWORD, [wintypes.HANDLE, wintypes.DWORD]),
            ("TerminateProcess", wintypes.BOOL, [wintypes.HANDLE, wintypes.UINT]),
            ("GetExitCodeProcess", wintypes.BOOL, [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]),
            ("CloseHandle", wintypes.BOOL, [wintypes.HANDLE]),
        ):
            function = getattr(self.api, name)
            function.restype, function.argtypes = result, arguments
        self.handle = self.api.OpenProcess(0x00100001 | 0x1000, False, pid)
        require(self.handle, "could not retain live fixture process " + str(pid))
        self.pid = pid
        require(self.alive(), "fixture exited before its identity was retained")

    def alive(self):
        status = self.api.WaitForSingleObject(self.handle, 0)
        require(status in (0, 258), "native process wait failed")
        return status == 258

    def stopped(self, timeout=5):
        status = self.api.WaitForSingleObject(self.handle, round(timeout * 1000))
        require(status in (0, 258), "native bounded process wait failed")
        return status == 0

    def terminate(self):
        require(self.api.TerminateProcess(self.handle, 91), "fixture owner termination failed")
        require(self.stopped(), "fixture owner did not terminate")

    def exit_code(self):
        code = wintypes.DWORD()
        require(self.api.GetExitCodeProcess(self.handle, ctypes.byref(code)), "exit-code query failed")
        return code.value

    def close(self):
        require(self.api.CloseHandle(self.handle), "process handle close failed")


def judge(record):
    """Actual source properties; the same predicates must reject both mutants."""
    if record["phase"] != "released" and record["workload_before_release"]:
        return "workload_crossed_unreleased_gate"
    if record["phase"] in ("assigned", "released") and any(record["alive_after_owner_death"].values()):
        return "assigned_process_survived_owner_death"
    return None


def run_case(target, phase, mutation="none"):
    shared, stream = load_sources()
    record = {"target": target, "phase": phase, "mutation": mutation}
    handles = {}
    with tempfile.TemporaryDirectory(prefix="owner-death-") as temporary:
        directory = Path(temporary)
        command = [*python_argv(), "--internal", "owner", "--directory", temporary,
                   "--target", target, "--phase", phase, "--mutation", mutation]
        with (directory / "owner-output.txt").open("wb") as output:
            try:
                # This separate outer job is only fixture containment. It stays
                # open throughout every observation, including expected leaks.
                with stream.OwnedPopen(command, shared._WINDOWS_GATE, cwd=directory,
                                      stdin=subprocess.DEVNULL, stdout=output, stderr=output):
                    owner = read_event(directory, "owner-ready")
                    handles["owner"] = ProcessHandle(owner["pid"])
                    read_event(directory, "checkpoint")
                    gate = read_event(directory, "gate-process")
                    handles["gate"] = ProcessHandle(gate["process_pid"])
                    if phase == "before_event_open":
                        read_event(directory, "gate-before-open")
                        require(not (directory / "gate-open.json").exists(), "gate opened before checkpoint")
                    elif mutation != "bypass-gate":
                        event = read_event(directory, "gate-wait")
                        require(event["timeout_ms"] == 30000, "original gate timeout changed")
                        record["native_wait_ms"] = event["timeout_ms"]
                        record["gate_wait_started"] = event["time"]
                    record["workload_before_release"] = (directory / "workload-start.json").exists()
                    if phase == "resume":
                        require(not record["workload_before_release"], "positive gate control started early")
                        (directory / "owner-continue").touch()
                    if phase in ("released", "resume") or mutation == "bypass-gate":
                        workload = read_event(directory, "workload-ready")
                        leaf = read_event(directory, "leaf-ready")
                        handles["workload"] = ProcessHandle(workload["pid"])
                        handles["leaf"] = ProcessHandle(leaf["pid"])
                        require(workload["leaf_pid"] == leaf["pid"], "leaf identity mismatch")
                        record["workload_before_release"] = phase != "released" and phase != "resume"
                    require(all(h.alive() for h in handles.values()), "barrier process exited early")
                    record["observed_pids"] = {name: h.pid for name, h in handles.items()}
                    if phase == "resume":
                        (directory / "finish").touch()
                        require(handles["owner"].stopped(15), "joined owner did not return")
                        require(handles["owner"].exit_code() == 0, "joined owner failed")
                        record["joined_return"] = 0
                        record["observation_boundary"] = "joined_owner_return"
                        record["alive_after_owner_death"] = {name: h.alive() for name, h in handles.items()}
                        require(not any(record["alive_after_owner_death"].values()), "joined processes survive")
                    else:
                        handles["owner"].terminate()
                        record["observation_boundary"] = "forced_owner_termination"
                        record["owner_terminated_at"] = time.monotonic()
                        if phase == "before_event_open":
                            (directory / "gate-continue").touch()
                            require(handles["gate"].stopped(), "gate survived failed event open")
                            event = read_event(directory, "gate-open")
                            require(not event["succeeded"], "event unexpectedly survived all owner handles")
                            record["event_open_after_owner_death"] = False
                        elif mutation == "none" and phase in ("assigned", "released"):
                            require(all(h.stopped() for name, h in handles.items() if name != "owner"),
                                    "owned process did not stop")
                        else:
                            time.sleep(0.5)
                        record["alive_after_owner_death"] = {name: h.alive() for name, h in handles.items()}
                        record["observation_seconds_after_owner_death"] = time.monotonic() - record["owner_terminated_at"]
                        if phase == "before_assign" and mutation == "none":
                            require(record["alive_after_owner_death"]["gate"], "unassigned waiter did not survive")
                            require(handles["gate"].stopped(35), "unassigned gate did not time out")
                            elapsed = time.monotonic() - record["gate_wait_started"]
                            require(29 <= elapsed <= 45, "unexpected original gate-wait duration")
                            record["gate_exit_seconds_from_native_wait"] = elapsed
                            record["gate_exit_code"] = handles["gate"].exit_code()
                            require(record["gate_exit_code"] == 1, "expected gate timeout exception")
                        if mutation == "none" and phase != "released":
                            require(not (directory / "workload-start.json").exists(), "unreleased workload started")
                    rejected = judge(record)
                    if mutation == "none":
                        require(rejected is None, "source observation rejected: " + str(rejected))
                    else:
                        expected = ("workload_crossed_unreleased_gate" if mutation == "bypass-gate"
                                    else "assigned_process_survived_owner_death")
                        require(rejected == expected, "mutation escaped its actual observation predicate")
                    record["rejected_rule"] = rejected
                    record["observed_before_outer_cleanup"] = True
                record["all_stopped_after_outer_cleanup"] = all(h.stopped() for h in handles.values())
                require(record["all_stopped_after_outer_cleanup"], "fixture teardown incomplete")
            finally:
                for handle in handles.values():
                    handle.close()
        record["owner_output"] = (directory / "owner-output.txt").read_text(encoding="utf-8", errors="replace")
        record["events"] = {p.stem: json.loads(p.read_text(encoding="utf-8"))
                            for p in sorted(directory.glob("*.json"))}
        if phase in ("released", "resume") and mutation == "none":
            require(record["events"]["assignment"]["time"]
                    < record["events"]["workload-start"]["time"],
                    "workload started before successful assignment")
        if phase == "before_assign" and mutation == "none" and target == "shared":
            require("replay ownership gate was not released" in record["owner_output"],
                    "missing actual gate-timeout diagnostic")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--target", choices=("shared", "stream", "all"), default="all")
    parser.add_argument("--phase", default="all")
    parser.add_argument("--mutation", default="none")
    parser.add_argument("--internal", choices=("owner", "gate", "workload", "leaf"))
    parser.add_argument("--directory")
    parser.add_argument("--gate-code")
    parser.add_argument("--event")
    parser.add_argument("--payload")
    args = parser.parse_args()
    if args.internal:
        if args.internal == "gate":
            gate_worker(args)
        elif args.internal == "owner":
            owner_worker(args)
        elif args.internal == "workload":
            workload_worker(args)
        else:
            publish(Path(args.directory), "leaf-ready")
            wait_release(Path(args.directory), "finish")
        return
    require(os.name == "nt", "native Windows required; no Windows coverage was executed")
    load_sources()  # Authenticate every executable source before starting fixtures.
    targets = ("shared", "stream") if args.target == "all" else (args.target,)
    cases = [(phase, "none") for phase in ("before_event_open", "before_assign", "assigned", "released", "resume")]
    cases += [("before_assign", "bypass-gate"), ("released", "no-kill-on-close")]
    if args.phase != "all":
        cases = [(args.phase, args.mutation)]
    report = {"schema": 1, "status": "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(),
              "platform": platform.platform(), "python": sys.version, "optimized": sys.flags.optimize,
              "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "source_sha256": PINS, "windows_observations_executed": True, "cases": []}
    for target in targets:
        for phase, mutation in cases:
            result = run_case(target, phase, mutation)
            report["cases"].append(result)
            print("PASS", target, phase, mutation, flush=True)
    report["status"] = "CONFIRMED_WINDOWS_OWNER_DEATH_BOUNDARIES"
    report["completed_utc"] = datetime.now(timezone.utc).isoformat()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report["status"], "cases=" + str(len(report["cases"])))


if __name__ == "__main__":
    main()
