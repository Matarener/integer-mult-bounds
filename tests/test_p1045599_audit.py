"""Reject incomplete, changed or inconsistent audit evidence without heavy replay."""
import importlib.util
import json
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('p104_audit', ROOT/'scripts/audit_p1045599.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.evidence = self.root/'review-evidence'
        self.evidence.mkdir()
        self.primary = (b'PASS_P104_HELPER_SUBSPACE_KAPPA_00310045\n' +
                        json.dumps({'kappa':'62009/20000000', 'paid_calls':66726,
                                    'productive_fields':13048}).encode()+b'\n')
        self.candidate = {'status':'PASS_SCOPED_CALLER_AND_TARGET_BINDING',
                          'paid':{'1':2}, 'targets':{'2':1},
                          'native_checks':{'fresh_helpers':9720},
                          'field_maps':[{'local_to_global':list(range(748))} for _ in range(18)],
                          'controls':{str(n):'rejected' for n in range(10)},
                          'ordinary':{'abstract_address_phase_scalar_pass_upper':4,
                                      'retained_raw_scalar_upper':5}}
        self.save('primary', self.primary)
        self.save('optimized', self.primary)
        self.save('control', b'fixture control\n')
        self.save('candidate', json.dumps(self.candidate).encode())
        write(self.root/'source'/audit.PRIMARY/'RESULT.json',
              {'complete_cost':{'paid':{'1':2}, 'targets':{'2':1}}})

    def save(self, name, raw):
        (self.evidence/(name+'.log')).write_bytes(raw)
        write(self.evidence/(name+'.json'),
              {'exit':0,'resource_stop':None,'log_sha256':sha256(raw).hexdigest()})

    def validate(self):
        # Fixture receipts exercise admission gates, not scientific construction.
        with patch.object(audit, 'CONTROL_SHA', sha256(b'fixture control\n').hexdigest()), \
                patch.object(audit, 'authenticate_export'):
            return audit.validate(self.root)

    def test_complete_fixture(self):
        self.assertEqual(self.validate()['status'], 'PASS_SOURCE_BOUND_P1045599_FINITE_REPLAYS')

    def test_timeout_is_not_pass(self):
        p=self.evidence/'primary.json'
        value=json.loads(p.read_text()); value['resource_stop']='timeout'; write(p,value)
        with self.assertRaisesRegex(ValueError, 'Incomplete primary'):
            self.validate()

    def test_log_tampering(self):
        (self.evidence/'candidate.log').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'Changed log'):
            self.validate()

    def test_optimized_mismatch(self):
        self.save('optimized', self.primary+b'changed\n')
        with self.assertRaisesRegex(ValueError, 'outputs differ'):
            self.validate()

    def test_independent_invoice_mismatch(self):
        self.candidate['paid']['1']=3
        self.save('candidate',json.dumps(self.candidate).encode())
        with self.assertRaisesRegex(ValueError, 'invoice differs'):
            self.validate()

    def test_missing_new_helper(self):
        self.candidate['native_checks']['fresh_helpers']=9702
        self.save('candidate',json.dumps(self.candidate).encode())
        with self.assertRaisesRegex(ValueError, 'ownership/controls'):
            self.validate()

    def test_control_drift(self):
        self.save('control',b'changed\n')
        with self.assertRaisesRegex(ValueError, 'positive control'):
            self.validate()

    def test_export_corruption(self):
        repo=self.root/'repo'
        write(repo/audit.REVIEW/'EXPORT.json',
              {'head':audit.HEAD, 'files':{'x':sha256(b'original').hexdigest()}})
        write(repo/audit.REVIEW/'CALLER-EXPORT.json',{})
        (self.root/'source/x').write_bytes(b'changed')
        with patch.object(audit,'ROOT',repo), self.assertRaisesRegex(ValueError,'Changed replay input'):
            audit.authenticate_export(self.root)


if __name__ == '__main__':
    unittest.main()
