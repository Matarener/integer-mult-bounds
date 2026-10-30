# A literal unit-modulus bypass for the G20 quarter-carry leaf

**Scoped physical construction and written proof; no new kappa.** A fixed
seven-instruction prefix lowers the complete runtime quarter-carry leaf's
uniform bounds from **468V to 1115V/3 transitions** and from **49V to 24V
visited cells**, where V=PQS. The new bounds are sufficient upper bounds,
with no claim that they are optimal.

For Q=1 the required rotation is the identity. The prefix physically reads
the next symbol of the canonical Q descriptor, restores its head and halts
in exactly four transitions. It visits exactly 20 cells under the retained
convention that all nineteen initial head positions count. For every odd
Q>=3 it restores the head and enters the original table after exactly four
additional transitions. Every retained instruction is unchanged apart from
the relocation of its finite program-counter destinations.

The [proof](PROOF.md) combines this construction with Ali Romman's cited
nonunit bounds in [PR #5849](https://github.com/CrocSwap/integer-mult-bounds/pull/5849).
The predecessor's arithmetic, general carry implementation and all-route
envelope are dependencies, not results re-audited here. The delivered step
is the physical prefix and its improved uniform envelope. Earlier high-route
callers already skip high operations at Q=1, as documented by Sagar Thakrar
in [PR #3265](https://github.com/CrocSwap/integer-mult-bounds/pull/3265).
No priority for that general observation is claimed.

The same valid interface is retained: positive canonical P,Q,S with Q odd,
the complete original-owner Boolean payload, a valid five-bit packet for
-16<=k<=12, the declared blank private tapes, and arbitrary spectators.
Both directions implement x -> x +/- k*4^-1 mod Q, preserve all descriptors
and spectators, restore every head, and return private storage blank.

## Evidence and reproduction

From the repository root, run these standard-library CPython 3.12 commands:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/unit-modulus-carry-bypass/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/unit-modulus-carry-bypass/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/unit-modulus-carry-bypass
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/unit-modulus-carry-bypass --check-source-history
```

The direct verifier prints a generated JSON receipt with status
`PASS_UNIT_MODULUS_CARRY_BYPASS`, hashes of its package and six declared
inputs, and these enumerated checks:

- 1,972 unit-modulus executions cover both directions, every valid packet,
  and every Boolean payload for shapes (1,1,1), (1,1,4) and (2,1,2).
  All cells and heads agree with their entry state; the exact bill is 4
  transitions and 20 visited cells. A separate interpreter covers 58 of them.
- Eight descriptor-only prefix fixtures, including 513-bit Q, check the
  exact four-transition return or four-transition fallback overhead with
  occupied spectators, in both interpreters.
- Every fallback row in both 31,873-instruction source tables is compared
  after independently undoing relocation.
- Six complete nonunit compositions in both interpreters cover Q=3,5,125
  and both directions, with a direct coordinate-gather oracle, full head
  return and private erasure. The source's port9 fixture k=-3,Q=125 uses
  residue 93. The new composition takes 16,694 transitions and visits 625
  cells in either direction.
- Six rejection controls cover each omitted descriptor-head return, an
  altered fallback instruction, an understated transition bill, a wrong
  tape count and an invalid entry state.

The verifier writes no files. The source table, both interpreters and cited
source statements are pinned by Git blob and SHA-256 in [SOURCES.json](SOURCES.json).
The registered normal and optimized commands are in [VERIFY.json](VERIFY.json).
The finite checks corroborate the proof; they do not establish its unbounded
claims by extrapolation.

## Limits

Nonunit correctness and bounds are inherited from the exact retained #5849
table and proof. This package does not repeat that predecessor's broad replay.
The Q=1 branch assumes valid descriptors and a valid packet; it does not
validate the unused payload, packet or private tapes. Invalid-input rejection
behavior is outside the successful-execution contract.

This is a component improvement. The complete G20 caller has not been
installed or repriced with it. Low-cache packet formation and selection,
whole-T staging, low-type commit, physical ROW presentation, ancestor
stock/P3, and the full caller invoice remain open. All five framework
assumptions retain their status. There is no selected-frontier change,
new recursive saving, or complete multiplication theorem.

## Open next questions

Can a real low-cache row be joined to the supplied packet and this wrapped
leaf in one paid physical execution? Begin with the retained port9 witness
and include low-row selection, the homogeneous route, packet formation,
cache erasure and low-type commit. Whole-T staging and the actual ROW caller
map are the blockers. [TASK.json](TASK.json) records this question structurally.

## Sources and credit

Base canonical main is `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority
revision 8. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19226097)
states this physical-leaf scope.

This package was produced by Nick Petalas. Apache-2.0. Credit Ali Romman for
#5849's complete carry leaf, physical bounds, retained interpreters and source
envelope; David Arias for the literal machine and counter/stream macros;
JoyboyBrian for quarter arithmetic and affine owner reuse; Sagar Thakrar for
the earlier high-route Q=1 branch; Charles Bethin, Jose Manuel, Tekalign,
ToikY, and the retained tape/ROW/G20 contributors for the predecessor chain.
All retained source files and their original credit lines are unchanged.
