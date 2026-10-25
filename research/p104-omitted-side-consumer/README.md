# One straight-line consumer of `(N-P) ⊗ M`

**Partial scalar bill. No new κ.** Selected κ stays `0.001672660197076918`.

Discussion comment 19056819 asked for a price of one repeated consumer of
`(N-P) ⊗ M` before the Gram addition saving is treated as paid. This package
gives that price for one 104×104 bank, in the unit-addition model of PR #3996.
It is not a minimum, a native rank bill, or a supplier.

## Scope

The card `p104-side-correction` asks for a chronological endpoint correction.
Scope is **changed**. The object here is the omitted identity side named in
PR #3996's proof, not a flag program and not a replay of its 763,392 events.

On the canonical fixture
`research/p104-native-channel/inputs/P104-FIXTURE.json`
(SHA256 `516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4`),
the ordered ports give an 8×96 matrix `B2` whose ASCII digest is
`88e9a726e8c8aec055bfd7cd024883b5c8ecbda0cd6471e591a08c43a108a535`.
Every entry is in `{0, ±1}`, there are 384 nonzeros, each row has weight 48,
each column has weight 4, and `B2 B2^t = 48 I`. Write `B = B2/2`,
`U = [I, B; 0, I]`, `A = U^t P U`, `M = U U^t`, and
`N - P = U^{-t}(I - A)U^{-1}`. The checker re-derives `A^2 = 13A`.

The index convention of PR #3996 sends `(N-P) ⊗ M` to the bank map
`(N-P) X M`, because `M` is symmetric. One straight-line program computes it
by the shears:

- right-multiply by `M = U U^t` with two `B2` matvecs per row (768 additions);
- left-multiply by `N-P` with three `B2` matvecs per column (1152 additions).

The closed form used for the second step is

```text
(N-P)(v1, v2) = (-B v2, v2 - B^t v1 + B^t B v2).
```

`B v2` is stored once and reused. Each matvec applies every nonzero of `B2`
once, as a `±1` multiple of one coordinate. The program is straight-line:
every bank pays the same count,

```text
104 * (2 + 3) * 384 = 199680
```

unit additions. Dyadic divisions by 2 and 4 restore the scale. They are not
included in this count, and the half/double column of PR #3996 is not
re-derived. The same program matches the integer operators `4(N-P)` and `4M`
on the all-ones bank, a single-spike bank, and one dense modular bank.
Dropping `B^t B v2` breaks that identity. The zero bank is the zero bank and
still executes 199680 additions.

## Comparison with the published Gram gap

PR #3996's unit-addition invoices are entry plus exit `319488`, one coded
Gram pair `26240`, and one specified reference pair `241280`. For `k`
uncorrected pairs the gap is

```text
241280 k - 319488 - 26240 k = 215040 k - 319488.
```

That is `-104448` at one pair and **`110592` at two pairs**. Paying this
consumer once against the two-pair saving leaves

```text
110592 - 199680 = -89088.
```

At three pairs the same one-time payment leaves `+125952`. The other omitted
side `M ⊗ (N-P)` has the same straight-line count by swapping axes. Charging
both, once each, costs `399360` additions. One coded pair plus both sides is
`425600` additions, which is already above one reference pair (`241280`),
before the entry/exit cost.

This does **not** prove that every program for `(N-P) ⊗ M` costs at least
`199680`, and it does not price native children, owners, or frames. A cheaper
program remains the first open question. Until one exists, the two-pair Gram
gap is not a paid saving.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B research/p104-omitted-side-consumer/verify.py
python3.12 -B research/p104-omitted-side-consumer/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-omitted-side-consumer
```

Expected marker:

```text
PASS_P104_OMITTED_SIDE_CONSUMER
```

with `adds_one_side` 199680, `k2_net_after_one_side` -89088, and
`new_kappa` false.

## Open next questions

1. Is there a straight-line program for one bank of `(N-P) ⊗ M` with fewer
   than 110592 unit additions in this `B2` model? The number above is one
   program, not a lower bound.
2. Can the two omitted sides share shears? Independent charging may
   double-count, which matters for the comparison with one 241280-addition
   reference pair.

## Credit

The omitted-side formulas, the index, and the 110592-addition gap are ToikY's
PR #3996 audit of Chris R / Clear1nsight's PR #3979. The fixture and root
normalization are the retained P104 native channel (Rohan Arun, Chafik
Boukhalfa, Adam Gall, and the native/E8 lineage named there). The request to
price the consumer is discussion comment 19056819.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review is claimed.
