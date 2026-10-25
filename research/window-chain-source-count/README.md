# Even source calls on overlapping write windows

## Question

A dirty connector must be restored, so the number of complete source calls is even. How many source calls does a chain of length-two write windows need, and how many scalar gates does the six-output pilot use?

## Result

For one through ten outputs, windows `[i, i+1]` have hitting number `ceil(k/2)`. The even source-call count is twice that number rounded up. A direct enumeration of the `{0,1,2}` multisets agrees with the slot scan. At ten outputs the count is 6.

The two-window prices `(1, 9, 1)` have optimum 6, using one call at each end. One call in the shared slot plus the cheapest outside call costs 14. Two calls in the shared slot cost 22.

The six-output scalar source `(3, 6, 7)` and alternating readers `(1, 2, 4)` and `(3, 2, 4)` expand to 70 gates on the overlapping chain, 84 on the six disjoint slots, and 126 when every output is closed by itself. The return-to-origin head steps are 1456, 1572 and 1920. Each program delivers `A_i B x` and restores the connector. The selected κ is unchanged.

## Boundary

This counts these chains and expands this one scalar fixture. It does not rerun the 5,336-case domain census or adopt a supplier. The stop rule is to record these bills.

## Reproduce

```bash
python3.12 -B research/window-chain-source-count/verify.py
python3.12 -B research/window-chain-source-count/test_verify.py
```

## Open next questions

None. The chains and the scalar fixture are finite. The domain census would leave this package.

## Credit

Yuzhou Wang (yzhouwang) recorded the overlapping-window optimum in PR #3778. The connector and the disjoint comparison are credited there to Ross Richardson and woklerx. The checker recounts the chains and the six-output gates. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
