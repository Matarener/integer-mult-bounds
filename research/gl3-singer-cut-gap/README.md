# Fano point and line cuts stop at three for a four-call Singer target

For the binary GL3 target with columns `(7,1,3)`, every nonnegative
combination of coordinate-cut rank inequalities from finite sums of the
Fano point and dual-line permutation modules has normalized value at most
**three per target**. Two explicit cuts attain three. The independent
coordinate word costs four per target.

The sharp cone value is `3t` for any number `t>=1` of targets, each either
g or its inverse, with any finite restored dirty workspace and free
invertible binary scalar mixing. This is a **scoped proof with a finite
256-cut certificate**. It rules out this particular invariant route for
closing the direct-word gap. It does not prove shared paid work or the
actual multi-target optimum. No new kappa or selected-frontier change.

[PROOF.md](PROOF.md) defines the model, proves the passage from the finite
certificate to all finite module sums and role counts, and gives the
matching rational primal and dual certificates. Every one of the 128
point cuts and 128 line cuts is checked exactly. The decisive inequality is
`2*c_H(g) <= sum_(i!=j) c_H(I+E_ij)`. The attaining point cut is `{2,4,6}`
with weight `1/2`; the line cut is `{2,4}` with weight `1`.

## Reproduce

From the repository root, Python 3.12 and the standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gl3-singer-cut-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gl3-singer-cut-gap
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gl3-singer-cut-gap --check-source-history
```

A reviewer can replace that interpreter path with any CPython 3.12 binary.
`VERIFY.json` registers warning-strict normal and optimized checks. Each
prints `PASS_GL3_SINGER_CUT_GAP` inside a generated JSON receipt that binds
all package files and both declared predecessor README inputs by SHA256.
No receipt is hand-written or accepted in place of recomputation. The
verifier writes no files and needs neither Git nor network in a source
export with its declared inputs.

Coverage includes all 168 group elements, 56,448 action-composition checks,
1,176 point-line incidence checks, all 256 cuts, and 2,520 actual paid
crossing blocks from all 35 rank-one idempotents through three roles on
six declared cuts. Formal group-algebra controls check the direct endpoint
with one to three targets and a dirty spectator, 24 omitted calls, three
restored dirty detours and three corresponding leaks. Four malformed-input
controls remain active under optimization. These controls support the
specified finite certificate; they are not larger-register word searches.

Both direct commands and the complete registered replay passed locally on
CPython 3.12.15, macOS arm64. Each registered command completed in under one
second. Hosted CI certification is separate from these local checks.

## Verifier bounds

The checker has no recursion, dynamic evaluation or subprocesses. All 21
functions are at most 29 lines. Group enumeration considers 343 column
triples; Cayley traversal has seven rounds and at most 168 states; each
action table has 168 rows. Formal coefficients have at most 168 group
keys and four scalar roles in the controls; each word has at most 14
factors. Rank elimination has at most 21 columns. Every rejection uses an
explicit exception, so optimization cannot disable it.

Python necessarily allocates managed objects during these computations.
This is a deviation from fixed allocation after initialization, confined
to the stated finite domains. Fixed matrix sizes, group support and loop
bounds constrain live mathematical data; Python allocator overhead is not
statically certified. Expanding these domains requires a fresh resource
bound. Warning-strict normal and optimized execution, source compilation
and the repository package checks are the available diagnostics; no
separate Python linter is installed in the environment used here.

## Scope and next decision

The original `bit-new-register-model` card is changed to the quotient-based
invariant question in Josie Elliston's PR #1974, Open next question 2.
That predecessor already proves the complete two-role tariff by a word
census. Its census is cited, not replayed. This package adds the exact
point-and-line coordinate-cut cone obstruction for the specified order-seven
endpoint. A natural-representation alias alone does not prove this closure.

Stop this certificate family for this target. Arbitrary subspaces,
other permutation modules, role-dependent cuts and nonlinear or integer
combinations are outside the proof. Native address realization, compiler,
hosting, precision, tape accounting, recursive profiles and the complete
multiplication theorem are unproved here. No human or proof-kernel review
is claimed; no predecessor engine, selected supplier, Lean or Docker replay
is run.

## Open next questions

- Can a coordinate cut in a different GL3 permutation module certify more
  than three for this exact target? Start with one explicit finite G-set
  and report its six generator crossings and target crossing. It must lie
  outside the point/line direct-sum class. A stronger valid cut is missing.
- Can a noncoordinate subspace cut in a point/line module sum exceed three?
  Start with one explicit binary subspace and compute all seven quotient
  ranks. The present proof uses coordinate subsets and does not settle it.

## Sources and credit

The proof and verifier were produced by Nick Petalas. Apache-2.0.
Credit Josie Elliston's
[PR #1974](https://github.com/CrocSwap/integer-mult-bounds/pull/1974) and
Hanson Sun's seed18 package for the formal mixed-target model and written
invariant question; Adam Gall and Ross Richardson for the cut-rank method;
JoyboyBrian's [PR #4974](https://github.com/CrocSwap/integer-mult-bounds/pull/4974)
for the existing single-target support argument; and the retained eumemic,
Ali Romman and Gareth Davidson register-model lineage. The cut inequality
and single-target distance principle are inherited. The matching finite
cone certificates for this Singer endpoint are the new contribution.

[SOURCES.json](SOURCES.json) pins the source bytes at canonical main
`de5ec2e7a6074068452f45b1a191b5c72832df4a`. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19217837)
records the exact scope. Main-tree, merged-PR, open-PR and live claim
searches found no matching Singer point/line certificate. This is search
coverage, not a guarantee about unpublished work. The existing three-cycle
cut-ceiling work has a different endpoint and is not extended here.
