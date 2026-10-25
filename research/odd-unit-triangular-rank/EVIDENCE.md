# Verification evidence

I used CPython 3.12.13 and its standard library. I passed the primary
replay under `-I -O -Werror -B`, the independent vector-coordinate replay
under `-I -Werror -B`, and the nine-control replay under optimized Python.
I also passed the registered replay and metadata/source-pin
validation. I record committed-byte/history and hosted status in the PR.

The primary and independent engines reconstruct 136 and 512 admissible
types, and selectors of 21 and 48 types. They agree on these canonical
selector SHA256 values:

```text
h5 96726988127c29a14030b175bada688bfc3eb574dcb5fed32ad973abe01f423f
h6 7422ceb1f7f0332c25ebaea83c18cf98bda5056536a73373b27ecde3c32d60be
```

I checked all 1,407 upper-triangular seed-selector positions and their
transposed reverse-order selectors. The primary
engine also checks repeated-port minors of orders 28 and 64 over Q,
F2, F3 and F5. Both engines check nonuniform multiplicities, including
missing types. The primary weighted fixtures have 342 and 1,282 port
occurrences; the independent fixtures have 395 and 1,470.

I reconstructed the retained 256-port rank-16 projector through its
16-by-32/32-by-16 exact factor identity after clearing denominator eight.
Its scalar factor fails the complete fitting condition, as expected.
I did not execute the original FLINT search or claim that a single
projector completes a unit.

The controls reject zero fitting diagonals, collapsed duplicate ports,
invalid multiplicities/types and a broken triangular selector. They also
exhibit the missing h5 special orbit, the failure of idempotency after
normalizing a nonidentity diagonal, correct removal of a zero-charge
term, and rejection of an altered archive by the actual optimized CLI.

The arbitrary-multiplicity and field quantifiers follow from PROOF.md.
Finite replays do not exhaust those domains. Source-analysis agents
checked the proof and its scope separately during this AI-assisted
session; I claim no independent human or formal-kernel review.

For the general-dimensional extension, I checked every admissible type,
selector entry and generated orbit for dimensions two through eight:
10,964 types and 451 selected types across those seven fixtures. The
uniform fractions are 1/2, 1/3, 1/4, 1/9, 3/32, 11/270 and 1/32. I also
checked exact odd-fraction comparisons through dimension 49. These are
finite corroboration; the affine-flag and symplectic arguments prove the
general formulas. The original h5/h6 checker implementations remain
separate from this extension checker.

I ran the card's existing ceiling control separately and obtained
`PASS_COMPLEX_LOCAL_WORD_CEILING`. It only orients the selected-word
baseline. I did not run the full selected supplier replay or change its
frontier. The new unit bound uses its own declared fitting/copy model.
