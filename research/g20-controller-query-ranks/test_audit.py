"""Self-contained controls for the independent controller-query checker.
Dennis / antunishdPursuit with OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit import audit, projector_rank


def fixture(ports=2, reverse=False):
    c = {'ambient_rank': 15, 'pairs': 1,
         'invoice': {'thick_stages': [0, 1], 'whole_idle': {'7': 2 * ports}, 'thin_queries': ports},
         'physical_events': [['IDLE', 0, [0]], ['QUERY_SHEAR', 2, 0, reverse]]}
    n = 2 * ports
    records = [['OWNED_CLEAR', n, None, None]]
    for bank in range(2):
        for p in range(ports):
            records.append(['QUERY', bank * ports + p, 7, ['WHOLE_IDLE', [0], p]])
    for p in range(ports):
        source, target = (1, 0) if reverse else (0, 1)
        records += [['ADD', n, source * ports + p, ['THIN_COPY', 2, p]],
                    ['QUERY', n, 1, ['THIN', 2, p]],
                    ['ADD', target * ports + p, n, ['THIN_DELIVER', 2, p]],
                    ['OWNED_CLEAR', n, None, ['THIN', 2, p]]]
    return c, records, n


class Controls(unittest.TestCase):
    def test_projectors(self):
        self.assertEqual(projector_rank([0, 1, 3], [0, 3]), 14)
        self.assertEqual(projector_rank([0, 1, 3], [], central=True), 1)
        for stages in ([0, 0], [2]):
            with self.assertRaises(ValueError):
                projector_rank([0, 1, 3], stages)

    def test_positive_ports_and_reversal(self):
        for ports in [1, 2, 3]:
            for reverse in [False, True]:
                c, records, n = fixture(ports, reverse)
                result = audit(c, records, n, 1, ports)
                self.assertEqual(result['component_rank_mass'], 15 * ports)
                self.assertEqual(result['controller_queries'], 3 * ports)

    def test_semantic_rejections(self):
        c, records, n = fixture()
        # QUERY index 6; copy 5, delivery 7, clear 8.
        cases = [
            ('wrong idle rank', lambda r: r[1].__setitem__(2, 8)),
            ('equal-rank wrong stages', lambda r: r[1][3].__setitem__(1, [1])),
            ('wrong idle owner', lambda r: r[1].__setitem__(1, 1)),
            ('wrong thin rank', lambda r: r[6].__setitem__(2, 2)),
            ('borrowed query field', lambda r: r[6].__setitem__(1, 0)),
            ('wrong copy source', lambda r: r[5].__setitem__(2, 2)),
            ('wrong delivery', lambda r: r[7].__setitem__(1, 0)),
            ('borrowed erasure', lambda r: r[8].__setitem__(1, 0)),
            ('missing erasure', lambda r: r.pop(8)),
            ('dirty scratch', lambda r: r.pop(0)),
            ('missing query', lambda r: r.pop(1)),
            ('extra query', lambda r: r.append(deepcopy(r[1]))),
            ('unknown query', lambda r: r[1][3].__setitem__(0, 'UNKNOWN')),
        ]
        for name, mutation in cases:
            with self.subTest(name=name):
                bad = deepcopy(records); mutation(bad)
                with self.assertRaises(ValueError):
                    audit(c, bad, n, 1, 2)

    def test_controller_rejections(self):
        c, records, n = fixture()
        for name, mutation in [
            ('wrong idle bill', lambda x: x['invoice']['whole_idle'].__setitem__('7', 5)),
            ('wrong thin count', lambda x: x['invoice'].__setitem__('thin_queries', 3)),
            ('duplicate idle stage', lambda x: x['physical_events'][0].__setitem__(2, [0, 0])),
            ('wrong dimension', lambda x: x.__setitem__('ambient_rank', 16)),
        ]:
            with self.subTest(name=name):
                bad = deepcopy(c); mutation(bad)
                with self.assertRaises(ValueError):
                    audit(bad, records, n, 1, 2)


if __name__ == '__main__':
    unittest.main()
