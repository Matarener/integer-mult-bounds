# Complete selected-C leaf action bound

Chris R / Clear1nsight, with OpenAI Codex assistance. Apache-2.0. The source
operations are Jose Manuel's retained complex controller (#3385), physical
Gaussian leaf, encoded Count arithmetic and native source closure. #4172's
successful coefficient opacity and phased history relation are inherited.
No controller, arithmetic implementation or physical reset is added here.

## Boundary and nonempty source domain

The boundary is original `Machine.run(payload, descriptors)` entry through its
successful root return, with output still resident and borrowed payload and
Count heads restored. Subsequent caller consumption belongs to the shell bill.
The named marker class is steady; a fresh nonempty original backend epoch adds
703 writes once, as proved in #4172. This is not multiplied by calls.

This lemma applies to complete admitted descriptor packets satisfying the actual
terminal predicate `w < 73 OR w^1000 < d`. The original selected `node` first
tests width against its dimension and, if needed, evaluates its capped-power
cutoff. Both branches reach `apply_leaf` before stock allocation or the
recursive group loop. **There are no descendants, monomial
calls, Binary calls or Ordinary calls in this branch.** A fitted/fallback
fixture does not price it and is not invoked as evidence.

This is not a claim that every small width can arise from RootLayer. In
particular the independently checked actual fast-entry condition excludes
parent columns 1 through 4. The integrated checker supplies an exact nonempty
fast RootPlan family with parent columns 5 through 44 and child widths lambda
and 8 lambda. Source
row stock, root grid, physical reserve and successful numerical inputs remain
admission requirements. Reduced physical calibrations below are not that huge
root's payload execution.

Let `R=prefixes*rows`,

    b = front + 3 compact_bits + before + w spacing + after + back,
    Gs = R coefficients 2^b,
    v = 2 H_b Gs,
    L = 16 + b + sum(max(1, bit_length(descriptor)))

where the sum includes all fourteen input descriptors, including root width,
physical `H_b`, coefficient count and unused row stock. The letter `Gs` here
counts Gaussian coefficients and is unrelated to the address guard `G`.
The active rank changes `w` and `after` together; it does not reduce `b` or `v`.
No logical coarse width substitutes for H_b. All quantities are positive where
required by the actual source. Residue is less than spacing.

## Exact amortized countdown, including ripple and terminal transition

For a positive canonical countdown starting at n, put
`z=n-popcount(n)` and `j=bit_length(n)-1`. All n calls to the actual
`stream.Counter.decrement` cost exactly

    reads  = 2z + 5n + 1,
    writes =  z +  n + 2j + 3,
    moves  = 2z + 4n + 2j + 4.

The sum of trailing-zero lengths over k=1..n is z. A non-power of two has
`(2 nu2(k)+5, nu2(k)+1, 2 nu2(k)+4)` actions. Powers of two greater than one
add `(0,2,2)` for shrinking the high delimiter; the final k=1 transition adds
`(1,3,4)`. The final rewind is included, so no head motion is hidden in the
amortization. Initialization copies the canonical source, normalizes the new
counter and restores the borrowed source; final close erases the canonical
zero plus its delimiter. Both together are at most `64(bit_length(n)+2)` in
each component. Zero initialization/close obey the same bound with bit length
one and no decrement. Thus a full n-step countdown is bounded by
`12n + 64(bit_length(n)+2)` separately in reads, writes and moves.

`check_countdowns` compares the exact formula against actual source execution
at zero, powers of two, their neighbors and multi-bit integers. This is a
calibration and rejection control; the trailing-zero sum supplies the
quantified proof. Charging log(n) at every decrement would lose the important
amortization and give a misleading production comparison.

## Hierarchical source upper bound

The following deliberately generous, componentwise bound is sufficient for
the comparison; it is not an exact fitted or whole-recursive-C tariff:

    E_w(g) <= 2^32 (w+1) [v + (Gs+1)L^4].                  (1)

Every coefficient-payload bit loop in the leaf is covered. The audit below
bounds the retained source's syntactic loops, not elapsed Python time. It does
not price a host algorithm substituted for those loops.

