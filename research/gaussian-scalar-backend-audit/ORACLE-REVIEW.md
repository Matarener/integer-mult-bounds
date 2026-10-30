# Independent scalar oracle proof/code review

No blocking finding was found in the first-frozen oracle core and proof. Reviewed `oracle.py` SHA256 `2f8affd40c49f97f1e15851a80deb4619053684cb2b2d9b07f3bb3eb48cb6b18` and `PROOF.md` SHA256 `55d9ac7e59a48208876cf23384278bcb16678aff571c6e2f0012d707abf5b113`, plus the first freeze and independently chosen self-test/smoke receipts. No scientific program was rerun for this review.

## Universal scalar correctness

The positive arcsine expansion is correct: pi=3 sum binom(2k,k)/(16^k(2k+1)), with successive-term ratio (2k+1)^2/[8(k+1)(2k+3)]<1/4. The exact positive tail is bounded by 4/3 times the next term. The source loop returns the exact rational partial sum and this tail endpoint, so it encloses pi, meets its tolerance, and terminates for every positive rational tolerance.

For a non-shortcut factor f, the chosen pi tolerance is epsilon/[16 max(1,f)], which bounds the constructed exponent width by epsilon/16. The helper reduces to [0,1/4], and its alternating Taylor lower/upper partial sums correctly alternate by degree. Their gap tends to zero, establishing termination at every positive tolerance. Mixing the lower bound at the upper argument and the upper bound at the lower argument uses the correct decreasing orientation of exp(-x).

The initial Taylor endpoints are within [0,1]. Outward dyadic rounding retains that range because zero and one are exact grid points; repeated squaring is monotone there. The proof's initial width 13 epsilon/(128 D), post-squaring width below7 epsilon/64, and final width below39 epsilon/64 follow from the stated local tolerances and at-most2q rounding errors. Thus the explicit output width/range guards follow from a universal bound, not an assumption that a runtime guard will pass.

The zero branch is exact. In the tiny branch x<=epsilon/4, the lower inequality 1-x<=exp(-x) and exact upper one are sound; outward rounding on the epsilon/4 grid has width at mostepsilon/4. In the huge branch 3f>=bits, pi>3 and e>2 imply exp(-pi f)<2^(-bits), so [0,epsilon] is valid. Neither shortcut changes the pi enclosure contract. Every branch and range-reduction loop terminates for accepted finite rational input under exact integer/Fraction arithmetic. No precision-independent runtime or physical preparation bound follows.

The parser rejects JSON floating numbers/constants, negative factors, boolean factors/precisions and insufficient precision. Internal correctness uses explicit `require`, not removable assertions. The core imports no predecessor, adapter, source interval implementation or external numerical library. Initial provenance explicitly discloses that the root described the source's method in words, while no implementation, numeric source outputs or queries had been read before freezing. This supports the documented implementation/code independence; it is not a claim of independent human acceptance or uncorrelated mathematical errors.

## Meaning of finite containment checks

Let y be the true scalar and O an independently certified oracle interval. If the exact comparison proves O is a subset of the actual source interval S, then y in O implies y in S. This is a valid finite source-enclosure certificate for that queried f and precision, relying on the oracle's written universal correctness and exact rational comparison. It does not establish source enclosure for unqueried inputs or source width/termination at every precision; the separate WIDTH-AUDIT proves that universal implication.

Overlap alone, O intersect S nonempty, does not establish that S contains y. The reverse inclusion S subset O also does not establish it without an independent proof of S. The actual query adapter must therefore identify which containment direction is tested, bind each f/precision to authenticated source outputs, and retain complete coverage/counts. Input-only query processing after first freeze may preserve oracle independence from source numeric outputs. It must not be described as pre-freeze independent choice of those query inputs.

This review does not yet approve the later query checker, source adapter, query-result provenance aliases or final package seals; those are separate artifacts to review after freezing. Existing first-freeze self-tests are corroboration and controls, not the universal proof or complete caller acceptance. Leading-section inverse, full circuit, raw gauges/normalization, source root/caller integration, delivery and outer theorem obligations remain outside the oracle.
