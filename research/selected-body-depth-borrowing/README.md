# Least borrowing at the selected BIT body's actual depth

The existing one-factor stock selector uses the original width's recursive
depth D(e). This package proves how to choose the least borrowed k using
the actual body n=floor((e-k)/w), with w fixed before borrowing. The exact
condition is the monotone inequality

```
k >= ceil(log_q S_D(n)),   2k<e,   n>=64.
```

Bisection returns the optimum. An independent formula enumerates inverse-depth
slabs. This is a conditional NODE-guard interface theorem and bounded exact
host-integer selector, with no installed backend change or new kappa.

The [proof](PROOF.md) gives a finite example in the selected parameter domain.
At q=2^127-1, e=250000 and the existing w=ceil(e^(17/10000))=2, the original
depth needs 147459 borrowed digits and fails strict fit. Even the unborrowed
body depth needs 139267 and fails. The optimum uses 122882 digits, leaving
63559 body atoms of depth 15, and satisfies 245764<250000. This is a reserve
calculation, not an execution or runtime measurement of that payload.

Direct fixed-point iteration is insufficient. At the same q and e=970370,
w=2, substitution cycles between 155651 and 163843. The least admissible
k is 159747, although its body requires only 155651 digits. Choosing that
smaller requirement again increases the body depth. No fixed point exists
for this example. The selector must solve the inequality.

## Reproduce

From the repository root, with standard-library Python 3.12:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/selected-body-depth-borrowing
```

The registered commands are also standalone and work in the committed
Git-free package export, including its seven explicit source files:

```sh
python3.12 -I -W error -B research/selected-body-depth-borrowing/verify.py
python3.12 -I -O -W error -B research/selected-body-depth-borrowing/verify.py
python3.12 -I -O -W error -B research/selected-body-depth-borrowing/independent.py
python3.12 -I -O -W error -B research/selected-body-depth-borrowing/test_controls.py
```

Set TMPDIR to an owned external directory for temporary CLI fixture copies.
The programs write no package outputs. The primary checks every declared
source hash and the complete typed RESULT.json. The independent implementation
imports neither primary code nor that receipt.

The implementations agree on 8192 toy cases, with 7113 fitted plans, and
five selected examples. The identical census SHA256 is
`2e796c10883b9dcc6ba238dc6359f391bae3e3bd1f4e30c7d2c165bfa210d51a`.
An exhaustive k scan checks all 8192 decisions and every accepted padded
quotient/Q guard. Capacity controls reject nine invalid boundaries. Actual
optimized CLI controls accept two valid exports and reject seven corrupted
sources, typed/duplicate receipts and incorrect selectors.

The q example has a checked Lucas-Lehmer certificate. Exact product enclosures
certify every consumed selected stock digit count without constructing its
huge group/reserve. These checks corroborate the written proof; they are not
proof-kernel verification or a full multiplication replay.

## Source boundary and delta

Canonical base is `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
[SOURCES.json](SOURCES.json) records exact main-branch paths, Git blobs and
SHA256s. Only this new package changes. No predecessor executable is imported.

Nick Petalas's PR3246 supplies the one-factor reserve. Tekalign's PR3264
connects it to both PR2899 padded calls and explicitly retains D(e), leaving
actual-body depth and optimal selection open. Jose Manuel supplied PR2899's
encoded width/stock selector and ordinary consumer, and PR2809's fixed-role
caller. David Arias supplied PR2753's all-size logical caller. Ross Richardson's
PR2420 supplies the stronger dual-format boundary. This contribution is the
borrowing optimum, its depth-slab characterization and a selected-domain
obstruction to fixed-point iteration.

Retain Adam Gall/PR2084, Nick Petalas/PR2808 and PR2120, the original
DreamingOfClouds/eumemic BIT/source527 lineage, and Rohan Arun/PR1094 and
Jeremy Kothe/PR1087 assembly attribution. Frozen predecessor notices remain
unchanged. No predecessor reserve reduction or consumer proof is claimed as new.

## Limits

The theorem assumes the prescribed stock and the completed callee's existing
fresh-row, full-cover, pointwise restoration, padding, spectator and ownership
contracts. A consumer promising both older full depth formats still needs
its stronger reserve. Physical refinement, uniform costs, all-size caller
premises, precision/tape and outer transfer remain. The host selector does not
supply Count tapes, a default-backend patch, a new cutoff, a supplier or a new
selected frontier. No selected GL64 payload, full selected cold replay,
independent human review or formal proof-kernel review is claimed.

The minimum retains the explicit covering constraint q^k>=S_D(n). It is not
an optimum over other padding budgets, formats or atom widths.

## Open next questions

The next useful implementation question is a bounded Count-tape translation
of the monotone predicate with an exact physical setup bill, before replacing
an existing callback. It must retain fixed w, compute the body after each
trial k, and rebuild the accepted plan's body and remainder. Current physical
and callee prerequisites remain blockers to supplier admission. Another
constant search or exponent substitution does not close them.

[ENGINEERING.md](ENGINEERING.md) records replay capacities, runtime deviations
and diagnostics. [TASK.json](TASK.json) gives the structured next question.
The family decision is narrow: preserve this selector lemma and fixed-point
obstruction without expanding a supplier campaign.

Nick Petalas. Apache-2.0.
