"""Real optimized CLI rejection controls in a relocated Git-free input closure."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PACKAGE = Path('research/physical-boundary-rhs-caller')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    with tempfile.TemporaryDirectory(prefix='rhs-integrity-') as directory:
        root = Path(directory)
        package = root / PACKAGE
        package.mkdir(parents=True)
        for path in HERE.iterdir():
            if path.is_file():
                shutil.copyfile(path, package / path.name)
        manifest = json.loads((HERE / 'VERIFY.json').read_text())
        for name in manifest['inputs']:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        command = [sys.executable, '-I', '-O', '-B', str(package / 'verify.py')]
        def rejects(fragment):
            result = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=30)
            need(result.returncode != 0 and fragment in result.stderr, 'actual optimized rejection: '+fragment)
        source = root / 'research/physical-gaussian-core/gaussian_core.py'
        original = source.read_bytes()
        source.write_bytes(original + b'\n# changed bound source\n')
        rejects('source bytes: research/physical-gaussian-core/gaussian_core.py')
        source.unlink()
        rejects('FileNotFoundError')
        source.write_bytes(original)
        receipt = package / 'RESULT.json'
        original_receipt = receipt.read_bytes()
        data = json.loads(original_receipt)
        data['cases'][0]['width'] = True
        receipt.write_text(json.dumps(data))
        rejects('typed receipt')
        receipt.unlink()
        rejects('FileNotFoundError')
        receipt.write_bytes(original_receipt)
        need(not (root / '.git').exists(), 'actual Git-free control relocation')
    print('PASS_RHS_CLI_INTEGRITY_CONTROLS changed-source missing-source typed-receipt missing-receipt')


if __name__ == '__main__':
    main()
