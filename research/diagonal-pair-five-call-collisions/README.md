# Five-call diagonal-pair collision obstruction

**All-group computer-assisted obstruction, restricted to width two over F2.
No new kappa.** In the formal rank-one-idempotent call model, a diagonal pair
of distinct targets, each requiring at least three labels, needs at least six
calls. For (xyx,yxy) satisfying these hypotheses, the direct six-call word
meets the bound.

[PROOF.md](PROOF.md) gives the exact scope, a symbolic five-call cancellation
example, and the soundness argument for the exhaustive finite refutation.
[verify.py](verify.py) checks every one of the 9,331 projector tuples of
length zero through five. It propagates common-prefix/suffix cancellation
jointly through the four group-algebra coefficient equations. Free invertible scalar basis changes are normalized by conjugation and
augmentation in the proof. The groups and label alphabets remain arbitrary; this is not evidence extrapolated
from a finite group census.

This resolves the width-two/F2 portion of Josie Elliston's #6048 open
question 1. That package's support-only relaxation admitted 20 four-call
and 938 five-call projector tuples. Its arbitrary subset-class assignment
omitted joint group-word consistency. This successor adds cancellation and
all coefficient equations, rather than repeating the free-group degree
control. Nick Petalas's #6038 established the earlier four-call xy/yx result.

## Reproduce

Standard-library Python 3.12; approximately two seconds per direct run:

```sh
python3 -B research/diagonal-pair-five-call-collisions/verify.py
python3 -O -B research/diagonal-pair-five-call-collisions/verify.py
python3 -B scripts/research_package.py --package research/diagonal-pair-five-call-collisions
```

Expected marker: `PASS_DIAGONAL_PAIR_FIVE_CALL_COLLISIONS`, with zero survivors
at every length. Registered controls include the six-call exact endpoint,
a reopened four-call support-only instance when cancellation is removed,
and a reopened two-call instance when short targets are allowed. Independent
controls authenticate every generated context rule and require the collision
solver itself to accept the known four- and six-call constructions.

The package has no runtime source dependencies. Exact predecessor proof and
README pins are provenance in SOURCES.json; their bytes are not imported or
modified. The verifier also runs directly in a Git-free source export.

## Open next questions

1. Does the six-call floor hold at larger widths over F2? It would remove the
   two-register restriction. First inspect whether the parity refutation can
   be replaced by a rank/corner argument; the six-projector inventory does
   not cover larger matrices.
2. Does it hold in odd characteristic or F4? It would address the remaining
   field scope of #6048's question. First derive coefficient-class constraints
   with nonbinary weights; even pairing is specific to F2 and is not valid
   unchanged over those fields.

Neither question authorizes another construction round or certifies a native
implementation. Conversion, restoration, tariffs, whole callers and the
selected multiplication frontier are outside this result.

## Credit

Prepared by JoyboyBrian with substantial OpenAI Codex assistance, Apache-2.0.
Josie Elliston (#6048, substantial Claude assistance) supplied the longer-pair
question, support-only counterexamples and group-free proof approach; Nick
Petalas (#6038) supplied the preceding all-group xy/yx theorem and corner
method; Wentao Li (#4089/#4093) supplied the rank-one-idempotent group-algebra
model, following Cinna Davis's A5 target (#2246). Their broader results are
not re-audited here. Source heads are pinned, and no frozen predecessor is
changed.
