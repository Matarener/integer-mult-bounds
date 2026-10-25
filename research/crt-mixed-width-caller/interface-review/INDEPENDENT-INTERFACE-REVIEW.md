# Independent mixed-width caller interface review

Reviewer: independent OpenAI Codex review, not human or formal-kernel review.
Source: Cinna Davis's retained PR4100 `CRT.md` sections 1–2 and
`check_batched_crt.py` at canonical main
`12fa8c5c844be21bfefb38a19503fbd867a11244`.
This review concerns exact semantic composition and quantified interfaces.
There is no tape, bit-cost, E-evaluator, placement, precision or multiplication
theorem claim. Existing omission/allocator/inverse work in PR4169 and PR4174
is predecessor work, not a new mechanism supplied by this note.

## Quantified domain

Let `d=2^m` for an integer `m>=0`. For a positive integer `ell`, each axis has
an explicitly declared integer width `h_i in {ell-1,ell}`, `h_i>=1`. Let
integer moduli satisfy `2<=s_i<2^(h_i)` and pairwise coprimality. These
conditions themselves exclude any purported width-one axis with modulus at
least two. The complete semantic domain is the padded Cartesian cube
`X=product_i [0,2^(h_i))`, not only the valid rectangle
`V=product_i [0,s_i)` and not only minimally encoded axes. For `d=1` there
are no tree levels and the caller is identity. Empty admitted parameter
families make no extra existence claim.

At a balanced-tree level, each consecutive node splits into equal axis
halves `A,B`. Only axes in `B` are targets. Reconstruct `k_A` from its
current locally scaled child CRT coordinates when all of `A` is valid;
otherwise use offset zero. For target `i` in `B`, use

```
c_i = k_A * (S_A * P_(B,i))^(-1) mod s_i.
```

The inverse exists because the moduli are pairwise coprime. Crucially,
every coordinate in every left half `A` remains unchanged for the entire
level: level nodes are disjoint, and no coordinate in a left half is a
target of another node at that level. Thus its validity flag, reconstructed
integer and every offset are constant through all rows of that level.

## Declared-width compilation and idle rows

Compile each target permutation on its *declared* domain `2^(h_i)`:

```
rho_i(x) = (x+c_i) mod s_i for x<s_i; x otherwise.
```

The retained `benes` construction returns `2h_i-1` rows. Its local target
bit at row `r` is `r` for `r<h_i`, and `2h_i-2-r` otherwise. A common
`2ell-1`-row caller can use those local rows in order followed by identity
rows. For `r>=2h_i-1`, the local descriptor is idle, has no target bit and
has no table lookup. Appending zero controls to an existing bit is another
semantic identity, but inventing an extra coordinate or querying beyond the
axis's declared width is not an admissible implementation of idle padding.
Other explicit order-preserving placements of identity rows are possible;
the proof and inverse must use the same declared decoder.

Each nonidle table is equal on the two values of its active-bit pair.
Its control depends only on its own other axis bits and the fixed left-half
controls. It is therefore independent of *every* simultaneously active
bit: its own by the Beneš invariant, other target axes' bits because they
are absent from its arguments. Distinct-axis operations commute in that
row. Idle descriptors are identities. This supplies the semantic omission
premise; it does not allocate physical borrowed fields or prove a machine
implementation of those controls.

The source helper `balanced(...,compiled=True)` chooses
`(s_i-1).bit_length()` instead of the declared `h_i`. It is not a valid
reference API for all wider padded target states. The exact counterexample
in `COUNTEREXAMPLES.json` uses moduli `(3,2)`, declared widths `(2,2)` and
state `(1,2)`: direct source semantics return `(1,2)`, while the compiled
helper indexes outside a two-wire table. Use the direct source semantics
or an explicitly declared-width adaptation for the whole padded caller.

## Intermediate validity and inverse order

Each *complete* `rho_i` is a permutation, fixes every invalid target value
and preserves target validity. None of this says that every internal switch
preserves validity. The retained four-wire compiler with `s=3,c=1` sends
valid `x=1` through `1,1,3,2`. Disabling a micro-switch whenever its current
target is invalid strands this trajectory at 3 and destroys the endpoint;
there is also a collision with the originally invalid target 3. The
left-half validity flag may gate preparation because those controls are
constant through the level. Current target validity must not gate an
individual compiled switch.

