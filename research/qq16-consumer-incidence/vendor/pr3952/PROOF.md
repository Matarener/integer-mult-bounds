# A projected F17 demand and its fixed-profile obstruction

This is an exact local interface result under the retained QQ16 common-label
cover contract. It is not a global controller, physical supplier, optimal
consumer, or new multiplication bound.

## 1. An actual demand, and the change of inputs

PR2512 (`851dd3486a2d0549b51e85978a65ccb4eec619c0`, ywz65) explicitly
ends with 96 consumer subtractions `Z_p -= X2_p`, ordinary ports p in U_ports,
returning logical `y1_U` in `F_U1`. Its proof defines this frame as the product
of C lines on coordinate axes 0 through 16, exactly PR2707's **F17**. The port
set U_ports and the 17-dimensional coordinate subspace are distinct objects.
The verifier authenticates the actual proof, full word and receipt, and checks
the literal 96-event consumer epilogue and its named output contract.

PR2512 reads 96 current X, 96 current Y and eight retained earlier T arrays.
Here the demand is supplied instead from **all 112 current Y arrays**, with no
X read or early T record. The extra sixteen selected current Y reads are
available under PR2707's 224-current-field contract; they are not available
merely by assuming PR2512's narrower interface. Every Y is borrowed, physically
in `F17 C_qp^-1`. The result needs 96 exclusively owned output arrays and sixteen
owned full-cover temporaries. Arbitrary owned dirt is erased by paid CLEARs.
No borrowed source is written. All sixteen temporaries and eight private scratch
arrays finish at zero in identity frame. There is no storage/hosting admission.

This pins a real published *local endpoint*, rather than inventing an ordinary
frame tariff. It does not establish that a complete selected outer controller
needs only these 96 values; other outputs may still be required there.

## 2. The projected logical operator

Use the actual ordered owner actions D_p in B1 and the pinned eight raw R rows.
Define the query and ordinary injection in the normalization used by PR2681:

    Q(Y)_k = sum_(p=0..111) R[k,p] D_p Y_p,
    (K_U q)_p = (1/4) sum_k R[k,p] D_p^-1 q_k, p in U_ports.

The retained complete B1 inverse first computes

    u_U = Y2_U - K_U Q(Y2).

Its future-logger reversal writes only selected A ports. Therefore it leaves
u_U unchanged, and

    y1_U = Y2_U - K_U Q(Y2).                       (1)

This also follows from the conserved B1 equations: `Q(Y2)` is the old selected
T query and `Y2_U = y1_U + K_U Q(Y2)`. The three conserved queries must not be
interchanged. The source proof gives the identity over the ordered cover
coefficient ring, so no owner matrices are silently commuted.

The checker compares every demanded routed row of the new word with (1) on
112 independent current Y symbols: 4,992 nonzero owner-labelled terms. It also
forms B1 from 224 *independent x1/y1 symbols*, without imposing an F0 relation,
and verifies that (1) recovers exactly those y1_U symbols. The latter replay
checks the actual selected-row coefficients and future logger, rather than
assuming a payload-constant or identity-owner special case.

## 3. A legal native word

`WORD.json` is regenerated deterministically from the complete authenticated
3,823-event PR2707 word. It has 1,410 events:

1. For every port, clear owned W_p in the Y hole frame, copy borrowed Y_p, and
   apply the positive rank-one line C_qp. W now has F17 and logical Y2.
2. Finish the source B1 alignment map on every W. With the actual source-derived
   affine translation, `M_p F17 = F17 D_p`. All query operands have common F17.
3. At each owner execute the entire private body: clear eight F_k, form all
   eight Q rows from the complete 112-port W bank, subtract `R[k,p] F_k/4` from
   ordinary W_p only, then clear all F_k in identity frame. Every query is
   formed before any W output is overwritten. Finish the owner body before
   visiting the next owner.
4. Undo the alignment map on the 96 ordinary W outputs. Clear the sixteen
   selected W temporaries directly in their existing frame, returning them
   to zero in identity frame. Clearing owned dirt is a paid primitive; no
   inverse map or native child is required to dispose of those owned values.

The temporary disposal is an explicit addition to the projected prefix. It
prevents an unreported dirty full-cover workspace liability. Every borrowed
Y retains its exact initial content and frame, and every X is untouched.

This projection is semantic: stage-2 map/line conjugations cancel on U because
that logger writes only A. A naive instruction-liveness pass would retain
conjugations on the demanded W fields. There is no reordering of native reads
or private bodies, and no claim of shortest code or a universal 112-child floor.

The phase checker uses complete modulo-four quadratic coefficients on all 73
coordinates at every ADD and output. A line contributes parity, and parity has
no terms above degree two modulo four. Thus these are full phase identities.
By Fourier spanning they hold on arbitrary payload arrays; owner pullback and
per-layer multiplication extend them to all owners and tensor layers under
the inherited cover contract. The source kernels are lowered using a basis
whose first column is q: one positive H1 child plus two inverse monomial
wrappers realizes C_q. All 112 bases and 57,344 basis columns are checked;
the other coordinates are spectators. This is not an execution on a huge
physical tape, or a proof of child precision/placement.

## 4. Complete local invoice and real removed work

| Charge | New demand word | Complete PR2707 decoder | Difference removed |
|---|---:|---:|---:|
| Positive rank-one children | 112 | 336 | 224 |
| Rank-eight children | 0 | 0 | 0 |
| Native monomial wrappers | 224 | 672 | 448 |
| Full-cover maps | 208 | 464 | 256 |
| Unit ADD macros | 560 | 1,808 | 1,248 |
| Quarter ADD macros | 384 | 896 | 512 |
| CLEAR macros | 144 | 312 | 168 |
| Real scalar primitive allowance | 9,376 | 25,840 | 16,464 |

