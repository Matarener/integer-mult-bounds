# Eight retained partial caches still do not identify the required observer

The observation channel is the raw PR5402 backward WORD, with **every**
full-nine-dimensional-frame value retained throughout its execution, enlarged
by all eight nonzero endpoint partial-frame cache values. This is the concrete
channel excluded from PR5447's full-frame-only theorem. We prove that even
arbitrary nonlinear postprocessing of this enlarged channel cannot determine
the actual consumer target `b=ZQY_return=ZRy` on arbitrary independent inputs.

This is not a statement about the whole machine state. In particular the
lower-frame current main inputs/outputs, original helper observations,
additional paid responses and PR5413's changed completion are not supplied
by this observation interface. No source instruction, cache lifetime or
selected provider is changed.

## 1. Source object and original-input convention

The canonical base is `32890bc5de034ab8fc93ac88ead7279a6a416d04`.
SOURCES.json pins the exact raw source, modified WORD, provider contracts and
physical normalizers by Git object and SHA256. The backward WORD contains
21,473 records. Native chart semantics are those of the pinned provider:
ordinary ADD/SCALE/COPY act on normalized rows at compatible charts; paid
climbs change the chart; warp records act by their signed invertible native
letter; only owned fields may be cleared. `phase` records are stage labels,
and `adapter` records retain physical entrance/exit bindings, not row updates.
These inherited native semantics and their all-width physical realization
are explicit premises, not a new supplier admission.

Let the 632 independent original logical fields be x_0,...,x_111,
y_0,...,y_111 and h_0,...,h_407. The nine initially arbitrary owned fields
are independent too; their displacement in the two inputs below is zero.
The full-row checker initializes all 641 independent columns, verifies their
owned clearing and retains all observation events, including after intended
exits. There are 5,897 full-frame touches, with 4,891 distinct nonzero rows.
The eight endpoint caches have roles C1,...,C8 (indices 633,...,640), at
frames 254,274,619,279,621,280,624,281, respectively; every frame has rank eight.
No current main X or Y value is silently appended to the channel.

## 2. Exact finite certificate

KERNEL.json supplies a scalar vector k on the 632 original roles, with 104
nonzero integer entries. Its Y block has just

    delta y_1=-2v, delta y_2=2v, delta y_12=-2v,

where v is one arbitrary whole-field value. The file gives every compensating
X and dirty-helper coefficient; no coefficient is inferred from an endpoint
label or a clean-helper assumption. All initial owned displacements are zero.
No support-minimality claim is made.

Write an actual normalized observation row as

    O_j = sum_(s,w) a_(j,s,w) w z_s,

where w is a reduced free word in the source warp letters and their inverses,
and a is an exterior rational scalar. The complete full-row replay checks

    sum_s a_(j,s,w) k_s = 0

for every word w of every retained full-frame row. It also checks that each
of the eight complete endpoint cache rows annihilates k. The free-word
histories contain 119,521 terms. This is not PR5447's 119,515-term actual
monomial canonicalization: six terms have not been identified by additional
one-column operator relations here. The new certificate is checked in the
stronger free-word grammar, using only adjacent inverse cancellation.

A separate direct-displacement interpreter starts with k_s v and executes
the same pinned instruction stream. It stores chronological words in the
opposite order and imports no primary parser/row code. Every one of the
5,897 full-frame events has zero displacement, including repeated/zero rows,
and all nine endpoint owned displacements are zero. This is a distinct
execution check; both implementations inherit the same source semantics.

Let M^T be the source's eight-by-112 `mode_columns` matrix. Exact arithmetic
on the supplied vector gives

    M^T delta y = (0,-4,0,0,0,0,0,0)^T v.              (1)

Thus the target ambiguity is not inferred from dimension counting or a
numerical nonmembership result: it has a complete input witness and nonzero
specified target image. Sparse rational elimination was used only to discover
the vector. Neither its rank nor its search procedure is a proof dependency.

## 3. Every positive width, and the actual physical target

At width f assign each free letter its actual conjugated backward native
operator lifted columnwise to f factors, with spectators unchanged. Assign
inverse letters inverse operators. A reduced-word cancellation remains an
operator identity. Exterior rational coefficients k_s and a_(j,s,w) are
applied once; they are not tensor-powered. Therefore the coefficientwise zero
above evaluates to zero at every positive width for every v. No independence
of actual monomial matrices, width-one sum relation, Gram lift or numerical
cutoff is required.

