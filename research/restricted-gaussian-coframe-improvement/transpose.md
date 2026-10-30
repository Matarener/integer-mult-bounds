# Plain-transpose closure exchanges the two Gaussian exception interfaces

## Exact result

For one fixed, fully typed pair of commuting symmetric Gaussian operators `D,Q`, put `R=DQ`. The actual lower interfaces

`B_y = [[D,0],[D,R]]`, `C_y = [[R,0],[D,D]]`

satisfy

`S B_yᵀ S = C_y`, `S C_yᵀ S = B_y`,

where `S` swaps the two main banks. Thus a complete admitted supplier for either interface yields a supplier for the other interface on the same actual `D,Q` geometry, with exactly the same paid Gaussian histogram and independent canonical helper grades. The new supplier is an explicitly transposed program with paid ordinary swaps and scans. It is not the old inverse-transpose program, and no destructive erasure is inverted.

This does not identify suppliers having different ambient dimensions, port projectors, retained-column interfaces or parent grades. In particular, a restricted rank-eight geometry is not thereby an unrestricted rank-nine geometry. The result supplies an additional orientation of each actual eligible source, to be used with its own complete invoice.

## 1. Physical transpose and its elementary compiler

Use plain bilinear transpose in the fixed physical delta-function basis, without complex conjugation. For a finite physical program, reverse the order of its high-level linear instructions and replace each instruction by its transpose. This constructs the transposed operator algebraically. It does not reverse the underlying Turing machine or assume random access.

The retained source instruction types have explicit transposes:

| Old physical instruction | New physical transpose instruction |
|---|---|
| Scalar SCALE by c | SCALE by the same c |
| ADD `v += c u` | ADD `u += c v` |
| Ordinary monomial `M` on a field | Its ordinary transpose `Mᵀ`, with the same literal scalar phase |
| Gaussian child `Γ_k` in its canonical positive normalization | The same child `Γ_k`, since `Γ_kᵀ=Γ_k` |
| Whole owned CLEAR | The same CLEAR |
| Owned overwrite COPY `(u,v)↦(u,u)` | ADD `u += v`, then CLEAR the owned v |
| Owned query-COPY `(u,v)↦(u,K u)` | Apply `Kᵀ` to owned v, ADD it into u, then CLEAR owned v |

The ordinary transpose of a monomial uses the inverse coordinate permutation and the corresponding transposed diagonal multiplier. It is not conjugated unless that conjugation is already a literal part of the supplied word. All fixed coefficients and phases are retained exactly.

For a whole Gaussian instruction `K=L Γ_k M`, with supplied ordinary two-sided normalizers, the new instruction is

`Kᵀ = Mᵀ Γ_k Lᵀ`.

This proves that its Gaussian rank and multiplicity are unchanged. It also supplies the actual changed input/output normalizers, rather than keeping old header labels blindly. A query-COPY therefore still uses exactly one rank-k query; overwriting its owned destination with the transposed query output is legal because the instruction's old destination value is no longer needed after its contribution is accumulated.

The COPY rule follows directly from the two-field matrices

`[[I,0],[I,0]]ᵀ = [[I,I],[0,0]]`.

Likewise the query-COPY rule follows from

`[[I,0],[K,0]]ᵀ = [[I,Kᵀ],[0,0]]`.

Every clearance in these rules is of the corresponding owned destination. The source's owned centre is an accumulator in the transposed program, not an immutable old cache ticket.

## 2. Owned entrances, complete endpoints and helper credit

If an old source is specified only on zero owned inputs, explicitly sandwich its physical program between complete paid owned-zero projectors `E_in,E_out`. Include the dirty entrance scrub, exact zero header acquisitions and final clearing scans. On all raw inputs its full operator is then

`F = diag(T,0_owned)`.

Consequently

`Fᵀ = diag(Tᵀ,0_owned)`.

The transposed program starts with the old final owned projector and ends with the old initial owned projector. Arbitrary dirty owned payloads therefore have no retained output effect, and every owned field again returns to zero. No inverse of a CLEAR is requested.

Apply the actual whole-job ordinary helper normalizers before transposing. If the old complete autonomous endpoint has the typed form

`diag(M_main, Γ_k1, …, Γ_km, 0_owned)`,

its transposed endpoint is

`diag(M_mainᵀ, Γ_k1, …, Γ_km, 0_owned)`.

Thus all surviving helper inputs remain arbitrary and independent, with exactly their actual positive canonical grades. This applies also to helpers beginning in nonzero coframes: their grade is the retained complete endpoint grade, not the dimension of a final frame. Transposing an unnormalized partial native fragment and simply calling it the old positive helper would not prove this statement.

The autonomous helper block has no cross-terms with the main block. It remains autonomous after main-bank swaps or ordinary main gauges. No helper is owned, identified with another helper, cleared or credited twice by this construction.

## 3. The actual interface algebra

Let `D,Q` act on the same payload space, and require the actual source identities

`Dᵀ=D`, `Qᵀ=Q`, `DQ=QD`, `R=DQ`.

These are the symmetric canonical Gaussian directions of the retained interface, with exact source phases. Let

`A_y = D S_y(Q⁻¹)`,

`G_y = diag(I,Q)`, `G_x = diag(Q,I)`,

where `D` in a two-bank expression means `diag(D,D)`. The source interfaces are

`B_y=G_y A_y`, `C_y=A_y G_x`.

Direct multiplication, using commutation, gives

`B_y = [[D,0],[D,R]]`,

