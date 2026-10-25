# Private copied-total transport and paid coded-stage wrappers

This appendix answers two interface questions. A copied-total private packet
can leave its original centre frame and return without changing its logical
payload. That algebra requires a new controller contract and does not by
itself deliver the desired target correction. The proposed free coded-stage
decoder instead fails an actual current-frame commutation test. Its explicit
paid wrapper has a restricted cancellation lower bound above the available
budget.

These are exact operator statements and finite source checks. No new physical
supplier, precision theorem, owner schedule or kappa is admitted. The
same-query receiver obstruction is proved in
[`../construction/PROOF.md`](../construction/PROOF.md), with its finite
chronological checks in `walk_certificate.py`; that is the primary result
for the receiver question.

## Private payload, frame and ownership contract

Write the ADDRESS involution for an orthogonal projector P as

    D_P(h,t) = ((I-P)h+Pt, Ph+(I-P)t).

The same notation below denotes its induced permutation of complete VALUE
arrays. Composition identities for ADDRESS permutations hold for arbitrary
VALUE payloads, including correlated dirty payloads and complete spectators.
No linearity of the input payload as a function of ADDRESS is assumed.

The ordinary source and helper packets are arbitrary. The private packet is
fresh owned workspace, empty before COPY and empty after ERASE. This is the
actual copied-total interface, not permission to overwrite or discard an
arbitrary preexisting dirty private packet.

Let the immutable centre be stored as D_F q. Choose G contained in F and
copy into a new private packet by applying the residual D_G D_F. The result
is D_G q. A private MOVE from current frame U to frame V applies

    D_V D_U.

For nested U,V this is the single projector interchange on their orthogonal
difference, in either direction, with rank |dim V-dim U|. If the current
private packet is D_U q, the new packet is exactly D_V q. Each equal-frame
ADD from the private packet into a receiver at V therefore adds logical q.
All other receiver data remain arbitrary.

For any sequence G=U0,U1,...,Uk=G of nested adjacent frames,

    (D_Uk D_U(k-1)) ... (D_U1 D_U0) D_G q = D_G q.

This telescopes without commuting nonnested frames. Readers do not modify
the private packet. The final packet is therefore exactly the original
transported snapshot, and the original source remains D_F q. The original
transported-source ERASE equality holds. Returning merely the frame label
without applying the residual would not establish that equality.

In particular, for distinct seven-dimensional F,H and G=F intersect H of
dimension six, the sequence is

    COPY F -> G; MOVE private G -> H; read at H;
    MOVE private H -> G; ERASE at G.

Its complete residual-rank list is **(1,1,1)**. Neither MOVE is free.
There is no extra logical query kernel or compensation term caused solely
by the private excursion. An arbitrary preexisting private dirt would
invalidate the fresh-copy premise and is outside this statement.

The zero-rank COPY case is also legitimate algebraically: COPY F to F,
promote to FULL, return to F, ERASE. Its residual-rank list is **(0,1,1)**.
The rank-zero COPY still clones and later clears a complete packet; zero
native child rank does not mean zero copying or storage cost.

## What must change in the retained implementation

The exact consumed source files and hashes are in `PRIVATE-MOVE-SOURCES.json`.
They are frozen alongside this appendix.

`PRIVATE-MOVE-control.py.txt` rejects a private MOVE at two distinct gates:
the destination must be an ordinary role, and every MOVE requires no open
COPY interval. Its ERASE also requires the stored private physical version
to be unchanged. The finite check executes the frozen `LocalState` class
and verifies rejection at the private-destination gate.

`PRIVATE-MOVE-episode.py.txt` accepts a COPY, a sequence of target ADDs from
the snapshot, and its ERASE. It clones the complete source, obtains a
distinct owned residual result, reads that private packet, then clears
the private result and clone. The existing episode grammar does not
include intervening residual calls on the private packet.

A valid extension must distinguish a logical snapshot generation from
physical frame/version changes. It must:

* Keep the original source packet and its logical version unchanged.
* Admit only checked private transport operations and read-only target ADDs
  during this interval; a private ADD destination is not a transport.
* Associate every transport with its actual source-bound residual request,
  current frame, owner chart, complete packet and current incoming weights.
* Maintain the invariant `private = D_current q`; require the initial
  private frame again at ERASE and the unchanged source generation.
* Clear each superseded owned residual output and all residual work, while
  protecting the borrowed current private packet until its replacement is
  available. Restore physical heads and retain full spectators.

It is unsound simply to reset the old version counter after moving the
private packet. Conversely, a checked closed frame path need not be a
literal stack of reversed edges: the displayed potential identity already
proves closure for any admitted closed path. Each edge remains paid.

