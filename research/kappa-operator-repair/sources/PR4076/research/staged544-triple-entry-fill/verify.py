"""Fresh local reconstruction and exact semantics of the staged-entry words; authenticate the fresh native receipts.

From PR3945's terminal-width5 words (inputs/OLD-*), the literal records in recipe/ reconstruct the staged-entry words
(inputs/NEW-*) with no search or solver.  Each word must pass PR3734/PR3945 hygiene, the Lagrangian frame bill equal
to its declared report, and arbitrary-dirty forward, dual and cleanup-boundary semantics (audit_core of Sagar Thakrar
PR3687/3693, as used by PR3945's apply_terminal.exact_semantics).  Native receipts are authenticated; the native
phases themselves are a separate fresh-run command (native/run_native.py).
Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
import gzip, hashlib, json, sys
from fractions import Fraction as Q
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'vendor')); sys.path.insert(0, str(HERE / 'recipe'))
import audit_core as C
import staged_entries_applier as S


def need(ok, why):
    if not ok: raise ValueError(why)
def read(p):
    b = p.read_bytes(); return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)


def exact_semantics(w):
    need(C.endpoint_defects(w, C.forward_rows(w, symbolic_buffers=True)) == ([], [], [], True), 'arbitrary-dirty forward')
    need(C.endpoint_defects(w, C.forward_rows(w, dual=True, symbolic_buffers=True), dual=True) == ([], [], [], True), 'arbitrary-dirty dual')
    need(not C.boundary_defects(w, C.transpose(C.reverse_columns(w, upto_cleanup=True))), 'cleanup boundary')


def load(root=HERE):
    pins = read(root / 'INPUTS.json')
    for name, digest in pins['gzip_sha256'].items(): need(hashlib.sha256((root / 'inputs' / name).read_bytes()).hexdigest() == digest, 'input hash: ' + name)
    return [(tag, read(root / 'inputs' / f'OLD-{tag}.json.gz'), read(root / 'recipe' / f'RECORD-{tag}.json'), read(root / 'inputs' / f'NEW-{tag}.json.gz')) for tag in ('base', 'extra')]


def main():
    sys.path.insert(0, str(HERE))
    from checks.exact_root import FULL_PROFILE, LOWER, UPPER, OUTER_LOWER
    need({int(k): v for k, v in read(HERE / 'owner/PROFILE.json').items()} == FULL_PROFILE, 'owner / moment profile bridge')
    declared = read(HERE / 'RESULT.json')
    need({int(k): v for k, v in declared['full_profile'].items()} == FULL_PROFILE, 'result profile')
    need(Q(declared['root_lower']) == LOWER and Q(declared['root_upper']) == UPPER, 'result root interval')
    need(Q(declared['conditional_kappa']) == OUTER_LOWER, 'result conditional endpoint')
    closure = {p.relative_to(HERE / 'native/vendor').as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in (HERE / 'native/vendor').rglob('*') if p.is_file()}
    rows = {}
    for tag, source, record, target in load():
        word = S.apply(source, record)
        need(word == target, 'entire frozen word mismatch')
        C.hygiene(word)
        bill, widths, *_ = C.frame_bill(word, lagrangian=True)
        need({str(k): v for k, v in bill.items()} == word['report']['local_profile'] and {str(k): v for k, v in widths.items()} == word['report']['width_inventory'], 'declared bill/inventory')
        need(word['cleanup'] == C.derive_cleanup(word), 'literal cleanup')
        exact_semantics(word)
        receipt = read(HERE / 'evidence' / f'NATIVE-{tag}.json')
        need(receipt['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY', 'native status')
        need(receipt['word_sha256'] == hashlib.sha256((HERE / 'inputs' / f'NEW-{tag}.json.gz').read_bytes()).hexdigest(), 'native input')
        need(receipt['source_sha256'] == closure, 'native source closure')
        need([s['step'] for s in receipt['steps']] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases'] and all(s['exit_code'] == 0 for s in receipt['steps']), 'native stages')
        rows[tag] = {'local_profile': word['report']['local_profile'], 'width_inventory': word['report']['width_inventory'], 'staged_entrances': [e['helper'] for e in record['entrances']]}
    print(json.dumps({'status': 'PASS_STAGED_ENTRY_WORDS', 'providers': rows,
                      'scope': 'Fresh literal reconstruction from PR3945 words, hygiene, exact Lagrangian frame bill, arbitrary-dirty forward/dual/boundary semantics. Native receipts authenticated; phases are a separate fresh-run command.'}, sort_keys=True))


if __name__ == '__main__':
    main()
