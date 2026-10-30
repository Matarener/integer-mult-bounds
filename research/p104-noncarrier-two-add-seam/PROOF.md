# Two ADDs across the 572 seam cannot restore the outside outputs

This is an exact finite exclusion in the rational scalar model of the selected
PR6030 word. It is not a new supplier or a universal P104 obstruction.
All event indices are zero based, and a window is immediately **after** its event.

## Domain

Keep the complete prefix, original event schedule, charts, fields and owned
lifetimes. Immediately after event 13637 (`COPY 778 <- 572` at chart 595),
replace field 572 by a new independent input `z`. The displaced original row is
`ell X`, where `X` consists of all 770 arbitrary original public inputs.

Insert precisely these two ADD opportunities (a zero coefficient is allowed,
so the exclusion also covers using fewer than two):

1. After any event `i` in 13637..13651, add `a * field_u` to `field_v`, with
   distinct `u,v` in chart 595. Its six roles are
   `[127,572,581,582,731,778]` throughout these windows.
2. After event `j` in `{13652,13654,13655}`, add `b * field_s` to `field_r`,
   with distinct `s,r` then at chart 603. The banks are respectively
   `[572,740]`, `[572,740]`, `[572,709,740]`.

Both coefficients may be arbitrary rationals. Sources need not be carriers:
these operations may temporarily change original `X` rows. Event 13652 is the
unchanged MOVE of 572 from 595 to 603; event 13654 adds `-572` into 740;
event 13655 brings 709 to 603. CLEAR 778 at 13656 also stays unchanged.

Let `V=127`, the original final chart of 572, and let `O` be the 186 public
roles whose final chart differs from V. The required necessary condition is
that **every O output equal its original unsplit output for every X and z**.

**Result.** None of the `15 * 30 * (2 + 2 + 6) = 4,500` location pairs can
meet that condition. This holds even if erasing z completely were permitted.
Consequently none can supply a legal split with a nonzero V-final z target.

## Exact endpoint polynomial

Use row vectors for input functionals and column vectors for final public
outputs. Let `R_i` be the original prefix at window i and `S_i` the original
public suffix. Let `beta_i` be the propagation, through original events, of
the unit vector placed at 572 at the overwrite. Set

```
e = z - ell X
D = S_cut e_572
A = S_i e_v
B = S_j e_r
b1 = (beta_i)_u
b2 = (beta_j)_s
g = (T_{j<-i})_{s,v}
f = (R_i X)_u + b1 e
h = (R_j X)_s + b2 e
```

Here `e_572,e_v,e_r` are state-coordinate unit vectors; `e` without a
subscript is the scalar functional `z-ell X`. `T_{j<-i}` is the unchanged
intervening linear program. The first source's value is f. Its update changes
the second source's value from h to `h + a*g*f`. Linearity of the retained
suffix gives the complete final public difference:

```
D e + a A f + b B h + a b g B f.                         (1)
```

This includes original-input defects as well as the z coefficient. It does
not assume that either correction has zero original value. Neither does it
linearize around zero coefficients or discard the interaction term.

Introduce independent rational unknowns `(a,b,c)` in place of `(a,b,a*b)`.
For each outside output and each input column (including z), setting (1) to
zero is a linear equation in these three unknowns. Every actual two-ADD
solution would solve this **more permissive** system with `c=a*b`.
The verifier proves all 4,500 relaxed systems inconsistent. No bounded
coefficient search, root-finding or unproved quadratic-solving step is used.

## Certificates and coverage

The checker authenticates the selected compressed word against SOURCES.json,
replays its exact rational rows and live charts, and constructs reverse public
suffix columns. The complete forward endpoint and reverse transpose agree;
all original owned rows restore and their lifetimes end. This authenticates
the scalar data used here, not the selected native implementation.

For each of all 4,500 location pairs, sparse elimination records a rational
linear combination of original protected-output equations whose left side is
zero and right side is one. A separate checker recomputes the selected original
equations and verifies those dot products directly, without row reduction.
There are 4,262 one-equation and 238 two-equation contradictions. The canonical
certificate transcript SHA-256 is retained in RESULT.json; every replay
recomputes and checks every certificate, not merely its digest.

For example, the first pair is
`(i,u,v,j,s,r)=(13637,127,572,13652,572,740)`. A contradiction uses output 120's
original input-column equations 0 and 34 with multipliers `-2` and `1`.
The exact right-side sum is 1 and all three unknown coefficients sum to zero.
The literal coordinates and multipliers are in RESULT.json.

Independent literal whole-word execution checks four parameterized production
cases against (1) on **all original input columns and the new z column**.
These include a nonzero interaction term, a correction using 778, a first
update before the ADD into 582, and a changed original row. The literal engine
has its own event loop and row arithmetic, separate from the prefix/suffix
engine. This is implementation cross-checking by an AI-assisted contributor,
not independent human or formal-kernel acceptance.

A synthetic changed-boundary fixture admits a two-ADD non-carrier repair; the
checker does not reject every model by construction. Moving 572 to the wrong
chart is rejected at its actual consumer, and a forged dual is rejected.

A particularly relevant false positive is `127 -> 572` with coefficient 1
after 13651, followed by `740 -> 572` with coefficient 1 after 13654. Its
outside z-leak is zero and z survives publicly, but its outside original-X
rows are wrong. The full equations reject it. This demonstrates why a z-only
check would not settle the claimed question.

## Scope boundary

PR6067 and PR6069 cover corrections that preserve the original scalar rows at
each completed atomic carrier update. Their results do not imply this one:
we allow non-carrier sources and change original rows between two different
charts. Conversely, this package covers only the stated two-ADD locations.
It says nothing about three or more ADDs, different later windows, changed
prefixes, non-unit injection, new routes/storage or changed scheduled events.
It does not audit either predecessor's complete proof or census.

The necessary scalar condition already fails. Therefore no candidate reaches
pairing, productive targets, owned-restoration after a successful edit, native
realization or full paid/ordinary/compiler/outer pricing. Those checks are not
silently counted as passed. The selected word, its five framework assumptions
and kappa remain unchanged.

Prepared for **JoyboyBrian**, with substantial OpenAI Codex assistance.
Apache-2.0. Credit apoursh (PR6067), Jonathan Capalbo (PR6069), JosieElliston
(PR6045), Nick Petalas (PR6040), Matarener (PR5994), flyingviper (PR5718),
Ali Romman and DreamingOfClouds (selected P104 word), and their retained lineage.
