# Adjacent reflections of the scaled E8 roots

## Question

Each adjacent pair of A8 coordinates determines a root. Does reflection through that root stay inside the scaled E8 alphabet, and does it swap the two corresponding label bits?

## Result

There are eight adjacent generators. Each reflection matrix is `4I - alpha alpha^T`. All 512 entries of the eight squares equal 16 on the diagonal and 0 off it, so each reflection is invertible over the half-integers.

Every one of the 120 lines is transported by every generator: 960 images. The image remains in the alphabet. Its label is the original label with the two adjacent bits exchanged when they differ. The integer formula `4 image = (4I - alpha alpha^T) row` holds for every coordinate. The selected κ is unchanged.

## Boundary

This checks these eight reflections. It does not enumerate the 130,305 character pairs. The stop rule is to record these reflections.

## Reproduce

```bash
python3.12 -B research/e8-reflection-transport/verify.py
python3.12 -B research/e8-reflection-transport/test_verify.py
```

## Open next questions

None. The eight generators and 120 lines are finite. The character-pair census would leave this package.

## Credit

conorholds recorded the reflection transport in PR #3755. The checker recomputes the eight adjacent actions on the scaled roots. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