No such extended controller or provider has been emitted here. The generic
arbitrary-input residual theorem supports the operator being requested,
but it does not make a new private destination or request label accepted
by the old executable controller.

## Exact frame domain and native invoice

The checker reconstructs the actual 120 rank-seven catalogue hyperplanes.
Two examples use centre F=frame510 and receiver H=frame511 or frame512.
Their normals are

    n510=(0,1,1,0,-1,0,0,1),
    n511=(0,-1,1,0,1,0,0,1),
    n512=(0,-1,-1,0,0,1,1,0).

Each squared norm is four. The first pair is orthogonal; its intersection
and residual projectors are dyadic. The second has inner product -2 and
normal Gram determinant 12. Its intersection and residual entries have
denominators among 1,3,6,12. The exact sixteen-column checks prove the
COPY, promotion and return identities and reject omission of the return.

Thus arbitrary intersections are not automatically members of the old
636-frame dyadic catalogue. The second example does not define the
displayed projector modulo 3. It is valid over every Z/q^w with odd
prime q other than 3, and in particular in the inherited fixed-prime
regime q>2^80. A finite extended catalogue needs its own authenticated
projector and split-basis labels. There is no claim here of admission over
every odd prime-power ring.

For incoming unit weights A and tail reversal C, the retained residual is

    v=P(CD-A^-1 H),
    T_A(P)(H,D)=(H+A v,D-C v).

It is a conjugate of D_P. At a fixed outer cut the copied source's weighted
view, raw header and spectators must be retained; one must not apply the
producer's chart a second time. Source-bound preparation of a split
projector uses its full raw header, including high digits. In the fixed
large-prime regime each displayed rational rank-one projector is split,
so the generic good/fallback construction applies once the new request
provider is implemented. Every complete residual child includes its
own cleanup and inverse adapters.

For n=64f+delta with f>=1, each positive rank r residual uses, on a good
packet, one complete width-rf child and

    A(r) f ordered affine ADD slots,
    A(r)=2[r(127-r)+4096].

Both adapter halves and all zero coefficient slots are included. Set
A(0)=0 and emit no native child at rank zero. Therefore replacing a
rank-seven COPY by the rank-three private excursion gives

| Invoice item | Original COPY7 | COPY1, MOVE1, MOVE1 |
| --- | ---: | ---: |
| Positive residual requests | 1 | 3 |
| Child rank mass | 7 | 3 |
| Good affine slots divided by f | 9,872 | 25,332 |
| Extra affine slots divided by f | — | 15,460 |

For a power moment Phi_b(r)=r(64/r)^b, the child change is
`3 Phi_b(1)-Phi_b(7)`. This is distinct from the increased adapter count.
For zero-COPY/FULL/return the positive-request count is two and the
affine count is 16,888f, an increase of 7,016f over COPY7.

The inherited bad-packet allowance is
`epsilon*131072` per positive request, epsilon=10^-16. It increases by
`2*epsilon*131072` for the rank-three excursion, and by
`epsilon*131072` for zero-COPY/FULL/return. This is a conservative per-edge
allowance, not equality of bad classes for different projectors.

The source clone, private reads, erasure, coefficient preparation, routes,
rewinds and complete packet scans remain charged. If K distinct staged
packets are live, including an existing private packet, the frozen
residual lifetime result bounds MOVE by `(K+2)v+3R` and initial COPY
by `(K+3)v+3R`. In the 660-ordinary-role R438 word, both the initial COPY
and a private MOVE fit the scoped bound `663v+3R`: COPY has K=660;
private MOVE has K=661. This counts staged roles and the active residual,
not whole families, protected input, directories, routing, scatter,
peel/merge, control tapes or the longer private lifetime.

The exact VALUE transform preserves the logical q, so private ADDRESS
transport alone introduces no new signed VALUE coefficient growth.
Nevertheless new residual calls, numerical coefficient work, receiving
ADDs and a longer live snapshot need their own complete rounded/error
and storage analysis before supplier admission.

## The coded-stage wrapper and its actual forbidden free operation

Use the notation of `PROOF.md`: C_s is the actual routed source code A_s,
N the diagonal port-root interchange, F_s=N G_s, and F_s commutes with C_s.
The code commutes with G_t for t different from s. It generally does
**not** commute with the current G_s:

    [C_s,G_s]=F_s[C_s,N] != 0.

The actual A[3,0]=1 supplies a witness. Ports 0 and 3 have roots 2e0 and
2e3. On a port-zero impulse HEAD=e0, TAIL=0, `(NA)[3]` has HEAD=e0,
whereas `(AN)[3]` has TAIL=e0. Conjugation by the stage routes preserves
noncommutation because each route fixes and commutes with its port root.
The same conclusion holds for C_s^-1.

