# Exactly 406 cross-side merges for the frozen joint invoice

This contribution is produced by Nick Petalas. It is a scoped mathematical
proof with a finite exact accounting certificate, under Apache-2.0.

For the complete frozen role ledger of Mark / Matarener's
[PR #5298](https://github.com/CrocSwap/integer-mult-bounds/pull/5298), the minimum
number of disjoint cross-side paid-job merges that passes the signed moment at
`C = 7/2000` is **406**. Each merge replaces one complex rank `a` and one BIT
rank `b` by the paid rank `a+b`. Every productive target and every unmerged paid
job stays in the bill. All roles are optimistically eligible. No job can be
used twice, and merged jobs cannot merge again.

The constructive witness is 222 pairs of ranks `(72,63)`, two pairs `(72,56)`,
and 182 pairs `(64,56)`. Write `M = sum targets^(1-C) - sum paid^(1-C)`.
The exact verifier encloses the optimal margins in these rational intervals:

```text
405 merges: -0.197285824316 <= M <= -0.197285824315
406 merges:  0.088428560458 <= M <=  0.088428560459
```

The general pairing theorem below makes 405 an exclusion for every allowed
matching, rather than a failed heuristic search. The application and exact threshold are the new result.
The predecessor's ledger and mathematical conclusions are cited premises and
are not re-audited here. This changes the `joint-query-controller` card to a
precise accounting question at the predecessor's explicit whole-job boundary.

## Optimal pairing theorem

Let `0 < alpha < 1` and let both sides be finite lists of positive ranks.
For exactly `k` disjoint cross-side merges, the smallest paid alpha-moment
comes from selecting the largest `k` ranks on each side and pairing them in
that same descending order. This holds for arbitrary positive real ranks.

To prove it, define the saving from one merge by

```text
Delta(a,b) = a^alpha + b^alpha - (a+b)^alpha.
```

It is positive by strict concavity. Its derivative in `a` is
`alpha [a^(alpha-1) - (a+b)^(alpha-1)] > 0`, and the derivative in `b` is
positive too. Thus replacing a selected rank by a larger unselected rank
cannot reduce the saving. Repeating the exchange selects the largest `k`
ranks on both sides, including ties in any order.

The mixed derivative is
`Delta_ab = alpha(1-alpha)(a+b)^(alpha-2) > 0`.
For `a >= a'` and `b >= b'`, integrate this derivative over the rectangle to
obtain

```text
Delta(a,b) + Delta(a',b') >= Delta(a,b') + Delta(a',b).
```

Exchanging inverted pairs therefore increases or preserves the total saving.
A finite sequence of exchanges produces the descending pairing. Since the
unmerged original bill is fixed, maximizing this saving minimizes the complete
paid moment. Further disjoint merges strictly improve the margin, so failure
at the optimal 405-pair matching excludes every matching with at most 405
pairs. The explicit 406-pair witness proves sharpness.

This is a specialization of the classical supermodular rearrangement argument.
The contribution claims the exact source-bound threshold and its application,
not discovery of rearrangement or of concave merge gains.

## Exact arithmetic and evidence

The stdlib-only verifier reads the full predecessor `RESULT.json` as a frozen
input, with SHA256
`e712e5373ecbfea0c1b7c115b52eea4fb533c6c7c2ebae3aa98a2dd1f058721c`.
It computes the new complete moments from that ledger, without replaying the
predecessor's roots, six models, native words or other conclusions.

The exponent is the exact rational `alpha=1993/2000`. Powers use rational
outward bounds, without floating point, Decimal, logarithm library calls or a
root grid. Write `r=2^s u` with `1<=u<2`. For `z=(u-1)/(u+1)`, sum the first
64 terms of `log u = 2 sum z^(2j+1)/(2j+1)` on a `2^-120` grid, rounding each
term outward. The remaining positive tail is bounded by
`2 z^129/[129(1-z^2)]`. Apply the same bound to `log 2`.

For `x=C log r`, the verifier sums `exp(x)` through degree 24 and bounds its
tail by the degree-25 term times `26/25`, valid for `0<=x<=1`. Monotonicity and
reciprocal interval arithmetic then bound `r exp(-C log r)`.
All later additions, subtractions and comparisons use exact rational numbers.

An independent certificate rounds every needed power interval outward to a
`2^-36` grid and checks the defining integer-power inequalities for all 145
ranks from 1 through 145. If its endpoints are `l/2^36` and `u/2^36`, it checks
`l^2000 <= r^1993 * 2^72000 <= u^2000`. The coarser, integer-certified bounds
separately prove both moment signs. Thus the sharp 406 threshold has a finite
certificate that does not require trusting the logarithm/exponential enclosure
implementation. The general matching theorem remains a written proof.

Finite corroboration enumerates all 1,200 choices of two three-job multisets
over ranks 1 through 4 and a merge count 1 through 3. All 13,200 labeled partial
matchings agree with the optimal pairing theorem. Seven invalid input controls
reject, and a strict crossed-pair example detects reversing the pairing rule.
The source hash, mass preservation, job-count reduction and explicit pair
multiplicities are executable invariants. Every run prints a generated receipt
binding the package files by SHA256.

## Reproduce

From the repository root, use CPython 3.12, standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/joint-cross-merge-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/joint-cross-merge-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/joint-cross-merge-threshold
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/joint-cross-merge-threshold --check-source-history
```

Use an available CPython 3.12 path on another machine. The expected marker is
`PASS_JOINT_CROSS_MERGE_THRESHOLD` with `minimum_merges: 406`.
Verification writes no files. See `VERIFY.json` for both registered commands.

## Scope and limitations

This is an exact threshold in an optimistic, finite accounting model of two
historical invoices. It supplies no physical merge, joint native word, compiler,
controller, dirty-state restoration, tape bill or new kappa. The target `7/2000`
is an explicit benchmark above the frozen side roots, not a selected admission
threshold. The current selected record remains unchanged.

Additional fees can consume the positive margin. Restrictions on eligible roles
can raise the minimum. Repeated merges, splitting, altered targets, extra credits
or a different invoice are outside the theorem's threshold application. Native
and all-size multiplication obligations were not run. Independent human and
formal proof-kernel review are unclaimed.

The runtime is managed Python. The verifier's largest supplied side has fewer
than 100,000 jobs and its exhaustive oracle has fixed finite loops. Dynamic
integer, rational and collection allocations are bounded by this fixture;
Python cannot enforce allocation-free execution. Memoization is limited to 512
power bounds. Functions remain below 60 physical lines. These are the applicable
Power of Ten deviations, not changes to shared repository checks. The bounded
cache decorator and seven-entry control dispatch are standard-Python deviations
from the restrictions on metaprogramming and indirect calls.

## Sources and credit

The exact source is PR #5298 head
`e63b0a32ed2c021a8f4344e5aeb7e9123ff2eaef`,
`research/joint-supplier-average-ceiling/RESULT.json`.
`inputs/PR5298-RESULT.json` retains its bytes verbatim because this pending
source is not available from the package base history. The verifier authenticates
that retained file locally; no remote Git object or network access is required.
`SOURCES.json` binds the original card and selected record at the package base.
`TASK.json` records the external source URL, head and digest explicitly.

Mark / Matarener supplied the joint invoice, whole-job boundary and merge
examples. James Reed / jwr404 identified the scope correction. zxv and the
retained #4470 lineage supplied the complex invoice; ai-nanachi and #4814 on
#4760 supplied the BIT invoice. Ali Romman's #5341 supplies separate crossing
results, which are not required or replayed here. The retained Zhihao Chen,
RaD/hipotures, icekylinx and eumemic controller and moment lineage keeps its
credit. This package adds the optimal disjoint-pair rule and exact 406 threshold.

## Open next questions

Can a native child legally realize any of the threshold witness's three rank
pairs while retaining both arbitrary payloads and their returned state? This
decides whether the relaxed accounting witness has a physical interpretation.
Start with one `(72,63)` pair and write its complete producer/consumer and fee
contract. No such joint native contract is supplied here.

Can an explicit role-eligibility graph still admit 406 effective merges? First
derive its legal edges from one actual joint word, then solve the finite weighted
matching problem with all fees. The missing physical edge relation is the blocker.
