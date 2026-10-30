"""Small rejecting controls for source pins and Git-free inventory; no source execution."""
from copy import deepcopy
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
v = types.ModuleType('bridge_replay_controls')
v.__file__ = str(HERE/'verify.py')
exec(compile((HERE/'verify.py').read_bytes(), v.__file__, 'exec'), v.__dict__)


class ReplayControls(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='source-bridge-controls-')
        self.root = Path(self.directory.name).resolve()
        (self.root/'input.txt').write_bytes(b'finite source\n')
        raw = (self.root/'input.txt').read_bytes()
        self.row = dict(path='input.txt',usage='input',sha256=sha256(raw).hexdigest(),
                       git_blob=sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())
        self.sources = dict(schema_version=1,base_commit='1'*40,files=[self.row])
        self.replay = dict(schema_version=1,inputs=['input.txt'])

    def tearDown(self):
        # Check the resolved target before recursive cleanup of this test-owned tempdir.
        self.assertEqual(self.root, Path(self.directory.name).resolve())
        self.assertEqual(self.root.parent, Path(tempfile.gettempdir()).resolve())
        self.directory.cleanup()

    def test_positive(self):
        self.assertEqual(v.authenticate(self.root,self.sources,self.replay), {'input.txt'})

    def test_corrupt_pins(self):
        for field,value in [('sha256','0'*64),('git_blob','0'*40),('path','../input.txt'),
                            ('path','/input.txt'),('path','./input.txt'),('path','x\\input.txt'),
                            ('usage','silently-skip')]:
            with self.subTest(field=field,value=value):
                bad=deepcopy(self.sources);bad['files'][0][field]=value
                with self.assertRaises(ValueError):v.authenticate(self.root,bad,self.replay)

    def test_duplicate_missing_and_undeclared(self):
        bad=deepcopy(self.sources);bad['files'].append(deepcopy(self.row))
        with self.assertRaises(ValueError):v.authenticate(self.root,bad,self.replay)
        bad=deepcopy(self.sources);bad['files']=[]
        with self.assertRaises(ValueError):v.authenticate(self.root,bad,self.replay)
        with self.assertRaises(ValueError):v.authenticate(self.root,self.sources,dict(schema_version=1,inputs=[]))

    def test_changed_live_bytes(self):
        (self.root/'input.txt').write_bytes(b'changed\n')
        with self.assertRaises(ValueError):v.authenticate(self.root,self.sources,self.replay)

    def export_manifest(self):
        d=dict(format='research-package-export-v1',commit='1'*40,
               package='research/selected-compiler-source-bridge',
               files=[dict(path='input.txt',mode=0o644,size=len((self.root/'input.txt').read_bytes()),
                           sha256=self.row['sha256'])])
        (self.root/'.research-export.json').write_text(json.dumps(d),encoding='utf-8')

    def test_export_missing_manifest(self):
        with self.assertRaises(ValueError):v.export_integrity(self.root)

    def test_export_positive_and_extra_file(self):
        self.export_manifest();self.assertEqual(v.export_integrity(self.root),1)
        (self.root/'extra.txt').write_text('not declared')
        with self.assertRaises(ValueError):v.export_integrity(self.root)

    def test_export_corruption_and_omission(self):
        self.export_manifest();(self.root/'input.txt').write_bytes(b'changed')
        with self.assertRaises(ValueError):v.export_integrity(self.root)
        (self.root/'input.txt').unlink()
        with self.assertRaises(ValueError):v.export_integrity(self.root)


    def test_export_bad_labels(self):
        self.export_manifest()
        path=self.root/'.research-export.json'
        original=json.loads(path.read_bytes())
        for field,value in [('format','wrong'),('commit','not-a-commit'),('package','research/other')]:
            with self.subTest(field=field):
                bad=deepcopy(original);bad[field]=value
                path.write_text(json.dumps(bad),encoding='utf-8')
                with self.assertRaises(ValueError):v.export_integrity(self.root)

    def test_export_duplicate_and_size_mode_controls(self):
        self.export_manifest();path=self.root/'.research-export.json'
        original=json.loads(path.read_bytes())
        cases=[]
        bad=deepcopy(original);bad['files'].append(deepcopy(bad['files'][0]));cases.append(bad)
        for field,value in [('size',-1),('mode',0o777),('path','../input.txt')]:
            bad=deepcopy(original);bad['files'][0][field]=value;cases.append(bad)
        for bad in cases:
            with self.subTest(bad=bad):
                path.write_text(json.dumps(bad),encoding='utf-8')
                with self.assertRaises(ValueError):v.export_integrity(self.root)


if __name__ == '__main__':
    unittest.main()