Physical values at a fixed chart differ from normalized rows by the chart's
invertible frame map. Zero differences remain zero at every observed full
or partial frame. Physical provider entry includes invertible birth frames,
input wrappers and its invertible helper basis/scalings. Hence the raw
logical displacement k v corresponds to two valid physical input states;
we do not claim that preparing that displacement is free.

To bind (1) to the actual consumer, distinguish raw logical y here from the
standardized physical input y_phys of the provider contract. The checker
evaluates all 112 literal input wrappers on all 512 one-column addresses,
including absolute phase, and establishes `B_Y,j=K_p,j`. Since raw Y enters
ground chart, `y_j=K_p,j y_phys,j`. The pinned provider establishes

    Z = diag(K_m^-1) M^T diag(K_p)/2,
    K_p,j R = R K_p,j,   Y_return=D y_phys,   R=DQ.

These monomial/full-Gaussian identities lift multiplicatively to every width;
the scalar owner coefficients stay exterior. Consequently the actual target
in raw input coordinates is

    b_k = (1/2) K_m,k^-1 R sum_j M_kj y_j.              (2)

No separate commutation of K_p with Q or D is asserted. Inserting (1) gives
zero change in seven target modes and

    delta b_1 = -2 K_m,1^-1 R v.                        (3)

R and K_m,1 are invertible, so (3) is nonzero for every nonzero v and ranges
over the whole target field. Two valid inputs have identical entire supplied
channels and identical other seven b modes, but arbitrary differing b_1.
No deterministic exact decoder of this channel can recover b, or any
nonconstant function of b_1 alone. Randomness cannot give a universally exact
decoder of indistinguishable inputs either. No approximation/error lower bound
or physical price lower bound is inferred.

## 4. Why helper versions matter

The checker reconstructs every coefficient of all eight cache rows and binds
their slot, chart, permutation and signed scale to PROVIDER.json:

    c_i = f_i (E_k h_original - M_k^T y),
    f_i = 1/(2 cache_scalar_i), k=mode(i).               (4)

For the new witness, `E delta h_original` equals the right side of (1).
The helper changes exactly hide the Y change in every cache. The old
fixed-helper ambiguity `(delta x,delta y,delta h)=(v,v,0)` is insufficient
here: the eight new caches genuinely add information. Eight separate controls
take y=M_k and x=y; full-frame values still agree, while exactly cache mode k
changes, using `M^T M=56 I`. We do not just reuse the earlier kernel.

If the **original** eight retractions `e=E h_original` were separately supplied,
(4) would give `M_k^T y=e_k-c_i/f_i`, and then (2) is an unrestricted linear
decoder for b. This is a changed observation interface; it does not establish
that e was retained, that an inverse cache-frame map is ordinary, or that the
required R action is free. Every such observation/transform and its retention
would need a physical bill before supplier use.

The tempting substitute `E h_current` is invalid. Fresh complete-row replay
proves `E h_current=0` at the raw WORD endpoint, for every original input.
For this witness `E delta h_original` has mode one equal to -4v, while the
same endpoint expression remains zero. Using it in the conditional decoder
would return zero change although the true target changes by (3). Freezing
the witness's helper displacements also exposes 821 full-frame observations;
the first is at zero-based event 16,366. Removing its X compensation exposes
924 observations, first at event 15,523. The roles and versions are substantive
parts of the impossibility statement.

## 5. Scope, consequences and credit

This closes the passive endpoint-cache candidate for this exact observer:
retaining all full-frame values and all eight already-created endpoint caches
still does not supply `ZQY_return` on unrestricted original inputs. It does not
exclude a different partial-frame history, an original-helper observation,
retained current Y, changed producer, new paid call or a relation restricting
the independent inputs. Ordinary output-basis operations cannot rescue this
channel: they combine already retained full-frame endpoints, and normalizing
or relabelling the eight caches preserves their zero differences. The whole
machine state is not claimed to be Y-blind. No recursive profile, selected
frontier, complete multiplication theorem or new kappa is asserted.

Credit Dillon Amburgey / dillona's PR5402 source and cache equations; Ali
Romman's cache/retraction and basis lineage; Mark/Matarener's PR5427 event and
versioned-history question; THU New Media Research Center's PR5447 full-frame
kernel and explicitly excluded partial-cache boundary; zxv's PR5415/5419
actual consumer and observer contract; Cao Yifan's native word and the
retained Cinna Davis, Dugongue, Chris R and native/phase/compiler/analytic
contributors. JoyboyBrian with substantial OpenAI Codex assistance.
Apache-2.0. No independent human or proof-kernel acceptance is claimed.
