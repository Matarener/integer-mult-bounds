# An alternate transfer for the failed shared-port star

The exact PR3547 star with marks E,F and ports G,F+G admits a GF4
support transfer. Replace its query E+F by E+wF, where w squared plus
w plus 1 is zero. Every source and reader implication then holds.
A separate written argument proves no transfer exists over F2 in any
ambient dimension. More generally, a characteristic-two transfer exists
exactly when the field has more than two elements.

The same map preserves the actual-reader pair floor m_A+m_B for arbitrary
finite three-terminal graphic attachments at these two ports, including
cycles and shared internal directions. This answers one explicit
[PR3547 handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/3547),
whose failure concerned a different fixed map. It is a scoped lower bound,
not a cheaper decoder or an improved multiplication exponent.

[PROOF.md](PROOF.md) contains the construction, the dimension-free binary
obstruction, all extremal premises, the graph projection argument and the
tariff consequence. [MAP.json](MAP.json) and [RESULT.json](RESULT.json)
contain exact finite data. The Gaussian and separate integer-minor/GF4
annihilator programs agree on all 64 star subsets and 256 implications.
The primary also checks 32 base and 16 difference-configuration subsets.
Eight optimized real-CLI corruptions must reject and eight restoration
runs must pass. The binary degeneration fails both reader conditions on
subset dbhy, mask 43. The programs certify finite premises; the written
proof supplies the statements over arbitrary fields, dimensions and graphs.

## Reproduce

From the repository root with CPython 3.12 and no third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/p112-alternate-star-transfer --check-only
python3.12 -B scripts/research_package.py --package research/p112-alternate-star-transfer
python3.12 -B scripts/check_research_commit.py --package research/p112-alternate-star-transfer --check-source-history
```

The registered commands are the following, also usable without Git in a
committed export containing the declared canonical proof input:

```sh
python3.12 -B research/p112-alternate-star-transfer/verify.py
python3.12 -B research/p112-alternate-star-transfer/independent.py
python3.12 -B research/p112-alternate-star-transfer/test_controls.py
```

Source pins are in [SOURCES.json](SOURCES.json). The actual used mathematical
premise is the generic support-to-tariff argument in the canonical retained
PR3506 proof. [ORIGINS.json](ORIGINS.json) gives its original source and
PR3547's exact witness origin commit, path, blob and SHA256. The pending
witness bytes are committed here unchanged, so scientific replay needs no
foreign Git object or network. No predecessor executable is imported.
Catalogue and selected-result pins record historical provenance only.

## Limits

Independent human and formal proof-kernel review are unclaimed. The old
field scope is characteristic zero. This proves one marked/port placement;
it does not classify the other 16 failed fixed-map cases, alternate scalings,
odd-characteristic old configurations, repeated attachments or larger
interfaces. The retained literal control still costs 14 against floor 4.
Acquisition, coefficient execution, dirty restoration, physical frames,
hosting, precision, stock, compiler/all-size admission, complete consumers
and both supplier invoices remain open. The selected frontier is unchanged.

## Open next questions

The structured questions in [TASK.json](TASK.json) ask for one other exact
failed placement, or a literal query/reader factorization outside the proved
family with a lower complete bill. Start by specifying all factors and
rectangular charges. This result does not justify another physical
construction round without a complete boundary and cost ledger.

## Credit

Nick Petalas. The source lineage retains Philippe Van Velzen's expanded
identity, ctoth's coverage question, PR3414/3463/3472/3489/3491/3505, and
Nick Petalas's PR3506/3524/3535/3547. The canonical retained proof contains
the detailed predecessor argument. Apache-2.0.
