# D4 OPEN carriers and independent helper channels

For one fixed twelve-port D4 geometry, the four-helper OPEN bus factors exactly into the zero-helper public carrier plus four independent native rank-three helper channels. All 28 entering fields may contain arbitrary data. Explicit raw field swaps restore physical IDs, and no helper dirt enters the public response.

| Local word | Native child histogram | Rank mass | Public source/target residual ranks |
| --- | --- | ---: | --- |
| Zero-helper OPEN carrier | `{1:8,2:40,3:16}` | 136 | 5 / 5 |
| Full-source carrier variant | `{1:20,2:56,3:4}` | 144 | 7 / 5 |
| Four-helper OPEN bus | `{1:8,2:40,3:20}` | 148 | 5 / 5, plus four separate rank 3 channels |
| Bus with literal helper-return tail | `{1:8,2:40,3:24}` | 160 | 5 / 5, helpers returned identically |

These are complete local native-query profiles. OPEN and the full-source variant each use 60 signed complex additions and 16 complex negations; the bus uses 84 additions and 24 negations. These counts expand every raw field swap into three additions and one negation. Native lowering also exposes 128, 160, 136 and 144 nonidentity monomial legs respectively, with an explicit paid in-place implementation bound; they are not free. The full-source variant is a different word, not the literal inverse of OPEN. Its extra source progress is a resource for a possible changed caller; it does not establish such a caller.

## Exact boundary and normalization

Write `p,q,r` for the cyclic orthogonal port directions and use the exact invariant gauge `F=X33 F7`. Each source enters `C_p` and its paired target enters `C_q`. After ID cleanup, the physical public block is

```text
[[S_p, 0], [J_p, T_p]],
T_p = F C_p^-1 C_q^-1,    J_p = F X_p.
```

The OPEN source channel S_p has rank 5. The carrier changes the source endpoint and must be consumed under that contract. Native-query products attached to fixed physical IDs have different ranks from the moved-value channels after cleanup; these are recorded separately and cannot be substituted in an owner invoice. The bus has exactly the same public block, direct-summed with four independent helper operators of rank 3. Counting those helper channels as public completion while retaining their helper-progress credit would count the same resource twice. The isolated helper output is H_j h_j, not the original physical value h_j. An explicit optional four-query inverse tail returns all helper values identically at an additional rank mass 12, giving 160 in total and leaving no helper-progress credit. Coupled global helper exchange is outside this factorization.

A written split-Lagrangian lemma proves a common-F monomial normalization criterion in all dimensions. Eight A/B ports use an explicit star involution, proved with its exact phase condition. Four frozen C-port witnesses handle the remaining ports. All twelve give normalized forward and backward boundaries

```text
F_K = [[T, 0], [T K, T]],
B_K = [[T, -T K^-1], [0, T]].
```

Physical K and logical A are distinct: `A=C_q^-1 K C_p`. The same logical pre-X and post-Y `A^-1` wrappers work in both orientations. Every inverse-B wrapper is retained and lowered explicitly to monomials; native rank zero means a paid address/phase scan, not a free operation. A separate all-dimension lemma proves that the output inverse-B wrapper is always monomial under the native common-F hypotheses. For the C ports, only the input inverse-B wrapper needs the four explicit witness checks; both wrappers still carry their paid scans. The eight A/B ports use only address involutions and translations: their exact two-cycle counts give an in-place O(fN) address scan, with no extra complex field, for N=2^(7f).

## Evidence and reproduction

With CPython 3.12 and its standard library, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/d4-open-carrier-interfaces
```

The registered commands authenticate all frozen inputs, replay the literal native words and normalization witnesses, compare complete deterministic records, and run actual defect-sensitive controls. Generated output goes to external temporary directories. The new checkers use the authenticated compiler source with assertions enabled even under optimized Python. [EVIDENCE-INDEX.md](EVIDENCE-INDEX.md) distinguishes fresh replay from preserved historical context.

[PROOF-NATIVE.md](PROOF-NATIVE.md) gives the arbitrary-input maps, local native and scalar bills, and exact phase checks. [PROOF-NORMALIZATION.md](PROOF-NORMALIZATION.md) gives the general lemma and the four C-port orientation/cut contracts. [PROOF-STARS.md](PROOF-STARS.md) closes the eight A/B ports. [OUTPUT-WRAPPER-LEMMA.md](OUTPUT-WRAPPER-LEMMA.md) proves the general output-wrapper result. Their tensor extensions apply to every chunk size; no four-term one-column expansion is charged as four scalar operations for all chunks.

## Scope and limits

The geometry is twelve ports in h7. It does not supply uniform h7 source widths for all 112 original P112 ports. The old 9D endpoint, batching and contact results are separate; the larger parent tiling has 120 labels with eight omitted ports.

This is an exact local interface and factorization. No global routed caller, ownership allocation, rounded child-error bound, physical tape implementation or improved kappa is established. In particular, common code left by successive local calls must either be consumed legally or decoded at its actual chronological cut. Extra source progress and separated helper channels do not by themselves pay that debt.

## Open next questions

1. Can a complete routed caller use these changed endpoints with a favorable fully charged bill? Specify actual source windows, common-code cuts, terminal completion and helper ownership before optimizing it.
2. Can that chosen caller satisfy the rounded and physical contracts? Derive its prefix/grid and child-error bounds, all address/phase scans, storage, copying and head return.

## Sources and credit

Scientific source pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The exact native compiler and original PR531/PR533/kernel92 credit chain are preserved in [NOTICE.md](NOTICE.md) and frozen/notices. The earlier local construction and witness files remain unchanged under frozen/history. This work does not claim priority for standard Clifford normalization, tensor identities or symplectic linear algebra.

Prepared by Ross Richardson with substantial OpenAI Codex assistance in construction, separate mathematical reviews and publication. AI review is not independent human or formal-kernel acceptance. Apache-2.0.
