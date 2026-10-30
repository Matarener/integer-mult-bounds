# Paired-stage chronology cut

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

[PROOF.md](PROOF.md) proves even pair ranks, a stronger odd-pair loss,
and the mixed query-stage condition. For the complete PR #5599 profile,
the paired-stage family fails at kappa >= 0.003 through 92 fields and,
for odd stage-pair counts, through 176 fields. No new kappa is claimed.

An unbounded compatible family has constant loss eight and passes the
previous rank and intersection cuts. It fails the new chronology cut in
every order. At 1024 fields its complete relaxed price is positive. This
separates a useful price screen from a real endpoint.

Run `python3 -B scripts/research_package.py --package research/paired-stage-chronology-cut`.
The registered normal and optimized Python checks use exact arithmetic.
RESULT.json records the finite controls and interval numerators.

## Sources and credit

PR #5617 supplies the general cuts, the full-capacity obstruction, and
both complete source profiles. Its exact files are retained in inputs/,
with hashes and source paths in SOURCE-CONTEXT.json. Cinna Davis supplies
the private-projector lemma in the pinned GLOBAL-PROOF.md. Douglas
Colkitt and the P104 source contributors retain the source package credit.
The new contributions are pair parity, the odd-pair strengthening, the
constant-loss compatible family, the mixed coefficient filter and their
complete-price consequences. No predecessor native admission is repeated.

## Open next questions

Impose the mixed cut in a paired-stage search, then verify every word
coefficient of a surviving candidate. A result must retain the full bill.
Determine whether a constant-loss family can satisfy chronology at all
sizes. The construction here cannot. Coupled ports and paid idles need
separate price theorems.
