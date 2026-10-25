# A first-touch cut gives an input-side phase correction

## Exact scope and retained sources

This is a structural lemma for the eight separately labelled physical
streams used by PR #3187,
`research/rank7-idle-star-stream-obstruction/algebra.py`, at canonical main
`12fa8c5c844be21bfefb38a19503fbd867a11244`. It addresses the narrow
eight-stream binding requested in Jacob Sussman's PR #4268, retained at
`45323d210ebf6f4b201b1d2a27729d14d059f2e2`:

- [source/PROOF.md](source/PROOF.md), section 3, items 6 and 8, requires a
  smaller-job word and literal heads, including the absence of earlier
  hosted use.
- [source/TASK.json](source/TASK.json), open question 2, requests the cut in
  the community's own eight-stream model, with a wrong-cut control.
- [source/tools/g0_staged.py](source/tools/g0_staged.py) classifies heads in
  the predecessor's own lowering/network. Its gate-read accounting is
  explicit; its classification is not automatically an eight-stream
  chronology certificate for the current replay.

The allocation in scope is the unchanged PR #2979 T74 allocation. No claim
about the alternate A-fc allocation or another instance follows here.
No code, native word internals, Lean proof, rate inequality, or outer
supplier theorem is executed or verified by this mathematical argument.

The retained eight-stream replay is at cover identity `g = I`, under its
completed-local-invocation contract. In particular it omits the separate
bank padding and the all-family correction that is zero at this cover.
An all-character statement below is within that stated model and cover;
it is not an all-cover statement.

## 1. Phase and multiplication conventions

For a Fourier label `chi in F2^73` and an address mask `v in F2^73`, write

```text
dot(chi,v) = sum_j chi_j v_j mod 2, represented by the integer 0 or 1.
```

For physical stream `s in {0,...,7}`, let `E_s(z)` be the diagonal `8 x 8`
matrix with `z` at position `(s,s)` and ones elsewhere. A literal ordered
list `A` of axes has phase

```text
theta_A(chi) = sum_{v in A} dot(chi,v) mod 4,
C_{s,A}(chi) = E_s(i^{theta_A(chi)}).
```

The sum is taken as an integer before reduction modulo four. It must not
be replaced by `dot(chi, XOR_{v in A} v)`: two summands equal to one give
phase `-1`, whereas that XOR parity would give phase `1`.

The retained `phase` operation rotates a matrix row. Its `shear` operation
adds a multiple of a source row to a destination row. Thus states are
columns and chronological operations `A_1,...,A_N` have total matrix

```text
M = A_N ... A_2 A_1.
```

Later operations multiply on the left. Input-side corrections multiply
on the right.

At an `idle_cover_sweep`, a child's stream is the literal
`s = 2 * pair + side`, with `pair` and `side` from the bound plan. The
retained event contributes on that stream

```text
E_s(i^{sum_{v in residual[child]} dot(chi,v)
          + 2 dot(chi, translation_after[child])}).
```

Suppose a fixed literal sublist `A` of that child's residual axes is
deleted and every other event is unchanged. In particular, the
`translation_after` term is retained. The changed event is exactly

```text
H_cut(chi) = H(chi) C_{s,A}(chi)^{-1}.
```

This remains true when the same idle event also phases the other stream
of its pair: the two diagonal phases commute. The chosen sublist must be
fixed by the input data and cut rule, rather than chosen separately for
each sampled character.

## 2. The first-touch lemma

Let `H` be the event being cut, let `P` be its chronological prefix, and
let `S` be its suffix. Thus

```text
M = S H P,                  M_cut = S H C^{-1} P.
```

Assume that `P C = C P`. Then

```text
M_cut = S H P C^{-1} = M C^{-1}.                 (1)
```

No condition on the suffix is needed. This is an equality of matrices,
not merely an equality of their rank bills, traces, or diagonal entries.

A sufficient condition independent of `chi` is literal first touch: every
earlier operation is the identity on the cut array, neither reading from
it nor writing to it. In the eight-stream projection, each earlier matrix
then has identity row `s` and identity column `s`, and therefore commutes
with every diagonal `E_s(z)`. Their product `P` commutes with `C(chi)` for
every one of the `2^73` Fourier labels. Under that structurally verified
premise, (1) holds for every label without enumerating the labels.

Literal first touch is sufficient, rather than necessary. Earlier
diagonal phases can also commute with `C`. This observation does not
license silently weakening the predecessor's literal-head or no-hosting
contract; an alternative prefix-commutation contract would need its own
explicit binding. A numerical phase equal to one at a sampled label is
not a structural identity event.

For several cuts, all the input-side correction matrices are diagonal
and commute. Apply (1) successively, or commute each removed phase to the
input. A verified first-touch premise for every cut gives

```text
M_all_cuts(chi) = M_original(chi) D(chi)^{-1},
D(chi) = product_{cut heads h} C_{s_h,A_h}(chi).  (2)
```

