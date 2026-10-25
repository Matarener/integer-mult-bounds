# A one-third fourth-entry fill at the pooled ceiling: conditional κ = 0.001730980255989036959962 − 10⁻⁴⁶ − 10⁻⁷⁰

**Author-checked conditional candidate; not maintainer-reviewed.** This package keeps PR4088's four words, native
receipts, clock (`ORDER.json`), template and plan unchanged. It changes only two things:

- **Selector.** It chooses which 1,080 of the 3,240 T360 calls use the four-entry word of their orientation. Here
  these are the calls at ticks t < 1080.
- **Fill.** It builds a new literal chronological owner fill for that selector.

| | PR4088 | this package |
|---|---|---|
| fourth-entry calls | 1,090 (`109·t mod 324 < 109`) | **1,080 (t < 1080)** |
| idle histogram | `{3:22783, 5:1625, 48:138492}` | `{3:22788, 5:1620, 48:138492}` |
| complete profile | `{1:8060060, 2:2310120, 3:751813, 4:327210, 5:66425, 8:25920, 48:138492}` | `{1:8060040, 2:2310120, 3:751788, 4:327240, 5:66420, 8:25920, 48:138492}` |
| root lower bound | 0.001730979115670792472760 | **0.001730980255989036959962** |

The gain is **+1.1403·10⁻⁹ over PR4088 (+0.0000659%)**. The root bracket
`[0.001730980255989036959962, 0.001730980255989036959963]` equals the sharp pooled ceiling that PR4091 proves for
this fixed two-provider invoice. PR4170 reported this as the remaining headroom, 1.1403·10⁻⁹. The fill therefore
attains that ceiling, and no other fill of these four words does better.

## Why PR4088 stopped at 1,090 calls, and the change here

At exactly one third of the calls, the window-free LP optimum is integral:

- 1,620 idle-5 bins of the form 32:(9,9,9);
- 22,788 idle-3 bins of the form 48:(9×5);
- 138,492 empty 48-bins.

On PR4088's arithmetic selector, the time windows make that optimum unreachable. Adapting the staged544-clock-ceiling
per-tick Hall LP to per-call supply rates the 109-mod rule at 1,080 calls at only 0.0017309790862. That is below
PR4088's root, which is why PR4088 moved to 1,090 calls.

The idle-5 bins close by about tick 208. They need early sevens and eights, which the arithmetic selector spreads too
thinly. Putting the fourth entry in the first 1,080 ticks instead makes the windowed LP reach the ceiling. The
reverse-time fill builder then gives an integral fill that attains it.

## Verification

```sh
python3.12 -B research/staged544-pooled-ceiling-fill/verify.py --controls   # ~8 s, standard library only
```

The verifier runs **PR4088's unchanged `owner_verify.walk`** with the t < 1080 dispatch. It checks every one of the
1,321,920 roles and 725,760 bins:

- chronology;
- same-call family distinctness;
- compact offsets;
- capacity;
- the complete histogram and rank mass.

It then encloses the new root with PR4088's vendored rational `exact_root.py` on the 10⁻²⁴ grid. It also re-certifies
PR4088's own bracket and checks strict improvement of the padded endpoint.

Six controls are rejected:

- PR4088's selector applied to this fill;
- one fourth-entry call reverted;
- a same-call family collision;
- an offset hole;
- the next grid point;
- PR4088's profile at the new root.

`construction/` holds the provenance tools. They are not run by the verifier and need numpy, scipy and highspy:

- `hall_mixed.py`: the staged544-clock-ceiling `hall_lp.py` with per-tick supply;
- `build_mixed.py`: its `build_fill.py` with per-call width vectors, run with `--distinct 40` on the selector file.

## Scope

All four words and their native evidence are PR4088's. This package adds no word or native change; the operator and
native claims are PR4088's. It inherits PR4088's conditional hypotheses, which are the uniform native, common-cover,
analytic, precision, tape, recovery and BIT transfer hypotheses.

The full ordinary/outer release has not been rerun for a mixed dispatch, as for PR4088 (see PR4165).

## Open next questions

- **Can the inherited release accept a mixed four-provider dispatch?** PR4165 shows that the inherited rebind stamps one
  width vector per provider. First step: generalize the rebind to per-call widths and rerun it on this fill.
- **Is there more to gain?** This fill attains PR4091's ceiling for these four words, so further gains need a changed
  word or inventory.

## Credit

- PR4088 (Cinna Davis / 1337isnot1337): the four-entry words, selector idea, owner walk and price.
- PR4091 (Ross Richardson): the sharp pooled optimum.
- PR4170 (Nick Petalas): the transfer audit.
- PR4085 (zxv): receiver sharing.
- PR4076, PR3945 and the staged544 lineage.
- The staged544-clock-ceiling package (ChaloupeMusic / Erwan Secousses): the Hall LP and reverse-time fill builder
  adapted here.

Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
