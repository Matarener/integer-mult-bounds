# Deferred two-helper sum: exact word and fixed-neighborhood obstruction

The deferred sum admits a legal literal word through the complete common
rank-four block. Its recursive frame profile and widths are unchanged, and
its full scalar-addition count increases by two. A sum chart retained to
cleanup has an exact arbitrary-input algebraic interpretation, but fails the
unchanged frame contract at the next pair of rank-six source updates. Two
written arguments explain the failure: all invertible scalar charts must pay
both rank-four visits, and an unchanged persistent chart mixing the two cells
cannot traverse the next incomparable source frames.

This is a scoped negative result for the indicated mechanism. It establishes
no improvement to a recursive moment or kappa.

## Pins, assumptions, and actual source sites

The inputs are the two complete `NEW-base` and `NEW-extra` PR4076 words frozen
under `../source4096/source4076/`, source PR4076 head
`9744f9df268590295a9872b1952c695a678192b9`. The containing PR4096 export is
`8d1e3b9399a2a7914f1ab538242cf2e6e6c4cd9f`. The package export manifest and
`witness.py` pin the actual bytes. Both providers have exactly the same source
sites considered below; the full-provider invoice is recalculated separately.

Write

```
x=608, y=609, z=610, t=612,
w=410, a=417, b=419, c=421,
E=span(76,45)=span(97,45),        dim E=2,
F=span(144,75,42,7),             dim F=4.
```

The entrance frames of x and y are E. Their only B reads before B948 are
B388 `121 += y/2` and B410 `137 -= x/2`, both at E. There is no A, cut,
restore, or native operation on x or y. Native operators 33--36, on w,a,b,c
respectively, occur immediately before B948 and map their source frames to
F. The proposed entry cut is **after those four native operations and before
B948**, where x and y still have frame E. No native operation occurs strictly
between B948 and B962.

The complete source B948:962 block is

```
z -= x; x -= w; z -= y; y -= w; z += w;
x += a; y -= a; t -= a;
x += b; z -= b; t -= b;
y -= c; z += c; t -= c.
```

All fourteen gates have frame F. The next two gates are

```
B962: x += 278,   U=span(266,138,75,42,26,7), dim U=6;
B963: y += 276,   V=span(272,144,72,41,4,3),  dim V=6.
```

Later pair sites, all retained in the legal word, are B1496--1498
`x+=421; 421-=x/2; 137-=x/2` and B1500--1502
`y+=419; 419-=y/2; 114-=y/2`. `WITNESS.json` records every actual pair site
with its complete frame, rather than treating the later x read as B410 again.

All current-state coordinates at the entry cut are arbitrary and independent.
This is legitimate even though the factory source registers contain evolved
data: the prefix consists of invertible gates. Equivalently, use independent
formal symbols for their current values. The full source has 632 independent
live inputs and 91 independent dirty buffer inputs. No helper is assumed clean.
Rational coefficients are exact, and the 72 native operators remain independent
noncommuting invertible generators. No native operator is moved across a source
update.

## A reconstructible legal combined word

Enter the chart `X=x+y, Y=y` with `x += y` at E, and keep it through the entire
F block. Replace the fourteen source gates above by these thirteen F gates,
where physical registers 608 and 609 now hold X and Y:

```
z -= X;
X -= 2*w; Y -= w; z += w;
Y -= a; t -= a;
X += b; z -= b; t -= b;
X -= c; Y -= c; z += c; t -= c.
```

Finally execute `X -= Y` at F, immediately before the inherited B962. This
restores the original physical meanings of x and y. In the B list replace
`B[948:962]` by the entry, thirteen gates, and exit (15 gates total). Keep
native operations at old B948 before the new entry; shift every native
position at least 962 by one. There are no intervening native positions to
interpret. Preserve every other scalar gate and field, and regenerate literal
cleanup from the complete changed non-target word using the source exclusions
and restored-buffer renaming.

For arbitrary initial `(x,y,z,t,w,a,b,c)`, both old and changed blocks give

```
x' = x-w+a+b,
y' = y-w-a-c,
z' = z-x-y+w-b+c,
t' = t-a-b-c,
(w',a',b',c') = (w,a,b,c).
```

This is an eight-input matrix identity; it includes the dirt carried by the
receivers z and t. Consequently all complete-word output rows and the cleanup
boundary agree, including all independent inputs outside this neighborhood.
The inverse is obtained by reversing the full changed non-target word and
negating each addition. In particular, it includes the inverse of both the
entry and the deferred exit; omitting either is not justified by the common
sum. Local reversal composes to the identity on all eight coordinates.

