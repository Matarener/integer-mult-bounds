# SPDX-License-Identifier: Apache-2.0
"""Distinguishing boundary controls for Git-free materialization."""
import gzip,hashlib,io,json,tarfile,tempfile
from pathlib import Path
import importlib.util
_spec=importlib.util.spec_from_file_location("scientific_materialize",Path(__file__).resolve().parent/"materialize.py")
_module=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_module)
build=_module.build
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def test():
 with tempfile.TemporaryDirectory(prefix='t16-materialize-controls-')as tmp:
  root=Path(tmp);repo=root/'main';repo.mkdir();(repo/'a').write_bytes(b'alpha')
  def archive(items):
   p=root/'overlay.tar.gz'
   with tarfile.open(p,'w:gz')as tar:
    for name,b in items:
     e=tarfile.TarInfo(name);e.size=len(b);tar.addfile(e,io.BytesIO(b))
   return p
  def recipe(extra=None):
   d={'entries':{'source/a':{'source_kind':'canonical_main','source_path':'a','bytes':5,'sha256':hashlib.sha256(b'alpha').hexdigest()},'source/b':{'source_kind':'overlay','source_path':'source/b','bytes':4,'sha256':hashlib.sha256(b'beta').hexdigest()}},'original_bundle_manifest':{'scope':'test only'}}
   if extra:extra(d)
   p=root/'recipe.json';p.write_text(json.dumps(d));return p
  r=recipe();o=archive([('source/b',b'beta')]);build(repo,r,o,root/'positive',sha(r),sha(o));assert(root/'positive/source/a').read_bytes()==b'alpha'
  count=1
  def reject(label,fn):
   nonlocal count
   try:fn()
   except (ValueError,AssertionError):count+=1
   else:raise AssertionError('accepted '+label)
  reject('archive authentication',lambda:build(repo,r,o,root/'bad-hash',sha(r),'0'*64))
  (repo/'a').write_bytes(b'ALPHA');reject('changed mainfile',lambda:build(repo,r,o,root/'bad-main',sha(r),sha(o)));(repo/'a').write_bytes(b'alpha')
  o=archive([('source/b',b'BETA')]);reject('corrupt overlay payload despite updated archivehash',lambda:build(repo,r,o,root/'bad-payload',sha(r),sha(o)))
  o=archive([('../escape',b'x'),('source/b',b'beta')]);reject('archive traversal',lambda:build(repo,r,o,root/'bad-path',sha(r),sha(o)))
  o=archive([('source/b',b'beta'),('extra',b'x')]);reject('extra archiveentry',lambda:build(repo,r,o,root/'bad-extra',sha(r),sha(o)))
  o=archive([('source/b',b'beta'),('source/b',b'beta')]);reject('duplicate entry',lambda:build(repo,r,o,root/'bad-duplicate',sha(r),sha(o)))
  o=archive([('source/b',b'beta')]);r=recipe(lambda d:d['entries']['source/a'].update(source_path='../escape'));reject('mainfile traversal',lambda:build(repo,r,o,root/'bad-sourcepath',sha(r),sha(o)))
  o=archive([]);r=recipe();reject('missing archiveentry',lambda:build(repo,r,o,root/'bad-missing',sha(r),sha(o)))
  if any(p.name.startswith('bad-')for p in root.iterdir()):raise AssertionError('invalid input wrote output')
  return {'controls_passed':count,'failed_inputs_write_no_output':True}
if __name__=='__main__':print(json.dumps(test()))
