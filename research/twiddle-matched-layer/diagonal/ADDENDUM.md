# Published fixed-diagonal pass joined to the matched layer

This is a source-relative addendum to the frozen matched-width layer proof.
It incorporates Sagar Thakrar's subsequently published [PR #3617](https://github.com/CrocSwap/integer-mult-bounds/pull/3617)
at `4bf091f415d6470b60a5062a08b0a47e5b12dbd7`. The original seventeen-file
layer component remains unchanged. The new bounded check runs the unchanged
complete diagonal implementation between explicitly unpriced arithmetic
operations for the normalized butterfly, rounding, and layout. It does not
implement a physical full layer.

## Exactly which previously conditional work is now supplied

The published successful-return theorem assumes a complete cube already in
the specified named-slot order, matching framed inputs and capacities,
distinct physical backing storage, and representable requested signed
negations. For one fixed round `h`, it supplies all of the following:

- Encoded full-wrap enumeration of every actual physical record address.
- The actual PR #3593 header passed to the actual PR #3611 packet consumer.
- Framed extraction and assembly of every record at its original position.
- Paid counter, header, packet and output rearming on the same physical tapes
  **within that fixed diagonal pass**.
- Preservation of the borrowed full source and descriptors, complete owned
  output, returned heads, and blank auxiliary data on successful completion.

With `N = 2^A`, `r = 2^ell`, and signed width `w`, the source proves

\[
T_{\mathrm{diag}}=O\!\left(N(rw+A+p^3)\right).
\]

Its 38 roles include both full streams; they are not auxiliary-only roles.
Writing `B = 2rw`, its exact capacity is

\[
C_{\mathrm{producer}}+2N(B+2)+4B+2w+A+3\ell+32.
\]

Allocation and valid framed-source admission remain the source premises.
The recorded tariff includes its constructor's counter initialization,
runtime primitive actions, explicit control/data gates, and stream returns;
it is not the complete enclosing caller's preparation bill.

The full `DiagonalPass` object is itself **one-shot**. Its successful
within-pass reuse does not establish a reusable all-round controller.

## Conditional normalized-round composition

Let `K = floor((d-1)^(1/500))` and use the changed named-slot layout of the
frozen proof. All nontrivial source-band premises, exceptional elementary
branches and active-root API obligations of that proof remain in force.
For a common round, use its repaired active-root extent and offset

\[
g=d-1,\quad n_P=a+gb+jgK,\quad
n_S=(q-j-1)gK,\quad \rho=(h-b)\bmod K,
\]

so that `n_P + gK + n_S = A` and the selected physical bit positions are
`n_S + rho + tK`, for `0 <= t < g`. The top/bottom elementary rounds use
their named singleton positions. These descriptors concern the arithmetic
target; the unchanged active-root/outer constructor is not thereby made
API-compatible.

Write `H_h` for the normalized tensor butterfly, `Q_p` for componentwise
truncation toward zero onto the `p`-grid, and `J_h^-`, `J_h^+` for the two
signed polynomial diagonals. The forward and opposite completed-round
targets are respectively

\[
J_h^- Q_p H_h,\qquad Q_p H_h J_h^+.
\]

For the forward call, apply `Q_p` **before** encoding the source packet.
This is exact because every `J_h` is a signed coordinate permutation and
`J_h Q_p = Q_p J_h`. An unrounded off-grid `H_h` intermediate is not a
same-width signed-integer input to the packet consumer.

Suppose the initial coefficient of each packet lies in the unit disk on
the `p`-grid. A normalized butterfly coefficient is an average of signed
input coefficients, hence still lies in that disk. Truncating the real and
imaginary components toward zero cannot increase its magnitude. A signed
polynomial rotation only permutes or negates whole Gaussian coefficients.
Induction over every forward or opposite round therefore preserves both
the disk and grid. Consequently `w = p + 2` suffices: every component
numerator has magnitude at most `2^p`, whereas the forbidden signed minimum
is `-2^(p+1)` and cannot occur. The one-packet width implication is already
credited to PR #3611; the application here is the complete-round induction.

Under these hypotheses the new published diagonal implements the required
`J_h` on every packet. It therefore composes with a correctly supplied
`H_h/Q_p` caller. This proves the exact conditional semantic join; it does
not prove that an approximate or differently framed physical root already
has the required return contract.

## Updated complete-round cost status

Let `M = ell - 1 + 1_{a>0}` be the number of retained round levels in one
direction. The fixed-diagonal part over those levels is now supplied by
the published source, with summed source tariff

\[
O\!\left(MN(rw+A+p^3)\right).
\]

