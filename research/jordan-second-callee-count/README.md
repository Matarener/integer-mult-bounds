# Two-dimensional Jordan first map: solved filtered callee count

This package resolves the two-dimensional nonsemisimple starting case of
the nonscalar counting question in Nick Petalas's PR5228. It does not close
that question for arbitrary rational canonical data.

For P=J_2(lambda) over F_q with lambda nonzero, the number of optimal
invertible second maps in the fixed ordinary wrapper is:

| Condition | Count |
| --- | ---: |
| lambda^2=1 | 1 |
| lambda^2!=1 and lambda^2=-1 | q^2 |
| lambda^2!=1 and lambda^2!=-1 | q(q-1) |

For lambda^2!=1 the parameters are Q=P+(P^2-I)S with S^2=0. Write
S=[[a,b],[c,-a]], a^2+bc=0. The determinant is exactly
lambda^2+(lambda^2+1)c. Each c has q square-zero preimages, giving both the
count and a complete description of singular rejections.

Examples: over F4 both eligible lambda give 12 optimal maps; over F5,
lambda=2,3 both give 25; over F7, lambda=2,3,4,5 each give 42. These examples
also show why the exceptional branch must be retained.

See [PROOF.md](PROOF.md) for the all-field proof and predecessor credit.

## Reproduce

Standard library only; Python 3.12 or newer:

```sh
python3 -I -W error -B research/jordan-second-callee-count/verify.py
python3 -I -O -W error -B research/jordan-second-callee-count/verify.py
```

The script prints a generated JSON receipt and writes no files. All checks
use explicit exceptions and remain active under Python -O.

The fields are q=2,3,4,5,7,8,9,11,13,16. Polynomial-basis extension fields
are used for nonprime q; these are not integers modulo q. The script verifies
the finite field tables, enumerates every 2x2 matrix to find S^2=0 without
using the claimed parameterization, then compares both sets and all
determinant fibers. For each regular lambda it checks the rejection family
and the accepted count. For every q<=9 and every nonzero lambda, it separately
enumerates all invertible Q and runs the six literal wrapper operations on
all four basis inputs. The resulting error-rank-optimal set must equal the
predicted set, including the lambda^2=1 boundary. This second path does not
use the block-matrix reduction to calculate the wrapper error rank.

`VALIDATION.json` records the actual interpreter and completed runs.
`SOURCES.json` records the pinned predecessor source. The predecessor documents are pinned at their canonical repository paths;
all predecessor attribution is retained in PROOF.md.

## Open next questions

The next narrow target is J_3(lambda); arbitrary block structures remain open.
See PROOF.md for the rank-one starting representation and the block-coupling
issue. This algebraic result does not change the selected multiplication bound.
