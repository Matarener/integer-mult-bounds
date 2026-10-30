# One actual low-cache column reaches the complete-owner carry leaf

This package connects the unchanged PR5332 low-cache frontend to the unchanged
generic PR5849 carry rotation through a literal tape and symbol translation.
It binds the released port9 inverse column1 at q=5 to one supplied complete
64-digit low-matrix cache, row0, and a supplied marked `[P] x [Q] x [S]` owner.
The program physically reads the selected old digits, constructs `C+1`, rotates
the complete supplied payload and erases the owned descriptor. New-low output
is retained, and borrowed inputs, spectators, private work and heads satisfy
the declared return contract.

For this column the quarter-scaled weights are
`(-1,0,-2,0,-1,0,0,0)`. Thus `N=-l0-2*l2-l4`, new low `t=4*N mod 5`,
and `k=(N-4*t)/5` lies in `[-6,0]`. The physical frontend computes
`C=k/4 mod Q` for canonical odd `Q>=3`. Its runtime branches select the
carry from actual cached digits; there is no host-selected offset. The fixed
compiler receives q, the source column and row before runtime inputs arrive.

[PROOF.md](PROOF.md) gives the interface and full composed leaf allowance.
The general high-matrix coordinate at row0/column1 would require `P=Q` and
`S=Q^62` times spectator volume. The small finite leaf fixtures do not materialize
that matrix owner. The inverse orientation undoes this fixed carry translation;
it is not the full forward matrix route.

## Evidence and reproduction

From the repository root with CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/port9-low-cache-carry --check-only
python3.12 -B scripts/research_package.py --package research/port9-low-cache-carry
python3 -B scripts/check_research_commit.py --package research/port9-low-cache-carry --check-source-history
```

[RESULT.json](RESULT.json) is the deterministic finite receipt. Normal replay
recomputes and compares it; `--write` explicitly regenerates it.
[VALIDATION.md](VALIDATION.md) records executed commands, counts and limitations.
The source pin manifest declares every live Python/table/route input. Frozen
source files are unchanged. No historical whole-package replay is needed for
this scoped composition.

The canonical [claim and finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/4945#discussioncomment-19284595)
records overlap and the explicit expansion boundary. Base main is
`a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority revision8, selected #6030.
The exact predecessors are PR5332 at
`8e96c889b924957c599687be56b19fce9161cad3` and PR5849 at
`35ee8364ccfe54d6d5ec154fbf74993624b0a0d4`, both already retained in main.
Their scientific acceptance is separate from this byte-bound reuse.

## Limits

The complete matrix cache, marked complete owner and extent descriptors are
supplied inputs. No GL-membership validation, whole-T cache formation or
selection, homogeneous high-word transformation, low-type commit, cache
retirement, physical ROW installation, supplier admission or new kappa follows.
Q=1 is outside this frontend contract; PR5985's separate bypass is credited
without claiming its integration here. A full caller invoice remains open;
the leaf allowance alone is not evidence of a profitable supplier change.

## Open next questions

1. Bind one complete tiny low-type domain to this cache/owner interface. Charge
   source construction, selection, staging and transport before expanding the
   implementation. The missing whole-T layout and full invoice are blockers.
2. Specify how new-low outputs are committed and how the old cache survives
   until its last consumer, then retires. Start with an explicit physical
   commit protocol and all cells/head walks; the low-type and ROW consumers
   are still missing.

The same questions, relevance and first steps are in [TASK.json](TASK.json).
This is scoped algorithmic interface evidence plus finite execution, not
independent human review, a proof-kernel certificate or a multiplication theorem.

## Attribution

Prepared by AAAmirinu with substantial OpenAI Codex assistance, including
parallel adapter, proof and checker work and root review. Apache-2.0.
JoyboyBrian/PR5332 supplies the low-cache decoder and runtime offset arithmetic;
Ali Romman/PR5849 supplies the complete-owner rotation and exact leaf ledger;
David Arias/PR2776 supplies literal tape machinery. Credit Charles Bethin,
Jose Manuel, Nick Petalas, Tekalign, ToikY, PR5820/5841/5842/5846 and the retained
G20/native/ROW/controller lineage. No predecessor bytes or authorship notices
are changed. The new contribution is the paid source-column interface and its
ownership-preserving literal composition.
