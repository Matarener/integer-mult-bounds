# Fixed-plane causal exposure bound

For each of the **120 pinned full E8 root lines and 153 rank-two frames
actually present in the pinned R438 word**, and every subset S of its 438
helpers, the retained complete partitions prove

\[
 \dim(E)\bigl(|S|-\operatorname{rank}_{\mathbf F_2}D_S\bigr)
 \leq 8\,|\mathcal X_E(S)|.
\]

The coefficient 8 is the least integer coefficient valid for this entire
specified finite family. This is an auxiliary rank-mass inequality under a
fixed causal promotion rule. It is not a complete native cost, owner, moment,
all-size, or multiplication-exponent statement.

## Exact objects and chronology

The scientific source pin is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
The byte-pinned word is `bit-r438-transport-rehost/words/r438-t154.json.gz`;
the full root list is `e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz`.
All exact hashes, columns, masks and partitions are retained in
`INDEPENDENT-RESULT.json`. Physical source registers are 0..110, targets are
111..221, and helpers are 222..659. One private ZERO field, 660, is reused
for the nine consecutive COPY/scatter/ERASE intervals.

Define D to be the 111-by-438 binary helper-to-target map of the retained
chronology with the initial compensation ADDs removed. It includes A, all
nine copied-total scatters, B and C. Signs reduce modulo two; this statement
does not assert independence of arbitrary signed integer target lifts.
The independent checker reconstructs all 27,175 events directly from the raw
word, then propagates the 111 final target covectors backwards through the
ADDs and copied snapshots. Every resulting D column agrees with the raw
initial compensation column. Its rank is 111, so its full nullity is 327.
No target rows are removed or quotiented.

For a fixed E, a helper entrance is marked as promoted after the initial
compensation. The prescribed common-E joining algorithm evolves those marks
as follows. At an ADD whose old common frame does not contain E, a marked
actor forces both actors to the joined frame; the marks combine by Boolean
OR. Upon reaching an old frame containing E, the promotion distinction is
absorbed. This is chronological propagation, not unrestricted reachability
in a graph that forgets time. Initial compensation is excluded from the
propagation. The private copied field stays ZERO, so its scatter ADDs do not
carry a promotion mark into targets. The A phase has no target incidence,
and these private scatters precede B, so the original ZERO scatter cuts
are consistent with this prescribed propagation model.

There are 120 resource labels: 111 final target caps followed by nine
chronological COPY source cuts. A resource is exposed if reached by a
promotion and its original frame does not already contain E. There is no
source-exposure label. The actual source exits are FULL, whereas all target
caps and all nine copied-total source cuts have rank seven. Thus, when E is
not contained, its join with such a hyperplane is FULL. The target lift adds
one rank and the COPY from that joined source to private ZERO adds one rank.
This does not price changes to intermediate source paths or the whole word.

Let e_E(h) be the 120-bit exposure mask for entrance helper h, and put
\(\mathcal X_E(S)=\bigcup_{h\in S}e_E(h)\). This union formula holds for
every S: each update is OR or a fixed reset and therefore preserves unions
of independently propagated initial marks. The checker uses forward bitsets
containing all 438 entrance identities simultaneously. It compares every one
of the 119,574 resulting helper masks with both complete retained receipts.
This construction is independent of the historical backwards propagation.

## Counting certificate, for every subset

This part is a written proof for an arbitrary finite binary column family,
exposure masks and positive integers r and lambda. It does not depend on
augmenting paths or an optimizer's claim of termination.

Take r colored copies of each helper. Suppose a partition assigns these
copies to r color classes and to resource classes, leaving g copies
unassigned. Require: the c-th color class uses only color c and its D
columns are linearly independent; each resource class contains at most
lambda copies, each incident to that resource; and every assigned copy has
exactly one owner. Restrict this partition to the colored copies of any S.
Each color class then contributes at most rank(D_S) copies. Only resource
classes indexed by the union X_E(S) can contribute, each with at most lambda
copies. At most g copies remain unassigned. Counting gives

\[
 r|S|\leq r\operatorname{rank}(D_S)+\lambda|\mathcal X_E(S)|+g.
\]

For each retained plane, r=dim(E) and lambda=8. The complete certificate
assigns all 438 colored copies when r=1 and all 876 when r=2, so g=0.
The checker verifies actual independence, color binding, incidence, capacity,
unique ownership and the exact complement of the assigned set. It also
checks every saved cut/count/mask field. The saved cuts are empty, and S=empty
attains auxiliary objective zero. Thus the maximum is exactly zero for each
fixed plane, and the displayed inequality holds for **every** S without
enumerating its 2^438 possibilities.

All 120 root spans are distinct, including the full-list root lines absent
from the punctured word's root list. All 153 rank-two frame spans in that
word are distinct. Exact rational row reduction and annihilator tests bind
the family and containment relations. This finite census is not a proof
for every rational plane or a size-parameterized family.

## Least integer common coefficient

The cap-eight receipt for the actual frame numbered 116 gives an immediate
counterexample to coefficient seven. Reconstruct E from that raw frame and
choose all 438 helpers. Then

\[
 r=2,\quad \operatorname{rank}D_S=111,\quad
 |\mathcal X_E(S)|=86+4=90,
\]
\[
 2(438-111)-7\cdot90=654-630=24>0.
\]

The exact union mask and all helper IDs are retained in the independent
receipt. Consequently every integer common coefficient must be at least
eight, and the complete partitions show eight suffices. The witness only
forces a real common coefficient to be at least 654/90=109/15; it does not
establish the optimal real coefficient. No separate weight-search receipt
is used in this argument.

## Cost and interface limits

The left side counts r kernel directions for a chosen common-E helper basis
change. Every selected helper, including pivot helpers, participates in the
prospective promotion; only nullity supplies the displayed kernel term.
This is not net stock credit. Shrinking helper residuals also reduces native
progress credit, and promoted pivot/public-source paths can change even when
nullity is zero. A rate implication needs a complete owner/moment benefit
bound and every changed query/COPY/source charge.

The private field here stays ZERO. B10's global-E private-at-E construction
has a different COPY bill. Neither model can silently replace the other.
The theorem uses full D, one fixed E and the retained chronology. It cannot
be transferred to cold-target quotients, mixed E with overlapping resources,
operator-valued kernels, retimed words, changed private cuts, or arbitrary
planes. It supplies no literal selective joined-frame native word, native
owner assignment, precision estimate or physical tape compiler.

## Provenance

The R438 source word is due to Ali Romman (PR1043); the pinned transported
word and its retained conditional scope are due to Sagar Thakrar's
`bit-r438-transport-rehost` package, with the PR589/PR555 lineage credited
there. The full E8 source credits Zhihao Chen's PR386 geometry and Dylan
Crow's PR370 format/checker lineage. The changed-endpoints lane supplied
the causal model, finite partitions and receipts. Its source explicitly
credits the parent investigation for the matroid-union strategy and
all-subset counting argument. This review adds independently reconstructed
semantic columns and forward causal masks, exhaustive certificate checking,
and the frame-116 least-integer consequence. It is not a new claim to those
underlying constructions. Apache-2.0; substantial OpenAI Codex assistance.