`C_y = [[R,0],[D,D]]`.

Since `Rᵀ=R`, ordinary main-bank interchange `S=[[0,I],[I,0]]` gives

`S B_yᵀ S = [[R,0],[D,D]] = C_y`,

`S C_yᵀ S = [[D,0],[D,R]] = B_y`.

This is the simplest exchange rule. It requires no extra Q call, no Q inverse call, and no Q-square gauge. Both bank swaps are actual paid ordinary field permutations at the supplier's boundaries. The transposed complete source supplies the middle operator.

For a direct sum of actual port geometries, apply the rule on each correctly matched pair. Each pair retains its own actual `D_p,Q_p`, port routes and dimension labels. The rule exchanges exception placement and the two named main banks within that pair. It does not replace those geometries by one shared unimplemented chart.

## 4. Upper-interface form and the ordinary Q-square gauge

The source also admits `J=Q²` and `J⁻¹` as explicit ordinary monomials, including their phases. Define

`A_x = D S_x(−Q)`, `E = diag(−Q²,I)`.

Plain transpose gives

`A_yᵀ = D S_x(Q⁻¹)`.

Conjugating by the ordinary E yields

`E A_yᵀ E⁻¹ = A_x`.

Since E commutes with both diagonal exception operators,

`E B_yᵀ E⁻¹ = A_x G_y`,

`E C_yᵀ E⁻¹ = G_x A_x`.

Thus the first actual supplier supports an input-Y exception in this upper orientation, and the second supports an output-X exception. These are the additional placements obtained by transpose, beyond placements proved only for the old inverse-transpose orientation.

If an interface requires the extra Q to be Q inverse, execute the ordinary square correction on the appropriate side:

`(A_x G_y) G_y⁻² = A_x G_y⁻¹`,

`G_x⁻² (G_x A_x) = G_x⁻¹ A_x`.

Here `G_y⁻²=diag(I,Q⁻²)` and `G_x⁻²=diag(Q⁻²,I)` are literal ordinary operators. The side of each correction matters; it is not commuted through `A_x` without proof.

One can recover the lower exchange by a bank swap and an ordinary diagonal gauge `diag(I,−Q⁻²)`. In that combined expression the two Q-square gauges cancel, leaving exactly the simpler `S B_yᵀ S=C_y` rule above. Keeping the upper-interface derivation separate prevents a gratuitous Gaussian request from being inserted into the lower exchange.

## 5. All-width meaning, cost and precision

The construction transposes a finite high-level program. It never forms the dense matrix of a payload operator. Each Gaussian query uses its retained transposed two-sided matcher and the same canonical Gaussian child; every monomial uses the supplied inverse permutation/phase word; scalar operations use the table above. The retained fixed-tape compiler can execute the finite reversed instruction list with freshly paid input/output, parking, restoration and head-return passes. No Word RAM primitive is introduced.

Every helper and child has exactly the same rank multiplicity as in the actual complete source. Owned field slots can be retained throughout; the transposed dataflow may have different lifetimes, so reserve the full declared bank rather than assuming a smaller cache schedule. Any extra temporary used by an ordinary implementation is explicitly owned, initialized and cleared, with no productive credit.

Transpose the entire physical ROW/spectator implementation, not merely an owner-index bitmap. An exact all-column identity `T⊗I` transposes to `Tᵀ⊗I`, so the same whole-row and spectator scope follows. Input/output adapters are transposed in reverse order with their real physical types. For normalized source boundaries `L T R`, the transpose is `Rᵀ Tᵀ Lᵀ`; all these ordinary words must be included. This is why no equality of old forward and new transposed internal headers is asserted.

Gaussian child phases are transposed, not conjugated. A fresh finite perturbation bound can use the product of `1+|c|` for the new scalar ADDs/SCALEs, the new ordinary-copy implementation, and the retained unitary child/monomial bounds. It includes both complete prefix and suffix effects at the chosen working precision. An old cancellation-sensitive coefficient bound is not silently reused. Every new ordinary fee is finite and width-uniform in the inherited primitive model; the complete compiler and eventual threshold must be refreshed before claiming a numerical κ.

## 6. Sufficient substitution consequence

Any actual complete B-type or C-type source admitted under the retained native/phase, all-column/ROW, canonical helper, precision and fixed-tape framework can therefore be supplied to a compatible caller in either of the exchanged placements above. Its own paid and productive histograms are unchanged. A caller must still match its actual `D,Q`, parent rank, physical port templates and positive helper normalizers. The theorem provides those transposed normalizers and paid finite adapters; it does not assume an unknown supply transformation.

This enlarges the available interface set of each actual source. It does not by itself prove that a particular heterogeneous caller is feasible or that its full moment is positive. Those are separate complete finite statements.

## Attribution

Retain the actual native-dual-supplier, orthogonal-restriction and main-interface constructions of Cao Yifan / intqwq, Cinna Davis and the credited native/helper/controller lineage; DaysSky, Nick Petalas and Ryanson Jonathan for quotient/endpoint work; Dugongue's transported-frame and typed-interface work; the exact Clifford and phase compiler; and all retained ROW, scalar, higher-moment, finite ordinary, precision and fixed-tape contributors. The old inverse-transpose interfaces are predecessors. This note contributes the explicit plain-transpose compiler with owned noninvertible instructions and the resulting actual exception-placement exchange. New prose is Apache-2.0, with substantial OpenAI Codex assistance. No numerical κ, formal verification or exhaustive priority claim is made.
