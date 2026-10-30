# Sharp mixed-rank invoice envelopes with an interior touching point

For every positive even m, integers a_i>1 and 0<p<q, lambda>0 and epsilon>=0,

```text
epsilon + lambda product_i (a_i^(q t) - a_i^p)
```

has sharp global minimum epsilon, attained uniquely at t=p/q. At epsilon=0,
the unique zero has exact multiplicity m. The written [proof](PROOF.md) covers
all real t and arbitrary finite even m. This is a **scoped algebraic proof**,
with finite executable corroboration. It is an arithmetic side result, with
no physical construction or new kappa claim.

The first example is

```text
6 H1 + H36 - 3 H4 - 2 H9
  = (4^t-2)(9^t-3) >= 0,
```

where H_r costs r^t. Equality holds only at t=1/2 and is a double zero. Adding
one H1 makes the sharp minimum gap one. Ranks 4 and 9 have no common integer
base. This resolves the touching-point obligation for this explicit infinite
family without numeric root isolation or exhaustion of a global root budget.

## Scope and predecessors

The question is the touching-root continuation in Ali Romman's
[#5788](https://github.com/CrocSwap/integer-mult-bounds/pull/5788), pinned at
`56565b9aec29203bddb14f5d0e76a657d7090699`. Its
[proof and limitation](https://github.com/aliromman/integer-mult-bounds/blob/56565b9aec29203bddb14f5d0e76a657d7090699/docs/research/recursive-power-variation.md)
are cited, not audited or replayed. Credit zxv for signed-invoice accounting,
mightyOil for the moment-order context, and woklerx for the specialized
crossing predecessor. Elementary factorization and calculus retain their
classical status; no literature priority is claimed for those methods.

This changes the `independent-moment` card from checking an existing supplier
to constructing a new exact invoice family and certificate. The card's first
selected-baseline binding command passed; no scientific predecessor replay
was run. [TASK.json](TASK.json) records the changed scope and source URL.
[SOURCES.json](SOURCES.json) binds the revision-8 catalogue and selected record
as historical provenance, with no live mathematical predecessor dependency.

The complete signed difference is new paid minus new targets minus old paid
plus old targets. `envelope.py` requires equal declared contracts and exact
agreement with an independently supplied sparse factor certificate. Equal
subset-product ranks are combined, including repeated bases. The executable
reports the sharp envelope only after this identity check. Matching contract
text does not prove a source-to-circuit interpretation.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/mixed-rank-touching-envelope/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/mixed-rank-touching-envelope/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/mixed-rank-touching-envelope
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/mixed-rank-touching-envelope --check-source-history
```

The first two commands print a generated JSON receipt with package/input hashes,
then `PASS_MIXED_RANK_TOUCHING_ENVELOPE`. They enumerate 696 factor contexts,
4,176 certificates, 49,944 expanded support entries and 23,472 exact
rational-power evaluations, with 26 rejection or mathematical failure controls.
Two-factor contexts use every ordered pair of bases in 2..7, q in 2..5 and
1<=p<q. Higher-factor contexts use every tuple over {2,3} of lengths 4,6,8,
with p=1,q=2. Each context uses scales 1,3 and offsets 0,1,7. Paid and target
placement alternates across certificates. These are finite corroboration of
the written proof, not a finite substitute for its continuum argument.

Inspect the portable authored example directly:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/mixed-rank-touching-envelope/envelope.py research/mixed-rank-touching-envelope/EXAMPLE.json
```

Expected minimum is 0, unique minimizer is 1/2, and root multiplicity is 2.
The checker and verifier write no files. Redirect receipts outside the checkout
if needed. Local checks use CPython 3.12.15 on Darwin arm64; no native packages
are required. Hosted CI status belongs to the PR, not to this proof.

## Limits

The checker accepts 2,4,6,8 synchronized factors, integer bases 2..64,
2<=q<=16, 1<=p<q, integer scale in 1..10^60 and offset in 0..10^60.
Expanded ranks must be at most 10^9 and coefficients at most 10^60.
Each histogram has at most 4096 keys; input files have at most one MiB.
The mathematical theorem is not restricted to these executable capacities.
Certificate discovery, unsynchronized touching points and arbitrary
exponential-polynomial classification remain outside the checker.

The example is synthetic. Source extraction, native implementation, ownership,
restoration, physical target independence, supplier/compiler admission, the
selected cold replay, Lean and a complete multiplication theorem are unclaimed.
Independent human and formal proof-kernel review are unclaimed. The selected
frontier and its five framework assumptions retain their existing status.

## Open next questions

Can an actual changed construction's complete signed invoice admit this factor
certificate after a justified common bill cancels? Start with one published
source-bound old/new pair and test exact sparse divisibility. This would turn
the arithmetic envelope into a useful source comparison. The blocker is a
complete physical bill, not finer sampling of the synthetic example.

Can exact factor certificates treat several distinct touching points without
assuming a decidable equality test for arbitrary logarithmic root ratios?
Start with factors whose roots are supplied rational exponents and group them
by exact rational equality. This would broaden the certified class. Root
recognition beyond that stated rational domain remains unresolved here.

## Credit

New proof application, integer invoice family and portable certificate checker
produced by Nick Petalas. Predecessor credit is retained above and in the proof.
New work is Apache-2.0.
