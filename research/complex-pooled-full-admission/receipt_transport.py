"""Lossless receipt storage and canonical addresses; no arithmetic changes.

Prepared for Ross Richardson with OpenAI Codex assistance. Apache-2.0.
Historical EVIDENCE.json commitments always refer to decompressed original bytes.
"""
import copy
import gzip
from hashlib import sha256
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RECEIPTS = {'evidence/PREFIX-AND-INVOICE.json', 'evidence/SPEC.json',
            'evidence/MIXED-CONTRACT.json'}
SELECTED = {
    'frozen/selected/ASSEMBLY.json': 'research/community-frontier1094-audit/ASSEMBLY.json',
    'frozen/selected/BIT-EXPECTED.json': 'research/e8-bit-p111-tuned/tune/EXPECTED.json',
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def regular(path):
    need(path.is_file() and not path.is_symlink(), 'ordinary transport file: ' + str(path))
    return path.read_bytes()


def unpack(path, record):
    packed = regular(path)
    need(len(packed) == record['bytes'] and sha256(packed).hexdigest() == record['sha256'],
         'compressed container commitment')
    raw = gzip.decompress(packed)
    need(len(raw) == record['payload_bytes'] and
         sha256(raw).hexdigest() == record['payload_sha256'], 'original payload commitment')
    return raw


def validate_manifest(value):
    need(value['schema_version'] == 1 and set(value['receipts']) == RECEIPTS,
         'complete compressed receipt inventory')
    need(set(value['selected_inputs']) == set(SELECTED), 'complete selected input inventory')
    for logical, row in value['receipts'].items():
        need(row['path'] == logical + '.gz', 'fixed compressed receipt address')
    for logical, row in value['selected_inputs'].items():
        need(row['path'] == SELECTED[logical], 'fixed canonical input address')
    need(value['historical_input_pins']['path'] == 'frozen/RECORDED-INPUT-PINS.json.gz',
         'fixed recorded source address')
    return value


def manifest():
    return validate_manifest(json.loads(regular(HERE / 'PACKAGING.json')))


def relative(path):
    # Match lexical package addresses without following an unexpected symlink.
    path = Path(path).absolute()
    return path.relative_to(HERE).as_posix() if path.is_relative_to(HERE) else None


def payload(path):
    key = relative(path)
    if key in RECEIPTS:
        need(not Path(path).exists() and not Path(path).is_symlink(),
             'only one compressed receipt representation')
        row = manifest()['receipts'][key]
        return unpack(HERE / row['path'], row)
    return regular(Path(path))


def read(path):
    raw = payload(path)
    return json.loads(gzip.decompress(raw) if Path(path).suffix == '.gz' else raw)


def sha(path):
    return sha256(payload(path)).hexdigest()


def selected_bytes(path, row):
    raw = regular(path)
    need(len(raw) == row['bytes'] and sha256(raw).hexdigest() == row['sha256'],
         'identical pinned canonical input')
    return raw


def selected_path(path):
    key = relative(path)
    if key not in SELECTED:
        return Path(path)
    need(not Path(path).exists() and not Path(path).is_symlink(),
         'only one selected input representation')
    row = manifest()['selected_inputs'][key]
    target = REPO / row['path']
    selected_bytes(target, row)
    return target


def historical_source_sha(name):
    if name != 'INPUT-PINS.json':
        return sha(HERE / name)
    row = manifest()['historical_input_pins']
    return sha256(unpack(HERE / row['path'], row)).hexdigest()


def check():
    """Keep the complete historical commitments and equivalent live input set."""
    value = manifest()
    evidence = read(HERE / 'EVIDENCE.json')
    for name, row in value['receipts'].items():
        need(row['payload_sha256'] == evidence['receipt_sha256'][name],
             'historical receipt commitment')
        read(HERE / name)
    row = value['historical_input_pins']
    old_raw = unpack(HERE / row['path'], row)
    need(sha256(old_raw).hexdigest() == evidence['execution_source_sha256']['INPUT-PINS.json'],
         'historical execution source commitment')
    old = json.loads(old_raw)
    expected = copy.deepcopy(old)
    seen = set()
    for entry in expected['files']:
        if entry['kind'] == 'package' and entry['path'] in SELECTED:
            logical = entry['path']
            target = selected_path(HERE / logical)
            need(sha(target) == entry['sha256'], 'same selected input payload')
            entry.update(kind='repository', path=SELECTED[logical])
            seen.add(logical)
    need(seen == set(SELECTED) and read(HERE / 'INPUT-PINS.json') == expected,
         'only two equivalent input addresses changed')
    return {'receipt_payloads': len(RECEIPTS), 'reused_canonical_inputs': len(seen),
            'historical_execution_sources': len(evidence['execution_source_sha256'])}


def controls():
    """Reject lost coverage, damaged containers/payloads, and missing inputs."""
    count = 0

    def rejects(action):
        nonlocal count
        try:
            action()
        except (ValueError, OSError, EOFError):
            count += 1
            return
        raise ValueError('accepted invalid transport fixture')

    value = manifest()
    for field in ('receipts', 'selected_inputs'):
        mutant = copy.deepcopy(value)
        mutant[field].pop(next(iter(mutant[field])))
        rejects(lambda: validate_manifest(mutant))
    mutant = copy.deepcopy(value)
    next(iter(mutant['selected_inputs'].values()))['path'] = 'different/source.json'
    rejects(lambda: validate_manifest(mutant))
    row = next(iter(value['receipts'].values()))
    raw = unpack(HERE / row['path'], row)
    with tempfile.TemporaryDirectory(prefix='pooled-transport-controls-') as temporary:
        path = Path(temporary) / 'receipt.gz'
        rejects(lambda: unpack(path, row))
        path.write_bytes(regular(HERE / row['path']) + b'changed')
        rejects(lambda: unpack(path, row))
        path.write_bytes(regular(HERE / row['path']))
        wrong = dict(row, payload_sha256='0' * 64)
        rejects(lambda: unpack(path, wrong))
        wrong = dict(row, payload_bytes=len(raw) + 1)
        rejects(lambda: unpack(path, wrong))
        link = Path(temporary) / 'linked.gz'
        link.symlink_to(path)
        rejects(lambda: unpack(link, row))
        selected = next(iter(value['selected_inputs'].values()))
        missing = Path(temporary) / 'selected.json'
        rejects(lambda: selected_bytes(missing, selected))
        missing.write_bytes(b'changed canonical input')
        rejects(lambda: selected_bytes(missing, selected))
    return count
