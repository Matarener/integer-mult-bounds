"""Direct script completion must release its ordinary POSIX descendants.

Builds on ywz65's PR2676 cancellation boundary and the isolated-test exit
controls. Prepared for roger-sato with substantial OpenAI Codex assistance.
Apache-2.0. No native Windows lifetime claim.
"""
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

SOLVER = '''import socket, subprocess, sys
from pathlib import Path
root, role = Path(sys.argv[1]), sys.argv[2]
child = None
if role == 'c':
    child = subprocess.Popen([sys.executable, __file__, str(root), 'g'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
with socket.socket(socket.AF_UNIX) as connection:
    connection.settimeout(20)
    connection.connect(str(root / 'observer'))
    connection.sendall(role.encode('ascii'))
    connection.recv(1)
if child is not None:
    child.wait(timeout=3)
'''

LEADER = '''import os, subprocess, sys, time
from pathlib import Path
root = Path(__file__).resolve().parent
(root / 'leader.pid').write_text(str(os.getpid()))
child = subprocess.Popen([sys.executable, str(root / 'solver.py'), str(root), 'c'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
deadline = time.monotonic() + 15
while not (root / 'leader-release').exists():
    if time.monotonic() >= deadline:
        raise SystemExit('fixture release timeout')
    time.sleep(.01)
if (root / 'join').exists():
    child.wait(timeout=3)
print('literal leader output')
raise SystemExit(7 if (root / 'fail').exists() else 0)
'''


@unittest.skipUnless(os.name == 'posix' and hasattr(socket, 'AF_UNIX'),
                     'requires POSIX process groups and Unix-domain sockets')
class ScriptExitCleanupTests(unittest.TestCase):
    def exercise(self, failed=False, joined=False, mutation=None):
        connections = {}
        runner = unrelated = None
        quiet = False
        with tempfile.TemporaryDirectory(prefix='script-exit-') as directory:
            root = Path(directory)
            source = (ROOT / 'scripts/run_parallel.py').read_text(encoding='utf-8')
            if mutation is not None:
                original = 'os.killpg(process.pid, signal.SIGKILL)'
                self.assertEqual(source.count(original), 1)
                source = source.replace(original, mutation)
            (root / 'run_parallel.py').write_text(source, encoding='utf-8')
            (root / 'solver.py').write_text(SOLVER, encoding='utf-8')
            (root / 'leader.py').write_text(LEADER, encoding='utf-8')
            if failed:
                (root / 'fail').touch()
            if joined:
                (root / 'join').touch()
            with socket.socket(socket.AF_UNIX) as observer:
                observer.settimeout(8)
                observer.bind(str(root / 'observer'))
                observer.listen(3)
                try:
                    unrelated = subprocess.Popen(
                        [sys.executable, str(root / 'solver.py'), str(root), 'u'],
                        start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    flags = ['-O'] if sys.flags.optimize else []
                    runner = subprocess.Popen(
                        [sys.executable, *flags, '-B', str(root / 'run_parallel.py'), 'leader.py'],
                        cwd=root, env=dict(os.environ, JOBS='1'),
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    for _ in range(3):
                        connection, _ = observer.accept()
                        connection.settimeout(8)
                        role = connection.recv(1).decode('ascii')
                        self.assertNotIn(role, connections)
                        connections[role] = connection
                    self.assertEqual(set(connections), {'c', 'g', 'u'})
                    if joined:
                        for role in ('g', 'c'):
                            connections[role].sendall(b'x')
                    (root / 'leader-release').touch()
                    out, err = runner.communicate(timeout=8)
                    if mutation and 'PermissionError' in mutation:
                        self.assertNotEqual(runner.returncode, 0)
                        self.assertIn(b'injected cleanup denial', err)
                        self.assertIn(b'Parallel script cleanup failed', err)
                        self.assertNotIn(b'PASS all', out)
                    else:
                        self.assertEqual(runner.returncode, 1 if failed else 0, err.decode())
                        self.assertIn(b'literal leader output\n', out)
                        self.assertIn(b'FAIL leader.py' if failed else b'Checked leader.py', out)
                        if failed:
                            self.assertIn(b'Failed: leader.py', err)
                            self.assertNotIn(b'PASS all', out)
                        else:
                            self.assertIn(b'PASS all 1 scripts', out)
                        for role in ('c', 'g'):
                            connections[role].settimeout(1)
                            try:
                                ended = connections[role].recv(1) == b''
                            except TimeoutError:
                                ended = False
                            self.assertTrue(ended, 'ordinary descendant survived runner completion: ' + role)
                        quiet = True
                    self.assertIsNone(unrelated.poll(), 'cleanup killed an unrelated process')
                    connections['u'].sendall(b'x')
                    self.assertEqual(unrelated.wait(timeout=3), 0)
                finally:
                    # A retained connection proves the fixture process has not
                    # finished; kill only its still-owned process group.
                    if not quiet and (root / 'leader.pid').exists():
                        try:
                            os.killpg(int((root / 'leader.pid').read_text()), signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                    for connection in connections.values():
                        connection.close()
                    if runner is not None:
                        if runner.poll() is None:
                            runner.kill()
                        runner.communicate(timeout=5)
                    if unrelated is not None:
                        if unrelated.poll() is None:
                            unrelated.kill()
                        unrelated.wait(timeout=5)

    def test_successful_leader_cleans_child_and_grandchild(self):
        self.exercise()

    def test_failed_leader_keeps_failure_and_cleans_descendants(self):
        self.exercise(failed=True)

    def test_joined_tree_preserves_success_and_output(self):
        self.exercise(joined=True)

    def test_parent_only_cleanup_mutant_is_detected(self):
        with self.assertRaisesRegex(AssertionError, 'ordinary descendant survived'):
            self.exercise(mutation='pass')

    def test_cleanup_denial_prevents_success_and_reports_retry_failure(self):
        self.exercise(mutation="raise PermissionError('injected cleanup denial')")


if __name__ == '__main__':
    unittest.main()
