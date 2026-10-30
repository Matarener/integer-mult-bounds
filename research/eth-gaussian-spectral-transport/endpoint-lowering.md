# Exact endpoint recovery and a charged multiplication interface

The constructions in this package are informal mathematics. The main result here is an explicit exact endpoint compiler for valuation-filtered Gaussian responses, including denominator debt, dirty restoration and a complete symbolic bill. It does not assume the preprint's headline ETH theorem. It does not declare a new numerical κ.

## E1 Gaussian precision after normalization

Let π=1+i, R=Z[i]_(π) and v=v_π, with v(π)=1. Let P be a positive integer. Suppose a finite expression has the form

    E(x)=sum_beta c_beta product_j L_j(x)^(beta_j),

where beta ranges over a specified finite set, v(c_beta)>=sum_j w_j beta_j, and v(L_j(x))>=-d_j for all allowed x. Here the w_j and d_j are explicit integers. Define the net weights ν_j=w_j-d_j.

**Theorem E1 (normalized weighted response compiler).** Deleting every summand with sum_j ν_j beta_j>=P preserves E(x) modulo π^P for all allowed inputs. If each ν_j is positive and at most K variables have any one net weight, the number of potentially retained exponent tuples is at most exp(2 sqrt(2KP)). Each retained tuple can be emitted by bounded-budget enumeration, using an explicit finite coefficient evaluator for that tuple.

**Proof.** Every deleted term has valuation at least sum_j(w_j-d_j)beta_j>=P. A finite sum of such errors remains in π^P R. The count is the generating-function estimate G3 in [preprint-assessment.md](preprint-assessment.md), now applied to the actual net weights. Successively choose each exponent up to the remaining budget divided by its weight. Every admissible partial choice has a zero continuation, so the traversal has at most the number of complete tuples times the number of variables, plus a constant, nodes. This is a constructive algorithm, with no oracle for missing coefficients. QED.

If a net weight is zero or negative, the finite expression still permits the stated deletion rule. The short positive-weight enumeration bound then requires a separate bound and cannot be quoted. A common denominator does not make a negative net weight positive.

For an integer mode multiplied by 2^b, its Gaussian weight is 2b. If the corresponding source value has denominator 2^d, its debt is 2d, leaving net weight 2(b-d). Division by an odd rational integer consumes no valuation, although its arithmetic cost remains. This is the exact distinction needed when transporting the preprint's integral crossing modes to a dyadically normalized Gaussian supplier.

## E2 Exact decoding, rather than a modular surrogate endpoint

**Theorem E2 (Gaussian integer endpoint recovery).** Let an explicitly specified finite computation produce an integer endpoint z in Z[i]. Suppose |Re z|,|Im z|<=B and a nonnegative integer D is known such that G=2^D z is the output of a specified Gaussian-integer computation. Choose an integer p with 2^p>2B. Computing G modulo π^(2(D+p)) determines z exactly.

**Proof.** Since 2=-iπ^2, division by 2^D maps the residue of G modulo π^(2(D+p)) to a well-defined residue of z modulo π^(2p). Representatives differing by π^(2(D+p)) give quotients differing by a multiple of π^(2p). Since (π^(2p))=(2^p), this gives the ordinary coordinate residues of Re z and Im z modulo 2^p. Two integers in [-B,B] with the same residue differ by a multiple of 2^p of magnitude at most 2B<2^p, so coincide. The centered representatives are therefore the exact endpoint. QED.

The same argument applies to each coordinate of an output vector. If the desired endpoint is Gaussian dyadic rather than integral, first specify its output denominator 2^d and recover the bounded Gaussian-integer numerator; division by 2^d is then an explicitly retained final operation. A bound only on the complex absolute value is also sufficient, since it bounds both coordinates.

**Corollary E2a (finite tensor network with honest denominators).** Consider a Boolean tensor network with E edges and vertices v. At vertex v let every tensor entry equal 2^(-d_v) a_v, where d_v>=0 and a_v is a specified Gaussian integer with coordinate magnitude at most 2^(b_v), b_v>=0. Put D=sum_v d_v and

    H=E+sum_v(b_v+1).

The contraction Z satisfies |2^D Z|_infinity<=2^H. If Z is an integral endpoint, p=H+2 is sufficient in E2. If Z is not integral, its numerator 2^D Z is recoverable modulo π^(2(H+2)), followed by the explicitly declared division by 2^D.

