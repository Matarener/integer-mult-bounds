#!/usr/bin/env python3
"""Rebind every guarded physical-fixture check to the final literal BIT word."""
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = HERE.parent/'kappa-next-regime'
WORD_SHA = 'f84bdf9b2d4e8758584e3a4759519acc2307e3723fb23568bb7ed4fde617a908'


def main():
    source = OLD/'word-search/physical_probe.py'
    invoice_path = HERE/'bit-integration/early-birth-prefixes/RESULT.json'
    native_path = HERE/'bit-integration/FINAL-NATIVE-REVIEW.json'
    invoice, native = (json.loads(p.read_text()) for p in (invoice_path, native_path))
    template = json.loads(gzip.decompress((HERE/'bit-integration/early-birth-prefixes/GLOBAL-TEMPLATE.json.gz').read_bytes()))
    assert invoice['word_content_sha256'] == native['actual_word_content_sha256'] == WORD_SHA
    assert invoice['paid_requests'] == native['canonical_requests'] == 987525
    program = template['local_programs']['forward']
    sites = [i for i, event in enumerate(program) if event == [2,475,659,515,0,7,0]]
    assert len(sites) == 1
    first = sites[0]
    last = first+65
    assert program[last-1] == [3,475,659,515,0,0,0]
    paid = sum(event[0] in (0,2) for event in program)
    ordinal = sum(event[0] in (0,2) for event in program[:first])
    assert paid == sum(invoice['local_profile'].values()) == 2913
    # The runtime checks these independently through catalogue.identifier().
    replica_one, replica_two = paid+ordinal, 2*paid+ordinal
    changes = [
        ('Actual T35 A/C-refined R437 records', 'Actual T35 final early-birth-prefix R437 records'),
        ("ADAPTER = SCOPE / 'native-catalogue/adapter.py'", "ADAPTER = SCOPE.parent / 'kappa-next-regime/native-catalogue/adapter.py'"),
        ("WORD = HERE / 'candidate/WORD.json.gz'", "WORD = SCOPE / 'bit-word/early-birth-prefixes/WORD.json.gz'"),
        ("TEMPLATE = SCOPE / 'geometry-search/pool35-word/GLOBAL-TEMPLATE.json.gz'", "TEMPLATE = HERE / 'early-birth-prefixes/GLOBAL-TEMPLATE.json.gz'"),
        ("ORIGINAL = SCOPE / 'sources/PR3967/research/r437-oq4-caller-binding/physical_probe.py'", "ORIGINAL = SCOPE.parent / 'kappa-next-regime/sources/PR3967/research/r437-oq4-caller-binding/physical_probe.py'"),
        ('3f7de7e1d8a6ff9da8ab7650209b559062da4cc053de2b2566b306eb4fbeffd0', WORD_SHA),
        ('af8e500f0ff8c3ef4842d2529991975bf32a675f026cbc55100136d21a399877', invoice['template_content_sha256']),
        ('ddd9dd6f3d1842744d5a677c3b1391923c9add0082a76de53b304d062eb466e4', native['binding_sha256']),
        ('22011', str(first)), ('22076', str(last)), ('4518', str(replica_one)), ('7433', str(replica_two)), ('988155', '987525'),
        ('PASS_ACTUAL_T35_AC_WORD_NESTED_PHYSICAL_PROTOCOL', 'PASS_ACTUAL_T35_FINAL_EARLY_BIRTH_NESTED_PHYSICAL_PROTOCOL'),
    ]
    payload = source.read_text()
    counts = []
    for old, new in changes:
        count = payload.count(old)
        assert count > 0, old
        payload = payload.replace(old, new)
        counts.append({'old': old, 'new': new, 'occurrences': count})
    destination = HERE/'bit-integration/final_physical_probe.py'
    data = payload.encode()
    if destination.exists():
        assert destination.read_bytes() == data, 'exact generated fixture'
    else:
        destination.write_bytes(data)
    result = {
        'status': 'PASS_FINAL_NATIVE_PHYSICAL_FIXTURE_BINDING',
        'source_sha256': {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in (source, Path(__file__), invoice_path, native_path)},
        'generated_script_sha256': sha256(data).hexdigest(),
        'literal_replacements': counts,
        'copy_window': [first, last], 'copy_replica_one_id': replica_one, 'copy_replica_two_id': replica_two,
        'scope': 'Only source paths, pins and actual native site identifiers change. Every physical fixture operation and guard is retained. This generation receipt alone does not claim execution of the fixture or a complete GL64 packet.',
    }
    (HERE/'bit-integration/FINAL-PHYSICAL-BINDING.json').write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'copy_window', 'copy_replica_one_id', 'copy_replica_two_id')}, sort_keys=True))


if __name__ == '__main__':
    main()
