# Conditional kappa 0.00304057 from a productive P104 caller

This construction gives **conditional kappa = 304057/100000000 = 0.00304057**.
It improves the selected
[PR #5413](https://github.com/CrocSwap/integer-mult-bounds/pull/5413)
value 0.003027288235 by **0.000013281765**, about **0.439%**. The complete
recursive profile changes. This is not extra precision on the old crossing.
The selected files and other contributors' work stay unchanged.

The contribution binds the completed P104 word from
[PR #2305](https://github.com/CrocSwap/integer-mult-bounds/pull/2305)
to the current mixed-target recursion. Its 527 independent helper outputs
receive their actual Gaussian target ranks. An explicit caller uses that
published forward word at all 18 full sites. Signed exchanges and central-square
translations supply the sixteen backward interfaces. The word's COPY and
CLEAR operations do not need an instruction-level transpose.

Read [the proof and full cost boundary](PROOF.md),
[the complete receipt](RESULT.json), [the emitted local word](WORD.json.gz),
[the emitted caller](CONTROLLER.json), and [exact source pins](SOURCES.json).
The source circuit and private reuse are credited predecessor results.
The new result is their physical caller and complete productive admission.

| Verified quantity | Result |
| --- | ---: |
| Independent local public inputs | 735 |
| Productive helpers per full call | 527 |
| Owned lifetimes / peak owned fields | 8 / 1 |
| Full calls / thin calls / whole idle jobs | 18 / 15 / 3,120 |
| Complete paid calls / productive fields | 69,930 / 12,814 |
| Complete rank-mass surplus | 760 |
| Native paid and helper maps / main adapters | 2,981 / 208 |
| Physical caller boundary contacts | 7,488 |
| Crossing enclosure | (0.00304057807630, 0.00304057807631) |
| Tested saving | 0.003040575 |
| Claimed complete kappa | 0.00304057 |

The proof checks both complete matrices with different arithmetic and
chronology, exact native phases, each helper boundary, all main targets and
whole idles, every owned lifetime, and all scalar and route charges. Two
rational interval engines check the moment. Cutoff 17 and floor 18 fund the
completion tails; the old cutoff 20 fails. The finite compiler threshold is
`N = 2^64215200000000`. All 54 strict outer inequalities and four functional
inequalities pass with the retained ordinary BIT saving 0.0034.

## Reproduce

Use Python 3.12 and the standard library, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/p104-productive-controller --check-only
python3 -B scripts/research_package.py --package research/p104-productive-controller
```

The registered hook runs the full verifier normally and with `-O`. Its final
marker is:

```text
PASS_P104_PRODUCTIVE_COMPLETE_KAPPA_00304057
```

Direct replay needs no Git, network or optimizer:

```sh
python3 -I -B research/p104-productive-controller/verify.py
python3 -I -O -B research/p104-productive-controller/verify.py
```

The source archive is read and authenticated, then copied to temporary
storage for reconstruction. Normal replay does not write artifacts. The
explicit `--write` mode rebuilds the three local artifacts. Controls reject a
missing COPY, a wrong frame, a wrong native phase, an omitted central
translation, unearned helper credit, the old cutoff, and insufficient BIT
stock. The compiler grid check rejects its preceding integer point.

## Scope and coordination

The scientific base is canonical main
`32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision 7. The
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19154639)
records this changed cost model. The
[source handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2299)
released the old composition scope and left global binding open. The initial
fresh cache covered 401 open PRs and 4,828 Discussion records. This scope does
not take literal-slot P104 repairs, original split-contact charts, global
border grading, the Global120 constructor or the p19 compiler. Full overlap
search is coordination evidence, not a novelty theorem.

The bound retains the selected framework assumptions: native all-column
implementation, owned erasure, uniform compiler, precision and tape cost,
and analytic recovery. The package supplies ideal uniform frame identities,
finite growth bounds and all new parameter checks. It does not execute the
complete rounded multiplier, materialize the enormous uniform compiler word,
provide a proof-kernel theorem, or claim independent human acceptance.
No fixed-profile or global optimality claim is made.

## Sources and credit

- **Gareth Davidson**, verified as `bitplane` in the retained source notice,
  supplied [PR #2305](https://github.com/CrocSwap/integer-mult-bounds/pull/2305),
  mathematical head `335e78619a17b7c418e11306f86a72fd366de35b`: the exact
  [composition](https://github.com/CrocSwap/integer-mult-bounds/blob/335e78619a17b7c418e11306f86a72fd366de35b/research/p104-coalesced-private-reuse/compose.py)
  and its complete local boundary. Its old owner-window price is not reused.
- **David Arias** supplied the coalesced 735-register word in
  [PR #2152](https://github.com/CrocSwap/integer-mult-bounds/pull/2152),
  head `05f7aad0f08992ee48ec2dd93e896d9a4567847d`. The source archive retains
  the original code, README and attribution unchanged.
- **Cinna Davis** supplied the private-query reuse in
  [PR #2219](https://github.com/CrocSwap/integer-mult-bounds/pull/2219)
  and the productive controller lineage. The pinned
  [p16 caller](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/joint-helper-lattice/CONTROLLER.json)
  supplies the finite path and boundary matrices.
- **Ali Romman** supplied the direct conjugation identity in
  [PR #5398](https://github.com/CrocSwap/integer-mult-bounds/pull/5398).
  This package uses its inverse to admit only forward invocations.
- **Jacob Alan Sussman** supplied the mixed-target recursion lineage in
  [PR #4268](https://github.com/CrocSwap/integer-mult-bounds/pull/4268).
  **zxv** supplied the retained higher-moment/compiler and outer machinery;
  **Cao Yifan** supplied the source pricing lineage. Their exact interval
  engines and outer ledger stay unchanged.
- The P104 lineage retains **Rohan Arun**'s scalar channel, **Chafik Boukhalfa**'s
  native binding, **Adam Gall**'s schedule, **Josie Elliston** and **Ali Romman**'s
  geometry/decoder work, **icekylinx**'s frame compiler, and the PR1042/PR1094
  scalar architecture. The unchanged source archive and
  [native notices](https://github.com/CrocSwap/integer-mult-bounds/tree/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/p104-native-channel/notices)
  retain their earlier contributors and licenses.

New caller, productive binding, independent replay, full cost and package:
Ali Romman with substantial OpenAI Codex assistance. No subagents. Apache-2.0.

## Open next questions

Can the P104 local word reduce its paid profile under productive accounting?
Its original coalescing optimized a different owner model. Start from the
emitted word, check active claims, preserve every independent boundary, and
compare a fully paid change against this complete invoice.

Can an independent review confirm this changed complete admission? The first
step is the registered cold replay, followed by review of the forward wrapper,
helper normalizers and compiler. [TASK.json](TASK.json) records these questions
and their current limits. Neither question reserves work in another chat.
