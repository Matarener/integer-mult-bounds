# Original complex-controller owner/common-view refinement

Copyright 2026 Sagar Thakrar. Apache-2.0. Prepared with substantial OpenAI
Codex assistance, including separate same-session implementation and review
agents. Those reviews are not independent human acceptance.

This package independently binds the original R480/T16 controller in
[PR3385](https://github.com/CrocSwap/integer-mult-bounds/pull/3385), at
`7e5a187214126d31afc241a8f89f4a652352b58c`, to its owner/common-view
formulas. It reconstructs all **101,376 owner occurrences** across 144 calls,
including 32,256 data and 69,120 helper occurrences and 10,002 emitted helper
charts. No discrepancy was found in the scoped source expressions.

## Result

For common cover label `d` and owner chart `sigma`, the physical owner is
`d sigma^-1`. The source stores chart **columns** but multiplies **rows**:
passing `sigma_columns` to that multiplication already supplies the inverse.
The entrance is `X_(sigma^-1 eta_in) P_d^-1` and the exit is
`P_d X_(sigma^-1 eta_out)`. [PROOF.md](PROOF.md) derives these identities for
every orthogonal cover label and proves the packet partition, conditional
on the retained cover bijection, monomial, local-program and physical
ownership endpoints. It does not infer the universal identities from samples.

The existing source check tests the first forward/backward owner groups at
the identity cover. It also has a separate nonidentity terminal-translation
check. This audit adds complete owner reconstruction and a noncommuting
**owner-composition** check. For call 0, helper role 224, family 13006,
port 14, route `[3,4,0]`, using `d=T_15 T_30` sends basis vector `e_0` to
602 under the correct composition and to 518 under reversed composition.

The unchanged `SelectedBinding.group` constructs all 144 local groups.
A declared symbolic cover adapter retains exact matrices in place of
ordinal labels; it does not replace the source multiplication, wrappers
or opcode order. Independent column-vector calculations check every
selector and affine entrance/exit envelope. Each middle word equals the
entire pinned compiled local word; this equality does not verify the
local word's arithmetic. Two separate literal `rank`/`unrank` round trips
exercise the actual cover encoder.

Six in-memory source mutations reverse owner composition, transpose the
owner chart, reverse the entrance or exit direction, apply an extra cover to a data
translation, or add an alignment translation to helpers. All are rejected
by the semantic checks. A separate counterfeit-source control verifies
rejection before execution. Frozen source files remain byte-identical.

## Reproduction and provenance

From the repository root, with CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/complex-owner-view-refinement
```

[VERIFY.json](VERIFY.json) registers ordinary and isolated, optimized,
warnings-as-errors executions. Both passed on CPython 3.12.15/Linux;
the metadata check and frozen-source comparison also passed. [RESULT.json](RESULT.json) retains exact
inventory and group digests, the separating witness, ordinal receipts and
mutation outcomes. [SOURCES.json](SOURCES.json) pins the selected replay
archive and eight unchanged original-controller files. The archive loader
also authenticates its seven decoded members. No predecessor Python code
is executed from that archive.

Jose Manuel (`jmbarrancoml`) supplied PR3385 and its credited source chain.
[PR3106](https://github.com/CrocSwap/integer-mult-bounds/pull/3106) already
proves the identity-chart first scalar pair and a packet partition;
[PR2569](https://github.com/CrocSwap/integer-mult-bounds/pull/2569) already
establishes binary owner/common routing. This is independent source binding
and direction coverage for the original complex controller, not a new
routing identity. Frozen notices and predecessor attribution are retained.

## Limits

This is a written conditional refinement and finite source audit, not a
formal kernel proof or complete physical O73/GL64 payload. It does not
independently prove the full cover encoder, native child arithmetic,
physical monomial backend, production guard, complete cost invoice,
outer multiplication transfer, or a changed T74 controller. It changes
neither the selected frontier nor supplier admission.

## Open next questions

* Independently complete the original controller's fixed-prime factory and
  normalized-root refinement, preserving these endpoint assumptions.
* Once the changed T74 caller has a pinned artifact, check its own changed
  owner inventory and conventions. This original R480/T16 receipt does not
  transfer to that caller automatically.
