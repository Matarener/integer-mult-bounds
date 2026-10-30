# Exact delayed-entry defect and cleanup boundary

This is a finite exact linear-algebra certificate for the two words at PR4076
head `9744f9df268590295a9872b1952c695a678192b9`. It is not a proof of
the full multiplication theorem or a new exponent. Tekalign (`tekuuu`), with
substantial OpenAI Codex assistance; Apache-2.0.

Let `P0` be the old prefix through `restore`, before private-buffer cleanup,
and `PS` the same prefix with entries in S ⊆ {600,608,609} staged. These are
operators on all 632 live register fields and 91 independently dirty private
fields. Every field is an arbitrary vector in a common vector space. Native
symbols denote arbitrary invertible linear operators; their signed occurrences
are inverse pairs. No commutation, binary-only lift or zero dirt is assumed.

The independently computed exact identity, for **both providers**, is

```
(P_S - P_0) x =
  1_{600∈S} (e565/2 - e602) x600
  + (e417/2 - e610) (1_{608∈S} x608 + 1_{609∈S} x609).
```

Here `xr` is an original input field, not the field currently stored in r.
Every omitted row and coefficient is zero, including every nontrivial native
operator word. `CERTIFICATE.json` retains the complete sparse difference for
all eight subsets; all eight are also independently compared with sums of
singleton differences. Thus there are no mixed terms in this finite family.
The hybrid subsets are algebraic diagnostics, **not** admitted frame schedules.

For the triple the register-coefficient matrix has rank exactly two: the two
output vectors have disjoint support, the input forms x600 and x608+x609 are
independent, and the rows417/565, columns600/608 minor has determinant −1/4.
For D-dimensional fields the corresponding ordinary linear matrix has rank
2D, not two. This does not reduce the three physical entrance dimensions.
In maximum-register norm, the exact difference has induced norm2: every row
has coefficient sum at most2, attained by x608=x609 with all other inputs zero.
This is a finite boundary estimate, not a completed physical error bill.
The prefixes coincide precisely when x600=0 and x608+x609=0; arbitrary other
input fields remain free. This is a boundary identity, not a new caller contract.

## Why cleanup must still be checked

The old and new prefixes are not the same map. Their nonzero differences lie
in ordinary helper rows417,565,602,610. Each of the 91 restored-helper rows
is exactly its own original input at the cleanup boundary, no restored-helper
input leaks into another live row, and target rows already equal y+x.

For each subset, construct the non-target inverse by reversing ordinary A,
interleaved B/native events and restore, skipping target writes and mapping
each restored helper r to its independent private field r+704. ADD coefficients
negate, scales invert, and native symbols invert. This is exactly the projected
cleanup prescription, not an inverse of the whole prefix. For the two actual
source endpoints it is separately compared with every literal cleanup opcode.
The new checker then executes this generated tail for each subset on all723
independent input fields. Its exact final operator is identity on helpers,
sources and private fields, and y←y+x on all112 targets. In particular every
private field returns with its arbitrary initial value, with no live leakage.

## What the computation proves

`algebra.py` stores each register row in the rational group algebra of the
free group on native symbols. Each axpy is exact rational linear combination;
operator application appends one symbol; only adjacent inverses cancel.
Induction over the serialized gates gives the exact row represented after
every gate. Equality of the computed rows is therefore an exact identity in
that algebra, and substitution gives the identity for any invertible native
operators respecting the same inverse convention. This is an executable finite
certificate with a written soundness argument, **not** proof-kernel verification.

All twelve deletion and six release positions are recovered from the actual
interleaved operator sequences, with frames stripped and identity scales removed.
All other scalar sections, domain/dirty returns and complete native interfaces
are compared. Both actual words have unchanged native matrices and entrance/exit
frames, not merely matching binary ranks.

Twelve semantic controls/provider omit or negate each release and regenerate
its inverse cleanup. All fail the exact endpoint test, so stale cleanup is not
the cause. Four further source controls reject corrupted bytes and swapped provider inputs.
A separate raw-JSON evaluator executes both actual words and their **literal**
cleanup on six deterministic all-state vector assignments using noncommuting
invertible 2×2 rational shears. This finite specialization calibrates parser,
operator-order and correction conventions; it does not replace the exact proof.

## Limits

The extra entrance frames, recursive rank invoice, numerical rounding, source
access, native Gaussian phases/physical lowering, owner fill, precision, tape,
all-size and outer transfer remain separate obligations. The unchanged native
interface comparison is not a fresh native compiler audit. No new κ is claimed.