**Proof.** There are 2^E Boolean edge assignments. The Gaussian one-norm |a+bi|_1=|a|+|b| is submultiplicative, so the magnitude of each product in either coordinate is at most product_v 2^(b_v+1). Summing gives 2^H. For an integral Z, its coordinate bound is at most 2^(H-D)<=2^H, so p=H+2 obeys the strict decoding inequality. The rational case recovers the bounded numerator directly. QED.

The global denominator in this statement is an upper bound, not a claim of minimality. It can be improved by proving cancellation; a favorable cancellation cannot be presumed. Reading the tensor descriptions and the actual source data is part of the cost. A small algebraic description does not allow an arbitrary dense input table to be read for free.

**Corollary E2b (the actual π-denominator convention).** More generally, if z is a bounded Gaussian-integer endpoint and G=π^d z is a supplied Gaussian-integer computation for some d>=0, then its residue modulo π^(d+2p), with 2^p>2B, determines z exactly. Divide the residue by π^d and apply the same coordinate argument. For the source Gaussian tensor, one raw axis contributes ONE π denominator unit; it need not be inflated to a full factor of 2. For a known output grid π^(-d), recover the bounded integral numerator first and retain that grid explicitly. A fixed odd common denominator q can also be retained: after the π-power division multiply by its unit inverse modulo the output modulus, paying the q arithmetic and height bill.

## E3 Observable-dependent precision with arbitrary dirty state

We next state an implementable precision-retirement rule. Fix a finite straight-line linear program over K=Q(i), including its input and output conventions. Its state x_i has a fixed declared number of coordinates; owned coordinates are initialized explicitly. Let A_i be its exact update matrix from event i to i+1. List every observation required by the caller: final public fields, restored dirty helpers, productive helper outputs, and any retained intermediate source reads or boundaries. Treat each such observation as a row functional of the appropriate state. Zero final owned fields are included whenever cleanup is required.

For a cut i and coordinate r, define μ_(i,r) to be any proved lower bound for the valuation of EVERY coefficient by which an error in that coordinate can affect a required future observation. If all those coefficients are zero, write μ_(i,r)=infinity. The bound can be obtained from literal suffix matrices. A conservative alternative is backwards propagation using

    μ_(i,r)<=min_s [ v(A_i[s,r])+μ_(i+1,s) ],

and the analogous minima with coefficients of observations made at the cut. A zero coefficient has valuation infinity. Cancellations may improve the exact bound; ignoring them is safe.

**Theorem E3 (charged precision retirement).** Fix desired observation precision P. At event i, replacing a coordinate by any value differing by an element of π^(P-μ_(i,r)) R preserves every required observation modulo π^P. The same is true for any finite set of such replacements. If the original program restores arbitrary dirty state, the replacement does so modulo π^P; exact restoration follows when E2 is applied to every required restored coordinate with a valid common height bound.

**Proof.** Propagating one error linearly to any observation multiplies it by a coefficient of valuation at least μ_(i,r), so its resulting valuation is at least P. The total change from finitely many errors is their sum propagated through the unchanged linear program. Every term has valuation at least P and so does the sum. The backwards rule is sufficient because matrix multiplication sums products and v(sum)>=min v(term). The same argument applies to arbitrary initial values of dirty coordinates; no zero-state assumption was used. Applying exact centered decoding to the restored fields gives the claimed equality. QED.

When μ is infinity the value is unobservable in the declared continuation. Erasure nevertheless requires the owned allocation/clearing operation if the machine contract demands it. When P-μ is negative, the notation specifies a fractional lattice congruence; the implementation must choose a representative in that lattice, or simply retain the old value. This theorem gives no license to discard an unlisted public output. Listing only the main target while omitting dirty restoration would change the contract.

This theorem is especially useful for the preprint's crossing-mode compiler: a high-weight mode may become wholly unobservable at the final precision, not merely cheap to approximate. The actual event and observation list, including helper lifetime boundaries, supplies the witness for deleting its query.

## E4 A genuinely shorter modular query routine

Here is a small exact construction showing query deletion, rather than a claim based only on rank. Let Q:R^m->R^m be a supplied linear operator that preserves the integral lattice. The implementation contract permits a query Q(u), with cost charged at the requested modulus. Let P>=1 and w>=P. Consider the explicitly specified endpoint

    y'=y+Qx+π^w Qz  (mod π^P),
    x'=x, z'=z.

