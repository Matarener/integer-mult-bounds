"""Read-only replay of the scoped signed-query physical refinement.

Mason Hale with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha1, sha256
import importlib
import json
from pathlib import Path, PurePosixPath
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.dont_write_bytecode = True


def need(ok, why):
    if not ok:
        raise ValueError(why)


def check_bytes(raw, row):
    need(sha256(raw).hexdigest() == row['sha256'], 'Authenticated SHA256: '+row['path'])
    need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], 'Authenticated Git blob: '+row['path'])


def authenticate():
    manifest=json.loads((HERE/'SOURCES.json').read_bytes())
    need(manifest['base_commit']=='de5ec2e7a6074068452f45b1a191b5c72832df4a', 'Exact base')
    rows=[r for r in manifest['files'] if r['usage']=='input']
    for row in rows:
        parts=PurePosixPath(row['path']).parts
        need(parts and '..' not in parts and not row['path'].startswith('/'), 'Relative input path')
        path=ROOT
        for part in parts:
            path=path/part
            need(not path.is_symlink(), 'No input symlinks')
        check_bytes(path.read_bytes(),row)
    for row in manifest['vendored']:
        check_bytes((HERE/row['local_path']).read_bytes(),row)
    first=rows[0]
    try:
        check_bytes((ROOT/first['path']).read_bytes()+b'changed',first)
    except ValueError:
        pass
    else:
        raise ValueError('Changed source accepted')
    return len(rows)+len(manifest['vendored'])


def receipt(name, actual):
    # JSON normalization accounts for the deliberate integer Counter keys.
    need(json.loads((HERE/name).read_bytes()) == json.loads(json.dumps(actual)), 'Exact regenerated receipt: '+name)


def run():
    count=authenticate()
    sys.path.insert(0,str(HERE))
    p=importlib.import_module('prototype')
    receipt('RESULT.json',p.run_checks())
    controls=importlib.import_module('controls').run_checks()
    receipt('CONTROLS.json',controls)
    invoices=importlib.import_module('check_invoice').run_checks()
    receipt('BOUNDARY-INVOICE.json',invoices)
    owners=importlib.import_module('owners')
    word,caller=owners.inputs()
    typed=owners.bind(word,caller)
    typed['negative_controls']=owners.controls(word,caller)
    receipt('OWNERSHIP.json',typed)
    bit=importlib.import_module('bit_owners').run(ROOT)
    receipt('BIT-OWNERSHIP.json',bit)
    names=importlib.import_module('fresh_names_controls')
    names.legal_nested_private_argument()
    name_tests=(names.duplicate_child_arguments,names.child_bank_captures_parent,
                names.child_clears_borrowed_parent,names.one_bank_per_depth,
                names.reused_missing_source,names.early_parent_erase)
    for test in name_tests:
        try:
            test()
        except ValueError:
            pass
        else:
            raise ValueError('Name/lifetime mutation accepted: '+test.__name__)
    receipt('WARM-TAIL-BOUNDARY.json',importlib.import_module('warm_tail_boundary').run(HERE))
    print('PASS_SELECTED_QUERY_DISPATCH: 23 fixed tapes; 114 chains; 9 unequal subjobs; 27 exact invoices; 8 coded-tail cases; 6 physical, 7 complex, 1 BIT and 6 name controls; '+str(count)+' authenticated inputs.')
    print('SCOPE: all-size query-boundary proof and literal raw owner bindings; all five project assumptions remain retained.')


if __name__=='__main__':
    # Prevent stale bytecode from substituting for authenticated working source
    # even when this standalone verifier is run outside the registered launcher.
    with tempfile.TemporaryDirectory(prefix='selected-dispatch-bytecode-') as cache:
        sys.pycache_prefix=cache
        run()
