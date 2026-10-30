# A late active injection: restoration obstruction and conditional repair

This checkpoint gives an exact scalar information test for a specified active
injection. It does not rule out active feedback in general, implement a new
physical transfer, or improve the multiplication bound.

## Frozen interface

Use the retained `F9-SOURCE-DAG-ALL8-WORD.json.gz`, SHA256
`934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775`,
backward direction, omitting its unimplemented `physical_add` events exactly
as the retained observer probe does. The independent inputs are 112 X fields,
112 Y fields, and 408 arbitrary helper fields H. All owned scratch is separate
from this 632-dimensional input inventory.

The test cut is immediately before word event 17978, original source event
17155:

```
['climb', 'scalar_refactor', 240, 280, 1, 1]
```

L240 is then in rank-eight frame 280 and climbs to the unique full frame 1.
Evaluate address operators on their common fixed vector. This retains every
original input coefficient while giving a necessary scalar observer quotient;
it is not a phase-aware physical replay.

Write R for the retained 8 by 112 mode matrix, with `R R^T = 56 I`, and
`A = I - R^T R/4`. The exact scalar baseline endpoint is

```
X -> X - A Y,       Y -> Y,       H -> H.
```

## 1. An active injection does not supply a clean extra observation

Let M consist of all chronological full-frame snapshot rows on the 632
original inputs. Let v record each snapshot's response to a unit injection
into L240 at the stated cut. Grant a missing mode m at that cut without
claiming that it can physically be supplied there. The changed snapshots
are `M' = M + v m`, not a collection containing both original and modified
versions of each affected snapshot.

For m outside `row(M)`, pure m is in `row(M')` exactly when some q satisfies
`qM = 0` and `qv != 0`. Such q extracts m, after which every original snapshot
can also be recovered. Conversely, any extraction must satisfy these two
conditions because m is outside the original row space. Equivalently,
`rank([M|v]) > rank(M)` is necessary and sufficient.

The exact replay finds 4868 distinct full snapshots and

```
rank(M) = rank([M|v]) = 482.
```

Every one of the eight RY modes lies outside `row(M)`. The saved certificate
provides a 104-term z and checks `Mz = v` directly on all 4868 rows. Therefore
the changed row space is the graph `r -> r + (rz)m` over the old row space;
it contains no pure m. The coefficient of the original helper endpoint e240
is `e240 z = 1`, so that original independent helper is not restored by
declaring the changed value a clean mode observation.

For `m5 = R5 Y`, a second directly checked certificate has

```
Mu = 0,   m5 u = 1,   m5 z = 0,
a = u-z,
(M+v m5)a = 0,   m5 a = 1,   e240 a = -1.
```

This separates both the pure mode and the original helper240 target from
all allowed changed observations. It is an exact certificate, not a modular
no-hit or a failed coefficient search. An invertible change of independent
helper coordinates preserves this information test.

## 2. Why the fixed full-frame sink gives a larger scoped obstruction

Metadata verifies that exactly 482 persistent roles enter the full frame,
each once; none leaves it. No owned scratch reaches the full frame. After
entry, full-frame updates are nonaliasing ADDs and nonzero SCALEs, with no
copy, clear, or non-full scalar source. The 72 full-frame warps act as the
identity in this fixed-vector quotient.

Consequently every recorded full snapshot is a fixed linear combination of
the 482 final full coordinates: `M = S F`. Reverse the invertible full-frame
updates to obtain S, leaving newly arriving coordinates unused until their
arrival. Final observations show that S has full column rank. The same S
applies if only lower-frame histories before first full arrival change.

The 482 baseline final rows F have distinct X/helper pivots. The eight RY
rows have only Y coordinates and rank eight. Thus their row spaces intersect
trivially and `rank([F; RY]) = 490`.

Suppose a family of added controls changes the full endpoint only by fixed
missing modes, so `F' = F + V(RY)`, while the full sink interface remains
unchanged. If `aF' = b(RY)`, independence gives `aF = 0`, hence a=0 and b=0.
No nonzero pure missing mode can then be extracted from any number of these
modified full-frame snapshots. This covers multiple fixed-mode injections
inside that interface, not arbitrary feedback words or changed source
alphabets. Feedback carrying other original input combinations, new full
ingress, saved independent owned data, new address maps, or changed target
inventory is not covered.

Most importantly, this theorem does not prohibit direct repair of the main
endpoint. A successful construction can change F to the desired target
without ever exposing a separate pure missing-mode observation.

## 3. A direct one-mode repair is algebraically consistent

The unit L240 impulse has final main coefficient `+R5^T` and helper
coefficient `+S5`, with 56 and 48 nonzero entries respectively. This agrees
with the retained center5 suffix data; that helper cleanup was already known.

The source already captures `c = R5 Y/4` in ground-frame owned C6 at events
511--567. At events 568--615 it applies `H -= S5 c`. C6 is unchanged through
the tested cut. Conditional on an oracle injection `L240 -= c`, omit those
48 existing helper precompensation ADDs. The resulting effects are

```
main:    -R5^T c,
helpers: -S5 c + S5 c = 0.
```

An independent direct replay verifies every coefficient in all 632 endpoint
rows, all 408 helper identities, all final charts, and every owned zero:

```
X -> X - A Y - R5^T R5 Y/4,       Y -> Y,       H -> H.
```

There are no downstream warp events after the named climb. Once the
required field reaches full frame 1, its remaining propagation is therefore
the displayed scalar suffix impulse. The payload supplied in frame 280
must transport through the selected climb to that required field. The
fixed-vector calculation does not establish this physical availability.

Indeed C6 is in frame 0 while L240 is in frame 280. The literal ADD between
them fails the ordinary coframing validator. The conditional identity is
therefore a target for a new routing or dependency construction, not an
unpaid legal edit or a claimed improvement.

## Distinction from retained passive exclusions

The retained `CORRECTIONS` and observer work study corrections built from
the unchanged history. Here the snapshots themselves change: the extra
response column v and all helper targets are tracked after a granted active
injection. The result adds an exact restoration certificate for this cut and
a fixed-mode extension under the verified full-sink interface. It does not
reprove the source-DAG helper compensation, supersede broader physical
semantics, or turn either the old passive exclusions or this scoped theorem
into a prohibition of active feedback.
