"""Replay the six-stage axis walk independently."""

from __future__ import annotations

import unittest


class WalkTest(unittest.TestCase):
    def test_axis_walk(self) -> None:
        frames = [1, 0]
        active = list(range(8))
        exterior = 0
        high, low = 0, 1
        next_axis = 8
        profile: dict[int, int] = {}
        normals = []

        def move(role: int, new: int) -> None:
            difference = new ^ frames[role]
            if difference:
                rank = difference.bit_count()
                profile[rank] = profile.get(rank, 0) + 1
                frames[role] = new

        for stage in range(6):
            source, normal_index = stage % 2, 1 - stage % 2
            full = exterior
            for axis in active:
                full |= 1 << axis
            normal = active[normal_index]
            complement = full ^ (1 << normal)
            move(high, complement)
            move(low, complement)
            move(low, full)
            high, low = low, high
            normals.append(normal)
            if stage != 5:
                exterior = complement
                active = [normal if index == normal_index else -1 for index in range(8)]
                for index in range(8):
                    if active[index] == -1:
                        active[index] = next_axis
                        next_axis += 1
        self.assertEqual(normals, [1, 8, 15, 22, 29, 36])
        self.assertEqual(next_axis, 43)
        self.assertEqual(sum(rank * count for rank, count in profile.items()), 84)
        self.assertEqual(2 * next_axis - 84, 2)


if __name__ == "__main__":
    unittest.main()
