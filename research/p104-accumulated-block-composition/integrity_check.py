"""Light, isolated controls for complete predecessor-byte authentication.

Run with --package PATH, or place beside sources.py and SOURCES.json.
No scientific replay, predecessor import, network, or package mutation occurs.
Mason Hale with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types

sys.dont_write_bytecode = True


def run(package):
    package = Path(package).resolve()
    code = (package/'sources.py').read_bytes()
    module = types.ModuleType('isolated_integrity_sources')
    module.__file__ = str(package/'sources.py')
    exec(compile(code, str(package/'sources.py'), 'exec'), module.__dict__)
    clean = module.authenticate(package)
    original = json.loads((package/'SOURCES.json').read_bytes())
    # Use a small runtime Python source for each corruption, preserving all other bytes.
    row = next(r for r in original['vendored'] if r['local_path'].endswith('/construct.py'))
    relative = row['local_path']
    results = {}
    with tempfile.TemporaryDirectory(prefix='p104-integrity-controls-') as name:
        root = Path(name)
        shutil.copytree(package/'vendor', root/'vendor')
        shutil.copy2(package/'SOURCES.json', root/'SOURCES.json')
        # copy2/copytree retain a sealed input's read-only mode. Mutations are
        # confined to these private temporary fixtures, never the input package.
        for fixture in root.rglob('*'):
            fixture.chmod(0o700 if fixture.is_dir() else 0o600)
        baseline = module.authenticate(root)
        module.need(baseline == clean, 'Positive exported authentication')
        target = root/relative
        raw = target.read_bytes()

        def save_pins(value):
            (root/'SOURCES.json').write_text(json.dumps(value))

        def rejects(label):
            try:
                module.authenticate(root)
            except ValueError as error:
                results[label] = str(error)
            else:
                raise ValueError('Corruption was accepted: '+label)

        target.write_bytes(raw+b'\n# changed source byte\n')
        rejects('changed_source_bytes')
        target.write_bytes(raw)
        target.unlink()
        rejects('missing_source')
        target.write_bytes(raw)
        extra = root/'vendor/unlisted-input.txt'
        extra.write_text('unlisted')
        rejects('extra_source_payload')
        extra.unlink()
        backing = root/'symlink-backing.py'
        backing.write_bytes(raw)
        target.unlink()
        target.symlink_to(backing)
        rejects('source_symlink')
        target.unlink()
        target.write_bytes(raw)
        pins = deepcopy(original)
        pins['vendored'].append(deepcopy(row))
        save_pins(pins)
        rejects('duplicate_runtime_pin')
        pins = deepcopy(original)
        selected = next(r for r in pins['vendored'] if r['local_path'] == relative)
        selected['local_path'] = 'vendor/../escape.py'
        save_pins(pins)
        rejects('source_path_escape')
        pins = deepcopy(original)
        pins['files'] = [r for r in pins['files'] if r.get('local_path') != relative]
        save_pins(pins)
        rejects('missing_repository_origin')
        pins = deepcopy(original)
        for group in ('vendored','files'):
            for r in pins[group]:
                if r.get('local_path') == relative:
                    r['git_blob'] = '0'*40
                    if 'origin' in r:
                        r['origin']['git_blob'] = '0'*40
        save_pins(pins)
        rejects('wrong_git_blob_with_correct_sha256')
        pins = deepcopy(original)
        pins['retained_commit'] = '0'*40
        save_pins(pins)
        rejects('wrong_retained_ancestor')
        pins = deepcopy(original)
        selected = next(r for r in pins['files'] if r.get('local_path') == relative)
        selected['origin']['path'] += '-wrong'
        save_pins(pins)
        rejects('wrong_original_source_mapping')
        pins = deepcopy(original)
        selected = next(r for r in pins['files'] if r.get('local_path') == relative)
        pins['files'].append(deepcopy(selected))
        save_pins(pins)
        rejects('duplicate_retained_repository_pin')
        shutil.copy2(package/'SOURCES.json', root/'SOURCES.json')
        module.need(module.authenticate(root) == clean, 'Restored copied payload')
    module.need(module.authenticate(package) == clean, 'Original payload preserved')
    return {'status':'PASS_SOURCE_AUTHENTICATION_CONTROLS',
            'authenticator_sha256':sha256(code).hexdigest(),
            'positive_authentication':clean, 'controls':results,
            'scope':'Source-byte/inventory checks only; no local/native/caller/pricing replay.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    result = run(args.package)
    encoded = json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.output:
        args.output.write_text(encoded)
    else:
        retained = json.loads((args.package/'INTEGRITY-CONTROLS.json').read_bytes())
        if retained != result:
            raise ValueError('Complete retained integrity receipt differs')
    print(result['status'])


if __name__ == '__main__':
    main()
