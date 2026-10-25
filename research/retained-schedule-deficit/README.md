# Signed deficit of the retained full-target schedule

## Question

The retained pure recipe opens one pair per local stage and charges idle rank when a later pair is entered. For a full target on every port, how far is the rank mass from capacity?

## Result

For every pair count `K` from 1 through 24 the recipe has `L = 2K + 1` local stages. The idle ranks sum to `7 L (K - 1)`. With local ranks `{7: one port, 8: one port}` on each stage, the capacity minus the paid mass equals minus the product of the port count and the replica count. The rank-seven local profile `{7: two ports}` instead leaves a deficit equal to the live width `2 K`.

At the published point of 111 ports and 32 replicas, pair counts 2, 4 and 5 each have deficit `-3552`. The selected κ is unchanged.

## Boundary

This replays the pure recipe through these pair counts. It does not replay the 111 port Householder charts or the owned-scratch word. The stop rule is to record this deficit.

## Reproduce

```bash
python3.12 -B research/retained-schedule-deficit/verify.py
python3.12 -B research/retained-schedule-deficit/test_verify.py
```

## Open next questions

None. The pair counts are finite. The port charts would leave this package.

## Credit

Gonzalo-Mier recorded the retained schedule in PR #3772. The checker replays its pure recipe and sums the idle ranks. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
