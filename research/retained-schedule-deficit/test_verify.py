"""Recompute the two-pair idle list and the published deficit."""

from __future__ import annotations

import unittest


class DeficitTest(unittest.TestCase):
    def test_two_pairs(self) -> None:
        idle = [14, 7, 14, 0]
        self.assertEqual(sum(idle), 7 * 5 * 1)
        ports, replicas = 111, 32
        stages = 5
        width = 1 + 7 * stages
        live = 2 * 2 * ports * replicas
        local = 15 * ports * stages * replicas
        idle_mass = sum(rank for rank in idle if rank) * 2 * ports * replicas
        self.assertEqual(width * live - local - idle_mass, -ports * replicas)


if __name__ == "__main__":
    unittest.main()
