"""Reject corrupt source boundaries before scientific imports or execution."""
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

from source import baseline, payload, require, HERE


def reject(action, expected):
    try:
        action()
    except ValueError as error:
        require(str(error) == expected, 'Exact custody rejection predicate')
    else:
        raise ValueError('Corrupt source accepted')


def main():
    require(not sys.argv[1:], 'No custody arguments')
    science = {'frozen_contract', 'frozen_precision', 'explicit_contract', 'integer_backend'}
    before = set(sys.modules) & science
    results = {}
    with tempfile.TemporaryDirectory(prefix='precision-custody-') as temporary:
        temporary = Path(temporary)
        raw = bytearray((HERE / 'inputs/PR5831.tar').read_bytes())
        raw[len(raw) // 2] ^= 1
        damaged = temporary / 'damaged.tar'
        damaged.write_bytes(raw)
        reject(lambda: payload(damaged), 'Exact PR5831 bundle')
        results['official_export_byte'] = 'Exact PR5831 bundle'
        with baseline() as package:
            for label in ('inner_archive', 'contract', 'declared_edit'):
                root = temporary / label
                copy = root / 'research/p104-integer-error-replay'
                shutil.copytree(package, copy)
                for path in [root, *root.rglob('*')]:
                    path.chmod(0o755 if path.is_dir() else 0o644)
                if label == 'inner_archive':
                    file = copy / 'inputs/source.tar'
                    raw = bytearray(file.read_bytes()); raw[len(raw) // 2] ^= 1
                    file.write_bytes(raw)
                    expected = 'source hash'
                elif label == 'contract':
                    file = copy / 'contract.py'
                    file.write_bytes(file.read_bytes() + b'\n# changed contract\n')
                    expected = 'declared contract edits'
                else:
                    file = copy / 'CONTRACT-EDITS.json'
                    edits = json.loads(file.read_bytes()); edits[0][0] = 'missing_backend_seam'
                    file.write_text(json.dumps(edits))
                    expected = 'unique backend seam'
                spec = importlib.util.spec_from_file_location('custody_entry_' + label, copy / 'verify.py')
                module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
                def enter():
                    with module.source():
                        raise ValueError('Unexpected scientific admission')
                reject(enter, expected)
                require(set(sys.modules) & science == before, 'No scientific imports before rejection')
                results[label] = expected
    print('PASS_PRECISION_LINUX_SOURCE_CONTROLS', json.dumps(results, sort_keys=True))


if __name__ == '__main__':
    main()