The scalar allowance is `8*560 + 12*384 + 2*144`. Its 144 clears include 112
initial owned clears, sixteen private entry/exit clears and sixteen final
full-cover temporary clears. There are 96 owned outputs, sixteen full-cover
temporaries, eight owner-private scratch arrays, no early records and no X
reads. All 112 borrowed Y fields are restored by remaining read-only.

What disappears is the future logger reversal, the F0 inverse and unrelated
X1/selected-output recovery, including the two complete future-frame line
sweeps. The final output contract changes from all 224 original arrays to the
96 published y1_U demand. These are actual deleted operations; no unchanged
recursive child is assigned a lower tariff merely because its bit axis became
cheaper. The comparison is not a same-output full-decoder improvement.

Against PR2512's same logical *output* with different input/lifetime premises,
this replaces `192 H1 + 16 H8` with `112 H1`, keeps 208 cover maps, and raises
scalar allowance from 7,392 to 9,376. It removes early retention but needs the
sixteen additional current Y fields, sixteen owned temporaries and eight
private scratch arrays rather than one. No dominance or global memory saving
follows from comparing child rank mass alone.

## 5. What the changed budget proves, and what it does not

Recounting the literal source F0/B1 words gives per-call average

    n = {1:2428, 2:418, 3:432, 4:142, 5:82}.

For the **same conditional pair-rate budget used by PR3908/PR3946**, allocate
one demand word per two calls: add 56 H1 per call. Retaining the reported
selected-profile eight H8 charges gives

    n_full = {1:2484, 2:418, 3:432, 4:142, 5:82, 8:8}.

The eight H8 charges are the retained profile premise, not new children in
this demand word. This package does not prove that all eight remain needed
by an outer controller with a changed demand. That is an explicit next audit.
Likewise, this local pair amortization does not prove a full nine-call schedule
or the number of decoder invocations required globally.

Keep m=73, W=896/9, centre=64, and total mass T=72W+64=7232. The largest idle
rank allowed by the outer halving guard is R=51 (`2*51^2 < 73^2 < 2*52^2`).
For a>=0, price per rank-mass unit is `73^(a-1) r^(-a)`, nonincreasing in r.
Every legal idle placement is therefore at least as expensive as fractional
rank-51 idle work. If L=sum r*n_r and I=T-L, the favorable necessary screen is

    G(a) = [sum_r n_r (r/73)^(1-a)
            + (I/51) (51/73)^(1-a)] / W.

For n_full, L=5658 and I=1574. For the rank-eight-waived variant, L=5594 and
I=1638. All maps, wrappers, scalar operations, storage, movement, placement,
precision and numerical-error costs are set favorably to zero in this screen.
Thus failure already excludes the fixed profile; passing supplies no physical
construction. The actual complete local invoice above remains a liability.

At the selected `a=836330098538459/499163669901461541`, exact rational bounds are:

| Hypothesis | Enclosure for G |
|---|---|
| Eight reported H8 charges retained | [1.000023149708, 1.000023150305] |
| All eight H8 charges waived into rank-51 idle mass | [0.999995759681, 0.999995760274] |

The previous *rank-eight-waived* obstruction no longer applies to this changed
endpoint. Carrying it over would be wrong. The retained-eight profile still
fails even before physical overhead. With those eight charges fixed, at most
61 integer decoder H1 calls per pair pass this relaxation; 62 fail. Our word
has 112, so it needs at least 51 fewer pair calls, with no compensating charges,
merely to pass the optimistic integer screen. There is no theorem that 61 is
achievable, or that no different operator implementation can do better.

Waiving all eight charges permits at most 121 integer pair calls; our 112 leaves
only [0.000004239726, 0.000004240319] normalized allowance. Neither removing those
children nor paying the remaining physical liabilities is constructed here.
With 112 H1 fixed, retaining two H8 across the pair gives
[0.999999183434, 0.999999184028], while three gives
[1.000000895311, 1.000000895905]. Thus at least fourteen of the reported sixteen
H8 charges across two calls must disappear, with no other new costs, to pass
this integer relaxation. This is a repayment target, not a claim that a copy
can be removed or that fractional per-call assignment is physically legal.
The exact fixed-profile exclusion is the stopping result; it is not a global
QQ16 obstruction and does not authorize construction expansion.

The rational arithmetic is explicitly adapted from PR3946's independently
checked midpoint/trapezoid logarithm and exponential remainder implementation.
For convex 1/t on [1,y], midpoint sums are lower and trapezoid sums upper
bounds on log(y). Scale arguments into [1,2], round outwards to 2^-80, and use
the degree-six positive exponential sum with first omitted term divided by
`1-hi/(degree+2)` as geometric tail. Every final decision compares Fractions;
decimal formatting also rounds outward. Both sides of the 61/62 and 121/122
thresholds are verified, rather than deriving a decision from rounded output.

## 6. Bounded next question

Audit the *actual eight H8 centre-copy outputs* in the retained supplier and
whether their downstream uses survive this 96-output demand. First bind each
copy's source, destination, frame and last use in the selected archive and a
single real continuation. Either identify legal retirement and recompute the
coverage mass (centre 64 cannot simply be kept or deleted by assertion), or
prove all eight copies are still required under that continuation. This decides
whether the relaxed opening has a valid premise before optimizing physical
kernels. If retained, stop this recipe unless producer/consumer fusion deletes
at least 51 genuine H1 pair charges or another priced premise changes.

No new retained-query construction, further precision optimization or centre
change is implemented. Full controller demand, copy lifetimes, both supplier
caps, physical map/wrapper costs, numerical grids/dirty ranges, child placement
and all-depth cleanup remain open.
