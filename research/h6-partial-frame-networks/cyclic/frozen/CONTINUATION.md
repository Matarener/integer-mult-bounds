# Full root-product tiling and a partial-centre substitution

Local continuation after the first area7 handoff, on the original parent
clock and scientific pin `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
**No new kappa.** The results are a concrete disjoint full root-product
tiling with its exact residual, and two fully specified partial-frame
substitutions for eight existing K centres. The parent requested both bounded
constructive checks. This document extends `EXTENSION.md`; it does not change
the scope of its positive finite words or sharp odd-Gram theorem.

## 1. An actual tiling of all28800 root-product ports

`module_tiling.py` stores an exact partition of the120 canonical a-root lines
into40 acute triples, with signs sigma_i making every inner product within
each triple +1. It also constructs an explicit orthogonal involution of all
120 b-root lines: for an integer D8 root, flip its second nonzero coordinate;
for a spinor root, flip coordinates4,...,7. This gives60 disjoint orthogonal
b-pairs. For each a-triple, b-pair and epsilon=+-1, use the six actual ports

```
(a_i,epsilon*sigma_i*b_z), i=0,1,2, z=0,1.
```

There are4800 disjoint r3 modules. Their product source IDs cover exactly
2160,...,30959, once each. Both pure1080-port blocks, IDs0,...,2159, are
untiled. The module coefficient is the sign conjugate of the actual cyclic
matrix from `dynamic_cyclic.py`. Every one of the172800 within-module ordered
pair coefficients is checked against `I-(t^3-4t)/48`. The2400 distinct binary
frame cases are checked for rank2 input planes, rank3 final arcs, actual cap
inclusion and nested source visits. The two epsilon variants have the same
binary frames. Reader input and output signs are charged unit scalar signs.

Let D be the block diagonal sum of these module compensations. Exactly115200
ordered nonzero entries of C=I-K are handled:57600 of absolute coefficient
1/16 and57600 of absolute coefficient5/16. The exact residual set is

```
{(t,s): actual Gram(t,s) is odd,
         t and s are not in the same six-port module above}.
