"""Reconstruction, chronology, paid deltas, and complete invoice boundaries."""

import copy
import unittest
import sys
import tempfile
from pathlib import Path

import verify as v


class ReconstructionChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.export = v.check_sources(v.ROOT)
        cls.old, cls.old_plan = v.predecessor(v.ROOT, cls.export)
        cls.ctx = (*v.context(v.ROOT)[:4], cls.old_plan)
        cls.steps = v.read(v.PACKAGE / "REPAIRS.json")["steps"]
        cls.new, cls.before, cls.after, cls.plan = v.construct(cls.old, cls.ctx)

    def test_exact_payload_and_paid_delta(self):
        self.assertEqual(v.digest(self.new), v.FINAL_SHA256)
        delta = v.Counter(self.after["idle"])
        delta.subtract(self.before["idle"])
        self.assertEqual({k: n for k, n in delta.items() if n}, {1: 3, 3: -25, 6: 8, 8: 3})
        self.assertEqual(self.after["rank_mass"], 1041408)
        self.assertEqual(self.after["deficit"], 5120)
        self.assertEqual(self.new, sorted(self.new, key=lambda row: (row["time"], row["helper"])))
        self.assertEqual(
            {(r["stage"], r["replica"], r["helper"], r["width"]) for r in self.old},
            {(r["stage"], r["replica"], r["helper"], r["width"]) for r in self.new},
        )

    def test_all_owner_mutation_controls(self):
        auditor, geometry, widths, local, _ = self.ctx
        controls = auditor.controls(geometry, widths, local, self.new, self.plan,
                                    v.Counter(self.after["idle"]), 16)
        self.assertEqual(len(controls), 11)

    def test_action_preimage_and_identity_controls(self):
        for field, value in (("width", True), ("from", [0, 0, 0]),
                             ("identity", {"stage": True, "replica": 0, "helper": 177})):
            steps = copy.deepcopy(self.steps)
            steps[0]["actions"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                v.construct(self.old, self.ctx, steps)
        steps = copy.deepcopy(self.steps)
        steps[0]["actions"].append(steps[0]["actions"][0])
        with self.assertRaisesRegex(ValueError, "repeated logical role"):
            v.construct(self.old, self.ctx, steps)

    def test_stage_source_and_chronology_bindings(self):
        for field, value in (("source_canonical_sha256", "0" * 64), ("paired_block", 0)):
            steps = copy.deepcopy(self.steps)
            steps[0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                v.construct(self.old, self.ctx, steps)

    def test_call_order_controls(self):
        original = copy.deepcopy(self.plan["order"])
        mutants = [original[:-1], [original[0]] + original[1:-1] + [original[0]]]
        unordered = copy.deepcopy(original)
        unordered[0], unordered[1] = unordered[1], unordered[0]
        mutants.append(unordered)
        noncausal = copy.deepcopy(original)
        indices = [i for i, call in enumerate(original) if call[1] == 0][:2]
        for bank in (0, 1):
            a, b = (i + bank for i in indices)
            noncausal[a], noncausal[b] = noncausal[b], noncausal[a]
        mutants.append(noncausal)
        boolean = copy.deepcopy(original)
        boolean[0][0] = bool(boolean[0][0])
        mutants.append(boolean)
        for order in mutants:
            with self.subTest(order=order[:3]), self.assertRaises(ValueError):
                v.validate_order(order)

    def test_coordinate_and_index_controls(self):
        for moves in ({"-1": [0, 0, 0]}, {"01": [0, 0, 0]},
                      {"0": [True, 0, 0]}, {"0": [16, 0, 0]},
                      {"0": [0, 0, 112]}):
            with self.subTest(moves=moves), self.assertRaises(ValueError):
                v.apply_moves(self.old, moves, self.ctx[1], False)

    def test_retained_predecessor_binding(self):
        export = dict(self.export, predecessor_canonical_sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "retained PR3388 owner payload"):
            v.predecessor(v.ROOT, export)

    def test_invoice_allows_only_complete_record_permutation(self):
        old = {"charge": 1, "selected_calls": [
            {"stage": s, "replica": r, "charge": 2, "future": [3, 4]}
            for s in range(9) for r in range(16)]}
        new = copy.deepcopy(old)
        new["selected_calls"].reverse()
        v.same_invoice(old, new)
        mutants = []
        for value in (True, 1.0, 2):
            mutant = copy.deepcopy(new)
            mutant["charge"] = value
            mutants.append(mutant)
        for modification in ("missing", "duplicate", "charge", "array_order", "boolean_call"):
            mutant = copy.deepcopy(new)
            if modification == "missing":
                mutant["selected_calls"].pop()
            elif modification == "duplicate":
                mutant["selected_calls"][0] = mutant["selected_calls"][1]
            elif modification == "charge":
                mutant["selected_calls"][0]["charge"] += 1
            elif modification == "array_order":
                mutant["selected_calls"][0]["future"].reverse()
            else:
                mutant["selected_calls"][0]["stage"] = True
            mutants.append(mutant)
        for mutant in mutants:
            with self.assertRaises(ValueError):
                v.same_invoice(old, mutant)

    def test_actual_extended_lift_positive_and_mutations(self):
        with tempfile.TemporaryDirectory(prefix="lift-controls-") as directory:
            source = v.replay.extract_source(v.ROOT, Path(directory))
            previous_path = sys.path[:]
            previous_builder = sys.modules.pop("build_parent", None)
            try:
                sys.path.insert(0, str(source / "t16"))
                lift = v.load("test_reordered_lift", source / "t16/lift16.py")
                plan8 = lift.read(source / "data/T8/PLAN.json")
                owners8 = lift.read(source / "data/T8/OWNERS.json.gz")
                parent = lift.lift_parent(v.read(v.ROOT / self.ctx[0].TEMPLATE))
                order = self.plan["order"]

                def check(candidate_order, rows):
                    return lift.lift_plan(plan8, parent, owners8, rows,
                                          "plan8", "owners8", "owners16", candidate_order)

                result, schedule, _, _ = check(order, self.new)
                at = {tuple(call): time for time, call in enumerate(order)}
                for field in ("provider_calls", "per_call_widths"):
                    self.assertTrue(all(call.get("time", at[call["stage"], call["replica"]])
                                        == at[call["stage"], call["replica"]]
                                        for call in result[field]))
                self.assertEqual(result["replica_lift"]["schedule_content_sha256"],
                                 lift.content_sha(schedule))
                mutations = []
                duplicate = copy.deepcopy(order)
                duplicate[0] = duplicate[2]
                mutations.append((duplicate, self.new, "complete requested order"))
                mutations.append((order[:-1], self.new, "complete requested order"))
                reversed_replica = copy.deepcopy(order)
                positions = [i for i in range(0, 144, 2) if order[i][1] == 0]
                a, b = positions[:2]
                reversed_replica[a:a+2], reversed_replica[b:b+2] = reversed_replica[b:b+2], reversed_replica[a:a+2]
                mutations.append((reversed_replica, self.new, "replica causal order"))
                unpaired = copy.deepcopy(order)
                a, b = next((i, j) for i in range(0, 144, 2) for j in range(i+2, 144, 2)
                            if order[i][0] == order[j][0])
                unpaired[a+1], unpaired[b+1] = unpaired[b+1], unpaired[a+1]
                mutations.append((unpaired, self.new, "two-bank paired order"))
                wrong_time = copy.deepcopy(self.new)
                wrong_time[0]["time"] = (wrong_time[0]["time"] + 1) % 144
                mutations.append((order, wrong_time, "role call time"))
                outside = copy.deepcopy(self.new)
                row = outside[0]
                valid = result["windows"][f"{row['owner_replica']},{row['child']}"][1]
                time = next(t for t in range(144) if t not in valid)
                row.update(time=time, stage=order[time][0], replica=order[time][1])
                mutations.append((order, outside, "owner outside actual window"))
                for candidate_order, rows, message in mutations:
                    with self.subTest(message=message), self.assertRaisesRegex(Exception, message):
                        check(candidate_order, rows)
            finally:
                sys.path[:] = previous_path
                sys.modules.pop("build_parent", None)
                if previous_builder is not None:
                    sys.modules["build_parent"] = previous_builder


if __name__ == "__main__":
    unittest.main()
