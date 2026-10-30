# Sharp T16 profile passes complete finite admission

The near-selected sharp T16 nomination from [PR3403](https://github.com/CrocSwap/integer-mult-bounds/pull/3403)
passes the unchanged eleven-stage strict controller and complete paid invoice.
The resulting conditional finite construction has

```text
kappa = 104630538241437/62500000000000000
      = 0.001674088611862992.
```

The selected record remains at `0.001672660197076918`. This candidate improves
that conditional exponent by exactly `0.000001428414786074`. It also exceeds
PR3390's separately published T16 candidate `0.001673677688974651`. This is a
packing improvement under the inherited construction assumptions. It does not
change the selected record or claim an unconditional multiplication theorem.

PR3403 proved combinatorial feasibility on supplied windows. This contribution
closes its first Open next question for the old profile. The actual source-event
windows are independently reconstructed, all physical charts are emitted and
audited, and both suppliers and the full finite/outer invoice are checked.

## Evidence and scope

The idle profile is `{1:2431,17:1,48:4887}`. The full paid profile is
`{1:349759,2:60192,3:62208,4:20448,5:11808,8:1152,17:1,48:4887}`.
All 69,120 whole-helper roles and 144 complete calls retain the selected
word, widths and call order. Rank mass is 1,041,408 and deficit is 5,120.

The 9,967 actual 73-axis charts pass the unchanged controller. Required prefix
is 397 bits, charged at 512. The physical row coefficient is 16,469, below
20,161. The complete typed paid invoice equals the selected invoice after
removing exactly three changing source-binding hashes. Their live bindings
are still checked. No cost field is omitted. All 69 admission, 12 bit, 15
controller and 6 independent T16 controls pass, along with 11 additional
inherited independent owner controls and all 47 strict outer inequalities.

The exact native complex endpoint is
`1676895884165954931459/10^24`; the bit endpoint remains
`1733427039589844234749/10^24`. Both rational moment engines certify the
complex lower endpoint and reject the next `10^-24` point. Conservative
kappa is `0.001674088609009798`. [PROOF.md](PROOF.md) explains the implications.
[RESULT.json](RESULT.json) contains exact values and the fixed-word packing
ceiling from `ceiling.ceiling()`, including the fraction of that cap attained.

No optimizer or solver enters replay. `predecessor/` retains all eleven
original PR3403 files. [SOURCE-EXPORT.json](SOURCE-EXPORT.json) authenticates
them at `9512b580d60eb84f6972954370acdd92746d5aa7`, and the unchanged PR3338
strict-replay adapter at `f2e33dd2c07caf5dac2ee42505852a081d8fa7ca`.
The original predecessor descriptions remain historical. Only this package's
top-level manifest is the new admission contract. Every external input is
declared and pinned to canonical base
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.

## Replay

Python 3.12 or later; standard library only. Set `RUN_ROOT` to a new owned
directory under `~/.cache/integer-mult-bounds-runs/`. From the repository root:

```sh
mkdir -p "$RUN_ROOT/scratch"
TMPDIR="$RUN_ROOT/scratch" python3 -B scripts/research_package.py \
  --package research/t16-sharp-profile-admission
TMPDIR="$RUN_ROOT/scratch" python3 -I -Werror -B \
  research/t16-sharp-profile-admission/verify.py --work "$RUN_ROOT/admission"
```

The registered command also runs seven behavioral groups under ordinary and
optimized Python. These reject changed literal owners, retained-certificate
corruption, paid-cost/type changes, duplicate JSON keys and an actual CLI
source mutation before scientific replay. Full admission refuses optimized
Python because the unchanged ancestral verifier requires assertions.

To reproduce from committed bytes without a checkout or pending Git objects:

```sh
python3 -B scripts/export_research_package.py export \
  --package research/t16-sharp-profile-admission --ref HEAD \
  --output "$RUN_ROOT/package.tar"
python3 -B scripts/export_research_package.py check "$RUN_ROOT/package.tar"
mkdir "$RUN_ROOT/export"
tar -xf "$RUN_ROOT/package.tar" -C "$RUN_ROOT/export"
TMPDIR="$RUN_ROOT/scratch" python3 -I -Werror -B \
  "$RUN_ROOT/export/research/t16-sharp-profile-admission/verify.py" \
  --work "$RUN_ROOT/export-admission"
```

Compare decompressed owner payloads across Python/zlib versions. Committed
source and archive hashes are exact. The three binding files are deterministically
derived from the retained certificate, actual owner audit and exact prices.
`ADMISSION.json` records the first complete local strict replay. Its stage
times are diagnostics, not performance claims. `VALIDATION.json` records the
publication checks. Hosted CI and independent human review remain separate.

## Open next questions and remaining assumptions

This reuses the authenticated selected native provider and its completed
ancestry receipts. It does not rebuild the entire PR1005/1018 native chain.
All-size compiler, common-label/mutable-source realization, whole-call hosting,
precision/tape, exact recovery, analytic transfer and PR589 bit H1-H5 remain
inherited assumptions. No Lean or full cold selected replay is claimed.

The finite nomination and actual controller/invoice gate are now passed.
Another fixed-T16 seed is not an improved contract. The next construction
question must change the local word, replica architecture or consumer and
derive its complete optimistic rank and physical bill before another search.
The structured questions in [TASK.json](TASK.json) also identify the separate
universal compiler/hosting proof obligations. This session reserves no further
round and makes no claim of global optimality across those changed contracts.

## Sources and credit

Credit Ali Romman/PR1129 and Hanson Sun/PR1914 for the pooled T16 bound and
integer-gap question; PR3352/3364/3378/3395/3403 for the exact integer envelope,
temporal allocation and distinct-family construction; Rohan Arun/PR1094,
Jeremy Kothe/PR1087 and preceding packing work; Hao Yan/FanPUYen/PR858 for
the T16 lift, controller and independent audit; Philippe Van Velzen for the
strict admission and source-closed replay route; Josie Elliston for the
independent owner/window audit; and the retained geometry, native, compiler,
PR3338 and PR589 bit-supplier lineage. PR3390's physical augmentations and
PR3396's fixed-buffer obstruction remain separately credited evidence.
New contribution by Nick Petalas. Apache-2.0.

## Engineering constraints

Build the Lever gives a deterministic certificate-to-admission replay.
Boundary Discipline concentrates source/data checks before scientific replay.
Test Behavior, Not Implementation gives semantic owner/invoice/CLI controls.
Prove It Works requires the actual emitted controller and a Git-free committed
export. Separate Before Serializing Shared State gives this package its own
branch/output directory and process-held ownership/shared-Git locks.

Power of Ten rules 3, 8 and 9 have bounded Python/framework deviations.
Managed-runtime allocation cannot be eliminated; decoded input is limited to
64 MiB, each source file to 32 MiB, and the retained constructor domain to
144 calls, 480 helpers, 32,256 bins and 69,120 roles. Graphs are at most 144
by 144 and at most 224 matchings. The strict child has a 300-second timeout.
Imports target named source-authenticated modules; unittest dispatch is confined
to seven groups. New functions and the retained adapter are below 60 physical
lines, with no new recursion. The unchanged predecessor's internal dynamic
Python allocations and legacy routines are retained for byte-identity rather
than refactored. Their original finite model and controls remain the boundary.
Verification uses warnings-as-errors, Ruff and ordinary/optimized behavioral
controls. Follow-up: if this domain grows, split the replay and replace its
fixed bounds and dispatch inventory before admitting the larger input class.
