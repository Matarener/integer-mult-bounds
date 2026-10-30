# A two-parameter P112 common-frame family cannot satisfy the rank caps

For the fixed asymmetric rank-eight anchor on physical groups `[1,2,27,28]`,
no rank-nine extension in the common-complement family

```
H_t = span(C0+t C1, A1, D2),
K_s = span(C0+s C1, A1, D2),  1+st != 0,
```

can extend to new groups 3 and 4 while satisfying all complete-group rectangle
ranks. Here `(A,B,C,D)=(1,2,27,28)`, scalar axes are numbered 0,1,2, and H/K
use the anchor source rows/reader columns respectively. The theorem covers
every rational split of these common frames, including all boundary cases.

The generic locus `st!=-2` is excluded by three self-rectangle caps and the
full projector equation. The exceptional locus `st=-2` has a different flag
normal form: two self caps force a six-dimensional minor inside a rectangle
whose physical binary tariff is only five. See [FAMILY-PROOF.md](FAMILY-PROOF.md)
and [the independent derivation](INDEPENDENT-FAMILY-PROOF.md).

The selected frame `t=s=0`, with anchor axes `[6,1,11]`, retains its short
trace certificate in [PROOF.md](PROOF.md):

```
trace((W-I)Q) + 7 det(S4) - 2 det(I3-Q[:3,:3]) = -4.
```

The complete family proof does not specialize this identity through a zero
denominator. Its exceptional branch is checked independently.

## Exact scope and relevance

This is a structural obstruction to a particular lower-bound certificate,
not a cheaper decoder or a selected-bound improvement. The family has the
required nested C and A+C flag incidences and nondegenerate source/reader
pairing. The primary and independent generic verifiers also compute the complete
label-preserving anchor centralizer and the invariant `tr(Pi Z_A Pi Z_C)=1/(1+st)`, so these
frames cannot all be normalized to two isolated choices. The centralizer
supplement is not needed for the main obstruction.

The family still fixes the A1 and D2 directions on both sides. Arbitrary
common complements, other anchors and higher-rank fits remain open. This
proves neither a global copy-cost floor of 334 nor a decoder of cost 296.
The latter is the first integer target below the optimistic threshold
`2672/9`; an improved selected bound requires a complete charged invoice
and supplier. No selected result changes.

A diagnostic exceptional projector passes all three original self caps,
with ranks 6,7,4, but fails exactly twelve of the 3,969 complete-group
rectangles. The independently regenerated receipt records every failure.
This is a control showing why the extra rectangle matters, not a successful
lift or a parameter search.

`FIXTURE.json` is explicit local research data. Its old local receipt hashes
record provenance, not accessible Git dependencies or accepted proofs. The
registered foundational verifier recomputes all 225 nonempty anchor
rectangle inequalities and the saturated flag spaces from the two declared
external inputs. The family commands authenticate the same literal data.
Frozen predecessor files remain unchanged.

## Reproduce

From the repository root, using Python 3.12 or later and the standard library:

```sh
python3 -I -O -Werror -B research/p112-alternate-frame-trace/verify.py
python3 -I -O -Werror -B research/p112-alternate-frame-trace/independent.py
python3 -I -O -Werror -B research/p112-alternate-frame-trace/family.py
python3 -I -O -Werror -B research/p112-alternate-frame-trace/independent_generic.py
python3 -I -O -Werror -B research/p112-alternate-frame-trace/independent_exceptional.py
python3 -B scripts/research_package.py --package research/p112-alternate-frame-trace
```

The five registered scientific commands are required together. They compare
exact recomputations with committed receipts and leave all files unchanged.
`--write-receipt` is an explicit maintenance option. `family.py` authenticates
the SHA-256 of local `verify.py` and compiles its source bytes for arithmetic
helpers; it does not load cached bytecode or hidden project dependencies.
The independent commands share literal input data, but no producer arithmetic
or polynomial code. Generic identities are checked formally over Q(s,t);
the exceptional factorization uses sixteen free variables and omits no
rank-two projector stratum. No coefficient grid or solver is involved.

The original coefficient/sign fault controls remain. The family checks
include a changed-compression control and a deleted forced-column control;
the independent exceptional replay also verifies that removing the forced
column destroys its invariant minor. The proof text states which deductions
are written linear algebra and which identities the scripts replay.

These are exact arithmetic and written proof checks, not a proof-assistant
kernel or independent human review. No full multiplication cold replay is
relevant to this isolated negative result. Native routes, scalar execution,
owned/borrowed state, dirty restoration, storage, precision, an all-size
compiler and complete supplier admission remain unproved; their cost is not
zero.

## Provenance, overlap and credit

Based on canonical main `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority
revision 7. The donor's existing decoder assignment takes precedence over a
new task draw; `TASK.json` records that scope change. The 20 October 2026 public
API scan covered all 354 open PRs. Nearby work included #4219 (actual-basis
C1 invoices), #3604 (tetrad co-delivery), and #4204 (paid helper return), with
different premises. Fresh Discussion coverage was unavailable after a
persistent HTTP406, so this is not a novelty certificate.

The fixed cover and canonical decoder are from flyingviper's
[p112-rational-decoder-gate](../p112-rational-decoder-gate/README.md), retaining
Cinna Davis's P112 cover lineage, Sagar Thakrar's scalar-mask/full-group audits,
Adam Gall's mask obstruction, ctoth and Philippe Van Velzen's endpoint and
whole-space pricing framework, and Hanson Sun's excess-rank/projection work.
The selected physical labels are retained through the adaptive-kernel-demotion
source and its upstream contributor notices. The current proof does not claim
those predecessor results as new.

The new contribution is the complete two-parameter obstruction, its separate
exceptional-locus argument, the anchor automorphism invariant, and independent
literal/symbolic checks. The selected-frame trace remains a readable special
case and foundational data replay. Prepared by flyingviper with substantial
OpenAI Codex assistance and separate AI-agent mathematical checks. Apache-2.0.

## Open next questions

- Describe the remaining common frames using the general nested Schubert
  incidences and nondegenerate pairing. The present family fixes A1 and D2;
  no reduction from arbitrary H,K to it is proved. A decisive next result
  would be an exact all-cap extension or an obstruction covering a justified
  additional structural class, rather than a coefficient grid.
- For the constructive route, give one sparse characteristic-dependent
  endpoint whose complete physical bill saves. A scalar identity alone does
  not supply the omitted native and supplier obligations.

`TASK.json` records the scope, stop rule and remaining blockers explicitly.
