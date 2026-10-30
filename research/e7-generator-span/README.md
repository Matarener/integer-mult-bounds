# Printed E7 generators

## Question

The rank-7 note prints `E7 = ⟨256, 128, 66, 36, 22, 8, 1⟩`. Do these vectors span the hyperplane of normal 7?

## Result

The seven vectors are linearly independent, so they span 128 vectors in `F2^9`. Their overlaps with 7 are even, even, odd, odd, even, even, odd. The odd generators are 66, 36 and 1. The hyperplane of vectors whose overlap with 7 is even has 256 points, and the span meets it in 64. The selected κ is unchanged.

## Boundary

This checks the printed generators. It does not rerun the obstruction census or rebuild the sets `R` and `H`. The stop rule is to record this intersection.

## Reproduce

```bash
python3.12 -B research/e7-generator-span/verify.py
python3.12 -B research/e7-generator-span/test_verify.py
```

## Open next questions

None. The span and the hyperplane are finite. Rerunning the obstruction census would leave this package.

## Credit

Marius-Paul Dumitrean (mdumitrean) printed the generators in PR #2979, where they are attributed to RossRichardson's PR #2918. The checker spans the generators and counts the even overlaps. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