```

The pinned exhaustive full-H6 pairing receipt then gives480222720 residual
ordered entries, consisting of476916480 unit-numerator entries and3306240
exceptional entries. This set specification and the explicit module partition
are exact; the residual dense matrix is not stored or billion-entry replayed.

### Complete local completion, with its actual cost

There is a legal complete local word using the existing residual edge helpers.
At ZERO precompensate the dirt of full K, the module readers and the residual
helpers. Load each residual helper from its original source at that source's
initial line. Then execute the disjoint mutable module gathers and move all
sources to FULL. Run the unchanged816-centre K while targets remain ZERO.
Deliver each module at its rank3 final arc, then finish every target cap climb.
Each residual helper advances from its source line to its rank16 target cap
and scatters there. All helpers finish at FULL and subtract their original
source accumulations. The usual same-order dual and separate dual K private
episodes give the transpose inverse.

Thus the complete logical map is y+=(K+D+(C-D))x=y+x, with all ordinary dirt
restored. This is a specified and counted full-domain stream, not an emitted
or executed billion-event fixture. The old exact factor and all-pair support
certificates are inherited at the scientific pin. New phase/adapter, bank,
controller, precision and all-size admission are absent.

The local native paths are source[1,1,14], target[3,13] and reader[2,1,14]
for tiled ports; pure data have their coarse[16] residual paths. The residual
edge readers have[1,15,1]. There are28800 module readers plus480222720 residual
edge readers, total480251520 ordinary compensation roles. All816 ordinary K
roles and separate private C=13872 remain paid. Every pad and idle term is in
the L5 full histogram. Its .002 normalized moment is
1.00396149237658136716079: this construction fails the requested target.

Complete scalar component work is11794300560 forward and11794303008 dual,
before real/imaginary doubling. It saves1209600 component primitives against
the old all-edge word by replacing115200 edges with28800 changing readers.
This is a concrete finite local saving on an extremely expensive fallback;
it does not establish a useful supplier improvement or large kappa jump.

### Residual rank budget

For these exact modules every restricted K block is invertible. Therefore
`rank(I-D)=30960`, including the untiled pure blocks. Since rank(K)=816,

```
rank(C-D)=rank((I-D)-K) >=30144.
```

If all residual information instead crosses a private-return interface, even
ideal rank1 episodes cost at least30144, giving total private C>=44016. The
coverage deficit is at most `-30960-13056L`, negative for every L. This is a
private-return contract result, not a bound on ordinary mixed residual readers.

Even arbitrary coefficient redesign within these disjoint r3 blocks cannot
make that particular private-residual approach meet .002. A module correction
has zero own-group2x2 blocks, so its I-D block contains I2 and has rank at
least2. Thus globally rank(I-D)>=2*4800+2160=11760, and residual rank>=10944.
Granting free residual banks and rank1 copies, total C>=24816. Active data
alone obey pressure/(NL)>.064 log L. The global minimum over L>0 of
`.064 log L+1/L` is `.064*(1+log(125/8))`; the exact rational lower interval
exceeds `1-24816/30960` by0.0414782081167369973214388. Hence every L fails
that favorable private-residual invoice. Overlapping/composed modules and
mutable ordinary residual networks are outside this argument.

## 2. Eight actual K centres gathered at a partial frame

`partial_pauli.py` chooses one actual traceless diagonal Pauli group from
the retained evaluator, columns120+44i for i=0,...,7, with weight1 and
denominator8192. On doubled root-product coordinates,

```
q(b)=sum_j (-1)^(j&1)*b_j^2,
E_i(a,b)=a_i*q(b), K_P=E E^T/8192.
```

All pure-port rows of these columns vanish. Exactly24 canonical b-lines
have q!=0, with q=+-8. Their two signed copies and all120 a-lines give5760
supported ports. Each feature has3744 nonzeros:3072 of absolute value8 and
672 of absolute value16. The actual17-bit support spans U of rank15.
Its orthogonal complement W=U-perp has rank2 and lies inside U; the support
frame is degenerate with a two-dimensional radical. All supported target caps
contain W. These complete support and inclusion statements are exhausted by
standard-library exact arithmetic and saved as literal bases in the receipt.

Allocate the same eight ordinary dirty centres c_i already charged in the
full K word. At ZERO perform `y_t-=E_ti*c_i/8192`. Supported sources climb
from their rank1 lines to U, paying14; the centres climb ZERO->U, paying15.
At U gather `c_i+=sum_s E_si*x_s`. The sources then reach FULL, paying2.
The other808 K centres retain their full-width words, and all of their ZERO
scatters precede the target moves described next.

There are two concrete private output interfaces:

1. **ZERO output:** copy c_i at U, descend U->ZERO paying15, scatter
   `y_t+=E_ti*private/8192`, erase the private stream. Targets then make their
   normal[16] climbs. Full private K bill is13856, a saving16.
2. **Radical output:** supported targets first climb ZERO->W, paying2. Copy
   c_i at U, descend U->W paying13, scatter the same coefficients, erase.
   Those targets finish W->Q_t, paying14. Full private K bill is13840,
   a saving32. Unsupported targets make no W visit.

In both variants each ordinary c_i finally climbs U->FULL, paying2, and
subtracts every original gather at FULL. Sources are unchanged. The arbitrary
dirt cancellation is exactly

```
y -= (E/8192)d;
c = d+E^T x;
y += (E/8192)c;
c -= E^T x,
```

so y+=K_P x and all c are restored. The private streams are independently
cleared, copied, descended, scattered and erased. In the same-order dual,
the private stream starts at the output frame, gathers E^T y/8192, ascends
to U, subtracts from c and erases there. The endpoint is x-=K_P^T y.

This substitutes exactly the same eight feature products in the full
factorization. It does not change the cubic kernel or invoke the odd-Gram
rank theorem. The19 actual-port diagnostic contains a rank15 support witness,
all eight feature columns and zero-feature ports. It checks every one of46
ordinary input columns in both variants/orientations, with26 meaningful
omission/frame controls. The all-supported-input identity follows from the
displayed factor product and frame inclusions; the full5760-port matrix is
not densely replayed.

### Complete tariffs and precision boundary

The two variants add no ordinary centre roles or helper pads. Each selected
ordinary centre has path[15,2], instead of[17]. Supported sources have
[14,2], instead of[16]. The ZERO variant has private[15], instead of[17].
The radical variant has private[13] and additionally supported target[2,14].
All scalar arithmetic is unchanged: the selected group costs1258008 forward
and1258032 dual component primitives. Full K retains247217040/247219488.
Every clear, copy, weighted add and restoration is included.

The selected subword's exact full-support logical prefix maxima are35329
forward and152 dual, denominator depth10. Forward centre rows attain
`1+3072*8+672*16=35329`. Dual source prefixes are exhausted by the120 actual
a-roots and the nine coordinate-prefix lengths; the maximum is152. This is
a logical subword range receipt. The full composed network's coefficient
temporaries, physical frame norms and approximate-child error bounds remain
unproved.

The private saving alone does not improve the full moment when its data
visits are newly paid. Relative to the same stock, ordinary role count and
all other unchanged costs, exact `Delta(pressure-D)/L` at m49 is:

| Target k | ZERO output | Radical output |
|---|---:|---:|
|.002|+53.7998503674671|+107.496538804777|
|.003|+88.8945552815504|+177.634095887455|
|.005|+159.475575170436|+318.691883815945|

Positive means worse. This sign holds for every arity: stock is unchanged,
the complete rank difference is minus the private saving, and

```
Delta(pressure-D)/L = m^b * sum_r DeltaH_r*r^(1-b).
```

The coefficient is independent of m; the exact positive interval at m49
therefore proves the sign for all L. Both ordinary-centre and private-copy
terms are present. It is not a floor derived merely from the unsplit feature's
support span, and no general splitting/factor-network lower bound is claimed.

The substitutions are useful if a compatible dynamic network already pays
the very same U visit, and in the second variant the same W target visit.
Under that explicit sharing premise, .003 gives negative differences
-15.8570913817969 and-31.8691974392400 per L, respectively. No compatible
global transport sharing is constructed here. Distinct Pauli support frames,
source updates and overlapping feature decompositions require fresh geometry
and accounting rather than multiplying this isolated saving.

## Reproduction and review

```
python3 -I -B module_tiling.py
python3 -I -O -B module_tiling.py
python3 -I -B partial_pauli.py
python3 -I -O -B partial_pauli.py
```

Normal and optimized executions passed. Independent specialist review of the
Pauli words also passed in `../recursive/PARTIAL-PAULI-REVIEW.json`: a separate
actual-geometry fit,18-port arbitrary-input fixture and independent power
intervals reproduce both variants and all six moment differences. The
review binds producer SHA256
`774d876402be6066121a982f0c149b924b53c72bc53f6bfd13d96f751600b8bd`.
The parent separately records in `../PAULI-FIXED-SUPPORT.json` that the35
traceless quadratic directions restrict with rank34 on the96 complementary
root lines; this fixed support cannot simply share a second independent
quadratic direction. That is a finite fixed-support statement, not a general
feature-network bound.

The final constructive source-interface question led to the independently
reviewed theorem in `SOURCE-SMITH.md`: det(C) has odd factors, exactly560
physical rows admit algebraic unit repair, and a560-direction stable
completion must carry changed outputs and arbitrary helper dirt. This does
not code the current native K response, whose rank816 instead requires at
least30144 repairs. A new cheap complement producer and all physical coding
costs remain missing. Final optimized receipts and independent specialist
review bindings are recorded in `HANDOFF.json`. Main/protected source
checkouts remain unchanged; no public action, commit or push occurred.
