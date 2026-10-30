# A native receiver rewrite that increases the supported kappa

This package constructs a literal improvement of the attached PR3734 words.
It changes the two receiver updates at borrowed-word events `B[692:694]`,
letting register 672 omit an intermediate rank-2 frame. The complete local
recursive profile changes by

\[
\Delta=-H_1-H_2+H_3.
\]

Both providers pass the full five-stage native replay, including every
arbitrary live input, the inverse-transpose orientation, residual wrappers,
Gaussian phases, private-work restoration and exact warp recipes. The
[native summary](NATIVE-SUMMARY.json) binds these results to the emitted words.
The independently implemented
[receiver review](../architecture/evidence/RECEIVER-REVIEW.json) confirms the
three-register identity, all frame paths and the precise tariff change.

The separate [complete owner and invoice replay](../global-budget/receiver-sharing/RESULT.json)
uses the attained PR3815 clock and its actual physical allocation. It certifies
the finite root interval

\[
[0.001730739780298357321619,\;
  0.001730739780298357321620].
\]

This exceeds the adopted PR3815 root by approximately
`0.000000161343032110502879`. The complete ordinary and outer admission,
including the inherited analytic and BIT conditions, is bound in the parent
continuation package. Those inherited conditions continue to qualify the
integer-multiplication claim.

## The exact changed word

All indices below are the original 704-register BORROW numbering. The native
transport compacts 72 removed helper identities, so native numeric register
IDs must be read through its `helper_origin` map.

Write `h = L544`, `u = L672`, and `v = L676`, and define the actual binary
subspaces

\[
P=\langle51\rangle,\qquad
Q=\langle414,51\rangle,\qquad
R=\langle413,72,48,3\rangle.
\]

Their ranks are 1, 2 and 4. The inclusions are literal: `51 = 48 XOR 3` and
`414 = 413 XOR 3`, so `P` is contained in `Q`, which is contained in `R`.
The source word puts both receivers at `P` immediately before these events;
helper 544 is at `Q`.

| Original event | Original operation | New event | New operation |
|---|---|---|---|
| `B[692]` | `u += h/2` at `Q` | `B[692]` | `u += v` at `P` |
| `B[693]` | `v -= h/2` at `Q` | `B[693]` | `v -= h/2` at `Q` |
| — | — | `B[694]` | `u -= v` at `R` |

After this replacement, every later scalar event retains its operation and
frame. The B-position of each later warp increases by one; its lender,
operator and before/after frames are identical. The literal FULL cleanup is
rederived from the new non-target word.

For arbitrary initial values, the three new assignments give

\[
u\longmapsto u+v\longmapsto (u+v)-(v-h/2)=u+h/2,
\qquad v\longmapsto v-h/2,
\qquad h\longmapsto h.
\]

Thus both the original and changed word have exactly the matrix

\[
\begin{pmatrix}
1&0&0\\
1/2&1&0\\
-1/2&0&1
\end{pmatrix}
\]

on the ordered coordinates `(h,u,v)`. This includes arbitrary dirty receiver
values. In native physical coordinates, let `A` lift `P` to `Q` and `B` lift
`Q` to `R`. The original outputs at `R` are `BAu + Bh/2` and `BAv - Bh/2`.
The changed circuit gives those same two expressions by adding at `P`,
subtracting the helper at `Q`, and subtracting receivers at `R`. The new
rank-3 native child implements the composite lift `BA`; its exact phase is
checked by the fresh native recipes.

Register 672 has no observation or warp between the old two-event block and
its next original contact, `B[1109]`, at `R`. Register 676's next original
contact is `B[1114]`, also at `R`. Raising the receivers to `R` at the new
subtraction therefore respects their complete future frame paths. The
changed rank sequence of register 672 is

| Path | Positive climb ranks |
|---|---|
| Original `1 → 2 → 4 → 6 → 7 → 8 → 9` | `1, 2, 2, 1, 1, 1` |
| Changed `1 → 4 → 6 → 7 → 8 → 9` | `3, 2, 1, 1, 1` |

Every other register retains its paid rank profile. Consequently the full
local profile is:

| Child rank | Original count | Changed count |
|---:|---:|---:|
| 1 | 2,440 | 2,439 |
| 2 | 725 | 724 |
| 3 | 224 | 225 |
| 4 | 102 | 102 |
| 5 | 20 | 20 |
| 8 | 8 | 8 |

Raw rank mass remains 5,134. The gain comes from the strict inequality
`3^(1-kappa) < 1 + 2^(1-kappa)` for `0 < kappa < 1`. The changed word adds one
B scalar operation and one cleanup scalar operation. Their emitted scalar
cost and coefficient bounds are included in the native receipts.

## Full finite obligations checked

The constructor preserves all port, center, entry and exit subspaces, all
408 helper identities, and the ordered helper-width inventory
`{4:26, 5:2, 6:18, 7:53, 8:96, 9:213}`. This lets the complete invoice use the
actual PR3815 physical helper allocation directly.

