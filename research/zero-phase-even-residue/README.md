# Sharp zero-phase native witness length for n=2 mod 4

This contribution was produced by Nick Petalas. Apache-2.0.

For every n=4k+2>=2, the shortest binary tuple with zero nonconstant
quadratic phase and full affine span has exactly **2n+2 columns**.
At six axes the minimum is 14. A two-coset Gauss-sum contradiction gives
the lower bound; disjoint length-eight code blocks and a six-column block
attain it. [PROOF.md](PROOF.md) gives the uniform argument and explicit rows.

The cited cuspidal cancellation lemma of Ali Romman's
[PR #5635](https://github.com/CrocSwap/integer-mult-bounds/pull/5635) then
makes the first-visible widths of its zero-phase residual exactly
`L_r=2n+2+((r-(2n+2)) mod 4)`. At six axes these are `(16,17,14,15)` in
residue order `(0,1,2,3)`. These are **not claimed complete native cutoff
thresholds**. An upper construction for every phase character remains open.

This is a scoped algebraic proof with finite corroboration, answering part
of #5635's explicit other-axis-residues question. The new unbounded domain
starts at six axes. Two axes supply a small exhaustive control. No new
kappa, physical supplier or selected-frontier change is claimed.

## Evidence and reproduction

Use the repository CPython 3.12 interpreter from the worktree root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/research_package.py --package research/zero-phase-even-residue
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/check_research_commit.py --package research/zero-phase-even-residue --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/zero-phase-even-residue/verify.py
```

On another machine substitute a CPython 3.12 executable. Standard library
only. The direct verifier prints `PASS_ZERO_PHASE_EVEN_RESIDUE` in its
JSON receipt; the registered runner prints `PASS_REGISTERED_RESEARCH_PACKAGE`.
Receipt hashes bind every package file and the exact cited source proof.
No receipt is handwritten, and the verifier writes no files.

The bounded check covers 132 attaining padded tuples on dimensions
2,6,...,130, 20 independent literal-column checks, 1,092 explicit codewords,
33 exact Gaussian-integer contradictions, two other-residue controls and
18 rejected malformed or mathematically invalid inputs. The complete
ordered two-axis census has 5,461 tuples and 174,752 literal phase checks.
There are exactly 90 full-span zero-phase tuples at length six and none
at shorter lengths. Each of those 90 is a permutation of `(1,1,2,2,3,3)`.
This finite census does not stand in for the all-size proof.

[VALIDATION.md](VALIDATION.md) records capacities and verification limits.
No predecessor executable, fixture or reported count is replayed. Its proof
is cited and source-bound as an input for the residual corollary.

## Limits

The complete all-character kernel cutoff, efficient expansion of a large
group-algebra residual, actual native inputs and returns, paid invoices,
compiler, precision, tapes and stock are outside this result. The corollary
uses #5635's cuspidal cancellation lemma and its classical character-theory
input. Independent human and formal proof-kernel review are unclaimed.
All five framework assumptions retain their status.

The original formal-interface card is explicitly changed to a written
native-interface side result. This does not discharge a selected all-size
assumption. Base main is `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority
revision 8. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19216168).
Published overlap was checked through current open PRs and Discussion
claims, with separate main/merged searches. Sparse local notes and unpublished
work remain coverage limits; a search with no hit does not prove novelty.

## Open next questions

- Determine whether every nonconstant phase character has a full-affine-span
  realization at the proposed widths in six dimensions. Start with a
  character-orbit reduction and a constructive upper bound. The present
  theorem handles only the zero character, so it does not settle this.
- Determine the complete test cutoff in the other higher-dimensional residue
  classes. Start with a matching all-character upper construction; the
  existence of a zero-phase witness alone is insufficient.

## Credit

Credit Ali Romman #5635 for the question and code/phase/cuspidal interface,
#5369/#5529/#5622 for the retained grammar and Fourier framework, Joseph
Anglada #5542, Hiroki KUMAZAKI #5522, Mihir Srivastava #5521, Jose Manuel,
ywz65, Chris R and the retained native/phase contributors. Doubly-even
codes, character orthogonality, Gauss sums and Green's character theorem
are classical. No global literature-priority claim is made. New work is
the n=2 mod 4 length theorem, its attaining family and zero-phase
first-visibility application.
