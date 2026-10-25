# Review of the PR3259 path-embedding argument (with PR3252 and PR3427)

Objects, at their exact heads:

- PR3259 (Nick Petalas, `b572b0c25569898579041200e95731c5a43c9189`),
  `research/p104-pooled-cut-independent/README.md`, sections "Contract and
  conclusion" and "Why one contact per dimension is a necessary relaxation"
  (README lines 17-100).
- PR3252 (Nick Petalas, `4784b71d2e0833537c9ae1e8be05ad2a6b334d92`),
  `research/p104-memory-relaxation-soundness/PROOF.md`.
- PR3427 (Jose Manuel, jmbarrancoml, `344774ba08a73fc3a85fdcb93fb319927bde3ea2`),
  `research/p104-source-preconditioning/PROOF.md`, "Pooled path-compression
  lemma". Only what it consumes is reviewed.

This is an audit, not a construction. It changes no κ and no frontier, and it
proves no P104 impossibility outside the stated contract.

## Verdict

These verdicts come from an author-checked, AI-assisted review. Ten AI
review passes in the same loop, over three rounds, checked the package; no
independent human or formal-kernel review has been done.

1. **PR3259's argument is valid as a necessary support test under its stated
   contract.** Each step below is valid as written. Two steps need a sentence
   that is implicit in the contract, recorded as clarifications rather than
   repairs. Under that contract, `C[71,102] = -1/2` cannot be delivered.
2. **The test is sound but far from sharp.** It discards one fact that every
   legal dependency path has: its frames are nested across dimensions.
   Reinstating that fact gives a valid criterion with **one recombined helper
   per path**. That lemma is stated in PR3427 and is re-proved below with every
   dimension case. Under it, **2,682 of the 4,992 required entries are
   unsupported**, containing a perfect matching (at least 14 per row and 9
   per column). PR3259's relaxation grants 10,815 source/target pairs,
   against 2,310 for the sharp criterion. "Exactly one missing coefficient"
   describes PR3259's test, not the contract. PR3259 itself says that passing its test is not a realization.
   PR3427 already states this criterion and its untimed exactness, and its
   published masks for sources 0-3 already exclude 92 required entries that
   PR3259's test grants. What is new here is the step-by-step review, the
   full 104-column count with its closed form, a multi-hop (PR3252
   full-memory) check over all 104 columns and 2,309 types that does not
   assume the lemma (PR3427 ran the same operations on its four columns),
   the rank and vertex-cover consequences, and the rows R1-R3.
3. Consequently the fixed-cover contract is closed by a much larger obstruction
   than one coefficient. A contract change that only reopens `C[71,102]` does
   not complete the correction. Examples are PR3427's rank-one source shear, a
   moved helper, or one extra dependency. The pending concrete corrections
   (README, "Concurrent pending work") change a frozen path, the channel or
   storage, so they lie outside K1-K7 and are not judged here.
4. **PR3427 consumes its own one-helper lemma and PR3252's full-memory
   operations, not PR3259's layered recurrence.** The lemma is valid. Its
   published four-column support masks are reproduced exactly by code written
   for this review. Its rank theorem stands as stated. Applied to all 104
   columns, the same argument gives **`rank(U-I) >= 23`** (section below).
5. **PR3252's theorem is valid** for its stated recurrence and contract.

## Contract, as used

PR3259 states the contract in prose. It is numbered here so that each step can
cite it. PR3259 first fixes a matching, one arrival per departure, and then
grants one virtual helper for every compatible pair at once. K1 is that pooled
relaxation. Every matching-based program satisfies it, so each exclusion below
holds a fortiori for every single matching. The exactness statement (the
converse below) is made for the pooled relaxation only.

- **K1 fixed cover, pooled.** Every added helper has one full flag through
  `0 < L[a//2] < A[a] < F3 < ... < F6 < B[b] < H[b//2] < FULL` for a compatible
  pair, `A[a] <= B[b]`. Skipped dimensions are granted, but the flag still
  passes through `L, A, B, H`.
- **K2 monotone.** A helper never descends or changes frame at a fixed
  dimension. It is never reloaded or reused with another flag.
- **K3 equal frames.** A scalar operation transfers dependence only between
  registers whose current frames are equal. A transport is register-local.
