# Call-space identities for mixed positive-Q8 words

**Scoped proof with an exact finite certificate, plus a conjecture. No new κ.**
The selected frontier is unchanged.

## Question

unpaidmoon's [PR #4378](https://github.com/CrocSwap/integer-mult-bounds/pull/4378)
(`research/q8-square-iblock-obstruction`) leaves open whether four `[zi]`
targets and one `[zj]` target need 13 or 15 positive i/j calls. For words that
use a single label, `research/q8-cyclic-cubic-obstruction` (PR3558) proves
`n >= 3t` from two call-space identities, `X K Y = 0` and `X K^2 Y = 0`. Can
the mixed coefficient equations supply a pair of the same kind?

## Result

[PROOF.md](PROOF.md) has the definitions and proofs.

- **Theorem A (identity space).** Take active compressions `X M_w Y` of the 30
  label-block monomials `E L E ... L E` with at most three factors `L`,
  together with the target projectors `P_i`, `P_j`. The linear identities
  that hold for every exact word, of every shape and every finite dirty
  workspace, are exactly the span of the seven `F2[Q8]` coefficient
  equations. This span has dimension 7. The 25 explicit exact words in
  [WITNESS.json](WITNESS.json) give compression rows of rank 25 out of 32,
  which refutes every other candidate.
- **Theorem B (shears).** Exactly four unitriangular operators `I+h`, with
  `h` of degree one or two, satisfy `X(I+h)Y = 0`. They are the two PR3570
  shears `K1` and `K2` and two cubic shears `Q1` and `Q2`. None of the 12
  products of two shears of degree at most three is an identity.
- **Theorem C (pairs meet).** For each of the six pairs among `K1 U`,
  `K2 U`, `Q1 U` and `Q2 U`, where `U = im Y`, some exact one-role
  three-call word makes the two images intersect. The cyclic two-image
  argument therefore has no mixed analogue in this calculus, even at `t = 1`.
- **Conjecture D.** For every exact word,
  `dim(K1 U + K2 U + Q1 U + Q2 U) >= 2t`. All four images lie in `ker X`, so
  the conjecture would give `n >= 3t` for every mixed shape. That would make
  the exact minimum 15 at `(4,1)` and 24 at `(7,1)`. The conjecture is
  unproved. In complete meet-in-the-middle censuses it holds on every exact
  mixed-label word:

  | roles | length | exact words | mixed-label | span − 2t: count |
  |---:|---:|---:|---:|---|
  | 1 | 3 | 6 | 4 | 0: 4 |
  | 2 | 5 | 24 | 24 | 1: 24 |
  | 2 | 6 | 12,368 | 9,824 | 0: 9,824 |
  | 2 | 7 | 68,512 | 52,592 | 0: 44,884; 1: 7,708 |
  | 2 | 8 (`--full`) | 407,296 | 407,296 | 1: 359,836; 2: 47,460 |

  Targets range over `{zi, zj, 1}^r`, excluding the all-identity target.
  These censuses have `t <= 2`, where `n >= 3t` is already known. They are
  evidence for the conjecture, not a new length bound.

The (4,1) question is not decided. For the next contributor, the result
means that a mixed `n >= 3t` proof cannot come from one more linear
compression identity of degree at most three, or from disjointness of a
single pair of shear images. It needs a joint four-image (or larger)
argument, monomials of degree four or higher, the dirty endpoint blocks,
or a non-compression method.

## Reproduce

From the repository root, with CPython 3.12 and the standard library only:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/q8-mixed-shear-identity-space
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/q8-mixed-shear-identity-space/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/q8-mixed-shear-identity-space/verify.py --full
```

The registered command takes about 15 seconds and prints
`PASS_Q8_MIXED_SHEAR_IDENTITY_SPACE` with a JSON summary. The `--full` run
adds the two-role length-8 census (about 3 minutes locally) and is opt-in.
Neither run writes files.

Not run: Lean, Docker and the selected full cold replay. This package
changes none of their inputs.

## Limitations

Theorem A covers the degree-three compression calculus only. It does not
exclude identities with degree-four or higher monomials, rank arguments
that are not linear identities, arguments that use dirty rows and columns,
or methods outside call space. The census proves Theorems A and C by
explicit witnesses; for Conjecture D it is finite evidence only. Nothing
here prices a physical caller, routing, restoration, hosting, precision or
a supplier. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

Structured versions are in [TASK.json](TASK.json).

1. **Prove Conjecture D.** A proof gives `n >= 3t` for every mixed shape and
   closes both open lengths of PR #4378. First step: test it on three-role
   words of length 9 with `t = 3`, where PR3536 already gives the minimum 9.
   Then look for a filtration argument that uses `K2 = K1 + (ij + ji)` and
   `Q2 = Q1 + (ij + ji)`.
2. **Which identities appear at degree four?** Theorem A stops at degree
   three. Higher monomials have zero coefficients in `W` but are nonzero
   compressions. First step: build two- and three-role witness sets with
   rank deficiency explained, before trusting any apparent degree-four
   relation found on two-role samples. Two-role samples can produce
   small-dimension relations.
3. **Does a 13-call word exist at shape (4,1)?** A counterexample to
   Conjecture D at `t = 5` would be the place to look. First step: a
   meet-in-the-middle search restricted to six-role cores (PR3536's
   half-call scalar core bounds the core at `floor(13/2)`). This is far
   beyond the census here.

## Credit

Produced by Nick Petalas. The model, the PR3517 normal form, the PR3570
mixed quadratic identities and the PR3558 cyclic subspace theorem are
earlier work of Nick Petalas, credited and not re-audited. The open (4,1)
question is from unpaidmoon's PR #4378. The register-model lineage in those
packages (Tuafo/PR2900, ywz65/PR2587, Aaron Wang/PR2318, Cinna Davis,
steph4n-gh and others) keeps its credit. New here: the complete identity
space of the degree-three calculus, the classification of the four shears,
the six pair-intersection witnesses, and Conjecture D with its census.

Apache-2.0.
