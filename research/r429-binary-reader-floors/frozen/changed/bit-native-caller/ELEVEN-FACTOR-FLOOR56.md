# Every eleven-term scalar cold factor costs at least56

For the fixed R429 matrix M=KR, every exact eleven-term binary outer-product
factorization has rational source/target root-span pairing tariff at least56.
The proof below is a written all-factor argument with finite certificates,
conditional on the stated standard E8 root-system facts. It is not a native
COPY or arbitrary-dirty restoration theorem and gives no new kappa.

The dependencies are COLD-COSETS.md (each coset of D has at most one nonzero
reader of geometric rank<=6), TEN-FACTOR-FLOOR56.md (every ten-term bill>=56),
and UNIT-COLD-EXTENSION.md (the complete638 unit-extension hyperplane bases).
The actual M is symmetric, allowing interchange of source and target factors.
The E8 line capacities in ranks1..6 are1,3,6,12,20,36; a rank7 root subsystem
other than E7 has at most42 lines. These are standard finite E8 parabolic
classification facts, not a formal-kernel certificate.

Duplicate source or target directions merge without raising the pairing
bill: projected rank of an XOR is no larger than the sum of projected ranks.
The resulting factor has at most ten terms, already costing>=56. Assume
therefore that both lists have distinct nonzero directions. Sylvester's
inequality leaves only rank pairs(9,9),(9,10),(9,11),(10,10) and transposes.

If one side has rank9, orient it as targets, all in D. At most nine distinct
targets span7, giving at most nine one-unit cold discounts. For source rank9
all eleven terms pair dimensions>=7, giving>=66. For source rank10 there is
at most one low reader, hence source dimension sum>=1+10*7=71 and bill>=62.
For source rank11 the quotient by D has dimension2, hence at most three low
readers. With at most two, source dimension sum>=2+9*7=65 and bill>=56.
With three, their distinct nonzero quotient classes sum to0. Their actual
sum is a nonzero D word because all eleven source rows are independent.
Its weight is at least48, forcing M(d1)+M(d2)+M(d3)>=48. The complete small
capacity check gives d1+d2+d3>=11, attained at the capacity level by(1,4,6).
The other eight sources have dimension>=7, yielding bill>=11+56-9=58.

It remains to consider rank10 on both sides. A bill<=55 requires exactly
nine high/high terms, costing at least54, and two distinct low tails. A
quotient code coordinate on each side is chosen by the actual low row:
write its space as D direct_sum <z> (or <w>), and project along that low
direction onto D. Thus each low tail has zero D component, while the nine
high/high projected terms alone must factor the rank9 matrix M.

A low/low term would leave ten high/high terms costing>=60. A repeated low
direction would merge to at most ten terms. Thus there is one low-source /
high-target tail and one high-source / low-target tail. If the low dimensions
are a,b, their costs are at least a-1,b-1. Hence a+b<=3. The unit/unit case
is already excluded. Only unit/rank2 remains.

A rank2 reader has at most three coordinates. After toggling it into a
nonzero D word, the result has weight>=45, so a rank7 support must lie in
an E7 cap. The new executable checks all120 caps against all511 nonzero D
words. The only outside pieces of weight<=3 are the nine deleted-root caps
(outside0) and111 live affine readers f_p (outside unit_p); every other
outside piece has weight>=18. Therefore a rank2 extension creates at most
three generic hyperplane code labels. The two tail costs use at least1 of
the55 budget, so all nine core terms must pair two hyperplanes. Orient the
unit extension as sources. Every one of its638 possible hyperplane code
bases has nine generic dual target labels. A rank2 extension cannot turn
nine of them into hyperplanes. This is a contradiction.

Run `python3 -B eleven_factor_floor56.py` and
`python3 -O -B eleven_factor_floor56.py`. The receipt records all rank cases,
the61,320 near-cap tests, capacities, hashes, premises and review targets.
Review should particularly check duplicate-factor subadditivity, the three
nonzero quotient classes and source independence, low-tail classification,
and the rank7 capacity42 premise. No claim covers twelve or more terms,
shared queries, operator-valued coefficients, changed KR, native owner
placement, rounding or physical tape/source costs.

Root proposed the cold-contact and two-unit routes. This lane supplies the
finite certificates and full rank-case proof. Substantial OpenAI Codex
assistance; Apache-2.0.
