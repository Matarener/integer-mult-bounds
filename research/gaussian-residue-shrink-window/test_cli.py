"""Real fail-closed CLI checks. ToikY + OpenAI Codex; Apache-2.0."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def snapshot():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in ROOT.rglob('*') if p.is_file()}


def run(copy, optimized):
    command = [sys.executable, '-I'] + (['-O'] if optimized else []) + ['-Werror', '-B']
    a = subprocess.run(command + [str(copy / 'verify.py'), '--arithmetic-only'],
                       capture_output=True, text=True, timeout=15)
    b = subprocess.run(command + [str(copy / 'independent.py')],
                       capture_output=True, text=True, timeout=15)
    return a, b


def main():
    before = snapshot()
    controls = []
    for optimized in (False, True):
        for mutation in ('positive', 'source', 'precision', 'capacity', 'partial-top', 'receipt', 'missing-result'):
            with tempfile.TemporaryDirectory(prefix='residue-window-control-') as temporary:
                target = Path(temporary) / 'package'
                shutil.copytree(ROOT, target)
                target.chmod(0o755)
                for path in target.rglob('*'):
                    path.chmod(0o755 if path.is_dir() else 0o644)
                if mutation == 'missing-result':
                    (target / 'RESULT.json').unlink()
                elif mutation == 'source':
                    with (target / 'source/hybrid.py').open('a') as stream:
                        stream.write('\n# deliberately changed source\n')
                elif mutation == 'precision':
                    result = json.loads((target / 'RESULT.json').read_text())
                    result['precision'][28]['p'] = 179
                    (target / 'RESULT.json').write_text(json.dumps(result))
                elif mutation == 'capacity':
                    result = json.loads((target / 'RESULT.json').read_text())
                    result['summary']['max_k_at_capacity'] = 29
                    (target / 'RESULT.json').write_text(json.dumps(result))
                elif mutation == 'partial-top':
                    result = json.loads((target / 'RESULT.json').read_text())
                    result['summary']['conservative_false_negatives'] = 0
                    (target / 'RESULT.json').write_text(json.dumps(result))
                elif mutation == 'receipt':
                    result = json.loads((target / 'INDEPENDENT-RESULT.json').read_text())
                    result['strict_full_box_endpoint']['child_bits'] = 14557
                    (target / 'INDEPENDENT-RESULT.json').write_text(json.dumps(result))
                primary, independent = run(target, optimized)
                if mutation == 'positive':
                    need(primary.returncode == independent.returncode == 0, 'positive real CLI')
                elif mutation == 'receipt':
                    need(primary.returncode == 0 and independent.returncode != 0, 'independent receipt control')
                else:
                    need(primary.returncode != 0 and independent.returncode != 0, 'both engines reject ' + mutation)
                controls.append({'mutation': mutation, 'optimized': optimized,
                                 'primary': primary.returncode, 'independent': independent.returncode})
    need(snapshot() == before, 'controls preserved original package')
    print(json.dumps({'status': 'PASS_RESIDUE_WINDOW_CLI_CONTROLS', 'controls': controls}, sort_keys=True))


if __name__ == '__main__':
    main()
