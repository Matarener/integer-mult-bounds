# Proof: the length-8 P104 decoding code is unique

Prepared for Matarener with Claude (Anthropic), via Claude Code.

## 1. Setting

We use the P104 local word in the accumulated-block schema
(`p104-accumulated-block-composition/2`). The pinned inputs are the PR5907
word (`research/p104-helper468-rung-removal/WORD.json.gz`) and the selected
PR6030 word (`research/p104-helper470-twin-rung-removal/WORD.json.gz`).
The checker rules used below are the following:

- Each role carries a row and sits in a frame, which is a subspace of `F_2^9`.
- `ADD`, `COPY` and `SCALE` act only between roles in the same frame.
- `COPY` writes only into owned roles.
- `INIT` and `CLEAR` empty an owned row.
- A public role only moves up: its frame grows.
- An owned role only moves down: its frame shrinks.
- The paid cost of a move is the dimension difference.

There are 104 live roles. Live `l` starts in `<q_l>`, where `q_l` is an
odd-weight port vector. Its partner `l + 112` starts at `{0}` and ends in
the hyperplane `q_l^perp`. The live projection of the partner's final row is
`e_l`. Ports `i` and `j` *conflict* when `<q_i, q_j> = 1`. Because every port
has odd weight, `q_l` does not lie in `q_l^perp`.

## 2. From words to decoding codes

**Lemma 1 (frame decomposition).** Split every public row into two parts:

- a *lives-in-frame* part, which grows only by ADDs between public roles;
- an *owned-delivered* part, which collects everything received from owned roles.

Then the lives-in-frame part of a public role is always supported on lives
whose ports lie in the role's current frame.

*Proof.* The claim holds at the start, since live `l` holds `e_l` in `<q_l>`
and every other public role is empty. An ADD from public role `s` into public
role `r` happens in a common frame `F`. By induction, the support of the source
lies on ports in `F`. A public role's frame only grows, so the support stays
inside its later frames. SCALE preserves supports, and COPY never targets a
public role. Owned content enters only the owned-delivered part. ∎

`wordcode.decompose` checks this invariant after every event of both words.

**Corollary 2.** Let `w_l` be the owned-delivered part of partner `l + 112` at
the end. Then `w_l[l] = 1` and `w_l[m] = 0` for every port `m` that conflicts
with `l`.

*Proof.* The partner's frame only grows and ends at `q_l^perp`, so it always
lies inside `q_l^perp`. By Lemma 1, the lives-in-frame part is supported on
ports in `q_l^perp`. That set contains neither `l` nor any port conflicting
with `l`. The endpoint is `e_l = lives-in-frame + w_l`, which gives the claim
on those coordinates. ∎

**Definition.** A *decoding code* over a field `K` is a subspace
`W <= K^104` that contains, for every port `l`, a vector `w_l` with
`w_l[l] = 1` and `w_l[m] = 0` for every `m` conflicting with `l`.

Let `T` be a conflict clique of size 8; `T_INDEX` is one. Then the vectors
`w_t` for `t` in `T`, restricted to `T`, form the identity, so
`dim W >= 8`. By Corollary 2, the span of the partner parts `w_l` of any legal
word is a decoding code over `Q`.

**Reduction mod 3.** Assume all scalars of the word are dyadic, so every row
is 3-integral. Let `W` be a decoding code over `Q` of dimension 8 that is
spanned by 3-integral decoding vectors. Then the reduction mod 3 of the
saturated lattice `W ∩ Z_(3)^104` is an 8-dimensional decoding code over
`F_3`. Reducing a 3-primitive multiple of a nonzero vector of `W` gives a
nonzero vector whose support is contained in the original support.

## 3. The finite model over F_3

Let `W` be an 8-dimensional decoding code over `F_3`. Restriction to `T` is
then a bijection `W -> F_3^T`, so the vectors `w_t` (`t` in `T`) form a basis.

For a port `j` outside `T`, write `w_j = sum_t a_{j,t} w_t`. Evaluating at
`t'` in `T` gives `a_{j,t'} = w_j[t']`, which is 0 when `t'` conflicts with
`j`. So `a_j` is supported on `T_j`, the members of `T` orthogonal to `q_j`.
For every `j` outside `T`, `|T_j| = 4`; `Model.__init__` asserts this.

