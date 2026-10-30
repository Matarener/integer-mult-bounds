# Sharp deterministic error for normalized Walsh stages

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Fix a grid spacing h>0 and an integer J>=0. On an array with J selected
binary axes and any spectator axes, apply the J distinct factors

    H0 = (1/2) [[1,1],[1,-1]],

one axis at a time, in any fixed order. After every factor, round each
coordinate to the nearest multiple of h, with ties to the even grid integer.
The input is any array in h Z, without a magnitude restriction in the
mathematical model. Every sum and difference before rounding is exact;
overflow and other arithmetic defects are excluded.

Let T be the exact normalized Walsh operator and F its rounded version.
Then the sharp uniform coordinate bound is

    sup_(x in (h Z)^(2^J)) ||F(x)-T x||_infinity = h a_J,
    a_J = J/3 + (1-(-1/2)^J)/9.                         (1)

Spectator fibers are independent, so the same bound holds for any number
of spectators. Exact final recovery to the raw Walsh operator multiplies
the error by 2^J. In particular its sharp bound is h 2^J a_J.

The more precise statement for one output coordinate is as follows. If
its stored output divided by h is even, the sharp absolute error is h a_J.
If it is odd and J>=1, the sharp absolute error is h a_(J-1).
At J=0 both errors are zero.

The theorem concerns this deterministic quantizer. It is not a theorem for
arbitrary bounded faults, non-grid initial data, repeated axes, intervening
non-Walsh gates or the actual accelerated recursive supplier.

## Reduction to a binary averaging tree

Scale by h and work with integer grid values. Write R(s) for nearest-even
rounding of a real number to an integer. It is odd, and

    R(s+2k) = R(s)+2k                                   (2)

for every integer k. Translation by an odd integer need not commute with R.

Fix an output of the J-stage butterfly network. Its dependencies form a
complete binary tree of depth J, with disjoint original inputs at its
leaves. Each internal node is R((u+v)/2) or R((u-v)/2).
Oddness lets us absorb every minus sign into the leaves and intermediate
subtrees. Thus it suffices to analyze a complete tree of rounded averages.
Its exact value is the average of its 2^J signed leaves. This reduction
uses distinct axes; repeated use of an axis need not give disjoint leaves.

## Parity-sensitive bounds

Let a_j and b_j be the maximal absolute error at depth j conditioned on
an even or odd integer output. Start with a_0=b_0=0. We prove inductively
that the finite maxima exist and satisfy

    b_j = a_(j-1),
    a_j = 1/2 + (a_(j-1)+b_(j-1))/2.                    (3)

Consider child outputs u,v. If u+v is even, the root division is exact.
The child parities agree, and averaging their errors costs at most
max(a_(j-1),b_(j-1))=a_(j-1).

If u+v is odd, its half lies exactly between consecutive integers. The
stored root is even, its local error has magnitude 1/2, and the child
parities differ. The total error is therefore at most the second line
of (3). An odd root can occur only in the exact-division case, proving
the first line's upper bound.

For completeness the second line dominates the exact-division bound.
Put d_j=a_j-a_(j-1). The recurrences give d_1=1/2 and

    d_j = (1-d_(j-1))/2,    j>=2.

Induction gives 1/4<=d_j<=1/2 for every j>=1. Hence a_j is increasing and
b_j<=a_j. This proves the comparisons used in the induction, without
assuming a closed form in advance.

## Attaining inputs

Construct integer leaf lists E_j,O_j with rounded outputs 0 and 1.
Their signed errors, stored output minus exact average, will be a_j,b_j.
Use concatenation, and let adding an integer to a list mean entrywise
addition. Define

    E_0=[0],  O_0=[1],
    E_j = E_(j-1) concatenated with (O_(j-1)-2),
    O_j = E_(j-1) concatenated with (E_(j-1)+2).          (4)

By (2), the children of E_j have stored outputs 0,-1 and errors
a_(j-1),b_(j-1). Their root rounds -1/2 to 0, so its error is the second
line of (3). The children of O_j have outputs 0,2 and both have error
a_(j-1). Their root is exactly 1, proving the first line of (3).
Negating a leaf list attains the negative extremum. Even translations
give every other prescribed output of the same parity.

