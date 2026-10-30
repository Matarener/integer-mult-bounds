# Bit budget for a cleared minor

## Question

After clearing B-bit denominators in a k-by-k matrix, how many bits does the published budget allow for a minor?

## Result

Each cleared entry is strictly below `2^{k B}`, so it fits in the coarse budget `M = (k+1)B` bits. The Hadamard number `k!(2^M-1)^k` is an upper bound on the absolute value of any minor. For every order and entry budget from 1 through 20, that integer's bit length is at most

```
D = k(k+1)B + k ceil(log2 k) + 2.
```

There are 400 such pairs. For order 2 and budget 1, every determinant with entries from −3 through 3 also fits: 2,401 determinants, and the largest absolute value 18 has bit length 5 against `D = 10`. The selected κ is unchanged.

## Boundary

This checks the Hadamard comparison and these small determinants. It does not run the Gaussian core or the word multiplier. The stop rule is to record this budget.

## Reproduce

```bash
python3.12 -B research/minor-bit-budget/verify.py
python3.12 -B research/minor-bit-budget/test_verify.py
```

## Open next questions

None. The Hadamard comparison settles the budget on this range. The Gaussian core would leave this package.

## Credit

Jose Manuel (`jmbarrancoml`) recorded the minor bit budget in PR #3851. The checker compares it with the Hadamard number. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
