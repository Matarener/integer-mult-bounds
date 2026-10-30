# A sharp parity-check barrier to relaxing integer recovery precision

This contribution was produced by Nick Petalas. Apache-2.0.

For N>=2 arbitrary integer coefficients, grant their exact sum and approximate
values with uniform absolute error at most R. A fixed binary-linear sketch
permits exact recovery for every input precisely as follows:

| Closed error radius | Necessary and sufficient condition |
| --- | --- |
| 0 <= R < 1/2 | No sketch needed |
| 1/2 <= R < 1 | Append the all-ones row to the sketch matrix: binary rank must be N |
| R >= 1 | Impossible even with every coordinate parity |

The middle regime needs exactly **N-1 parity checks**, attained by revealing
the first N-1 coordinate parities. Dense fixed checks cannot improve that
count. Every sketch excluded in the middle regime has an explicit pair of nonnegative zero/one
coefficient vectors with the same sum and sketch, both within 1/2 of the
same observation. [PROOF.md](PROOF.md) proves the all-input classification.

This is a **scoped obstruction and construction proof with finite exact
corroboration**, not a search failure or a complete multiplication theorem.
It rejects a sublinear fixed-parity replacement for the strict half-unit
error requirement in the unrestricted coefficient interface. It gives no new kappa,
supplier admission or lower bound for actual convolution coefficient sets.

## Reproduction

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/sum-parity-recovery/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/sum-parity-recovery/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/sum-parity-recovery
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/sum-parity-recovery --check-source-history
```

Any CPython 3.12 executable can replace the local path. The verifier writes
nothing. It prints a generated JSON receipt bound to every package file,
then `PASS_SUM_PARITY_RECOVERY`. The registered replay runs both modes.
The finite oracle enumerates all binary sketch row spaces for N=2..6 and
tests their actual equal-weight binary coefficient observations. It also
checks the constructive decoder, closed endpoints and rejected contracts.

On CPython 3.12.15, normal and optimized direct runs passed in about 0.25
seconds each; the complete registered replay passed in 0.75 seconds. These
are replay-budget observations. The exact finite result is 3,287 row spaces,
67 admitting sketches, 3,220 explicit ambiguities, 5,704 boundary decodes,
1,089 sub-half-unit decodes, 66 omitted-check controls, 63 unit-radius
ambiguities, 20 invalid-contract rejections and one 4,001-bit integer fixture.

## Scope, sources and credit

The new question changes `uniform-transfer-audit` to an analytic-recovery
contract obstruction; it does not audit or discharge a selected assumption.
Base is canonical main `a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority
revision 8. The selected conditional kappa is .003125804.

The selected review and zxv's [PR6062](https://github.com/CrocSwap/integer-mult-bounds/pull/6062)
supply recovery context. The original fixed-syndrome question is not taken
from that package. Standard binary linear algebra, coding and integer-lattice
separation retain their background credit; no literature-priority claim is
made. No predecessor numerical result, matrix or scientific checker is used.
The P104/native/helper/compiler/outer lineage retains its original credit.
[PR6182](https://github.com/CrocSwap/integer-mult-bounds/pull/6182) has a different
deterministic rounded inverse and coordinate-tag model, absent here.

The mathematical result permits all N and all integer magnitudes. The exact
decoder executable accepts N=2..64, at most 64 sketch rows, and at most 4096
bits in each input integer or rational numerator/denominator. Python requires
dynamic allocation; these bounds constrain its live arithmetic and equation
storage. Exhaustive checks stop at N=6. No recursive code, external dependency
or generated code is used. Test rejection callbacks have fixed local targets.

The exact sum and sketch acquisition, restoration, tape movement and complete
physical bill are unpriced. Sparse/probabilistic errors, adaptive or nonlinear
checks, odd moduli, and additional coefficient restrictions are not covered.
No selected cold replay, numerical supplier, formal kernel or full outer
proof ran. Independent human and formal proof-kernel review are unclaimed.
The two Python files pass warning-strict execution, syntax/AST checks and
the 60-line function ceiling. There is no project Python linter configuration
in this checkout; no separate linter or static type-checker pass is claimed.

## Open next questions

- Can one actual convolution caller restrict the possible coefficient-error
  supports enough to use fewer exact checks? First prove a support restriction
  from its completed numerical error, then price acquisition and decoding.
  A uniform norm bound alone supplies no such restriction.
- Can a fully charged odd-modulus recovery interface improve the precision
  budget? First specify its exact coefficient domain, modulus acquisition,
  returned error and storage. This binary theorem gives no odd-modulus bound.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19272169)
records the predicted scope. Only this package is changed.