- **K4 immutable X.** Sources keep their original channel frame path and are
  never written. They are read only at frames of that path.
- **K5 unread Y.** Targets keep their original channel frame path and are
  never read. They receive additive increments only.
- **K6 no other source-dependent state.** The correction neither reads nor
  writes original channel helpers (G, D, Q, C) or other correlated storage.
  The channel contributes its unchanged `G/2`.
- **K7 independent dirt.** Helper initial values carry no X dependence.

The original channel word satisfies K4 and K5: X is never written and Y is
never read. The verifier checks this from the 4,058 events (`channel_roles`).
K6 is a premise about the correction, not about the channel.

## Step-by-step review of PR3259 (checklist a-h)

| # | Step in PR3259 | Uses | Verdict |
|---|---|---|---|
| a | Skipped dimensions are granted; frames at dims 1, 2, 7, 8 are the singletons `L, A, B, H`; dims 3-6 are any d-flat in `[A,B]`. | K1 | Valid. The intervals are exactly the members a K1 flag can take. Nesting between layers is dropped, which only enlarges the test. Forcing every helper through a fixed `L[a//2]` and `A[a]` is a premise, not a consequence. Row R2 shows it is load-bearing. |
| b | "Within one dimension, a monotone helper has one fixed actual frame." | K1, K2 | Valid. Clarification: this needs K2's "never reloaded or reused". A helper that is cleared and restarted with a new flag is a second helper. If it has a pool type, the pool still covers it. |
| c | Sources read at every frame of their frozen path; targets receive at every frame of theirs; direct X-to-Y contacts granted. | K4, K5 | Valid. X is never an intermediate node because nothing writes it. Y is never intermediate because nothing reads it. Untimed reads and writes are a superset of legal ones. |
| d | Original channel helpers excluded. | K6 | Valid as a premise. Row R3 shows it is load-bearing: reading channel helper state reopens every entry. |
| e | Dirt has no source coefficient; cancellation cannot create one. | K7, linearity | Valid. A coefficient of `X_s` in `Y_t` is a sum over dependency paths of products of operation scalars. With no path it is zero. Restoration operations are linear operations and are included. |
| f | Same-dimension runs share one frame, so first and last helpers are adjacent and one step suffices. | K2, K3 | Valid, including a read or write in mid-run (the path starts or ends there) and runs that revisit a helper. Only the endpoints' common frame is used. Equal-frame groups in an actual program are cliques. |
| g | Read-first seeding; accumulation after the edge; dims 0 and 9 excluded; early writes. | K4, K5 | Valid. Seeding the layer's reads before the single step covers a read followed by relays at that dimension. Accumulating after the step covers relays followed by a write. X frames have dimension at least 1 and Y frames at most 8, so dims 0 and 9 cannot join a read to a write. The recurrence accumulates at every layer, so Y71's dimension-5 writes are checked. |
| h | Pooling: "every matching embeds by its selected edges". | K1 | Valid, and slightly stronger than stated. Any multiset of helpers with pool types embeds: helpers of one type merge into one virtual helper, whose state is a union. PR3259's layered test does not need the pool to be closed under recombination. The sharper lemma below does; see `unpooled_relay_example`. |

Stop-rule outcome: no step fails. The control engine reproduces every PR3259
number: missing set `{(71,102)}`, forward counts
`16,25,52,365,1725,2283,2285,2297`, a 37-edge backward cone and disjointness.
It uses literal d-flat hosting with reduced-echelon keys and shares no code with
PR3259.

## The sharper valid criterion: one recombined helper per path

**Lemma.** Assume K1-K7 and suppose a program gives `Y_t`'s increment a nonzero
coefficient on `X_s`. Then either `X_s` and `Y_t` share a path frame, or there
are frames `V` on `X_s`'s path and `W` on `Y_t`'s path, and a compatible pair
`(a,b)`, such that

```
V < W,
V lies in (a,b)'s interval at dim V, and W in its interval at dim W.
```

Here `V < W` means V is strictly contained in W. The interval at dimension d is
`L[a//2]`, `A[a]`, `[A[a],B[b]]`, `B[b]` or `H[b//2]` for d = 1, 2, 3-6, 7 or 8.

