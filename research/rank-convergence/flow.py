#!/usr/bin/env python3
"""Arbitrary-height wrapper of zxv's PR4436 integer Pascal flow.

The inherited chronological literal evaluator is unchanged. Jacob Alan
Sussman's integer compiler supplies the underlying construction. New source
classification and exact invoice checks: OpenAI Codex assistance, Apache-2.0.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from types import ModuleType

SOURCE = Path(__file__).resolve().parent.parent / 'direct-mixed-flow/flow.py'
SOURCE_SHA256 = '460f0b0262d7b6880973f46240b3fff1e9f04601fa1d658dda18688b1e26575a'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_source(path=SOURCE):
    """Authenticate bytes before executing the frozen predecessor source."""
    path = Path(path)
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == SOURCE_SHA256, 'Changed predecessor flow bytes')
    module = ModuleType('_rank_convergence_predecessor_flow')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module.Flow


BaseFlow = load_source()


def positive(counter):
    return Counter({k: v for k, v in counter.items() if v})


def verify_receipt(targets, paid, n, receipt):
    """Check the formal rank invoice, without evaluating fractional powers."""
    sources, exits = receipt['sources'], receipt['exits']
    roots, inner = receipt['root_sources'], receipt['nonroot_sources']
    boundary, leaves = receipt['boundary_exits'], receipt['leaf_exits']
    columns = receipt['unit_columns']
    m, rmax = max(targets), max(paid)
    for inventory in (sources, exits, roots, inner, boundary, leaves, columns):
        need(all(isinstance(k, int) and k > 0 and isinstance(v, int) and v > 0
                 for k, v in inventory.items()), 'Positive integer rank inventory')
    need(bool(sources) and bool(columns), 'Empty arbitrary-height flow')
    need(sources == roots + inner, 'Root/nonroot source partition')
    need(exits == boundary + leaves, 'Boundary/leaf exit partition')
    need(all(s <= n and 0 <= n-s < n for s in sources), 'Strict complement descent')
    need(all(m*s > n for s in inner), 'Nonroot source lower bound')
    need(all(e < n and m*e <= rmax*n for e in exits), 'Strict paid-exit descent')
    need(all(m*z <= n for z in columns), 'Native positive integer columns fit cap')
    invoice = Counter(sources)
    invoice.subtract(exits)
    for z, count in columns.items():
        for k, repetitions in targets.items():
            invoice[k*z] -= count*repetitions
        for r, repetitions in paid.items():
            invoice[r*z] += count*repetitions
    need(not positive(invoice), 'Formal rank-invoice cancellation')
    need(sum(columns.values()) == receipt['units'], 'Unit column histogram count')
    need(sum(z*w for z, w in columns.items()) == receipt['column_mass'],
         'Unit column histogram rank mass')
    return True


class Flow(BaseFlow):
    def __init__(self, targets, paid, n, G):
        need(isinstance(G, int) and not isinstance(G, bool) and G >= 0,
             'Nonnegative integer explicit height')
        need(targets and paid and all(isinstance(k, int) and k >= 1
             for inventory in (targets, paid) for k in inventory),
             'Positive integer target and paid ranks')
        # Base initialization uses no cached point/unit/demand method. A base
        # greater than kmin disables only its obsolete ALL-source lower bound;
        # our receipt checks the correct nonroot bound below. No cache is
        # populated at one height and reused after assigning another height.
        super().__init__(targets, paid, n, height_base=max(targets)+1)
        self.G = G

    def merged(self):
        # An arbitrary-height forest may be empty for a generic profile.
        # Classify it first so rejection has a specific, intentional reason.
        roots = Counter()
        for b, count in self.demand(0, 1).items():
            roots[self.column(b)] += count
        inner, boundary, leaves, columns = Counter(), Counter(), Counter(), Counter()
        paths = Counter({1: 1})
        for depth in range(self.G+1):
            following = Counter()
            for rho, multiplicity in paths.items():
                batch = self.units(depth, rho)
                for a, count in batch.items():
                    columns[rho*self.column(a)] += multiplicity*count
                for rank, repetitions in self.P.items():
                    new_rho, copies = rho*rank, multiplicity*repetitions
                    if depth == self.G:
                        for a, count in batch.items():
                            leaves[new_rho*self.column(a)] += copies*count
                        continue
                    child = self.demand(depth+1, new_rho)
                    # Empty parent classes do not suppress later fresh-source
                    # components. Prefix multipliers are nondecreasing.
                    if new_rho <= self.cap:
                        following[new_rho] += copies
                    for b in set(batch) | set(child):
                        supply, demand = batch.get(b, 0), child.get(b, 0)
                        e = new_rho*self.column(b)
                        if supply > demand:
                            boundary[e] += copies*(supply-demand)
                        elif demand > supply:
                            need(supply == 0, 'Absent parent supplies fresh source')
                            inner[e] += copies*(demand-supply)
            paths = following
        need(bool(columns) and bool(roots + inner), 'Empty arbitrary-height flow')
        receipt = super().merged()
        need(receipt['sources'] == roots + inner, 'Predecessor source agreement')
        need(receipt['exits'] == boundary + leaves, 'Predecessor exit agreement')
        need(receipt['boundary_exits'] == boundary, 'Predecessor boundary agreement')
        receipt.update(root_sources=roots, nonroot_sources=inner,
                       leaf_exits=leaves, unit_columns=columns)
        verify_receipt(self.T, self.P, self.n, receipt)
        return receipt


def adaptive_flow(targets, paid, n, witness):
    """Construct G=(a+b)*floor(log_M floor(n/m)) with integer arithmetic."""
    M, a, b = (witness[key] for key in ('height_base', 'a', 'b'))
    need(type(M) is int and M >= 2 and all(type(x) is int and x >= 1 for x in (a, b)),
         'Integer adaptive geometry')
    cap, ell = n//max(targets), 0
    while cap >= M:
        cap //= M
        ell += 1
    result = Flow(targets, paid, n, (a+b)*ell)
    result.adaptive_geometry = {'height_base': M, 'height_multiplier': a+b, 'ell': ell}
    return result
