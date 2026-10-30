# Construct optimal theta sharing in encoded-width time

Scoped proof and deterministic constructor, produced by Nick Petalas.
Apache-2.0. Independent human and formal proof-kernel review are unclaimed.

For the fixed seven-vertex theta(2,3,3) query mask, an optimal coordinate-sharing
recipe can be computed with a number of integer arithmetic operations independent
of the seven payload widths. If the largest width has B bits, construction and
working storage use O(B) bit operations and bits. The output is eight shared
counts, seven private counts, a seven-entry half-cover and the exact fitting rank.

This replaces the `product_i(d_i+1)` residual-state algorithm in JoyboyBrian's
[PR #5218](https://github.com/CrocSwap/integer-mult-bounds/pull/5218).
Its all-field fitting-rank theorem is cited, not replayed or audited. The
new contribution is the compressed constructor and its integer optimality
certificate. This is a theoretical complexity improvement, with no measured
runtime comparison and no new kappa.

Write `S=sum(d)` and let `Y` contain the 267 vectors `y in {0,1,2}^7` with
`y_u+y_v>=2` on every edge. The implementation also gives the value formula

```
maximum shared pairs = floor(min_(y in Y) d dot y / 2)
minimum fitting rank = S - maximum shared pairs
```

[PROOF.md](PROOF.md) proves the all-width constructor. A fractional matching
extreme point has at most one half-integral odd cycle because the theta graph's
odd cycles share endpoints. Alternating rounding loses at most one half and
attains the integer optimum. A fixed family of 1,583 incidence-matrix templates
constructs a fractional optimum without expanding any coordinates. The returned
integer matching and half-cover certify optimality using only integer sums.

The complete ordered fitting contract retains identity diagonal blocks and
zeros on both ordered nonedges. Allowed rectangular blocks may be nonsymmetric
and noncommuting. The compressed recipe constructs a block-diagonal sum of
two-coordinate all-ones channels and private coordinates when expansion is
desired. Writing a full matrix still costs its full output size.

## Reproduction and evidence

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/theta-compressed-constructor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/theta-compressed-constructor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/theta-compressed-constructor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/theta-compressed-constructor --check-source-history
```

The direct checks print `PASS_THETA_COMPRESSED_CONSTRUCTOR`. They cover all
2,187 vectors in `{0,1,2}^7` against an independent one-copy matching recurrence,
390 rank calculations over F2, F3 and F101 on 130 attaining matrices, all 2,109
fitting entries, nine large-width fixtures up to 4,099 bits, and fourteen
rejection controls. The small domain contains 76 half-integer fractional optima.
The finite checks corroborate the written proof; they do not prove it by census.

Pass `--receipt /absolute/path/outside/checkout.json` to either direct check
for a generated receipt binding counts and every package file's SHA256.
Default verification writes nothing. It hashes the two cited source documents;
it imports no predecessor executable and repeats no predecessor census.

To use the constructor from this package directory:

```python
from constructor import compile_templates, construct, validate

templates = compile_templates()  # graph-only initialization, reusable
widths = (2**4096,) * 7
certificate = construct(widths, templates)
validate(widths, certificate)
```

## Scope, credit and overlap

The revision-8 `complex-rank-shape-decoder` card is changed to this scoped
algorithmic side result. The selected baseline reported
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; no selected supplier replay was run.
The selected conditional kappa and all five framework assumptions remain.
There is no physical supplier, complete invoice, native execution, precision,
fixed-tape, restoration, owner-lifetime or compiler admission claim.

Credit JoyboyBrian #5218 for the exact theta fitting-rank theorem, matching
reduction and earlier constructor; JoyboyBrian #5023, Tekalign #3362, Nick
Petalas #4909, Sagar Thakrar #2484 and the retained query-mask lineage.
LP duality, half-integrality and incidence basis methods are classical.
No general matching-theory or literature-wide priority is claimed.
The predecessor package and its attribution remain unchanged.

The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19221484)
records the target. Overlap checking read live PRs, this account's recent
contributions, active Discussions, local reservations, all-main README terms
and merged-PR searches. The cached task scan reports its own freshness and
sparse omissions. These checks do not exclude unpublished or unindexed work.
The predecessor's current Open next questions concern physical callers; this
constructor improvement is a new algorithmic extension, not a claim to answer
that physical question. There is no automatic wider graph search.

## Open next questions

Can an actual recursive caller supply this theta ordered read mask with a
favorable complete invoice? First identify its literal incidence map and
charge copies, coefficient delivery, owner lifetimes and restoration. A
source-bound producer/consumer and a physical tariff remain missing.
The structured question is in [TASK.json](TASK.json). Stop this contribution
at the compressed constructor.

## Implementation constraints

The two new Python files use bounded structured iteration and no recursion.
All functions are under 60 physical lines. Constructor loops have fixed bounds
from the seven vertices and eight edges; matrix checks enforce at most fourteen
coordinates. Exhaustive verification has exactly 3^7 small width vectors and
nine large fixtures. Explicit `ValueError` contracts remain active under `-O`.

Power-of-ten rule 3 has a managed-runtime deviation in both files. Python
allocates arbitrary-precision integers and finite collections dynamically.
The constructor keeps a fixed number of O(B)-bit integers and graph-only
templates; the verifier bounds its table at 2,187 entries and matrices at
14 by 14. No fixed-allocation claim is made. A fixed-storage port would be
needed only for a runtime requiring it. Rule 9 has a bounded standard-library
callback deviation for `min`/`sorted` keys and the rejection-test callable;
targets and lifetimes are local and explicit. There is no dynamic code
generation or external solver. Warning-strict normal and optimized execution
and source compilation provide the applicable interpreter diagnostics.
