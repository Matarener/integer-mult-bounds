#!/usr/bin/env python3
"""Bind the inherited guarded physical fixture to the achieved BIT word.

Only source paths, exact pins, native COPY positions and native identifiers
change. The controlled fixture and every runtime guard remain identical.
It is a two-level 46-bit protocol check, not full GL64 residual execution.
Apache-2.0; predecessor attribution is retained in the generated script.
"""
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = HERE.parent / 'kappa-next-regime'


def main():
    source = OLD / 'word-search/physical_probe.py'
    native = json.loads((HERE / 'bit-integration/RETIMED444-NATIVE-REVIEW.json').read_text())
    invoice = json.loads((HERE / 'bit-integration/retimed444/RESULT.json').read_text())
    template = json.loads(gzip.decompress((HERE / 'bit-integration/retimed444/GLOBAL-TEMPLATE.json.gz').read_bytes()))
    assert invoice['word_content_sha256'] == 'ddc4f70ef7e0721f25bc5a2027ec09671457384aeb22b45f1a7dae33dae6482a'
    assert invoice['template_content_sha256'] == '80d43131cd84269c5cc05b829315a4ec0acce65371a9d8adb52e91f7c5208aaf'
    assert native['binding_sha256'] == 'd1575b8d4d89140088eebe6bd13dc2867b43ef0008560d273dbcdd6b57400b0c'
    assert native['canonical_requests'] == 987840
    program = template['local_programs']['forward']
    assert program[21607] == [2,475,659,515,0,7,0]
    assert program[21671] == [3,475,659,515,0,0,0]
    changes = [
        ('Actual T35 A/C-refined R437 records', 'Actual T35 SOURCE-resynthesized and retimed R437 records'),
        ("ADAPTER = SCOPE / 'native-catalogue/adapter.py'", "ADAPTER = SCOPE.parent / 'kappa-next-regime/native-catalogue/adapter.py'"),
        ("WORD = HERE / 'candidate/WORD.json.gz'", "WORD = SCOPE / 'bit-word/retimed444/WORD.json.gz'"),
        ("TEMPLATE = SCOPE / 'geometry-search/pool35-word/GLOBAL-TEMPLATE.json.gz'", "TEMPLATE = HERE / 'retimed444/GLOBAL-TEMPLATE.json.gz'"),
        ("ORIGINAL = SCOPE / 'sources/PR3967/research/r437-oq4-caller-binding/physical_probe.py'", "ORIGINAL = SCOPE.parent / 'kappa-next-regime/sources/PR3967/research/r437-oq4-caller-binding/physical_probe.py'"),
        ('3f7de7e1d8a6ff9da8ab7650209b559062da4cc053de2b2566b306eb4fbeffd0', invoice['word_content_sha256']),
        ('af8e500f0ff8c3ef4842d2529991975bf32a675f026cbc55100136d21a399877', invoice['template_content_sha256']),
        ('ddd9dd6f3d1842744d5a677c3b1391923c9add0082a76de53b304d062eb466e4', native['binding_sha256']),
        ('22011', '21607'), ('22076', '21672'), ('4518', '4516'), ('7433', '7430'), ('988155', '987840'),
        ('PASS_ACTUAL_T35_AC_WORD_NESTED_PHYSICAL_PROTOCOL', 'PASS_ACTUAL_T35_RETIMED444_NESTED_PHYSICAL_PROTOCOL'),
    ]
    payload = source.read_text()
    counts = []
    for old, new in changes:
        count = payload.count(old)
        assert count > 0, old
        payload = payload.replace(old, new)
        counts.append({'old': old, 'new': new, 'occurrences': count})
    destination = HERE / 'bit-integration/physical_probe.py'
    data = payload.encode()
    if destination.exists():
        assert destination.read_bytes() == data, 'existing generated probe is exact'
    else:
        destination.write_bytes(data)
    result = {
        'status': 'PASS_EXACT_PHYSICAL_FIXTURE_REBIND',
        'source_sha256': {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in (source, Path(__file__), HERE/'bit-integration/RETIMED444-NATIVE-REVIEW.json', HERE/'bit-integration/retimed444/RESULT.json')},
        'generated_script_sha256': sha256(data).hexdigest(),
        'literal_replacements': counts,
        'scope': 'Exact source-binding and native-site changes only. Every physical fixture operation and guard is retained. The generated runtime must still be executed; this construction receipt is not that execution.',
    }
    (HERE / 'bit-integration/PHYSICAL-REBIND.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'], result['generated_script_sha256'])


if __name__ == '__main__':
    main()
