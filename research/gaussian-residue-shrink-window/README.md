# Sharp strict-child window for residue-assisted Gaussian recovery

This independently checks the **recursive size contract** of
[Dugongue's PR3881](https://github.com/CrocSwap/integer-mult-bounds/pull/3881)
at `75e098dc12a2567e73a2858137408e08d31dbf84`, and executes its new
boundary point. It supplies a sharp declared-width admission formula, not
a physical caller, whole-cost improvement, all-size recurrence or new κ.

For the unchanged 455-point source box and 64-bit digits:

| Contract | Exact result |
|---|---|
| Largest residue width at the full 14,592-bit declared input width | k=28, p=180; child inputs at most **14,556 bits** |
| Next width, k=29 | p=179, but **15,011-bit** child inputs are attained; fails strict shrinkage |
| Largest fixed k valid throughout widths k+1 through 14,592 | **k=27** |
| k=28 at shorter widths | Works from 29 through 8,192; above that, only top digits of at least 29 bits work |
| Partial-top control n=65,k=29 | Actual maximal child **60 bits**; conservative bound 88 bits |

The last row is an admission missed by a conservative bound, not an error
in that bound. The unchanged predecessor's `strictly_smaller_child_bound`
receipt reports its conservative bound and is **not** an acceptance guard.
Its false value is retained in the new executed 65-bit control.

Put L=ceil(n/b), t=n-b(L-1), h=ceil(log2 L). The exact maximum packed
operand bit length is

    D_star = min(k,t) + (L-1)(2k+h).

The input 2^n-1 attains it. Strict recursion is exactly D_star<n.
[PROOF.md](PROOF.md) derives the general closed maximum-k formula and the
uniform finite-box implication using the inherited numerical proof premises.
The exact source certificate has least payload precision p=208-k for every
k=0..64. These are minima of this frozen sufficient certificate only.

## Evidence and replay

`RESULT.json` binds all 933,888 declared-width/residue-width pairs: 410,725
are strictly admissible. It records **599 conservative false rejections**,
all 65 exact precision boundaries and two actual Gaussian products.
The replay freshly certifies all three p=180 Gaussian operators, compares
their matrices and error bounds with precision transfer from p=256, then
executes maximal inputs at n=14,592/k=28 and n=65/k=29. Original-input
multiplication is used only as a postcheck after reconstruction.

`independent.py` imports neither the primary verifier nor any predecessor
executable. It separately enumerates the width domains, derives the exact
precision coefficients, checks 70 literal maximal packed words and compares
every shared arithmetic claim. Its complete receipt is
`INDEPENDENT-RESULT.json`. Its eight semantic controls and the actual CLI
source/precision/capacity/partial-top/receipt mutations survive normal and
optimized Python. The primary also checks the general size formula across
936 small (n,b) cases; the general theorem supplies the universal argument.

With standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-residue-shrink-window
```

The registered commands regenerate and compare receipts without writing to
this package. `verify.py --write` deliberately regenerates its own result;
`independent.py --write` creates an absent independent receipt. Ordinary
replay never treats stale PASS text as acceptance. No dependencies, Lean,
native compiler, selected-supplier or complete selected cold replay is needed.

`ORIGINS.json` binds retained PR3881 bytes by Git blob and SHA256 before any
import. The package-local `source/` closure is unchanged and replayable without
Git; `SOURCES.json` retains the originating main/catalogue provenance. Those
external PR objects are authenticated through retained bytes, rather than
claimed as locally reachable history. Prior checked main bindings at the
same base were reused; this work does not revalidate the selected construction.

## Limitations

The Gaussian numerical identity, interval arithmetic, operator proof, CRT and
carry theorem remain inherited premises; fresh finite operator checks and
actual executions do not constitute a new kernel proof. Q=448 working
enclosures are unchanged. The exact multiplication, packing, extraction,
lifting, all transforms and preparation remain paid. A smaller child and
lower payload precision alone imply no total runtime saving. The fixed
455-point box cannot serve an arbitrary-size recursive caller without new
geometry, complete recurrence and base cases.

## Open next questions

1. Can a complete physical caller exploit k=28 or the uninterrupted k=27
   tail after paying the whole invoice? First join an explicit tensor/CRT
   caller to this residue lane; physical composition and its cost inequality
   remain blockers.
2. Can another packing or numerical certificate improve the tradeoff?
   First specify the changed layout or enclosure and prove its true maximum
   child width. The k=29 exclusion here applies only to this literal layout
   and frozen certificate. Structured next steps are in `TASK.json`.

## Credit and disclosure

ToikY, with substantial OpenAI Codex assistance, including separately
implemented AI arithmetic verification and mathematical review. Apache-2.0.
No independent human or formal-kernel review is claimed.

Credit **Dugongue** for PR3881's paid residue lane, precision transfer and
finite-box recovery proof; **Mason Hale** for the complete certified Gaussian
backend and its normalization/CRT/carry path. Their unmodified notices in
`source/NOTICE.md` and `source/vendor/NOTICE.md` retain the Harvey–van der Hoeven,
frozen OpenAI source and community lineage. **Jose Manuel**'s PR3878 supplies
physical-caller context only; its separate compression/chirp/tensor joining
obligations are not closed here. PR3890 and the selected frontier are unchanged.
