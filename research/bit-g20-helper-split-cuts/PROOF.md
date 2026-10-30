# No common-frame helper split in the frozen G20 word

The inputs are the exact nine-owned G20 word in PR5512 at main
5e0052ca0aa3036a3afa8b0438927377c8d97d53. Use its physical frame induction:
a field in frame U is D_U times its normalized binary row. Every common-frame
ADD acts on those rows by XOR. QUERY changes the frame and leaves the row
unchanged. ERASE removes the entire owned row. The rows retain all 660 RAW
and arbitrary DIRTY input columns. No owned input is assumed clean before
its actual ERASE.

Let A be the complete prefix matrix at a cut and B its remaining suffix
matrix. Let H be one set of retained helper inputs and outputs with the
same physical entrance projector and zero exit frame. There are four such
sets: 423 full rank8 helpers, two helpers with one rank4 entrance, and two
single helpers with their respective rank4 entrances. These are all 427
retained helpers. Their source endpoint is the identity in normalized rows.

Choose any cut bank F in a common frame strictly between zero and the
entrance projector. Equal rational projector subspaces count as one frame;
labels do not decide this condition. All public and owned fields can occur
in F. Define

    R = A[F, inputs outside H],
    C = B[outputs outside H, F].

A cut functional v can depend only on the chosen independent helper inputs
only if v^T R=0. A cut direction u can affect only the chosen helper outputs
only if C u=0. To isolate one independent channel by invertible input,
cut and output bases, their pairing must be nonzero. Normalize it to
v^T u=1. To isolate k channels, the pairing matrix must have rank k.
This necessary condition grants arbitrary binary bases and allows all
existing owned buffers in F. It does not require a pure original helper
coordinate or a diagonal input completion.

The verifier proves

    (ker R^T)^T (ker C) = 0

at every cut and every eligible frame and endpoint group. Thus no positive
number of independent helper channels can be split at any of these cuts.
This includes a split found only by coupled input and output bases. It also
excludes a sequence whose first step is such a split. It does not exclude
a changed scalar word that creates a new cut matrix.

## Independent rank criterion and coverage

The zero pairing is equivalent to ker C being a subspace of im R. By
rank-nullity, this is equivalent to

    rank(C R) = rank(R) + rank(C) - |F|.

The verifier first constructs both annihilator kernels with highest-bit
pivots. It then constructs C R explicitly and checks this rank identity
with lowest-bit pivots. These checks use separate arithmetic paths.

Forward replay obtains every prefix and suffix. For ADD, advance A by its
row addition and remove that ADD from B by its column addition. ERASE is
not inverted: its exact after-value for B comes from a separate backward
pass. A complete reverse traversal uses the saved before-value for A at
each ERASE. The two traversals reach the exact endpoint and entry and
produce identical sets of cut states.

Between instructions, only the touched common-frame bank can change its
R or C. A frame move changes its two endpoint banks. The verifier checks
those banks and all initial banks, so unchanged banks require no repeated
check. Every boundary, including entry and exit, is covered. Deduplication
uses the complete field list and exact A and B rows, not a hash alone.
Hashes identify the final certificate. The all-input endpoint is checked
separately. A true isolated channel and a false orthogonality example test
that the procedure detects a possible split.

The result also holds over every field of characteristic two: kernel
bases extend by scalars, so a zero pairing remains zero. For the bilinear
transpose word, prefix and suffix exchange and transpose. R and C^T
exchange, so the same certificate covers that orientation. This is an
algebraic transpose conclusion, not a newly emitted native inverse word.

## Price and limits

A valid split of a rank-a helper at a proper nested rank-r frame could
replace its target by two independent targets of ranks r and a-r. With
unchanged paid work, this would improve concave credit by

    r^t + (a-r)^t - a^t > 0,  0<t<1.

The source-bound pairing test excludes that free split before a compiler
or a larger target inventory is built. It does not give a global BIT lower
bound. Changed contacts, scalar order, address-dependent recoding entries,
paid boundaries between different frames and a new producer remain open.
General simultaneous basis changes in different physical frames are not
included. No new kappa or selected-frontier change is claimed.
