# One F17 block-scale scan at the exact F0/B_1_2 entry width

**Same card, one unpaid term.** #3374 already binds the F17 runtime pair
kernel and the 464-field bit count at `lambda=1`, `f=64`, `e=0`, `beta=64`,
`W=532`. This package prices the common block-scale **scan** at those
parameters. Selected kappa remains `0.001672660197076918`.

The incorporated scan polynomial, with `w=W-3=529` and `p=k=137`, gives one
owner-local line

```text
4232 D + 2415
```

gates. Across the 336-line decoder, one scan per line per owner, the scan
subtotal is

```text
1421952 N D + 811440 N
```

gate evaluations. The published `W=456` control remains
`1217664 N D + 666624 N`. The physical bill that changes is that scan
subtotal of the F17 direct Boolean arithmetic invoice.

```sh
python3.12 -I -B research/qq16-f17-scan-bill/verify.py
```

Expected:

```text
PASS_QQ16_F17_SCAN_BILL W=532 scan=1421952*N*D+811440*N control=1217664*N*D+666624*N no_new_kappa
```

## What is bound

`W=532` is the published example in Nick Petalas's exact F0/B_1_2 entry
contract. Arham Tahir's block-scale scan states

```text
G_scan(w,q,p) = w*(4q+2) - 2p + S(w-p) + 3
```

and binds `p=k`, `w=W-3`, `q=2D`, and one scan per line per owner on the
336-line decoder. The proof is in [PROOF.md](PROOF.md). The receipt is
[CERTIFICATE.json](CERTIFICATE.json).

## What stays unpaid

Scalar ADDs, wrappers, maps, addressing, movement and cleanup remain
outside this scan count. The pair-kernel and named-field coefficients stay
the submitted #3374 values.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/qq16-f17-scan-bill/verify.py
python3.12 -I -O -B research/qq16-f17-scan-bill/verify.py
python3.12 -I -B research/qq16-f17-scan-bill/independent.py
python3.12 -I -B research/qq16-f17-scan-bill/test_package.py
python3.12 -B scripts/research_package.py --package research/qq16-f17-scan-bill
```

Default verification is read-only. `--write` creates a missing certificate
and refuses to overwrite one.

## Open next questions

1. **Scalar ADDs under a width-dependent model.** The incorporated finite
   format already charges `5408*N*D` real ADD/subtracts, and that count does
   not use `W`. It matters because a Boolean ADD circuit at `w=529` would be
   a different unit from that real-operation count. The first step is to pin
   one incorporated ADD circuit whose gate count is a stated function of the
   component width. The blocker is that no such width-dependent ADD circuit
   is the formula already attached to these 2,704 sites.

2. **Wrappers and maps at W=532.** The scan proof leaves exact signed
   coordinate wrappers and the 464 full-cover maps as separate charges. The
   first step is to instantiate one pinned wrapper or map tariff at `w=529`.
   The blocker is that the scan invoice treats those permutations as unpaid
   routing.

3. **Addressing, movement and cleanup.** The scan model gives wires and
   fan-out for free and does not erase the exponent. The first step is to
   bind one admitted caller layout and charge address travel plus exponent
   cleanup in that layout. The blocker is that neither pinned word supplies
   that physical lifetime.

## Credit

Arham Tahir supplied the block-scale scan polynomial and its `W=456`
evaluation. Nick Petalas supplied the exact F0/B_1_2 entry contract and the
finite-format width `w=W-3`. ywz65 supplied the PR2707 F17 decoder. The
#3374 pair-kernel and field-bit coefficients are used only as the terms this
package does not recompute. Predecessor files are unchanged.

Prepared by Wentao Li with substantial AI assistance.
No independent human review is claimed. New work is Apache-2.0.
