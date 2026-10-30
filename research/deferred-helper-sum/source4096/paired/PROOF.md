# Fixed receiver obstruction for helpers 608 and 609

The sum/difference direction cancels the **rewrite defect** in the pinned
PR4076 words, but it does not isolate a restored helper in the complete forward
word. This remains impossible when the terminal change may use all four actual
outward receivers, with the helper input support fixed to `{608,609}`.

## Contract, pins and cuts

The source is Rohan Arun's PR4076 at
`9744f9df268590295a9872b1952c695a678192b9`, including its base and extra providers.
The checker authenticates the eight retained source files by byte length,
SHA256 and Git blob. Its standard-library interpreter imports or executes no
source Python. The interpretation of BORROW-WORD was read from Sagar Thakrar's
Apache-2.0 `audit_core.py`; the source proof credits the inherited construction
and audit lineage. This analysis was prepared with substantial OpenAI Codex
assistance. It is an exact coefficient computation and a written algebraic
argument, not independent human review or a formal-kernel theorem.

Work over the dyadic scalar ring `D=Z[1/2]`, or its extension `Q`. Warp operators
are invertible independent noncommuting symbols, so coefficients are checked in
`D[F_72]`, reducing only adjacent inverse pairs. The resulting displayed rows and
columns are scalar identities, hence survive any specialization to invertible
linear warp operators over a characteristic-zero module. Binary frame spaces
are a separate `F_2^9` structure.

Every current non-target coordinate is arbitrary, including every helper.
The full forward word has 632 live coordinates; 112 are targets and 520 are
non-targets. Its 91 inherited private buffers are separate arbitrary dirty
coordinates used in cleanup; they do not occur in this forward word. No value
is assumed zero. The matrix `M` is the complete invertible non-target forward
operator through `restore`, immediately before inverse cleanup. Target writes,
wrappers and corrections are checked separately. The literal cleanup is not
part of `M`; including it would erase exactly the forward dependency being
tested.

There is a potentially misleading reuse of the number 10535 across staged
source records. The following three exact **NEW-word** boundaries are all checked.
Indices count zero-based events in the sequence of initial corrections,
precondition, compensation, A, cut, B with native warps inserted before their
declared B positions, and restore. A cut is immediately before its event.

* The physical predecessor OLD event 10535 is before `B[314]`, `3 -= 554`.
  Deleting the twelve early target reads from helpers 600, 608 and 609 maps it
  to NEW event **10523**, before `B[302]`, the same operator `3 -= 554`.
  Prefix operator equality is checked exactly; optimized scalar frame
  annotations are allowed to differ.
* Helper609's record uses numeric cut10535 **after the608 edit**. At this
  boundary only the four early608 reads have been deleted; its first release
  is later. Thus this record refers to OLD event10539, before `B[318]`,
  `181 += 397`. Deleting all twelve early reads maps it to NEW event
  **10527**, before `B[306]`, the same operator. The prefix and sequential
  cut-length identities are checked exactly.
* Literal NEW event **10535** is before `B[314]`, `161 -= 34/2`.

None of these cuts is a native warp boundary. The preceding native warps 71 and 72
occur at NEW B positions 238 and 241 on registers 401 and 403. The helpers'
first actual access is NEW event 10609, `B[388]: 121 += 609/2`.
Thus both helpers are available at the same actual entrance frame
`E=span{97,45}=span{76,45}`, of dimension 2, at all three cuts.

For each cut `c`, the checker computes the suffix operator `M_c` on an
**arbitrary current non-target state**. It independently verifies all displayed
columns and inverse rows below for `M`, `M_10523`, `M_10527` and `M_10535`, in both providers.
It also checks each inverse reader by the complete pullback
`(e_h^T M_c^-1) M_c=e_h^T`, over every current input coordinate and operator word.
The suffix inverse-row result is not inferred from the helpers being idle.

## Complete forward columns and two-helper obstruction

Let `H={608,609}`. In each of the eight covered operator instances,

```
M e608 = e608 + (1/2)e417 - (1/2)e421 - e610,
M e609 = e609 + (1/2)e417 - (1/2)e419 - e610.
```

There are no omitted output terms, scalar or noncommuting. For
`v=a e608+b e609`, the outward rows 421 and 419 are respectively `-a/2`
and `-b/2`. Their coefficient minor has determinant `1/4`, a unit in `D`.
Consequently `Mv` can be supported on H only for `v=0`. Invertible scalar
entrance and terminal changes supported on H cannot isolate any restored
coordinate: a terminal change supported on H leaves these outward rows fixed.

In particular,

```
M(e608-e609) = e608-e609 + (1/2)e419 - (1/2)e421.
```