For each provider, the fresh native chain checks 632 independent input
columns in both orientations. It restores all 91 zero buffers, clears the
private centers and coefficient stream, and checks the physical warp maps
on all 512 basis columns. The independent phase checker covers 72 warp
operators in 180 frame classes. The retained semantic rejection controls
are also exercised.

Both providers have emitted real-component primitive bounds of 158,186
forward and 158,234 backward. Their certified prefix bounds are 89 and 95
bits, within the retained 192-bit charged payload. Exact source hashes,
candidate hashes, native program hashes and individual receipt hashes appear
in [CONSTRUCTION.json](candidate/CONSTRUCTION.json) and
[NATIVE-SUMMARY.json](NATIVE-SUMMARY.json).

The independent invoice thread recounts all four provider/orientation
profiles and all 1,321,920 helper rows over 3,240 calls. Its complete paid
histogram is:

```text
{1:7986600, 2:2345760, 3:752328, 4:330480,
 5:69120, 8:25920, 48:137952}
```

The physical stock is 323,069 families, including 322,560 productive
families. These counts come from the checked literal chronological
allocation and the new native words.

## Reproduction

From the repository root, rebuild the two words using only the deterministic
three-gate applier:

```bash
python3 -B research/kappa-adaptive-continuation/native-alternatives/construct.py
```

Expected output starts with `PASS_BOTH_PROVIDER_LITERAL_RECEIVER_SHARING`.
The default input is the attached PR3734 words preserved under
`research/kappa-global-continuation/inputs`. The options `--source-dir` and
`--out` accept an explicitly supplied source directory and output directory.
The production path does not run the optimizer.

Bind the emitted words to both fresh native receipts:

```bash
python3 -B research/kappa-adaptive-continuation/native-alternatives/verify.py
```

Expected output is `PASS_LITERAL_RECEIVER_SHARING_BOTH_NATIVE_PROVIDERS` and
the new local profile. This command checks receipt and artifact bindings;
the full native computation is reproduced by the following two commands,
with fresh output directories:

```bash
python3 -B research/gmx-t74-borrow43-handoff/new/fastnative/run_native.py \
  research/kappa-adaptive-continuation/native-alternatives/candidate/BORROW-WORD-43base.json.gz \
  receiver-replay/native-base --engine sparse
python3 -B research/gmx-t74-borrow43-handoff/new/fastnative/run_native.py \
  research/kappa-adaptive-continuation/native-alternatives/candidate/BORROW-WORD-43extra.json.gz \
  receiver-replay/native-extra --engine sparse
```

Each finishes with `PASS_COMPLETE_T74_NATIVE_REPLAY`. The root continuation
verifier composes these local results with the independent receiver review,
actual owners, two-engine price enclosure and ordinary/outer admission.

## Discovery scope and attribution

The new search considered source covectors, permanent FULL carriers and
their transposed receiver identities, with changed scalar graphs followed
by constructive joint frame assignment. A positive control reproduces Nick
Petalas's known `X40 - 2 X54` restore rewrite and passes the independent
632-column audit. The existing PR3734 frame assignment was reproduced
unchanged by the min-sum screening optimizer. That numerical screening is
not a new formal optimality certificate.

The successful receiver identity is candidate 175 of the transposed B
search. Three variants of the same receiver pair have the same tariff;
the minimal two-event preimage was selected for the production applier.
Search scripts and receipts document bounded discovery experiments. The
claimed construction depends on the literal applier and native checks.

[DISCOVERY.json](DISCOVERY.json) records the completed bounded experiments,
the interrupted A-search prefix, and the overlap check. All four positive
variants replace the same original `B[692:694]` pair and eliminate the same
single rank-2 stop. Their tariff changes cannot be added as independent
savings. The A search was stopped after the successful construction passed
the full native checks; its final observed prefix was 1,850 cases, with
1,848 feasible frame graphs, two infeasible graphs and no emitted candidate.
The interrupted run is not an exhaustive statement about A rewrites.

Credit dataisfire for PR3734's staged544 producer-return construction, Nick
Petalas for the dirty-source covector mechanism and the joint frame-graph
elimination method, and Tekalign for the retained complete sparse native
replay driver. The source lineage also includes Ross Richardson's staged
entrances, dcharb78's carrier rewrites, Marius-Paul Dumitrean's joint rank-7
end frames, Jeremy Kothe's scalar/native accounting, and the other authors
credited by the retained packages. This continuation uses substantial
OpenAI assistance and retains the Apache-2.0 source attribution. Independent
software implementations are distinguished from independent human review.

## Open next questions

- Which other staged receiver pairs can share a partial sum across native
  frames? Start with a literal observer-free interval and price the complete
  changed word; the bounded searches here are not a general impossibility
  result.
- Can receiver sharing and source sharing be composed across a B/restore
  boundary while retaining arbitrary helper restoration? The present
  production change is wholly inside B.
- Which inherited all-size realization or precision/recovery premise can
  be discharged for the resulting frozen words? This local finite rewrite
  does not resolve those theorem-level conditions.
