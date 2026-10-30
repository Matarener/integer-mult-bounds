# An auxiliary ordinary-interchange construction

Written proof assembled in the current audit, 2026-10-19. This is an auxiliary
BIT construction, not a multiplication theorem or a formal-kernel result.
The physical Python suites are not all passing within their registered time
limits; their exact status remains in AUDIT.md. The mathematical
construction below uses complete sequential scans and encoded arithmetic,
not the wall-clock behavior of that simulator.

The finite source is the selected PR589/PR1627 word retained at canonical
`bb4bccbf42844d2801487450727c2f63e10d1d0f`. Attribution and source hashes
are in the unchanged source packages and SOURCES.json.
The all-size assembly follows PR2195, PR2234, PR2753/2809, PR2899 and PR2915;
the retuned c, explicit prime and independent normal-form derivations here
must not be attributed to those earlier fixed-parameter statements.

## Statement

Set

    q=2^89-1,
    c=8667/5000000,
    a1=c(1-c)=0.00173039532444,
    a2=c(1-c^2)=0.001733394791695384296.

There is a fixed finite-tape, finite-alphabet machine that exchanges two
complete equal e-bit binary address fields, with arbitrary complete preceding,
intervening and following fields, in O(V e^(1-a2)) time and O(V) visited
space. It preserves its borrowed input, returns a distinct owned output,
fixes every spectator, erases its work and returns its heads. Constants
depend on the fixed source and q, not the fields, payload or e. This is an
existence construction with enormous constants.

## 1. Fixed finite data and the local-ring endpoint

`check_bit_prime.py` checks all 20 nodes of a complete Lucas order certificate
for q. If g^(n-1)=1 mod n and g^((n-1)/r)!=1 for every certified prime r
dividing n-1, g has order n-1 in the units modulo n. A composite n has fewer
than n-1 units, which is impossible. Induction from the node2 proves every
certificate node. Thus q is a specified prime, and

    2*64^3/q < 10^-16.

The freshly replayed finite word certificate checks the rational frame
idempotents, nested differences, complete scalar words, literal private-copy
guards, hosted supports and untouched time windows. These are finite exact
identities. The replay of selected-bit-local-ring-sweeps also authenticates
the same word and owner data; see evidence/bit-local-ring-current.log.

For every w>=1 those rational identities specialize to Z/q^w, since their
denominators are powers of two. The characteristic polynomial of each
idempotent gives its rank after reduction; image/kernel columns lift to a
unit basis, proving split rank over the full ring. For P idempotent put

    N(P)=[[I-P,PC],[CP,I-CPC]].

Then N(P)^2=I, nested differences multiply as their corresponding residuals,
and disjoint commuting projectors add. These identities survive conjugation
by diag(A,I) for any diagonal unit A. At one node A reads only already
frozen ancestor fields, so it is unchanged by fresh-header routes and scalar
payload operations.

The complete GL cover and the finite owner charts supply disjoint low packets
within a call: same-family helper supports are disjoint nonzero summands, so
their chart reductions differ over every odd characteristic. Route a whole
packet by the exact right multiplication, including low/high carries. The
common-label induction then applies the checked scalar word on arbitrary
correlated dirty data. After a complete word, helper endpoints are unary
permutations. Full-cover sweeps put each on its named physical slot once;
the checked untouched intervals permit their collapse with the exact idle
remainder. This proves the weighted reversed endpoint on every live family.
No high-prefix value is deduplicated and no scalar observation is crossed.

NORMAL-FORM.md proves the good residual with one rank-r child over the
full ring. FALLBACK.md proves the other branch with at most49911
children of width at most f, including odd central spectators and each
shear's actual permutation snapshot. It also gives the completed weighted
leaf using only ordinary swaps, ordered additions and a linear sign pass.

## 2. Uniform stock and well-founded recursion

Let W=28416, N=|GL_64(F_q)| and

    K(w)=269241600 N q^(4096(w-1)),
    D(n)=0 (n<64),  D(n)=1+D(42 floor(n/64)) (n>=64).

At a node require R=t K(w)^D(n) fresh rows. Splitting its complete family,
low matrix and high matrix fields leaves U=t*9475*K(w)^(D(n)-1) fresh rows.
Every child has width <=42 floor(n/64)<n and depth at most D(n)-1, so its
stock divides U. The whole high packet becomes one new frozen-prefix field;
the child is outside the high-prefix loop and sees its complete packet once.
Its incoming weight program reads only older fields. All inactive atoms,
intervening fields and unused stock are complete spectators. Strong induction
on n gives the endpoint, restored rows and owned output together.

The fixed number of source operations and low classes can be unrolled into
finite control because q and all source dimensions are constants. Variable
column loops and all cardinalities use encoded counters. At a recursive cut
the column loops have finished; the continuation is a finite instruction
label plus encoded parameters. Serialize parent streams and arithmetic
state to a sequential stack, copy the child's capsule, reuse the fixed work
roles, and restore the parent after the protected child output returns.
All encodings have explicit markers and are erased on return. This is the
PR2809 block construction; it requires no variable number of tapes, random
access, host iterator or uncharged restoration.

Within a block, nested complete-field counters have amortized linear scan
cost. Ordinary schoolbook modular arithmetic suffices for numerical control.
The dimension64 matrices use a fixed number of numerical fields; ancestry
evaluation uses an encoded pending/value stack. At global ancestry depth h,
its work is at most 2^h times a fixed polynomial in w and log(e+1).