The unknowns are:

- the 384 trits `x_{t,m} = w_t[m]`, for `m` not conflicting with `t`;
- the coefficient vectors `a_j`.

On the clique the values are fixed: `w_t[t] = 1`, and `w_t[m] = 0` for every
`m` conflicting with `t`, which includes `T \ {t}`. Port `j` contributes these
equations, which are linear in `x` once `a_j` is fixed:

- `sum_t a_{j,t} x_{t,j} = 1`;
- `sum_t a_{j,t} w_t[m] = 0` for every `m` conflicting with `j`.

`Model.equations` builds exactly these.

**Gauge.** A diagonal sign matrix `D` maps decoding codes to decoding codes
(`w_l -> D_ll^{-1} w_l D`). It preserves zero patterns and weights, and sends
`a_{j,t}` to `D_jj^{-1} a_{j,t} D_tt`.

The search assigns ports one at a time. It keeps a partition of `T` into sign
classes, where two members are in the same class once their relative sign is
fixed by an assigned `a_j`. An option `a_j` is *canonical* when two conditions
hold:

1. its first nonzero entry is 1;
2. on the first member of every class it meets that is not the class of its
   first entry, its entry is 1.

*Completeness.* Take any solution and any node on its path. Fix the first
entry with `D_jj`. Then flip, one at a time, each further class that `a_j`
meets. A flip negates `D_tt` on the whole class, and also `D_{j'j'}` for every
earlier port `j'` whose support lies in that class. Earlier options keep their
form, because the support of each earlier option lies inside a single merged
class. The result is a gauge-equivalent solution that agrees with the node and
is canonical at `j`. By induction every solution is gauge-equivalent to one
reached by the search.

*Branching.* At a node with free ports `R`, the completions are the disjoint
union, over the canonical consistent options `c` of any single port `j` in
`R`, of the completions below `(j, c)`. So any branching order gives a
complete enumeration. `gen8.py` picks the most constrained port (MRV); the
replay simply accepts the port named in the certificate. Consistency means the
accumulated linear system over `F_3` has no row `0 = 1`. It is maintained by
exact incremental Gaussian elimination on bitmasks.

## 4. The certificate

`gen8.py` wrote a pre-order token stream:

- `n j`: an internal node branching on `j`;
- `d j`: a dead node, where `j` has no canonical consistent option;
- `s`: a leaf with all 96 ports assigned.

The root options are split into four parts by option index modulo 4. The parts
were generated on Kaggle, one process per part, and are stored in
`cert/part*.txt.gz`. Their node counts are in `RESULT.json`.

`replay.replay` re-runs the model along the stream and checks the following:

- At every internal node it recomputes all canonical consistent options of the
  named port and descends into each in order.
- At every dead node it checks that there is no such option.
- At every leaf it checks that no port is left.
- Every stream must end exactly when its subtree ends.

The certificate is therefore only a branching schedule. Every claim about
options is recomputed, so a wrong certificate can fail but cannot hide a
solution.

## 5. Result

**Theorem 3.** Up to the sign gauge, there is exactly one 8-dimensional
decoding code over `F_3` on the 104 P104 ports. The four parts contain one
leaf in total, and its linear system has no free variable. The code `C*` has
these properties:

- its decoding vectors are unique at every port;
- its decoding matrix `M = (w_l[m])` is sign-equivalent to `M^T`, so the
  column code is `C*` up to signs;
- its weight distribution is the one recorded in `RESULT.json`, with
  minimum weight 49 (208 words), then 52 (32), 62 (16), 65 (448), and so on.

The weight-52 owned deliveries of both pinned words (ten each) span exactly
`C*` up to signs.

**Lemma 4 (frame capacity).** A hyperplane of `F_2^9` contains at most 60
ports, and a subspace of codimension 2 contains at most 36. `verify.py`
checks this by enumerating all subspaces. Hence any 49 ports span a space of
dimension at least 8.

## 5a. Why the code exists: E8