The identity also holds on a direct sum of the independently labelled
`(owner_replica, port)` projections, with each phase placed on its own
physical coordinate. This extension requires that the completed-call
contract actually makes those projections independent. It is not an
assumption that native helper internals never mix their temporary roles.

## 3. Why the side and the read guard matter

For a concrete side check, embed these two-dimensional matrices into two
of the eight streams:

```text
C = [[i,0],[0,1]],       G = [[1,0],[1,1]].
```

If the head `C` occurs first and the shear `G` later, then

```text
M = G C,       M_cut = G = M C^{-1},
C^{-1} M = [[1,0],[i,1]] != G.
```

Output-side left multiplication is therefore not the general relation.
It may coincide with right multiplication for a particular baseline
matrix; such a coincidence does not prove the side convention.

If the shear occurs before `C`, deleting `C` still leaves `G`, but

```text
M C^{-1} = C G C^{-1} = [[1,0],[-i,1]] != G.
```

Here `G` reads the first stream even though it does not write that stream.
Counting only writes would wrongly call the later phase a first touch.
At a label where the removed phase is one, this error is invisible.
Thus both a chronology guard and an active wrong-cut control matter.

## 4. Obligations for the unchanged T74 input binding

The lemma does not itself assert which literal bins satisfy its premise.
To apply it to the reported half cut, the binding must establish:

1. **Exact inputs.** Bind the unchanged PR #2979 `FILL`, `ORDER`,
   `DISPATCH`, `PROVIDERS`, `PLAN`, `TEMPLATE`, and phase recipe. Resolve
   each hosted width through the provider at its actual call. Derive the
   child's physical pair/side and its ordered axes from those inputs.
2. **Literal projection.** For every tested or certified
   `(owner_replica, port)`, retain every hosted occurrence affecting that
   array, in actual global call order, including calls issued by other
   replicas. Execute the owner's local stage events at the corresponding
   points of that same order.
3. **Residual and cut.** Check slice bounds, disjoint occupied positions,
   and the exact complementary residual. A claimed rank-48 head must have
   that actual unhosted residual; a half cut must remove exactly its
   declared 24 axes. It changes neither another child nor a translation
   nor an event time.
4. **First touch.** Inspect every earlier event affecting the array.
   A nonzero bridge coefficient touches both its source and destination.
   A local mixing event touches both streams of its pair. Hosted phases
   and adapters must be accounted for under the actual completed-call
   contract; an empty span must be established from literal occupancy,
   not from a zero phase at one character. No earlier nonidentity use may
   be discarded merely because the residual rank is unchanged.
5. **Correct target.** Compare the cut replay with
   `M_original D^{-1}`, changing the input columns indicated by (2).
   Do not demand that cutting leaves the original full-job matrix
   unchanged, and do not replace the relation by an output-row correction.
6. **Class coverage.** Name the exact child, replica, and port keys whose
   guards are checked. A sample from one replica/port is not every such
   key. To promote representatives to all keys, either check each literal
   key or prove the required exact symmetry of axes, schedule, hosted
   occurrences, and stream incidence. An equal rank histogram alone is
   not that symmetry.

The predecessor's instance file reports 16,086 heads, in children 8 and
10. That is a retained claim about its own lowering/network; this lemma
does not assume it has already been established in the eight-stream
model. Likewise the retained PR #3187 `source.py` loader reconstructs a
particular PR3148/T740 lift and restricts its projection to owner zero and
port zero. It cannot be used unchanged as a PR #2979 T74 loader. The
eight-stream algebra may be reused while its actual inputs and projection
are separately rebound.

If the actual literal-first-touch guards are certified for a named set
of keys, the all-character conclusion (2) applies to exactly that set in
the specified cover-identity model. Replaying a finite list of characters
is additional exact regression evidence only for those labels. Passing
those samples, by itself, proves neither the guard nor (2) at untested
labels. Conversely, one failed label disproves the claimed equality for
that literal cut and key.

## Scope and credit

Jacob Sussman/PR #4268 proposed the mixed-target recursion and half/full
cuts. Marius-Paul Dumitrean/PR #2979 supplied the unchanged words and T74
allocation, with the predecessor lineage recorded in its retained notices
and credits. Nick Petalas/PR #3187 supplied the exact eight-stream algebra
and physical-stream obstruction, crediting Gareth Davidson/PR #1387 and
Rohan Arun's earlier objection. Those contributions remain distinct.
Commuting a diagonal factor through an untouched prefix is elementary
linear algebra; the useful contribution here is its precise side, guards,
and source-binding boundary for this proposed cut.

This is a scoped written argument, prepared with substantial OpenAI Codex
assistance and separate AI assessment. It claims no independent human or
formal-kernel acceptance. It supplies no new DFT rate, native-frame or
helper-internal proof, physical routing/restoration/precision cost, mixed
recursion admission, integer-multiplication supplier, or new kappa.
