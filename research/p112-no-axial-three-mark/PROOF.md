# A source-density floor for three ordinary marked targets

21 October 2026. Local structural deduction, not a lower multiplication bound.
This proof is independent of the selective circuit-relaxation package.

## Precise statement

Choose three ordinary two-copy canonical P112 marks from three distinct paired
roles. Their indicator matrix C has six nonzero rows, one in each of six
distinct physical triads. Let Q=C A, where every nonzero column of A has at
least two nonzero coordinates. For an arbitrary rational actual reader R with

`Q R = C C^T`,

first zero every reader column outside the six selected actual ports, and
delete zero outer products. Call the remaining number n. Then the original
complete physical-group invoice satisfies

`cost >= 12+n`.

In particular, n>=6 cannot improve the canonical local invoice18. Combining
this with the prior at-most-five-term three-projector floor gives a corollary
excluding every term count in this no-axial-query class; see the dependency
statement below. The primary new
claim here is the self-contained `12+n` bound; the older five-term theorem is
not a computational input to this note.

This does not cover a query column proportional to one marked axis, repeated
paired roles, J-singleton targets, or the residual-bearing three-copy target.
Nor does it cover query vectors outside the chosen canonical span. It allows
arbitrary rational coefficients, all reader asymmetry and cancellation, and
unbounded term count within the stated class.

## Pinned finite geometric facts

Use the physical groups and canonical marks from
`research/p112-rational-decoder-gate/CANDIDATE.json`, and their binary
nine-coordinate vectors from
`research/adaptive-kernel-demotion/inputs/DATA-PHASES.json`. The script verifies
their exact SHA256 pins before use, both partitions of112 ports, orthonormality
of every physical triad, and the following small facts.

1. The18 ordinary paired roles consist of disjoint pairs of triads and each
   role spans dimension6. Every two roles together span dimension at least8:
   142 of the153 pairs have rank9 and11 have rank8.
2. Among the666 distinct triad pairs,605 have rank6,59 rank5 and two rank4.
   The rank4 pairs have physical group indices(1,11) and(2,27). Adjoining any
   third physical triad to either pair gives rank at least6, in all70 tests.
   Consequently every pair of triads has rank at least4, and every triple has
   rank at least5: a triple of rank<=4 would have every pair of rank<=4 and
   contradict the checked third-triad property.

These are geometry premises, not a search over embeddings or coefficients.

## Proof

First delete every reader entry at a port outside the six selected rows of C.
Its complete old column Q R[:,p] is zero, so this deletion preserves the
endpoint and weakly shrinks the support/tariff of each term. Work with this
restricted factorization. Any terms that become zero can be removed; let n
denote its number of active terms. For a factorization with additional active
terms outside these ports, the proved lower bound uses this restricted n;
the conclusion cost>=18 for n>=6 refers to the restricted active count.

For a term let U be the binary span of all physical triads touched by its query,
and T the nonempty set of selected triads touched by its reader. Its query uses
at least two marked coordinates, so disjointness of C implies its source
support includes the two complete paired roles. By Fact1, dim U>=8.

Write V for the span of T and k=|T|. Then dim V>=k+2:

- k=1 gives3 by triad orthonormality;
- k=2 gives at least4, and k=3 at least5, by Fact2;
- k=4 contains both triads of some one of the three roles, giving at least6;
- k=5 or6 contains both triads of at least two roles, giving at least8.

The ambient binary dot product is nondegenerate in dimension9. The complete
source/reader tariff is

`rank <U,V> = dim V - dim(V intersect U-perp) >= dim V -1 >= k+1`.

Injectivity of C gives `A R = C^T`. At each of the six selected actual ports,
the active A-columns must span its marked unit vector. A single column cannot
do this, because every A-column has at least two nonzero coordinates. Thus each
selected port has at least two nonzero reader entries. Since those six ports
belong to distinct triads, summing k over the terms counts those reader
incidences exactly, and gives at least12. Summing the tariff bounds yields

`cost >= sum(k+1) >=12+n`.

If the original factorization has terms removed by reader restriction, its cost
is at least the restricted cost. For a complete no-saving conclusion, apply
the `12+n` bound when the restricted n>=6 and the prior five-term theorem when
the restricted n<=5. No inference is made by counting removed zero-effect terms.

## Candidate consequence and provenance

The locally proposed two-sign non-Fano dictionary

`a+b, a+c, b+c, a+b+c, a-c, b-c, a+b-c`

has no axial column. Hence it cannot improve the invoice in this scope,
without any reader or physical-placement search. Its original motivation was
to glue two sign-related specializations of the non-Fano recovery construction
in Das and Rai, [Generalized Fano and non-Fano networks](https://arxiv.org/pdf/1609.05815),
Lemma5 with q=2. Neither that paper nor a network broadcast rate supplies the
physical tariff argument. The dictionary gluing and geometric floor are local
deductions. More broadly, this bound applies to all no-axial dictionaries in the
specified three-mark canonical span, not only the seven displayed queries.

## Prior five-term corollary and evidence boundary

The standalone new theorem is `cost>=12+n`. For restricted n<=5, invoke the
five-term triple theorem in `research/p112-triad-matroid-boundary/PROOF.md`,
section "Every five-term replacement of three canonical terms has the original floor", and
its `COST-PROOF.md`. It covers any three canonical projectors and arbitrary
rational replacement factors, a superset of this note's factors. Consequently
the two results together give cost>=18 for every term count in the stated
no-axial three-distinct-role class. Keep the restricted n convention: terms
removed by zero-column restriction cannot move a factorization between cases.

That earlier package is PR3684, exact source head
`fad2e401ff63c634fb04e47146b0323449af70dd`, retained in canonical main
`12fa8c5c844be21bfefb38a19503fbd867a11244`. Its unchanged proof files are pinned
as provenance in SOURCES.json. It has archival, partially-reviewed status;
merging is not scientific acceptance. Its complete classification/pricing
replay was previously run, but is not rerun or silently included in this
package's two geometry commands. The all-term corollary depends on that prior
theorem; the new12+n result does not.

## Replay and next boundary

`python3 -I -O -Werror -B research/p112-no-axial-three-mark/verify.py`

The primary script authenticates the two foundational inputs and checks the
small geometry premises, all53 ordinary marks and their tariff6. Its default
is read-only; `--write-receipt` explicitly regenerates RESULT.json. The separate
independent checker reconstructs the geometry using annihilator sets instead
of elimination and additionally checks all7770 triad triples. The quantified
invoice proof above is a written argument, not a coefficient enumeration or a
proof-assistant theorem. These replays do not recheck the older five-term result.

An axial query, an exterior query direction, repeated roles, or more marked
targets can evade this proof's premises. Their presence is not evidence of a
saving. A new construction should identify how it pays for dense reader/source
supports before any coefficient search.

Prepared by flyingviper with substantial OpenAI Codex assistance. Separate
AI agents audited the proof and implemented independent checks; no independent
human or formal-kernel review is claimed. Apache-2.0.
