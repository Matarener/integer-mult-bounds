# Independent audit of GL3 right-translated support pruning

This checks one implication explicitly left for independent review by Brian Ross's PR4211, frozen at **ca0002008b497428f0b651501c4a220a9d2785e7**. The original ENCODING_AUDIT already states the support argument. This contribution independently checks its exact hypotheses, multiplication order, finite data and actual source implementation; it does not invent a new pruning method or recertify minimum nine. James Reed's earlier pin/seal/certificate-metadata review excludes this semantic layer.

## Exact implication and evidence

For every integer n>=0, every legal normalized word attaining diag([T0],[T1],[T2]), every cut0<=t<=n and entry(r,c),

```
support(S_t[r,c]) is contained in B_t intersect (B_(n-t) * T_c).
```

This is a RIGHT translate in the noncommutative address group. The written proof uses forward support propagation and reverses the involutory suffix before the diagonal target. Characteristic2 and involutory address labels give F²=I for F=I+([g]+[e])N; idempotence is part of the selected legal alphabet but is not needed for that particular square-zero argument. A noninvolutory address mutant, rather than merely a nonidempotent N, tests that premise.

The separately frozen implementation reads no predecessor source/checker. It independently enumerates168 elements, six CNOT labels and28rank-one idempotents. Cayley balls have sizes1,7,31,82,142,166,168. It checks168 symbolic factor involutions and84672 regular-module basis actions. For fixedtargets(1,4,3),(2,4,3),I at lengths7/8 it retains all153 cut/row/column support rows and defined cone edges (2362/4660, including stays). These masks are necessary supersets, not reachable-prefix classifications or a lower bound by themselves.

An actual legal two-call noncommuting word distinguishes B1*T from T*B1: g01=(3,2,4), g12=(1,6,4), T=g12*g01=(3,6,4). The valid cut containsg01, which the wrong translate removes. Additional legal dirty-restoring and mixed-register examples and the direct-nine positive word check exact parity group-algebra endpoints. The input model is the full group algebra F2[GL3(F2)], not its potentially aliasing natural3x3 representation.

The adapter intentionally reuses authenticated unchanged predecessor modules. It compares all153 support rows from both implementations, all117 actual interior CNF allocation rows/5247 state bits,1008 label translations and all ten direct-nine prefix matrices. It regenerates the length7/8 CNFs exactly:18882/30591variables,61138/97770clauses,1004699/1673686bytes, matching the recorded accepted-formula hashes. It does not solve those formulas or replay their proofs. Endpoint constants and full transition/Tseitin clause equivalence are not separately semantically audited here. Four controls expose wrong translate, an excluded legal prefix bit, wrong target and a noninvolutory address. The missing-bit diagnostic rejects an actual attaining prefix, not a solved mutant CNF.

## Reproduction and integrity

Python3.12, stdlib only; four normal/optimized registered commands:

```sh
python3.12 -B scripts/research_package.py --package research/gl3-support-cone-audit
```

Default runs write no package files. Source bytes and source origin credit are bound through SOURCE-PINS and a public unchanged-source ancestor. The local `.gitattributes` preserves immutable source bytes, including the original DIRECT_NINE.json CRLF container; regenerated CNF mathematical/formula byte comparisons are separate. The independent oracle's initial positive-example length metadata shadowed a loop variable. Separate review caught this before publication; revision2 changes only those four typed receipt fields, preserves original private freeze/history, and leaves cone/algebra data unchanged. The published revision2 code, receipts and review aliases are explicitly sealed.

## Remaining obligations

This audits necessary support pruning and its source binding. It does not independently certify every CNF gate/endpoint equivalence, free scalar-mixing normalization, any SAT solve/RUP proof, minimum-nine claim, changed target/alphabet, physical compiler/caller, supplier or multiplication theorem. No new kappa, frontier change or merge. Written and mechanical checks are not independent human or proof-assistant acceptance.

## Open next questions

Select one unclaimed remaining CNF clause/normalization implication at the frozen generator, then separately budget another-platform proof replay. Those links matter because correct necessary support alone cannot turn UNSAT formula certificates into an admitted model lower bound. Broader fixed-target searches require a fresh overlap and resource decision.

## Sources and credit

Brian Ross supplied the conceptual strategy, research direction and oversight for PR4211, with substantial OpenAI Codex implementation/checking/documentation assistance. Preserve Hanson Sun's seed18 and Josie Elliston's length10/three-register model lineage, the original support argument and all unchanged source NOTICE/license text. James Reed/rcfc-jreed's finite pin/seal audit (issuecomment6296495429) is separate. Classical support propagation, involutions and group algebra are not claimed as new general mathematics. This audit is by ToikY with substantial OpenAI Codex independently frozen implementation, source-reusing integration and separate proof/code review assistance. Apache-2.0.
