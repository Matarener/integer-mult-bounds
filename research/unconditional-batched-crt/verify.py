"""Authenticate sources and finite receipts, not the written all-size proof."""
import hashlib
import json
from pathlib import Path
import subprocess

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
MIXED = ROOT / 'research/staged544-mixed-fourth-entry'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def main():
    sources = json.loads((P/'SOURCES.json').read_text())
    live = 0
    for row in sources['files']:
        if row['usage'] == 'input':
            data = (ROOT/row['path']).read_bytes()
            live += 1
        else:
            data = subprocess.check_output(['git','-C',str(ROOT),'show',
                                            sources['base_commit']+':'+row['path']])
        need(sha(data) == row['sha256'] and blob(data) == row['git_blob'],
             'source bytes: '+row['path'])
    exports = json.loads((P/'EXPORTED-SOURCES.json').read_text())
    for path, row in exports.items():
        data = (P/path).read_bytes()
        need(sha(data) == row['sha256'] and blob(data) == row['git_blob'], 'export bytes: '+path)
    native = {path.relative_to(MIXED/'native/vendor').as_posix():sha(path.read_bytes())
              for path in (MIXED/'native/vendor').rglob('*')
              if path.is_file() and '__pycache__' not in path.parts}
    receipts = []
    for tag in ['base','extra']:
        row = json.loads((P/f'evidence/THREE-NATIVE-{tag}.json').read_text())
        need(row['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY', 'fresh native status')
        need(row['word_sha256'] == sha((MIXED/f'inputs/THREE-{tag}.json.gz').read_bytes()), 'fresh native word')
        need(row['source_sha256'] == native, 'fresh native source inventory')
        need([step['step'] for step in row['steps']] ==
             ['native','ledgers','local-replay','wrappers','phases'], 'five native stages')
        need(all(step['exit_code'] == 0 for step in row['steps']), 'native success')
        receipts.append('THREE-'+tag)
    print(json.dumps({'status':'PASS_UNCONDITIONAL_ROUTE_SOURCE_BINDINGS',
                      'live_inputs':live,'exports':len(exports),'fresh_native_receipts':receipts,
                      'all_size_theorem_verified_by_this_script':False},sort_keys=True))


if __name__ == '__main__':
    main()