*Proof.* Take a dependency path. Its first node is a read of `X_s` at frame V
and its last a write into `Y_t` at frame W. By K4 and K5 every intermediate node
is a helper. By K6 none is a channel register. By K3 scalar steps keep the frame
and transports enlarge it. So the frames along the path form a chain, and
`V <= W`. If `V = W` the pair shares a frame. Otherwise `1 <= dim V < dim W <= 8`.

*Choice of departure a.* Let P be the first path frame of dimension at
least 2.

- If `dim V >= 2`, then P = V. Let a be the departure of the reading helper.
  Its flag passes `A[a]` at dimension 2 and V at `dim V`, so `A[a] <= V`.
- If `dim V = 1`, the run at dimension 1 shares frame V (step f). Let h' be the
  helper that carries the path out of dimension 1, from V to P, and a its
  departure. Its dimension-1 frame is V, so `L[a//2] = V`. Its flag passes
  `A[a]` and P, so `A[a] <= P`.

*Choice of arrival b.* Let Q be the last path frame of dimension at most 7.

- If `dim W <= 7`, then Q = W. Let b be the arrival of the writing helper.
  Then `W <= B[b]`.
- If `dim W = 8`, let h'' be the helper that carries the path into dimension 8,
  from Q to W, and b its arrival. Then `H[b//2] = W`. Its flag passes Q and
  `B[b]`, so `Q <= B[b]`.

*Compatibility.* If h' = h'' (the path leaves dimension 1 and enters
dimension 8 in one transport), `A[a]` and `B[b]` lie on one flag, so
`A[a] <= B[b]`, and V, W lie on that flag too. Otherwise P comes no later than
Q along the path. This is immediate unless `dim V = 1` and `dim W = 8`. In that
case the step out of dimension 1 and the step into dimension 8 are different
steps, and the first precedes the second because frames along the path never
shrink. So P <= Q, and

```
A[a] <= P <= Q <= B[b],   V <= P,   Q <= W.
```

In every case `A[a] <= B[b]`, so `(a,b)` is in the pool, and also
`V <= B[b]` and `A[a] <= W`. The spaces `L[a//2] <= A[a]`, V, W and
`B[b] <= H[b//2]` therefore form a nested partial flag:

- for `dim V = 1`, `V = L[a//2]`;
- for `dim V = 2`, `V = A[a]`;
- for `dim W = 7`, `W = B[b]`;
- for `dim W = 8`, `W = H[b//2]`.

That partial flag extends to a full flag. One helper of type `(a,b)` therefore
admits both V and W. ∎

The proof uses the fact that the pool contains *every* compatible pair, so
that the recombined type exists. For a type list without that closure the
conclusion can fail. The verifier's fixed `F_2^4` example relays across two
rigid types at a shared plane. It lies in PR3259's test but outside the
one-helper test, and the exhaustive small-domain search below finds 33 more
such pairs.

*Second methods.* Two checks support the lemma beyond the written proof.

- **Small domains.** On 4,500 seeded pooled `F_2^3`/`F_2^4` instances, an
  exhaustive untimed reachability that does not assume the lemma gives
  exactly the one-helper support every time. Each of its 4,264 helper-only
  pairs is realized by an explicit program in the checked interpreter, with
  exact `Fraction` coefficients. The instances include 54 (75 pairs) where
  PR3259's test is strictly looser, the only places where the lemma's extra
  precision can be tested. On 4,500 unpooled instances the same search finds
  33 pairs on 26 instances outside the one-helper test, each realized by a
  legal program, so the check has teeth. The 9,000 random pooled programs
  (4,500 directed programs run in the checked interpreter and 4,500 uniform
  programs legal by construction; 1,043 nonzero coefficients counted per
  program, 604 of them on pairs whose X and Y chains share no frame) are a
  soundness sample only; on unpooled instances they found none of the 33
  escapes.
- **P104.** A new implementation of PR3252's multi-hop full-memory
  recurrence over all 104 columns, which does not assume the lemma, gives the
  same support on all 10,816 pairs. PR3427 ran the same operations on its
  four columns.