For the source-restored B'_s, the purported free target wrapper
`diag(I,C_s^-1) B'_s diag(I,C_s)` has target-only block
`C_s^-1 G_s C_s`, not G_s. This fails even when its source is zero.
The required target postdecoder is

    G_s C_s^-1 G_s = N C_s^-1 N,

which mixes HEAD and TAIL. It is not an equal-frame scalar ADD circuit
at the capped target cut.

There is a simpler exact paid wrapper for the original coded word, without
first restoring its source:

    B_s diag(N C_s^-1 N,I) = B_clean,s,
    diag(I,N C_s N) R_s = R_clean,s.                (W)

The checker verifies both identities over a noncommutative group algebra,
factoring off the central F_s on the two active banks. Every source code
and its inverse retain their stage index; no equality C_s=C_t is assumed.
The literal inverse code has 1,499 signed scalar ADDs. Each N sweep on
one complete bank consists of 111 positive rank-one port requests.
The direct implementation of (W) uses two such sweeps per local stage,
18 across the actual nine-stage recipe, or 1,998 rank-one requests.
Its full good-adapter, fallback and data-access invoice cannot improve
upon that child count.

## A restricted cancellation bound for those wrappers

This subsection covers a fixed ordered-barrier rewriting model. Retain
the chronological order of both the nine coded-call factors and every
individual C_s or C_s^-1 factor in (W). Move, combine and cancel only
the N sweeps. Ordinary scalar bank basis changes and the actual bridge
ADDs transport sweep matrices and the corresponding boundary functionals.
Reordering code factors or commuting a sweep across a composite product
of barriers is not allowed by this model. It does not cover modifying a
coded call, replacing an N sweep by a partial-port or different routed
query, or synthesizing a different coupled caller.

Over binary VALUE arrays put z=N+I, so z^2=0. A scalar bank-conjugate of
an N sweep has form `I+zP`, where P is a rank-one bank projector.
Products of such sweeps between fixed noncommuting operations add the
bank matrices P. Allowing arbitrary P and charging at least rank(P) is
a relaxation, so a lower bound in that model also applies to sweep
words. Scalar bank changes conjugate P and preserve rank.

At a code factor acting on bank i, any commuting sweep matrix must have
P_ii=0: its (i,i) commutator is `P_ii [N,C_s]`. At a forward coded call,
any commuting sweep similarly has P_ii=0 on the active source x.
For the role-swapped inverse, P_ii=0 on its active source y.

For completeness, write the active 2-by-2 bank block of P as
`[[a,b],[c,d]]` and factor off F_s. The forward code has matrix
`[[C_s N,0],[N C_s N,N]]`. Its upper-left commutator equation reduces to

    (a+b) z C_s = a C_s z.

If a=1, this either says C_s z=0, impossible since C_s is invertible,
or says C_s commutes with N, contrary to the actual witness. Hence a=0.
For the inverse `[[N,I],[0,N C_s^-1]]`, its lower-right equation with
d=1 would imply `[z,C_s^-1]=c z`. The diagonal port entries of C_s^-1
are scalar identities, so the left-hand side has zero diagonal port
blocks while c z does not unless c=0. The nonzero off-diagonal
commutator then rejects d=1. Blocks outside the active pair cannot
alter these active diagonal equations.

In each forward wrapper the last N_x is therefore trapped between
C_s^-1 and its forward coded call; in each inverse wrapper the first
N_y is trapped between the coded inverse and C_s. The actual
`recipe(4)` has nine such disjoint chronological intervals. Within
each interval the active diagonal bank coefficient is one. A sweep
commuting out through either boundary has coefficient zero there,
and scalar basis changes preserve the equivalent rank-one functional.
Thus each interval retains a nonzero bank matrix and costs at least
one bank sweep. Other commuting sweeps, even after bridge transport,
cannot remove this requirement.

The resulting restricted lower bound is **9 sweeps, or 999 rank-one
requests**. It already exceeds the parent allowance of less than
525.45 rank-tariff units over all nine stages. The true positive-power
cost is at least `999 Phi_b(1)`, before adapters, fallback and access.
This stops this precise commutation-only wrapper optimization; it is
not a universal paid-decoder lower bound.

## Reproduction

Run with standard-library Python 3.12:

    python3.12 -I -B -Werror composition/PRIVATE-MOVE-CHECK.py

The default recomputes and compares `PRIVATE-MOVE-RESULT.json` without
writing. `--output /absolute/new/path.json` explicitly emits a receipt.
The check authenticates every consumed source, reconstructs exact
rational projectors, executes the frozen old-controller rejection,
checks the exact group-algebra wrapper identities and lists the actual
nine chronological intervals. The all-path private transport proof,
receiver lower bound and restricted sweep argument are written
arguments; finite checks do not replace their stated hypotheses.
