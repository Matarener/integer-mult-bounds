# Source-specific native admission for the pooled providers

The three actual pooled providers have the stated native endpoints for every
positive tensor multiplicity, with arbitrary dirty persistent inputs and with
their owned private work returned blank. This is a written all-parameter
algebra proof, supported by a complete finite certificate for the exact source
words and native recipes. It assumes exact child substitution and the literal
scalar/monomial/private-work semantics. Whole-call hosting, physical execution,
restoration tariffs, the recursive induction and the outer multiplication
bound are separate obligations of this package. This document alone makes no
new exponent claim and is not a formal-kernel verification.

## Source identity and credit

Scientific inputs remain those of PR4270 head
`a929a3fa36301bdfcffe82afd37434dd9e3c4887`; the frozen physical bundle and
`PHYSICAL-PINS.json` in `research/complex-pooled-full-admission` remain unchanged.
The exact native transport, emitter, local replay and Clifford primitives are
from canonical base `12fa8c5c844be21bfefb38a19503fbd867a11244`.

The existing free-word tensor-lift result is reused from PR4184, exact head
`94b9ca9cf59ea6de346a59c92b414454bdde1de4`, package
`research/free-word-tensor-lift-audit`. PR4184 was prepared for ToikY with
substantial OpenAI Codex assistance. It attributes the representation argument
to Cinna Davis/PR4100, the actual words to Cinna Davis/PR4088, and the retained
free engines to Sagar Thakrar/PR3687 and roger-sato/PR3693. The source lineage,
notices and complete retained PR4184 package are preserved byte-for-byte in
`frozen/native/SOURCE-CLOSURE.tar.gz`; `MANIFEST.json` records original commit,
path, byte length, Git blob and SHA256 for every member. This work contributes
the binding to the active pooled native providers and the native recipe and
frame-gauge substitution proof, not a new free-word lift.

`native_admission.py` authenticates both complete source archives before
execution, regenerates each canonical word with the unchanged
`bw_transport.run`, and regenerates both orientations with unchanged
`bw_emit.py`. Equality is equality of complete scientific JSON, independently
of gzip encoding:

| Active pooled provider | PR4184 checked PR4088 export | Native persistent roles |
| --- | --- | ---: |
| `gauge44` | `THREE-base` | 632 |
| `extra` | `THREE-extra` | 632 |
| `extra-four` | `FOUR-extra` | 632 |

Thus no unverified interchange of source words, compensated helpers or fourth
entry is used. The fourth audited export, `FOUR-base`, is retained and replayed
as part of the original complete PR4184 result; it is not an active pooled
provider in this construction.

## Exact native input and output contract

Work over a characteristic-zero field containing the Gaussian dyadics, for
example \(K=\mathbb Q(i)\). Fix a positive integer \(f\). Let each packet have
the internal space

\[
 V_f=(K^{2^9})^{\otimes f}\otimes W,
\]

where \(W\) is an arbitrary spectator factor. In the historical \(m=73\)
model, the 64 unused coordinates in every column are included in \(W\), up to
the fixed column-major/coordinate-major permutation. Extra spectator factors
are allowed as well. No independence of packet contents or tensor factors is
assumed: all statements are linear identities on the full direct sum of
packet spaces.

There are 112 source packets \(x_q\), 112 target packets \(y_q\), and 408
arbitrary dirty helper packets. The eight centre packets and 91 cleanup
packets are owned work, initially blank under the physical work ABI. They
return blank. The 632 persistent packets may be arbitrary and correlated.
The stronger underlying PR4184 word identity allows all 91 abstract private
cleanup inputs to be independent dirty variables and restores them; the
native implementation here specializes these inputs to zero. This does not
turn the eight centre `clear` operations into an arbitrary-workspace claim.

Write

\[
 C_q=\tfrac{1+i}{2}I+\tfrac{1-i}{2}X_q,\qquad
 F=C_9=\prod_{j=0}^{8}C_{e_j},\qquad D_q=FC_q^{-1}.
\]

Here \(q\) is the actual nonzero direction in the provider's port table. A
subscript \(f\) means the unary operator's \(f\)-fold tensor power, extended
by identity on \(W\); it never tensors the 632-role matrix. The source-bound
physical pair endpoints of the literal native orientations are

\[
\begin{array}{ll}
\texttt{forward}:&
 (x_q,y_q)\longmapsto
 (D_{q,f}x_q,\ D_{q,f}y_q+(FC_q^{-2})_f x_q),\\[2mm]
\texttt{backward}:&
 (x_q,y_q)\longmapsto
 (D_{q,f}x_q-F_fy_q,\ D_{q,f}y_q).
\end{array}
\tag{1}
\]

The coefficient of the second term is one, and the backward minus sign occurs
once. In particular it is not \((-1)^f\). Although \(C_q^{-2}=X_q\), leaving
the product as written avoids hiding any factor. These are the actual local
endpoints before the whole-call controller applies its source-bound gauges
and correction. The word `backward` names the literal program; it is not a
claim that its full physical pair map is the inverse transpose of the first
line of (1).

