# Sharp A5 three-call rank threshold

For every field and every finite dirty role space, the A5 conjugate-pair
operator with two orthogonal target blocks of ranks r,s has exact paid-call
minimum three when the allowed coupling rank h is at least r+s, and four
when max(r,s)<=h<r+s. After scalar normalization, every three-call
implementation must use middle coupling P+Q, of rank r+s. Arbitrarily many restored dirty spectators and
free scalar mixing preserve this threshold.

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

This is a scoped algebraic proof with exact finite corroboration. It changes
the rank-one hypothesis of Wentao Li's [#4089](https://github.com/CrocSwap/integer-mult-bounds/pull/4089),
following Cinna Davis's [#2246](https://github.com/CrocSwap/integer-mult-bounds/pull/2246).
Their rank-one theorem, support filter and special-case forced middle
projector are cited predecessors, not new claims here. Their searches and
verifiers are not replayed. The new result is the sharp higher-rank cap
transition, arbitrary-rank construction and field-uniform proof.

## Operator and complete invoice

In End_K(V)[A5], let x=(12)(34), y=(135), and let P,Q be nonzero
idempotents satisfying PQ=QP=0. Products act rightmost first. A paid call is
F_g(N)=I+([g]-[e])N, with g in {x,y}, N idempotent and 1<=rank(N)<=h.
The target is T=I+([xy]-[e])P+([yx]-[e])Q.

```text
four calls: F_x(P) F_y(P)   F_y(Q) F_x(Q)
three calls: F_x(P) F_y(P+Q)        F_x(Q)
```

Both equal the full operator T and restore the common kernel. Their total
coupling rank is the same, 2(r+s). The change saves one paid-call overhead
only if the enlarged call is available under the declared cap. It is not a
claim of native speed, a recursive-child saving or a new kappa.

[PROOF.md](PROOF.md) proves the all-field threshold by matching full
noncommutative group coefficients. The necessity argument even allows
non-idempotent paid couplings; the legal alphabet and witnesses use
idempotents. Scalar augmentation removes any residual free GL(V) map.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/a5-rank-cap-threshold
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/a5-rank-cap-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/a5-rank-cap-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/a5-rank-cap-threshold --check-source-history
```

Use an equivalent CPython 3.12 path on another machine. The direct marker is
`PASS_A5_RANK_CAP_THRESHOLD`. Each direct execution is read-only and emits a
generated receipt containing freshly computed counts and SHA256 hashes of
all six package files. No receipt is hand-written or used as a proof input.
The registered normal and optimized commands use explicit exception checks.
All source pins are provenance only; the standalone verifier imports no
predecessor implementation or external data file.

The finite evidence is separate from the universal written theorem. The
verifier expands all fifteen short label words, enumerates complete ternary
and quinary two-role idempotent alphabets including higher-rank calls, and
checks all attaining target pairs. It also checks exact rational and
F2/F3/F5/F7 oblique projectors of ranks up to 3 and 4 in at most eight roles,
complete three/four-call endpoints, every single-call omission, malformed
inputs, and a dirty-spectator leakage control. A separate regular-action
engine acts on every basis column of both four-role words over F3.

The direct run enumerates 21,952 ternary words and 262,144 quinary words,
with 24 and 60 three-call hits across 12 and 30 target pairs, respectively.
Every hit has the required rank-two middle coupling. The remaining checks
cover 60 complete endpoints from 30 oblique pairs, 480 regular-action basis
columns, 210 omission controls, six invalid-input controls and one spectator
leakage control. These counts are freshly enumerated, not a predecessor
receipt or a claim of exhaustive coverage in larger dimensions.

## Scope and decision

The base is canonical main de5ec2e7a6074068452f45b1a191b5c72832df4a,
priority revision 8. The selected source-binding orientation passed; it was
metadata orientation, not a selected scientific replay. The card is
`bit-new-register-model`, explicitly changed to the paid rank cap. This is a
formal algebraic side result. The first improvement ends the investigation.

Initial overlap checking covered live PRs, this account's recent work,
active handoffs, all-main README searches and merged PR searches for A5,
conjugate pairs and rank caps. The card cache reported 416 open PRs and
5,315 Discussion records; its local scan omitted sparse packages. Direct
Git searches covered all main READMEs for the distinctive candidate terms.
Arbitrary code diffs and unpublished work are not fully covered. No match
is a novelty guarantee. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19214476)
records the intended scope. Global literature priority is unclaimed.

No optimum is asserted when h<max(r,s), under an arbitrary rank tariff,
with other group labels, or for nonorthogonal targets. Native realization,
physical scalar mixing, frames, movement, preparation, storage, restoration
cost, precision, compiler closure and a complete recursive consumer remain
unpriced. No selected-frontier change, supplier admission, complete
multiplication theorem, Lean run or Docker run is supplied.

## Open next questions

Can an actual nonabelian native caller execute the combined middle call
more cheaply than the two separate y calls? Start with one runtime carrier
and a rank-two idempotent, then give a full invoice for scalar mixing,
movement, frames and return on arbitrary dirty data. The missing native
tariff and recursive consumer block any profitability claim. This question
is also structured in [TASK.json](TASK.json); no follow-up is reserved.

## Related work and credit

- Wentao Li #4089 supplies the arbitrary-role binary rank-one theorem and
  the support/coefficient argument. Cinna Davis #2246 supplies the original
  A5 target, finite result and all-role question. The retained register-model
  and PR840 construction lineage remains credited through those sources.
- Cinna Davis's open [#3914](https://github.com/CrocSwap/integer-mult-bounds/pull/3914)
  proves collapse into an additive caller. Our changed rank cap does not
  remove that caller obstruction and computes no common numerical value.
- Nick Petalas #5114 supplies an algebra-faithful address carrier;
  JoyboyBrian #5186 supplies a distinct paid physical rank-one caller.
  Neither is a price for the higher-rank alphabet used here.

[SOURCES.json](SOURCES.json) pins exact historical provenance. Predecessor
files and credit are unchanged. No independent acceptance is claimed.

## Verifier implementation limits

All loops have fixed finite domains: fields 0,2,3,5,7, role counts at most
8, word lengths at most 4, 120 permutations and at most 32 two-role
idempotents. Formal states have at most sixteen coefficient blocks;
regular-action states have at most 240 scalar entries. There is no recursion,
network access, subprocess, dynamic code generation or callback dispatch.
Functions fit within sixty lines. Python and Fraction allocate dynamically;
the fixed domains bound live objects but do not provide allocation-free
execution. Warning-strict normal and optimized runs are the supported
interpreter diagnostics. No external static analyzer is assumed installed.
