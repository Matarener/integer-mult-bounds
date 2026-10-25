"""Standard-library authentication of the retained complete-admission evidence (no heavy rerun).

full_replay.py regenerates all of it.  This checker binds the evidence to the package: the 672-file changed source
closure (PR3945's exact 666-file closure plus our six additive staged-entry files), the adapted admission engine,
the fresh native providers, the literal fill/order/dispatch, the complete admission result, the release receipt and
the final headline.  Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
import gzip, hashlib, json
P = Path(__file__).resolve().parent
PACKAGE = P.parent
E = P / 'evidence'
PR3945_MANIFEST = '3d2ee0175b0cd8aec80c12fef82c2da3a3a54785ca9113140762fd5c41979608'
ENGINE = '76f1b45793abb32a902a8d3cd353b39a018a35a277bb4e223e7508226b71eb6e'


def need(ok, msg):
    if not ok: raise ValueError(msg)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    b = p.read_bytes(); return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)
def encoded(x): return (json.dumps(x, indent=2, sort_keys=True) + '\n').encode()


def main():
    pins = read(E / 'SOURCES.json')
    for rel, digest in pins['files'].items(): need(sha(E / rel) == digest, 'admission evidence hash ' + rel)
    for rel, digest in pins['package_files'].items(): need(sha(PACKAGE / rel) == digest, 'package file hash ' + rel)
    prepared = read(E / 'PREPARED.json'); manifest = read(E / 'SOURCE-NEW.json')
    need(prepared['status'] == 'PASS_STAGED_ENTRY_SOURCE_RECONSTRUCTION' and prepared['pr3945_source_manifest_sha256'] == PR3945_MANIFEST, 'reconstructed PR3945 closure')
    need(prepared['source_manifest_sha256'] == sha(E / 'SOURCE-NEW.json') and prepared['source_files'] == len(manifest) == 672, 'exact 672-file changed source closure')
    added = {'new/borrow/staged_entries_applier.py': PACKAGE / 'recipe/staged_entries_applier.py', 'new/borrow/staged_entries_review.py': PACKAGE / 'recipe/staged_entries_review.py',
             'new/borrow/staged3/RECORD-base.json': PACKAGE / 'recipe/RECORD-base.json', 'new/borrow/staged3/RECORD-extra.json': PACKAGE / 'recipe/RECORD-extra.json',
             'new/borrow/staged3/PRE-base.json.gz': PACKAGE / 'inputs/OLD-base.json.gz', 'new/borrow/staged3/PRE-extra.json.gz': PACKAGE / 'inputs/OLD-extra.json.gz',
             'new/borrow/words/BORROW-WORD-43base.json.gz': PACKAGE / 'inputs/NEW-base.json.gz', 'new/borrow/words/BORROW-WORD-43extra.json.gz': PACKAGE / 'inputs/NEW-extra.json.gz'}
    for rel, local in added.items(): need(manifest[rel] == sha(local), 'source closure binds package file ' + rel)
    registry = {}
    for tag, pid in [('base', 'gauge44'), ('extra', 'extra')]:
        new = read(PACKAGE / 'inputs' / f'NEW-{tag}.json.gz'); origin = read(PACKAGE / 'owner/inputs' / f'old-NATIVE-{tag}.json.gz')['helper_origin']
        registry[pid] = {'widths': [len(new['helper_final'].get(str(r), [1 << i for i in range(9)])) - len(new['start_extra'].get(str(r), [])) for r in origin],
                         'actual_paid_profile': new['report']['local_profile']}
    need(hashlib.sha256(encoded(registry)).hexdigest() == manifest['new/BORROW-PROVIDERS.json'], 'native provider width/profile registry')
    adapter = read(E / 'ADAPTER.json')
    need(adapter['original_engine_sha256'] == ENGINE and len(adapter['literal_patches']) == 4, 'admission engine adaptation scope')
    need(adapter['literal_patches'][0][1].startswith("'staged544': dict(commit='staged-entries-608-609-600-20261019',manifest='" + prepared['source_manifest_sha256'] + "'"), 'engine source profile binding')
    need(adapter['literal_patches'][1] == ['helpers=408,source_file_count=660', 'helpers=408,source_file_count=672'], 'engine file count binding')
    receipt = read(E / 'NATIVE-RECEIPT.json')
    need(receipt['status'] == 'PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE' and receipt['manifest_sha256'] == prepared['source_manifest_sha256'], 'composed native receipt')
    for tag in ('base', 'extra'):
        word = sha(PACKAGE / 'inputs' / f'NEW-{tag}.json.gz'); nr = read(E / f'NATIVE-{tag}-RESULT.json')
        need(receipt['providers'][tag]['word_sha256'] == word == nr['word_sha256'] and nr['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY', 'fresh native provider ' + tag)
        need([z['step'] for z in nr['steps']] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases'] and all(z['exit_code'] == 0 for z in nr['steps']), 'five-stage native coverage ' + tag)
    declared = read(PACKAGE / 'RESULT.json'); kappa = Q(declared['conditional_kappa'])
    result = read(E / 'ADMISSION-RESULT.json')
    need(result['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE', 'complete admission status')
    need(result['source_manifest_sha256'] == prepared['source_manifest_sha256'] and result['source_file_count'] == 672 and result['source_commit'] == 'staged-entries-608-609-600-20261019', 'admission source binding')
    need(result['fill_sha256'] == sha(PACKAGE / 'owner/FILL.json.gz') and result['order_sha256'] == sha(PACKAGE / 'owner/inputs/ORDER.json') and result['dispatch_sha256'] == sha(PACKAGE / 'owner/inputs/DISPATCH.json'), 'admission literal fill/order/dispatch binding')
    need(result['native_receipt_sha256'] == sha(E / 'NATIVE-RECEIPT.json'), 'admission native receipt binding')
    need(result['profile'] == read(PACKAGE / 'owner/PROFILE.json') and Q(result['kappa']) == kappa and Q(result['complex_lower']) == Q(declared['complex_lower']), 'admission profile and headline')
    need(Q(result['comparison_kappa']) < kappa and result['comparison_pr'] == 3682, 'strict improvement over the inherited comparison claim')
    need(result['release_receipt_sha256'] == sha(E / 'RELEASE-RECEIPT.json') and result['package_manifest_sha256'] == sha(E / 'PACKAGE-MANIFEST.json'), 'release receipt and generated package binding')
    release = read(E / 'RELEASE-RECEIPT.json')
    need(release['status'] == 'PASS_RELEASE' and Q(release['kappa_decimal']) == kappa and release['manifest_sha256'] == sha(E / 'PACKAGE-MANIFEST.json'), 'release receipt')
    stages = result['stages']
    need([z['name'] for z in stages] == ['owners', 'parent-lift', 'rebind', 'discovery', 'outer-check_ledger.py', 'outer-independent_check.py', 'release'] and all(z['exit_code'] == 0 for z in stages), 'all complete admission stages')
    final = read(E / 'RESULT.json')
    need(final['status'] == 'PASS_STAGED_ENTRIES_COMPLETE_CONDITIONAL_RELEASE' and Q(final['kappa']) == kappa and final['release_receipt_sha256'] == sha(E / 'RELEASE-RECEIPT.json')
         and final['source_manifest_sha256'] == prepared['source_manifest_sha256'] and final['new_native_fresh'] is True, 'final complete conditional release')
    print(json.dumps({'status': 'PASS_STAGED_ENTRY_COMPLETE_RELEASE_EVIDENCE', 'kappa': str(kappa), 'source_files': 672, 'source_manifest_sha256': prepared['source_manifest_sha256'],
                      'stages': [z['name'] for z in stages], 'scope': 'Authenticates retained evidence of one complete fresh run of admission/full_replay.py; it does not rerun it.'}, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
