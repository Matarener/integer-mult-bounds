# One-pair alternating shears

## Question

Forward sends `(X, Y)` to `(X, X+Y)` and reverse sends `(X, Y)` to `(X-Y, Y)`. What do the two alternating triples do, and how does the final exchange `(X, Y)` to `(Y, -X)` act on them?

## Result

Both triples, forward-reverse-forward and reverse-forward-reverse, equal the map `(X, Y)` to `(-Y, X)`. The final exchange is its inverse, so either triple followed by the exchange restores the pair. This holds for every coordinate from −128 through 128, which is 66,049 points, and the two-by-two products agree. The selected κ is unchanged.

## Boundary

This checks one pair. It does not census bridge schedules, insert a bridge, or price an idle alphabet. The stop rule is to record this exchange.

## Reproduce

```bash
python3.12 -B research/alternating-shear-exchange/verify.py
python3.12 -B research/alternating-shear-exchange/test_verify.py
```

## Open next questions

None. The coordinate box and the two triples are finite. A schedule census would leave this package.

## Credit

Matarener recorded the shears and the final exchange in PR #3836. The checker multiplies the maps and applies them to the coordinate box. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
