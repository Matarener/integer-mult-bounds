# Validation record

Base: `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority 8.
Interpreter: Python 3.12.14 from the registered Codex runtime, macOS arm64.

The official source export reproduces the published SHA256
`5a3046462b06c108e2853898c9daf4b466bc46f47e5f77983515b6e5e7ed5023`.
The input archive is retained in this branch before the audit code. The audit
checks all six nested manifests and payload digests without importing source
Python modules or extracting files to the workspace.

The standalone record run and the standard registered runner pass:

```sh
python3.12 -B research/p104-meeting-dual-audit/verify.py --record
python3.12 -B scripts/research_package.py --package research/p104-meeting-dual-audit
```

Markers: `PASS_P104_MEETING_DUAL_AUDIT` and `PASS_REGISTERED_RESEARCH_PACKAGE`.
Metadata and source pins also pass separately. Coverage includes all 23 cuts,
all 776 input columns and 602,176 coefficients, all actual COPY zero conditions,
20 source-specific negative controls and 4,369 dense-matrix oracle programs.
The word and entire witness match the source exactly. Both complete invoices
match their published source receipts. The new bill has 66,834 paid calls and
13,390 targets, with rank surplus 760.

The common invoice CLI accepts both generated files. Its concave-order result
is inconclusive, with hinges 72 at rank 1 and -72 at rank 2. This does not prove
a crossing of power tariffs or invalidate the source's pointwise improvement.
The audit does not run the source moment or compiler engines.

The scientific commit is `b482572647e1256affae014297de7b4e8632be50`.
The committed-byte and executable-mode preflight and the official 16-file export
pass. Its sealed replay passes under Python 3.12.14 with `-I -O -B`, no Git, empty
PATH, files mode 444 and directories mode 555. All 17 file bytes and modes,
including the export manifest, remain unchanged. Corrupting the actual source
archive rejects before evaluation. PORTABILITY.json records the export digest.
Only this validation text and the portability receipt change after that commit.

The final refresh at 17:36 UTC covers 327 open PRs, 5,137 Discussion records and
all 7,845 main notes. The matches are this investigation and the released source
handoffs. Main remains de5ec2e7a6074068452f45b1a191b5c72832df4a, priority 8.
See the canonical Discussion for the final publication head and readback status.

The optional complete
Git-history check is not run in this shallow checkout. The complete source
archive is retained and checked directly. Hosted scientific CI, native/compiler
admission and independent human review are separate.
