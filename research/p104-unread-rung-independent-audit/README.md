# Independent replay, invoice, native and funding audit of PR5827 and PR5907

**Result (scoped audit, no new κ).** An independent check of the two latest conditional P104 words finds no
error. It covers [PR #5827](https://github.com/CrocSwap/integer-mult-bounds/pull/5827) (Ali Romman, unread-path
resynthesis, κ 0.00312476680) and [PR #5907](https://github.com/CrocSwap/integer-mult-bounds/pull/5907)
(DreamingOfClouds, helper 468 rung removal, κ 0.003125282). For both words, an own exact replay, an own invoice
recount, a dense all-column native check with absolute phase and an own decimal funding engine reproduce the
authors' claims. That includes the exact raw crossings (.00312476681507, .00312476681508) and
(.00312528909884, .00312528909885). One reproducibility defect was found: PR5907's `verify.py` fails on Linux
(see below). Its mathematical content is unaffected.

Base: canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`, which contains both packages
(`research/p104-unread-path-resynthesis`, head `05cd36e5`, and `research/p104-helper468-rung-removal`, head
`c1cbd9e3`). The intake ledger records both as `partially_reviewed`, with "independent scientific review and
source-bound replay remain open". This package supplies that review for the finite local words and their
complete invoices. Live inputs are pinned in [SOURCES.json](SOURCES.json).

## What is checked

| Layer | Check | Result |
|---|---|---|
| Author verifiers | `verify.py` of PR5827 and PR5907, Python 3.12.3 on Linux, zlib 1.3 | PR5827 PASS (5.4 min). PR5907 stops at `Entire regenerated WORD.json.gz, byte for byte`. The two containers differ only in gzip header byte 9 (OS code 0x13 in the shipped file, 0x03 from Linux zlib) and the payloads are equal. With that one comparison made on the decompressed payload (as CONTRIBUTING.md asks), the complete PR5907 chain passes, including its committed RESULT.json (5.5 min) |
| 0. Sources | PR5827 archive pinned inside PR5907 against the canonical PR5827 package; PR5907 `construct.py` | all archive members equal canonical main byte for byte; regenerated PR5907 word equals the shipped word after decompression |
| 1. Own replay, importing nothing from the packages | PR5811, PR5827 and PR5907 words: strict span nesting of every MOVE, common chart of every ADD/COPY/SCALE, dyadic coefficients, owned INIT/CLEAR lifetimes, all 799 endpoint rows (identity on public registers plus X into Y for the 104 live ports), strict nesting of every helper's initial span in its final span | PASS on all three words: 770 public, 29 owned labels, 31 lifetimes, peak 13 |
| | PR5811 → PR5827 | exactly the seven events from index 13815 change; paid delta −H1 − H4 + H5; boundaries and helper profile unchanged; one ADD added |
| | PR5827 → PR5907 | exactly the five declared boundary changes (initial 557: 3→105, 765: 245→263; final 455, 557: 105→925, 765: 127→742); helper ranks 1→7, 1→6, 1→3; paid delta −4H1 + H4 + H6 + H7; target delta −3H1 + H3 + H6 + H7; one MOVE fewer, 15 ADDs more; 25,998 events ≤ 26,000 |
| 2. Invoice | own recount from the 51 physical caller events (18 LOCAL, 15 QUERY_SHEAR, 15 IDLE, diagonal terms) and separately from the closed formula in PR5827 PROOF.md | equal to each author `complete_cost`: 66,870 / 13,444 (PR5827) and 66,852 / 13,444 (PR5907); rank-mass surplus 760 |
| 3. Dense native inventory | PR5548's credited exact Gaussian-dyadic interpreter compares the lowered recipe with the literal frame circuit on all 512 columns: exact equality, norm, support size 2^rank | PASS on the union of both inventories: 3,163 operators (2,918 and 2,921 distinct signed maps, matching the authors, plus 208 main adapters), 8.3·10⁸ complex entries. A phase-only fault with an unchanged signed tableau and a flipped child sign on the new map 3 → 712 are both rejected |
| 4. Own funding engine | 80-digit decimal ln/exp with 10⁻⁷⁰ relative padding, bisection on a 10⁻¹⁴ grid | both raw crossings equal the author intervals; tested savings .003124766805 and .0031252870 positive; the tail ratios α < 1 − 10⁻¹², γ, δ < 125/128 hold at the tested savings; the margin derivative is negative on [0, .0034], so each crossing is unique there |

The gain of PR5907 over PR5827 per local call is H1 + H3 − H4 in the moment margin. It is positive for every t in (0, 1).

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/p104-unread-rung-independent-audit/verify.py
```

The default run is serial and takes about three minutes. It checks layers 0, 1, 2 and 4 completely. For layer 3 it
checks a fixed subset: all seven maps new in PR5907, every helper pair, every 8th main adapter and every 64th MOVE
map. Each digest must equal [FULL-CHECK.json](FULL-CHECK.json). The complete inventory runs with

```sh
python3.12 -B research/p104-unread-rung-independent-audit/verify.py --full --jobs 4
```

in about 15 minutes on four cores. It recomputes all 3,163 digests. The marker is
`PASS_P104_5827_5907_INDEPENDENT_AUDIT`. [PROOF.md](PROOF.md) explains each layer.

## Scope and limits

This audits the finite 9-qubit local words and their complete invoices. The five inherited framework assumptions
remain: native_all_columns for the uniform word, owned_erasure, compiler, precision_tape and analytic_recovery.
The physical caller (`research/p104-productive-controller`, unchanged since its admission in `e2a6cce2f`) is
recounted, not re-derived. The compiler threshold and the 54 strict and 4 functional outer conditions are checked
only by the authors' code, which passes here. This is an agent check, not human or proof-kernel acceptance. It does
not change the selected record.

## Open next questions

- Should PR5907's verifier compare the decompressed word? A one-line change makes it pass on Linux hosts, and
  hosted CI is likely to hit the same failure. First step: replace the byte comparison in `verify.py` line 55 by
  a payload comparison, as in this audit's layer 0.
- Can maintainers admit PR5827 and PR5907 on this evidence, with the inherited premises unchanged? First step:
  intake review of this package against the ledger entries for #5827 and #5907.
- Do the uniform-compiler premises bind to the FULL-CHECK.json digests, so that the finite native check carries
  to every recursion level? This is still blocked by the inherited native_all_columns premise.

## Credit

Ali Romman (PR5827 word, verifier and lineage, with OpenAI Codex assistance) and DreamingOfClouds (PR5907 edit
and packaging). Mason Hale (PR5811). Chris R / Clear1nsight (PR5548 dense interpreter, imported unchanged).
unpaidmoon (frame-rank correction of the PR5827 early read). The P104 native, Clifford, controller, compiler
and analytic contributors are credited in the cited packages. This package was prepared for Matarener with Claude
(Anthropic), via Claude Code. Apache-2.0.
