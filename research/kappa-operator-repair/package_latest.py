#!/usr/bin/env python3
"""Package the repaired continuation and preserve every prior full-ZIP byte.

The old compressed member prefix is preserved exactly. Generated runtime
clones are omitted only from this new scope; all prior members survive.
Apache-2.0. Substantial OpenAI assistance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OLD_SHA = 'f2406e81f2548873cfe624b316aa2a59f48ada97864e65d51135f40e5751db05'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path, remaining=None):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while remaining is None or remaining:
            block = f.read(4 * 1024 * 1024 if remaining is None else min(remaining, 4 * 1024 * 1024))
            if not block:
                need(remaining is None, 'Entire original compressed prefix')
                break
            h.update(block)
            if remaining is not None:
                remaining -= len(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--destination', type=Path, required=True)
    ap.add_argument('--previous-full', type=Path)
    ap.add_argument('--stage', action='store_true')
    a = ap.parse_args()
    dest = a.destination.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((HERE / 'MANIFEST.json').read_text())
    paths = []
    for base, key in [(HERE, 'files'), (REPO, 'repository_dependencies')]:
        for name, row in manifest[key].items():
            p = base / name
            need(p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], 'Manifest source ' + name)
            paths.append(p)
    paths.append(HERE / 'MANIFEST.json')
    if (HERE / 'VALIDATION.json').exists():
        paths.append(HERE / 'VALIDATION.json')
    need(len(paths) == len(set(paths)), 'Disjoint manifest namespaces')
    paths.sort()
    compact = dest / 'kappa-operator-repair-replay.zip'
    full = dest / 'integer-mult-bounds-kappa-operator-repair.zip'
    prefix = 'integer-mult-bounds/'
    with ZipFile(compact, 'w', ZIP_DEFLATED, compresslevel=6) as z:
        for p in paths:
            z.write(p, prefix + p.relative_to(REPO).as_posix())
    with ZipFile(compact) as z:
        need(z.testzip() is None, 'All compact CRCs')
        need(len(z.namelist()) == len(set(z.namelist())), 'Unique compact members')
        for p in paths:
            need(hashlib.sha256(z.read(prefix + p.relative_to(REPO).as_posix())).hexdigest() == sha(p),
                 'Every compact source byte')
    if a.stage:
        print(json.dumps(dict(status='PASS_OPERATOR_REPAIR_COMPACT_STAGE', path=str(compact),
                              bytes=compact.stat().st_size, sha256=sha(compact), members=len(paths)), indent=2))
        return
    need(a.previous_full is not None, '--previous-full required for complete delivery')
    old = a.previous_full.resolve()
    need(sha(old) == OLD_SHA, 'Exact frozen previous full deliverable')
    validation = json.loads((HERE / 'VALIDATION.json').read_text())
    need(validation['status'] == 'PASS_PORTABLE_OPERATOR_GUARDED_KAPPA_REPLAY', 'Successful portable replay')
    need(validation['manifest_sha256'] == sha(HERE / 'MANIFEST.json'), 'Validated final manifest')
    need(validation['selected_supplier'] == 'late-staged-composition'
         and validation['claim_sha256'] == manifest['current_claim_sha256']
         == sha(HERE / 'late-staged-composition/CLAIM.json'), 'Validated strongest completed claim')
    with ZipFile(old) as z:
        previous_names = set(z.namelist())
    additions = [p for p in paths if prefix + p.relative_to(REPO).as_posix() not in previous_names]
    need(all(prefix + p.relative_to(REPO).as_posix() not in previous_names for p in paths if p.is_relative_to(HERE)),
         'New scope does not replace any prior member')
    shutil.copyfile(old, full)
    with ZipFile(full, 'a', ZIP_DEFLATED, compresslevel=6) as z:
        for p in additions:
            z.write(p, prefix + p.relative_to(REPO).as_posix())
    with ZipFile(old) as before, ZipFile(full) as after:
        need(len(after.namelist()) == len(set(after.namelist())), 'Unique full members')
        for info in before.infolist():
            current = after.getinfo(info.filename)
            for key in ['CRC', 'file_size', 'compress_size', 'compress_type', 'header_offset', 'external_attr', 'date_time']:
                need(getattr(info, key) == getattr(current, key), 'Prior metadata preserved ' + info.filename)
        compressed_prefix_bytes = before.start_dir
        original_prefix_sha = sha(old, compressed_prefix_bytes)
        need(original_prefix_sha == sha(full, compressed_prefix_bytes), 'Every prior compressed byte preserved')
        for p in additions:
            need(hashlib.sha256(after.read(prefix + p.relative_to(REPO).as_posix())).hexdigest() == sha(p),
                 'Every new full-archive member byte')
        preservation = dict(prior_members=len(before.infolist()), final_members=len(after.infolist()),
                            new_members=len(additions), prior_compressed_prefix_bytes=compressed_prefix_bytes,
                            prior_compressed_prefix_sha256=original_prefix_sha,
                            all_previous_archive_members_and_compressed_bytes_preserved=True)
    outputs = [full, compact]
    for name, filename in [
        ('README.md', 'kappa-operator-repair-report.md'),
        ('late-staged-composition/CLAIM.json', 'kappa-operator-repair-claim.json'),
        ('VALIDATION.json', 'kappa-operator-repair-validation.json'),
        ('late-staged-composition/invoice/RESULT.json', 'kappa-operator-repair-complete-complex-invoice.json'),
    ]:
        p = dest / filename
        if name == 'README.md':
            def standalone(match):
                label, target = match.groups()
                return match.group(0) if '://' in target or target.startswith('#') else label + ' (`research/kappa-operator-repair/' + target + '`)'
            p.write_text(re.sub(r'\[([^\]]+)\]\(([^)]+)\)', standalone, (HERE / name).read_text()))
        else:
            shutil.copyfile(HERE / name, p)
        outputs.append(p)
    result = dict(status='PASS_OPERATOR_GUARDED_KAPPA_DELIVERABLES', **preservation,
                  manifest_sha256=sha(HERE / 'MANIFEST.json'),
                  compact_archive_all_CRCs_and_hashes_checked=True,
                  outputs=[dict(name=p.name, path=str(p), bytes=p.stat().st_size, sha256=sha(p)) for p in outputs],
                  claim='Stronger staged-entry/receiver operator-guarded conditional complex and kappa increase; the target 0.001745 remains unmet. Historical invalid complex claims are preserved only as explicitly withdrawn history.')
    (dest / 'KAPPA-OPERATOR-REPAIR-PACKAGING.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
