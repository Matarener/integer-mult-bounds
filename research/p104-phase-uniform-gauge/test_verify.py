#!/usr/bin/env python3
"""Destructive API/CLI controls for the explicit phase-uniform gauge package.

Apache-2.0. Separate AI test implementation; no human or kernel review claimed.
Private mutation fixtures copy bytes without inheriting read-only export modes.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def snapshot(folder):
    return {str(p.relative_to(folder)): (p.stat().st_ino, stat.S_IMODE(p.stat().st_mode),
                                       hashlib.sha256(p.read_bytes()).hexdigest())
            for p in folder.rglob('*') if p.is_file()}


def fixture(destination):
    destination.mkdir()
    for name in ('verify.py', 'independent.py', 'CERTIFICATE.json'):
        shutil.copyfile(HERE / name, destination / name)
    shutil.copytree(HERE / 'source', destination / 'source', copy_function=shutil.copyfile)
    # copytree also copies directory modes; mutate only this private fixture.
    for directory in [destination / 'source'] + [p for p in (destination / 'source').rglob('*') if p.is_dir()]:
        directory.chmod(0o755)


def execute(arguments, optimized=False, cwd=None):
    command = [sys.executable, '-I', '-B']
    if optimized:
        command.append('-O')
    result = subprocess.run(command + arguments, cwd=cwd, text=True, capture_output=True, timeout=20)
    return result


API_PREFIX = '''import json,runpy,sys
v=runpy.run_path(sys.argv[1])
cert=json.loads((v['HERE']/'CERTIFICATE.json').read_text())
O=cert['columns']
K=[v['tensor'](O[i],O[j]) for i in range(9) for j in range(9)]
a=cert['translation']
'''

API_CASES = {
    'zero_completion_tag': "v['check_completion'](K,0)",
    'incorrect_completion_tag': "v['check_completion'](K,a^1)",
    'corrupt_completion_columns': "K[0]^=2; v['check_completion'](K,a)",
    'helper_208_missing_translation': "tags=[a]*280; tags[208]=0; v['check_roles'](K,tags,a)",
    'omitted_helpers': "v['check_roles'](K,[a]*208,a)",
    'boolean_helper_tag': "tags=[a]*280; tags[208]=True; v['check_roles'](K,tags,a)",
    'odd_translation': "v['translation_word'](1,81)",
    'wrong_word_endpoint': "w=v['translation_word'](a,81); w[2]=(w[2][0]^6,1); w[3]=w[2]; v['check_word'](w,a,81)",
    'even_line_alphabet': "w=v['translation_word'](a,81); w[0]=(3,1); v['check_word'](w,a,81)",
    'boolean_line_sign': "w=v['translation_word'](a,81); w[0]=(w[0][0],True); v['check_word'](w,a,81)",
    'unpaired_word': "w=v['translation_word'](a,81); w[0]=(w[0][0],-1); v['check_word'](w,a,81)",
}


def api_controls():
    for name, statement in API_CASES.items():
        for optimized in (False, True):
            result = execute(['-c', API_PREFIX + statement, str(HERE / 'verify.py')], optimized)
            need(result.returncode != 0 and 'ValueError' in result.stderr,
                 'API control accepted or crashed unexpectedly: ' + name + '\n' + result.stderr)
    return len(API_CASES)


def certificate_mutations(original):
    def changed(name, key, value):
        cert = copy.deepcopy(original)
        cert[key] = value
        return name, cert
    columns = list(original['columns'])
    columns[0] ^= 2
    bool_columns = list(original['columns'])
    bool_columns[0] = True
    bad_word = copy.deepcopy(original['translation_word'])
    bad_word[2][0] ^= 6
    bad_word[3] = list(bad_word[2])
    even_word = copy.deepcopy(original['translation_word'])
    even_word[0][0] = 3
    bool_sign = copy.deepcopy(original['translation_word'])
    bool_sign[0][1] = True
    return (
        changed('bad_z', 'z', 91),
        changed('zero_z', 'z', 0),
        changed('boolean_z', 'z', True),
        changed('string_z', 'z', '420'),
        changed('corrupt_columns', 'columns', columns),
        changed('boolean_column', 'columns', bool_columns),
        changed('zero_translation', 'translation', 0),
        changed('boolean_translation', 'translation', True),
        changed('wrong_translation_word', 'translation_word', bad_word),
        changed('even_line_word', 'translation_word', even_word),
        changed('boolean_word_sign', 'translation_word', bool_sign),
        changed('undercharged_appended', 'bankwise_appended_calls', original['bankwise_appended_calls'] - 1),
        changed('boolean_appended', 'bankwise_appended_calls', True),
    )


def cli_controls(base):
    cert = json.loads((HERE / 'CERTIFICATE.json').read_text())
    mutations = certificate_mutations(cert)
    cases = [name for name, _ in mutations] + [
        'altered_source_result', 'missing_source_result', 'altered_source_readme',
        'missing_source_proof', 'missing_certificate', 'duplicate_certificate_key',
    ]
    values = dict(mutations)
    independent_negative_runs = 0
    for name in cases:
        folder = base / name
        fixture(folder)
        cert_path = folder / 'CERTIFICATE.json'
        if name in values:
            cert_path.write_text(json.dumps(values[name]))
        elif name == 'altered_source_result':
            path = folder / 'source/RESULT.json'
            path.write_bytes(path.read_bytes() + b'\n')
        elif name == 'missing_source_result':
            (folder / 'source/RESULT.json').unlink()
        elif name == 'altered_source_readme':
            path = folder / 'source/README.md'
            path.write_bytes(path.read_bytes() + b'\n')
        elif name == 'missing_source_proof':
            (folder / 'source/PROOF.md').unlink()
        elif name == 'missing_certificate':
            cert_path.unlink()
        elif name == 'duplicate_certificate_key':
            text = cert_path.read_text()
            cert_path.write_text(text.replace('{', '{"z":420,', 1))
        for optimized in (False, True):
            result = execute([str(folder / 'verify.py')], optimized, folder)
            need(result.returncode != 0 and 'PASS_P104_PHASE_UNIFORM_GAUGE' not in result.stdout,
                 'CLI damaged-input control accepted: ' + name + ' optimized=' + str(optimized))
            need('ValueError' in result.stderr or 'FileNotFoundError' in result.stderr,
                 'CLI damaged-input control crashed unexpectedly: ' + name + '\n' + result.stderr)
            if name in {'altered_source_result', 'missing_source_result',
                        'altered_source_readme', 'missing_source_proof'}:
                independent = execute([str(folder / 'independent.py')], optimized, folder)
                need(independent.returncode != 0 and
                     ('ValueError' in independent.stderr or 'FileNotFoundError' in independent.stderr),
                     'independent CLI accepted damaged source: ' + name)
                independent_negative_runs += 1
    return len(cases), independent_negative_runs


def readonly_positive(base):
    folder = base / 'readonly'
    fixture(folder)
    files = [p for p in folder.rglob('*') if p.is_file()]
    directories = [folder] + [p for p in folder.rglob('*') if p.is_dir()]
    for p in files:
        need(p.stat().st_ino != (HERE / p.relative_to(folder)).stat().st_ino,
             'read-only fixture shares an inode with source')
        p.chmod(0o444)
    for p in directories:
        p.chmod(0o555)
    before = snapshot(folder)
    try:
        for optimized in (False, True):
            result = execute([str(folder / 'verify.py')], optimized, folder)
            need(result.returncode == 0 and result.stdout.startswith('PASS_P104_PHASE_UNIFORM_GAUGE '),
                 'read-only Git-free positive CLI failed: ' + result.stderr)
        need(snapshot(folder) == before, 'read-only positive export changed')
    finally:
        for p in sorted(directories, key=lambda q: len(q.parts)):
            p.chmod(0o755)
    return len(files)


def main():
    started = time.monotonic()
    original = snapshot(HERE)
    api = api_controls()
    with tempfile.TemporaryDirectory(prefix='p104-uniform-gauge-controls-') as temporary:
        base = Path(temporary)
        cli, independent_negative_runs = cli_controls(base)
        readonly_files = readonly_positive(base)
    need(snapshot(HERE) == original, 'source package was modified by controls')
    print('PASS_P104_PHASE_UNIFORM_GAUGE_CONTROLS api_cases=' + str(api)
          + ' cli_cases=' + str(cli) + ' negative_runs=' + str(2 * (api + cli))
          + ' independent_source_negative_runs=' + str(independent_negative_runs)
          + ' normal_and_optimized=PASS readonly_git_free_files=' + str(readonly_files)
          + ' source_unchanged=PASS elapsed_seconds=' + format(time.monotonic() - started, '.3f'))


if __name__ == '__main__':
    main()
