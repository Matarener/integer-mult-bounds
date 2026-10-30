#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded corruption checks for native-cache reuse and source authentication."""
import argparse,json,shutil,tempfile
from pathlib import Path
import native_auth as A

HERE=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--shipped-root',type=Path,default=HERE.parent/'native-alternatives')
    ap.add_argument('--out',type=Path,default=HERE/'FIXTURES.json')
    args=ap.parse_args();controls=[]
    A.authenticate_reused(args.shipped_root)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='native-auth-fixture-',dir=args.out.parent) as td:
        root=Path(td)
        for tag in ['base','extra']:shutil.copytree(args.shipped_root/('native-'+tag),root/('native-'+tag))
        A.authenticate_reused(root)
        for tag in ['base','extra']:A.authenticate_fresh_native(root/('native-'+tag),tag)

        def changed(name,path,transform,check):
            old=path.read_bytes() if path.exists() else None
            path.write_bytes(transform(old))
            try:
                try:check()
                except RuntimeError as error:controls.append(dict(name=name,rejected=True,reason=str(error)))
                else:raise AssertionError('accepted corrupted native fixture: '+name)
            finally:
                if old is None:path.unlink()
                else:path.write_bytes(old)

        base=root/'native-base'
        reuse=lambda:A.authenticate_reused(root)
        fresh=lambda:A.authenticate_fresh_native(base,'base')
        changed('native output bytes changed',base/'native/local/CLIFFORD-REVIEW.json',lambda b:b+b' ',reuse)
        changed('reused compiler source changed',base/'source/accelerators/sparse_state.py',lambda b:b+b'\n',reuse)
        changed('fresh actual compiler source changed',base/'source/accelerators/sparse_state.py',lambda b:b+b'\n',fresh)
        def wrong_source(raw):
            value=json.loads(raw);value['source_sha256']['accelerators/sparse_state.py']='0'*64
            return json.dumps(value).encode()
        changed('RESULT source declaration changed',base/'RESULT.json',wrong_source,fresh)
        changed('unexpected run file',base/'unexpected.json',lambda b:b'{}',reuse)
        changed('unexpected compiler source file',base/'source/unlisted.py',lambda b:b'pass\n',fresh)
        changed('wrong executed input bytes',base/'INPUT.json.gz',lambda b:b+b' ',fresh)
        def failed_stage(raw):
            value=json.loads(raw);value['steps'][2]['exit_code']=23
            return json.dumps(value).encode()
        changed('failed native stage',base/'RESULT.json',failed_stage,fresh)
        path=base/'native/local/WRAPPER-CHECKS.json';old=path.read_bytes();path.unlink()
        try:
            try:reuse()
            except RuntimeError as error:controls.append(dict(name='missing native output',rejected=True,reason=str(error)))
            else:raise AssertionError('accepted missing native output')
        finally:path.write_bytes(old)
        A.authenticate_reused(root)
    # Strip the temporary root from error messages to keep the proof receipt portable.
    for row in controls:row['reason']=row['reason'].replace(str(root),'TEMP')
    result=dict(status='PASS_NATIVE_AUTH_CORRUPTION_CONTROLS',pins_sha256=A.PINS_SHA256,
                native_auth_sha256=A.sha(HERE/'native_auth.py'),exact_copy_accepted=True,
                original_shipped_runs_unchanged=True,controls_rejected=controls)
    A.authenticate_reused(args.shipped_root)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],len(controls),'controls')

if __name__=='__main__':main()
