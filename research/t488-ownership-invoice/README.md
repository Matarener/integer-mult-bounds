# T488 ownership invoice

**Audit of one published histogram. No new κ.** Selected κ stays
`0.001672660197076918`.

## Scope and evidence

Original card: `scalar-to-moment`. Scope is **changed**: Discussion #1166
comment 19022532, question 1, asks for an invoice-level audit of the composed
T488 package's literal ownership and outputs against its published profile.
Question 2, the packing-vertex saturation, is already PR #3796 and is not
repeated here.

Predecessor: PR #3653 (`research/retimed-t488-composition`), publication head
`607a09ff441c79b215a8127a81f4cc70021d0d9b`, by Rohan Arun / roger-sato, with
the PR #3633 owner certificate and the PR #3642 retimed words. The arithmetic
reproduction in PR #3740 explicitly left this ownership invoice open.

The vendored inputs are byte copies of that head:

| File | SHA-256 |
|---|---|
| `inputs/checked-base-CANONICAL-WORD.json.gz` | `ba1e3767f52c849c49d7d3852b879d9562265f1f51d15ca40421c51cae0aae6a` |
| `inputs/checked-extra-CANONICAL-WORD.json.gz` | `f30605f35030460f18b053dbd6031e862bf3c6661141d481d54ffdc1e8d1ad01` |
| `inputs/PROVIDERS.json` | `d96f2798024ab83edbb8848b62c425992aec182f1f24ef46bb8286dd390618c2` |
| `inputs/CANDIDATE.json` | `fbdda845beac5bba9baa4b1b8c8f596e98f70b59e1d60ebf4f4d3e8758631bfd` |

These objects are not on canonical main `bb4bccbf42844d2801487450727c2f63e10d1d0f`,
so they are copied into the package rather than pinned as `base_commit` paths.
The verifier checks the hashes above.

**Established.** Both retimed canonical words have 408 helpers. For each helper,
the rank of its final frame minus the rank of its start frame equals that
provider's literal width, index by index (`gauge44` for the base word, `extra`
for the other). The two frame tables differ at index 300 only, both of rank 4,
and that index is not a helper entrance or final frame. The stored local bill
on both words is `{1:2437, 2:724, 3:226, 4:102, 5:20, 8:8}`. The owner
certificate's local bill and both provider `actual_paid_profile` maps are
`{1:2439, 2:726, 3:224, 4:102, 5:20, 8:8}`. The per-call delta is
`-2` rank 1, `-2` rank 2, `+2` rank 3, and its rank mass is 0.

With `4392 = 9 * 488` calls, the certificate profile plus `4392` times that
delta is exactly the published histogram

```text
{1:10817496, 2:3179808, 3:1024434, 4:447984, 5:94794, 8:35136, 48:186782}
```

The idle residual, `profile - calls * local`, is the same before and after the
delta: `{1:114192, 3:31842, 5:6954, 48:186782}`. Rank mass stays
`65088 * 488 = 31762944`. The published physical count `437757` equals
`896 * 488 + 509`. Placed helper width per call is `3279`, a different ledger
from the local child bill.

**Not established.** The 1,791,936 literal rows were not regenerated, and this
package does not import `owners/run.py` or `independent_literal.py`. The
predecessor profile is the certificate value. The stored `local_profile` field
is cross-checked, not re-derived by a gate climb. No native admission, no
moment bracket, and no selected-frontier change.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 scripts/research_package.py --package research/t488-ownership-invoice --check-only
python3.12 -B scripts/research_package.py --package research/t488-ownership-invoice
```

Expected marker: `PASS_T488_OWNERSHIP_INVOICE` with `rows_regenerated=false`
and `no_new_kappa=true`. One incremented helper width and one incremented
published count are rejected in memory.

## Open next questions

1. Sum residual capacities from a fresh `FILL.json.gz` and compare them with
   `{1:114192, 3:31842, 5:6954, 48:186782}` without reading `CANDIDATE.profile`.
   That closes the certificate-versus-rows gap. The blocker is the
   several-minute integral-network expander in PR #3653.
2. Climb the canonical gate frames, including warps and centre charges, and
   compare the resulting child histogram with the stored local bill. Helper
   output widths do not determine that bill. The blocker is that the canonical
   encoding is not the borrow-word schedule already checked by the local proof.

## Credit

PR #3633 supplies the T488 owner certificate. PR #3642 supplies the retimed
words. PR #3653 publishes the composed profile and its own owner replay.
PR #3740 records the open invoice question, and PR #3796 closes the separate
saturation question. Prepared by unpaidmoon with substantial Cursor Grok
assistance. Apache-2.0.
