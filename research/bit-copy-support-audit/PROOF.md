# Independent causal-support audit for the unchanged-total private walk

## Exact conclusion

The support implication in PR4200, head
`ddfc3133cbdf548e163c867d5671f8f01dd5d5ae`, is valid under its stated
fixed-trace, upward-public-MOVE/common-frame-ADD hypotheses. The proof below
does not assume clean helpers, noncancelling paths, independent values of
ordinary registers, or a particular characteristic for the data group.
It separates this causal assertion from the linear same-query decomposition
and the rational geometric tariff argument.

This is an independent written proof and a bounded source-trace applicability audit.
It is not a formal-kernel proof, a new lower bound for arbitrary algorithms,
or admission of a physical private-MOVE interface. The rank-seven obstruction
and its finite input geometry are predecessor results, not new discoveries.

## 1. Fixed-trace causal-support lemma

Let V be a finite-dimensional rational or real vector space. A fixed finite
straight-line trace assigns a frame U_r(t) subset V to each public register r
after event t. Fix a subspace L. Compare two runs with identical initial
public values, frames and prescribed events. The runs may differ only at a
specified family of external/private read events. Every such read changes
only a receiver whose frame contains L.

Ordinary public events have the following dependency condition: for every
input register of frame U which can affect an output register of frame W,

    L subset U implies L subset W.                         (S)

All data dependencies, including a guard or coefficient if data dependent,
must be counted. The events and frame schedule are fixed independently of
which compared run is used. Deterministic local transport may change its
data representation; it has no hidden dependency on a different register.

**Lemma.** At every time t, if the two values of register r differ, then
L subset U_r(t). In particular a differing final target of frame K must
satisfy L subset K.

**Proof.** Initially all public values agree. Consider the first output
whose compared values would differ despite its frame excluding L. An
external/private read cannot be this event, because its receiver contains
L. At an ordinary deterministic event, differing output values imply a
differing value of at least one of its inputs. By induction that input's
frame contains L. Condition (S) then forces the output frame to contain L,
a contradiction. Unmodified outputs preserve the inductive claim. This
proves the invariant for every finite event sequence. In particular, dirty
values can be arbitrary and correlated: the two runs begin with exactly the
same dirty values. No assumption about their numerical values is made. QED.

Upward public MOVE U -> W satisfies (S) because U subset W. A common-frame
ADD `b <- b + c*a` satisfies (S) because its source and destination frames
are equal (and its old destination is in that same frame). Thus these are
sufficient hypotheses for the lemma. They are stronger than necessary:
a transfer from U to W is safe for this particular L whenever it preserves
the truth of containment of L, even when U is not a subspace of W.

The proof uses equality of values rather than a path count or a notion of
positive influence. Cancellation can make an output agree; it cannot make
an output differ without some differing predecessor. The claim therefore
does not fail over F2, where two identical paths can cancel.

## 2. Isolating one private branch and its coefficient

The comparison relevant to the predecessor is an intervention on a single
branch: suppress only that branch's private-to-public ADD increments, not
the pre-existing public values, its original source q, or unrelated
branches. Keep the same public schedule and frames. The private source q
is unchanged throughout; the branch carries that same logical q and does
not read branch-modified public values. Thus suppressing these increments
does not change any later injection value or invalidate the stipulated
private return/ERASE contract.

Let L be the intersection of every private frame visited by the branch.
Every private-to-public ADD is at a common frame W, so L subset W. Applying
the lemma shows that this intervention can change final target p only if
L subset K_p.

For scalar linear logical data operations over a field k, write the initial
public state as z. If q=q(z) is a fixed linear functional, the intervention
difference is

    Delta_r(t,z) = a_r(t) q(z),                            (C)

where a_r(t) is computed by the same scalar ADD recurrence starting from
zero and inserting the branch's read coefficients. In a decoded chart in
which MOVE preserves the logical scalar, MOVE preserves a_r. Equation (C)
follows by induction and does not require q to be independent of z. If q is
not identically zero, `a_p != 0` means an actual difference for at least one
input z; the support lemma forces L subset K_p. In F2 the a's are path sums
modulo two. Multiple paths may cancel a coefficient, never create one
outside the lemma's permitted frames.

