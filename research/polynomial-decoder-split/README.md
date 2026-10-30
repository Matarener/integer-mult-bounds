# Constructive binary decoder splits and equal-valued cuts

This package answers the algorithmic part of Open next question 1 in
[Charan/theon199's PR #2330](https://github.com/CrocSwap/integer-mult-bounds/pull/2330).
For supplied binary square blocks, `solve` deterministically extracts a maximum
packing of nonsingular minors with disjoint original rows and columns. It also
returns an equal-valued row/column cut. The implementation uses two nested
instances of classical unweighted matroid intersection. It does not enumerate
minor packings, cut pairs, or finite-field substitutions.

The contribution is a constructive specialization and executable certificate
interface for this decoder problem. Matroid intersection and induced matroids
are classical results. The predecessor's min-max theorem is a cited premise,
not an audit deliverable. [PROOF.md](PROOF.md) establishes the extraction and
cut-recovery contract and a conservative polynomial bound. This is a scoped
constructive algorithm with exact finite corroboration, not a physical decoder,
proof-assistant formalization, new kappa, or complete multiplication theorem.

For blocks `H_c` of order `v`, the output satisfies

```text
sum_c |U_c| = 2v - |S| - |T| + sum_c rank_F2 H_c[S,T],
det_F2 H_c[U_c,W_c] = 1,
```

with equally sized `U_c,W_c`, pairwise disjoint `U_c`, and separately pairwise
disjoint `W_c`. Elementary weak duality makes each such output an independently
checkable optimality certificate. The empty minor has determinant one.

## Reproduce

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/polynomial-decoder-split/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/polynomial-decoder-split
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/polynomial-decoder-split --check-source-history
```

The interpreter may be replaced by any CPython 3.12 interpreter. Only the
standard library is required. The verifier prints generated JSON ending in
`PASS_POLYNOMIAL_DECODER_SPLIT`, with SHA256 hashes of the package files and
literal certificates for the larger structured fixtures. It writes no files.
Registered commands run normally and with `-O`; acceptance uses explicit
exceptions in both modes.

New finite coverage exhausts all one-, two-, and three-color binary block
tuples at width two. It checks each output against permutation determinants
and exhaustive cut minimization, independently of the solver's elimination.
Thirty specified SHA256-derived inputs at widths 3, 4, 6, 8 and 12 and nine
structured inputs at widths 8, 16 and 32 receive a separate dense-rank
certificate check. The width-three samples also receive the literal exhaustive
check. A greedy-trap example and malformed-input/certificate controls are
included. These are new extraction tests; no predecessor verifier is run.

## Scope and dependencies

The written construction applies to every finite binary input. The executable
accepts 1 through 8 colors, 1 through 32 rows per square block, and at most 96
color copies per side. It rejects larger inputs before search. These are
implementation capacity bounds, not mathematical obstructions. The verifier's
exhaustive part has width two; its larger unstructured inputs are samples.

The supplied-block interface does not extract a pairing or support sets from
the actual `tied_min` decoder, prove the universal rational decoder conjecture,
or realize a selected supplier. It supplies an exact oracle for a later
source-bound application. All selected compiler, native, hosting, precision,
tape and analytic obligations remain unchanged. No Lean or production supplier
replay was run.

The task picker suggested `formal-interface-lemma`; `TASK.json` records the
changed scope. The concrete handoff in #2330 and the explicit instruction to
produce new work led to constructive extraction instead of a proof-assistant
binding or another audit. The cheap selected first control passed
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` on canonical main
`de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8.

## Open next questions

1. Bind this extractor to one actual `tied_min` pairing and its row/column
   supports. This would produce inspectable decoder-specific splits or cuts.
   First export the binary blocks from the pinned #2162 data without importing
   its search. The exact input adapter and source attribution remain to be done.
2. Extend the executable to other finite fields, retaining the same nested
   intersection and cut contract. Start with prime-field elimination and
   independent determinant checks. Field arithmetic and extension-field input
   formats are not implemented here.

## Credit and license

This contribution was produced by Nick Petalas. Charan/theon199 #2330 posed
the polynomial witness-extraction question and supplied the explicit cut
contract. DreamingOfClouds #2162 supplied the decoder split formulation and
generic-rank interpretation, following the #1590/#2111 decoder model.
A. Schrijver's [Theorem 3.3](https://ir.cwi.nl/pub/9901/9901D.pdf#page=12)
supplies the classical induced-matroid theorem. The shortest augmenting-path
algorithm and its terminal rank cut are the classical matroid-intersection
method, as presented in
[Michel Goemans's notes, section 6](https://math.mit.edu/~goemans/18453S17/matroid-intersect-notes.pdf).
Their results are credited rather than claimed as new. No predecessor code or
text is copied. New files are Apache-2.0 under the repository license.

Independent human and formal proof-kernel review are unclaimed.
