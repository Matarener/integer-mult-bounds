# Rank-optimal folding and sharp phase repair for composite cyclic chirps

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

Claim type: scoped algebraic construction and sharp lower bound, with exact
finite corroboration. For every positive odd axis n, let

```
K_b[j,k] = exp(2 pi i (a(j-k)^2+b(j-k))/n),
g = gcd(a,n),   m = n/g.

K_b = phased replication[n <- m]
      * nonsingular reduced chirp[m <- m]
      * phased fold[m <- n].
```

The intermediate dimension m is optimal. A sum of chirps with this same
quadratic coefficient needs at least g phase twists to become invertible.
Exactly g attain the bound, and the explicit sum S of twists b=0,...,g-1
has S* S=n g I. Its condition number is one and its inverse is S*/(n g).
For n=9,a=3 this reduces a nine-coordinate operator to three coordinates
and requires three twists to repair invertibility. For n=45,a=15 the
reduced dimension is again three, while the minimum repair count is fifteen.

[PROOF.md](PROOF.md) proves the universal statement and supplies every
matrix in the factorization. The lower bound permits arbitrary scalar
weights and arbitrary linear phase parameters within this fixed quadratic
family. Repeated phase residues cannot compensate for a missing residue.
The result includes the nonsingular unit-coefficient case on composite axes.

## Connection and credit

David Ganz / Dugongue's [PR5564](https://github.com/CrocSwap/integer-mult-bounds/pull/5564)
constructs prime-free coprime axes and leaves a complete composite-axis
numerical caller open. This is one algebraic side result for that question.
It supplies a rank-optimal implementation of a possible phase-only cyclic
convolution, together with the exact cost of repairing its rank in its own
term alphabet. It does not identify this operator with an existing real
Gaussian resampler. The actual caller and complete physical bill remain open.
No predecessor scientific verifier is imported or replayed as the deliverable.

Finite-character orthogonality and quadratic Gauss-sum algebra are classical;
see [NIST DLMF](https://dlmf.nist.gov/20.11.i). Global novelty of those facts is
unclaimed. The new repository contribution is the explicit folding/replication
interface, sharp constrained phase-repair construction and bounded exact
implementation. Credit PR5564's retained ToikY, Jose Manuel, Tekalign, Cinna
Davis, Chafik Boukhalfa, Josie Elliston and Harvey–van der Hoeven lineage.
Its source credit and files are unchanged.

## Reproduction and evidence

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/composite-chirp-phase-repair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/composite-chirp-phase-repair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/composite-chirp-phase-repair
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/composite-chirp-phase-repair --check-source-history
```

Another CPython 3.12 executable can replace the absolute local path.
The direct checker prints `PASS_COMPOSITE_CHIRP_PHASE_REPAIR` in a generated
JSON receipt bound to all eight package files. It writes no files. No receipt
is handwritten. The registered hook runs normal and optimized modes.

`chirp.py` implements the factorization. `oracle.py` imports no part of that
implementation: it builds literal dense matrices, performs finite-field
elimination and constructs integer cyclotomic polynomials by exact division.
The verifier checks all odd n through 31 and every a,b modulo n for the
factorization, with complete basis inputs through n=9. Literal modular ranks,
complex cyclotomic Gram entries and the complete attaining inverse use the
separately declared smaller domains. Every subset of phase residues is tested
when n<=15 and g<=9. The generated receipt enumerates 5,456 factorization
cases, 3,344,528 phase entries, 1,225 basis vectors, 127 modular ranks,
16,255 cyclotomic Gram entries, 890 phase subsets and 8,128 inverse entries
across 64 repair families. No floating-point rank or complex tolerance is used.

Controls exercise invalid dimensions, coefficient types and bounds, malformed
ring evaluations, omitted twists, repeated phase residues, a nonprimitive root
that hides rank, and the failure of the odd-axis rank formula at n=4. Acceptance
checks use exceptions and remain enabled with optimization. All seventeen
listed domain/semantic controls pass.

## Scope and implementation bounds

This is a linear-algebra theorem and a reference implementation, not a finite
certificate for the selected supplier or a complete multiplication theorem.
No new kappa or selected-assumption discharge is claimed. Phase manufacture,
rounded normalization, input encoding, native calls, movement, owned workspace
restoration, compiler stock, physical time/storage and the whole recovery
contract remain unpriced and unrun. No selected cold replay, Lean or Docker
run is part of this contribution. Matrix conditioning alone supplies no rounded
implementation theorem. An odd composite modulus alone does not cause a defect;
the decisive quantity for this operator is gcd(a,n).

The theorem has no size cap. The executable accepts odd n<=255, coefficients
of at most 256 bits, modular rings of size at most 1,000,000 and n input
coordinates. It evaluates in the supplied ring and needs only a root whose
order divides n. Complex rank checks additionally use independently certified
prime fields with primitive roots; a nonprimitive evaluation is explicitly
not accepted as evidence of complex rank. Verification axes are at most 31,
the independent field-search axis cap is 63, and every search is bounded.

Power of Ten review: no recursion, external process, dynamic code generation,
mutable global state or acceptance assertions occur in the new computation.
All functions fit within sixty lines. Domain limits bound every loop; field
search has 1,023 prime candidates and fewer than 64,514 root candidates per
candidate. Every verifier matrix has at most 31 squared entries. The repair
census retains two families of at most fifteen phase matrices plus their sums.
Every reference-API array has at most 255 entries, including the folded and
middle arrays, phase table and input/output vectors.
Python allocation is a rule-3 deviation forced by its managed integer/list
runtime. These enforced finite domains and bounded live arrays are the
compensating controls; a fixed-allocation native implementation remains future
work. No allocation-free runtime or bit-cost theorem is asserted. Warning-strict
normal/optimized execution and AST/compilation inspection supply diagnostics.
No external linter or type checker was available in the supplied environment.

## Provenance and overlap

Canonical base `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.
[SOURCES.json](SOURCES.json) pins the task catalogue, selected record and the
two PR5564 source notes as historical provenance. Runtime inputs are package
local. [TASK.json](TASK.json) explicitly changes the card from selected-caller
assumption discharge to this algebraic side result. The current selected
source-binding orientation passed; it is not scientific evidence for this result.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19227603)
followed live open PRs, recent account publications, handoff/active discussions,
main README searches and merged searches for composite chirps, Gauss sums,
rank and singular kernels. The cached card search covered 377 open PRs and
5,601 Discussion records with complete remote pagination at 21:06 UTC. Its
sparse local coverage was 254 of 8,136 HEAD notes, supplemented by distinctive
all-main README searches. Absence of a
search match is not a novelty certificate and excludes unpublished work and
unread arbitrary diffs. Nearby #5946 concerns the allowed second-input space
of unequal Fourier read layouts, not this quadratic convolution or repair.
Its result and the Gaussian adapter packages are not reverified here.

## Open next questions

Can an actual composite-axis consumer use K_b or the g-term repair at a
favorable complete cost? First name one literal kernel and its coefficient a,
prove the actual input/output contract, and charge the folds, phase tables,
recursive calls, normalization and owned restoration. A compatible producer,
native implementation and complete invoice are the blockers. The present
result reserves no continuation and establishes no profitable supplier.