The two early target releases and all later target reads are retained in their
original coordinates, because the chart ends before B962. No target-dirt
compensation change is required. The result is not obtained by reusing the
one-channel residual from PR4096; its local equality is derived directly.

## Exact pullbacks for a chart kept to cleanup

Let `S=I+e608 e609^T`. To retain this chart, replace each subsequent scalar
gate G by `S G S^-1`, preserving its chronological position relative to all
native operations. On the actual source suffix the rules are:

```
d += q*x  -> d += q*X; d -= q*Y             (d outside pair),
d += q*y  -> d += q*Y,
x += q*u  -> X += q*u                      (u outside pair),
y += q*u  -> X += q*u; Y += q*u.
```

Unrelated scales and additions are unchanged. There is no pair scale or
pair native operation in these providers. The target read B1498, for example,
becomes `137 -= X/2; 137 += Y/2`; retaining only its first term is an actual
dirty-input error. The source read B1497 similarly needs both terms, so the
current 421 value must also be propagated through its later consumers.

If P is the full source prefix through the cleanup boundary, the exact
conjugated construction has `P_new=S P`. Its target rows equal those of P;
its two pair rows carry the chart. The regenerated cleanup is the old cleanup
composed with `S^-1` at its input, with the source's private-buffer renaming.
The pair is outside the restored-helper set, so that renaming commutes with S.
Thus the complete endpoint map agrees on arbitrary live and dirty buffer
values. This statement is an algebraic identity in the free operator ring;
it is not a legal-frame or native-phase certificate.

At a **current-coordinate observation cut** the correct pullback of an old
row C is `C S^-1`, since old values equal `S^-1` times chart values. This does
not conflict with the raw-entrance rewrite rule `C_new=C S` when
`A_new=A_old S`: that is a different interface. Here the entrance and wrappers
are unchanged, and `P_new=S P` is a left action on boundary coordinates.

## Why a two-cell chart cannot save the rank-four visit

Use the two source columns of the exact F-block endpoint map:

```
v_w=(-1,-1)^T,     v_a=(1,-1)^T,
det[v_w v_a]=2.
```

Fix any `T in GL2(Q)` (or an invertible dyadic chart with its inverse) on the
two physical cells, while retaining the external source/native neighborhood
and requiring its source interactions at F. Their contributions become
`T v_w` and `T v_a`. If a chart row b avoided both source interactions, then

```
b v_w=0 and b v_a=0,
```

which force `b=0`. An invertible chart has no zero row. Therefore each physical
chart cell must be touched at F. Starting from E, both must pay their E-to-F
raise. A row aligned with the difference can cancel the w source, and the sum
row can cancel the a source, but no nonzero row cancels both. This is an
all-GL2 proof, not a finite chart search.

The same conclusion holds for temporal scalar pair realizations under this
precise restriction: transitions use invertible pair-only scalar gates; the
only permitted inflow of the source410/source417 dependence into the pair is
through the fixed direct source interactions at **exactly F**; and, immediately
after B961, the physical pair is an invertible scalar chart T of the original
output pair, with no external-register offset. No additional storage, source
requery, native operation, source-frame change, or transfer of the pair update
to an external register is allowed. The endpoint influence matrix must then be
`T [v_w v_a]`, which has rank two.

Suppose one physical cell never visited exactly F. Before any inflow at F,
both cells have zero influence from the two independent current sources. Only
the other cell can receive such inflow directly, so the pair influence rank
is at most one until an F-bearing row first mixes into the avoiding cell. At
that first mix the common frame G contains F. If `G=F`, the purported avoiding
cell has visited F. If `G` strictly contains F, both cells now have a frame
strictly larger than F, so monotonicity prevents either from participating in
any later exact-F source interaction. Pair-only invertible operations cannot
raise the influence rank from one to two after this event. If the mix never
occurs, the rank likewise stays at most one. All cases contradict the required
rank-two endpoint. This also excludes an escape that jumps the avoiding cell
directly to a strict superframe rather than leaving it below F.

For `H_r=r^p`, `0<p<1`, any monotone E2-to-F4 path costs at least H2:
its positive dimension increments sum to two and subadditivity gives
`sum_j (d_j)^p >= 2^p`. Consequently the pair-entry subtotal is at least
`2 H2`, attained by the inherited two direct raises. This is a sharp bound
only on this subtotal in the stated temporal model, not an optimum for the
complete supplier profile. Any temporary external encoding or changed
receiver-to-pair recovery is outside this two-cell model.

In particular, the proposed signed cost change `H4-2 H2`, obtained by skipping one
intermediate rank-four visit on a rank-two to rank-six path, cannot arise from
this fixed F neighborhood. Pricing a different neighborhood remains open.

## Why a persistent mixed chart fails the next two source frames

