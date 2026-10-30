"""Authenticate the later default-wrapper run; does not rerun its heavy stages."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import tarfile

from evidence_check import need, semantic

P = Path(__file__).resolve().parent
D = P / 'evidence/full-wrapper'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def check_records(files):
    def read(name):
        return json.loads(files[name])

    wrapper = read('RESULT.json')
    admission = read('admission/RESULT.json')
    release = read('admission/release/RELEASE-RECEIPT.json')
    native = read('NATIVE-RECEIPT.json')
    strict = 'admission/release/verify/strict/'
    kappa = semantic(admission, release, native,
                     read(strict + 'global/audit/PREFIX-AND-INVOICE.json'),
                     read(strict + 'INDEPENDENT.json'))
    need(wrapper['status'] == 'PASS_DELAYED_RELEASE_COMPLETE_CONDITIONAL_RELEASE', 'wrapper terminal status')
    need(Fraction(wrapper['kappa']) == Fraction(wrapper['kappa_decimal']) == kappa, 'wrapper exact endpoint')
    need(wrapper['reuse_current_native'] is False and wrapper['retained_parent_reused'] is True, 'wrapper reuse scope')
    need(wrapper['source_archive_sha256'] == digest((P / 'REPLAY-INPUTS.tar.gz').read_bytes()), 'wrapper source archive')
    need(wrapper['release_receipt_sha256'] == admission['release_receipt_sha256'] == digest(files['admission/release/RELEASE-RECEIPT.json']), 'wrapper release linkage')
    need(admission['native_receipt_sha256'] == digest(files['NATIVE-RECEIPT.json']), 'wrapper native linkage')
    need(admission['package_manifest_sha256'] == release['manifest_sha256'] == digest(files['admission/package/MANIFEST.json']), 'wrapper package linkage')

    expected = {
        '': ['fresh-native-base', 'fresh-native-extra', 'complete-admission'],
        'admission/': ['owners', 'parent-lift', 'rebind', 'discovery', 'outer-check_ledger.py', 'outer-independent_check.py', 'release'],
        strict: ['bind', 'emit', 'audit', 'invoice', 'assembly', 'admission', 'bit', 'independent'],
    }
    for root in ['', 'admission/', 'admission/discovery/', 'admission/release/verify/', strict]:
        stages = read(root + 'STAGES.json')
        if root in expected:
            need([s['name'] for s in stages] == expected[root], 'wrapper stage coverage ' + root)
        for stage in stages:
            need(stage['exit_code'] == 0, 'wrapper failed stage ' + stage['name'])
            if 'log_sha256' in stage:
                need(digest(files[root + stage['name'] + '.log']) == stage['log_sha256'], 'wrapper stage log ' + stage['name'])
    verify_stages = {s['name'] for s in read('admission/release/verify/STAGES.json')}
    need({'staged3605-review', 'delayed-release-independent-review'} <= verify_stages, 'wrapper declared edit coverage')
    for tag in ['base', 'extra']:
        result = read('native-' + tag + '/RESULT.json')
        need(result['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY', 'wrapper fresh native status')
        original = json.loads((P / 'evidence' / ('native-' + tag) / 'RESULT.json').read_text())
        need(result['source_sha256'] == original['source_sha256'], 'wrapper native scientific engines')
        need(result['word_sha256'] == digest((P / 'lead1-words' / ('DELAYED-' + tag + '.json.gz')).read_bytes()), 'wrapper fresh native word')
        need([s['step'] for s in result['steps']] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases'] and all(s['exit_code'] == 0 for s in result['steps']), 'wrapper native five stages')
    return 'PASS_AUTHENTICATED_DEFAULT_WRAPPER_RECEIPTS_NOT_FRESH_REPLAY'


def check():
    pins = json.loads((D / 'PINS.json').read_text())
    need(pins['full_replay_sha256'] == digest((P / 'full_replay.py').read_bytes()), 'recorded wrapper source')
    need(pins['source_archive_sha256'] == digest((P / 'REPLAY-INPUTS.tar.gz').read_bytes()), 'recorded wrapper inputs')
    archive = D / 'RECEIPTS.tar.gz'
    need(pins['receipts_archive_sha256'] == digest(archive.read_bytes()), 'wrapper receipt archive')
    files = {}
    with tarfile.open(archive) as tf:
        for member in tf:
            need(member.isfile() and member.name in pins['files'] and member.name not in files, 'wrapper receipt member')
            raw = tf.extractfile(member).read()
            need(digest(raw) == pins['files'][member.name], 'wrapper receipt bytes')
            files[member.name] = raw
    need(set(files) == set(pins['files']), 'wrapper receipt inventory')
    for name in ['RESULT.json', 'STAGES.json', 'ENVIRONMENT.json']:
        need((D / name).read_bytes() == files[name], 'readable wrapper receipt ' + name)
    result = check_records(files)
    # Reject receipts that contradict this run's fresh-provider/complete-wrapper claim.
    controls = [
        ('RESULT.json', lambda x: x.update(reuse_current_native=True)),
        ('RESULT.json', lambda x: x.update(kappa='0')),
        ('STAGES.json', lambda x: x.pop(1)),
        ('native-base/RESULT.json', lambda x: x.update(source_sha256={})),
    ]
    for name, mutate in controls:
        changed = dict(files)
        value = json.loads(changed[name])
        mutate(value)
        changed[name] = json.dumps(value).encode()
        try:
            check_records(changed)
        except ValueError:
            pass
        else:
            raise ValueError('wrapper semantic control accepted: ' + name)
    return result + ' (4 semantic rejection controls)'


if __name__ == '__main__':
    print(check())
