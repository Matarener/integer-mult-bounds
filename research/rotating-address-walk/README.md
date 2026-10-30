# Six-stage rotating address walk

## Question

A rotating word reads one active axis, moves both banks, and replaces the axes that leave the core. After six stages, where is the spectator, and how does the rank mass compare with the closed dimension?

## Result

The spectator axes are 1, 8, 15, 22, 29 and 36. The walk closes at dimension 43, with the source bank back in role 0. The moves have ranks `{1: 6, 6: 6, 7: 6}` and mass 84. Twice the dimension is 86. The first bank ends on every axis except axis 0. The second bank ends on every axis except axis 36. XORing axes 0 and 36 into that mask puts it on the same endpoint as the first bank. The two banks stay on distinct scalar identities. The selected κ is unchanged.

## Boundary

This replays this six-stage walk. It does not replay the 111 port charts or the 120 root lines. The stop rule is to record this walk.

## Reproduce

```bash
python3.12 -B research/rotating-address-walk/verify.py
python3.12 -B research/rotating-address-walk/test_verify.py
```

## Open next questions

None. The six stages are finite. The port charts and the root-line census would leave this package.

## Credit

Gonzalo-Mier recorded the rotating walk in PR #3772. The checker replays the six coordinate stages. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
