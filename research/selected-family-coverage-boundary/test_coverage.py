#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact family-ledger controls, not physical geometry or two-unpaid admission."""
from pathlib import Path
from copy import deepcopy
import tempfile
import types
import unittest

HERE=Path(__file__).resolve().parent
m=types.ModuleType('coverage_source'); m.__file__=str(HERE/'verify.py')
exec(compile((HERE/'verify.py').read_bytes(),m.__file__,'exec'),m.__dict__)


class Tests(unittest.TestCase):
    def setUp(self): self.rows=[[0,2,12,44],[1,3,8,40],[2,4,9,31]]

    def test_complete_family_ledger(self):
        self.assertIsNone(m.validate_family_rows(self.rows))
        self.assertEqual(m.aggregate_mass(self.rows,0),216)

    def test_aggregate_mass_does_not_imply_family_coverage(self):
        rows=deepcopy(self.rows); rows[0][3]-=1; rows[1][3]+=1
        self.assertEqual(m.aggregate_mass(rows,0),m.aggregate_mass(self.rows,0))
        with self.assertRaises(ValueError): m.validate_family_rows(rows)

    def test_second_unpaid_is_not_relabelling(self):
        with self.assertRaises(ValueError): m.validate_family_rows(self.rows,unpaid=2)
        rows=deepcopy(self.rows)
        for row in rows: row[3]-=1
        self.assertIsNone(m.validate_family_rows(rows,unpaid=2))
        self.assertEqual(m.aggregate_mass(self.rows,0)-m.aggregate_mass(rows,0),3)
        with self.assertRaises(ValueError): m.validate_family_rows(rows)

    def test_refinement_and_deferral_telescope(self):
        rows=deepcopy(self.rows)
        for row in rows: row[2]-=3; row[3]+=3
        self.assertIsNone(m.validate_family_rows(rows))
        self.assertEqual(m.aggregate_mass(rows,0),m.aggregate_mass(self.rows,0))

    def test_partition_conservation(self):
        for mod in (1,2,3,7):
            groups={}
            for f,k,h,i in self.rows: groups[f%mod]=groups.get(f%mod,0)+73-8*k-h-i
            self.assertEqual(sum(groups.values()),len(self.rows))

    def test_typed_negative_guard(self):
        with self.assertRaises(ValueError): m.validate_family_rows(self.rows,unpaid=True)
        bad=deepcopy(self.rows); bad[0][2]=-1
        with self.assertRaises(ValueError): m.validate_family_rows(bad)
        self.assertNotEqual(m.canon({'mass':1}),m.canon({'mass':True}))

    def test_coordinate_change_does_not_supply_endpoint(self):
        # Equal dimension can describe different axis spaces. The ledger
        # deliberately must not purport to verify these physical subspaces.
        a=(1,2); b=(1,4)
        self.assertEqual(m.binary_rank(a),m.binary_rank(b)); self.assertNotEqual(set(a),set(b))

    def test_actual_loader_missing_and_corrupt(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): m.load(Path(tmp))
            path=Path(tmp)/m.ARCHIVE; path.parent.mkdir(parents=True); path.write_bytes(b'corrupt')
            with self.assertRaises(ValueError): m.load(Path(tmp))


if __name__=='__main__': unittest.main()
