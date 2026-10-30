# Bounded proof review: active-fiber Hilbert sharpening

This reviews the proposed corollary only. The active-fiber unitary method is
credited to Ross Richardson / Adam Gall and the retained
`research/p104-retimed-internal-grid` lineage. It is not a new method or a
proof of the five framework premises. The new binding concerns the actual
735-input complete P104 word, COPY residuals, all intervals and whole caller.

Fix a spectator address and let each active fiber have complex dimension
`D=2^(d f)`. For the state use **maximum individual-field Hilbert norm**,
`H(z)=max_r ||z_r||_2`. Do not use joint l2 over all fields. For coordinate
norm `C(z)=max_{r,a} max(|Re z_r(a)|,|Im z_r(a)|)`,

`H(z) <= sqrt(2D) C(z)`, and `C(z) <= H(z)`.

If a complete interval has maximum-individual-field Hilbert norm at most L,
its coordinate norm is therefore at most `L sqrt(2D)`. This uses only one
fiber conversion, on the input. There is no factor from the number of
fields, helpers, or spectator addresses. An integer power-of-two upper bound
is `L 2^ceil((d f+1)/2)`.

For a local scalar/gauge interval, each field block has the form
`A_rs Psi_out,r Psi_in,s^-1`. The normalized native C factors and their
canonical P/D/X/phase factors are unitary. At an interior native cut the
current Psi is a partial native recipe times the previous canonical frame,
also unitary. Thus the block has Hilbert norm `|A_rs|`; the maximum absolute
scalar row sum bounds H on the whole interval. The previously proved
LambdaP / LambdaS / Gamma estimates consequently acquire no native N-power
in H. For local component estimates apply one conversion with d=9.

For the whole caller, a complete or partial local module costs at most
Gamma=2^296 in H. An ADD costs at most 2 in H, even for different field
gauges. All native factors, routes, signs and whole IDLEs are isometries.
An owned copied-query schema costs at most 4 from its COPY-ADD and target
ADD, including arbitrary injected owned residual; its Q_f and partial
native factors are isometries. INIT/CLEAR are contractions on owned state.
The owned query stream must be cleared between ports, retaining the
declared block/ownership separation. No joint-l2 copy-isometry is asserted.

The checked counts therefore give the whole-caller interval H bound
`2^(486+2*15) Gamma^18 = 2^5844`. Every truncated module has the same upper
bound as its full module, and all such majorants are at least one, so their
full product bounds intervals beginning or ending inside modules. The
explicit 265-axis chart/route support gives, conditionally on that declared
support, the coordinate interval corollary

`2^(5844 + ceil((265 f+1)/2))`.

Axes outside those 265 f coordinates must truly be fixed spectators; no
claim that arbitrary additional active axes are free is made. Different
modules may use different active subspaces inside the same 265-axis fiber.
The argument does not require a common smaller fiber across modules.

The unitary cut statement applies after a complete C factor or complete
butterfly pair. Updating only some disjoint pairs is also a direct-sum
unitary. An accumulator halfway through computing a real output component
is not itself one of these field cuts and retains its separate fixed local
arithmetic guard. The earlier coarse component bounds remain valid.

Conclusion: the proposed sharpening is mathematically sound at the declared
field/native-C-factor cuts, with the stated inherited native and ownership
contracts. It does not establish recursive internal precision or runtime,
uniform physical stock/tape bounds, scientific acceptance or a new κ.
Prepared for thu-nmrc with OpenAI Codex assistance, Apache-2.0.
