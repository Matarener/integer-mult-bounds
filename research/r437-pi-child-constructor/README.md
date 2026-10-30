# One R437 child-constructor term inside Pi

PR #3983 leaves `Pi_v` uninstantiated in its call ledger

```text
gamma_v = checkpoint_v + elementary_preparation_v + result_transfer_v + Pi_v.
```

Its open question 2 asks for one source-bound child constructor, with
original-width stock and prefix multiplicity retained. This package prices
the program tapes of `children.extend`, the constructor that
`SelectedBinding.child_program` calls. It does not instantiate the rest of
`Pi_v` and it does not admit a stock coefficient.

On a parent program that enters already rewound, with `h` steps, index width
`I`, residue width `L` and code width `Q`, the pinned `FINITE_BITS = 16`
gives step length `c = Q + 2I + 90` and root length `R0 = 2I + L + 5`.
The constructor's program-tape meters are

```text
parent reads  = 2 R0 + 3 h c + 3,   writes = 0,   moves = 2 R0 + 2 h c + 4,
child  reads  = 2 S + 1,            writes = S,   moves = 2 S + 2,
S = R0 + (h + 1) c.
```

The child writes `S` symbols. That count is positive, independent of child
kind, and is production rather than the later capsule copy in PR #3983's
equation (5). The counting argument is in [PROOF.md](PROOF.md). Forty
executed fixtures match it, including good, pair, unit and half-width
children. A parent head moved one cell off the rewind postcondition does
not match the formula. Dropping one parent read per copied symbol does not
match either.

`SelectedBinding.check_stock` is a single `pass`. This constructor therefore
does not compare an original-width stock word. `extend` does not read a
prefix; prefix multiplicity stays in `prepare_child`, outside this term.
Index-arena traffic during the extent arithmetic is nonzero (6706 reads on
the largest checked case) and is not given a closed form here.

No new κ. Selected κ stays `0.001672660197076918`.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/r437-pi-child-constructor
```

Expected marker: `PASS_R437_PI_CHILD_CONSTRUCTOR cases=40 finite_bits=16 stock_gate=pass prefix_in_extend=false index_reads_seen=6706 no_new_kappa`, then the independent marker and `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=partial`.

## Open next questions

1. Price `Callback._validate_program` on the same rewound programs and add
   its program-tape and arena meters to this constructor. That is the other
   half of `SelectedBinding.child_program`. The prime-power division on the
   modulus is value-dependent, so the tape formulas above do not cover it.
2. Name a selected original-width stock word that `check_stock` should have
   compared, or show that no selected caller reaches that method. Until then
   the empty gate is not an admission of stock.

## Credit

The uninstantiated `Pi_v` ledger and the length `P_h` are Chris R /
Clear1nsight, PR #3983, following PR #3967. The constructor and tapes are
the retained physical-caller sources (Jose Manuel / jmbarrancoml, ywz65,
David Arias, Nick Petalas, and the PR #2753 / #2769 lineage). Prepared by
unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
