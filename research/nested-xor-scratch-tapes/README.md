# Fewer head crossings for dirty-scratch XOR correction

The construction, proof and verifier were produced by Nick Petalas.
Apache-2.0. Claim type: scoped construction and mathematical proof, with
exact finite machine evidence. No new kappa.

Nesting the scratch swaps in Dugongue / David Ganz's
[PR #3879](https://github.com/CrocSwap/integer-mult-bounds/pull/3879)
reduces its in-place XOR correction cost for every nonzero mask on N>=4
records. Both heads and the arbitrary dirty scratch record still return
exactly. The alphabet, record representation, scratch capacity and 3N/2
record swaps are the same.

For N=2^h, delta=m+l, m the highest power of two in delta, and 0<=l<m,
the exact record-crossing counts are

```
serial, cited from #3879: (N-2)*m + 2N-2
nested, proved here:     N*m + 2*(N/(2m)-1)*(l+1).
```

The saving is at least N-2 record crossings, or (N-2)*(B+2) unit tape
transitions at record width B. With N=512 and delta=16, crossings fall
from 9,182 to 8,222, saving 960*(B+2) transitions. At B=2 the new literal
machine executes 38,264 transitions, saving 3,840 under the cited serial
invoice. This is an exact operation count, not a measured runtime speedup.

[PROOF.md](PROOF.md) gives the unrestricted h/B theorem, dirty-state
argument, exact travel formula and finite-control invoice.
[machine.py](machine.py) emits the new visit order and literal four-symbol
two-tape transition tables. [verify.py](verify.py) supplies an independent
unit-step executor and token-permutation oracle. The star-transposition
identity is classical; the contribution is this nested tape construction
and its exact all-mask invoice. No global minimum is claimed.

## Reproduce

From the repository root, CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/nested-xor-scratch-tapes/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/nested-xor-scratch-tapes/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/nested-xor-scratch-tapes
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/nested-xor-scratch-tapes --check-source-history
```

Any CPython 3.12 path can replace the local interpreter. Expected markers
are `PASS_NESTED_XOR_SCRATCH_TAPES`, `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`. Default replay writes nothing. `--emit-result`
prints a generated receipt with SHA256 of all eight package files.

[RESULT.json](RESULT.json) records 1,023 complete token schedules through
h=9, with 1,012 strict improvements; 254 literal payload executions; 100
complete one-bit data/scratch basis cases; 284,889 unit transitions in those
accepted machine runs; and twelve rejecting controls. The controls cover
wrong nesting, omitted scratch restoration, wrong mask, illegal movement
or write, malformed framing, execution exhaustion and input/expansion bounds.
The two h=9 literal executions have masks 1 and 16. Larger literal tables
are not counted as executed. The old machine is not replayed: its published
invoice is a cited comparison, and no predecessor verification is claimed.

## Scope and implementation bounds

This is a cheaper standalone physical permutation primitive. Native return
layout, stream acquisition, placement, representation conversion, full
caller integration, compiler and recursive/outer funding remain open.
None of the selected record's five framework assumptions is discharged.
No selected cold replay, Lean proof or complete multiplier is supplied.
Independent human and formal proof-kernel review are unclaimed.

The written schedule works for every finite h and B. Executable schedules
are bounded to h<=9; table expansion rejects more than 250,000 entries
before allocation. The literal executor permits at most 1,000,000 steps.
Its fixed fixtures have B<=3 and at most 512 records. All loops have these
finite bounds, and no runtime recursion or generated Python code is used.
Functions are below sixty lines. Invariants use explicit exceptions and
remain active under optimized Python.

Power-of-Ten deviations are limited to Python's managed allocation and the
twelve explicit rejection callbacks. Table entries, operations, fixture
cells and interpreter steps have the bounds above; callbacks have only the
twelve local targets listed in `controls`. Direct execution and the normal
and optimized registered checks exercise these limits. A future larger
literal replay must first revise the resource caps and evidence. Python
warning-strict execution, AST parsing and indentation checks provide the
available diagnostics; no static type-checker configuration is introduced.

## Source and credit

This takes the cost comparison in Open next question 2 of PR #3879 as a
source, narrowing it to a faster in-place primitive before full native
placement. Its exact record ABI, W/R0/L0 transition templates and serial
formula retain Dugongue / David Ganz's credit. The templates are reimplemented
with attribution; no predecessor executable is imported. Gonzalo Mier's
PR #3480 supplies the endpoint-correction context, Cinna Davis's PR #2297
the five-plane operator, and Sagar Thakrar's PR #3876 the scalar-contract
boundary. Tekalign's permutation-frame compiler and the earlier native
routing and decoder authors retain the credit recorded in #3879.

The same author's merged [PR #3880](https://github.com/CrocSwap/integer-mult-bounds/pull/3880)
provides a streamed-chunk space/time tradeoff with larger dirty buffers.
It explicitly reports that its one-record point is slower than #3879.
This contribution improves #3879's one-record schedule. It does not replay
or compare the larger-buffer points of #3880.

[SOURCES.json](SOURCES.json) pins the source README, proof and machine as
provenance at canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`.
They are not live replay dependencies. Priority revision 8 is pinned in
[TASK.json](TASK.json). The source-binding positive control passed after
materializing its sparse closure. Remote overlap coverage included 401
open PR bodies and 5,645 Discussion records with complete pagination;
working local notes were sparse. Separate searches covered merged main,
merged PRs, this account's recent PRs and concurrent claims. These checks
do not cover unpublished work or prove exhaustive novelty.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19228649)
states the same schedule and predicted formula. The first verified
improvement ended construction work.

## Open next questions

1. Can another dirty-scratch swap order reduce head travel further at the
   same record-swap count? Start with exact shortest paths for four or eight
   records. A global travel lower bound is missing; this package asserts none.
2. Which actual native return supplies this framed record bank, and does
   the saving survive its complete placement/representation bill? Bind one
   producer's output and charge acquisition, return and ownership. Those
   physical interfaces remain the blocker to using the primitive in a supplier.
