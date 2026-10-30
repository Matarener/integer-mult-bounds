# Solver equivalence and scope

The mathematical background is ordinary Gaussian elimination over a prime
field. The contribution is its application to the measured P104 fold bottleneck,
the opt-in substitution and the complete-command evidence. No priority claim
is made for the elimination algorithm.

Let p = 2147483647. For an m by n integer matrix A and vector b, the retained
`rp.solve` returns None when Ax = b is inconsistent. Otherwise it selects pivot
columns from left to right and sets all free coordinates to zero. It obtains
that solution by fully reducing the augmented matrix.

The new solver eliminates only below each pivot, then substitutes backwards.
Both algorithms perform the same row selection, normalization and elimination
on the unprocessed rows. Eliminating entries above a pivot has no effect on
those rows. Induction on the pivot index therefore gives the same pivot columns
and the same unprocessed submatrix in both algorithms. Rows below the last
pivot have zero coefficient entries. A nonzero right-hand entry on such a row
is exactly the inconsistency condition. The original augmented-matrix reduction
detects this by selecting the augmented column as a pivot.

In the consistent case, restrict A to its selected pivot columns. These columns
are independent and span its column space. Thus there is exactly one solution
supported on those columns. Back substitution and full reduction both produce
that solution. Every other coordinate is zero in both outputs. This covers
rank deficiency, zero rows, zero columns and empty matrices. Neither algorithm
needs an inverse of a zero pivot.

All calculations in the replacement use signed 64-bit integers after modular
reduction. A product of residues is less than p squared, which is below 2^62.
The elimination subtraction occurs after reducing its product, so its absolute
value is below p. During back substitution, at most 4096 reduced products are
summed, giving a sum below 4096p and hence below 2^43. There is no signed overflow
in these operations. Each matrix dimension is checked to be at most 4096 before
the working matrix is allocated. The supported interface accepts integer NumPy
arrays and copies its inputs; it rejects noninteger or incompatible arrays.

The substitution changes only the function called as `rp.solve`. The source
coefficient construction, projection seed, candidate order, Newton iterations,
rational reconstruction, builder, legality check and pricer retain their exact
bytes. Equality of the returned solution, including None, therefore preserves
every later deterministic computation in this pinned command. The finite replay
checks the complete emitted word as JSON, rather than compressed container bytes.
All ten timed commands produce the same canonical word digest and fold status.

This is not a proof that the retained toolkit's projection or legality oracle
certifies every mathematical obligation of a P104 supplier. Their scope is
inherited. No native-phase, physical caller, uniform compiler, precision, BIT,
outer or selected-frontier result is established here.

## Resource and code constraints

All new loops have finite bounds: at most 4096 pivot or substitution steps,
50 retained source entries, 1234 small-system fixtures, five rejection controls,
two integration commands and at most ten benchmark pairs. Each child command
has a timeout. Every new function is below 60 physical lines. New verification
conditions use explicit exceptions and remain active under optimization.

Power of Ten rule 3 requires a managed-runtime deviation in `solver.py` and its
NumPy callers. Python and NumPy allocate arrays and temporary values during
elimination. The dimension cap bounds each array by 4096 by 4097 entries and
the implementation has no unbounded queue or retained history. A working array
uses less than 129 MiB; the source matrix and elimination temporaries add further
bounded arrays. This is a capacity argument, not a measured peak-RSS claim.
Replacing NumPy with a fixed-buffer implementation would be a separate change.

Rule 9 requires one explicit integration deviation in `runtime.install`.
The opt-in adapter binds `rp.solve` to the replacement function in a fresh
process. Its only possible targets are the retained baseline and `solver.solve`.
The retained files are authenticated before import, and no predecessor file is
edited. The baseline/candidate complete-command comparisons exercise both
targets. A future toolkit-owned parameter for the solver could remove this
binding step.

The unchanged predecessor closure has its original coding conventions. This
package does not refactor that code or claim it satisfies the new-code rules.
Warning-strict execution reports unclosed-profile-file ResourceWarnings in
`tkcommon._load_data_profiles`. The files are closed by their finalizers; the
warning is not suppressed. Rule 10's limitation is confined to this frozen
predecessor import, whose exact bytes must remain preserved. A toolkit-owned
change to scoped profile reads would remove it. New-code syntax and warning
checks remain enabled.
