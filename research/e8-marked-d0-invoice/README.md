# The complete marked d=0 C1 invoice

This package proves the **whole marked d=0 invoice** left open in
DreamingOfClouds' [PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154),
CONJ-G Section 0 and CONJG2 Section 2, for the tight t=2,3 cells:

    I - epsilon_k >=64.

It starts with the raw actual basis and its restricted duals. The proof
derives the rigid shape and actual low-basis total cap itself, using neither
the source's N8 normalization premise nor the pending one-sided floor K2.
It retains the actual coefficient map, both pivot-rebate values, repeated
corrected LOW frame indices, weight-nine highs and the actual marked witness.
The bound is attained by explicit marked examples at both t=2 and t=3.

It also proves the **unmarked invoice I>=64** in the same d=0 actual-basis
class. Together these imply a broader actual-decoder floor: a singleton
pivot may be paid or free, and no losing root row is assumed. A separate
raw correction-count lemma supplies N8 for marked t=2 packets for every d.

The exact statement is in [PROOF.md](PROOF.md). Write C_h(s)=(r_s,h) on P112,
S containing C, dim(S)=8+t, T=span{q in S:w(q)<=7}, and C intersect T=0.
Let the actual basis F have nonzero restricted dual functionals xi_j. A
correction means xi_j is a nonzero frame functional whose frame label lies
in the actual column-label span. Put I=sum_F w-n_c. The mark consists of a
nonframe root v, xi_k=gamma ev_v with gamma!=0, and an actual word g in S
vanishing on O_v={v} union {s:(r_s,v)=0}, with phi_k(g)!=0.
The theorem gives the displayed bound over every characteristic-zero field.

## What is new

1. **No imported rigid shape/N8/K2.** Raw counts and a singleton frame-group
   argument derive the actual low/high basis split. Complete Sigma9/10
   exclusions repair the low-total cap. Every actual Sigma8 profile is
   excluded, including `(7,1)` without assuming that basis is minimum.
2. **All remaining coefficient cases.** [SMALL.md](SMALL.md) proves every
   Sigma<=6 case; the Sigma7 geometric consequence is re-established with
   its local hypotheses. Carrier triples use the actual fixed coefficient
   A(h)=-sum xi_a(h)b_a. The private-label lemma excludes every frame label
   from the span of privately matched roots. The last low-k equality case
   subtracts an actual high basis member and preserves phi_k(g).
3. **Unmarked floor and a broader consumer.** [UNMARKED.md](UNMARKED.md)
   proves I>=64 with no marked root or g. [CONSUMER.md](CONSUMER.md)
   derives the embedding, mark, exact projected invoice and unique possible
   rebate directly from an explicit class of actual exact factorizations.
   The actual rank pair (9,8+t) and singleton pivot derive the code-plus-unit
   row shape; it is not an additional normalization premise.
   Neither a free pivot nor a losing root row is a premise: a paid pivot
   pays any rebate, and a free pivot supplies g when needed. Eleven actual
   factorizations cover paid/free, loss/no-loss and both t values; the paid
   equality control is also reconstructed in the separate D8+ algorithm.
4. **A raw N8 bridge beyond d=0.** [RAW-COUNT.md](RAW-COUNT.md) proves
   n_c<=m-2 for a marked actual basis of size m<=11, without a condition on
   T or g. This gives n_c<=8 for marked t=2, every d. It does not close any
   positive-d survivor or establish the source's t=3 N8 premise.

The g condition is essential. The replay constructs a literal unmarked
I=64,epsilon=1 example with S_v=0; without g the claimed inequality would
read63>=64. A separate D8+ implementation reconstructs that countercontrol
and checks every entry of its N0 factorization and its binary costs.

This directly closes the marked invoice; it does not claim the unrestricted
Swap(+carrier) conjecture or unrestricted F1. Those are stronger intermediate
routes, and unrestricted F1 is already false at the recorded boundary.

## Reproduce and evidence

