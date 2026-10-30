"""Git-free fail-closed source and typed-receipt controls, standard library only."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def main():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        package = root / 'research' / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        for relative in json.loads((HERE / 'VERIFY.json').read_text())['inputs']:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        command = [sys.executable, '-I', '-B']
        if not __debug__: command.append('-O')
        command.append(str(package / 'verify.py'))
        def run(expected, marker):
            result = subprocess.run(command, env={'PATH':''}, capture_output=True, text=True, timeout=20)
            if (result.returncode == 0) != expected or marker not in result.stdout + result.stderr:
                raise ValueError('portable control: ' + marker + '\n' + result.stdout + result.stderr)
        run(True, 'PASS_DIRECT_RESIDUAL_RUN_EMISSION')
        receipt = package / 'RESULT.json'
        original = receipt.read_bytes()
        receipt.unlink()
        run(False, 'FileNotFoundError')
        changed = json.loads(original)
        changed['source_words'][0]['mode'] = False
        receipt.write_text(json.dumps(changed))
        run(False, 'typed frozen receipt')
        receipt.write_bytes(original)
        source = root / 'research/selected-bit-physical-caller/macro_code.py'
        source.write_bytes(source.read_bytes() + b'\n# byte corruption control\n')
        run(False, 'source hash:')
    print('PASS_PORTABLE_DIRECT_RUN_CONTROLS: cold replay, missing receipt, bool/int receipt, source bytes')


if __name__ == '__main__': main()
