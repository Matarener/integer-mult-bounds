# Audit the native tensor cutoff and sharpen its one-axis case

This independently audits the phase-character, affine-separation and residue
arguments in Ali Romman's [PR #5369](https://github.com/CrocSwap/integer-mult-bounds/pull/5369),
Sections 2, 3 and 5. No gap was found under the stated hypotheses. A separate
exact implementation corroborates those implications, and the
[written proof](PROOF.md) gives a **sharp one-axis monomial test at widths
3,4,5,6**. Four tests and maximum width six are necessary; the source's
general sufficient bound gives 6,7,8,9 for this case.

The added one-axis result distinguishes two questions: realizing every phase
character with a spanning tuple, and faithfulness of the tensor representation.
The former is sufficient but can overestimate the latter. The complete
multiplication kappa and selected frontier are unchanged.

## Scope and sources

The [canonical claim and result](https://github.com/CrocSwap/integer-mult-bounds/discussions/5354#discussioncomment-19174027)
answers the [open independent-review handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19153575).
The original `formal-interface-lemma` card is retained in [TASK.json](TASK.json);
the scope is declared changed to this live mathematical audit before
formalization. No Lean build is claimed.

Base: current canonical main `32890bc5de034ab8fc93ac88ead7279a6a416d04`,
priority revision 7. The predecessor head is
`18354f41de4dc7bfda4692e814cf1d91a6d619ef`. [SOURCES.json](SOURCES.json)
pins its unchanged main-branch proof by Git blob and SHA256, plus the task and
selected-record provenance. The verifier authenticates the proof text on every
run. No predecessor executable, arithmetic library or fixture is imported.
The existing ledger's `partially_reviewed` archival status is not upgraded by
this contribution.

## Evidence and reproduction

Python 3.12, standard library only:

```sh
python -I -W error -B research/native-cutoff-independent-audit/verify.py
python -I -O -W error -B research/native-cutoff-independent-audit/verify.py
python -I -W error -B research/native-cutoff-independent-audit/audit_mutations.py
python -B scripts/research_package.py --package research/native-cutoff-independent-audit
```

The complete checker reports `PASS_NATIVE_CUTOFF_INDEPENDENT_AUDIT`; the
mutation driver reports `PASS_NATIVE_CUTOFF_AUDIT_MUTATIONS`. The registered
manifest runs both complete modes and the mutation driver. Section-only runs
are diagnostic and carry a different status. Each complete direct run takes
about five seconds on the local Windows environment.

[RESULT.json](RESULT.json) contains the identical normal/optimized result:

- **391,275 multisets**, exhausting all 2,192 phase characters on one, two and
  three axes. Reduction of positive multiplicities to 1..4 proves that the
  search contains a shortest spanning tuple for every character. This uses a
  different method from the predecessor's Gram-factor construction.
- **29,760 literal phase-generator probes**, including the padded tuples in
  the published four-width window; **200,378 affine-map restrictions** over
  every spanning support in the same domain.
- All **32 one-axis group elements**, with exact Gaussian rational ranks from
  **2,044 literal matrix-entry rows** at widths 1..9. The consecutive windows
  1..4, 2..5 and 3..6 have ranks 26, 30 and 32. An explicit residual vanishes
  at all positive widths below six and has entry **16** at width six.
- Controls for modulo-four counts, quadratic pair statistics, affine span,
  tensor-scaled constant phase, missing central residues and width-dependent
  coefficients.

[MUTATIONS.json](MUTATIONS.json) records **12 expected rejections**: five
mathematical code mutations and a changed proof byte, each tested in normal
and optimized mode in disposable copies. These remove a quadratic phase,
apply the constant only once, omit span, forbid multiplicity four, change the
sharpness projector, or corrupt the reviewed source. Each fails at its named
semantic/hash check. [EVIDENCE.json](EVIDENCE.json) identifies the local runtime.

The scoped registered replay, committed-byte comparison and whitespace check
pass. The official package exporter includes this package and its single
declared proof input; export integrity and complete normal/optimized direct
replays pass in a Git-free tree. The selected metadata baseline also passes;
that baseline is source-binding orientation, not a selected scientific replay.

For an exported tree, retain the repository-relative paths above and run the
direct commands. They require neither Git nor network access. Generic metadata
validation still needs the recorded Git objects. Full-history provenance
preflight was not run in this shallow checkout; the base and source are already
on canonical main. Hosted CI is separate from the local evidence.

## What remains unverified

The result is a separate agent-assisted proof review and finite exact check,
not independent human review or a formal proof kernel. It does not review
Section 6's coNP reduction, the general compiler or native composition code,
event8814's source adapter, physical cost/stock/precision, or a complete
supplier. No selected cold replay was run. The one-axis result is for the
monomial group; PR5376's larger full Clifford group has a different contract.
The least representation cutoff for n>=2 remains open here. The small
character minima are not asserted to be representation minima.

## Coordination and overlap

The initial completed snapshot searched 377 open PR bodies, 4,786 Discussion
records and all 7,402 tracked in-scope local notes, with complete reported
pagination/inventory and no coverage warnings (2026-10-25 06:11 UTC).
The direct canonical thread, central handoff, partially reviewed ledger entry
and the full relevant match set were inspected. PR5441 uses the predecessor's
source recipe for finite-memory lifting; PR5376 treats full Clifford operators.
Neither is this audit. The final refresh at 06:22 UTC covered 378 open PRs,
4,797 Discussion records and all 7,402 tracked base notes (plus this package's
two new notes), again with complete reported coverage and no warnings. Main
and priority revision remained unchanged.

That refresh found [Hiroki KUMAZAKI's complementary two-axis claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5354#discussioncomment-19174077).
It explicitly takes the n=2 representation-kernel question excluded here.
Our small character table is corroboration, not a competing n=2 cutoff claim.
These searches do not cover arbitrary diffs, all historical versions or
unpublished work, and do not establish novelty.

## Open next questions

1. Independently audit Section 6's reversible complexity reduction. Begin with
   the dirty controlled swap and permutation convention, then the balanced CNF
   size bound and implementation. This closes a separate proof obligation;
   it was deliberately left outside this session.
2. Audit the predecessor implementation against the established grammar at an
   actual source-bound caller, retaining every dirty input and return. Start
   with composition, inversion and self-query semantics. The present abstract
   audit and source hash cannot supply that implementation evidence.

Both questions and their blockers are also in TASK.json. Extending the small
census is not required for either one.

## Attribution

Prepared for Mihir Srivastava (@mihir-s-05) with substantial OpenAI Codex
assistance in proof review, implementation, verification and writing; one
agent. Ali Romman retains the general four-width theorem, constructive
witness and package. Jose Manuel's phase-sector and native-recipe work,
ywz65's affine-basis argument, Chris R's finite-alphabet tensor separation,
and the source lineage including Douglas Colkitt, JoyboyBrian and Cinna Davis
retain their credit. The associated interface work of zxv and Krzysztof Wójt
remains credited by the predecessor. Binary symmetric factorization, finite
Fourier inversion and central projectors are classical; no priority for those
tools is claimed. New prose and code are Apache-2.0; [LICENSE](LICENSE) is
included for standalone redistribution. No frozen source was changed.
