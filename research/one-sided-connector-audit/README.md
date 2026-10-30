# Sharp static connector bounds and an independent proof audit

The one-sided obstruction in [PR5673](https://github.com/CrocSwap/integer-mult-bounds/pull/5673)
passes a separate proof and coefficient audit under its stated full-stage,
characteristic-two contract. The new construction proves that its rank and
signature bounds are sharp at an unbounded family of sizes, even when every
thin query has square zero. **No new kappa is claimed.**

Over F_q, choose positive d,h and g=2q^(dh)-1 leaves. The explicit maps have
required sum K, total thin rank 2d+2h, extra image/row dimensions h, and at
most two leaves per signature. When h=1,d>=2, they group into d+1 rank-two
square-zero queries. This supplies static maps for both source targets:

- F2, d=4: 31 leaves and five rank-two queries.
- F2, d=2, h=3: 127 leaves and ten rank-one queries.

[PROOF.md](PROOF.md) gives the formulas and the audited implication.
[RESULT.json](RESULT.json) gives the exact finite checks.
[SOURCES.json](SOURCES.json) pins the retained source proof. The static maps
are not chronological words. Their purpose is to settle the proposed static
rank cut and give precise matrices for the next full-word search. A stronger
exclusion needs another condition. Native frames, ownership, tape costs and
the complete supplier remain open; the selected kappa is unchanged.

## Reproduce

Python 3.12 and its standard library suffice. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/one-sided-connector-audit
python3.12 -I -O -B research/one-sided-connector-audit/verify.py
```

Expect `PASS_ONE_SIDED_AUDIT_AND_STATIC_SHARPNESS` and the registered package
pass. The separate implementation imports no predecessor checker or finite
certificate. It checks 19,440 flag/order pairs, 72 literal words, 432 extracted
blocks, formal polynomial determinants and six full static matrices. The
matrices include the two proposed targets and F4. Twelve damaged constructions
are rejected. [VALIDATION.md](VALIDATION.md) records the executed export and
source corruption checks and the omitted checks.

## Open next questions

Choose a chronological split and order for the explicit 31-leaf maps, or
change these maps. Check every independent stage polynomial coefficient.
The static bounds give no guarantee that this is possible. Even a successful
binary word needs a native lift and a complete paid invoice before it can
change the multiplication bound. Do not run another rank-only search of
these exact targets as a substitute for that missing step.

## Credit and scope

Source: Ali Romman's PR5673 at c10f75f09e41803ae8efe478331a7509b7379b2f,
with substantial OpenAI Codex assistance. It supplies the one-sided proof,
Sylvester/signature cuts and the two search targets. Its retained proof credits
Cinna Davis, the PR5617/5631/5649 interface line and all P104/native/helper
contributors. This package adds the static sharpness theorem and a separate
implementation; it does not claim independent human or model-family review.
Prepared by Ali Romman with substantial OpenAI Codex assistance. No subagents.
Apache-2.0. Base main df0137efd35e11b4445734bf612bdd4c7ebc330c, priority7.
Coordination is in [Discussion5593](https://github.com/CrocSwap/integer-mult-bounds/discussions/5593#discussioncomment-19188781).
