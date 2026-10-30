# Independent fixed source and typed-contact audit for PR5713

This package independently checks the fixed original-source premises behind [Ali Romman's PR5713](https://github.com/CrocSwap/integer-mult-bounds/pull/5713), head `a5348f7143f95fe0046b92b96172e30763c7d731`. It verifies the credited temporal identity's causal write, observer and owned-lifetime premises, together with every prescribed prospective contact of field 715. It does not independently admit the complete successor, its native provider or its price.

**Direct qualification completed:** the portable normal verifier, explicit `-O` verifier and all 12 synthetic controls passed their registered phases. Both positive runs reproduce the complete 17-field historical scientific projection, SHA256 `8ad201fe2ce3ebcbb0a081774790fd4511d3ecce1b5b5c1cee3dd9bde033895c`. A separate local AI postrun review accepted this exact limited result. Final publication, generic metadata validation, export and hosted replay are separate: none is claimed as completed here.

## Result and scope

The original independent local checker completed 25,451 PR5684 events and returned the real 23-entry scoped ledger. Portable normal and optimized runs reproduce all ten named predicates, the complete cuts/anchors/ledgers and the prescribed contact trace. The certificate checks:

- field 712's sole relevant write at 13572 and field 525's writes at 13737 and 14654;
- field 747's same live owned birth from 13565 at both reads;
- the protected field-715 interval and the actual common charts at cuts 823 and 14983;
- all 14 retained original field-715 contacts and four insertion contacts, including the retained destination ADD at 17439.

The actual event 11202 is `ADD 340,337,1@396`. It is nonblocking provenance. The needed condition is no write to 340 in `[14654,14983)`, fixed before the original execution and satisfied by the source. This clarifies a stronger earlier no-write wording; it is not an identity bug or a post-run boundary repair.

The author's relation is

$$
D=A-4(B+V)+C,\qquad V=A/4-B-D/4+C/4.
$$

[PROOF.md](PROOF.md) explains the conditional arbitrary-value transfer and its limits. No prefix matrix, 105-coordinate spanning assertion, author constructor or new mathematical identity is used by this checker. This is independent implementation evidence for the fixed causal and typing premises.

## Reproduction and exact sources

Python 3.12 and its standard library suffice. From the repository root:

```sh
python3 -B research/p104-temporal-fixed-independent-audit/verify.py research/p104-temporal-fixed-independent-audit/inputs/WORD.json.gz
python3 -O -B research/p104-temporal-fixed-independent-audit/verify.py research/p104-temporal-fixed-independent-audit/inputs/WORD.json.gz
python3 -B research/p104-temporal-fixed-independent-audit/controls.py research/p104-temporal-fixed-independent-audit/inputs/WORD.json.gz
```

The two verifier commands return `PASS_FIXED_CAUSAL_LEDGER_AND_TYPED_CONTACTS_ONLY`. The control command returns `PASS_EXPLICIT_PORTABLE_CONTROL_SET_ONLY`; every test record is labeled `SYNTHETIC_CONTROL_ONLY`. Controls authenticate and compile raw verifier bytes rather than import cached `verify.pyc`. The original fixed input is authenticated before any in-memory derivative. No original file is written, and there is no assert-only acceptance.

The original source is [PR5684](https://github.com/CrocSwap/integer-mult-bounds/pull/5684) at `d0f6fa2555410a1e23fe4191424c2097ab3d5d97`, path `research/p104-reframe-r22/WORD.json.gz`: 106613 compressed bytes, Git blob `f3fb0e2144ec8a5c3407e4eaa6528bb3436ba573`, SHA256 `d6db1d0d97b13ea483a462c65437664d15d34dec56c3682cf6e1de31266ec6c2`.

The three live inputs are retained in `Clear1nsight/integer-mult-bounds` at real commit `e8567c39feda6412a1e5a54e10aeb0a6d4d1e80c`, tree `7f4c2d03f0b44dfe7da32aaeffaf59f30d780582`: `inputs/WORD.json.gz`, [LICENSE](inputs/LICENSE) and [NOTICE](inputs/NOTICE). All are actively checked by length, SHA256 and Git blob; WORD is authenticated before decoding. The retention parent is PR5703's shared fix `475cfff509e3369926c5b2ee258fc8f1f9c3c6a1` over canonical base `df0137efd35e11b4445734bf612bdd4c7ebc330c`. Original PR5684 is descriptive source credit rather than an assumed reachable foreign dependency. No Git, network, author import or archive is needed by the standalone verifier.

## Qualification evidence

[PORTABLE-V2-OUTCOME.json](evidence/PORTABLE-V2-OUTCOME.json), SHA256 `7298b86c76e400876962c3daf8908a09694bee05501b8b0f62d2fd17d91c8fc8`, records the three real runs. [The static postrun review](evidence/PORTABLE-V2-POSTRUN-REVIEW.json), SHA256 `5162081de87c51ebb8dc3a8375513928ad1fb39226c60e7f9dfed78a4477f1ce`, accepts their limited scope. Root's acceptance hash `84d22f2e8f7c5bd3621064793de1dea4ce9a2363d8f1e7aad7a192cec4580666` identifies coordination metadata, not additional source science.

| Recorded phase | Child elapsed seconds | Sampled descendant RSS maximum, bytes | Result |
| --- | ---: | ---: | --- |
| Normal | 0.503533 | 26210304 | Narrow source/contact PASS |
| Explicit `-O` | 0.705401 | 29077504 | Same full scientific projection |
| Synthetic controls | 1.107103 | 27848704 | All 12 controls PASS |

All three children exited zero without termination. The recorded related child time is **2.8210496769752353 seconds**, including the original local run of 0.5050126829883084 seconds. This is child-time accounting, not complete orchestration wall time. RSS values are sampled maxima, not exact peaks or future performance guarantees. Root used phase caps of 45/45/60 seconds, 512 MiB limits and a shared 150-second budget, with serial execution and no retries.

The controls exercise predecode source rejection with zero gzip/decode calls; hidden 715 observation; 747 write/lifetime changes; a prospective-only retained contact; unknown semantics; nonblocking 11202 versus minimal 340 stability; and digest, status and full-projection validators. Each negative reaches its exact intended predicate/site. Synthetic rejection establishes no actual source counterexample or identity defect. Normal/optimized agreement is reproduction by the same scientific method, not a second independent method.

[The runtime summary](evidence/PORTABLE-V2-RUNTIME-SUMMARY.json) is explicitly **derived and privacy-filtered**, not an original raw guard or stdout. It retains actual original hashes. Private command/cwd/request/registration wrappers and raw guards are excluded. [The scientific extract](evidence/SCIENTIFIC-RECEIPT-EXTRACT.json) preserves all 17 historical scientific fields, excluding only explicit private source/binding and elapsed/runtime wrapper fields. Its own file hash is distinct from original stdout/body hashes. The postrun reviewer checked recorded evidence; it did not reread WORD or independently rehash the checkout.

`verify.py`, `controls.py`, fixtures and all retained input pins are byte-for-byte unchanged from qualified V2. [ADAPTATION.json](ADAPTATION.json) seals their identities and the scientific-core manifest. Their frozen preparation-time `UNRUN` headers and fixture status remain as historical input notices; actual execution status is recorded separately here and in qualification evidence. This final revision changes documentation/evidence/metadata only and performs no scientific rerun.

## Remaining boundaries

All five inherited assumptions remain: native all-column extension; owned allocation/erasure; uniform compiler/completion/splitting; precision/storage/fixed tape; and analytic decomposition/fine-prime/exact recovery.

This certificate does not establish emitted5713 equality, exact 3→396 native provider/absolute phase/all widths, a complete scalar endpoint matrix, owned-zero erasures, the physical caller, full invoice, both moment engines, ordinary/stock/precision/tape/BIT/compiler or 54+4 outer predicates. All eight owned H7 centre queries remain paid. PR5713's author-reported `.00310915222` and its raw invoice are unchanged. This certificate supplies no new saving or `.00311` admission. The selected record at the stated canonical main remains `.00310045`.

Root identifies [PR5717](https://github.com/CrocSwap/integer-mult-bounds/pull/5717) as external complementary caller/owned-lifetime evidence. Its externally reviewed head is `41fda9302e5de79911b0c91c6161beaf386798b3`. It is not a pinned input or replay by this package, and its scope must not be conflated with this fixed-715 audit or credited here as native/full-price admission.

A later construction, [PR5718](https://github.com/CrocSwap/integer-mult-bounds/pull/5718), flyingviper head `a1534ac45401c9a9c80c07aa65c89e00e33594f8`, reports conditional kappa `.00311024570` using distinct input/output helper bases. This is external author evidence, not this package's validation or gain. Its inserted events, new public helper and shifted owned labels mean the fixed event/field certificate here does not automatically transfer to that successor. The present package remains bound to PR5713 and its original PR5684 input.

`VERIFY.json` is ready/runnable metadata for the qualified commands. At the qualification snapshot, generic metadata, export and hosted checks were **NOT RUN**. This declaration claims no such pass; later publication evidence belongs to the PR and export records. The implementation commit, PR and CI identities remain pending until real values are supplied by root. Final byte/history/guidance/render/publication decisions remain separate.

## Open next questions

1. Does the emitted5713 artifact implement exactly the credited edit under complete native and caller contracts? A distinct scope must bind the emitted word, exact provider/phase/all-width and endpoint/erasure evidence before broader admission.
2. Are the final committed source/history metadata, replay selection and public rendering correct? Root must bind the actual implementation identity and choose applicable metadata/CI/render checks. Direct qualification does not answer these publication questions or grant an export/rerun.

These questions and the unchanged full original `p104-side-correction` card are in [TASK.json](TASK.json), with refined audit scope. No picker/reroll, Lean theorem or broad novelty claim is involved. Credit Ali Romman's temporal construction; Joel Pulikkan/GamingPuzzled with Claude assistance for R22; and the complete retained PR5678/5660/P104/native/helper/caller/compiler lineage. [NOTICE](NOTICE) preserves the original notice verbatim and appends the R22 and multi-agent OpenAI disclosures. Separate local AI reviews are not independent human or proof-kernel acceptance. Apache-2.0 applies.
