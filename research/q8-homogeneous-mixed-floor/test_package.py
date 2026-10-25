"""Behavioral fault and boundary controls, including optimized execution."""
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as m
import verify as v

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rejects(call):
    try:
        call()
    except ValueError:
        return
    raise ValueError('bad behavior accepted')


def arithmetic_faults():
    bad = ((1, 1, 2, 3), *m.TABLE[1:])
    with patch.object(m, 'TABLE', bad):
        rejects(v.arithmetic)
    original = m.call_matrices

    def wrong_h(roles, word):
        x, y, ell, ei, ej, _h, hp = original(roles, word)
        return x, y, ell, ei, ej, ell, hp

    with patch.object(m, 'call_matrices', wrong_h):
        rejects(lambda: v.check_word(1, ((2, 1, 1), (1, 1, 1))))
    with patch.object(v.oracle, 'action', return_value=(0,)):
        rejects(lambda: v.check_word(1, ((1, 1, 1),)))
    with patch.object(m, 'allowed_counts', return_value=True):
        rejects(v.count_controls)


def domain_faults():
    for roles, word in ((0, ()), (9, ()), (True, ()), (1, []),
                        (1, ((3, 1, 1),)), (1, ((1, 0, 1),)),
                        (2, ((1, 1, 2),)), (1, ((1, True, 1),)),
                        (1, ((1, 1, 1),) * 25)):
        rejects(lambda roles=roles, word=word: m.endpoint(roles, word))
    for value in (0, True, 1_000_001):
        rejects(lambda value=value: m.lower_bound(value))
    rejects(lambda: m.allowed_counts(4, -1, 4))
    rejects(lambda: m.mul(256, 1))
    rejects(lambda: m.bx((1,), ()))


def rank_hypothesis_controls():
    # Without X_jY_j=0, the boundary ranks need not fit inside n_j.
    require(m.rank((1,)) + m.rank((1,)) > 1, 'zero-product hypothesis control')
    # Without invertibility of K_i, the quadratic rank lower bound fails.
    require(m.bm(m.bm((1,), (0,)), (1,)) == (0,), 'invertible-block control')
    # Without X_iY_i=I_t, the homogeneous Sylvester input rank is absent.
    require(m.bm((0,), (1,)) == (0,), 'homogeneous hypothesis control')
    # A 2/2 endpoint is deliberately outside the homogeneous zero-block premise.
    word = tuple((g, 1 << a, 1 << a) for a, g in enumerate((1, 1, 2, 2))
                 for _ in range(3))
    x, y, _ell, _ei, ej, _h, _hp = m.call_matrices(4, word)
    require(m.rank(m.bm(m.bm(x, ej), y)) == 2, 'mixed-target scope control')


def copy_payload(destination):
    names = [*v.source_hashes(), 'RESULT.json']
    for name in names:
        source = ROOT / name
        before = source.lstat()
        require(stat.S_ISREG(before.st_mode) and not source.is_symlink()
                and before.st_uid == os.getuid(), 'source type and owner')
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(source.read_bytes())
        after = target.lstat()
        require((before.st_dev, before.st_ino) != (after.st_dev, after.st_ino),
                'control copy inode alias')
        require(after.st_uid == os.getuid() and target.read_bytes() == source.read_bytes(),
                'control copy owner and bytes')


def run_clone(root, *args):
    return subprocess.run([sys.executable, '-I', '-O', '-Werror', '-B',
                           '-X', 'pycache_prefix=' + str(root / 'cache'),
                           str(root / 'verify.py'), *args], capture_output=True,
                          text=True, timeout=30, check=False)


def file_controls():
    with tempfile.TemporaryDirectory(prefix='q8-homogeneous-control-') as name:
        root = Path(name)
        copy_payload(root)
        result = json.loads((root / 'RESULT.json').read_text())
        result['claim'] = 'incorrect receipt'
        (root / 'RESULT.json').write_text(json.dumps(result))
        failed = run_clone(root)
        require(failed.returncode != 0 and 'receipt mismatch' in failed.stderr,
                'receipt fault escaped')
        (root / 'RESULT.json').write_bytes((ROOT / 'RESULT.json').read_bytes())
        with (root / 'model.py').open('ab') as stream:
            stream.write(b'\n# altered authenticated source\n')
        failed = run_clone(root)
        require(failed.returncode != 0 and 'receipt mismatch' in failed.stderr,
                'source fault escaped')
        (root / 'model.py').write_bytes((ROOT / 'model.py').read_bytes())
        output = root / 'existing.json'
        output.write_bytes(b'preserve existing bytes')
        failed = run_clone(root, '--write', str(output))
        require(failed.returncode != 0 and output.read_bytes() == b'preserve existing bytes',
                'existing output overwritten')
        (root / 'inputs/pr3570-PROOF.md').write_bytes(b'corrupt actual proof premise')
        failed = run_clone(root)
        require(failed.returncode != 0 and 'retained source changed' in failed.stderr,
                'retained proof fault escaped')


def main():
    arithmetic_faults()
    domain_faults()
    rank_hypothesis_controls()
    file_controls()
    print('PASS_Q8_HOMOGENEOUS_CONTROLS groups=4 optimized=' + str(bool(sys.flags.optimize)))


if __name__ == '__main__':
    main()
