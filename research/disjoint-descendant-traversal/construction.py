"""One descendant factor-order change in the historical disjoint-triple DAG.

Produced by Nick Petalas. Apache-2.0.
The root adapter is ToikY's PR981, adapting Curtis Dransfield's PR863.
The tensor expansion below adapts Douglas R. Colkitt's disjoint_tensor.py.
Their retained source files and notices are unchanged.
"""
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/disjoint-joint-ties'))
from circuit import JointTies, plan, subsets


class DescendantCircuit(JointTies):
    def __init__(self):
        super().__init__(22, 11, ((1, 1),), (1, 2, 3, 0))

    def transform(self, points, a, b, values):
        if (len(points), a, b) != (11, 2, 2):
            return super().transform(points, a, b, values)
        split = plan(11, 2, 2)[1]
        if split != 5:
            raise ValueError('the pinned descendant must split into five and six')
        left, right = points[:split], points[split:]
        terms = {target: [] for target in subsets(points, b)}
        for j in range(3):
            for i in range(3):
                if i + j > 5 or 4 - i - j > 6:
                    continue
                cost_left = plan(5, i, j)[0]
                cost_right = plan(6, 2 - i, 2 - j)[0]
                lr = comb(6, 2 - i) * cost_left + comb(5, j) * cost_right
                rl = comb(5, i) * cost_right + comb(6, 2 - j) * cost_left
                left_first = lr <= rl
                if (i, j) == (1, 1):
                    if lr != 146 or rl != 146:
                        raise ValueError('the changed channel must remain a 146/146 tie')
                    left_first = not left_first
                if left_first:
                    middle = {
                        s: self.transform(left, i, j, {
                            r: values[r | s] for r in subsets(left, i)})
                        for s in subsets(right, 2 - i)}
                    for target in subsets(left, j):
                        row = self.transform(right, 2 - i, 2 - j, {
                            s: mapped[target] for s, mapped in middle.items()})
                        for other, node in row.items():
                            terms[target | other].append(node)
                else:
                    middle = {
                        s: self.transform(right, 2 - i, 2 - j, {
                            r: values[r | s] for r in subsets(right, 2 - i)})
                        for s in subsets(left, i)}
                    for target in subsets(right, 2 - j):
                        row = self.transform(left, i, j, {
                            s: mapped[target] for s, mapped in middle.items()})
                        for other, node in row.items():
                            terms[target | other].append(node)
        return {target: self.total(nodes) for target, nodes in terms.items()}