For the actual next two source updates,

```
dim U=dim V=6,  dim(U intersect V)=5,  dim(U+V)=7;
26 belongs to U but not V; 3 belongs to V but not U.
```

The sources 278 and 276 are independent current coordinates. In a constant
chart T their required pair update columns are `T e1` and `T e2`. If row i
has both entries nonzero, physical chart cell i must interact with source 278
at U and source 276 at V. A monotone chronological frame cannot visit U and
then V because neither contains the other. Therefore every row of a legal
unchanged-label persistent scalar chart has at most one nonzero entry.
Invertibility then forces T to be a scaled permutation. No sum row is possible.

For S itself, B962 becomes `X += 278` at U. B963 then requires
`X += 276; Y += 276` at V. The first of those additions fails U containment
in V. `witness.py` constructs the literal conjugated suffix and confirms that
this is its first frame-accounting failure in both providers. The rank-four
necessity already rules out the intended omitted-visit saving; this rank-six
failure separately prevents declaring the constant sum-to-cleanup word legal.

This persistent-chart argument fixes the actual direct source interactions
and their frames. It does not prohibit a temporal unmix before B962, a new
third cell, a source-partner recovery, source-frame widening, retiming outside
the fixed neighborhood, or a changed graph that stores source contributions
elsewhere. Each such change needs its own literal word and full bill. For
example, replacing U and V by their rank-seven join changes the external
source frames and can affect their later consumers; the join is a necessary
new cost to examine, not an established admissible construction.

## Complete paid comparison for the legal word

The source pair's positive dimension increments are, for each helper,
`2,2,1,1,1`: E2 to F4 to its inherited rank-six, rank-seven, rank-eight, and
full rank-nine frame. The legal delayed word has exactly these same ordered
increments. Every other register has the same ordered paid chain, including
native transports. Its full per-call invoice remains

```
2488 H1 + 714 H2 + 223 H3 + 102 H4 + 20 H5 + 8 H8.
```

The complete width inventory is still `5:28, 6:18, 7:56, 8:93, 9:213`.
Both pair helpers have width seven. No register, buffer, wrapper, native
operator, entrance/terminal frame, or recursive frame event is added. Fourteen
forward additions become fifteen; literal cleanup becomes `5228 -> 5229`.
The exact total scalar-addition delta is `+2`.

Thus the recursive-profile delta is zero at every common exponent, conditional
on a valid unchanged owner and source-window contract. Equal ordered frame
increments and widths are useful necessary evidence for that reuse; this
derivation does not replay the owner assignment or establish physical timing.
No paid recursive invoice is asserted for the frame-invalid persistent word.

## Reproduction, evidence level, and open premise

```
python3 research/deferred-helper-sum/design/witness.py \
  --out research/deferred-helper-sum/design/WITNESS.json
```

The script checks pinned inputs, the complete source block, the exact local
matrix, reverse-inverse cleanup locally, the full frozen frame invoice and
ordered paid chains for both providers, and the actual first containment
failure of literal S conjugation. It rejects a wrong unmix sign and omission
of the required y-source410 update. The primary package checker separately
owns complete 723-column arbitrary-dirty and noncommuting-operator replay;
the small design script does not claim to duplicate that check. The GL2 and
temporal arguments are written algebraic proofs from checked finite source
data, with no formal-kernel or independent human proof claim.

The next changed premise would need to remove or relocate one of the two
independent F source directions, or admit extra recovery/storage with a
fully paid frame/native/cleanup/owner cost below the missing-visit benefit.
Changing the scalar coordinates of this same pair does not do that. Native
global phases, source-window/owner reuse, physical hosting, precision/tape,
all-size source existence, outer admission, and a kappa implication remain
unresolved for a changed supplier.

## Separate source credit

Rohan Arun's PR4076, with Anthropic Claude assistance, supplies the two NEW
providers, the staged-entry construction and owner lineage. PR4096 supplies
the preceding immediate sum/unmix experiment, exact shared-610 question and
its zero recursive-profile comparison. Its source mechanism is not counted
as a new saving here. Dugongue's PR3945, Ross Richardson's PR3605, and Sagar
Thakrar's PR3687 (retaining Arham Tahir's audit credit) supply the inherited
word, cleanup and frame-accounting mechanisms. Full notices and Apache-2.0
attribution remain in the frozen source.

The new contribution is the exact thirteen-gate chart block, its legal
delayed exit and complete unchanged invoice; the determinant-two proof for
all scalar pair charts and the stated temporal class; and the incomparable
rank-six witness excluding a persistent mixed chart with the fixed source
labels. The derivation and its small witness were produced with substantial
OpenAI Codex GPT-6.1 Sol assistance.