*Converse (untimed).* If the condition holds, one helper of type `(a,b)` with
that full flag reads `X_s` at V and writes `Y_t` at W. With the relative timing
of different registers relaxed, the criterion is therefore exact for the pooled
contract. No sound untimed support test under K1-K7 can exclude more pairs.
Timed tests can. A single fixed matching has fewer helper types, so its support
can only be smaller and at least 2,682 entries stay unsupported; exactness is
not claimed there.

*Where PR3259 loses precision.* At layer d PR3259 lets helper w relay through
any d-flat that w shares with a neighbour. It does not require that flat to
contain the frame through which the signal reached w. The lemma keeps that
containment.

*Why K4/K5 matter for the lemma, not only for PR3259.* The choice of a and b
uses a helper at the dimension-1 exit and the dimension-8 entry. If Y may relay,
a path can leave dimension 1 inside a target that the channel transports
upward. No helper then carries the source line. The verifier's F_2^3 program
(`y_relay_counterexample`) does this with four scalar operations. It
delivers a nonzero coefficient outside both PR3259's test and the sharp test.

## Finite consequences at P104 (verifier)

| Quantity | PR3259 layered test | Sharp one-helper criterion |
|---|---:|---:|
| Supported source/target pairs | 10,815 | 2,310 |
| Required entries unsupported | 1 (`(71,102)`) | 2,682 (a perfect matching; at least 14 per row, 9 per column) |
| Values of unsupported entries | `-1/2` | 1,801 at `-1/2`, 881 at `+1/2` |
| Pairs granted with `C = 0` | 5,720 off-diagonal and 104 diagonal | none |

The sharp support is computed three times: the one-helper criterion in two
loop orders (reduced-echelon keys with helper-type masks, and point-set
bitmaps looped by helper type), and an independent multi-hop implementation of
PR3252's full-memory recurrence over the whole pool. All three agree on all
10,816 pairs.

The sharp support has a simple shape. It is exactly the 2,309 compatible slot
pairs `(a,b)` read as port pairs (target `b//2`, source `a//2`), which are
distinct and all required, plus the pair `(73,83)`. That extra pair comes from
a dimension-4 frame of X83 admitted, with Y73's cap, by one pool type,
`(17,147)`, and by no other. Each own pair is admitted by its own type, and 31
of them also by another type. Hence `2,682 = 4,992 - 2,309 - 1`. At P104 no X
path shares a frame with a Y path, and dropping the containment `V <= W`
changes no pair, so containment is never decisive here. The verifier asserts
each of these facts.

The 2,682 missing entries contain a perfect matching: Kuhn's augmenting-path
matching has size 104, so by König's theorem no fewer than 104 rows and
columns cover them. Every row holds at least 14 and every column at least 9.
Under the criterion an entry's support depends only on the frames of its
source and target paths and on the cover, so a reopening that keeps K1-K3,
K6, K7 and the K4/K5 roles and changes only individual X or Y frame paths
must change at least 104 of them. This makes no cost claim.

For sources 0-3 the per-source target masks equal PR3427's published masks
exactly. They exclude 92 required entries, all granted by PR3259's test.
Those masks come from PR3427's direct criterion and from PR3252's full-memory
operations.

## PR3252 PROOF.md (shorter review)

The theorem makes two changes to PR3182's recurrence: it deletes the output
`break` and it adds direct contacts. Its full and one-step memory modes are then
necessary tests under PR3252's contract, items 1-5. That contract is
PR3259's K1-K7 written with per-helper bounds `L(h,d) <= F(h,d) <= U(h,d)`.

- *Run compression.* Valid; same argument as step f.
- *Relay of old state only.* Valid. A fresh read followed by a relay at the
  same dimension ends at a receiver with the read frame. Complete untimed
  snapshots grant that receiver its own read, and PR3252 says so explicitly.
  The argument fails for an incomplete read set, as PR3252 also states.
- *Witness induction.* Valid. The relay guard `S + L(h,d) + L(w,d) <= U(h,d) ∩
  U(w,d)` with the dimension bounds holds whenever the actual common frame
  contains S. Carries keep `S <= F`.
- *Pruning.* Valid, because the guards are monotone under shrinking a memory.