1. **Encoded setup.** All live Count values in this leaf are input values,
   sums of fixed-schema address widths, powers of two of those widths, products
   for record/row/packet extents, axis suffix/pair counts, or loop positions.
   Their canonical binary bodies have fewer than `4L` digits, including
   intermediate products. The width<73 branch bypasses `fixed_power`; the second terminal branch pays
   the fifteen capped products explained below, whose transient values are
   at most d². A linear Count operation (literal/copy/normalize,
   increment, small multiply, zero, compare, subtract or close) has at most
   256L actions per component by counting at most a fixed number of full
   scans over those bodies. General product scans at most 4L digits and makes
   at most two such operations per digit. `power_two` makes at most b
   `multiply_small(2)` iterations, with the exact countdown just proved.
   The conservative common envelope is 4096L² per product/power operation.
   There is no variable-exponent bisection or general native division here.

2. **Coefficient pairs.** `signed_linear.c_pair` makes four width-H_b opaque
   copies, four width-H_b `linear_word` calls, and buffer clear/rewinds. Each
   linear word reads and moves four component ports and appends exactly H_b
   result bits (first-bit suppression is offset by the sign-extension append).
   Carries change bits but not the action schedule on successful inputs.
   Complete width countdowns are amortized as above. Component copy, append,
   clear and rewind traffic is linear in H_b. Per pair there are fewer than
   1024 payload actions per component per H_b plus fewer than 1024 linear
   Count/Counter setup operations; `1024 H_b + 2^20 L²` is an upper envelope.
   This includes loop tests, append-blank checks, right-end reads and rewinds.

3. **One axis.** `c_axis` processes exactly Gs/2 coefficient pairs. It performs
   two suffix input copies and two suffix output copies per prefix, totaling
   2v bits of opaque copying; input/output/intermediate erasure and rewind
   lengths total at most a fixed multiple of v. The outer row loop has R
   iterations and the nested prefix loop has `R*2^position` iterations, each
   at most Gs (coefficients>=1 and position<b). All prefix/row/pair countdowns
   are full countdowns, so their total variable decrement traffic is linear
   in Gs and v, not Gs log Gs. Their constructor/close work is bounded by L
   per activation. Fixed descriptor construction and cleanup makes fewer
   than 4096 elementary/setup operations for this axis. Summing the preceding
   bounds gives the simpler envelope `2^28[v+(Gs+1)L^4]` for a whole axis.
   This loosens both the lower polynomial degree and coefficients deliberately.

4. **Leaf and complete controller.** `run_leaf` makes w axis calls; its
   pre/post copies add O(v) payload actions. Layout has eight fixed fields;
   constructing all radices, records and row bits and closing them uses fewer
   than 4096 of the elementary/setup operations above. It rearms/closes the
   fixed 256-role leaf pool. `Machine.run/node/apply_leaf/return_node` includes
   payload copy, all fourteen descriptor copies, positivity/width checks,
   shape, complete-extent skip, leaf argument creation, returned payload
   transfer, all parked-role clearing and borrowed rewinds. There are fewer
   than 4096 fixed role/setup operations, besides linear complete-packet
   traffic and the one leaf call. This includes the original selected
   controller's 712 packet/private roles, its descriptors, capsule and
   markers; closed native inventories are tested but never executed. Applying
   the envelopes above and rounding upward gives (1), including w=0.

The large margin in 2^32 is intentional. The proof needs the structural bounds
in the table; passing a few calibrations does not establish that coefficient.
No cancelled descendant or unpaid native tariff is hidden in (1), because the
source branch has no descendants/native invocation. This lemma rejects failure of both terminal tests; width>=73 alone is insufficient
to classify a call as nonterminal.

For integer arithmetic the implementation rounds `L^4/(2H_b)` upward to give
an affine bound in v:

    A = 2^32 (w+1) [1 + ceil(L^4/(2H_b))],
    D = 2^32 (w+1)L^4,
    E_w <= A v + D.

It can return this exact compact representation without constructing 2^b.
For the particularly useful domain `H_b >= L^4`, `Gs>=1` implies
`(Gs+1)L^4 <= v`, so a still simpler bound is

    E_w <= 2^33 (w+1)v                  in each R/W/M component,
    sum E_w <= 3*2^33 (w+1)v.                              (2)

