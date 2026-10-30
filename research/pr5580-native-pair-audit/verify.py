#!/usr/bin/env python3
"""Portable replay of one byte-preserved PR5580 native-pair qualification.

Chris R/Clear1nsight with OpenAI Codex assistance. Apache-2.0.
Native/compiler/Clifford arithmetic retains all credited predecessor notices.
"""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
AUDIT = 'outputs/continuous-kappa-process-20261026/admission-map/pr5580-native-nomination'
REQUEST_SHA = 'ad28fe76aaa7a56d717a205a2b519f75dfaa366e57141a2b3f5a17fa10d18e83'
RESULT_SHA = '896021cbb14577bc242d8c884210b56e9ded0133acf02ab22295c3324e657ad9'
MATRIX_SHA = '4880642a0492ed39e066828674c80eaf3f62cccbd68a3b45b17bccbe03f1245e'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def regular(root, name):
    relative = Path(name)
    need(not relative.is_absolute() and relative.as_posix() == name and '..' not in relative.parts,
         'canonical relative path '+name)
    current = root
    for part in relative.parts:
        current = current/part
        need(not current.is_symlink(), 'symlink path '+name)
    need(current.is_file(), 'regular file '+name)
    return current


def semantic(result):
    need(result['status'] == 'PASS_PR5580_SINGLE_NATIVE_PAIR' and result['new_kappa'] is None,
         'original one-pair scientific scope')
    need(result['reviewed_head'] == '6efa248cf456d6101d757e9d09ba29711d18a13a' and
         result['target_pair'] == [3,737] and result['rank'] == 4 and
         result['paid_occurrences'] == [[12658,451,False]], 'exact source/operator/occurrence')
    native = result['native_result']
    need(native['columns'] == 512 and native['complex_entries'] == 262144 and
         native['matrix_sha256'] == MATRIX_SHA and native['independent_B_block_rank'] == 4 and
         native['each_column_support'] == 16 and native['each_column_squared_norm'] == 1 and
         len(native['signed_Pauli_images']) == 18, 'complete original native coverage')
    controls = result['controls']
    columns = ['global_phase','wrong_child_sign','wrong_boundary_correction','reverse_orientation']
    messages = ['wrong_rank','omitted_paid_occurrence','compiler_source_corruption','literal_source_corruption']
    need(set(controls) == set(columns+messages), 'all eight original controls')
    need(all(type(controls[k]['first_rejected_column']) is int and
             0 <= controls[k]['first_rejected_column'] < 512 for k in columns) and
         controls['global_phase']['signed_tableau_unchanged'] is True,
         'all physical fault controls rejected')
    need(all(isinstance(controls[k],str) and controls[k] for k in messages),
         'rank/occurrence/source controls rejected')
    need(result['all_input_local_743row_ABI_checked'] is False and result['full_caller_checked'] is False and
         result['full_native_universe_checked'] is False and result['complete_raw_dual_checked'] is False and
         result['compiler_outer_admitted'] is False and result['precision_tape_storage_admitted'] is False,
         'retained scope boundaries')


def authenticate():
    inventory = json.loads(regular(HERE,'PAYLOAD-INVENTORY.json').read_bytes())['files']
    actual = set()
    for path in HERE.rglob('*'):
        need(not path.is_symlink(), 'symlink package member')
        if path.is_file() and path != HERE/'PAYLOAD-INVENTORY.json':
            actual.add(path.relative_to(HERE).as_posix())
    need(actual == set(inventory), 'complete package inventory')
    for name,row in inventory.items():
        raw = regular(HERE,name).read_bytes()
        need(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'frozen package byte '+name)
    capsule = HERE/'capsule'
    raw = regular(capsule,AUDIT+'/REQUEST.json').read_bytes()
    need(sha(raw) == REQUEST_SHA, 'original request bytes')
    request = json.loads(raw)
    need(request['total_seconds'] == 150 and request['per_child_seconds'] == 60 and
         request['memory_mib'] == 512 and request['target_pair'] == [3,737], 'original resource/object domain')
    for name,digest in request['files'].items():
        need(sha(regular(capsule,name).read_bytes()) == digest, 'original frozen input '+name)
    expected = regular(HERE,'original-evidence/RESULT-normal.json').read_bytes()
    need(sha(expected) == RESULT_SHA and
         regular(HERE,'original-evidence/RESULT-optimized.json').read_bytes() == expected,
         'complete original scientific result bytes')
    pair = json.loads(regular(HERE,'original-evidence/PAIR-RECEIPT.json').read_bytes())
    need(pair['result_sha256'] == RESULT_SHA and pair['request_sha256'] == REQUEST_SHA and
         pair['complete_output_equal'] is True and pair['scientific_fields_excluded'] == 0,
         'original exact paired receipt')
    semantic(json.loads(expected))
    return expected


def child_limits():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))


def main():
    expected = authenticate()
    if sys.argv[1:] == ['--integrity-only']:
        print('PASS_PR5580_NATIVE_PAIR_INTEGRITY_ONLY_NO_SCIENCE')
        return
    need(not sys.argv[1:], 'unsupported verifier arguments')
    env = dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONOPTIMIZE',None)
    with tempfile.TemporaryDirectory(prefix='pr5580-native-pair-') as folder:
        command = [sys.executable,'-I','-X','pycache_prefix='+folder+'/bytecode']
        command += ['-O'] if sys.flags.optimize else []
        command += ['-B',str(HERE/'capsule'/AUDIT/'check.py')]
        with (Path(folder)/'stdout.json').open('wb+') as out,(Path(folder)/'stderr.txt').open('wb+') as err:
            run = subprocess.run(command,cwd=HERE/'capsule',env=env,stdout=out,stderr=err,
                                 timeout=60,preexec_fn=child_limits)
            out.seek(0); actual = out.read()
            err.seek(0); errors = err.read()
        need(run.returncode == 0 and not errors, 'scientific subprocess failed: '+errors.decode(errors='replace')[:4000])
        need(actual == expected, 'complete original scientific output equality')
    semantic(json.loads(actual))
    authenticate()
    print('PASS_PR5580_NATIVE_PAIR_AUDIT')
    print(json.dumps({'complete_original_output_sha256':sha(actual),'matrix_sha256':MATRIX_SHA,
                      'pair':[3,737],'rank':4,'columns':512,'controls_rejected':8,
                      'full_supplier_admission':False,'new_kappa':None},sort_keys=True,separators=(',',':')))


if __name__ == '__main__':
    main()