A helper whose native entrance and terminal frames have dimensions \(e\)
and \(u\) has residual width \(w=u-e\). The exact residual wrappers return
that helper as

\[
 C_{[w],f}h\quad\text{on its first \(wf\) selected axes,}
\tag{2}
\]

and restore all complementary axes identically. A plain cold/FULL helper has
\(w=9\) and residual \(F_fh\). The actual physical-family/cohort placement
of these selected axes is supplied by the hosting proof. Equations (1)–(2)
already include both helper wrappers, every zero-buffer inverse cleanup and
the declared native cleanup tail.

## Reused universal free-word identity

PR4184 independently pulls every one of 723 output functionals backward
through each of the four actual literal words in both orientations. Its
coefficients are exact fractions and its operator words reduce only adjacent
inverse letters. The fresh replay here reproduces its frozen result:
5784 output functionals, 6680 endpoint terms, and no surviving nonempty word.
There is no commutation, finite-order rule or one-column minimal polynomial.
On common labels the endpoints are

\[
 (x,y,h,b)\mapsto(x,y+x,h,b),\qquad
 (x,y,h,b)\mapsto(x-y,y,h,b).
\tag{3}
\]

Let \(\mathcal A=\mathbb Q[F_{72}]\), the group algebra of the free group
on the 72 warp symbols. A word program is a finite product of elementary
role matrices over \(\mathcal A\). For any chosen invertible operators
\(K_1,\ldots,K_{72}\), define

\[
 \rho_f(g_k)=K_k^{\otimes f}\otimes I_W.
\]

The free universal property gives a group homomorphism, and linear extension
gives a unital rational algebra homomorphism. Applying it entrywise to the
proved finite elementary-matrix identity gives (3) on the full \(V_f\)
space for every positive \(f\). This argument does not infer an unbounded
statement from finitely many \(f\) tests. The separately checked dual word
is universal in its own free generators, so the actual unary warp assignment
of either native orientation is allowed. The native source deliberately
serializes the same physical warp record in both orientations; no extra
conjugation of that record is inserted here.

Two distinctions are essential:

\[
 \rho_f(g-I)=K^{\otimes f}-I,
 \qquad \rho_f(cg)=cK^{\otimes f}.
\tag{4}
\]

These are not \((K-I)^{\otimes f}\) and \(c^fK^{\otimes f}\). Role
ADD/SCALE coefficients, including initial corrections and signs, stay once.
Conversely a constant phase already inside a unary monomial is tensorized:
\((i^aM)^{\otimes f}=i^{af}M^{\otimes f}\). This keeps every
\(f\)-dependent phase, including phases of inverse wrappers.

## Complete native recipe certificate

Let \(\Gamma_U\) be the exact source `canonical_frame(9,U)`. Each supplied
directed child recipe is checked as

\[
 \Gamma_V\Gamma_U^{-1}=L_{UV}C_{[r]}R_{UV},
 \qquad r=|\dim V-\dim U|.
\tag{5}
\]

The apply order is right monomial, exact rank-\(r\) child, left monomial.
All source-listed recipes are checked, not merely recipes reached by one
orientation. The active provider inventories are 3069, 3069 and 3071 directed
children; both orientations together reach every one. The certificate also
checks all 224 endpoint adapters, all 180 serialized warp classes per
provider, every residual pair, and every serialized warp-generator recipe.
Duplicate mathematical cases across providers are cached using the exact
frame vectors and full recipe content; metadata coverage is checked before
deduplication.

The checker decodes the supplied monomials with the pinned primitive
constructors; it never calls `lower_child` or generates replacement recipes.
A supplied operator and its reference are equal if their conjugation actions
agree on all 18 Pauli generators and a corresponding nonzero amplitude of
their zero-input columns agrees exactly, including Gaussian numerator and
dyadic denominator. This is a complete equality test: the quotient then
commutes with every \(X_j,Z_j\), whose commutant on \(K^{2^9}\) consists
only of scalars; one equal nonzero matrix coefficient fixes that scalar.
The primitive tableau rules follow directly by conjugating \(i^pX^xZ^z\)
through the literal diagonal, permutation, translation, phase and quarter-X
instructions. `zero_state` evaluates those same instructions in exact
Gaussian dyadics. It never uses floating point or hash equality as an
operator-equality test.

The relevant references, with ordinary matrix apply order, are:

\[
\begin{aligned}
 A_{q,\mathrm{source}}&=\Gamma_{\mathrm{start}(q)}C_q^{-1},\\
 A_{q,\mathrm{target}}&=\Gamma_{\mathrm{final}(q)}(FC_q^{-1})^{-1},\\
 W_{k,U,V}^{\epsilon}&=\Gamma_VK_k^{\epsilon}\Gamma_U^{-1},\\
 S_{E,U}&=\Gamma_U\Gamma_E^{-1}=L_{E,U}C_{[u-e]}R_{E,U}.
\end{aligned}
\tag{6}
\]

