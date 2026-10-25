#!/usr/bin/env python3
"""Behavior and boundary controls for the independent exact scorer."""
from fractions import Fraction as F
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import score

ROOT = Path(__file__).resolve().parent
BASELINE_FIXTURE = ROOT / 'inputs/SELECTED-ASSEMBLY.json'


class ScorerTests(unittest.TestCase):
    def test_exact_dyadic_powers_by_integer_comparison(self):
        for base in [F(1), F(4, 3), F(2), F(73, 3), F(73), F(256)]:
            for depth in range(1, 6):
                denominator = 1 << depth
                for numerator in range(denominator):
                    exponent = F(numerator, denominator)
                    low, high = score.power_bounds(base, exponent, 48, 128)
                    target = base**numerator
                    self.assertLessEqual(low**denominator, target)
                    self.assertLessEqual(target, high**denominator)

    def test_near_unit_exponent_boundary(self):
        low, high = score.power_bounds(F(73), 1 - F(1, 2**200), 32, 96)
        self.assertLess(low, F(73))
        self.assertEqual(high, F(73))

    def test_exact_zero_saving_cost(self):
        for profile, width, live in [({1: 7, 3: 2}, 8, 2),
                                     (score.BIT_PROFILE, 64, 28416)]:
            exact = sum(F(r * count, width * live) for r, count in profile.items())
            self.assertEqual(score.moment(profile, width, live, F(0), False), (exact, exact))
            charged = exact + F(32 * width * sum(profile.values()), 10**16 * live)
            self.assertEqual(score.moment(profile, width, live, F(0), True), (charged, charged))

    def test_power_domain_rejections(self):
        for base, exponent in [(F(0), F(1, 2)), (F(1, 2), F(1, 2)),
                               (F(257), F(1, 2)), (F(2), F(-1)), (F(2), F(1))]:
            with self.assertRaises(ValueError):
                score.power_bounds(base, exponent)
        for bits, precision in [(0, 256), (257, 512), (160, 191), (160, 513)]:
            with self.assertRaises(ValueError):
                score.root_table(F(2), bits, precision)

    def test_changed_rank_count_is_not_a_certificate(self):
        original = json.loads(BASELINE_FIXTURE.read_bytes())
        profile = {int(r): n for r, n in original['complex_profile'].items()}
        endpoint = F(original['complex_lower'])
        profile[48] += 1
        with self.assertRaisesRegex(ValueError, 'strict moment endpoint'):
            score.endpoint_decisions(profile, 73, 14336, endpoint, False)
        original['complex_profile']['48'] += 1
        with self.assertRaisesRegex(ValueError, 'complete rank mass'):
            score.score(original)

    def test_omitted_bit_surcharge_changes_upper_decision(self):
        upper = score.BIT_ENDPOINT + F(1, 10**24)
        self.assertLess(score.moment(score.BIT_PROFILE, 64, 28416, upper, False)[1], 1)
        self.assertGreater(score.moment(score.BIT_PROFILE, 64, 28416, upper, True)[0], 1)

    def test_all_selected_slacks_and_bootstrap_are_exact(self):
        original = json.loads(BASELINE_FIXTURE.read_bytes())
        saving, rows = score.bootstrap(score.BIT_ENDPOINT, F(original['complex_lower']))
        self.assertEqual(rows, original['bootstrap'])
        slacks, _ = score.outer_slacks(saving, F(original['complex_lower']), F(original['kappa']))
        self.assertEqual({k: str(v) for k, v in slacks.items()}, original['outer'])
        corrupted = dict(original)
        corrupted['outer'] = dict(original['outer'], literal_scalar_guard='0')
        with self.assertRaisesRegex(ValueError, '47 slacks agree'):
            score.score(corrupted)

    def test_caps_and_profile_domains_fail_closed(self):
        for args in [({}, 73, 14336), ({0: 1}, 73, 14336),
                     ({73: 1}, 73, 14336), ({1: 0}, 73, 14336),
                     ({1: 1}, 73, 0), ({1: True}, 73, 1)]:
            with self.assertRaises(ValueError):
                score.moment(*args, F(0), False)
        with self.assertRaises(ValueError):
            score.endpoint_decisions({52: 1}, 73, 14336, F(1, 1000), False)

    def test_surcharge_and_invocation_metadata_are_load_bearing(self):
        original = json.loads(BASELINE_FIXTURE.read_bytes())
        for key, value, reason in [('surcharge_model', {'complex': True, 'bit': False}, 'surcharge conventions'),
                                   ('provider_counts', {'gauge44': 72}, 'invocation count')]:
            corrupted = dict(original)
            corrupted[key] = value
            with self.assertRaisesRegex(ValueError, reason):
                score.score(corrupted)

    def test_candidate_source_hash_chain(self):
        inputs = ROOT / 'inputs'
        assembly = json.loads((inputs / 'ASSEMBLY.json').read_bytes())
        bindings = (inputs / 'data', inputs / 'PREFIX-AND-INVOICE.json',
                    inputs / 'OWNERS-AND-PROFILE.json', inputs / 'PR589-EXPECTED.json')
        hashes = score.bind_candidate(assembly, *bindings)
        self.assertEqual(len(hashes), 6)
        corrupted = json.loads(json.dumps(assembly))
        corrupted['input_sha256']['fresh_invoice'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'invoice hash chain'):
            score.bind_candidate(corrupted, *bindings)
        corrupted = json.loads(json.dumps(assembly))
        corrupted['complex_profile']['1'] += 1
        with self.assertRaisesRegex(ValueError, 'profile/scoring binding'):
            score.bind_candidate(corrupted, *bindings)

    def test_cli_keeps_existing_output(self):
        with tempfile.TemporaryDirectory() as scratch:
            output = Path(scratch) / 'existing.json'
            output.write_bytes(b'preserve me\n')
            child = subprocess.run([sys.executable, '-O', '-B', str(ROOT / 'score.py'),
                                    '--assembly', str(BASELINE_FIXTURE), '--output', str(output)],
                                   capture_output=True, timeout=10)
            self.assertNotEqual(child.returncode, 0)
            self.assertIn(b'fresh output only', child.stderr)
            self.assertEqual(output.read_bytes(), b'preserve me\n')


if __name__ == '__main__':
    unittest.main()
