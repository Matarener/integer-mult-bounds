# Asymmetric pure-bank factor and compensation splice

This written proof is for the fixed 30,960-port H6 shell at scientific pin
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. It uses the inherited PR606 factor
`K = E diag(w) E^T / 8192`, the actual source/cap representatives, and the
declared paid copied-total/erasure interface. It is a local exact construction.
It does not implement that private interface on a finite tape or admit an
all-size supplier.

## 1. The dyadic change is an exact unit change

For one coordinate u of a block let S and T be the squared norms of its own
and other block. On the fixed shell S+T=16. Write

`a = (16u-u^3)/3`, `g = (u^3-4u)/3`,
`h_l = u sum_{j in Fano line l} u_j^2 - a`, and `t = u T`.

Each of the seven other coordinates occurs in three Fano lines. Therefore

`sum_l h_l = 3u(S-u^2) - 7(16u-u^3)/3`,

and hence

`2g + sum_l h_l + 2t = u(3S+2T-40) = u(S-T)/2`.

Define `f = u(S-T)/16`. This proves `8f = 2g+sum h_l+2t`.
On a mixed port S=T=8. On a pure own-block port (S,T)=(16,0), and
on a pure other-block port u=0. Consequently

`f(p)=1_[p pure in the coordinate's own block] u`.

Replace g by f and retain h_1,...,h_7,t. This 9 by 9 triangular basis map has
determinant 1/4, a unit of Z[1/2], and inverse

`g = 4f - (sum_l h_l)/2 - t`.

In the old bilinear factor this block contributes

`32g(target)g(source) + 4 sum_l h_l(target)h_l(source)
 - 3t(target)t(source)`.

Substituting the inverse only on the source side gives the new scatter
numerators

`128g(target)` for f,
`4h_l(target)-16g(target)` for each retained h_l, and
`-3t(target)-32g(target)` for t.

Every other feature is unchanged. Thus, with A the new source-feature
matrix and B the scatter-numerator matrix, `B A^T /8192 = K`. This is a
symbolic nine-feature calculation repeated in 16 disjoint blocks. It does
not rely on fitting a few source values or on a physical change of dirty
centre basis. All actual gather coefficients are integers; scatter
coefficients are dyadic. The inherited full polynomial certificate supplies
the original K identity, while this calculation proves its preservation.

## 2. Arbitrary-dirt K word

Let x,y,d be arbitrary logical sources, targets and 816 ordinary-centre
entrance values. They may be correlated. At ZERO subtract Bd/8192 from y.
Gather A^T x into the centres. Their values are now `d+A^T x`.
For each centre use its separately paid copied-total episode to deliver
its B column at ZERO, erase the private episode, and finally undo all
gathers. Algebraically the resulting map is

`(x,d,y) -> (x,d,y - Bd/8192 + B(d+A^T x)/8192)
           = (x,d,y+Kx)`.

The source chronology is legal: a pure source visits its own U9, where
the eight corresponding f features are supported. The two banks are
disjoint, so no source visits both incomparable U9 frames. All sources
then reach FULL, where the remaining 800 centres gather. Partial centres
perform their private episodes at U9, then reach FULL before cleanup.
All targets remain ZERO until all private episodes finish, then reach
their final caps. Ordinary centres finish at FULL.

For the same-order inverse-transpose orientation, precompensation puts
`d+B^T y/8192` in the centres. Dual gathers subtract
`A(d+B^T y/8192)` from x. Each dual private episode gathers its B-column
total from unchanged ZERO targets, ascends to the centre frame, subtracts
that total from the centre, and is erased under the declared interface.
The centres now contain d. Dual cleanup adds Ad back to x, giving
`(x,d,y) -> (x-K^T y,d,y)`.

The erased private value need not be zero before the interface's erasure.
Its cleanup is a named premise, not an ordinary reversible CLEAR inferred
from this linear calculation. Given the admitted exact common-frame
operators, these identities hold for arbitrary complex physical register
vectors, including arbitrary Gaussian-dyadic inputs. Logical restoration
of an ordinary helper at FULL means physical output Fd for entrance d at
ZERO. It does not mean literal physical output d.