For the actual retained long-record bands, `A = O(p)`, `w = p+2`, and
`r` eventually dominates every fixed polynomial in `p`. Thus this term is
`O(MNrp)`. With `T = Nr` and `M <= ell`, it is absorbed by the retained
layer term `O(Tp ell g^alpha log p)` when `g >= 1` and `p` is in the
nontrivial admitted range. This absorption changes constants; it is not
an unchanged exact finite tariff. The old outer exponent
`tau = 99830289/10^8` and its narrower bottleneck remain unchanged.

The remainder of the earlier `Q` obligation still includes:

| Required caller work | Status after this addendum |
|---|---|
| Fixed-h address traversal, packet extraction/assembly, packet reuse, head returns | Supplied by PR #3617 under its stated input and successful-return premises |
| Initial `L` placement and complete framed-input construction | Still needs the actual physical caller and bill |
| Active root or elementary butterfly, MSB/LSB bridge, and `Q_p` return | Still conditional; this check uses arithmetic oracles |
| Changes of `h`, descriptor preparation, whole-output consumption/reset, and bounded reuse across round lifetimes | Still needs an enclosing schedule; each source full pass is one-shot |
| Fixed simultaneous stock and a bounded collection of live full-cube buffers | Still an enclosing caller obligation; 38 roles per stage is not 38 roles globally |
| Truncated domains, spectators, recursive precision/error, and complete multiplication invoice | Unchanged obligations |

The published physical support router PR #3619 is adjacent current work,
but no composition with it is asserted or executed here.

## Bounded executable evidence

The new checker imports the three unchanged execution bodies directly and
authenticates all twelve retained PR #3617 package files against their
published Git blob IDs, SHA-256 digests and byte lengths. The arithmetic
component is separately byte-bound to the unchanged frozen layer checker.
It does not invoke the predecessor's large six-cube replay.

| Geometry | Actual diagonal packets in positive schedules | Completed forward/opposite round comparisons |
|---|---:|---:|
| `ell=3`, three short axes, matched `K=1` | 256 | 4 |
| `ell=4`, one long axis, `K=2`, including top and bottom elementary rounds | 128 | 8 |

All twelve returned rounds agree with the independent explicit tensor
formula in original axis order: 4,096 Gaussian coefficient comparisons.
The local examples use `p=4`, `w=6`; they verify the local grid/width
interface, not the enormous production `p=6b` parameter domain. The old
literal executable caps and the frozen layer's production-width gap remain.

The twelve actual diagonal executions record a combined source action
tariff of **19,566,850**, including constructor counter work. Each has
exactly 38 distinct physical roles, preserved borrowed bytes, returned
heads, blank private data, fixed capacities and no runtime tape replacement.
The two fixture families use 13,373--13,396 and 7,419--7,488 cells per stage,
respectively, including both full streams. These are stage measurements;
the arithmetic H/Q/layout and host fixture serialization are not charged.

A further actual 64-packet pass supplies a negative control: the old
`K=2` descriptor on the matched `K=1` physical cube disagrees with the
required completed-round output at `(record, coefficient)` positions
`(48,0), (48,4), (56,0), (56,4)`. This wrong-descriptor pass costs
3,331,410 source actions and is excluded from the positive invoice.
An off-grid numerator is rejected before encoding. A second full-pass
invocation rejects with `one-shot full pass` after each stage and preserves
the returned state.

Each positive or control pass is a **fresh admitted stage instance**.
This is a checker implementation choice, not a physical all-round
allocation or reuse construction. The result upgrades the available
fixed-diagonal endpoint and cost evidence while retaining the remaining
caller obligations in the table above.

## Reproduce and credit

From this packaged addendum directory, with the unchanged original checker
in its parent directory:

```sh
python3 -I -B check_3617_join.py --layer-component ../check_join.py
python3 -I -O -B check_3617_join.py --layer-component ../check_join.py
```

The CLI emits a deterministic receipt. Publication must bind it with the
package's strict typed receipt and source-inventory checks; ordinary Python
JSON-value equality is not a substitute for strict type comparison.

Sagar Thakrar supplies PR #3617's encoded fixed-diagonal pass and PR #3611's
signed packet consumer. Nick Petalas supplies PR #3593's encoded producer,
its PR #3582/#3590 lineage, and the earlier layer/interface work. The
retained transform sources supply the layout and diagonal identities.
The original matched-width proof preserves Jose Manuel's PR #2298/#3599,
Nick Petalas's PR #3493 and Hiroki Kumazaki's PR #3576 factory/rate lineage.
This addendum's bounded
caller join and obligation update were prepared for Clear1nsight with
substantial OpenAI Codex assistance. Same-session AI reviews are not
independent human acceptance or formal-kernel proof. No frontier change
or achieved multiplication exponent is claimed.
