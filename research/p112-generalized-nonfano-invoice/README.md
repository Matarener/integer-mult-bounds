# A generalized non-Fano decoder has the wrong full-group invoice

The q=4 generalized non-Fano identity gives six rational queries for five canonical P112 targets, with different readers at the two physical copies of its hub. It reconstructs the endpoint exactly, but cannot save on the complete physical-group invoice for the reader assignment stated in [PROOF.md](PROOF.md). This is a structural rejection of one mechanism, not a coefficient or embedding search.

For five ordinary targets the invoice is at least32 versus baseline30, including repeated axes in a paired role. A residual-bearing target raises that baseline to31 and still cannot help. The proof also closes every permitted placement of the exceptional J targets. The two ordinary hub copies use the two different displayed readers; an optional residual copy may use either. Other reader assignments are not silently included.

The result does not improve334, meet the296 target, or change the selected multiplication bound. It does not exclude different sparse network codes, changed covers, or higher-rank fitting matrices.

## Evidence and reproduction

[PROOF.md](PROOF.md) derives the exact identity and the physical rank inequalities. [verify.py](verify.py) checks all100 endpoint entries, rejects altered nonzero coefficients, and authenticates the two physical inputs. It derives the fixed annihilator incidences: any two ordinary pair roles span at least8 dimensions, J plus a pair spans at least7, and every foreign triad plus a pair spans at least7. These are complete fixed-premise checks; the analytic case argument is in the proof.

```sh
python3.12 -I -O -Werror -B research/p112-generalized-nonfano-invoice/verify.py
python3.12 -B scripts/research_package.py --package research/p112-generalized-nonfano-invoice
```

Standard-library Python3.12. The direct verifier also runs from an exported package containing its declared inputs, without Git or network access. [RESULT.json](RESULT.json) records the replay output. The hub-J case uses the pinned canonical-span theorem, whose proof is an explicitly declared input; it is not reproved here.

## Sources and credit

The network coding construction is from N. Das and B. K. Rai, [Generalized Fano and non-Fano networks](https://arxiv.org/pdf/1609.05815), Section IV, Lemma5 and the scalar code following equation(44). This package's contribution is the explicit split-reader adaptation and its complete-group invoice obstruction on the fixed P112 geometry. No novelty claim is made for the underlying coding identity. Repository geometry, canonical-span proof and their predecessor attribution are retained through [SOURCES.json](SOURCES.json).

Prepared by flyingviper with substantial OpenAI Codex assistance, including a literature agent and separate mathematical audit. No independent human or proof-kernel review is claimed. New work is Apache-2.0; no third-party paper text is vendored.

## Open next questions

A useful next construction must avoid the dense-source obstruction. Give a sparse characteristic-dependent query identity and derive its exact whole-group masks and annihilator benefit before optimizing its placement. No such cheaper construction is supplied. [TASK.json](TASK.json) records this question, its first test and the remaining blockers.