The E_j entries lie in [-j,0]. In the ordinary low-bit-first Walsh
schedule, concatenate the lists along the last processed axis. Then its
zero-frequency output is exactly the averaging tree above. This proves
attainment in the actual butterfly network, rather than in a relaxed
independent-error model. Other fixed axis orders use the matching input
axis permutation. Therefore the coordinate upper bound and the sup norm
maximum in (1) are both sharp.

Substituting b_j=a_(j-1) in (3), with a_0=0 and a_1=1/2, gives

    a_j = 1/2 + (a_(j-1)+a_(j-2))/2,    j>=2.

The expression (1) satisfies these initial conditions and recurrence,
which proves the formula. The usual stagewise bound is J h/2. Equation
(1) is strictly smaller for every J>=2, and its ratio to J h/2 tends to 2/3.
These are exact algebraic comparisons, not measured speedups.

## Complete residue domains

For depth J the error is periodic in each integer input coordinate with
period 2^(J+1). Indeed, add 2^(J+1) times an arbitrary integer array to
the input. After k stages its exact displacement has coordinates
divisible by 2^(J+1-k), which are even integers for all k<=J. Equation
(2) therefore propagates precisely that displacement through every
rounded stage. The final displacement equals the exact Walsh displacement,
so their error arrays coincide. This also holds in the presence of signs.

Consequently the verifier's 4^2 one-stage inputs and 8^4 two-stage inputs
are complete residue-domain checks for those depths. Larger depths are
corroborated by witnesses and a parity-state enumeration; the all-J
conclusion rests on the proof above.

## Application to PR #6119's numerical surrogate

CubeJerry's PR #6119, head bdfe5a10d488b5f774e906d8d4588dc8da25e7ba,
defines an eight-input surrogate with exposure, four temporary coordinates,
the echo m=1/2,a=4, two distinct H0 axes and projection of the temporaries.
It rounds after its six nominated noisy maps to the same h grid.
Its arbitrary-defect theorem and its finite ternary-cube observation are
credited prior results and context; neither is re-audited here.

For every grid retained coordinate x=h k, its initially zero echo temporary
becomes h R(k/2). The upper addition and its inverse are integer-grid
operations and cancel exactly. The lower inverse leaves, before rounding,

    h [R(k/2)-k/2],

which is 0 or +/-h/2, and hence rounds to zero. Thus for every grid input
the entire rounded echo is the identity on retained data and returns the
temporary row to zero. The remaining retained computation is precisely
two rounded Walsh axes. Exposure and its inverse are exact permutations.
Its sharp normalized error is therefore 3h/4, for all eight grid inputs.

At the predecessor's h=1/4 this is 3/16; exact raw recovery multiplies it
by four, giving 3/4. One attaining original-coordinate input is

    (0,0,-1/4,0,-1/2,0,0,0).

The four entries of the first spectator fiber are E_2/4. This supplies an
all-grid theorem and explicit witness beyond the predecessor's finite
6,561-point cube. It is still a numerical surrogate, not a materialized
PR6030 child or a physical disposal implementation.

## Limits and credit

CubeJerry supplies the explicit open distinction between independent
defect boxes and deterministic quantizer errors, and the two-phase surrogate.
Vlado Vojdanovski's PR1673 supplies the normalized H0/deferred-row context;
the selected construction retains its original authors and five assumptions.
JoyboyBrian's `native-rounded-butterfly-contract` supplies related pair-first
nearest-even arithmetic and parity constraints for different complex Gaussian
letters. The present averaging-tree parity recurrence and attaining all-J
Walsh bound are the new result.

No full selected replay, native admission, proof-kernel check or independent
human review is claimed. The theorem assumes exact pre-rounding arithmetic,
unbounded integer range and the specified grid ABI. Bit costs, intermediate
range guards, tape movement, reversible history and an accelerated supplier
remain separate obligations. Source files and the selected frontier are unchanged.