With several branches reading the same unchanged q, their scalar
intervention coefficients add by linearity. The support of the total
coefficient is contained in the union of the individual supports. This is
why the predecessor may use a union bound despite arbitrary F2
cancellations. It is essential to distinguish isolating a branch from
changing the original source value: changing q at its ordinary source can
also alter unrelated public uses of q and is not this intervention.

Source immutability and carrying exactly q are not needed for the abstract
causal-support lemma: arbitrary exogenous read values are allowed there.
They are needed to conclude that this one branch supplies a coefficient
of the required unchanged functional q, and to justify the copied-field
return/ERASE and independent same-query decomposition. Similarly, private
closure/nestedness is not needed for support; it is needed for the next
dimension bound.

## 3. Closed private walks: distinct geometric obligation

Suppose the branch starts and ends at G subset F, and every consecutive
private frame pair is nested. Let f=dim(F), r=f-dim(G), and let m be the sum
of the absolute dimension differences of every private MOVE, in both
directions. Since the walk is closed, its total downward dimension loss D
equals its upward dimension gain, so D=m/2.

Intersect frames in chronological order. An upward edge does not shrink
the running intersection: it already lies in the old, smaller frame. A
downward edge U -> W of codimension d loses at most d dimensions, since
for R subset U, `dim(R intersect W) >= dim(R)-d`. Therefore

    L subset G subset F,
    dim(L) >= dim(G)-m/2 = f-r-m/2.                        (D)

This calculation uses rational/real frame dimensions independently of the
data field k. No preservation of rational ranks under arbitrary finite
characteristic specialization follows from it.

Suppose final target frames are K_p = u_p^perp in a positive definite
rational/real inner product space. If target p is affected, then u_p is
orthogonal to L. Since L subset F, orthogonal projection P_F gives

    P_F(u_p) in F intersect L^perp,
    dim(F intersect L^perp) = f-dim(L) <= r+m/2.            (P)

For finitely many branches i, if a required coefficient vector k is
delivered and the projected roots `{P_F(u_p): k[p] != 0}` span F, the union
of permitted supports and (P) yield

    f <= sum_i (r_i+m_i/2) <= sum_i (r_i+m_i).

For f=7 this reproduces the predecessor's seven-rank floor. It does not
establish the required projected-root ranks: those are separate
source-bound finite geometry obligations. If a single branch's required
unprojected roots span V, support forces L=0 and (D) gives
`r+m >= 2f-r`, the predecessor's stronger one-branch inequality.

## 4. Minimal necessity controls

The following are counterexamples to relaxed hypotheses, not legal words
in the original model and not bugs in the predecessor.

1. **Allow one downward public MOVE.** Take V=Q, L=Q, receiver A at Q,
   final target frame K=0. A private read adds a nonzero q to A. Now move A
   downward Q -> 0 while preserving its logical scalar. The final target
   changes by q although L is not contained in K. This uses one receiver,
   one read and one downward transfer. Dimension one is minimal, since V=0
   admits no pair L,K with L not contained in K.
2. **Allow one unequal-frame public ADD.** Take V=Q, L=Q, A at Q and B at
   K=0. Read q into A at its common frame, then execute cross-frame
   `B <- B+A`. B changes by q although L is not contained in K. All public
   frames stay fixed, so this control relaxes ADD's frame restriction alone.
   Two public registers are required for this unequal-frame ADD control.

If one insists on a strictly positive entrance COPY, embed either example
in V=Q^2: let F=Q^2, G=L=span(e1), and COPY the unchanged q at rank one.
Read at G, return trivially to G, and ERASE against unchanged q. For the
downward control use target frame 0; for the ADD control use B's frame
span(e2). The private copied-total and closed-return conditions remain
satisfied. The only offending public event is the named relaxation.

An additional fixed-trace control is necessary in any proposed extension:
a branch-dependent guard at frame L cannot choose whether to update an
unrelated target K excluding L while hiding that guard from the event's
dependency list. Such control flow introduces a dependency L -> K and
violates (S); calling the visible payload operand constant does not remove
that dependency.

## 5. Applicability to the exact predecessor

The audited source text is `research/bit-copy-path/construction/PROOF.md`,
`construction/walk_certificate.py`, and `independent/REVIEW.md` at the
stated PR4200 head. The source checker explicitly tests:

- Every original public MOVE has nested entrance/exit frames and positive
  dimension increase (`literal_frames`).
