# Completed compression error

## Question

For every production precision `p >= 101`, is the completed compression error below two units of the `p` grid?

## Result

The stated sum is

```
sqrt(2) 2^(-p) + 2^(-16p) + 2^(-32p) + 2^(-42p) + 18 p 2^(-32768 p).
```

`99² = 9801 > 9800 = 2·70²`, so `sqrt(2) < 99/70` and the remaining room is `41/70` of a `p`-grid unit. For every integer `p >= 101` the other four terms are together strictly below that room: each is below `2^(-15p)`, and `4·2^(-15·101) < 41/70`. The coefficient `18p` stays below the exponential gap by induction from `p = 101`. The same comparison was evaluated directly for every precision from 101 through 200. The selected κ is unchanged.

## Boundary

This checks the completed error sum. It does not run the Gaussian core or the chirp consumer. The stop rule is to record this error sum.

## Reproduce

```bash
python3.12 -B research/compression-error-sum/verify.py
python3.12 -B research/compression-error-sum/test_verify.py
```

## Open next questions

None. The comparison holds for every production precision. The Gaussian core would leave this package.

## Credit

Jose Manuel (`jmbarrancoml`) recorded the completed error sum in PR #3851. The checker proves the comparison from `99/70`. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
