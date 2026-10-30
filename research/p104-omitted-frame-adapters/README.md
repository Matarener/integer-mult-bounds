# Exact P104 omitted endpoint adapters

PR3462's normalized endpoint correction leaves 93 physical chart changes unpaid.
This package supplies exact native recipes for all of them and proves their
sharp bank-local native-only tariff. It closes that adapter cost obligation.

The profile is 52 rank-eight calls and 41 rank-nine calls, with total rank mass
785. For every real `0 <= s <= 1`, the sharp tariff is `52*8^s + 41*9^s`
when rank-t native calls cost `t^s` and monomial Cliffords are free. This is a
lower bound and matching construction for separate nine-axis bank-local
Clifford words. Cross-bank operations and chart changes performed inside the
scalar completion are outside the optimality claim.

[PROOF.md](PROOF.md) defines the projection, exact endpoint maps, tariff model,
rank-potential proof and remaining cost ledger. [ADAPTERS.json](ADAPTERS.json)
contains every bank, initial/final frame, all 53 distinct explicit recipes,
signed Pauli and exact anchor certificates, and dense Gaussian execution hashes.
The projection is reconstructed from the original source, with the published
4,027-event/265-input closure digest. None of its retained events targets an
omitted bank. The 41 banks with zero normalized scalar residual still require
physical adapters.

The retained source compiler synthesizes the recipes. A separate unchanged
PR3416 checker verifies all 18 signed Pauli generators and an exact 512-entry
anchor for each requested map. It also checks a dense arbitrary Gaussian payload
and exact inverse restoration. The rank floor is independently eliminated from
the requested map. Controls reject a global-phase fault that preserves the
tableau, wrong ranks, wrong endpoints and wrapper phases, damaged receipts,
changed/missing source bytes, and a damaged frozen checker. These are finite
exact certificates plus a written tariff proof, not formal kernel acceptance.

## Reproduction

Use Python 3.12 and only its standard library, from the repository root:

```sh
python3.12 -I -Werror -B research/p104-omitted-frame-adapters/verify.py
python3.12 -I -O -Werror -B research/p104-omitted-frame-adapters/verify.py
python3.12 -I -O -Werror -B research/p104-omitted-frame-adapters/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-omitted-frame-adapters
python3.12 -B scripts/check_research_commit.py --package research/p104-omitted-frame-adapters --check-source-history
```

Set TMPDIR to an owned external directory for disposable CLI fixtures.
The registered replay declares all three live canonical inputs. SOURCES.json
pins their original bytes and the task catalogue at canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
The separate PR3416 checker is retained byte for byte inside this package, with
its source URL/head/hash in inputs/ORIGINS.json. Runtime never consults Git,
pending branches or network services. The receipt can be regenerated with
`verify.py --write-receipt PATH`; compare the complete JSON content.

## Limits and stop decision

These recipes implement the exact endpoint map on every complex payload.
They do not implement PR3462's scalar correction, its normalized half-readouts
or a paid caller. Monomial wrappers have real physical costs outside this
native-only tariff. Routing/ownership, common-frame accesses, precision/tape,
idle/cleanup costs, the consumer, full recursive bill and all-size transfer
remain open. The original 473 omitted transport events are interleaved with
other operations and are not a replaceable standalone adapter program.
No runtime speedup follows from the 93-call endpoint certificate.

Stop after this local adapter obligation. The unchanged-profile supplier stop
remains. No supplier, improved kappa or selected-frontier change is claimed.
Independent human and formal proof-kernel review are unclaimed.
Engineering checks and justified retained-code limits are in ENGINEERING.md.

## Open next questions

Can an actual paid caller produce the scalar completion and its common-frame
readouts while paying this adapter profile? Start with the actual retained Y
dimension-eight endpoints and the listed omitted-bank endpoints. Include every
conversion, weighted scalar expansion, dirty restoration, routing and consumer
action in one invoice. Missing ownership, numerical execution or a favorable
complete cost blocks supplier admission. TASK.json records this bounded handoff.

## Attribution

Nick Petalas. Apache-2.0. Hiroki Kumazaki's PR3446 supplies the projection and
released recipient-history handoff. PR3462 supplies the normalized completion
and identifies this unpaid frame boundary. Clear1nsight's PR3382/3423 supplies
the open-port Newton producer/consumer lineage. ywz65's PR2586/2497 supplies
the original physical/logical P104 word; Arham Tahir's PR2665 lineage retains
the exact source bytes. Nick Petalas's PR3416 supplies the separate covariance
checker, retained unchanged here. PR3466 and Clear1nsight's concurrent PR3467
address correlated entrance conditions and encoding, rather than these adapters.

The canonical retained Gaussian Clifford compiler is reused unchanged from
Jeremy Kothe's gmx-t74-borrow43-handoff source lineage. The original native,
geometry, Lemma G and compiler contributors, including DreamingOfClouds,
Vasek and Douglas Colkitt, retain their source-specific credit. Exact source
paths, hashes and originating published heads remain inspectable; no frozen
predecessor input or notice is altered.
