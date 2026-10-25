#!/usr/bin/env python3
"""Portable replay of byte-preserved focused contact and native audits.

New material Apache-2.0; Chris R/Clear1nsight with OpenAI Codex assistance.
Frozen source/compiler/interval authors retain the notices in the capsule.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,why):
    if not ok:
        raise ValueError(why)


def main():
    pins=json.loads((HERE/'SOURCES.json').read_text())['files']
    for row in pins:
        if row['usage']=='input':
            raw=(ROOT/row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest()==row['sha256'],'canonical live input '+row['path'])
            need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],
                 'canonical source object '+row['path'])
    inventory=json.loads((HERE/'CAPSULE-INVENTORY.json').read_text())['files']
    actual={str(p.relative_to(HERE)) for folder in ('capsule','expected')
            for p in (HERE/folder).rglob('*') if p.is_file()}
    need(actual==set(inventory),'complete capsule inventory')
    for rel,expected in inventory.items():
        path=HERE/rel
        need(not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest()==expected,
             'frozen capsule byte '+rel)
    vendor=HERE/'capsule/outputs/p104-native-contact-audit-20261025/sources'
    for name in ('clifford_exact.py','native_verify.py'):
        need((vendor/name).read_bytes()==(ROOT/'research/p104-native-channel/vendor'/name).read_bytes(),
             'canonical native library binding '+name)
    outputs=[]
    for slug,expected in [('p104-contact-reassessment-20261025','contact-ceiling.json'),
                          ('p104-native-contact-audit-20261025','native.json')]:
        script=HERE/'capsule/outputs'/slug/'check.py'
        command=[sys.executable]+(['-O'] if sys.flags.optimize else [])+['-B',str(script)]
        result=subprocess.run(command,cwd=HERE/'capsule',capture_output=True,timeout=60,
                              env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
        need(result.returncode==0 and not result.stderr,'focused scientific subprocess '+slug)
        need(result.stdout==(HERE/'expected'/expected).read_bytes(),'complete frozen scientific output '+slug)
        outputs.append(json.loads(result.stdout))
    for rel,expected in inventory.items():
        need(hashlib.sha256((HERE/rel).read_bytes()).hexdigest()==expected,'source unchanged '+rel)
    contact,native=outputs
    need(contact['stop'] and native['stop'] and contact['new_kappa'] is native['new_kappa'] is None,
         'no new kappa or continuing search')
    print('PASS_P104_CONTACT_INDEPENDENT_AUDIT')
    print(json.dumps({'normalized_rows':contact['independent_normalized_endpoint_rows'],
                      'native_complex_entries':native['direct_dense_complex_entries']+native['composition_complex_entries'],
                      'fixed_edit_raw_ceiling':contact['all_remaining_edits_raw_ceiling_interval'],
                      'full_parent_admitted':False,'new_kappa':None},sort_keys=True))


if __name__=='__main__':main()