The ports are 104 of the 120 root lines of `E8`. We write `E8` in `A8`
coordinates, so the root lines are `±(e_i − e_j)` and `±(2/3 on a 3-set,
−1/3 elsewhere)`. A port `q` of weight 7, with zeros at `i` and `j`, gives the
root `e_i − e_j`. A port of weight 3 gives the root with `2/3` on its three
coordinates.

These roots have norm 2. Two ports conflict (`<q, q'> = 1` over `F_2`) exactly
when their roots are orthogonal. The code `C*` is, up to signs, the Gram
matrix of these roots divided by 2. Over `Q` its eigenvalues are 13 (eight
times) and 0 (96 times). The missing lines are 14 of weight 3 and 2 of
weight 7. `verify.py` checks the norms, the orthogonality and the sign equivalence.

In clique coordinates every other root is `½(±r_a ± r_b ± r_c ± r_d)` over a
block of the Steiner system `S(3,4,8)`: there are 14 blocks with 8 lines
each, and 96 of these 112 lines are ports. The finite model of section 3 then
reads as follows. For each line `j` there are two 4-vectors `α_j, β_j` on its
block, with `<α_j, β_j> = 1` and `<α_j, β_k> = 0` for orthogonal pairs.

The `E8` solution is `α_j = β_j = ε_j`, the sign pattern of the root. This
works because `4 ≡ 1` mod 3.

Subsystems of three blocks through a pair of clique points do not force full
supports: every probed degenerate support is locally consistent. A proof
without the search must therefore use all of E8 at once. Such a proof is in
[`e8/E8-PROOF.md`](e8/E8-PROOF.md): frame factorisation over all 759 frames,
an A2 triangle argument, and a sign step in one frame. It is formalized in
Lean (`lean/CarrierCode/E8*.lean`).

## 6. Scoped cost corollary

**Corollary 5.** Take a legal word with dyadic scalars whose partner code
`W_P = span{w_l}` has dimension 8. Assume `W_P` has a basis `v_1, ..., v_8`
of delivered vectors, each carried down one owned chain. A chain is a
sequence of owned lives linked by same-frame COPY/ADD, and its cost is its
total paid descent. Make two single-stage assumptions:

- the live support of `v_c` lies on ports of the chain's root frame;
- every partner `l` with `a_{l,c} != 0` in `w_l = sum_c a_{l,c} v_c` receives
  `v_c` from that chain, in a common frame.

Then every chain costs at least 7, so the eight chains cost at least 56 per
call. This is exactly what the PR5907 word pays: chains 8→4→3→1 four times,
8→7→1 three times and 8→5→1 once.

*Proof.* Reducing `W_P` mod 3 gives `C*` up to signs (section 2 and
Theorem 3). So `v_c` has at least 49 nonzero live coordinates. By Lemma 4,
its root frame has dimension at least 8.

The vector `(a_{l,c})_l` is the functional "coefficient of `v_c`" evaluated
on the `w_l`. It is therefore a nonzero vector of the column space of `M`
over `Q`. That column space reduces mod 3 to the column code of `C*`, which is
`C*` up to signs. So at least 49 partners receive `v_c`.

A receiving partner's frame lies inside `q_l^perp`. The chain's frames only
shrink, so its lowest frame `B` lies in `q_l^perp` for every receiver, that
is, in the orthogonal complement of the span of at least 49 ports. That span
has dimension at least 8, so `dim B <= 1`. The chain descends from dimension
at least 8 to at most 1, so it costs at least 7. ∎

## 7. Limits

- **Larger partner codes are open.** The corollary needs `dim W_P = 8`.
  The selected PR6030 word has `dim W_P = 9` mod 3: one bookkeeping direction
  outside `C*`. Its ten weight-52 carrier deliveries still span `C*`. So the
  corollary describes PR6030's carriers but does not bound PR6030 as written.
  Codes of dimension 9 or more, and their cheapest carriers, are not
  classified here.
- **Multi-stage designs are not covered.** In such designs partners receive
  mixtures relayed through public roles, so a carrier's receivers are not
  forced to reach 49.
- **No new kappa is claimed.** The result removes "cheaper carriers for the
  same eight-dimensional code" as a source of paid-H1 savings in the local
  word.
