#!/usr/bin/env python3
"""Mutate private copies, then reject via literal counts and expected periods.
SHIN09-git with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PROBE = """
import json,sys
from pathlib import Path
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p))
import verify
from oracle import literal_census
verify.check_sources()
rows=verify.source_rows()
table,_=verify.all_period_rows(rows)
expected=json.loads((p/'EXPECTED.json').read_text())
for m in range(1,5):
    actual=literal_census(m)
    for c in range(m):
        row=table[str(m)][c]
        if row['cyclic_orbits'] != actual['orbits'][c]:
            raise ValueError('literal orbit mismatch')
        for d in actual['fixed']:
            if row['fixed'][str(d)] != actual['fixed'][d][c]:
                raise ValueError('literal fixed-point mismatch')
if table != expected['period_counts']:
    raise ValueError('period table differs from retained computation')
print('PASS_MUTATION_PROBE')
"""
MUTATIONS = [
    ("pair_gate", "periods.py", "if d % 2 == 0 and n % 2 == 1:", "if False:"),
    ("cubic_shift", "periods.py", "delta = c - comb(d, 3) * n**3", "delta = c"),
    ("shift_sign", "periods.py", "delta = c - comb(d, 3) * n**3", "delta = c + comb(d, 3) * n**3"),
    ("divisibility", "periods.py", "if delta % d:", "if False:"),
    ("totient_weight", "periods.py", "phi(d) * fixed[d]", "fixed[d]"),
    ("mobius_sign", "periods.py", "result = -result", "result = result"),
    ("unit_all_primitive", "periods.py", "return rows[n][((c - n**3) // 3) % n]", "return 0"),
    ("existence_six", "periods.py", "((6, 5), (12, 1))", "((0, 0), (12, 1))"),
    ("existence_twelve", "periods.py", "((6, 5), (12, 1))", "((6, 5), (0, 0))"),
    ("source_tamper", "source/6037-RESULT.json", '"6741578652"', '"6741578653"'),
    ("expected_tamper", "EXPECTED.json", '"cyclic_orbits": 7,', '"cyclic_orbits": 8,'),
]


def private_copy(source, destination):
    # A read-only export must stay read-only; only its temporary copies change.
    shutil.copytree(source, destination, copy_function=shutil.copyfile,
                    ignore=shutil.ignore_patterns("__pycache__"))
    directories = [destination] + [p for p in destination.rglob("*") if p.is_dir()]
    for directory in directories:
        directory.chmod(directory.stat().st_mode | stat.S_IRWXU)


def run_probe(folder, optimized):
    argv = [sys.executable, "-I", "-W", "error", "-B"]
    if optimized:
        argv.append("-O")
    result = subprocess.run(argv + [str(folder / "probe.py")], cwd=folder,
                            capture_output=True, text=True, timeout=120)
    return result


def main():
    source_hashes = {path.relative_to(HERE).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in HERE.rglob("*") if path.is_file() and "__pycache__" not in path.parts}
    evidence = []
    with tempfile.TemporaryDirectory(prefix="chain-cyclic-controls-") as tmp:
        baseline = Path(tmp) / "baseline"
        private_copy(HERE, baseline)
        (baseline / "probe.py").write_text(PROBE, encoding="utf-8", newline="\n")
        for optimized in (False, True):
            control = run_probe(baseline, optimized)
            if control.returncode or control.stdout.strip() != "PASS_MUTATION_PROBE":
                raise ValueError("positive mutation probe failed: " + control.stderr)
        for name, relative, old, new in MUTATIONS:
            changed = Path(tmp) / name
            private_copy(baseline, changed)
            path = changed / relative
            original = path.read_text(encoding="utf-8")
            if original.count(old) != 1:
                raise ValueError("mutation anchor must be unique: " + name)
            path.write_text(original.replace(old, new), encoding="utf-8", newline="\n")
            for optimized in (False, True):
                result = run_probe(changed, optimized)
                if result.returncode == 0 or "ValueError:" not in result.stderr:
                    raise ValueError("mutation was not semantically rejected: " + name)
                reason = result.stderr.strip().splitlines()[-1]
                evidence.append(dict(mutation=name, optimized=optimized, reason=reason))
    print(json.dumps(dict(status="PASS_CHAIN_CYCLIC_MUTATIONS",
                          positive_probes=2, rejections=evidence,
                          input_sha256=source_hashes), sort_keys=True))


if __name__ == "__main__":
    main()