- Every original ADD has the exact same actual source/destination frame,
  with fixed scalar coefficient +1 or -1.
- The postscatter target-writing interval is `[24069,25768)` and its
  records contain only MOVE and ADD; there is no downstream COPY.
- Registers 471..479, the nine copied sources, receive neither ADD nor
  MOVE in that interval; their values and source frames are unchanged.
- No actual target register is ever an ADD source, so the literal scatter
  coefficient k_j is retained rather than inferred from a clean trial.
- All final target caps are tested against their actual root-orthogonal
  hyperplanes. The new checker separately computes all 636 supplied frame
  ranks and all 111 final cap ranks, norms and hyperplane equalities.

The predecessor also computes ranks of the actual K-supported recipient
roots and of their projections onto each source frame. Those recipient
and projected-recipient rank claims remain predecessor evidence: this
new checker does not reconstruct K/R or rerun those particular ranks.

These checks are the right hypotheses for the written support proof. This
agent separately authenticated the raw WORD and GEOMETRY compressed bytes
and replayed their frame/operation trace using `source_check.py`, importing no
producer code. It checks all 38,927 records: 2,904 public MOVEs, 36,005 ADDs,
nine COPYs and nine ERASEs. The exact B interval has 1,699 records, comprising
760 MOVEs and 939 ADDs. It verifies actual source identities 471..479 at
entry frames 510..518, and that neither their values nor their frames are
modified within B. Public upward containment is checked by literal
inclusion of old frame root generators among new frame root generators,
which directly implies containment of their rational spans. A separate
fraction-free primitive-integer elimination computes the rational ranks
of all 636 supplied frame spans, verifies the exact positive MOVE ranks,
and checks source rank seven. It checks full-frame rank eight, all 111
final cap ranks seven, each port root's squared norm four, exact final
frame labels and 6,470 final cap-generator/root orthogonality equalities.
Rank seven plus containment in the nonzero root's perpendicular hyperplane
proves equality with that cap; orthogonality alone would not suffice.

This replay does not reconstruct complete root closures, R/K coefficients,
all 660 decoded columns, or physical MOVE semantics. Those remain separate
predecessor or companion evidence. The source trace
checks establish the support lemma's literal operation premises, rather
than treating the producer code's existence as proof that its inputs
passed.

A separate finite closure explores all reachable difference states of two
F2 public scalar registers with five rational frame labels
`{0,span(e1),span(e2),span(e1+e2),Q2}`. It permits every upward MOVE,
same-frame ADD, and read into a frame containing L, starting from every
frame pair and zero intervention difference. Its full finite-state closure
contains 283 states and 1,780 transition occurrences over all five choices
of L. This tests arbitrary finite schedule length in that finite abstract
model; it is not a proof for all rational subspaces. Four ordinary F2
double-read cancellations are accepted. Six nonzero-q paired executions
over all relevant dirty assignments demonstrate the two forbidden
relaxations. Normal and optimized Python runs produce identical receipts.

The written theorem itself has no enumerated-trace bound and is not
inferred from either finite replay.

## Remaining obligations and credit

No new source-preserving construction, frame compiler, native private-MOVE
ABI, recursive invoice, precision bound, selected-result change, or kappa
improvement follows. A changed public downward-query model, mixed query
totals, changed factory, data-dependent schedule, or different physical
caller needs its own support and complete cost argument.

Credit Ross Richardson/PR4200 and its independent review agent for the
unchanged-total closed-walk obstruction and finite-branch projection
argument. The source word/transport credit belongs to Ali Romman, Sagar
Thakrar and the DreamingOfClouds/eumemic/PR589/PR555 lineage retained by that
package. Russell Seligmann/PR757 and Cody Harris/PR761 own the separate
historical direct-decoder floor; this note does not rediscover it. This
independent audit and its paired-run/edge formulation were prepared with
substantial OpenAI Codex assistance; no human or formal-kernel review is
claimed. Apache-2.0.

## Open next questions

- Combine this independently replayed suffix frame/operation and rational
  rank trace with separately checked coefficient patterns and full
  endpoint semantics before claiming a complete actual R438 audit.
- If extending the model, classify every new dependency edge using (S),
  including control inputs, before reusing the rank-seven corollary.
- Keep physical feasibility, complete charged invoice and precision as
  separate obligations rather than interpreting this support lemma as a
  supplier or a selected-frontier result.
