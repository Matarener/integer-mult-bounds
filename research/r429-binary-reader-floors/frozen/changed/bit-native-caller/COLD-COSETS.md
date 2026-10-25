# Source cosets and ten-term cold factors

This is a necessary scalar-factor cost screen for the fixed R429 correction,
not an admitted native COPY implementation or a new exponent. Source pin:
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

TEN-FACTOR-FLOOR56.md closes the55 equality case and strengthens the
ten-term conclusion below to56. The coset theorem remains a premise there.

Let D=rowspace(R), the actual dimension9 binary reader code on111 E8 source
lines. Its minimum nonzero weight is48. A scalar reader's geometric rank
means the rational dimension of the span of the E8 roots in its support.

Every coset z+D contains at most one nonzero reader of geometric rank<=6.

Here is a finite certificate plus a standard root-system reduction. A
root-spanned rational flat meets E8 in a parabolic root subsystem, as in
READOUT-FLOOR.md. Among rank<=6 root subsystems, only E6 and D6 have more
than21 unoriented root lines. Every other irreducible type has at most A6's
21, and every other product has at most D5+A1's21. Thus two flats of the
other types together cover at most42<48 source coordinates and cannot
support a nonzero D word.

The E6 and D6 cases are exhaustively covered as orthogonal complements of
actual A2 and A1+A1 root planes in E8. There are1120 and3780 distinct flats
respectively, reconstructed from the actual120 full root lines. Their
punctured supports still have rational rank6. For every one of those4900
supports S and every one of511 nonzero words d in D, the certificate checks

`rank_Q(roots in supp(d) outside S) >= 7`.

The executable supplies a modular rank7 lower certificate over F65537 in
each of2503900 cases. These are rational lower certificates regardless of
whether modular and rational ranks agree. If c0 were supported in S and c1
in any rank<=6 flat, with c0+c1=d, then supp(d) outside S would be contained
in supp(c1), contradicting that rank7 certificate. This also permits the
second flat to have a type not enumerated explicitly.

For completeness, the complement-type assertion follows either from the
usual E8 parabolic classification or its primitive lattice embeddings:
E6 has determinant3 and complement A2; D6 has determinant4 and complement
A1+A1. This is a written finite-root-system reduction, not a formal-kernel
certificate. The actual root planes and all code data are pinned in the
executable and receipt.

The coset result applies to an exact ten-term scalar correction

`K R = sum_(i=1)^10 b_i c_i^T`.

Use the optimistic term tariff `rank_Q(pairing(U_i,V_i))`, where U_i is the
source-root span of c_i and V_i the target-root span of b_i. It equals
`dim(U_i)-dim(U_i intersect V_i^perp)` and is the proposed cold-contact
descent price before source gathering, target lifts and restoration.

The total tariff is at least55. By Sylvester's inequality, the two factor
ranks cannot both be10 when the product has rank9. If both are9, their
row/column spaces equal D, so every U_i,V_i has dimension>=7; each pairing
rank is at least6 and the total is at least60.

Otherwise transpose if needed so the ten c_i are independent and their
span contains D with quotient dimension1. Every c_i of geometric rank<=6
lies outside D, hence in its sole nonzero quotient coset. There is at most
one such reader. The other nine each cost at least7, so the sum of source
dimensions is at least64. All target readers lie in D. A generic target
reader spans8 and gives no cold discount. Only the nine original special
directions span7, each allowing a discount of at most1.

If target readers are distinct, at most nine such discounts give64−9=55.
If two target readers coincide, merge their source readers by XOR. The
projected source rank of the sum is no larger than the sum of their ranks,
so the bill does not rise. The resulting nine-term factor has bill>=63.

The nine-term63 assertion has a short independent check. Both sides are
bases of D. Their special rank7 directions are the same nine labels. Each
special label has binary self-pairing1 in the actual inverse coefficient
form, checked in the receipt. A label appearing on both factor sides must
therefore occupy the same factor, where the same-normal pairing rank is7.
For each factor the lower cost is8, minus1 for a special source, minus1
for a special target, plus1 when those two special labels coincide. Summing
charges each of the nine available special labels at most once, giving
72−9=63. No search over bases is needed.

These are necessary costs only. There is no claimed55-cost construction,
no source-gather compiler, no immutable COPY/ERASE chronology, no target
native-frame schedule, and no ordinary-helper restoration beyond the frozen
bulk premise. Eleven or more terms, shared queries, operator-valued readers,
changed R/K and different callers remain open.

Reproduce with `python3 -B cold_cosets.py` or
`python3 -O -B cold_cosets.py` (about50 seconds locally). `--write`
regenerates COLD-COSETS.json in this owned directory only. The finite
negative control substitutes a two-source word outside D and confirms that
the rank condition can fail when code membership is removed.

Credit: root proposed the one-dimensional extension/coset test and the cold
source/target tariff; the R429 bulk and E8/R438 geometry retain predecessor
attribution. This lane adds the4900-flat exact certificate, the all-flat
coset consequence, and the ten-term55 screen. Substantial OpenAI Codex
assistance; Apache-2.0.
