# What continuation routing and a changed dual core actually buy

Scientific source: canonical `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
All work here is local to this lane. Frozen predecessor sources are
read-only inputs. The results are scoped circuit and component-moment
gates; none is a global multiplication obstruction or an improved kappa.

The current response is the exact all-f Gaussian operator
`J_f=i^(f+1) Z U`, with `J_f^2=-I`. Use q>=2,
`n=2q+2`, `k=2q+1`, `m=4q+4`, and actual output **F_k J**, where
`F_s=N_s...N_1`. All original inputs, including the two old owner fields,
are arbitrary. Public-reader terms are retained in the full original
column matrix and do not disappear when its pivot block is considered.

The common method is a bound on a coefficient of the *unfactored joint
inverse*, rather than the cost of cleaning the two factories separately.
For a full bank/address circuit, a native arity-r child has maximum row
support2^r, a physical monomial has support1, and a binary scalar bank
ADD has support at most2. Consequently a required coefficient with row
support at least2^(rho*f-O(1)) forces

    total native arity + binary ADD count >=rho*f-O(1).

Arbitrary Gaussian cancellations and additional independent dirty banks
do not evade that induction. It does not price an operator-valued ADD
as one scalar primitive. The native-mass/moment corollaries additionally
require **equal-volume full-bank child normalization**, separately
charged query sites and the parent's source-bound full-scan transfer.
Fixed positive relative volumes alone are insufficient. See
`COST-SCOPE.md` and the pinned parent `FULL-SCAN-TRANSFER.md`.

Three changes were assessed, with different covered domains.

1. **Any scalar GL2 at the one q3 continuation cut.** An arbitrary
   invertible scalar matrix M, even with f-dependent coefficients, gives
   an original-t/current-V inverse coefficient that is a nonzero
   combination of three distinct native-10f Clifford rays. Their exact
   normalized one-coordinate Hilbert-Schmidt overlaps have moduli
   1/16,0,1/256. After grouping proportional rays, the tensor Gram matrix
   has minimum eigenvalue at least7/8. Hence some row of the coefficient
   has at least `(7/24)2^(10f)` nonzeros, uniformly in the coefficients.
   The q3 prefix margin is6, so this cut cannot yield a favorable native
   moment under the cost premises above. The upper/lower/balanced
   physical traces are independent source bindings, not the proof of
   the arbitrary-M claim. The theorem is one cut at q3; it does not
   cover all-q arbitrary GL2 schedules. Proof and receipt:
   `GL2-CONTINUATION-PROOF.md`, `GL2-CONTINUATION-GATE.json`.

2. **Identity/SWAP routing at every nonfinal continuation.** Let d0,d1
   count the odd source factors on the two base-core paths. Then
   `d0+d1=q-1`, `d0>=1`. The required original-t inverse coefficients
   have support exponents `2d0+6` and `2d1+8`; the second coefficient is
   a two-ray difference whose support is separately bounded by an exact
   overlap calculation. Both paths retain the initial B3J factor.
   Balancing gives the exact all-q necessary exponent

       r*(q)=2ceil(q/2)+6.

   The exponent sum2q+12 is not asserted to be a joint native bill.
   The finite producer checks511 schedules q2..10 and preserves full
   signed best-path witnesses; the written polar-block calculation
   proves the all-q formula. Even an ideal single rank-r* cleanup query
   fails the equal-volume complete moment for every q>=2 at component
   `b0=1/600`, by an exact rational/logarithmic inequality. It therefore
   fails for b>=b0. Interpreting this as a kappa exclusion additionally
   uses the separately pinned retained transfer kappa<b; another
   transfer needs its own relation. Proofs/receipts:
   `ROUTING-PROOF.md`, `ROUTING-INVENTORY.json`,
   `ROUTING-MOMENT-GATE.json`.

3. **A changed first-two-source dual core.** This genuinely changes the
   old base and is outside its fixed-core theorem. With normalized
   retraction columns `w1=(-J,lambda J)`, `w2=(mu,1+mu)`, symbolic
   noncommutative inversion gives the first row of the new core inverse.
   The exact dual choice lambda=-1,mu=0 removes B2^-1 from the required
   original-t/current-V coefficient. Its native arity is2qf, four units
   below the original coefficient. In the literal compiler, however,
   that choice adds one early rank-2f J continuation. Its separately
   charged prefix margin is2q-2, leaving a necessary native mass gap+2.
   The other scalar-parameter strata have gaps4,6 or8. The rank blocks,
   all-f phases and exact generic polynomial inverse are preserved in
   `DUAL-CORE-PROOF.md`, `DUAL-CORE-GATE.json`.

   The caller then found a real cross-cut improvement: fold the single
   stage2 J-valued fanout into the next paid source query using
   `J(b1+Jt)=Jb1-t`, delaying the intervening bridge as well. The folded
   source code is B2; the paid code is JB2. The two prefixes must not be
   conflated. Independent literal-circuit inverse-row replay at q2/q3
   verifies both complete original-owner pivot blocks and every f
   phase. The folded prefix has its original margin2q and the same
   coefficient exponent2q, proving only mass>=stock. That is still
   incompatible with a strict positive-b equal-volume child moment;
   it is not the paid +2 gap. The source-bound distinction is recorded
   in `DUAL-CORE-BINDING.json`, `DUAL-CORE-BINDING-NOTE.md`.

These results do not assign usable helper stock to an unfactored coupled
endpoint. Finite physical source bindings are explicitly q2/q3; all-q
algebraic conclusions require the specified all-q original-column
interface. Native lowering of the caller's complete derivative words
is a separate evidence layer. Each receipt states which layer it checks.

The next constructive change is a chronological owner-retirement
contract, a different delivery/core or retained-continuation map,
further cross-cut query fusion, a genuinely operator-valued coupled
bridge, or a changed coupled terminal owner. Those choices can alter
the required inverse coefficient. In particular a virtual cocycle
J(v+JA) is not treated as a physical native read: its bank must actually
be at the query cut, with every original-column contribution retained.

The exact source pins and reproducible normal/-O commands are listed
in `FOLLOWUP-SOURCES.json`. The predecessors' generic typed-normalizer
identities retain upstream attribution; this follow-up concerns the
source-bound core, inverse support, routing and actual cut tariffs.
