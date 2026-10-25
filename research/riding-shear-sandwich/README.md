# Riding shear sandwich

## Question

Place a bridge of coefficient `q` around one shear of the owner, and cancel it with the inverse bridge. How do the owner and the rider change?

## Result

On a forward shear, the owner's `Y` increases by `X_owner + q X_rider` and the rider's `Y` increases by `q` times that increment. The `X` wires are unchanged. On a reverse shear, the owner's `X` increases by `-Y_owner + q Y_rider` and the rider's `X` increases by `-q` times that increment. The `Y` wires are unchanged. Coefficient 0 is the owner's own shear.

This holds for every coefficient from −6 through 6 and every wire value from −8 through 8. There are 13 coefficients and 83,521 wire states. The selected κ is unchanged.

## Boundary

This checks one owner and one rider. It does not census bridge schedules or price an idle alphabet. The stop rule is to record this sandwich.

## Reproduce

```bash
python3.12 -B research/riding-shear-sandwich/verify.py
python3.12 -B research/riding-shear-sandwich/test_verify.py
```

## Open next questions

None. The coefficients and the wire values are finite. A schedule census would leave this package.

## Credit

Matarener recorded the bridge orientation around an owner shear in PR #3836. The checker applies both sandwiches. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
