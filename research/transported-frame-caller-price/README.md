# Transported-frame caller price

**Negative result. No new κ.** Selected κ stays `0.001672660197076918`.

## Scope and evidence

Original card: `scalar-to-moment`, scope **changed**. The card asks whether one
scalar simplification improves a paid profile. This package prices the
alternative left by Discussion #1166 comment 19034220 after the moved-ADD pair
was already priced: one compatible transported-native frame under PR #3929,
including entrance, terminal, and caller changes.

The frame is warp 0 on lender 243 in the published recipe. The entrance basis
goes from `(261, 133, 85, 45)` to `(258, 130, 82, 42, 7)`, and the exit basis
goes from `(320, 192, 45, 30)` to `(320, 192, 42, 25, 7)`. The native map is
unchanged. All 36 scalar edits are in section B.

On the vendored base word:

- The entrance charge is one identity scale, `['scale', 243, 1, 1, entrance]`,
  at new B index 916. Its own climb is `+1 H1`. The warp position moves from
  916 to 917.
- Caller fields `ports`, `start_extra`, `helper_final`, `target_levels`,
  `cut`, `precondition`, `compensation`, `centers`, `center_frames`,
  `initial_corrections`, `A`, `restore`, `removed`, and `prelude_events` are
  unchanged. The caller adds no child.
- Terminal end-climbs stay `H1: 289`, `H2: 77`, `H3: 54`. Restore is unchanged.
  Cleanup gains exactly one inverse scale, `(scale, 243, 1, 1)`, and no other
  opcode or frame.
- The forward histogram changes by `+28 H1 − 16 H2 − 4 H3 + 4 H4`: the entrance
  scale, `+11 H1 − 4 H3 + 4 H4` at edited B indices, and `+16 H1 − 16 H2` on
  later unedited B climbs. Rank mass stays 5134. The width inventory stays
  `{4: 26, 5: 2, 6: 18, 7: 53, 8: 96, 9: 213}`.

[PROOF.md](PROOF.md) shows this delta is strictly positive for every power
tariff `r^q` with `q ∈ [0, 1)`, and zero at the rank-mass tariff `q = 1`. The
zero caller and terminal end-climb deltas cannot reverse that sign.

PR #3933 already proved that the least legal completion of this entrance also
loses, and that these published non-minimal frames cost less than that
completion while still losing. This package does not repeat the 374-superframe
census. It separates the entrance, terminal, and caller charges that #3933
left unitemized; that note records no physical caller invoice.

The base word label is `PR2312-width-exchange-plus-coherent-joint616`. Bytes
are the PR #3929 head `0c0e31cf12e8f4f07e8419a6d33ae85129fb5a01` files
`inputs/BASE-WORD.json.gz`, `inputs/RECIPE.json`, and `vendor/audit_core.py`.
SHA256 pins are checked by `verify.py`. Catalogue provenance is in
[SOURCES.json](SOURCES.json).

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/transported-frame-caller-price
```

Direct check:

```sh
python3.12 -B research/transported-frame-caller-price/verify.py
```

Observed marker:

`PASS_TRANSPORTED_FRAME_CALLER_PRICE entrance=+1H1 terminal_end_climbs=0 caller_fields=0 histogram=+28H1-16H2-4H3+4H4 mass=5134 power_tariff_strict_for_q_in_[0,1) no_new_kappa`

Not run: native phase replay, an owner fill against PR #3945, a selected cold
replay, Lean, or Docker. The power-tariff sign is the argument in PROOF.md;
the verifier checks the integer hypotheses that argument cites.

## Open next questions

1. Does any warp other than warp 0 have a compatible transported entrance
   whose entrance, terminal, and caller bill lowers a power tariff? First
   step: one later warp's maximal legal superframe, with the identity scale
   and end-climbs charged before native replay. Blocker: the other 71 warps
   are not searched here.
2. Can PR #3945's idle-owner fill absorb `+28 H1` without a new slot? First
   step: add this exact child delta to the pinned #3945 profile. Blocker: that
   word is not an input of this package.

## Credit

Dugongue, PR #3929, for the transported-frame recipe, compiler, and base word.
Sagar Thakrar for `audit_core.py`, following Arham Tahir's BORROW-WORD reading.
The word label credits the PR #2312 lineage; dataisfire, PR #3734, is the
staged544 provider context of the handoff. ToikY, PR #3933, for the entrance-cap
obstruction that this note does not re-derive. Chris R / Clear1nsight, discussion
comment 19034220, for the requested three-part price. Prepared by unpaidmoon
with substantial Cursor Grok assistance. Apache-2.0. No independent human or
formal-kernel review is claimed.
