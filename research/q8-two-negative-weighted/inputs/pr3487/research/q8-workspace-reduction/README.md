# Arbitrary dirty workspace for two negative Q8 targets

Two negative-generator targets need exactly six positive Q8 calls, with any
finite restored dirty workspace. Adding one positive-generator target raises
the sharp bill to seven. These are computer-assisted scoped theorems in the
full formal `F2[Q8]` register model. They do not improve the selected exponent.

The new [proof](PROOF.md) reduces every n-call diagonal Q8 word to at most
`floor((n+t)/2)` total roles, where t counts targets in `{i,zi,j,zj}`.
Write `X=(u_l)` and `Y=(v_l^T)` for its binary rank-one idempotent factors.
The combined character gives `XY=P_odd`, so `rank X+rank Y <= n+t`.
Restrict to the image span, or quotient by the common kernel, whichever is
smaller. Both operations preserve every paid label, order and full dirty
endpoint. The quotient avoids transposing noncommuting coefficients.

Every potential improvement to the six-call pair would fit on three roles,
and every improvement to the seven-call triple would fit on four.
[PR3471](https://github.com/CrocSwap/integer-mult-bounds/pull/3471)
already excludes both at four roles. This closes its arbitrary-workspace
handoff without enlarging a census. Its three-negative three-role values
remain finite-width results.

## Model and boundary

The paid labels are positive i,j, each at unit price. A call is
`I+([g]+1)uv^T`, with binary `v^T u=1`. All inputs are independent arbitrary
dirty data, including spectators; endpoints require equality of every formal
coefficient. Only scalar binary GL mixing is free. There are no clean inputs,
erasures, free address maps or higher-rank calls.

The theorem covers the four ordered active pairs in `{zi,zj}²` and all 24
ordered triples with exactly two negative-generator targets and one positive
i/j target, in arbitrary positions and with arbitrary finite restored dirt.
It does not give nonuniform-price minima or the arbitrary-workspace
three-negative tariff. A physical implementation and its complete caller,
ownership, routing and consumer invoice remain separate obligations.

## Evidence and replay

[RESULT.json](RESULT.json) is recomputed, not accepted as a premise. The
constructive checker implements both reductions, checks every scalar
intertwining column and every formal endpoint, and exercises dirt that the
quotient discards. It checks all 5,333 words in its fixed short-word domains;
487 have diagonal monomial endpoints. Five larger fixtures include both
reduction routes, central and noncommuting targets, and the empty word.
All 116 fitting direct words and their 792 single-call omissions are checked
at widths 2,3,4,8,12.

The unchanged retained PR3471 C++ source reruns its original finite queries.
The new independent Hamilton/full-convolution implementation checks all 64
group products, 8,502 native probe states, both 42,041-state depth-two balls
and the two negative-pair meets. The triple's complete streamed membership
query uses the retained native engine after these checks; a second complete
implementation of that stream is unclaimed. Extra original native cases run
because the retained executable is unchanged and supply no broader new claim.
The source, receipt and scope note are retained byte-for-byte with exact
origin heads, blobs and hashes in [inputs/RETENTION.json](inputs/RETENTION.json).
No unmerged foreign Git object is needed to reproduce the result.

Python 3.12 or newer and a C++20 compiler are required. Use a private output
directory, for example `RUN=$HOME/.cache/integer-mult-bounds-runs/q8-workspace`.
Create its `scratch` directory before setting `TMPDIR`.

```sh
TMPDIR="$RUN/scratch" python3.12 -Werror -B scripts/research_package.py \
  --package research/q8-workspace-reduction
TMPDIR="$RUN/scratch" python3.12 -I -O -Werror -B \
  research/q8-workspace-reduction/verify.py
TMPDIR="$RUN/scratch" python3.12 -I -O -Werror -B \
  research/q8-workspace-reduction/test_package.py
```

Direct commands support the committed Git-free export with its declared
proof input. They make no network or Git calls. The registered runner also
validates pinned historical metadata. [VALIDATION.md](VALIDATION.md) records
controls, bounded resources, diagnostics and unrun obligations.

## Source scope and credit

Canonical main is `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority
revision 6. [SOURCES.json](SOURCES.json) pins the historical card, selected
record and ywz65's retained mixed tariff proof. [COMPARISONS.json](COMPARISONS.json)
records exact comparison sources without declaring them runtime ancestry.
The new proof states every used image, kernel, character and rank step.

Credit Tuafo's image argument and Nick Petalas/PR2900's abelian mixed-target
restriction, ywz65/PR2587's coefficient-support/Sylvester method,
Nick Petalas/PR3450's character, PR3460's one-negative boundary and
PR3471's finite exclusion. Aaron Wang/PR2318 retains the two-role values.
Retain Cinna Davis/PR1925/2047/2248, steph4n-gh/PR1573, eumemic/PR288,
Ali Romman/PR468, Gareth Davidson/PR1333, Navinor/PR1822, woklerx/PR1443,
waynenilsen and the register-model lineage. Arham Tahir/PR3137's physical
compiler and PR3461's scalar preparation result retain separate contracts.
New work is Apache-2.0. Nick Petalas.
Independent human and formal proof-kernel review are unclaimed.

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2034#discussioncomment-19010336)
contains scope and artifact status. Entry overlap covered 396 open PR bodies
and 2,320 Discussion records with complete pagination and no warnings.
Submission refresh retained the same canonical main and guidance. Complete
pagination covered 398 open PR bodies and 2,324 Discussion records at
03:25-26 UTC on 2026-10-18, without warnings. These snapshots do not cover
every diff or unpublished work.

## Open next questions

Does a five-role word of at most seven calls reach three negative-generator
targets and two restored dirty spectators? The reduction proves that this
finite question would settle the arbitrary-workspace nine-call tariff.
First seek a sign-sensitive invariant or a cheaper exact word, before funding
another census. That exclusion is unrun and is not implied by the present
certificate. [TASK.json](TASK.json) records the boundary and first step.

A supplier improvement still needs an actual paid caller and complete
physical invoice. No further dependent construction round is reserved.