Every public coordinate x,y,z may be arbitrary. Initialize one owned field h=0, query h=Qx modulo π^P, add h to y, and clear h by the declared owned-clear operation. This realizes the endpoint with ONE Q call, because Qz is integral and π^w Qz is zero modulo π^P. The naïve expression uses TWO calls. It obtains no extra productive helper credit, and pays initialization, the add, routing and the clear. If this endpoint is a bounded integral result after denominator clearing, E2 turns the modular routine into the exact ordinary endpoint with the larger modulus specified there; the inequality w>=P must then hold at THAT larger modulus, not at a smaller displayed one.

For w<P the second query can instead be made at precision P-w, provided the implementation actually supports that truncated query. A complete tariff compares

    H_Q(P)+H_Q(P-w)+ordinary_fees

with 2H_Q(P), including source reading and precision conversion. This is a positive exact construction for the stated input class. It does not assert that an existing unfiltered P104 helper update has w>=P.

More generally, a finite response that is a literal sum of separately supplied query modes has one paid query for each surviving mode, at its proved needed precision. E1 gives a deletion test, G4 gives the precision of the required node responses, and the concrete Cauchy expansion in [algebraic-application.md](algebraic-application.md) supplies actual mode coefficients. A generic polynomial monomial does not automatically correspond to one query; its explicit child-network or straight-line implementation must be supplied and charged.

## E5 Sufficient assembly into the current κ framework

The preceding theorems are constructive on their stated domains. Their use in the multiplication project has the following exact interface. Select ONE actual source interval and its complete caller. Replace it by the explicit node/jet/filtered-mode construction only after identifying its input lattice, all required observations, denominator debt, height bound, native implementation and complete ordinary bill. The emitted construction is finite; the comparison must use the same physical targets and either retain or explicitly debit any removed helper targets.

At a proposed saving C, let

    F_old(C)=sum_r T_old(r) r^(1-C)
             -sum_r P_old(r) r^(1-C)-E_old(C)

be the source's full normalized signed moment, with E the applicable extra fees. Define F_new by the actual new histogram and its fees. Then

    F_new(C)=F_old(C)
             +sum_r (T_new(r)-T_old(r)) r^(1-C)
             -sum_r (P_new(r)-P_old(r)) r^(1-C)
             -(E_new(C)-E_old(C)).

This identity is exact. If its right side is strictly positive and the retained completion, higher-moment, compiler, BIT and outer guards hold strictly at C, the same declared framework supplies every smaller κ allowed by those strict guards. This is a sufficient assembly argument, not permission to replace any of the guards by a plausible price estimate. The historical conversion κ=a/(1+a) is not the selected mixed-target formula.

In particular, deleting k rank-r query modes with unchanged targets contributes +k r^(1-C), before new node evaluations, ordinary work, loss of productive targets and other changed charges. A lower modulus at the same finite template need not change the exponent at all. A reduction in offline synthesis time does not appear in this recurrence as a removed recursive call.

For the actual pinned P104 and G20 words this package supplies no new fully realized histogram, no exact-operator replay and no new strict outer test. Accordingly no numerical κ increase follows here. The deliverable instead provides the exact mathematical constructors and sufficient accounting rule needed to investigate a changed valuation-filtered provider, with the denominator, observations and ordinary implementation fixed in advance. No unknown favorable gadget is assumed inside any of E1-E4.

## Open next questions

1. **A literal Cauchy response window.** Does one actual Gaussian provider interval admit the paper's displacement kernel, or a polynomial deformation with the same integral local expansions? First step: write its literal response matrix and define F(T) and its exact origin endpoint. A similarity of ranks or names is not the required equality.
2. **Net-weight survival.** For that explicit deformation, do the positive crossing weights remain positive after input scaling, normalization and exact decoding? First step: give a termwise denominator table and the resulting net weights in E1. Integer spectral kernels are attractive because their ordinary implementation adds no division debt.
3. **Chronological observability.** Can those modes be retired before any retained source read, target boundary or dirty restoration needs them? First step: give the actual observation list and suffix sensitivity witnesses from E3. A final matrix identity alone does not answer this.
4. **Full signed gain at a useful exponent.** Once the finite construction exists, can its complete new paid/target bill pass the selected strict guards at a saving materially beyond the current pending result? First step: a symbolic invoice with every node, jet, cache, target debit and ordinary fee. BIT .0034 is still the currently admitted cap; an additional compatible BIT result is needed above it.

New text is Apache-2.0 with substantial OpenAI Codex assistance. Gaussian valuations, polynomial interpolation and the standard generating-function bound retain their classical attribution; the preprint-specific taper and spectral construction are credited to OpenAI. Project precedents and exact heads are in [SOURCES.md](SOURCES.md).
