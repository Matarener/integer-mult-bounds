# One F17 pair-kernel bill at the exact F0/B_1_2 entry width

**Switched card.** The selected stock coefficient is already registered:
Adam Gall's parent reserve gives conditional `sigma=8194`, Nick Petalas's
ceiling-free refinement gives `6748`, and the lcm-reserve package binds the
same depth recurrence to `269241600 |GL_64(F_q)| q^(4096(w-1))`. The complex
`m=73` coefficients `A`, `B` and `rho` are already recorded as unbound.
This package takes card `joint-query-controller` instead.

**Partial arithmetic bill; no new kappa.** For the literal exact producer
F0 followed by B_1_2, the inherited entry contract at

```text
lambda=1, f=64, e=0, beta=64, h=73
```

gives decoder width `W=532`. Under the incorporated runtime-exponent pair
model, the F17 zero-retention decoder's pair kernel costs at most

```text
26744256 lambda N D
```

gate evaluations, and its 464 named fields use at most

```text
493696 N D
```

data bits. The registered dirty-helper magnitude ledger does **not** supply
this width. The selected kappa remains `0.001672660197076918`.

```sh
python3.12 -I -B research/qq16-f17-pair-bill/verify.py
```

Expected:

```text
PASS_QQ16_F17_PAIR_BILL W=532 gates_per_pair=159192 pair_kernel=26744256*lambda*N*D field_bits=493696*N*D dirty_width=unsupplied control_gates=124028
```

## What is bound

The producer and the post-B1 norm `B=17628*H < 2^(e+15)` are Nick Petalas's
exact entry contract. The width chain `Q0=80`, `b=79`, `k=137`, `Qmax=497`,
`W=532` is that contract's published example, recomputed here. PR2807's
component and numerator bounds give signed pair inputs `w=W-3=529` and
`L=531`. PR2811's runtime gate formula then gives `159192` gates per pair.
The published control `L=455` still gives `124028` gates and kernel
coefficient `20836704`. The field-bit formula `2*464*N*D*W` is PR2807's.

The consumer is the PR2707 decoder: it reads the producer's F17 and
`F17 C_q^{-1}` charts and returns the original arrays in F17. The proof is
in [PROOF.md](PROOF.md). The receipt is [CERTIFICATE.json](CERTIFICATE.json).

## What the dirty ledger does not give

The rounded-producer envelope already records this producer's intermediate
magnitude and dirty-helper state, including the all-cut bound
`2^(delta+80) H`. It leaves the component grid and F17 consumption unknown.
PR2807 states that a norm bound alone does not determine the adaptive line
exponent. That is the obstruction: the dirty ledger cannot be substituted
for `E` and `Q0`. No second magnitude table is computed here.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/qq16-f17-pair-bill/verify.py
python3.12 -I -O -B research/qq16-f17-pair-bill/verify.py
python3.12 -I -B research/qq16-f17-pair-bill/independent.py
python3.12 -I -B research/qq16-f17-pair-bill/test_package.py
python3.12 -B scripts/research_package.py --package research/qq16-f17-pair-bill
```

Default verification is read-only. `--write` creates a missing certificate
and refuses to overwrite one.

## Open next questions

1. **Entry grid for the dirty ledger.** The question is which proved grid
   `2^{-Q0} Z` and exponent `E` the rounded F0/B_1_2 helpers actually meet.
   It matters because without them the pair-kernel count above does not
   apply to the noisy contract. The first step is to pin one finite producer
   implementation and prove its completed components lie on that grid. The
   blocker is that the rounded envelope leaves the grid unknown.

2. **The remaining physical terms at W=532.** Scans, scalar ADDs, wrappers,
   maps, addressing, movement and cleanup are still unpaid. The first step
   is to apply the incorporated finite-format operation counts at this width.
   The blocker is that the pair-circuit proof leaves those terms outside its
   gate count, and the navigation scan formula is a separate pending model.

3. **Whether the caller accepts F17.** A caller that needs the original
   `C_q`/`I` frames pays an additional frame conversion. The first step is
   to bind one admitted caller to either the F17 output contract or that
   adapter tariff. The blocker is that neither pinned word chooses the caller.

## Credit

Nick Petalas supplied the #2965 defect transfer, the exact F0/B_1_2 entry
contract, PR2807's finite format and PR2811's pair circuit, and the
rounded-producer magnitude ledger. ywz65 supplied the PR2707 F17 decoder.
Arham Tahir supplied the logical inverse that decoder lowers. Ali Romman and
the retained joint-query authors supplied the literal F0/B_1_2 words.
Adam Gall and Nick Petalas supplied the selected BIT stock coefficients that
this package does not repeat. Hiroki KUMAZAKI's cutoff chain remains the
stock-margin record. Predecessor files are unchanged.

Prepared by Wentao Li with substantial AI assistance.
No independent human review is claimed. New work is Apache-2.0.
