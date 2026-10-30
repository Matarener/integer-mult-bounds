# Native support and paid full-bank scans

Scientific base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
This is a transfer gate for a specified implementation model. It is not a
general linear-circuit lower bound or a new conditional kappa.

## Exact circuit model

Fix the number and relative volumes of the physical banks, independently of
the chunk size `f`. The complete state includes every arbitrary dirty helper.
Allowed elementary operations are physical monomial maps, nonzero scalar
maps, bank permutations, binary scalar bank additions, and native children.
A native child of actual arity `r` has at most `2^r` nonzero entries per
physical matrix row. An ADD is one literal `destination += c * source`,
with distinct banks, not an unpriced operator-valued coefficient.

Suppose a required coefficient block of the complete map has exactly
`2^(c*f)` nonzero entries in a row. Let `A(f)` be the sum of the actual
arities of all native children and let `S(f)` count the binary bank ADDs.
Then

```
A(f) + S(f) >= c*f.                                      (1)
```

Start with the identity matrix on the entire bank-by-address state, whose
maximum row support is one. A monomial or scalar operation does not increase
this maximum. A binary ADD increases it by at most a factor two; a native
child of arity `r` increases it by at most `2^r`. Multiplying these bounds
proves (1). Cancellations only decrease support. Extra arbitrary dirty banks
and their subsequent restoration do not affect this argument: they were
included in the initial identity. No norm or bounded coefficient assumption
is needed.

## Full scans cannot absorb a linear arity shortfall in the retained transfer

In addition assume that each counted ADD is executed as a full scan of a
physical bank containing at least `delta*V` records, for a fixed `delta>0`,
and costs at least `a*delta*V` elementary steps, with fixed `a>0`. These are
implementation assumptions, not conclusions of row-support algebra.
If `A(f) <= (c-epsilon)*f`, with a fixed `epsilon>0`, then (1) forces
`S(f) >= epsilon*f` and the ADD work alone is at least
`a*delta*epsilon*V*f`.

The retained integer-width transfer uses `f=floor(e/m)`, with fixed `m`.
For `e>=2m`, `f>=e/(2m)`, so this work is `Omega(V*e)`. It cannot satisfy
`O(V*e^lambda)` for any fixed `lambda<1`; the ratio grows as
`e^(1-lambda)`. At a root whose active width is a positive fixed fraction
of the outer width `d`, the same argument excludes `O(V*d^lambda)`.
It is enough to count the root work; no recursive-tree lower bound is
assumed.

More generally, a sublinear full-scan cost requires `S(f)=o(f)`. Thus (1)
implies `liminf A(f)/f >= c`. For a fixed native profile `A(f)=R*f`, the
necessary condition is `R>=c`. Stopping recursion at `e<d^beta`, `beta<1`,
does not remove the root charge for unbounded root width.

## Conditional application to the separate-pivot J prefix

The new physical prefix has `n=2q+2`, `m=4q+4` and native mass
`n*m-2q`, for fixed `q>=2`. The independently derived coefficient identity
in `../joint-native/GENERAL-SOURCE-PROOF.md` proves that its required
pivot-to-output coefficient has row support at least `2^((2q+4)*f)`.
The proof's SHA-256 is
`464bfd5ff9c9d8ef1270b1379361d13d42da452b8236ba73e97dd318e83b9778`.
Thus (1) applies with `c=2q+4` to every cleanup of
that exact prefix and target, including cleanup that mixes both pivots
with all public outputs and arbitrary dirty helpers.

In the full-scan transfer model, an admissible fixed cleanup profile must
have unweighted native mass at least `2q+4`. To turn this support bound
into the following moment comparison, also require the retained
equal-volume, full-bank native-child normalization: every counted native
operation acts on a full bank of the same volume and is charged one unit
in H, with the prescribed child volume V/W. Extra queried dirty helpers
must use that same normalization. The unweighted support inequality alone
does not imply this volume premise. Under these combined assumptions the
complete native mass is at least `n*m+4`, above the full-output stock
`n*m`. For proper child ranks
`0<r<m` and any `0<b<1`,

```
sum H[r]*(r/m)^(1-b) >= sum H[r]*r/m > n.
```

Consequently that fixed-prefix completion cannot have a favorable moment
under the inherited full-output stock convention and the explicit full-scan
premises above. This uses a written coefficient/gauge identity, not a claim
that a search found every possible word. The coefficient identity covers
arbitrary source monomials and any response J with J squared equal to -I
and the stated full-support target; its fixed scalar core, diagonal
continuation and separately exposed query sites remain hypotheses.

## Source binding and boundaries

* `notes/batched-bit-rows.tex` fixes finite circuit constants, child volume
  `V/W`, chunk `floor(e/m)`, and a constant normalized local toll.
* `notes/batched-complex-rows.tex` retains that chunk shape, exact child
  volume, stopped-tree exponents and a final layer exponent below one.
* `references/semantic-bulk/rad20/reports/review-whole-complex-transfer.md`
  states the volume-weighted proper-child moment and keeps fixed phase
  scans in the constants; a growing scan count cannot be placed there.

The argument does **not** exclude a changed physical prefix, changed
input/target chart, different endpoint credit, cross-cut retiming, scans
on a vanishing fraction of the volume, a fused algorithm whose work is
not the sum of the declared full scans, or a different transfer theorem.
Such a proposal must give its actual complete operation and volume bill.
Unequal queried-bank volumes require their actual volume-weighted moment;
no unweighted mass-to-moment conclusion for that case is supplied here.
An abstract count of `O(f)` ADDs alone neither admits nor excludes an
implementation outside this model. No compatible BIT result, precision
proof, native controller or stronger kappa is supplied here.

Apache-2.0. Substantial OpenAI Codex assistance. The retained transfer and
its source attribution remain with their original authors; this note
isolates the additional full-scan consequence of the support inequality.