For a source generator whose GF(2) matrix has columns \(G\), the actual
\(K_G\) is the permutation by \(G\), followed by the diagonal quadratic
phase with matrix \(I+G^{-T}G^{-1}\). This definition, including its scalar
phase, is compared to the serialized generator and physical warp records.
The residual pre-wrapper is \(R_{E,U}^{-1}\) and its post-wrapper is
\(L_{E,U}^{-1}\); (6) therefore gives exactly (2), including cold proper
terminal frames \(E=0\). A proper terminal recipe is never replaced by the
FULL terminal recipe sharing the same entrance.

Every equality (5)–(6) is now an equality between fixed unary operators.
Taking its \(f\)-fold tensor power gives the required equality for every
positive \(f\), with all factors and scalar phases retained. Under the fixed
coordinate permutation, \(C_{[r]}^{\otimes f}\) is the rank-\(rf\)
coordinate child, with identity on its complement. This is the sole child
action needed by the native lift. It is smaller than the parent because all
positive native child ranks satisfy \(r\le8<73\). The recursive induction
must supply that exact child action on its actual hosted coordinate set.

This does not assume `U(S1)` or lift a one-column 632-role native endpoint
matrix. The role-level cancellation is proved in the free group algebra.
The fixed nine-coordinate computation is used only to certify individual
unary recipe identities, to which tensor functoriality legitimately applies.

## Frame gauge, private cleanup and endpoints

At a common frame \(U\), represent a physical packet as
\(p=\Gamma_{U,f}z\). Every scalar gate applies the same rational coefficient
to its physical operands, so it applies the literal scalar gate to their
logical \(z\)'s. Equation (5) changes the frame without changing \(z\).
The warp identity in (6) changes \(z\) to \(K_{k,f}^{\epsilon}z\).
An owned centre copy, its complete descending/ascending child path and its
clear therefore realize exactly the emitted common-label centre macro.

The original `bw_audit_local.local` is freshly replayed in both orientations
for each provider. Its four algebra/interval function definitions are
compiled unchanged from the authenticated AST, with assertions explicitly
enabled even under `python -O`. Module I/O and its NumPy matrix engine are
omitted; the warp callback instead invokes the separate exact certificate
above. The symbolic rows and cancellation rules, frame incidences, scalar
prefix calculation, wrappers, centre paths and 91 zero-buffer lifetimes are
unchanged. The replay begins with 632 independent dirty persistent symbols,
checks the full endpoint on every symbol and checks that every private row
is zero at return.

In particular, this replay forbids *any* read or warp of a wrapped helper
before its pre-wrapper or after its post-wrapper. That includes zero-frame
premix reads. Hence, for a dirty helper \(h\), it is legitimate to choose
the initial logical variable
\(z=\Gamma_{E,f}^{-1}R_{E,U,f}^{-1}h\). There is no illicit movement of a
wrapper across a prefix that already reads the helper. The free-word result
restores \(z\), so the terminal physical helper after its post-wrapper is
\(L_{E,U,f}^{-1}\Gamma_{U,f}z=C_{[u-e],f}h\).

For a source pair the initial logical variables are
\(z_x=C_{q,f}^{-1}x_q\), \(z_y=y_q\). Source entry adapters implement
those gauges; source exits are identity at FULL, while target exits apply
the inverse of the target adapter in (6). Substitute these logical variables
into each line of (3). The resulting physical endpoint is exactly (1).
All 91 private cleanup packets start zero and have identically zero output;
all eight centre packets are closed; all other tensor/spectator coordinates
are covered by the same operator identities. No zero dirt, product-state
assumption or one-column representation relation has been used.

## Reproducible evidence and remaining boundary

Run `python3 native_admission.py --check evidence/NATIVE-ADMISSION.json` from
this directory; the same command with `python3 -O` must give the identical
receipt. It uses only the standard library and the two authenticated local
source bundles. There is no live Git, network, solver or historical run-path
dependency. Normal execution is bounded by the finite 29-member source
closure and complete recipe inventories, independently of \(f\).

The controls reject a child phase change invisible to its Pauli tableau,
swapped residual wrapper sides, a missing zero-buffer release, a missing
warp inverse cleanup, a missing helper post-wrapper and a helper read moved
before its pre-wrapper. The reused PR4184 controls independently forbid
commutative/fourth-power collapse and preserve the two terms of \(g-I\).
These controls test the delicate boundaries of the proof; they are not its
all-parameter argument.

Discharged here are the source identity of all three pooled native providers,
their complete arbitrary-dirty persistent endpoints and owned-work cleanup,
every phase-inclusive native recipe, and their lift to every positive
\(f\) under exact child substitution. Retained premises are exact physical
scalar/monomial/work operations on a representable common grid; exact child
implementation on each selected coordinate set; whole-call placement and
hosting; paid controller and restoration costs; recursive storage and time;
and the outer multiplication transfer. Those premises must be discharged by
their owning proofs before calling \(\kappa=1/580\) admitted. Historical
model assumptions of the multiplication theorem remain explicit in the
package-level admission statement.
