# Related work and comparison boundary

Restored target bases, signed forests and two-sided bases are prior methods.
The identity `T^-1(Ty + T C H^-1 Hh) = y+Ch` is not new.

- Oscar Fennell's rooted target forests, Sricharan Vagvala's JP8 target
  factorization, and the target-pair work of Scott Woolsey Biggart, Sagar
  Thakrar, Dugongue, @dd-hemant and ToikY establish the relevant lineage.
- PR816 gives signed CK target forests and their exact class floor.
- David Awad's PR807 and Ross Richardson's
  [PR917](https://github.com/CrocSwap/integer-mult-bounds/pull/917)
  apply disjoint helper bases around target factorizations. PR917 is pinned
  at `085c32a25e2a09b029fa816195b97fa93d6f0788`.
- PR967 allows depth-one helper stars.
  [PR1080](https://github.com/CrocSwap/integer-mult-bounds/pull/1080),
  pinned at `803e080e181229a3af2196b7a13615c9d81ae10d`, supplies a broader
  two-sided signed bi-forest alphabet with arbitrary depth.

Those numerical savings concern other matrices. This package compares all
four displayed costs on the exact PR3605 compensation matrix. In particular,
PR1080 has 216 active helpers and a quarter-grid matrix; this source has 207
active helpers and nonzero eighth-grid coefficients. Its frozen literal
register recipe also refers to removed or differently wrapped helpers in the
staged word. A paid port or role remapping would be a separate construction.
The restricted 88-pair result does not exclude bi-forests or any other wider
alphabet.

The historical unpublished C01 panel is supplied as an exact comparator,
not a new claim for basis-factorization priority. Its finite benefit is
superseded by the new circuit. The earlier source-factory failure screens
answer different questions and are not expanded here.

Live overlap checks on 2026-10-20 searched paginated open and closed PR titles
and bodies, Discussions, and 5,234 local records. The snapshot reached
312 open PRs, 3,540 closed PRs and 2,707 Discussions, with individual fetches
between 12:45 and 12:47 UTC. These searches identify leads; they do not prove
novelty or inspect every code diff.
