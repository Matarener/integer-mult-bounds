# Independent full replay of the corrected seven-label length-20 exclusion

**Scoped finite result; no new κ.** A separate C implementation completed all
five admissible `n=7, L=20` weight-parity split searches with zero universal
words. It uses a different state representation from the retained corrected
census: byte frequency tables for pair differences and direct rollback. The
Python runner also checks the exact predecessor pruning behavior against a
direct raw-word oracle on the complete `n=4, L=8, (4,4)` domain.

The full result independently reproduces the lower bound `f(7) >= 22` in the
PR943 abstract singleton prefix-walk model. With the retained length-24 word,
the value is restricted to `{22,24}` in that model; this work does not decide
whether length 22 is attainable. It does not affect the selected multiplier
result, suppliers, or κ.

## Audited pruning defect

The pinned predecessor is `research/universal-f7-singleton-seedb859517b/engine.py`
at base `5ada57b37270163b736c7018db88cc27025abed0`. In `cyclic_census`, its
prefix parity class is selected by `q & 1` (coordinate bit 0), while the
supplied fixed collision budget comes from the target split by Hamming-weight
parity. The named restored word `01021323` has prefix states
`[0,1,3,2,6,4,12,8]`. Direct pairwise XOR gives all 16 masks; all eight prefix
states are distinct; every label occurs twice. Its weight-parity split is
`(4,4)`, but its bit-0 split is `(6,2)`. The bit-0 collision excess is 8. The
wrong fixed budget is 5, while the valid budget for the actual bit-0 group
sizes is 9.

The independent raw-word oracle visits all `4^8` raw words, then filters for
restricted-growth form, restoration, simplicity, the `(4,4)` weight split and
direct XOR coverage. It finds 22 universal words; the predecessor's fixed
budget falsely removes 6 of them. The named word is one of the six. This proves
the generic old pruning rule unsound in the small simple-word domain. It does
**not** prove a seven-label universal word exists or that every historical
seven-label exclusion is false.

## Complete n=7 result

The all-split arithmetic in [PROOF.md](PROOF.md) reduces the length-20 search
to the following five representatives; the `(9,8)` split is ruled out by the
pair-collision identity before enumeration.

| Weight-parity split | Independent nodes | Admissible closed leaves | Universal hits |
|---|---:|---:|---:|
| `(10,10)` | 856,786,320 | 0 | 0 |
| `(10,9)` | 268,464,478 | 0 | 0 |
| `(10,8)` | 13,803,385 | 0 | 0 |
| `(9,9)` | 31,403,241 | 0 | 0 |
| `(10,7)` | 57,280 | 0 | 0 |

Total: 1,170,514,704 completed recursive nodes. Each split had zero closed
admissible leaves after sound necessary-condition pruning, zero hits, and
`complete=true, aborted=false`.

Each run is uncapped. The program reports `complete=true` only on normal
exhaustion; the separate 1,000-node control must exit with status 2 and
`complete=false`. The direct leaf check computes `P+P` over all 128 masks.
Detailed proof of coverage and every prune is in [PROOF.md](PROOF.md).

## Reproduce

Requires Python 3.10+ and a C11 compiler (`cc`, GCC or Clang); no Python
packages are used. From the repository root:

```sh
python3 -I -B research/f7-independent-full-replay/verify.py --quick
python3 -I -B research/f7-independent-full-replay/verify.py --full
python3 scripts/research_package.py --package research/f7-independent-full-replay --check-only
```

`--quick` rebuilds the C engine, performs the full small-domain raw-word
comparison, confirms how the pinned predecessor accepts/rejects the named
word, checks the independent `(4,4)` census, and validates the fail-closed cap
control. It does not run a full n=7 search. `--full` repeats those controls,
then freshly enumerates all five complete n=7 splits and checks the length-24
upper witness directly. The complete run has a 600-second per-case timeout;
the PR runner may execute the same command and must see exit code 0.

The full-replay receipts from the retained correction package are read only
after the independent runs finish. They are comparison artifacts, not imported
search output. No code from either the old engine or the corrected engine is
called by `replay.c`.

## Scope and remaining gap

The exact conclusion is limited to the PR943 restored singleton prefix-walk
model, seven labels, and the five length-20 split representatives proved
complete in [PROOF.md](PROOF.md). The counterexample invalidates the old
bit-0/fixed-weight-budget prune; by itself it says nothing about existence at
`n=7`. The second full implementation supplies new computational evidence for
the corrected zero-hit result, but is not a proof-kernel verification.

## Open next questions

The next mathematical question is whether a restored universal seven-label
word of length 22 exists. This package does not search length 22. It also does
not independently rerun the corrected length-18 census; that is unnecessary
for the length-20-plus-padding lower bound shown here. The exact value of
`f(7)` remains unresolved.

No selected record or frozen package was changed. The selected κ remains
`836330098538459/500000000000000000` (decimal `0.001672660197076918`). All
all-size, compiler, hosting, precision, tape and analytic assumptions attached
to that separate multiplication result remain outside this word-model audit.

## Coordination, source pins and credit

Task: `census-pruning-audit`, refined to answer the correction package's named
open question about a second complete n=7 length-20 replay. The research
decision is whether the author-checked `f(7) >= 22` exclusion can be independently
corroborated. The card's first bounded step—manual counterexample, exact old
pruning rule and a complete small domain—was completed before this larger run;
the full replay used a separate 60-minute session budget. Base main is
`5ada57b37270163b736c7018db88cc27025abed0`, priority revision 6. The final
live overlap check (2026-10-17 22:00:41–22:02:03 UTC) covered complete
pagination of 247 open PRs and 2,170 discussion records; the exact census
terms returned no matches. This is a lead search, not a novelty certificate.

Credit Ross Richardson for the PR943 word model; Nicholas Stone for the
parity correction and retained corrected census; Aaron Wang and the cited
predecessor chain for the earlier word model and engines. This new C replay and
raw-word oracle were written with OpenAI Codex assistance. No separate human
review or formal proof assistant is claimed. Apache-2.0.
