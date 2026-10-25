# Whole K_odd: independent scalar/common-frame proof

The proposed K-only interface is valid. It needs no algebraic helper bank,
COPY, gather cache or owned scratch. Direct scalar ADDs are sufficient once
the two actual main banks occupy the common source-class frame.

## Literal support and parity geometry

The 112 P112 ports partition into 14 sign cubes of eight roots. In each
cube let B be the normalized root Gram matrix and put K_i=I-B. The literal
eight-by-eight matrices satisfy K_i^2=I. Each row has four nonzero entries,
all equal to ±1/2. Relative-sign parity splits each cube into two classes
of four roots, and K_i has support only between opposite parity classes.

On one product cube of 8^3=512 ports define

    K_odd=(K1+K2+K3-K1 K2 K3)/2.

Each single-factor term flips one parity, and the product term flips all
three. Thus every nonzero scalar entry has opposite total parity at its
two ends. The supports of the three single-factor terms and the triple
term are disjoint. Each row has 12 coefficients ±1/4 and 64 coefficients
±1/16, giving 76 nonzeros and absolute row sum seven. The quotient algebra
K_i^2=I gives K_odd^2=I; the eight scalar sign substitutions check this
polynomial identity. Therefore its two 256-by-256 off-diagonal blocks are
invertible, although invertibility is not needed for the direct read word.

The concatenated q=(q1,q2,q3) labels lie in the nondegenerate U25 inside
F2^27. Each product parity class has 256 distinct labels spanning a
nine-dimensional subspace S_p. Every source label q_s belongs to S_p.
Opposite parity-class spans are orthogonal, so

    S_p subset q_r^perp  for every reader r of parity 1-p.

All 2744 cubes were checked independently from the pinned normalizer roots:
1,404,928 literal labels, both class sizes/spans, all restricted form ranks,
and every reader against all nine source-basis vectors. Bilinearity then
certifies every source/reader pairing, not merely sampled port pairs.

Important correction: S_p is DEGENERATE. Its restricted pairing has rank one
and radical dimension eight. In fact all q within one class pair to one.
Each odd q is consequently a representative of the characteristic functional
of that restricted form. It is false to require q to be noncharacteristic
inside S_p. The actual q is not the characteristic vector of ambient U25.
Neither of these facts obstructs a nested canonical-frame flag. S_p must
not be modeled as a nondegenerate coordinate I9 subspace.

## Exact main-bank interface

Write Phi_S for the actual canonical frame on S, R25 for the full frame,
and Phi_(q_r^perp) for reader r's requested final frame. Process each
product cube, and each source parity p, as follows:

1. For its 256 source fields, move the supplied own-line frame to Phi_Sp.
   Inclusion q_s subset S_p gives a rank8 child for each field.
2. For its 256 opposite reader fields, move ground to Phi_Sp, rank9 each.
3. For every nonzero K_odd[r,s], execute Y_r += K_odd[r,s] X_s.
   BOTH physical fields are exactly at Phi_Sp; this is an ordinary scalar
   ADD. No support-containment shortcut or nonmatching-chart read is used.
4. Move source fields from Phi_Sp to R25, rank16 each.
5. Move each reader from Phi_Sp to its own Phi_(q_r^perp), rank15 each.

All four ranks are actual nested-flag dimensions: 9-1,9-0,25-9,24-9.
The general canonical-frame distance identity applies to degenerate flags.
The separate native review/compiler is responsible for phase-exact monomial
wrappers; this independent audit verifies the scalar and flag premises and
does not duplicate that compilation.

For arbitrary logical inputs x_s,y_r, the common-frame read is

    Phi_Sp y_r + sum_s K[r,s] Phi_Sp x_s
      = Phi_Sp (y_r+sum_s K[r,s]x_s).

After its final transport the reader is exactly
Phi_(q_r^perp)(y_r+Kx)_r. The source is R25 x_s, because no source is ever
written by an ADD. Arbitrary old reader inputs are preserved in this formula.
No dirty helper correction or uncompute exists: there is no helper data.

The two parity passes use disjoint source X subsets and disjoint reader Y
subsets. The 2744 product cubes partition all global ports. A main field
therefore enters exactly one source/reader common frame, and no port-index
packing or independent-field identification is hidden in the program.

## Complete K-only accounting

For v=112^3=1,404,928, the whole paid profile is

    {H8:v,H9:v,H15:v,H16:v},   rank mass48v=67,436,544.

Each port has76 ordinary read ADDs, totaling106,774,528. The exact scalar
coefficients have denominators four or16. There are no logical helper fields,
COPY instructions, owned captures, zero retags or helper restores. Any work
arrays needed by the ordinary physical permutation implementation remain
ordinary compiler workspace and must still be included in its eventual bill.
At the common-frame scalar boundary, X coefficient l1 remains one and every
Y prefix has l1 at most1+7=8. Native child precision/normalizer expenses are
separate and have not been assigned zero.

Compared arithmetically with the earlier planning main profile
H8+2H15+10H1 per port, this profile has the same rank mass and reduces the
main moment at the selected a by about0.07093076880151 per port/local call.
This is only a profile comparison. It does not prove the F3 copied decoder,
H side producer or a whole caller can retain this chronology and this saving.

The settled boundary is K-only:

    X_s: Phi_[q_s]x_s -> R25 x_s,
    Y_r: y_r -> Phi_(q_r^perp)(y_r+K_odd x)_r.

The original source-line services are supplied by the entry contract. The
remaining H=F_block-F3, F3 readout, compatible K/H/F3 chronology, caller target
credit, terminal identity transfer, global precision/storage/compiler costs
and outer recurrence are NOT supplied by this result. A complete E caller
remains necessary before any new κ or supplier claim.
