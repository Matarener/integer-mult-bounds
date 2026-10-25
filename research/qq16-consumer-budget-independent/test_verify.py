#!/usr/bin/env python3
"""Behavioral controls; no network, Git objects or predecessor imports needed."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
import gzip
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
V = runpy.run_path(str(HERE / 'verify.py'))
ROOT = V['ROOT']
BASE = {1:2428, 2:418, 3:432, 4:142, 5:82}
A = Q(836330098538459, 499163669901461541)


class Audit(unittest.TestCase):
    def test_01_complete_receipt(self):
        self.assertEqual(V['canonical'](V['calculate']()),
                         V['canonical'](V['decode']((HERE / 'RESULT.json').read_bytes())))

    def test_02_log_integral_enclosures(self):
        self.assertEqual(V['integral_log'](Q(1)), (0, 0))
        lo, hi = V['logarithm'](Q(2))
        known = Q(693147180559945309417, 10**21)
        self.assertLess(lo, known)
        self.assertGreater(hi, known + Q(1, 10**21))
        for y in [Q(9,8), Q(73,51), Q(2)]:
            coarse = V['integral_log'](y, 16)
            fine = V['integral_log'](y, 128)
            self.assertLessEqual(coarse[0], fine[0])
            self.assertLessEqual(fine[1], coarse[1])
            self.assertGreaterEqual(fine[0], 1 - 1/y)
            self.assertLessEqual(fine[1], y-1)
        with self.assertRaisesRegex(ValueError, 'domain'):
            V['logarithm'](Q(1,2))

    def test_03_exp_tail_and_rounding(self):
        self.assertEqual(V['exponential'](Q(0), Q(0)), (1,1))
        lo, hi = V['exponential'](Q(1,2), Q(1,2), 12)
        # Independently bounded e^(1/2), from squaring a known e enclosure.
        self.assertLess(lo*lo, Q(2718281828459045235361, 10**21))
        self.assertGreater(hi*hi, Q(2718281828459045235362, 10**21))
        self.assertLess(hi-lo, Q(1,10**12))
        self.assertEqual(V['outward'](Q(1,3),Q(2,3))[0] <= Q(1,3), True)
        self.assertEqual(V['outward'](Q(1,3),Q(2,3))[1] >= Q(2,3), True)
        with self.assertRaisesRegex(ValueError, 'domain'):
            V['exponential'](Q(0), Q(1))

    def test_04_idle_mass_relaxation(self):
        for r in [1,2,3,4,5,8,17,34,50]:
            lo, hi = V['cost'](r,A)
            rlo, rhi = V['cost'](51,A)
            self.assertGreater(lo/r, rhi/51)
            zlo, zhi = V['cost'](r,Q(0))
            self.assertLessEqual(zlo, Q(r,73))
            self.assertGreaterEqual(zhi, Q(r,73))
        with self.assertRaisesRegex(ValueError, 'halving'):
            V['moment'](BASE,336,64,False,A,52)

    def test_05_omitted_decoder_changes_decision(self):
        self.assertLess(V['moment'](BASE,0,64,True,A)[1],1)
        self.assertGreater(V['moment'](BASE,336,64,False,A)[0],1)
        # Even deleting two whole groups of 112 leaves 112, above the full threshold.
        self.assertGreater(V['moment'](BASE,112,64,True,A)[0],1)

    def test_06_thresholds_and_repayment(self):
        for rank8,last in [(False,121),(True,61)]:
            self.assertLess(V['moment'](BASE,last,64,rank8,A)[1],1)
            self.assertGreater(V['moment'](BASE,last+1,64,rank8,A)[0],1)
        self.assertLess(V['moment'](BASE,363,63,True,A)[1],1)
        self.assertGreater(V['moment'](BASE,364,63,True,A)[0],1)
        self.assertGreater(V['moment'](BASE,336,64,True,A)[0],1)

    def test_07_negative_and_excess_budget(self):
        with self.assertRaisesRegex(ValueError, 'negative budget'):
            V['moment'](BASE,-1,64,True,A)
        with self.assertRaisesRegex(ValueError, 'negative idle'):
            V['moment'](BASE,10000,64,True,A)

    def test_08_literal_omissions(self):
        c = V['decode'](gzip.decompress(V['pinned']('research/joint-query/certificate.json.gz')))
        original = V['profile'](c,V['expand'](c,'F_0'))
        altered = deepcopy(c)
        altered['programs']['F_0'] = [e for e in altered['programs']['F_0'] if e[0] != 'private_sweep']
        self.assertNotEqual(V['profile'](altered,V['expand'](altered,'F_0')), original)
        changed = deepcopy(c)
        next(e for e in changed['core_words']['forward'] if e[0]=='climb')[5] = 2
        self.assertNotEqual(V['profile'](changed,V['expand'](changed,'F_0')), original)
        changed['programs']['F_0'].append(['unknown'])
        with self.assertRaisesRegex(ValueError, 'unknown event'):
            V['expand'](changed,'F_0')

    def test_09_source_and_manifest_controls(self):
        manifest = V['decode']((HERE/'SOURCES.json').read_bytes())
        path = 'certificates/selected-result.json'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/path).parent.mkdir(parents=True)
            (root/path).write_bytes((ROOT/path).read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'SHA256'):
                V['pinned'](path,root,manifest)
            (root/path).write_bytes((ROOT/path).read_bytes())
            duplicate = deepcopy(manifest)
            duplicate['files'].append(deepcopy(duplicate['files'][0]))
            with self.assertRaisesRegex(ValueError,'unique input'):
                V['pinned'](path,root,duplicate)
            manifest['files'][0]['git_blob'] = '0'*40
            with self.assertRaisesRegex(ValueError,'Git blob'):
                V['pinned'](path,root,manifest)
        with self.assertRaisesRegex(ValueError,'duplicate JSON'):
            V['decode']('{"a":1,"a":2}')
        self.assertNotEqual(V['canonical']({'a':1}),V['canonical']({'a':True}))

    def test_10_retained_original_replay(self):
        meta = V['decode']((HERE/'PREDECESSORS.json').read_bytes())
        archive = (HERE/'vendor/PR3908.tar.gz').read_bytes()
        self.assertEqual(sha256(archive).hexdigest(),meta['archive_sha256'])
        expected = {r['path']:r for r in meta['files']}
        self.assertEqual(len(expected),7)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as t:
                members=t.getmembers()
                self.assertEqual(len(members),7)
                self.assertEqual({m.name for m in members},set(expected))
                for member in members:
                    self.assertTrue(member.isfile())
                    self.assertNotIn('..',Path(member.name).parts)
                    self.assertFalse(Path(member.name).is_absolute())
                    b=t.extractfile(member).read()
                    self.assertEqual(sha256(b).hexdigest(),expected[member.name]['sha256'])
                    self.assertEqual(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),expected[member.name]['git_blob'])
                    dest=root/member.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
            manifest=V['decode']((HERE/'SOURCES.json').read_bytes())
            for row in manifest['files']:
                if row['usage']=='input':
                    dest=root/row['path'];dest.parent.mkdir(parents=True,exist_ok=True)
                    dest.write_bytes(V['pinned'](row['path']))
            result=subprocess.run([sys.executable,'-I','-O','-Werror','-B',
                                   str(root/'research/qq16-consumer-cap-audit/verify.py')],
                                  cwd=root,check=True,capture_output=True,text=True,timeout=60)
            answer=json.loads(result.stdout)
            self.assertEqual(answer['status'],'PASS_QQ16_CONSUMER_CAP_BELOW_SELECTED no_new_kappa')
            self.assertEqual(answer['display_decimal'],'1.000097677879937')
            # This predecessor output is a lower bound, not a feasibility proof.
            self.assertGreater(Q(answer['display_decimal']), Q(100009,100000))

    def test_11_rebound_semantic_mutants(self):
        """Rebind hashes deliberately: semantic checks must also reject."""
        original=V['pinned']
        cp='research/joint-query/certificate.json.gz'
        rp='research/joint-query/evidence/CONSERVED-QQ16.json'
        packet=V['decode'](gzip.decompress(original(cp)))
        reported=V['decode'](original(rp))
        # Wire mutation preserves every rank/count, but changes caller applicability.
        next(e for e in packet['core_words']['forward'] if e[0]=='climb')[2]=547
        payload=V['canonical'](packet)
        reported['payload_sha256']=sha256(payload).hexdigest()
        replacements={cp:gzip.compress(payload,mtime=0),rp:V['canonical'](reported)}
        def load(path,*args,**kwargs):
            return replacements.get(path) if path in replacements else original(path,*args,**kwargs)
        with patch.dict(V['calculate'].__globals__,{'pinned':load}):
            with self.assertRaisesRegex(ValueError,'first F0 caller'):
                V['calculate']()
        # A deleted line cannot acquire the original invoice through a new hash.
        dp='research/qq16-line-normalized-decoder/WORD.json'
        word=V['decode'](original(dp));word.remove(next(e for e in word if e[0]=='line'))
        replacements.clear();replacements[dp]=V['canonical'](word)
        with patch.dict(V['calculate'].__globals__,{'pinned':load}):
            with self.assertRaisesRegex(ValueError,'literal decoder inventory'):
                V['calculate']()


if __name__=='__main__':
    unittest.main()
