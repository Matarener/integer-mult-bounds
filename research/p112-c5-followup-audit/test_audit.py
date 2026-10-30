#!/usr/bin/env python3
"""Behavioral controls for the new Fourier/table audit. Apache-2.0."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify  # noqa: E402


def rejected(function):
    try:
        function()
    except (ValueError, KeyError):
        return
    raise ValueError("losing control accepted")


def main():
    data = verify.authenticate()
    _, live, labels, _ = verify.table_model(data[verify.TABLE])
    # An explicit primal membership oracle checks every dual 7-space against
    # several supports, including a single site, complement and irregular set.
    samples = [labels[:1], labels[1:], labels[::3], labels]
    pairs = [(a,b) for a in range(1,512) for b in range(a+1,512) if a^b > b]
    for selected in samples:
        spectrum = [sum(1 if (a&x).bit_count()%2 == 0 else -1 for x in selected)
                    for a in range(512)]
        for a,b in pairs:
            direct = sum((a&x).bit_count()%2 == 0 and (b&x).bit_count()%2 == 0
                         for x in selected)
            verify.require(verify.character_section(len(selected),spectrum,a,b) == direct,
                           "Fourier versus primal membership")
    rejected(lambda: verify.character_section(1,[0]*512,1,2))
    rejected(lambda: verify.quadruples([(1<<15)-1]*120))
    rejected(lambda: verify.read_json('{"capacity":32,"capacity":33}'))
    changed = data[verify.TABLE].decode().splitlines()
    changed[2] = '0 0 0 0 0 0 0 0'
    rejected(lambda: verify.table_model('\n'.join(changed).encode()))
    verify.require(4*21-3*24 == 12 <= 14, "cut24 is not certified by this argument")
    verify.require(6-4 == 2 and 65+3 == 68 < 65+4 == 69, "caller composition boundary")
    # Actual optimized verifier processes on private copies; no frozen writes.
    with tempfile.TemporaryDirectory(prefix="c5-followup-controls-") as tmp:
        root = Path(tmp)
        target = root / 'research/p112-c5-followup-audit'
        target.mkdir(parents=True)
        for name in ('verify.py','SOURCES.json','RESULT.json'):
            (target/name).write_bytes((HERE/name).read_bytes())
        for name,raw in data.items():
            path = root/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(raw)
        mutations = [(root/verify.TABLE, b'fault'),
                     (target/'SOURCES.json', b'{}'),
                     (target/'RESULT.json', b'{}')]
        for path,mutant in mutations:
            original = path.read_bytes()
            path.write_bytes(mutant)
            run = subprocess.run([sys.executable,'-I','-O','-Werror','-B',str(target/'verify.py')],
                                 capture_output=True,text=True,timeout=90)
            path.write_bytes(original)
            verify.require(run.returncode != 0 and 'ValueError' in run.stderr,
                           "actual optimized CLI accepted corruption")
    print('PASS_C5_AUDIT_CONTROLS primal_oracle=173740 semantic_rejections=4 optimized_CLI_rejections=3')


if __name__ == '__main__':
    main()
