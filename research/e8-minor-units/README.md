# Half-integer units among the published E8 minors

## Question

The one-coset certificate lists eight root lines for nine characters and for each forbidden pair profile. Are those 8×8 minors units over the half-integers?

## Result

The A8 alphabet has 120 roots, each of sum zero and squared length 18. The standard E8 roots, scaled by two, match them through the eight-coordinate star. There are 192 ordered pair profiles with nine coordinates, and 100 of them are forbidden by the published parity rule.

Each of the 109 listed minors has a nonzero determinant, and every absolute value lies in {256, 512, 1024, 2048}. Each is therefore a unit over the half-integers. The selected rows meet the stated character supports. The selected κ is unchanged.

## Boundary

This recomputes these published minors. It does not enumerate the 130,305 character pairs or rebuild the sparse-pair census. The stop rule is to record these minors.

## Reproduce

```bash
python3.12 -B research/e8-minor-units/verify.py
python3.12 -B research/e8-minor-units/test_verify.py
```

## Open next questions

None. The published witnesses are finite. The character-pair census would leave this package.

## Credit

conorholds recorded the witnesses in PR #3755. The root alphabet is credited there to the earlier E8 model. The checker recomputes the minors from the scaled roots. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