At a root choose w=ceil(e^c), and retain that w at every descendant.
Two coarse levels reduce width by at least a factor two, so h<=2log2(e)+O(1).
Also e<=w^(1/c). Thus preparation is a fixed polynomial in w. It occurs
once per complete q^w target fiber, so its cost/volume ratio is uniformly
bounded. Header primitives use complete q^(w-1) fibers; w=1 has no high
operation. Arbitrary spectator counters are initialized once per their
complete scan and updated by ripple counters, not recopied at every record.
Directories retain all physical prefix ordinals even when their values repeat.

Each child's payload has volume V/(WN). Active ancestor payloads therefore
form a geometric series. Metadata and coefficient scratch are bounded by
their complete fibers; sequential parking adds a constant multiple of that
volume. Hence visited space is O_q(V), including erased backing, markers,
templates, borrowed-source preservation and the owned return buffer.

## 3. Both reached primitive sites and the recurrence

Suppose a preceding completed ordinary stage has saving a, initially a=0
from elementary q-digit swaps. Use it both for the weighted-leaf swaps AND
the owner header routes. For a dyadic chart factor, its full high-field map
is obtained from the low-digit carry, followed by an ordered high-field
addition, fixed doubling/halving/sign/translation, and at most two ordinary
swaps. The exact column-factor products are fixed finite certificate data.
Doubling/halving on an odd modulus is a two-piece split/interleave; it does
not make w digit passes. At w=1 copy the unique high cube without a zero-width
callee. These are PR2915's two actual reached call sites.

Good adapters and fallback shears have O(n) ordered complete-fiber additions.
Peeling, leaves and fixed header routes cost O(w^(1-a)) after normalization
by volume. Canonical commits and checkpoints contribute O(n+1); ordinary
callee output copies/clearing are included. The resulting local toll is
O_q(n+w^(1-a)). A preceding stage finishes before a successor resumes;
the stage order is C1 -> B1 -> C0 -> elementary, so there is no circular call.

For each paid residual, clearing leading minors gives a nonzero polynomial
of degree <=64k with a diagonal-projector witness. Schwartz-Zippel and
GL density>1/2 bound its bad low-class fraction by2*64^3/q. Apply the bound
per request, not to a simultaneous intersection of all requests. The paid
profile is

    H={1:381024,2:400416,3:22752,4:26880,5:29376,6:17376,7:26784,42:288}.

With F=32*64^2*sum_r(H_r)=118606528512, t=1-c and eta=10^-16, normalized runtime
satisfies for n>=64, f=floor(n/64),

    T(n,w) <= sum_r H_r/W T(rf,w)
              +eta F/W max_(1<=j<=f) T(j,w)+C(n+w^(1-a)).

The finite leaves have T(n,w)<=C w^(1-a). The rational interval certificate
evidence/composition-controls.json proves mu_t<1 and mu_1<1, where

    mu_x=(sum_r H_r (r/64)^x+eta F (1/64)^x)/W.

Strong induction with the monotone proposed envelope, without assuming
monotonicity of actual runtime, gives

    T(n,w) <= C/(1-mu_1) n + C/(1-mu_t) n^t w^(1-a)

after increasing C for the finitely many leaves. All constants are uniform
over payload values, frozen prefixes, complete spectators and parking height.
The old source constants200/10000 are not used at this new c.

## 4. Ordinary wrapper and two completed stages

On original radix width e compute stock=K(w)^D(e) and the least k with
q^k>=stock before removing borrowed digits. If 2k>=e or the body width is
below64, use the elementary algorithm. Since k=O_q(w log(e+1))=o(e), these
failures occur at only finitely many widths. Otherwise write e=k+nw+ell
with 0<=ell<w. Pad the q^k row range to a multiple of stock, at ratio<2,
for each reversed call separately; restrict immediately after it returns.

With unit incoming weights, execute the body word

    D-=H; F_I; D+=H; F_I; D=-D; D+=H.

These additions are COMPONENTWISE in Z/q^w across the n body atoms, not
one carry-propagating addition modulo q^(nw). They cost O(Vn) and are
already included in the linear term. If R reverses the atom order, F_I is
(D,H)->(RH,RD). On original (x,y), the successive states are
(x-y,y), (Ry,Rx-Ry), (Rx,Rx-Ry), (x-y,x), (y-x,x), (y,x).
Thus the endpoint exchanges the original D and H. Exchange the high and
remainder fields by elementary digit swaps. Restored rows permit both F_I
calls to reuse the same stock. Their complete cost is

    O_q(V [n+n^(1-c)w^(1-a)+k+w])
      = O_q(V e^(1-c+c^2-ca)).

All setup uses polynomial encoded arithmetic and is absorbed by complete
input volume. Thus a completed stage a gives a NEXT completed stage
a_next=c(1-c)+ca. Apply this first to a=0 and then to the completed a1,
obtaining exactly a2. The total number of stage inventories is fixed.

Finally embed each 2^e binary field into q^E, E=ceil(log_q(2^e)); each
ratio is <q. Fill other positions with zero records, run the ordinary q-ary
exchange and restrict the returned rectangle. The endpoint preserves that
rectangle and restores every spectator. This changes volume by <q^2 and
width by a fixed factor, proving the stated binary bound and cleanup.

COMPLEX.md uses this completed auxiliary theorem; GAUSSIAN.md and PROOF.md
then supply the Gaussian construction and exact multiplication recovery.
