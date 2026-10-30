# Named-class C5 cancellation charge beats termwise `180/7`

After identical-support opposite-sign netting among the four named term classes
`{diagonal, J, off-diagonal, pairwise Gram}`, an explicit charging certificate
with weights summing to `9/4` dominates every 1- and 2-plane support rectangle
and credits each remaining net full-support term by `159/16`. The resulting
fit-level floors are

- **45** when no net `J` remains,
- **561/16** when exactly one net `J` remains,

both strictly above the classical termwise ceiling `180/7`. Dual scanners agree
on the `2,547,216`-rectangle census. Selected κ is unchanged at
`0.001672660197076918`.

This answers the cancellation-identity OQ left open by
`research/c5-fit-level-residual-charge` / [#3639](https://github.com/CrocSwap/integer-mult-bounds/pull/3639).
It does not reprint the residual/local-opt failure `460 > 224` as a new charge,
nor the termwise `180/7` bill.

[PROOF.md](PROOF.md) states the identity and corollary. RESULT.json records the
exact weights, `ρ = 303/16`, both floors and the diagonal / J-extension tariffs
`224` / `16097`.

## Evidence and reproduction

From the repository root, using standard-library CPython 3.12:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/c5-fit-level-cancellation-charge
```

Direct commands:

```sh
python3.12 -Werror -I -B research/c5-fit-level-cancellation-charge/verify.py
python3.12 -Werror -I -B research/c5-fit-level-cancellation-charge/independent.py
python3.12 -Werror -I -O -B research/c5-fit-level-cancellation-charge/test_verify.py
```

Expected markers:

```text
PASS_C5_FIT_LEVEL_CANCELLATION_CHARGE cycles=23 weight_sum=9/4 J_free_floor=45 one_J_floor=561/16 termwise_ceiling=180/7 beats=true
PASS_C5_FIT_LEVEL_CANCELLATION_CHARGE_INDEPENDENT cycles=23 weight_sum=9/4 J_free_floor=45 one_J_floor=561/16 termwise_ceiling=180/7 beats=true
```

Default verify is read-only and compares the committed RESULT.json. Admission
uses `need()` and still fires under `-O`.

## Open next questions

1. Does a cost-preserving reduction eliminate net full-support terms from every
   named-class exact fit, so the J-free floor 45 applies universally in this
   class?

## Credit

Nick Petalas (termwise charging obstruction/ceiling), Krzysztof Wójt
(four-residual floors), the residual/local-opt fit-level audit (#3639),
Tekalign/PR2782, Cinna Davis/PR1825, Adam Gall/PR1889, thakrarsagar/PR3256,
and the retained matching lineage. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.