The review applies the theorem to one merged helper per pool type. That is
justified: actual helpers of one type have identical bounds, contacts and
granted reads, so the outputs of any multiset of them are contained in the
one-helper-per-type run, whose memory set is the union. A relay from such a
helper to itself only produces a memory `T >= S`, which the monotone guards
make redundant.

The full-memory mode keeps a lower bound on the frame the signal used. Like any
sound untimed test under this contract, it cannot be stricter than the sharp
criterion, which is exact. A new implementation over the whole 2,309-type pool
and all 104 sources (`full_memory` in the verifier) **equals the sharp criterion
on every pair**: 2,310 supported pairs and the same 2,682 unsupported required
entries. The 2,682 count therefore rests on two separately proved sound tests,
computed by different algorithms. The one-step mode forgets the memory bound
and is weaker; it was not run. PR3252's finite checks use fixed matchings and
F_2^3 interval fixtures. The proof is universal over its contract, and no gap
was found.

## What PR3427 consumes

- Its rank theorem rests on its own "pooled path-compression lemma", which is
  the lemma above. It also uses a finite four-column certificate computed two
  ways: the direct criterion and PR3252's unchanged full-memory operations on
  a 2,309-helper model.
- It cites PR3259 for the 2,309-pair pool and as the motivation for the
  one-shear candidate at `(71,102)`. It does not need PR3259's recurrence to be
  correct or sharp.
- At code level it depends on PR3259 more than the citation suggests. Both of
  its methods execute PR3259's `verify.py` routines for inputs, frame paths,
  endpoints, interval bounds and contacts. Its boundary check also replays
  PR3259's layered recurrence and asserts that the missing set is exactly
  `(71,102)`. That replay serves only the one-shear boundary; the rank
  theorem does not depend on it. The independent engine here covers the
  shared geometry code.
- The consumption is justified. The lemma is valid, and the four-column masks
  are reproduced exactly by an engine that shares no code with PR3427.

## Consequence for PR3427: rank(U-I) >= 23

PR3427's contract adds an invertible scalar source preconditioner U to K1-K7.
The prepared sources `X' = UX` stay in the original frames, so the support
criterion is unchanged. The correction must deliver `D = U^-1 - M` with
`M = G/2`, and D vanishes on every unsupported pair. Write `V = U^-1`. On an
unsupported pair, `(V - I)[t,s] = M[t,s] - [t = s] = -C[t,s]`.

Every diagonal pair is unsupported, and its entry is consistent because
`C[t,t] = 0`. Hence for any rectangle `R x S` of unsupported pairs, overlap
allowed,

```
rank(U - I) = rank(V - I) >= rank C[R,S],
```

using `V - I = -V(U - I)` for the equality.

A principal block `C[S,S]` is fully unsupported exactly when S is
independent in the undirected support graph: no pair of S is supported in
either order (diagonal pairs never are). A maximum independent set has 23
ports,

```
S = 8 11 17 18 23 30 34 37 42 50 51 58 59 63 70 71 78 80 84 87 91 96 100,
```

by two exact searches (a branch and bound with a greedy colouring bound and
a pivoted Bron-Kerbosch). Exact `Fraction` elimination gives
`rank C[S,S] = 23`, and an integer Bareiss determinant gives
`det(2C[S,S]) = 2^30`, so `det C[S,S] = 2^7`.

Thus `rank(U-I) >= 23` under PR3427's contract, against its published 4.
This prices no joint preparation. No unsupported principal block does
better; a non-principal rectangle or a min-rank completion may force more.
Rectangles alone cannot go past 31. On an unsupported rectangle,
`C[R,S] = I[R,S] - (G/2)[R,S]`; `R ∩ S` is independent, since each of its
pairs is unsupported in both orders, so `|R ∩ S| <= 23`; and
`rank(G/2) = 8` (asserted). Hence `rank C[R,S] <= |R ∩ S| + 8 <= 31`.

## Load-bearing hypotheses (support level, sharp criterion)

