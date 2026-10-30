# Record 13 exhausts one restricted helper-cut interface

## Result and exact scope

The exact historical pre-record-13 stage of [PR #5612](https://github.com/CrocSwap/integer-mult-bounds/pull/5612) has dyadic capacity
**exactly one** on the fixed support
$E=(57,81,92,224,225,234)$ at frame 267, after zero-based event 12626.
The already published record 13 channel attains that capacity. The residual
left module is zero, so this bounded test earns **no additional independent
channel, target credit, paid saving, P–T gain or kappa**.

The source is [PR #5612](https://github.com/CrocSwap/integer-mult-bounds/pull/5612) head
`faa9f6dbe6b8cc4a996d3edeca71823056453e1a`. Reconstruction applies the
published parent preparation, delayed preparation and exactly the first
12 splits. Its canonical stage SHA256 is
`0ba81142bc47457490996c88d88c74849c7648922ff696e496f95bfb7afcf801`.
This stage has 747 public inputs and 25,492 events. It precedes record 13
and later contact/source changes; no result is transferred to final [PR #5613](https://github.com/CrocSwap/integer-mult-bounds/pull/5613).

The helper group $H$ is the full original same-boundary non-main public group
of carrier 225, with boundary frames 3 and 127. Both fixed carriers 225 and
224 lie in that group and at the common cut frame. The replay-derived gates
check chart nesting, split ranks $(8,1)$, an empty owned cut, arbitrary-input
endpoints and the known normalized prefix/suffix channel before capacity.
This is a restricted source-bound ceiling, not a whole-bank or global no-go.

The complete fixed-caller invoice distinguishes actual and comparison data:

| Invoice | Paid jobs | Target fields | Status |
|---|---:|---:|---|
| Reconstructed pre-record-13 stage | 66,690 | 13,030 | Actual replay-derived bill |
| After the already published record 13 split | 66,690 | 13,048 | One-channel comparison |
| One additional optimistic channel | 66,690 | 13,066 | Unrealized comparison; not earned |

Paid and target rank masses are 241,268 and 242,028, with surplus 760.
The two comparison invoices preserve rank mass. They are not two newly
constructed successor words. The existing record 13 split is not refuted.

## Certificate and short proof

Work over $D=\mathbb Z[1/2]$, in the displayed order of $E$. Let $L$ be all
rows supported on $E$ whose prefix image is supported on $H$. Five stored
original independent prefix constraints, cleared by the unit denominator 2,
give $Cx^T=0$, where

$$
C=\begin{pmatrix}
-2&-2&2&-2&0&0\\
-2&-2&2&2&0&1\\
-2&2&2&-2&0&-1\\
2&-2&2&-2&2&0\\
2&-2&2&2&0&0
\end{pmatrix}.
$$

The first and fifth equations imply $x_4=-x_1$ and $x_3=x_2$. The second
then gives $x_6=4x_1$, the third gives $x_2=x_1$, and the fourth gives
$x_5=-2x_1$. Only powers of two are divided out. Hence

$$L\subseteq Dq,\qquad q=(1,1,1,-1,-2,4).$$

The source-bound known row is $a_0=q/4$, with prefix image $e_{227}$ in $H$.
Thus $q\in L$, giving $L=Dq$. The checker also verifies that every original
constraint annihilates the full saturated kernel, and checks integer
unimodular Smith transforms. The selected constraint diagonal is
$(1,2,2,4,4)$; its free column is $q$. The full right module has dimension 5.
The induced pairing is $(1,1,-1,-2,4)$, with unit Smith factor $(1)$.

Any normalized $t$-channel interface selects its left rows from the rank-one
module $L$, so its pairing cannot equal $I_t$ when $t\ge2$. The existing
right column $b_0=-2e_{225}$ satisfies $a_0b_0=1$, attaining capacity one.
Moreover $qb_0=4$ is a unit in $D$. If $x=sq$ is orthogonal to $b_0$, then
$4s=0$, hence $x=0$. The residual left module and residual capacity are zero.
Rescaling or rediscovering the old channel cannot produce a second credit.

The general capacity theorem and Smith implementation are credited to
released [PR #5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615) head `d914f77d948ac377bdb9823daca93d08913c3fa7`.
This contribution binds that classical rank/Smith argument to one concrete
historical source cut. It supplies neither a new general theorem nor an
independent human or proof-kernel acceptance.

## Reproduction and evidence

The original root-owned normal and optimized pair completed in
9.576948022993747 seconds, with 60,301,312 bytes sampled peak descendant RSS,
under the 150-second/512-MiB serial guard. Complete result bytes matched with
zero fields excluded. The result status is
`NO_ADDITIONAL_RESTRICTED_CHANNEL_STOP_THIS_OBJECT`.
Its SHA256 is
`ca4b71b20a3c1cf35aa0985cb6d4aeed05385bceaf66f1c1a5d5e8e21ad5db90`.

Five rejecting algebraic sanity controls address odd denominator, nonunit
transform, rational rank versus dyadic capacity, double credit and truncated
product width. One positive saturation control verifies a full kernel basis.
These are not a source-mutation campaign or independent physical experiments.
Static v2 review and the post-result readable proof are preserved in `reviews/`.
The latter inspected stored evidence without rerunning reconstruction or Smith.

```sh
python3 -B scripts/research_package.py --package research/p104-record13-capacity-ceiling
```

`VERIFY.json` registers normal and optimized wrappers. Each authenticates the
whole payload, all 49 original request pins and all 42 external inputs before
launching the unchanged v2 checker in a private isolated child. The original
relative tree is retained under `capsule/`; its root replaces the original
project root, with no source-path text rewrite or algorithm change. The
original absolute guard command is preserved as provenance and is not invoked.

The child repeats only the originally authorized reconstruction, sole endpoint
replay, known-channel gate and restricted capacity certificate. It does not
invoke full source verifiers, native/framework routines, pricing or other cuts.
The complete 24-file source export remains intact because its hashes are part
of the original closure. Uncalled sources and archives are not execution authority.
Version 1 is retained as explicitly **unrun provenance** and is never executed.

For a relocated, read-only, Git-free export, including an empty PATH:

```sh
/usr/bin/python3 -I -O -B research/p104-record13-capacity-ceiling/verify.py
```

Expected marker: `PASS_P104_RECORD13_RESTRICTED_CAPACITY_CEILING`.
Portable checks are **UNRUN_BY_PREPARER** and remain separate from the
completed original run. Each child has a 60-second timeout and 512-MiB
address-space bound. Root alone performs validation under the shared guard;
no retries, cap increases or source repins follow a failure.

## Sources and credit

The package preserves the original request, acceptance, runner/checker, inputs,
full result pair, guard/runner receipts, v2 review and post-result proof.
`CAPSULE-MAP.json` records every original-path-to-internal-path binding.
All runtime sources are internal committed bytes; no network, foreign Git
object or writable source package is needed. Publication uses available
ancestor base `32890bc5de034ab8fc93ac88ead7279a6a416d04`, distinct from the
fresh canonical main `6cf7a683f447b9f1e2333791907fd92be5009a63`.
The sealed publication gate in `presentation/` clears this exact restricted
ceiling within its stated bounded coverage; no global novelty claim follows.

Credit Ali Romman for [PR #5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599),
[PR #5602](https://github.com/CrocSwap/integer-mult-bounds/pull/5602) and
[PR #5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615) and the source-word lineage;
flyingviper for [PR #5612](https://github.com/CrocSwap/integer-mult-bounds/pull/5612) and
[PR #5608](https://github.com/CrocSwap/integer-mult-bounds/pull/5608);
Hexapode for [PR #5565](https://github.com/CrocSwap/integer-mult-bounds/pull/5565); and all retained
private-word, controller, compiler, native, precision and analytic contributors.
The rank and Smith-normal-form mathematics is classical. The bounded
source-bound qualification, static review and portable packaging were prepared
for Chris R/Clear1nsight with substantial OpenAI Codex/Astra assistance.
Apache-2.0 notices and source-specific attribution remain unchanged.

No new physical basis/split program, native all-width phases, ordinary cost
cap, complete compiler/outer/BIT admission or full multiplication theorem is
claimed. Those positive realization obligations do not weaken the negative
rank-one upper bound within this precisely fixed interface.

The latest complete author comparison is [PR #5627](https://github.com/CrocSwap/integer-mult-bounds/pull/5627) head
`ed4dc88a09a7d201971f6603b8c2074e95dd9c32`, claiming conditional
$\kappa=.00310440546$, tested $.003104405465$, with 66,546 paid jobs
and 12,958 target fields. Its hosted run 40247590574 was recorded successful;
it is not selected or independently admitted. It removes 72 H5 from both
paid and target invoices, preserving the signed recursive moment; the small
endpoint gain concerns funding/headroom, not a new raw crossing.

[PR #5627](https://github.com/CrocSwap/integer-mult-bounds/pull/5627) repeats the **same literal** pivot 225/frame 267 $a,b,c,d$ witness,
but at cut 12603 on a different nine-split changed-boundary word. Neither
that witness nor the split method is claimed here. Our contribution is the
exhausted restricted module at the exact historical pre-record-13 stage.
There is no transfer of this ceiling to [PR #5627](https://github.com/CrocSwap/integer-mult-bounds/pull/5627), final [PR #5613](https://github.com/CrocSwap/integer-mult-bounds/pull/5613) or another
support. `CURRENT-CONTEXT.json` preserves exact comparison source links,
Git blobs and the fresh bounded overlap decision.

## Open next questions

- No further construction is justified on this unchanged $E_6$ object: its
  published channel exhausts the restricted interface. Do not automatically
  scan more vectors, rescale the known pair or repeat the same test.
- A larger support, different cut, helper group, source or changed boundary
  would be a new object. Its relevance is whether the rank-one constraint
  changes; the first step is a fresh source-bound nomination and ownership
  gate. This package grants no scan or construction authority.
- Independent human or formal review can inspect the five-row elimination,
  known channel and stage-to-constraint binding. The blocker is a separate
  review or formalization, not another execution of the same certificate.
