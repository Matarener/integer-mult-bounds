# Validation boundary

Author environment: macOS arm64, CPython 3.12.13. The verifier uses only the
standard library. The same assistant made the construction and these checks.
This is not an independent human review or a proof-kernel result.

The primary command passed with warnings treated as errors:

```sh
python3.12 -W error -B research/p104-accumulated-native-updates/verify.py --write
```

The output binds all three fixed transformations and all retained result fields.
It checks 798 input columns,636804 endpoint coefficients, a separate dense
transpose,2924 native maps and their absolute phases,1124 helper normalizers,
208 main adapters,1704 protected events and all 23 COPY values. The whole caller,
complete invoice, both rational interval engines, finite compiler and 54 strict
plus four functional outer checks pass. Every declared mutation control rejects.

The exact raw crossing is
`(0.00312336059973,0.00312336059974)`. The declared saving 0.00312336057 is
2.973e-11 to 2.974e-11 below it. The complete local ordinary allowance is 5548026;
the whole ordinary bound is 184647552. These are upper bounds, not measured
runtime or memory use. The compiler threshold is 80511200000000000.

Metadata and exact source pins pass:

```sh
python3 -B scripts/research_package.py --package research/p104-accumulated-native-updates --check-only
```

The registered command passed in normal and optimized Python modes:

```sh
python3.12 -B scripts/research_package.py --package research/p104-accumulated-native-updates
```

Both runs reproduced the retained outputs and passed every declared control.
The final marker was `PASS_REGISTERED_RESEARCH_PACKAGE`.

The publication receipt in the PR records committed-byte, deterministic export
and sealed replay checks after they complete. Hosted scientific CI and
independent acceptance are separate. The optional full-history preflight is
not claimed in this shallow checkout. The publication check covers direct
base and archive-commit ancestry.

The five selected framework assumptions remain. The large uniform word and
rounded multiplier are not materialized. No selected-frontier file is changed.