## 3. Full address-bucket splice

Let C=I-K. Index one helper by (s,b) for every source s and target label b
with `p_s dot b=0`. Let G be the R by N capture matrix with one entry 1
in row (s,b), column s. Let D be the N by R matrix whose entry in row t,
column (s,b) is C_ts when t has label b, and zero otherwise. The inherited
support identity gives `DG=C`.

For arbitrary helper dirt e perform, in order:

1. At ZERO subtract De from targets.
2. Capture source values: helpers become `e+Gx` at their source lines.
3. Run the complete asymmetric K word, including its own source climbs,
   private erasures, centre cleanup and target-cap climbs.
4. At each bucket cap add D times the captured helpers to the targets.
5. At FULL subtract Gx from the helpers.

This gives `y-De+Kx+D(e+Gx)=y+x`, and restores every helper logically.
Each helper follows `[1,15,1]` because its source line is contained in its
bucket cap. Its line-to-cap climb can occur immediately after capture or
after K: K touches none of these helper registers. In either placement,
the capture precedes every K source climb.

The five dual phases yield helpers `e+D^T y`, subtract
`G^T(e+D^T y)` from sources, apply the arbitrary-source K dual, restore
helpers to e, and add G^T e back. The source output is

`x - G^T D^T y - K^T y = x-y`.

The pre-K source mutation is accepted by the arbitrary-source contract
proved above. There is no assumption of clean targets or helpers at this
cut. In the inherited bucket schema, the old outer source-to-FULL climb,
old K hook and outer target-cap climb are replaced by the complete new
K word. Appending the partial U9 gather after the old FULL climb is illegal.

## 4. Complete local path invoice

The role paths, each charged once, are:

| Role | Count | Path |
| --- | ---: | --- |
| Pure-bank sources | 2,160 | [8,8] |
| Mixed sources | 28,800 | [16] |
| Targets | 30,960 | [16] |
| Partial ordinary centres | 16 | [9,8] |
| Other ordinary centres | 800 | [17] |
| Partial private episodes | 16 | [9] |
| Other private episodes | 800 | [17] |
| Compensation helpers | R | [1,15,1] |

The full label enumeration has 14,400 labels of multiplicity two meeting
7,312 orthogonal labels, and 270 labels of multiplicity eight meeting
7,744 orthogonal labels. Thus

`R=14400*2*7312+270*8*7744=227312640`.

The resulting histogram is

`H={1:454625280,8:4336,9:32,15:227312640,16:59760,17:1600}`.

The total rank mass is 3,865,333,216; private rank mass is
`16*9+800*17=13744`. Relative to the original complete K stage,

`DeltaH={8:4336,9:32,16:-2160,17:-32}` and `sum_r r DeltaH_r=-128`.

This counts the extra visits of all 2,160 pure sources. No ordinary role,
physical width, stock or pad is deleted. Under the inherited scalar
Horner tariff the new K word costs 243,600,112 component primitives forward
and 243,602,560 dual, before real/imaginary doubling and native adapters.
The existing complete bucket compensation alone costs 9,524,090,880 under
that same tariff: `16*480337920 + 6*3363840 + 8R`. Hence the combined
semantic scalar invoices are 9,767,690,992 forward and 9,767,693,440 dual.
These are upper invoices under an explicit lowering convention, not tape
step counts or a proof of faster physical execution.

## 5. Proof and evidence boundary

The phasewise identities prove the full indexed construction under the
stated inputs and interfaces. The finite literal replay covers 32 actual
ports, every 816 K centre, 436 edge helpers and all 1,316 independent input
columns in each orientation; it does not execute the full bucket network.
The phase compiler obligation belongs to the native-frame audit. The
recursive copied-total/erasure and physical restoration wrapper, complete
bank placement, composite precision with approximate children, source and
tape access costs, and joint BIT/complex outer moment remain separate.
No new kappa, full supplier or global helper lower bound follows.

Credit: Dominik Scholz's PR606 geometry and factor, DreamingOfClouds's H6
proposal, the upstream H6 compensation network, and the frozen asymmetric
U9 and composition work. This independent review/proof was prepared with
OpenAI Codex assistance; Apache-2.0.