The difference cancels the shared 417/610 release direction while retaining
two distinct outward receivers. For comparison, subtracting the OLD and NEW
full columns yields only

```
(M_NEW-M_OLD)(a e608+b e609)
    = (a+b)((1/2)e417-e610).
```

This exact rank-one rewrite difference is not the full outward map, whose
restriction to the pair has rank two.

## Allowing all existing outward receivers still fails

Now allow the terminal change on
`R={608,609,417,419,421,610}`, while retaining input support H.
The complete inverse rows, in every covered full or suffix instance, are

```
e608^T M^-1 = 2e342^T + 2e356^T + (1/2)e410^T
             - e417^T - e419^T - e421^T
             + (1/2)e608^T - (1/2)e609^T
             - (1/2)e610^T - e612^T,

e609^T M^-1 = -e276^T - e292^T + (1/2)e410^T
             + e417^T - e419^T + e421^T
             + (1/2)e608^T + (1/2)e609^T
             + (1/2)e610^T - e612^T.
```

Suppose a terminal reader alpha is supported on R and `u=alpha M` is a scalar
row supported on H. Write `u=a e608^T+b e609^T`. Invertibility gives

```
alpha = a(e608^T M^-1) + b(e609^T M^-1).
```

Its coefficients at 342 and 276 are `2a` and `-b`. Both coordinates lie
outside R, so `a=b=0`, and then `alpha=0`. This is a unit-minor obstruction,
of determinant `-2`, and excludes every nonzero such reader, not just one
chosen sum/difference pairing.

For completeness the paired-extraction equations are

```
S e_h=v,       u S=e_h^T,
T y=e_h,       e_h^T T=alpha,
y=Mv,         u=alpha M,       u v=alpha y=1.
```

Here S is invertible and acts only on H, and T is invertible and acts only on
R. If `(TMS)e_h=e_h` and `e_h^T(TMS)=e_h^T`, these equations follow with
`v=S e_h`, `y=Mv`, `alpha=e_h^T T` and `u=e_h^T S^-1`.
The preceding calculation forces `alpha y=0`, contradicting the required 1.
Therefore no such paired S,T exist, for any scalar `v` supported on H.

## Target map, costs and exact limits

The full target block on both helper inputs is zero. It is also zero for all three
covered suffix boundaries. The inherited zero-frame compensation and operator
corrections never read either helper, as the checker verifies directly. Thus
there is no hidden target-compensation term that restores the failed pair:
the obstruction lies in the non-target forward and inverse cones. An entrance
change would still require transforming the entire changed forward word and
its target map; equality of the rewrite defect alone does not supply that word.

For both helpers the actual inherited terminal frame is FULL, of dimension 9,
and their entrance frame E has dimension 2. Their physical frame residual is
`T_FULL T_E^-1`, with inherited width `9-2=7` each. Neither obstruction supplies
a replacement paired endpoint. The accepted local construction is therefore
unchanged: **no decrement** to helper width, local rank histogram, private-buffer
count, stock, owner remainder or complete recursive moment is justified here.
There are no new gates to invoice. Merely combining two scalar releases may
change gate count without establishing any of these recursive-cost changes.

This result excludes scalar entrance changes on H and terminal changes on R
at the stated full/suffix boundaries of the pinned two words. It does not
exclude a changed middle word, additional source access, a larger terminal
support, a different intermediate terminal cut, or a non-scalar interface.
For example, any nonzero eligible reader coefficient on 608 forces both 342
and 356 into its inverse support; any on 609 forces both 276 and 292.
Those are necessary newly affected supports, not a priced construction.

No native Clifford phases, chronological owner rearrangement, new private-buffer
interface, whole-word supplier admission or inherited universal/all-size
obligation has been changed or certified. No new kappa or selected-frontier
improvement is claimed. The separate release checker tests the scalar shared-release rewrite's
complete frame invoice; that is a different, narrower possibility.

## Reproduction and controls

```
python3.12 -I -B research/shared-staged-helper-interface/paired/verify.py --source research/shared-staged-helper-interface/source4076
python3.12 -I -O -B research/shared-staged-helper-interface/paired/verify.py --source research/shared-staged-helper-interface/source4076
```

The explicit failure checks survive `-O`. Both providers pass complete pair
columns, complete inverse rows, all-coordinate reader pullbacks, all three cut
bindings, target columns and correction-access checks. Five controls per
provider reject an omitted outward421 coefficient, an omitted inverse342
coefficient, a receiver-only projection of the inverse reader, the falsely
restored difference direction, and an off-by-one physical cut. They test the
algebra and cut predicates, without modifying any frozen source bytes.
