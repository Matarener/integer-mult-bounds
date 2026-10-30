"""Static inverse tables for the retained complete fanout command.

Inverse-table changes produced by Nick Petalas. Apache-2.0.
The theorem, interpreter, search and enumerated workload remain lee-phys's.
"""

from dataclasses import dataclass, field
import hashlib
from pathlib import Path


SOURCE_SHA256 = 'f2f4b7f8cfb900488af2ac86202fa2a177279c97302cc6d84a64135b157e2b3c'
source_path = Path(__file__).with_name('retained_source.py')
if hashlib.sha256(source_path.read_bytes()).hexdigest() != SOURCE_SHA256:
    raise ValueError('retained executable source bytes changed')

import retained_source as source  # Authenticate before importing executable bytes.


@dataclass(frozen=True)
class InverseTableRing(source.Ring):
    """Keep one immutable answer per element, including the nonunit sentinel."""

    _neg: tuple = field(init=False, repr=False, compare=False)
    _inv: tuple = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        if not 1 <= self.n <= 81:
            raise ValueError('supported ring order is 1 through 81')
        if len(self.add) != self.n or len(self.mul) != self.n:
            raise ValueError('one addition and multiplication row per element')
        if any(len(row) != self.n for row in (*self.add, *self.mul)):
            raise ValueError('square operation tables required')
        negatives = tuple(row.index(0) for row in self.add)
        units = tuple(row.index(self.one) if self.one in row else None
                      for row in self.mul)
        object.__setattr__(self, '_neg', negatives)
        object.__setattr__(self, '_inv', units)

    def neg(self, x):
        return self._neg[x]

    def inv(self, x):
        value = self._inv[x]
        if value is None:
            return self.mul[x].index(self.one)
        return value


def main():
    # One explicit factory boundary; no workload, check or search is replaced.
    source.Ring = InverseTableRing
    source.main()


if __name__ == '__main__':
    main()
