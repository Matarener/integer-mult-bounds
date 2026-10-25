# A completed-word internal-error and dirty-state lemma

Chris R / Clear 1 nsight, with substantial OpenAI Codex assistance. Apache-2.0.

## Source and norm

The four exact gzip words are authenticated by FROZEN-SOURCES.json at PR3945
head 91f81d131252db704f945891da1ea54e29d46b8b. The two old words are PR3734
controls preserved in that snapshot. The literal order is: initial corrections,
precondition, compensation, A, cut, B with its native operations at recorded
cuts, restore, then private-buffer cleanup. All 632 live registers and 91
private buffers begin as independent inputs. Both prescribed orientations are
analyzed. Frames affect legality and the recursive invoice; they are not
silently charged as numerical operations here.

Each register is a vector in a common complex Hilbert space. Use the maximum
over registers of its Hilbert norm. Every formal native generator denotes an
isometry with the stated inverse; the dual generators are also isometries.
Products retain their order. This is a conditional semantic premise inherited
from native realization; no coordinate-infinity norm or new native phase proof
is substituted. Scalar coefficients are exact rationals. An operator row is
a finite sum of rational multiples of words in a free group. Adjacent inverse
letters cancel, identical words combine, and different generators never commute.
The sum of coefficient absolute values is consequently a certified row norm
bound for every realization satisfying the isometry premise. Additional actual
relations may improve the bound; no optimality is claimed.

## Exact full-state map, including dirty private buffers

The independently implemented forward rows and reverse columns agree for every
one of the 723 by 723 blocks as free-operator polynomials. In the primal
orientation the final map is exactly

    target[t] <- target[t] + source[t],    t=0,...,111,

with all sources, helpers and private buffers unchanged. The dual map is

    source[t] <- source[t] - target[t],    t=0,...,111,

with all remaining fields unchanged. In particular every private buffer has
identity self-map, no incoming live dependence and zero outgoing dependence
into live fields. Thus this exact formal-word statement holds for arbitrary
initial dirty buffers as well as dirty helpers. It strengthens the limited
zero-buffer endpoint predicate used in a credited predecessor audit; it does
not contradict PR3969's relative old/new arbitrary-dirty program identity.
The full endpoint norm is at most two. Positive controls use full independent
inputs, and explicit mutations inject a dirty buffer into a live output and
corrupt a buffer's return map.

## Prefix and suffix certificates

Let M_j be instruction j and L_k=M_k...M_1, with L_0=I. Each literal instruction
is invertible. Immediately after instruction j, permit one arbitrary additive
error eta_j in its destination block, with no independence or randomness
assumption. Errors may be coherent and depend on the actual state. Let E_t
inject a block into register t.

For a common bound ||eta_j||<=epsilon, the final error is

    sum_j (M_m...M_(j+1)) E_(t_j) eta_j.

A backward pass computes each suffix column exactly in the same free algebra,
then sums its absolute coefficients separately for each output. This yields
final uniform gains B=1335 (primal) and B=4841 (dual), including restored
helpers and private buffers. Destination errors are charged even after literal
identity SCALEs. Each macro correction/native warp is one fault site; its
physical internal operations are a separate obligation.

For all intermediate states the forward pass gives ||L_k||<=G, where G=302
(primal) or 169 (dual). Bounding every intermediate error by unsigned circuit
paths is much looser. Instead transport a fault back to initial coordinates:

    L_k L_j^(-1) E_(t_j) eta_j.

A separate chronological pass constructs columns of L_j^(-1) by right
multiplying each next inverse instruction. Put h_j equal to the certified
maximum block-row norm of its destination column and D=sum_j h_j. Then for
every k,

    ||actual_state_k - exact_state_k|| <= G D epsilon.

This follows by the triangle inequality applied to the displayed identity,
using only j<=k and nonnegative h_j. The checked new-word constants are

| Orientation | G | D | A=G D | B |
| --- | ---: | ---: | ---: | ---: |
| Primal |302|149131/8|22518781/4|1335|
| Dual |169|187687/8|31719103/8|4841|

Both providers have these values. Old PR3734 words have D=149099/8 and 187679/8;
their slightly smaller values reflect changed literal identity-instruction
fault sites, not improved ideal endpoint maps. The inverse-column calculation
has an independent dense-matrix Gauss-Jordan oracle. The certificate also
retains the much larger unsigned-path envelope as a contrasting method.

## Absolute-error precision and an explicit magnitude allowance

Let H>0 bound every initial register, including dirty helpers and private
buffers, and let beta>=0. Uniform per-instruction block faults bounded by

    epsilon <= H 2^(-beta-13)

imply final error at most H 2^(-beta), since both B<2^13. The primal orientation
alone needs only beta+11 by this sufficient test. Throughout either execution,

    ||actual_state_k|| <= (G + A/8192) H < 1024 H.

The last strict inequalities are checked rationally. This is a completed
literal-word range bound, not just a bound on instruction coefficients.
If initial dirty fields are bounded only by 2^delta times the desired data
scale H0, replace H with 2^delta H0 and add delta to the requested fractional
reserve to recover an H0-relative final tolerance.