For exact inverse transcripts, reverse the tree levels, reverse the common
padded row order at each level, and apply the same table-controlled bit
flips. Every row map is an involution because its controls omit all active
bits; its simultaneous target operations commute. At inverse entry to a
level, all later forward levels have already been undone, so the left-half
controls agree with those of the forward level. Within the level they stay
unchanged. This proves exact inverse composition on *all* of `X`.
Compiling a negative modular offset yields the same complete inverse target
permutation, but that alone does not justify reversing a particular row
transcript or reusing different row tables.

## Complete endpoint and valid restriction

Inductively, a valid child group has locally scaled CRT coordinates
`Phi_A(a),Phi_B(a)`. Let `k_G=k_A+S_A*k_B`. For `i in B`, adding the offset
changes its coordinate to

```
k_B/P_(B,i) + k_A/(S_A*P_(B,i)) = k_G/P_(G,i) mod s_i.
```

For `i in A`, `k_G=k_A mod s_i`, so its coordinate already has the desired
value. This establishes the valid root restriction. On the complete padded
cube, each conditional level is a composition of target permutations
conditioned on unchanged left-half coordinates, hence a permutation.
It preserves the globally valid rectangle at complete-level boundaries and
therefore permutes its complement too. Dirty invalid states need not be
pointwise fixed; they are carried bijectively. The inverse proof applies
equally to them. Endpoint/validity conclusions are not asserted at internal
rows.

No material obstruction is visible to this semantic interface. A submitted
implementation still needs an explicit local-row/idle decoder, declared-width
compilation, complete padded-state reference and the exact inverse order.
Finite exhaustive checks corroborate those choices but do not prove the
all-size theorem by their counts.

## Final submitted caller review

I read the submitted `research/crt-mixed-width-caller/{verify.py,PROOF.md,
README.md,RESULT.json,SOURCE-PINS.json}`. This is a read-only proof/interface
review; I did not author or change its implementation and do not represent
its stored finite receipt as an independently implemented oracle.

The actual submitted decoder chooses a center-idle embedding, rather than
the simpler trailing-idle example above: short axes idle at global rows
`ell-1,ell`, use local `g` before those rows and local `g-2` afterwards.
For `g<=ell-2`, both active schedules use bit `g`. For `g>=ell+1`, the
short schedule uses `2(ell-1)-2-(g-2)=2ell-2-g`, exactly the long schedule's
bit. The `ell=2` post-idle range is empty. Removing the two idles therefore
recovers every local row in order, for every admitted ell, with no phantom
coordinate. The implementation retains the supplied global ell even when
all axes are short; it does not normalize ell to the maximum declared width.

Each network is compiled on `2^h_i` entries. The row decoder returns its
idle descriptor before any network access. Each nonidle table is queried at
the current target-axis value. Only unchanged left-half offsets are frozen
at level entry. Increasing-depth and decreasing-depth schedules match the
claimed forward/inverse constructions. Both full padded-domain comparison
to source uncompiled arithmetic and the additional source compiled oracle
are used within their explicitly correct width domains.

The validity counterexample is bound to a genuine admitted CRT caller:
moduli `(7,3)`, widths `(3,2)`, global ell 3, input `(1,1)`, right-target
offset 1. The short network visits invalid target 3 between valid endpoints;
incorrect target-validity gating returns `(1,3)` instead of `(1,2)`.
The source-helper wider-width witness and globally-invalid-but-moving
witness are also explicitly scoped as incorrect inference/API coverage
boundaries, not defects in the predecessor's mathematical construction.

The submitted all-size proof correctly treats left controls as constant
through a level, preserves each axis's own row order, uses disjoint-axis
commutation to identify the complete level endpoint, and reverses both
levels and padded global rows for exact inversion. Global invalid tuples
are permuted; pointwise fixation is not asserted. Source Phi and predecessor
omission/allocator/inverse credit are retained. No tape/E or physical compact
execution claim is introduced.

No material proof, declared-width, idle-row, inverse-order or padding-interface
defect remains in the reviewed submitted candidate. The accompanying report
pins exactly the files read. The finite Python receipt remains corroboration
of the separately quantified written result, and no human review or formal
kernel acceptance is claimed.
