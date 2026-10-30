# Focused independent review of the symmetric 128-port extension

**No local algebra or newly added native-frame defect was found.** A fresh
run of `baseline/symmetric_extended.py`, with its output directed to this
review's separate directory, passes all 632 independent columns for both
orientations and both PR3734 providers. Its profile has rank mass 5070 in each
case; the reported scalar prefix ceilings are 124 bits forward and 128 bits
backward, below the retained 192-bit scalar cap.

That replay uses the author's endpoint interpreter. This review separately
walks the literal modern frame changes and every new Gaussian scalar event.
Every such event uses actual I or FULL operands; all ADDs are nonaliasing,
their coefficients are Gaussian dyadic, the query field is owned and reset,
and every native core endpoint frame agrees with the original canonical word.
The frame walk is implemented in `review_symmetric_extension.py` and records
its result in `symmetric-extension-review/INDEPENDENT-REVIEW.json`.

## Algebra and normalization

The normalization B is an invertible Gaussian-dyadic map on eligible I-entry,
FULL-exit helpers. Its exact endpoint is checked as

\[
HB=[4I\text{ on SX},\;8iI\text{ on TX}],
\]

and B followed by B^-1 is checked on all 632 columns. In the backward word,
B^-T before the omitted core and B^T afterward are the correct dual
normalizations for the bilinear block contract. They should not be replaced
by conjugate-transpose operators.

For Q=[R,4I,8iI], the decisive distinction is

\[
QQ^T=(56+16-64)I=8I,\qquad
QQ^*=(56+16+64)I=136I.
\]

Thus D=I-Q^TQ/4 is symmetric and satisfies D^2=I. It is not thereby unitary.
Multiplication by i is nevertheless an ordinary Gaussian scalar operation:
it swaps the real and imaginary components and changes one sign. It commutes
with the complex-linear native transformations when both operands have the
same frame, as the new frame walk verifies. Its cost and error amplification
must use the actual Gaussian scalar bound rather than a unitary norm assumption.

The complete local maps established by the replay are

\[
F(X,Y,h)=(DX,Y+DX,h),\qquad
B(X,Y,h)=(X-Y,DY,h),
\]

with 128 source and 128 target coordinates. The 376 arbitrary helpers are the
remaining 632−256 inputs; 32 previous helpers have become data ports.

The identities D^T=D and D^2=I do not say that this displayed B equals F^-T.
In block form, F^-T=[[D,−I],[0,I]], while B=[[I,−I],[0,D]]. Any later controller
must use the actual two endpoint maps or separately supply the companion its
global proof requires.

## Source authentication and canonical reproduction

**The source-pin issue requested by the first review is closed.** The final
producer rejects execution with assertions disabled, authenticates its modern
component source, checks the retained native receipt SHA, and checks all four
retained native files for each provider: the canonical word, local programs,
Clifford recipes, and residual adapters. The refreshed review checks those same
bytes before executing the producer.

From the workspace-shaped package root, one command regenerates the complete
review evidence without depending on pre-existing review output:

```sh
python3 -B recovered-involutory/review_symmetric_extension.py
```

The command pins producer SHA
`15f29c5a84e4b055668ff78bb6ec8c8e2d15aa8064b35832839a27a4ec205323`
and component SHA
`f6769f1ecd6b2e582748805b3afcf4c65824ba108ce7f23a4d011c45f8b724de`.
It executes the exact checked producer source bytes with the original input
paths and source path preserved. Only its in-memory output directory is
redirected to `symmetric-extension-review`. The fresh producer writes both
complete emitted words and its endpoint receipt there. The review then writes
`SOURCE.json`, authenticates the emitted payloads, and runs its separately
written literal-frame walk before writing `INDEPENDENT-REVIEW.json`.

This is one reproducible review command; the endpoint algebra replay still
uses the author's endpoint interpreter, while the new scalar-frame walk is
independently written. The fresh receipt reports 172250 real scalar primitives
forward and 181578 backward and includes integer numerator accumulators in
the scalar prefix bounds quoted above.

## Global boundary

The 16 additional port labels are zero. Their source entrance gauge is I and
their source and target terminal gauges are FULL. This finite local endpoint
does not satisfy the old norm-one port hypothesis, and it does not by itself
supply new global geometry, routed ownership, physical allocation, a complete
precision recurrence, or an improved kappa. Those remain separate obligations.

The review therefore accepts the stated finite Gaussian-dyadic component and
its frame placements, while preserving the author's explicit global scope
limit. It does not certify a complete supplier or provide a second independent
endpoint interpreter.

Prepared with substantial OpenAI Codex assistance under the user's direction.
The component author and original native/core suppliers retain attribution.
Apache-2.0.
