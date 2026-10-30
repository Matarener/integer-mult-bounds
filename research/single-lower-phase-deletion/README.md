# One lower-only phase cannot change an upper-shear endpoint

This contribution was produced by Nick Petalas. Apache-2.0.

A contiguous phase of lower-left updates and binary register mixing can be
deleted from a rational upper-shear superposition word whenever its required
data entries are supported on upper-shear labels. The replacement preserves
those entries and every paid call, including its rational rank. Width,
register count, rational denominators and the rank of each lower update are
unrestricted in the written theorem.

This is a **scoped proof with exact finite corroboration**, not a search
failure, new finite supplier or complete multiplication theorem. No new
kappa is claimed.

## The new reduction

For upper shears u_A and lower shears v_K, the map

\[
 [u_Av_Ku_B]\longmapsto[u_{A+B}]
\]

is well-defined on distinct formal labels. This remains true for singular
K. Its linear extension is an upper-shear bimodule retraction. Therefore,
if X=L F B with L,B over the upper-shear group algebra and F over the
lower-shear group algebra, then

\[
 P(X)=L\,\epsilon(F)\,B.
\]

At every required entry already supported on upper labels, P is identity.
The scalar augmentation epsilon(F) is exactly the phase's binary mixing
after all lower updates are deleted. [PROOF.md](PROOF.md) gives the full
argument over any address field and any commutative coefficient ring.

For ordinary circuits with all moves multiplying on one side, a contiguous
lower-only phase has this factorization. In a model with both left and
right actions, the final factorization must be supplied separately.
Contiguity in chronological order alone is insufficient for this argument.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/single-lower-phase-deletion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/single-lower-phase-deletion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/single-lower-phase-deletion
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/single-lower-phase-deletion --check-source-history
```

Any CPython 3.12 executable may replace the displayed path. Each direct run
prints `PASS_SINGLE_LOWER_PHASE_DELETION` in a generated JSON receipt bound
to the package files by SHA256. Default replay writes no files. The same
standalone check works without Git or predecessor packages.

The verifier checks:

- All 4,256 triples in four complete finite-field domains: width one over
  F2, F3 and F5, and width two over F2. It compares all 1,420 repeated labels
  with their previously computed A+B. The respective distinct-label counts
  are 6, 21, 105 and 2,704.
- 144 literal rational triples at widths one through three, including 92
  singular K matrices, and 144 outer bimodule identities. An independent
  recovery formula uses a checked inner inverse H with K H K=K, rather
  than the generating A and B.
- 24 complete binary group-algebra factorizations, containing 112 entries.
  Projection agrees with phase deletion throughout; all 42 upper-supported
  entries agree directly.
- Six hypothesis or mutation controls and three invalid-dimension
  rejections. These distinguish a singular-K collision, an incorrect raw
  upper-right-block rule, a non-upper endpoint, internal Levi maps,
  separated lower phases and unconstrained auxiliary output. Checks remain
  enabled under optimized Python.

Finite checks corroborate the written proof. No finite enumeration is used
to infer its all-width conclusion.

## Scope and predecessor credit

The source question is the first open question of Sagar Thakrar's
[PR2613](https://github.com/CrocSwap/integer-mult-bounds/pull/2613), which
proposes one inserted lower-left update in a rational shear superposition
word. That package supplies the model and the distinct 2-integral
obstruction. eumemic's PR288 supplies the original register model and
upper-only width-two obstruction; Swapnil Jain's framework supplies the
credited related rank functional and free class. Their scientific results
are cited as premises, not replayed or claimed as new here.

ywz65's [PR2671](https://github.com/CrocSwap/integer-mult-bounds/pull/2671)
and Nick Petalas's
[PR6027](https://github.com/CrocSwap/integer-mult-bounds/pull/6027) concern
common invariant lattice filters. This theorem uses no integrality or
lattice-feasibility assumption and does not extend those filters.
dcharb78's [PR3183](https://github.com/CrocSwap/integer-mult-bounds/pull/3183)
reports a separate finite width-two block-Borel screen. This contribution
neither audits that screen nor claims its call-count result. Exact main
READMEs and the source proof are pinned as provenance in
[SOURCES.json](SOURCES.json); no predecessor executable is imported.

The active card is `bit-helper-contract`, changed from G20 helper
construction to the explicit full-Borel handoff. This is a local interface
obstruction relevant to a proposed way around paid-call floors. Its new
step is the single-phase deletion theorem. General literature priority
for elementary block multiplication or bimodule methods is unclaimed.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19246973)
records the question and source baseline.

Required endpoints must be supported on upper labels. Arbitrary independent
internal Levi maps, multiple alternating lower phases and an arbitrary
bidirectional chronological phase are outside the theorem. The supplied
Levi and three-phase identities reject broader naive deletion rules.
No complete full-Borel impossibility result is claimed. The reduction
preserves an existing paid profile; it does not produce an improved one.

Physical lower-update legality, native operators, boundary conversions,
dirty restoration beyond the declared data block, stock, precision/tape,
uniform compiler and the full signed invoice remain separate obligations.
No selected-word replay, native replay, Lean, Docker or complete multiplier
ran. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Can separated lower-only phases provide a favorable completed rational
  superposition word? Start with a width-two word with two such phases,
  its full formal data block and complete paid/target invoice. No such
  saving word or physical caller is supplied here; the projection cannot
  be multiplied across arbitrary phases.
- What deletion criterion survives internal register-dependent Levi maps?
  Specify the enlarged middle alphabet and test equality of double-coset
  labels against the proposed deleted labels. The simple Levi identity
  already rejects naive deletion, so another search needs a changed
  reduction and full boundary accounting.

Structured first steps and blockers are in [TASK.json](TASK.json).

## Implementation bounds

The executable is a bounded verifier, not a public matrix solver. Its
largest address matrix is 6 by 6, scalar register count is at most three,
and group-algebra support is capped at 256 labels per entry. Finite-field
enumeration has at most 16^3 triples per domain. Functions remain below
60 physical lines, control flow is nonrecursive, and invariant checks use
explicit exceptions that survive `-O`.

Power-of-ten rule 3 has a managed-runtime deviation in `verify.py`.
CPython allocates exact Fraction values, tuples and sets during checking.
Fixed dimensions, fixture counts, rational input alphabets and support
caps bound the computation and live data. No external matrix or circuit
is read. Each declared replay has a 60-second timeout. A public solver
would require separate bit-size and memory budgets. Warning-strict normal
and optimized runs provide the available standard-library diagnostics;
there is no project Python type-checker configuration for this package.
