# Actual Gaussian reader: rank, basis and coefficient tariff

This package binds the reader of PR5634 to the actual 112-port source.
The maximum character rank is **30**, attained at character 92. Thus the
sharp dirty-bank tariff of PR5640 is **2 ceil(30/q)+2** cross-bank shears.
A dyadic change of the centre basis reduces the four-shear coefficient bill
from **31,608 to 20,352 ADDs**. There is no new odd denominator.
No new kappa or complete supplier is claimed.

## Boundary and source

Let S_chi be diagonal with entries (-1)^(chi dot q_p). The frozen source gives
U of size 112 by 30 and V of size 30 by 112. Put B=VU, T_chi=V S_chi U,
J_chi=S_chi U, and Delta_chi=B^(-1)V S_chi-T_chi^(-1)V. All 512 matrices T_chi
are invertible. Then Delta_chi J_chi=0. Since B is invertible, U and J_chi
are injective, so rank(J_chi Delta_chi)=rank(Delta_chi).

The coefficient ring is Q[C2^9]. Translation by g is an involution on the
nine-axis address space. At each positive tensor width the representation
contains every character. Inverse Walsh transformation gives each physical
kernel coefficient exactly. This is the source all-width translation
contract; the finite data do not prove the native Gaussian supplier.

SOURCES.json pins the response, directions, character inverse and source proof
to canonical main df0137efd35e11b4445734bf612bdd4c7ebc330c. SOURCE-CONTEXT.json
pins byte-exact copies of PR5634 and PR5640. They are proposed, author-checked
sources. The selected record at this base has conditional kappa 0.00310045.
Priority revision 7 remains in force.

## Exact rank and word

The rational rank histogram is in RESULT.json. An independent modular
elimination modulo 1000003 gives the same lower bounds for every character.
The maximum is 30, and the four zero characters are 0,45,466,511. The checker
verifies both inverse products for every T_chi and Delta_chi J_chi=0. It does
not infer the recoder rank from rank(E-I).

For N=J Delta, N squared is zero. The reader recoder uses
G(Delta), S(J), G(-Delta), S(-J), in execution order, where G adds to the
borrowed bank and S adds to the data. Its endpoint is diag(I+N,I).
For smaller q, split J and Delta into matching groups V_i,L_i with at most
q columns/rows. The complete word is

```
G(L_1), S(V_1), G(L_2-L_1), S(V_2), ...,
G(L_s-L_(s-1)), S(V_s), G(-L_s), S(-sum_i V_i).
```

All L_i V_j vanish. This proves the endpoint for every input and every dirty
baseline. The PR5640 lower bound applies to every word with only rectangular
cross-bank shears and q restored borrowed coordinates. The rank-30 character
makes its count sharp for this source. The coefficient count need not be
monotone in q. RESULT.json gives the complete q=1,...,30 tradeoff.

## Basis reduction and its precise optimum claim

The source Delta has 15,628 nonzero physical coefficients and J has 176.
The coefficient ADD bill is twice their sum. For distinct a,b and dyadic c,
replace row L_b by L_b+c L_a and column V_a by V_a-c V_b. This is an invertible
centre basis change. It preserves VL and LV=0, and needs no extra runtime
basis map: the compiler emits the changed factors directly.

BASIS.json supplies ten such changes. The final factors have 9,968 and 208
coefficients. Both complete factors and the inverse basis sequence are
reconstructed and checked. The search first removes eight repeated row
patterns, then makes two more changes. No source coefficient is rounded.

There is a finite complete test for further single dyadic row ADDs. For each
of all 870 ordered row pairs, the only c that can decrease support is a ratio
that cancels an entry of L_b+c L_a or V_a-c V_b. The checker counts all such
ratios, filters the dyadic values, and charges the union of the two supports.
Every remaining move has nonpositive gain. This is a certified local minimum
for arbitrary dyadic c, not a minimum over sequences with temporary increases,
all centre bases, all kernel gauges or all ordinary implementations.

## Cost and precision boundary

Each coefficient ADD means x_i <- x_i + c shift_g(x_j), with separate source
and target banks. The two passes use opposite signs. RESULT.json also counts
nonidentity-shift ADDs and records the common coefficient denominator.
These counts do not make rational multiplication, shift routing or tape work
free. No Gaussian request, fresh centre, COPY or CLEAR is added by the word.
The 30-field bank required inside the Gaussian section is still required.
A smaller borrowed bank for the surrounding recoder does not remove it.

For each group put j_i=||V_i||_infinity and d_i=||L_i||_infinity, where physical
coefficient absolute sums define the norms. Put J=sum j_i, D=max d_i,
M=max(1+2D,1+J), B0=max(1+sum j_i d_i+J,1+D), and
C0=max(1+J(2D+1),1+D). The coefficient-ADD prefix bound is B0 M and the suffix
bound is (1+JD) C0 M. These are the group-word bounds proved in the frozen
tariff source. They apply inside each coefficient pass because every partial
row sum is at most the full absolute coefficient sum. They are uniform in
payload volume. Arithmetic-interior and tape bounds remain separate tasks.

## Verification

```
python3.12 -B scripts/research_package.py --package research/actual-gaussian-reader-tariff
```

Expected: PASS_ACTUAL_GAUSSIAN_READER_TARIFF and
PASS_REGISTERED_RESEARCH_PACKAGE. Python 3.12 standard library suffices.
The replay checks every character, exact inverse Walsh reconstruction, all
rank values, all coefficient invoices and all 870 local search directions.
The all-input endpoint follows from the checked factor identities and the
word proof. A separate literal 512-address replay checks a deterministic
nonzero payload and arbitrary nonzero dirty baseline against the original
source factors. Three controls reject a corrupted actual inverse, a wrong
restoration-gather sign and an omitted final scatter. This physical payload
check is not an exhaustive input enumeration or independent human review.

Full native, outer, compiler, precision and tape admission was not run.
The source-history preflight needs more Git history than this shallow checkout.
Source hashes, committed bytes, registered normal/optimized checks and a
Git-free export are separate publication checks. No proof assistant was used.

## Open next questions

1. Can a multi-row or address-dependent basis reduce the coefficient bill
   below the certified single-ADD local minimum? It must include coefficient
   magnitude and physical routing costs. Start from the emitted factors;
   no new search is reserved by this package.
2. Can this cheaper reader be placed in one complete native supplier with a
   favorable recursive invoice? Use the actual thirty-row source, preserve
   the section bank, and price the later consumer and restoration. A full
   caller and arithmetic-interior implementation are still missing.

## Credit

David Ganz (@Dugongue) supplies PR5634, its reader substitution, four-shear
identity and section conjugacy. PR5640 supplies the sharp storage theorem.
The centre-code-services source supplies the actual factors, phase sections
and exact inverse certificate. Retain reciprocal-native-responses,
native-centre-capture, centre-metric-encoders, the source campaign notices,
and PR3133, PR3148, PR2588 and PR2226. The frozen source text retains the
individual contributor notices. This package does not infer owning authors
from a PR submitter. New source binding, basis search, proof and code: Ali
Romman, with substantial OpenAI Codex assistance. Apache-2.0.