The rows are support-level necessary-test relaxations. They are unpriced and
give no coefficient or dirty restoration. Each row relaxes one item. The five
rows R1, R1u, R1c, R2 and R3 relax three hypotheses: K5 in three variants
(R1u was added at a round-1 review's request), K1 and K6. The task's stop
rule planned at most three rows; TASK.json records the deviation. Like the
sharp criterion, the rows relax the relative timing of different registers
but keep the order of operations along one dependency path.

| Relaxed item | Reaches `(71,102)` | Sharp-missing entries reopened | Minimal witness (operations counted, unpriced) |
|---|---|---:|---|
| none (sharp baseline) | no | 0 of 2,682 | - |
| PR3259's dropped cross-layer nesting (a proof relaxation, not a contract change) | no | 2,681 | layered test |
| K5, correction-only Y relay, keeping each target's write-before-read order (R1) | no | 0 | none at P104; F_2^3 escape uses 4 scalar operations |
| R1 without that order (R1u; a looser test, since no program reads content before it is written) | yes | 2,682 | - |
| K5 with the channel's own Y content readable, including target feedback (R1c) | yes | 2,682 | feedback on `Y71`: read it at its dimension-5 snapshot, after the channel has deposited its X102 term, and add a multiple back (1 read and 1 write, or 1 self-add) |
| K1, free nested flags: helpers not tied to `L/A/B/H` (R2) | yes | 2,682 | one helper with a free flag from X102's dimension-1 frame to Y71's dimension-8 frame; 1 read, >= 1 transport, 1 write |
| K6, reads of old channel-helper state (R3) | yes | 2,682 | one equal-frame add from `D11` into `Y71` at their shared dimension-5 frame |

*R1 and the target's own order.* In R1, content written into `Y_u` at one of
its frames can be read only at that frame or a later one. Every program obeys
this, because `Y_u`'s frames ascend in time; it is the path order that makes
path frames nested, applied at a target used as a relay. Correction content
reaches targets at their final caps (2,310 source arrivals, one for each
supported pair) and in 55 further source arrivals at 26 lower target
snapshots (31 arrivals on 19 dimension-5 snapshots, 24 on 7 dimension-6
snapshots). Content at a cap can be read only at that cap, which feeds only
itself because the 104 caps are distinct. The lower arrivals relay nothing
new. So R1 reopens nothing. R1u
drops the order, lets cap content be read at the target's low frames, and
reopens everything. R1's zero therefore rests on that order.

*R1c and R3.* Both use the channel's actual coefficients, recorded per register
and frame from an exact `Fraction` run of the 4,058 channel events. The same
run checks that every Y increment equals `G/2` exactly in the sorted port
order, with all helper dirt cancelled, and that every channel add is at equal
frames. The channel first puts `X102` into `Y71` at event 3378, with
coefficient `1/2`, from `D11` at dimension 5; the R1c and R3 witnesses read
that state. Both rows reopen every entry for the same reason: the channel
already delivers the support of `G/2`, which contains every off-diagonal
required entry. Any access to the channel's source-dependent state exposes
that support, through its helpers or by reading a target after the channel has
written it. Scaling that state is not a correction; its coefficients, dirt and
cost are unknown.

Known rows are cited, not recomputed:

- PR3013: component/containment pooling reaches all 4,992 entries.
- PR3427: a one-H2 source shear removes the `(71,102)` requirement, but
  `D[3,2]` stays unsupported. A source preconditioner needs `rank(U-I) >= 4`
  (23 by the section above).

Reading. Among the rows computed here, two hypotheses each reopen every entry:
the fixed cover (K1) and the exclusion of the channel's source-dependent state
(K6, including its exposure through Y). Unread Y matters at P104 only through
that exposure, given each target's write-before-read order. The rows are not
a complete map. Not computed as rows at P104: frame descent (K2), cross-frame
mixing (K3), changed source or target frame paths and source mutation (K4,
K5), dependent dirt (K7) and extra correlated storage. The small-domain negative
controls show that descent, cross-frame mixing, off-cover flags and correlated
old state can each escape both tests. Changing a frozen target path also
suffices at support level, one row at a time: every X path ends at FULL, so a
target that visits FULL shares that frame with every source (pending #3618's
T48 prices one such row at +2 rank mass). Path changes alone must touch at
least 104 registers. A reopening must change at least one of K1-K7, or add
storage, and must support all 4,992 required entries, in particular the 2,682
missing here, with a full bill; a changed cover or path can lose some of the
2,310 pairs supported now.
