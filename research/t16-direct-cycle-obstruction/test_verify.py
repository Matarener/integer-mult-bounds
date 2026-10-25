"""Independent hinge controls and the concurrent interacting-move boundary."""

import copy
import tempfile
import unittest
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import verify as v


def synthetic():
    rows = []
    ranks = {i: rank for i, rank in enumerate((8, 12, 16, 20, 48))}
    order = [(i, 0) for i in range(4)]
    for owner in range(2):
        for time in range(4):
            for child in range(5):
                rows.append(
                    {
                        "owner_replica": owner,
                        "child": child,
                        "port": 0,
                        "time": time,
                        "width": child + 1,
                    }
                )
    spans = {(owner, child): (-1, 4) for owner in range(2) for child in range(5)}
    positions = {call: i for i, call in enumerate(order)}
    auditor = SimpleNamespace(windows=lambda geometry, calls: (spans, positions))
    ctx = auditor, {"rank": ranks}, (1, 2, 3, 4, 5), {}, {"order": order}
    return rows, ctx


def rotate(rows, indices):
    """Apply worker 1's supplied literal nominations; no search or pricing."""
    out = [dict(row) for row in rows]
    keys = ("owner_replica", "child", "port", "copy", "family")
    affected = {v.bin_key(rows[i]) for i in indices}
    for position, index in enumerate(indices):
        target = rows[indices[(position + 1) % len(indices)]]
        out[index].update({key: target[key] for key in keys})
    members = defaultdict(list)
    for index, row in enumerate(out):
        if v.bin_key(row) in affected:
            members[v.bin_key(row)].append(index)
    for indices_in_bin in members.values():
        offset = 0
        for index in sorted(indices_in_bin, key=lambda i: (out[i]["offset"], i)):
            out[index]["offset"] = offset
            offset += out[index]["width"]
    return out


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = v.predecessor(v.ROOT, v.sources(v.ROOT))
        cls.ctx = v.context(v.ROOT)
        cls.states, cls.edges = v.relaxed_graph(cls.rows, cls.ctx)
        cls.certificate = v.read(v.PACKAGE / "POTENTIALS.json")

    def test_collapse_matches_every_uncompressed_hinge(self):
        rows, ctx = synthetic()
        with patch.object(v, "CALLS", 4):
            states, edges = v.relaxed_graph(rows, ctx)
        used = Counter()
        for row in rows:
            used[v.bin_key(row)] += row["width"]
        for k in range(1, 48):
            expected = {}
            for si, (_, incoming) in enumerate(states):
                for row in rows:
                    target = states.index((row["time"], row["width"]))
                    free = ctx[1]["rank"][row["child"]] - used[v.bin_key(row)]
                    new = free + row["width"] - incoming
                    if new >= 0:
                        edge = si * len(states) + target
                        gain = max(new - k, 0) - max(free - k, 0)
                        expected[edge] = max(expected.get(edge, -100), gain)
            actual = {}
            for edge, free in edges.items():
                si, ti = divmod(edge, len(states))
                new = free + states[ti][1] - states[si][1]
                actual[edge] = max(new - k, 0) - max(free - k, 0)
            self.assertEqual(actual, expected)

    def test_missing_hinge_and_reordered_states_reject(self):
        bad = copy.deepcopy(self.certificate)
        del bad["hinges"]["47"]
        with self.assertRaisesRegex(ValueError, "all hinge indices"):
            v.check_potentials(self.states, self.edges, bad)
        bad = copy.deepcopy(self.certificate)
        bad["states"].reverse()
        with self.assertRaisesRegex(ValueError, "potential states"):
            v.check_potentials(self.states, self.edges, bad)

    def test_zero_and_noninteger_potentials_reject(self):
        bad = copy.deepcopy(self.certificate)
        bad["hinges"]["1"] = [0] * len(self.states)
        with self.assertRaisesRegex(ValueError, "hinge edge inequality"):
            v.check_potentials(self.states, self.edges, bad)
        for value in (True, 0.0, -1, 65):
            bad["hinges"]["1"][0] = value
            with self.assertRaisesRegex(ValueError, "integer potentials"):
                v.check_potentials(self.states, self.edges, bad)

    def test_changed_source_rejects_before_import(self):
        manifest = v.read(v.PACKAGE / "SOURCES.json")
        first = next(
            item["path"] for item in manifest["files"] if item["usage"] == "input"
        )
        with tempfile.TemporaryDirectory(prefix="direct-cycle-control-") as directory:
            root = Path(directory)
            path = root / first
            path.parent.mkdir(parents=True)
            path.write_bytes(b"changed scientific input")
            with self.assertRaisesRegex(ValueError, "source pin"):
                v.sources(root)

    def test_wrong_role_or_family_is_not_admitted(self):
        for key in ("width", "family"):
            bad = [dict(row) for row in self.rows]
            bad[0][key] += 1
            with self.assertRaises((ValueError, self.ctx[0].Reject)):
                v.audit(bad, self.ctx)

    def test_interacting_five_role_control_is_outside_theorem(self):
        neutral = rotate(self.rows, (34864, 43904))
        self.assertEqual(
            v.audit(neutral, self.ctx)["idle"], v.audit(self.rows, self.ctx)["idle"]
        )
        after = rotate(neutral, (37210, 30301, 31680))
        old, new = v.audit(self.rows, self.ctx), v.audit(after, self.ctx)
        delta = Counter(new["idle"])
        delta.subtract(old["idle"])
        self.assertEqual({k: n for k, n in delta.items() if n}, {1: -2, 2: 1})
        departures, arrivals = defaultdict(list), defaultdict(list)
        for before, row in zip(self.rows, after):
            if v.bin_key(before) != v.bin_key(row):
                departures[v.bin_key(before)].append(before["width"])
                arrivals[v.bin_key(row)].append(row["width"])
        self.assertEqual(sum(map(len, departures.values())), 5)
        self.assertEqual(sorted(departures[11, 14, 1]), [8, 8])
        self.assertEqual(sorted(arrivals[11, 14, 1]), [7, 9])
        self.assertEqual(
            v.digest(after),
            "96f0dc4e3b8f08cdfd385992e8675f033ed83bcd61bb14f8f6b9671b8c125fe3",
        )
        self.assertEqual((new["rank_mass"], new["deficit"]), (1041408, 5120))


if __name__ == "__main__":
    unittest.main(verbosity=2)
