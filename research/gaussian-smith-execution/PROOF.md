# Executable Gaussian Smith response and sharp precision

## Scope and retained source

Use the Smith factorization and schedule from PR5815 at
f0fcda576df410dc15cd5b8183d4f74d284eba2b. The frozen notes have no executed
mathematical checker. This package supplies an independent integer interpreter,
independent dense and direct-tensor oracles, literal cost receipts and sharp
precision witnesses. It does not reattribute the factorization or schedule.

Let pi=1+i, C=[[i,1],[1,i]], N=2^n and P>=0. The output is the raw numerator
C tensor n times x modulo pi^P, for every x in Z[i]^N. For normalized output
A_n x modulo pi^p, set P=p+n and retain denominator header n. Precision p=0
can still require nonzero raw precision. All original input coordinates stay
unchanged. The output and work arrays are owned. Exact reset of owned work is
an explicit operation in the indexed array model, not a reversible tape proof.

## Canonical residues

For q=2k, reduce both Gaussian coordinates modulo 2^k. For q=2k+1, put

```
b0 = b mod 2^k,
a0 = (a - (b-b0)) mod 2^(k+1).
```

The change in b is t*2^k and the same change is subtracted from a. The
removed vector is a multiple of 2^k(1+i); the remaining a reduction is a
multiple of 2^(k+1). Both belong to (pi^(2k+1)). There are exactly
2^(k+1)*2^k=2^q representatives, so the representation is complete and unique.
The even case has the same cardinality. Each representative uses exactly q
binary digits in two nonnegative integers; no spare odd-precision bit is lost.

The checker compares this formula with successive parity digits and exact
Gaussian division. Negative values and every q from0 through12 are included.

## Circuit and complete endpoint

The source proves C=S diag(1,pi^2) T, where

```
T(a,b) = (a-i*b,b),
S(a,b) = (i*a,a+b).
```

The interpreter uses each T axis in increasing bit order. At depth k, a
processed prefix of weight w has precision Q=max(P-2w,0). Compute a-i*b at Q
before truncating b to max(Q-2,0). This order retains every bit required by the
low child. The diagonal scale is represented by the coordinate's tag.

The S pass uses the same axis order. At a pair with high precision Q, compute
b_new=a+pi^2*b and a_new=i*a at Q. The b operand has two fewer precision digits;
its pi^2 factor supplies exactly those two digits. Both outputs receive the
high operand's tag. After the last axis, every tag is n. Induction on the two
passes proves the raw numerator endpoint at precision P for every n and input.
The implementation emits all outputs before it resets its work array.

The independent dense oracle uses entry `i^(n-popcount(r xor s))`. A second
oracle applies the original two-output C butterfly, with no Smith factors or
intermediate precision reductions. These check the complete output, not a
rank or selected set of coordinates.

## Exact information requirement

The diagonal channel at label u needs q_u=max(P-2|u|,0) digits. Its total is

```
D(n,P) = sum_(j=0)^n binom(n,j) max(P-2j,0).
```

**Theorem.** The raw tensor map over Z[i]/(pi^P) has exactly 2^D distinct
outputs. Thus every lossless fixed-length binary encoding of its response
needs at least D bits. The diagonal bank attains this information bound.

Proof: S and T have unit determinants. Their tensor products are invertible
over the residue ring. Multiplication by pi^(2j) has exactly 2^max(P-2j,0)
possible values. Independent diagonal coordinates give the product of these
cardinalities. Invertible input and output maps preserve that number. The
canonical bank uses exactly the sum of the required digit counts. This is an
information bound, not a lower bound on time, total workspace or physical I/O.

## Sharp independent precision at every T cut

After k T axes, consider coordinate r with processed weight w. Its required
precision Q=max(P-2w,0) is the smallest modulus that can be assigned to that
coordinate independently of the other coordinates while preserving every
output for every input.

Sufficiency is the schedule proof. For necessity when Q>0, compare zero with
a cut state whose only nonzero entry is pi^(Q-1) at r. The processed T map is
unimodular, so applying its explicit inverse produces a valid integral input.
In the remaining map, at least one output coefficient of that coordinate is
a unit times pi^(2w): use a nonzero entry of the processed S column and any
entry of the unprocessed C tensor. The output difference therefore has
valuation Q-1+2w=P-1. The cut inputs become identical if this one coordinate
is stored at Q-1 digits, yet their required outputs differ. This proves the
claim. It does not exclude an encoding that mixes coordinates.

The checker constructs2746 such integral input pairs across every cut and
coordinate for n<=5 and the stated raw-precision range. The proof covers all n.

## Whole precision and operation invoice

Let B_m(P)=sum_j binom(m,j) max(P-2j,0). The exact T-stage addition masses are
2^(n-m-1) B_m(P), m=0,...,n-1. The S list is the reverse list. Therefore

```
Q_add = 2 sum_(m=0)^(n-1) 2^(n-m-1) B_m(P).
```

The interpreter counts each executed ADD and its precision independently of
this formula. It also records PHASE, PI2_SCALE, TRUNCATE, input/output COPY
owned INIT and work CLEAR counts and operand widths. PI2_SCALE includes an actual binary
shift and phase; it is not a free relabeling. These counts describe the emitted
indexed circuit. They do not price Python object overhead, a fixed-tape route,
a recursive native query, source matchers or a complete multiplication caller.

At normalized p=n, the source's exact addition-mass ratio to a uniform-modulus
raw tensor is (3n+1)/(4n). Both passes still have growing-width work. The result
is not a wall-clock ratio or an exponent improvement. It retains the source's
Theta(2^n*n^2) limitation when p is proportional to n.

## Exact in-place installation and its extra work

For integral coordinate magnitudes below2^b, raw C tensor n output coordinates
have magnitude below2^(b+n). Use P=2(b+n+2), then decode the two coordinate
residues in the centered interval. This recovers the exact numerator.

Compute the forward response, swap actual public and owned payloads and
headers, and compute the exact inverse response of the new public field.
The inverse numerator is i^n times conjugate(C) tensor n. Applied to the
forward numerator, it gives pi^(2n) times the old numerator. Exact division
by pi^(2n) aligns the original header. Subtract it from the owned old value;
that value is exactly zero. The receipt charges both kernels, the payload
swap, header swap, alignment divisions and cleanup additions. This central
adapter does not include native matchers or physical movement outside the
indexed arrays. A rounded forward image does not justify this cleanup; a
nonzero-residual control checks the distinction.

## Limits and credit

PR5815 supplies the Smith circuit, complete schedule, native assembly argument
and cost formula. The new results are the executable residue/installation
interface, its independent endpoint and cost audit, the exact image-information
bound and the sharp T-cut witnesses. Smith form and finite-ring cardinality
are classical. All frozen source notices are retained. No new native phase
admission, physical tape theorem, rounded recursive child or kappa is claimed.
