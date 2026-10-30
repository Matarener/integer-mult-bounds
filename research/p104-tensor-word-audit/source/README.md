# One dyadic tensor code across both P104 axes

This package constructs one invertible code on all **21,632 data fields**:
`L=U_r U_c^-t`, `(Xhat,Yhat)=(L X,L^-t Y)`, with
`U=[[I,B],[0,I]]`. The same code is retained across both logical Gram stages,
so the row/column representation mismatch in [PR3961](https://github.com/CrocSwap/integer-mult-bounds/pull/3961)
is replaced by a matched shared representation. Every independent payload,
including the Gram kernel, is retained; entry and exit return fixed X/Y slots.
No division by 13, scratch array, helper erasure or free owner relabel is used.

The exact transformed Gram coefficients are `P_r M_c` and `M_r P_c`, where
`M=UU^t`. Literal scalar words and both code boundaries are fully counted.
For two **repeated uncorrected Gram pairs** they save 110,592 unit additions
and 33,280 halves/restoring doubles each against the specified uncoded word.
One pair loses 104,448 additions. This is an exact common-chart protocol
comparison, **not a full-caller, native-rank or runtime improvement**.

The actual retained caller requires identity shears. With `N=M^-1`, their
coded coefficients become `N_r M_c` and `M_r N_c`; the omitted side terms each
have full rational rank 10,816. Algebraic rank is not native tariff. Native
transport, actual repeated consumer, identity completion, helpers, ownership
and precision remain unpriced. No complete gate passes on the present evidence.

A separate coefficient-ring result explains why M cannot simply be discarded:
`A tensor A` has rank 64 modulo 13, while a proposed fully normalized spectral
projector product `169 P_r P_c` is zero there. Thus invertible bank-separate
Gaussian-dyadic codes cannot perform that particular free spectral split.
This does not prohibit arbitrary joint codes or programs with a changed alphabet.

See [PROOF.md](PROOF.md) for the physical chart-conjugation order, constructive
words, full obligation ledger and scoped module proof. [RESULT.json](RESULT.json)
contains finite counts; [TASK.json](TASK.json) records the changed premise and
next questions. Selected frontier and frozen predecessors are unchanged.

## Reproduce

Standard-library Python 3.12:

```
python3.12 -B scripts/research_package.py --package research/p104-tensor-code
python3.12 -B scripts/check_research_commit.py --package research/p104-tensor-code --check-source-history
```

The primary verifier authenticates three canonical-main inputs, reconstructs
the P104 matrix, executes the complete encoder/two-pair/decoder scalar word on
an arbitrary dense fixture with dirty-helper sentinels, enumerates every charged
operation, and checks the modular ranks. The separate Fraction oracle imports
only the word builders, evaluates them independently on every basis column of
two small whole-grid fixtures, and checks the tensor and physical-chart formulas.
It does not import the primary evaluator or claimed receipt. Destructive tests
cover optimized execution, false typed receipts, corrupted/missing source,
readonly Git-free replay and altered operation/return behavior. Finite evidence
supports the displayed algebra; no human or kernel theorem review is claimed.

## Open next questions

Find one actual repeated producer/consumer pair that can retain this shared code
through the **identity completion**, and specify every intermediate physical
chart/owner. Begin with the explicit `N-P` side maps, not an eight-coordinate
restriction of the input domain. Alternatively, derive one native triangular
code sweep with exact chart transport, fixed returns and a complete allowance.
Do not expand native construction until that allowance is favorable. A new
non-dyadic alphabet or general bank-mixing code must state its changed contract
before invoking the modulo-13 result.

## Credit

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.
PR3961 supplies the preceding mismatch question; its source authentication/root
constructor is reused here with credit. PR3882/3940/3943/3954 retain the residual,
caller, cleanup and gate lineage. ToikY/PR3956 owns the adapter comparison and
PR3966 the independent uniform-phase gauge; neither is a premise of this replay.
Rohan Arun/PR1972, Chafik Boukhalfa/PR1991, Adam Gall/PR1940, Josie Elliston/E8,
Sagar Thakrar/PR1012, Douglas Colkitt, Dominik Scholz and the retained native,
compiler, occupancy and terminal-floor sources retain their original credit.
The code is newly derived; it does not claim their native word as implemented
in coded coordinates. Pending PRs are context only: all replay inputs and
provenance are on canonical main, so no unmerged Git object is required.
