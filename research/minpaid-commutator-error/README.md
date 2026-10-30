# Sharp target error at the minimum dirty-commutator call count

This contribution was produced by Nick Petalas. Apache-2.0.

A different split tree reduces the sharp completed-target defect coefficient
without increasing the minimum paid leaf count or dirty scratch depth.
At three factors it reduces **7 to 5**, with ten paid calls and two dirty
connectors. At five factors it reduces **17 to 11**, with 28 paid calls.
At 63 factors it reduces **727 to 665**, with 4,000 paid calls and six
connectors. These coefficients multiply the same ordered-subset product
norm bound and the same per-leaf destination-defect allowance.

This is a **scoped all-n proof with exact finite corroboration**. It changes
the split topology in Adam Gall's [PR #2067](https://github.com/CrocSwap/integer-mult-bounds/pull/2067).
That source's response argument and rounded-leaf boundary are cited, not
replayed as the contribution. The changed tree retains arbitrary dirty
inputs, ideal restoration, product order, both word orientations and every
inverse call. No new kappa or complete multiplication theorem is claimed.

## Exact optimum

For n>=1, let d=floor(log2 n), q=2^d and k=n-q. The minimum number of
paid leaf calls among all full ordered binary commutator trees is

```
P_min(n) = 3qn-2q^2.
```

Among the trees attaining this minimum, the smallest sharp target coefficient
is

```
C_min(n) = 3^d + 2 * sum of the k smallest weights in W_d,
W_d = {2^j with multiplicity binomial(d,j), j=0,...,d}.
```

Start with the perfect depth-d tree and expand its k bottom paths with the
fewest right edges. Assign the original factors to the new leaves from
left to right. This realizes the optimum at depth ceil(log2 n).
[PROOF.md](PROOF.md) proves the paid-count exchange, the target response law
for arbitrary trees and the sharp binomial formula. No global literature
priority is claimed for binary-tree exchange or binomial counting methods.

The paid-count formula already describes the balanced source word in #2067.
The new result is the sharp target coefficient at that minimum paid count,
with an attaining changed tree. The first strict improvement is already n=3.

## Reproduce

From the repository root, with the Python 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/minpaid-commutator-error/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/minpaid-commutator-error/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/minpaid-commutator-error
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/minpaid-commutator-error --check-source-history
```

Other hosts can substitute any CPython 3.12 executable. The direct verifier
prints `PASS_MINPAID_COMMUTATOR_ERROR` in a generated JSON receipt that binds
all six package files by SHA256. It writes nothing and needs neither Git
nor predecessor files. No receipt is hand-written or stored as a result.

The independent shape oracle enumerates all 6,918 full ordered tree shapes
with one through ten leaves, without restricting their paid count before
minimization. A separate literal-word interpreter checks every minimum-paid
tree through 16 leaves, both orientations, arbitrary-input endpoints and
signed-defect attainment. This is 275 trees, 550 oriented words and 83,122
paid gate occurrences. Noncommuting rational orthogonal 2-by-2 factors
check both orientations at n=3,5,9, including full dirty-role endpoints and
independently aligned defects. Rejection controls distinguish malformed
inputs/trees, omitted restoration, wrong chronology and a lower error count
that requires more paid calls. These finite tests corroborate the written
all-n proof; their finite bounds are not restrictions on that theorem.

## Scope and limits

The original `uniform-transfer-audit` card is explicitly changed to a local
precision side result. This resolves a new split-tree optimization problem;
it does not discharge any selected framework assumption at its actual caller.
The selected source-binding orientation passes on canonical main
`19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19219035)
records the changed premise before substantial work.

The error contract permits arbitrary additive destination-supported defects
at every paid leaf, bounded by epsilon, and assumes every ordered subset
product has norm at most G>=1. Sharpness concerns independent defects, not
a particular rounded numerical kernel. Scratch error, intermediate growth,
feedback stability and numerical inverse cancellation require separate
bounds. No smaller whole-state or caller precision reserve is asserted.

The paid optimum is only within full ordered binary four-phase commutator
trees. Extra operations, other word families, different defect support and
correlated defects are outside the claim. No native/physical caller,
rounding implementation, preparation, stock, tape, compiler or analytic
recovery is supplied. All five selected assumptions remain. Lean, Docker,
predecessor scientific replays and the selected full replay are unrun.
Independent human and formal proof-kernel review are unclaimed.

Power-of-ten inspection: all loops use fixed finite census domains or
validated n<=256, and expansion is iterative with at most twice the paid
leaf count in stack-processing steps. No recursion or dynamic evaluation
is used. Functions stay below 60 physical lines. Python integers, fractions
and collections allocate dynamically, a managed-runtime deviation. Trees
have at most 255 internal positions; literal scalar words have at most 256
calls in the exhaustive bottom-subset domain, and matrix fixtures at most
88 calls. The larger n=255 comparison constructs a tree and counts its
leaves, without expanding its word. Normal and optimized warning-strict
checks use explicit exceptions. No separate static type checker was run.

Overlap checking covered a fresh 310-open-PR cache and 5,453 Discussion
records, plus live PR/claim reads and targeted merged-PR/main-tree searches.
The sparse local-note scan covered only 238 of 8,136 note paths; the explicit
main-tree searches partly supplement that gap. No match is not a novelty
certificate. Ali Romman's [Discussion #5257](https://github.com/CrocSwap/integer-mult-bounds/discussions/5257)
studies deterministic two-factor scalar rounding correlations. This result
changes the tree under the independent-defect contract. Earlier multiway
echo-tree call optimizers use different grammars and objectives.

## Open next questions

1. Can one actual rounded-leaf caller use this changed tree with a smaller
   completed-target precision term while retaining all interior stability,
   inverse-preimage and movement charges? Start with the n=5 word, whose
   integer target-count ceiling drops by one binary bit. Actual kernel
   defect bounds and a complete caller are required.
2. What is the optimal target-error versus paid-call tradeoff when extra
   paid calls are permitted? Start with n=4, where 16 calls give coefficient
   nine and a 22-call comb gives seven. A declared paid budget and any
   scratch/interior constraints must remain explicit. No such frontier is
   computed here.

## Credit

New theorem, attaining trees and verifier produced by Nick Petalas. Credit
Adam Gall / adamgall #2067 for the sharp completed-endpoint response model;
Chafik Boukhalfa #628, #862 and #905 for the recursive dirty construction;
Hanson Sun #1085 for factor-order invariants; Charles Bethin #1278 and
single-register interval transport; Arham Tahir #1374; woklerx #1855;
Philipp / mightyOil #1295; Ali Romman #1054 and #985; Gareth Davidson #877;
0xkilgore #663 and the retained numerical lineage. Their results are cited
without importing, auditing or changing their source files or credit lines.
