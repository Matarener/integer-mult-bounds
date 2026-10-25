# Read-only mathematical cross-review of the hybrid controller

**Verdict: PASS within the stated abstract and conditional scope.**
No actionable mathematical error was found in the all-B tail proof, the
two-code construction, the restricted determinant lower bound, the direct
forward VALUE witness, or their presentation in the staging README.
This is a separate AI mathematical reading, not human acceptance or a
formal-kernel proof. No full replay was run during this cross-review.

The reviewed source hashes are:

| File | SHA-256 |
| --- | --- |
| `b07-hybrid-review/PROOF.md` | `3f90c6c169d48b567ba1d406db058662cf18d1ca823acb5bdc18e16d180db732` |
| `b07-hybrid-review/check_hybrid.py` | `148b456444486d4fde75c83d20717aef7dcd2c6aef31adb009035f834c530138` |
| `b07-hybrid-review/REVIEW.md` | `367f780480a09cfe25f34fa28b44132cfa91d61d51d1fdb43b496110ffd318d1` |
| `b07-staging/README.md` | `5b97d9f6261ec3c6a6bc4b5da69bc8fba503a36fb71b31f54b3e227480aac623` |

## Clean-tail induction

I independently expanded the ladder operations with their signed dual
bridges. On pair zero, the positive bridge, clean forward local and negative
bridge leave `(U,U+V+x1)` and present pair one as
`(x1,y1+U+x1)`. For later pairs the incoming second bank is
`yj+s(j-1)+xj`; the reverse local sets its first bank to
`sj=-yj-s(j-1)`. The next forward local and opposite bridge pair leave
`(sj,xj+x(j+1))` and propagate the same incoming formula to the next pair.

In the descending return ladder the source `sj` has not yet been changed,
while the next pair's second bank already equals `x(j+1)`. Consequently the
new first bank is `s(j+1)+sj=-y(j+1)` and the second-bank telescoping removes
exactly `x(j+1)`. Pair zero ends `(U,U+V)` and all other pairs end `(-yj,xj)`.
The B=1 case is a single clean forward local. The induction therefore covers
every B>=1 without using a finite list as an extrapolation.

## Two-code correction and lower bound

The fixed coded prefix gives `U=-y0` and
`V=a1^-1(y0+a0*x0)`. The tail gives `X0=U, Y0=U+V`.
The four displayed terminal steps send Y0 through V, `y0+a0*x0`,
`a0*x0`, and x0, while X0 remains `-y0`. No code labels were commuted in
this calculation. The unchanged exchange closes every input bank.

The determinant argument is taken only after the valid commutative
specialization to Q(t,u); no determinant over the noncommutative group
algebra is presumed. The fixed prefix has factor t/u and the fixed target
requires added factor u/t. Under the declared single-bank primitive alphabet,
each extra occurrence changes at most one independent exponent by one.
Thus at least two occurrences are required, and the construction attains it.

The argument is an optimum for universal words in that independent-generator
alphabet. It is not an optimum for one specialized pair of physical codes
that could satisfy additional relations, and not a scalar-ADD or physical
frame-normalization lower bound. The proof and README keep those boundaries.

## Direct VALUE orientation

The relevant convention is ADDRESS push T and VALUE push
`g(w)=f(T^-1*w)`. The source function `f(w)=1[w10=0]` on F101 addresses
is constant under translation by every source P0 root-line vector, since
those vectors have zero fresh-coordinate component. The recorded inverse
route sends the target P3 vector `2e3` to `2e10`; hence
`g(0)=1` and `g(2e3)=0`. This directly violates target P3-line invariance
in the required source-to-target direction.

The separate forward route and pullback separator are useful dual checks;
they are not substituted for the direct VALUE push argument. A point delta
is not assumed to be an admitted source quotient function. Reading the
selected route code confirms that it constructs both route orders and
checks the inverse relation and the exact inverse image. The reported
native obstruction remains one selected ordered off-diagonal pair.

## Conditional cost and native boundary

The scalar arithmetic `9216-3220=5996` is correct at the same declared
1499-ADD code tariff and 111-ADD bank-shear tariff. The two words have the
same two declared normalization sweeps. The comparison
`2*60-222=-102` remains negative and independent of B under the stated
equal-price owner-return premises.

The proof does not infer native legality from abstract endpoint equality.
Its normalization controls explicitly distinguish the unchanged algebraic
endpoint after deleting a logical identity from the failed native inventory.
The common terminal FULL cut, legal current frames, mixed owners, helpers,
physical source access, actual integer target leakage and precision remain
separate premises. The README also preserves the B=1 algebraic versus native
driver distinction and does not turn the scalar saving into a supplier or
kappa claim.

Only this cross-review file was written. No frozen contribution files,
staging content or other worker-owned material was changed.