For a binary fixed-point implementation choose H as a power-of-two upper bound. For a block with d complex coordinates, real and imaginary component rounding
errors bounded by H 2^(-p) imply a block error <=sqrt(2 d) H 2^(-p). Therefore

    p >= beta + 13 + ceil(log2(sqrt(2 d)))

suffices for the absolute-error premise when it applies to the completed
instruction output. This conversion explicitly pays dimension; a block error
budget is not a per-coordinate error budget. Dyadic scalar ADD and SCALE can
be evaluated exactly before a single output quantization. Their operand
accumulator has magnitude <9*1024 H<16384 H under the same bounds; this counts
its extra range, but not a native macro's internal workspace. A physical native
macro must establish its own completed block-error budget before using this
lemma. Its internal operations are not assumed exact or free.

## Relative completed-instruction error

Alternatively assume ADD faults are bounded by
u(||destination||+|c| ||source||), SCALE faults by u|c| ||operand||, and warp
faults by u||operand||, on the actual entering operands. A correction's ordered
native word is an isometry in this defined macro contract. The exact prefix
operand-sum bounds are R=454 (primal) and R=635/2 (dual). Each local operand
bound has Lipschitz constant at most 9 in the maximum-register norm.

Writing eta=max_j ||eta_j|| and using the all-cut bound A eta gives

    eta <= u(R H +9 A eta).

If 18 A u<=1, then eta<=2 u R H, so final error is <=2 B R u H.
For both new providers and both orientations, exact rational inequalities give

    18 A < 2^27,       2 B R < 2^27.

Consequently u<=2^(-beta-27) suffices for final error <=H 2^(-beta).
This is a sufficient reserve, not minimum precision. The unsigned-path
alternative would require 94 bits primal or 100 bits dual for this same proof;
the inverse-prefix transport uses cancellation before taking absolute values.
No bound independent of all dirty-input magnitudes is asserted.

## Composition and the missing stock implication

The completed ideal full-state map has norm at most 2. For a sequence of L
such calls, with each call's absolute completed error epsilon_j and otherwise
norm-preserving chart changes, the running range and accumulated error obey

    H_(j+1) <= 2 H_j + epsilon_j,
    Delta_L <= sum_(j=1)^L 2^(L-j) epsilon_j.

Thus a caller can allocate a concrete error budget rather than silently price
completed calls at unit sensitivity. Sharper bounds may use its actual ordered
shears. If other consumer maps have norm C_j, those exact C_j replace 2.
The lemma does not establish that a physical owner schedule uses only these
723 abstract fields, exact restoration under rounding, native internal error
and storage, recursive depth, or the relation between d and selected-stage
widths. In particular 27 is not the selected stock coefficient sigma in an
O(w log e) envelope. No selected cutoff comparison, uniform stock/tape theorem,
supplier admission or new kappa follows without those missing source maps.

## Extension for arbitrary-register conversion errors at cuts

The 27-bit result above charges destination-local faults at the literal
arithmetic/warp sites. A physical frame climb or recursive child can also
perturb a source or borrowed field. Such errors cannot silently be treated as
a destination-only arithmetic fault. This extension makes their needed caller
contract explicit without pretending to implement the conversions.

For j=0,...,m, permit an arbitrary full-state additive defect e_j at cut j,
with maximum block norm <=epsilon. A cut includes the completed aggregate
error of whatever conversions are assigned there. A conversion before the
next instruction must either be assigned to that preceding cut or transported
through that instruction when assigning the following cut; its norm is not
silently unchanged by a non-isometric scalar instruction.

Let K_j be the sum, over all columns of L_j^(-1), of that column's maximum
block-row l1 bound. It bounds ||L_j^(-1)|| in our maximum block norm. The
independent inverse pass accumulates S=sum_(j=0)^m K_j, including K_0=723
as a conservative bound for the identity. Then

    all-cut error <= G S epsilon,
    final error <= 2 S epsilon.

These follow from the same conjugated-fault identity and the checked endpoint
norm 2. For both new providers, S=202653291/16 primal and 109667669/8 dual;
2 S=202653291/8 and 109667669/4. Both are below 2^25, giving 25 sufficient
absolute guard bits. The relative-cut sufficient guards below are 38 primal
and 37 dual. They cover arbitrary fields and all private/borrowed state, unlike
the smaller destination-column bounds. RESULT.json records S, both gains and
the corresponding absolute guard bits for every input word/orientation.

A sufficient normwise relative-cut contract is
||e_j||<=9 u||actual_state_(j-1)|| for j>=1, and ||e_0||<=u H.
With A_full=G S and B_full=2 S, the same maximum-error argument gives
eta<=u(9 G H+9 A_full eta). Thus

    u <= 2^(-beta-b),    b=ceil(log2(36 G S))

suffices for final error <=H 2^(-beta). This is a conservative conditional
full-state aggregation allowance. It does not show that individual recursive
calls meet it, bound their internal scratch, or identify an affordable physical
consumer. Those implementation obligations remain in the cost ledger.
