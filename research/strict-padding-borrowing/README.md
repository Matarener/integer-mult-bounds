# Strict-volume padding saves a borrowed radix digit

This package replaces the sufficient covering condition R>=S with the exact
strict volume condition for compatible-row padding:

```text
Rprime=ceil(R/S)*S < 2R   exactly when   S < 2R.
```

At fixed atom width, this makes least borrowing a monotone body-depth threshold
problem. It saves at most one radix digit when both optima fit, and can admit
a case where covering has no fitted plan. At the existing selected prime
q=2^127-1, width e=630087102387535114 and exact atom width 2, the least
borrowing falls from 696331 to 696330. This is exact reserve arithmetic and
a conditional interface improvement. The selected exponent is unchanged.

The opt-in tape_padding.py adapter actually accepts S/2<R<S, which the pinned
PR2786 planner rejects. It uses the retained canonical Count and Tape classes,
keeps the old planner on R>=S, and uses the same padding/restriction scans and
completed-return checks. No frozen code or default backend changes.

## Replay

Python 3.12 and its standard library suffice. From the repository root, with
TMPDIR pointing to an existing owned external scratch directory:

```sh
python3.12 -W error -B scripts/research_package.py --package research/strict-padding-borrowing
python3.12 -I -O -W error -B research/strict-padding-borrowing/independent.py
python3.12 -W error -B scripts/check_research_commit.py --package research/strict-padding-borrowing --check-source-history
```

The registered replay runs normal and optimized primary checks, the separate
oracle and behavioral controls. The direct scripts support Git-free exports.
The verifier compares a typed canonical JSON receipt and never rewrites it.
To recompute the receipt explicitly, run verify.py --emit and review stdout.
SOURCES.json pins four canonical inputs and separately identifies the retained
PR3486 comparison proof. That pending PR is not a foreign-history runtime
dependency. The frozen padding archive retains all original source notices.

The primary and separate implementations agree on 8192 cases, with 8030
admitted plans, 3058 one-digit improvements among jointly fitted cases, and
32 newly fitted cases. Those counts describe this finite domain only. Literal
Count execution checks 576 accepted and 576 rejected plans. Of the accepted
plans, 276 are rejected by the old covering precondition. Five synthetic
rowwise-reversal fixtures check all 258 independent basis inputs. No selected
GL64 payload is executed.

## Sources and limitations

Nick Petalas's PR3486 supplies the covering-constrained predecessor and its
body-depth selection method. This package changes the explicit padding premise;
its exact comparison proof is retained unchanged. Nick Petalas/PR3246 supplies
the one-factor guard stock. Tekalign/PR3264 supplies the conditional ordinary
consumer proof. Jose Manuel/PR2786/2808/2899 supplies compatible-row padding,
the ordinary wrapper and encoded interface. David Arias/PR2753 supplies the
recursive BIT caller. Ross Richardson/PR2420's stronger dual-format contract
retains its separate divisor requirement. DreamingOfClouds/eumemic's BIT
source527, Adam Gall/PR2084, Nick Petalas/PR2808/2120, Rohan Arun/PR1094,
Jeremy Kothe/PR1087 and the retained geometry/hosting/assembly sources keep
their predecessor attribution.

The borrowing implementation is a bounded host specification, and the row
adapter has a 4096-bit Count capacity. Its callee fixtures are synthetic complete
rowwise reversals. Complete physical C0/refinement, uniform costs, fresh fields,
pointwise spectator restoration, full-cover, precision/tape and outer-transfer
premises remain. No default integration, new cutoff, supplier, kappa or full
multiplication theorem is claimed. Independent human and formal proof-kernel
review are unclaimed.

## Open next questions

Connect the wider row planner to one opt-in real fitted Ordinary/C0 callback,
then translate the complete borrowing selection to fixed-role Count tapes and
derive its setup invoice. Begin with the exact selected S_d producer and both
immediate restrictions. Retain the genuine other high field and all ownership
and restoration premises. A synthetic endpoint or a smaller k cannot establish
those physical obligations.

Nick Petalas. Apache-2.0.
