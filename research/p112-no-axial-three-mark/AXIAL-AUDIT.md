# Independent audit of the axial normal form

21 October 2026. PASS for the support-monotone normalization and the bound
`cost >= 12+n-3a`. This is a written proof audit using the previously checked
geometry; no new coefficient search, invoice solver or literature claim.

Keep the precise hypotheses: three ordinary two-copy canonical marks in three
distinct paired roles, query matrix `C A`, exact endpoint `C C^T`, arbitrary
rational actual readers, and whole-group binary-rank tariffs.

After restricting readers to the six marked ports, absorb each axial query's
nonzero scale into its reader. Queries on one axis have the same physical
source closure. Their merged reader support lies in the union of the old
supports. Rank of the corresponding concatenated pairing blocks is at most
the sum of their ranks, so the merge cannot increase the invoice. Removing
zero products gives normalized counts n and a, with a<=3. The counts need
not agree with the original factorization's term counts.

For an axial term the source span has dimension six. The ambient binary
pairing is nondegenerate in dimension nine, so its annihilator has dimension
three. The established reader-span bound gives tariff at least k-1, where
k is the number of its selected reader triads. If h of those readers occupy
its own two marked ports, their full triads give an identity submatrix of
size3h: each own triad is orthonormal and the two are mutually orthogonal.
Thus tariff >= max(k-1,3h). This is at least k+h-2: use k-1 for h=0,1, and
3h=6 with k<=6 for h=2. Non-axial terms retain tariff >= k+1.

At each output port, a sole active query must be proportional to the desired
marked unit vector. It is therefore its own axial query. Uniqueness of the
merged axial query per axis means every output with only one reader incidence
is counted in H=sum h; H may also count ports with more incidences, which only
weakens the lower bound. Hence I=sum k >=12-H. Summing the term tariffs yields

    cost >= I+(n-a)+H-2a >=12+n-3a.

A hypothetical cost<=17 consequently has n<=5+3a. The retained at-most-five-term
floor excludes n<=5 independently of axial count. Thus the remaining normalized
ranges are n=6..8 for a=1, n=6..11 for a=2, and n=6..14 for a=3. The a=0 case
is already closed. These are necessary bounds, not existence statements.

This audit does not claim a result for exterior queries, repeated paired roles,
residual-bearing or singleton marks, or changed fitting endpoints. Neither a
support-only feasible solution nor the systematic non-Fano suggestion in the
research note has been verified as an exact cheaper decoder.

Separate AI-agent proof audit; no independent human or formal-kernel review.
