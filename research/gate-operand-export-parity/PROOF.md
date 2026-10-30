# Gate operand symbolic/export parity

## Claim

Let a multi-source gate be a triple `(f, d, srcs)` with destination register
`d` and ordered source list `srcs`. Over `F_2`, compare two operators that both
start from a pre-gate valuation `val0`:

- **Sym** (selected symbolic checker): read every source from `val0`, form
  `acc = ⊕_{s ∈ srcs} val0[s]`, then set `val[d] ← val0[d] ⊕ acc`.
- **Exp** (selected record exporter): for each `s` in `srcs` in order, set
  `val[d] ← val[d] ⊕ val[s]` using the *current* valuation.

Then:

1. If `d ∉ srcs`, then Sym and Exp agree for every `val0` (even when `srcs`
   contains repeated indices).
2. If `d ∈ srcs`, they need not agree. Concrete finite witnesses include
   `srcs = [d, d]` and `srcs = [a, d]` for any `a ≠ d`.

The selected PR589 checker rejects every gate with
`len(set([d] + srcs)) ≠ len([d] + srcs)` before export. The exporter does not
enforce distinctness. Scatter-only uniqueness guards therefore leave this gap
open.

Selected kappa is unchanged.

## Proof of (1)

Assume `d ∉ srcs`. In Exp, every assignment writes only register `d`. Every
source read therefore observes `val0[s]`. The net update is

```text
val[d] ← val0[d] ⊕ (⊕_{s ∈ srcs} val0[s]),
```

counting multiplicity. That is exactly Sym. Agreement is independent of order
and of whether source multiplicities are odd or even.

## Proof of (2) by witness

Take registers valued in `F_2` (or any `F_2`-vector space) and `d = 0`.

- `srcs = [0, 0]`. Sym: `acc = val0[0] ⊕ val0[0] = 0`, so `val[0]` is unchanged.
  Exp: first ADD forces `val[0] ← 0`; second ADD leaves it `0`. These differ
  whenever `val0[0] ≠ 0`.
- `srcs = [1, 0]` with `a = 1 ≠ 0`. Sym: `acc = val0[1] ⊕ val0[0]`, so
  `val[0] ← val0[1]`. Exp: after ADD from 1 one has `val[0] = val0[0] ⊕ val0[1]`;
  the subsequent self-ADD forces `val[0] ← 0`. These differ whenever
  `val0[1] ≠ 0`.

## Relation to scatter parity (#2977 / #3004)

For scatter rows the symbolic loop XORs once per occurrence while the exporter
emits one ADD per membership. They agree exactly when every positive
multiplicity is odd. Gate lists are different: both operators are
occurrence-based, yet they still diverge when the destination appears among
the sources because Exp re-reads the updated destination. #3004's open
question on gate operands treated distinctness as schema hygiene with "no
known divergent word"; the witnesses above are divergent under export-without
the checker. Accepted words cannot carry them only because the checker rejects
`bad operands` first.

## What this does not claim

- No production adoption and no new kappa.
- No claim that the selected word is defective: every D/A/B/C gate on the
  pinned tuned word has distinct operands.
- No native C++ replay and no change to frozen exporters.