Python3.12, standard library only, from repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/e8-marked-d0-invoice --check-only
python3.12 -I -B scripts/research_package.py --package research/e8-marked-d0-invoice
```

The registered command is read-only. `verify.py --emit` explicitly regenerates
the deterministic [RESULT.json](RESULT.json) receipt after scientific edits.
[SOURCES.json](SOURCES.json) authenticates all live predecessor inputs before
execution; source bytes are compiled directly, so predecessor `.pyc` files
cannot replace them. Provenance and live-input invalidation follow the
repository's registered-package conventions.

The replay recomputes the inherited root-only/F1/plane inputs, then checks the
new finite facts using Cartan/lattice labels and a separate explicit D8+
construction with Gram-row labels. It covers all 511 hyperplanes,7,168 carrier
triples,21,504 carrier/unit placements, all private-quartet sign products,
all ordered two-frame nonaxis carrying cases, and all one-/two-/three-axis
form inventories. The independent no-coloop test uses dual functionals;
the predecessor uses dependence masks. Finite coefficient-grid examples are
controls; the universal coefficient classification is the written proof.

The coordinate binding checks all 14,400 Gram pairs and the rank-nine graph
of the two label maps, proving their binary support matroids isomorphic.
An additional marked intrinsic example has two corrected LOW members using
the same frame; it guards against silently reinstating distinct-low indices.

The four [Lean files](formal/README.md) check private-incidence,
private-label, quadratic-parity and actual-basis coefficient-map cores at
Lean4.21.0/mathlib308445d7. Their printed axioms are
only the reported standard axioms. **The E8 instantiation and complete theorem
assembly are not formalized.** Internal AI reviewers separately reconstructed
the larger-count cases, small-coefficient arguments, actual consumer and
source scope; this is not independent human peer review.

## Exact scope and remaining limits

The intrinsic theorem covers PR3154's marked d=0 packet before its rigid-shape
reduction. CONSUMER.md additionally proves a local actual-decoder consequence
under displayed exact-factorization, singleton-pivot, rank-pair, tight-term
and nonparallel-actual-row hypotheses. The row shape follows from those ranks.
Its pivot may be paid or free. The unmarked conclusion is I>=64, while
I-epsilon>=64 still requires the actual marked witness. RAW-COUNT.md removes
the numerical N8 premise only for marked t=2; marked t=3 still permits n_c=9.
The original global reduction of every potential two-sided counterexample to
these or other branches remains outside this package. No d>=1 invoice closure,
complete P112/L120 floor, supplier or selected-frontier change is claimed.
Hosted CI and independent human review remain outstanding.

## Sources, credit and overlap

Prepared by **conorholds**, with substantial OpenAI Codex assistance, including
GPT-6.1 SOL agents at xHigh reasoning. New work is Apache-2.0.

DreamingOfClouds' PR2816 supplies the E8 lift/parabolic framework; PR2832
supplies the actual decoder and binary tariff context; PR2862 supplies the
carrier/parity predecessor; PR2985 supplies cap context; PR3154 and
[Discussion3156](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156)
state the open marked obligation. PR1590's two-factor lemma underlies the
reused weighted root-swap theorem. CubeJerry's PR3095 supplies field and
normalization context. All predecessor credits remain in the frozen inputs.

[PR3166](https://github.com/CrocSwap/integer-mult-bounds/pull/3166), at
7c2a62363ad4945e8803fedea6ead78e1ad412b2, supplies the weighted root-swap bound,
root-only and F1 geometry, and selected earlier C1 strata. Its C1 consequences
explicitly retained N8/rigid-shape assumptions and left the present cases
open. This package reuses its independent geometric theorems, not those
unvalidated normalization premises. PR3154 is pinned at
708f0ad8928c383de8294aea3c126e9461d2066d. Adjacent C6 work in PR3191 is not a
premise. The new C5 shortening/physical-graph results do not cover this
basis/dual/marked class.

PR2816's one-sided root-swap cost64 family and PR2854's normalized `(1,1)`
cost64 witnesses retain priority in their scopes. The present sharp controls
attain the displayed marked theorem/consumer at t=2,3; no first-ever cost64
factorization is claimed.

Base24db9bfffd4a7c812545ea6ae58853cb9ef094b2, priority revision6. The original
`complex-rank-shape-decoder` card and changed scope are retained in TASK.json.
This follows the named handoff instead of attempting the card's positive
rank-shape construction. Read-only overlap checking found no competing marked
or unmarked d=0 completion. The complete snapshot covered247 open PRs at
22:03:19 UTC,2,170 Discussion records at22:03:52 UTC and2,761 closed PRs at
22:04:14 UTC on2026-10-17, with no warnings. The large open/closed count change
reflects upstream archive intake; archival merger is not scientific approval.
New capacity, fixed-cover and shortening results have different predicates;
PR3300's rank-seven equality classification does not change the inherited
capacity36 used here. Collections are non-atomic, and arbitrary diffs and
unpublished work are not exhaustively covered. Public coordination remains
pending the user's approval; no upstream action was posted by this investigation.

## Open next questions

The [structured questions](TASK.json) retain two concrete follow-ups:

- Audit the original global branch-coverage/normalization reduction before
  importing the local result into a full P112 floor. Start with exact actual
  factorizations and source3154's transition into the tight cells. The local
  singleton consumer now covers paid pivots, while positive-d filters and
  the marked t=3 n_c=9/slack9 boundary remain separate.
- Formalize the E8 instantiation and case assembly. Start by connecting the
  exact private pairing and root residue quadratic form to the four generic
  Lean cores. The complete finite-normal and decoder bridges remain blockers.
