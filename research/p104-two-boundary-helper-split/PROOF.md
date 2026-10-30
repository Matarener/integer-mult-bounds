# Two boundary functionals for helper708

## Source and scope

This construction starts from PR5713 head
`a5348f7143f95fe0046b92b96172e30763c7d731`, package
`p104-temporal-updates`, canonical word SHA256
`32adce6656e49aa020d3e6317f1c45c11fccadeeb67a8d506172d101703d2138`.
Its source lineage and authors remain credited. The new construction changes
scalar dependencies and adds one independent public helper while retaining
every paid MOVE. It retains nine owned labels, eleven lifetimes and peak two.
All owned identifiers increase by one to make room for the new public field743.

The resulting word has744 independent public fields and nine dirty owned input
columns. Its canonical SHA256 is
`a1c8277189a811546bdc7b147d72e6a594504ff9585c9bf59a5681aa873abb01`.
The exact constructor and independent checks below are finite checks; the
publication verifier separately binds native maps, the complete caller,
ordinary allowances and the numerical pricing claim.

## Initial basis and retirement

Use the cut immediately after source event14330. Roles708 and154 share frame602,
of rank2. Let A be the scalar prefix, B its suffix, T=BA, e=e708, and define

```
a = e708^T A,        c = e154^T A / 2,
h = a+c,            d = B e708 = -2e126+2e188+e708,
k = h-e708^T.
```

Exact replay verifies that T has identity input columns and output rows for
helpers126,188,708. It also gives h708=d708=1, hd=1 and k708=kd=0. Every term of h has its
initial value at the empty frame. Its only main-input terms are
`(x154+x217)/4`. The covector c has zero coefficients on126,188,708.

Apply the ordinary initial basis change

```
Q = (I+(d-e)e^T)(I-e k) = I+(d-e)e^T-d k.
```

The first factor is implemented after the second:87 initial ADDs
`708 -= k_r*r`, then `126 -=2*708` and `188 +=2*708`. All operands share the
empty frame, and the main fields are read but unchanged. The identities
`hQ=e^T`, `Qe=d` and `cQ=c` follow directly.

At the cut, `708 +=154/2` restores exactly x708. Retire original708 at rank2.
A new independent helper starts in frame602 with arbitrary input z and replaces
every subsequent occurrence of original708. No subtraction of154/2 is applied
to this new helper, and no MOVE is inserted or removed.

## Output normalization at an existing meeting

Before retirement the transformed continuation value was `aQ=e^T-c`. Replacing
it by z injects `d*(z-e^T+c)` into the suffix. Combining this with TQ gives the
following three dirty full-frame values, with every other endpoint unchanged:

```
126 = x126 - 2*t,
188 = x188 + 2*t,
new = t = z-k+c.
```

The output nuisance is `g=k-c=a-e708^T`. It differs from the input nuisance k.
An independent backwards calculation expresses g using118 full-frame endpoint
fields. This provides a direct exact endpoint check, but the final program
uses the shorter current-version identity below.

Original708 has only one destination update after the cut:
`708 +=146/2` at source event17433, at frame127 of rank9. Because the original
endpoint is x708, the exact value of146 at that event satisfies
`g=-value(146)/2`. In the candidate the renamed update is event17523,
`new +=146/2`. Immediately after it, insert these three ordinary operations:

```
126 += 2*new
188 -= 2*new
new -= 146/2
```

The first two remove the126/188 defects at this point; later ADDs still build
their final values. The third restores new to z. Their order is
necessary: applying the inverse146 update first leaves errors at126 and188.
The literal suffix has no later source reads from126,188 or new, and no later
write to new. Later writes to126 and188 are only ADDs at frame127. Consequently
the first two normalizations commute with that suffix, and the source146 is
read at precisely its required live version. A separate covector check verifies
that this146 value is unchanged by the initial basis and raw-z replacement: its
126/188/708 input coefficients and its response to the cut perturbation vanish.

The pure constructor first builds the equivalent terminal normalization and
then performs this checked substitution: three early operations replace the
two terminal restorations plus118 final correction operations. No algebraic
search, historical-value assumption, or new transport is used.

## Complete signed invoice

The paid histogram is unchanged. Original708's H9 productive target is replaced
by its retired H2 target and the new independent helper's H7 target:

```
Delta paid = 0
Delta targets = H2+H7-H9
Delta(targets-paid) = H2+H7-H9 > 0.
```

For `H_r=r^t` and0<t<1, strict subadditivity gives `2^t+7^t>9^t`. Rank mass
is unchanged. The eighteen local calls multiply this delta by18. The complete
paid occurrence count stays66348 and the productive count increases to12976;
the complete rank surplus remains760. The extra independent helper's ordinary
routing and allocation costs are still charged.

The final local word has25546 events and scalar allowance221474. Its paid
histogram is `{1:2184,2:459,3:495,4:92,5:159,6:22,7:15}` and its productive
histogram is `{1:2,2:5,4:91,5:6,7:6,8:15,9:411}`.

## Finite verification

The pure constructor accepts only the pinned canonical source and returns
the exact final candidate plus a witness. The independent literal checker
verifies all753 arbitrary input columns, frames, owned initialization/use/clear
rules, both complete local histograms and the ordinary scalar count. A separate
backwards implementation verifies all753 transpose columns.

Ten actual mutations are rejected under ordinary Python and `python -O`:
missing retirement; either omitted early restoration; omitted or wrong-sign146
inverse; incorrect cleanup order; reinstated obsolete decoder; omitted owned
identifier shift; overstated old helper target; and wrong new helper boundary.

Independent agents separately derived the88-term h and118-term output
functional and checked the temporal simplification. These are independent
agent calculations, not independent human review or proof-kernel acceptance.
Prepared for flyingviper with substantial OpenAI Codex assistance. Apache-2.0.