This is an upper bound on removed work and can therefore be subtracted safely
in a lower bound for candidate-minus-baseline cost. Subtracting a leaf lower
bound would have the wrong direction. Fresh-marker potential is explicit and
is globally matched once in B/D by #4172; it is not a per-call refund.

## Finite evidence and limitations

The executable interface accepts every descriptor, the original selected
binding and external root flag, and a named marker class. Its cache key keeps
all of them, not just width/rank. Geometry mutations that move active axes into
spectators preserve packet volume but change the axis schedule; they cannot
reuse an arbitrary rank-only exact price. The returned object is an upper
certificate, so a coarse bound may intentionally be equal for different keys.

Seven complete reduced C calibrations use actual original selected-controller
leaf execution, nonconstant exact-grid data, encoded descriptors, borrowed
bytes/heads and repeated completed returns. An additional complete dimension-two
fixture uses the same actual controller and an authenticated reduced binding to
reach the capped-power terminal branch. It is identified separately. They independently compute the
Gaussian endpoint. They exercise the zero/leaf and reduced cutoff branches and cold/warm markers;
they do not exercise nonleaf C or Ordinary. The countdown calibration is
exact; the complete-C calibration checks the stated upper bound and records
actual measured R/W/M. Source authentication occurs before imports/execution.

## Open next question

For the actual terminal-child band this closes the removed rank-eight C-body upper term,
with no recursive supplier underneath it. It does not close removed f>1
monomial wrapper/native prices; those require matched source operation
cancellation or a complete native upper bound. Failure of both terminal tests requires a genuine completed C recurrence and
is explicitly outside this evaluator. This leaf
lemma alone does not meet the publication significance gate or prove QQ16's
complete sign.

## The second terminal branch and the installed terminal-child band

The dimension cutoff is sufficient but not necessary. The actual
source next computes `fixed_power(width,1000,root_width)` and returns a leaf
whenever `width^1000 < root_width`. Consequently a width of 80 or 144 is not
a certificate of a recursive C call. At the actual p=2^8500 root witness these
widths are still terminal. The admitted root's global d must remain in the
cost key.

Equations (1) and (2) use the exact terminal predicate

    w < 73 OR w^1000 < d.

The additional source work is paid as follows. Binary exponentiation for the
fixed integer 1000 has six multiply-result sites and nine squaring sites.
`encoded.product(...,cap)` tests its operands and either returns a copied cap
or computes a product then caps it. Operands remain at most d and the transient
uncapped product is at most d². Their Count bodies therefore remain below 4L.
Fifteen general products plus the associated comparisons, copies and cleanup
remain below the 4096 fixed setup-operation allowance in step 4 above. The
4096L² primitive envelope and the conservative 2^32 whole-leaf coefficient
therefore continue to hold. This supplies the additional paid branch; the cutoff test is not free.

For parent columns lambda, the source-compatible terminal-child band includes

    ((8 lambda)<73 OR (8 lambda)^1000<d) AND d<=(73 lambda)^1000,

along with the separate actual RootPlan fast-entry, row stock, grid and width
conditions. Both rank-one and rank-eight children are terminal throughout this
band. In particular the independently checked p=2^8500 family admits lambda
5 through 44. The first possible transition there is not lambda10: it occurs
when the global-power cutoff fails. A proposed one-level columns-one recursive
price without this admission check is rejected. The general upper certificate
now tests the exact predicate; the reserve-dominated corollary can receive d
explicitly for the same purpose.

The full width-73 cutoff kernel at d=73^1000+1 was executed once: it
returned the terminal decision with (230491720, 51790603, 174593792) source
actions. The four-case calibration took 209.934 seconds including the smaller
cases. It executed encoded Count arithmetic only, not a 2^73 payload. Fresh
registered checks use both sides of the width-two power boundary and a small
width-73 saturating cap; `check(include_large_cutoff=True)` explicitly repeats
the larger calibration. The retained large-kernel receipt is once-executed
evidence, not a claim that every normal/optimised/export replay reran it.
