# Sharp commuting repair with a common small-block decomposition

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written mathematical proof with exact finite corroboration.
For three Hermitian contractions with a given common orthogonal invariant
decomposition into m two-dimensional blocks and s scalar blocks, put
d=2m+s and w=2m/d. Then their nearest commuting Hermitian contraction triple
satisfies

$$
E\le(w/3)^{1/4}\sqrt\delta,\qquad
\delta^2=\sum_{i<j}\|[A_i,A_j]\|_{2,d}^2,\qquad
\|M\|_{2,d}^2=\operatorname{Tr}(M^*M)/d.
$$

The constant is best possible for every m>=1 and s>=0, even when a competing
repair can mix the original blocks. Repeated scaled Pauli triples with
zero scalar padding have exact global minimum `E^2=2wr^2` and
`delta^2=12wr^4`. They attain the constant arbitrarily close to zero
commutator. The exponent one-half is also sharp. If m=0 the inputs commute.

This answers the common-decomposition question in merged
[PR #5245](https://github.com/CrocSwap/integer-mult-bounds/pull/5245), extending
its cited qubit theorem to a dimension-uniform structured case of David Ganz's
[atlas B099](../pure-math-atlas-400/volumes/02-geometry.md#b099),
[PR #2849](https://github.com/CrocSwap/integer-mult-bounds/pull/2849).
Neither predecessor is audited or replayed here. The new step is weighted
assembly and sharpness against arbitrary common eigenbases, including
mixing between active blocks and scalar padding. No new kappa is claimed.

## Proof and evidence

[PROOF.md](PROOF.md) cites the local contraction-preserving repair, whose
squared error and squared commutator aggregate are e_j and q_j>=3e_j^2.
For alpha=2/d, the exact gap identity is

$$
w\delta^2-3E_{\rm dec}^4
=\alpha^2\left[m\sum_j(q_j-3e_j^2)
+3\sum_{j<k}(e_j-e_k)^2\right]\ge0.
$$

Here E_dec is the optimum among repairs preserving the supplied blocks.
The unrestricted optimum E is no larger. For the sharp witnesses a unit
vector with active squared norm t has total squared Pauli expectation at
most t^2<=t. Summing over any common eigenbasis bounds its captured diagonal
mass and proves the matching unrestricted lower bound. No assumption that
a global minimizer preserves the blocks enters that proof.

The standalone standard-library verifier checks:

- 23,404 abstract weighted profiles, including scalar-only decompositions,
  unequal local errors and strict local slack, against the exact gap identity.
- 60 literal rational direct sums with shifted scalar parts, anisotropic,
  isotropic, commuting and zero blocks, and explicit commuting repairs.
- 27 sharp Pauli witnesses and 657 exact common bases, including complex
  rotations within and between qubit blocks and scalar coordinates. These
  corroborate the all-basis argument; they do not enumerate all bases.
- Eight rejection controls for an empty space, wrong block count, negative
  error, violated local bound, missing dimension weight, wrong commutator
  normalization, a nonunitary basis and a real orthogonal map that is not
  complex linear.

All counts are enumerated by verify.py. The universal quantifiers rest on
the written proof and cited local theorem. Receipts are generated to stdout
and bind all six package files by SHA256. The direct verifier authenticates
both declared source inputs and imports no predecessor executable.

## Reproduce

From the repository root with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/block-qubit-commuting-repair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/block-qubit-commuting-repair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/block-qubit-commuting-repair
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/block-qubit-commuting-repair --check-source-history
```

Another CPython 3.12 path may replace the local interpreter path. The direct
command prints `PASS_BLOCK_QUBIT_COMMUTING_REPAIR` in its JSON receipt and
writes nothing. VERIFY.json registers both warning-strict modes with
120-second limits. Committed-byte/source-history checks are publication
integrity checks, separate from the mathematical proof. Direct replay also
supports a Git-free export containing the two declared inputs.

## Scope and implementation bounds

The common invariant decomposition is an exact hypothesis. No formula for
the unrestricted optimum of an arbitrary decomposable triple, stability of
an approximate decomposition or irreducible block of size at least three
is supplied. General B099 remains open here. Physical supplier construction,
native realization, dirty restoration, caller/stock/precision/tape charges
and the complete multiplication theorem remain outside scope. The selected
frontier is unchanged. Independent human and formal proof-kernel review and
global literature priority are unclaimed. No Lean, Docker, predecessor
scientific suite or selected cold replay is required or run.

The verifier accepts no external search parameters. Profile enumeration has
at most four two-dimensional blocks, five scalar counts and eight states per
block. Literal matrices have at most sixteen real rows; the helper enforces
a twenty-row capacity. Basis enumeration uses at most eight complex
coordinates and two phases per coordinate pair. Only the current profile,
matrices and counters persist. Functions are shorter than sixty lines.
Control flow is iterative, with direct calls and explicit exceptions that
remain active under optimization. There are no subprocesses, recursion,
dynamic code generation, runtime registrations or external dependencies.
Warning-strict execution and AST inspection are the available diagnostics;
an external static analyzer is not claimed.

Power of Ten rule 3 deviation: CPython arithmetic and standard-library
collections allocate dynamically during this bounded verifier. Fixed
initialization allocation is unavailable for this implementation. The fixed
grids, twenty-row capacity, six package files of at most 100,000 bytes and
at most eight source records with input files capped at 1 MB bound live data.
Both registered modes exercise the complete domain and controls. No external
mutable resource is owned. Reassess fixed storage and input validation before
adding externally supplied dimensions or search grids.

## Open next questions

1. Can block mixing strictly improve E over E_dec for a particular common
   two-dimensional-block triple? Start with two anisotropic blocks and one
   certified mixed common eigenbasis. The present global lower bound applies
   only to the sharp witness family, so it does not answer this question.
2. Can an approximately common small-block decomposition give a useful repair
   bound with an explicit decomposition-error term? First specify errors in
   normalized Hilbert-Schmidt norm and preserve the contraction constraint.
   No exact invariant decomposition follows from a small commutator alone.

## Credit and coordination

David Ganz's #2849 supplies B099 and its normalization. Nick Petalas's #5245
supplies the cited local minimum and common-block open question. The Pauli
representation, direct-sum trace rule, Cauchy-Schwarz and simultaneous
diagonalization are classical. Existing source credit remains unchanged.

The formal-interface-lemma card is explicitly changed to this algebraic side
result. The picker initially suggested verifier engineering; the donor's
original-mathematics assignment and the explicit open question determine this
scope. This does not discharge a selected supplier assumption. Canonical main
and source pins are in SOURCES.json; coverage and preserved checkout state
are in TASK.json. The selected baseline passed after sparse inputs were
materialized, as a metadata-only orientation check.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19213498).
