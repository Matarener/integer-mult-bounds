# Reproduction record

Local registered replay: CPython 3.12.14, numpy 2.3.5, 2026-10-19,
commit `75d0f95418487f7061dbea204cda866036bff393`.

```
python3.12 -B scripts/research_package.py --package research/unconditional-batched-crt --check-only
python3.12 -B scripts/research_package.py --package research/unconditional-batched-crt
python3.12 -B scripts/check_research_commit.py --package research/unconditional-batched-crt --check-source-history
```

Results:

- Metadata and all declared pins: pass.
- Working/committed bytes and declared source ancestry: pass, 393 files
  before this record was added. Source commits are `bb4bccbf42844d2801487450727c2f63e10d1d0f`
  and `72d7efc181edb21806a878f174847c96dd410ab0`.
- All seven registered commands: pass. Source binding covers 354 live
  inputs, seven immutable exports and both fresh five-stage THREE receipts.
- Complete recursive prime certificate: pass.
- Exact root, BIT moments, twelve cost rows, fifteen side conditions,
  obsolete-route rejection and scalar hygiene: pass, normal and optimized.
- Batched CRT controls and complete compact CRT composition: pass.
- Retained current-value union schedule: pass.

Exported predecessor sources preserve their original bytes, including CRLF,
using the package-local .gitattributes. A transport-only initial commit
normalized three exports; the tested commit above restores their exact bytes.

Canonical main was refreshed at submission preparation and remains
`bb4bccbf42844d2801487450727c2f63e10d1d0f`. Latest PRs through #4099
were checked. #4097 excludes two further helper-544 interfaces; #4098 and
#4099 prove diagonal-call lower bounds. None supplies a stronger kappa.
#4091's larger pooled relaxation root has no feasible chronological supplier
and is not treated as an attained exponent. The exact comparison benchmark
is the published conditional result in #4088.

These are executable and source-transport results. The all-size theorem
is the mathematical argument in PROOF.md and its dependencies, not a
consequence of these pass labels. AUDIT.md records the earlier incomplete
physical simulations and the absence of independent or formal acceptance.
