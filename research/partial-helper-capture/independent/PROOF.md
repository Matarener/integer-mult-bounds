# Independent partial-capture proof and paid-frame invoice

This is an exact local proof and independent finite invoice for the two frozen
PR3945 words carried by PR4061. It is not a formal-kernel proof or independent
human review. The mathematical model is the pinned BORROW-WORD format, including
its existing source/helper entrances, terminal frames, center-service billing,
native warps, and literal inverse cleanup. No project checker is imported.
`check.py` uses exact rational matrices and reduced GF(2) row bases; PR4076's
`audit_core.py` was read only to establish the format's frame/cleanup contract.

## Exact arbitrary-input operator

Both source files have the same eight ADDs at zero-based `B[77:85]`, with the
same frame representative `[45]` and coefficient magnitudes `1/4`. Their byte
hashes are checked against both fixed constants and `SOURCE-EXPORT.json`:

| word | SHA-256 |
| --- | --- |
| base | `08e6c96fbe3dfec96cb8451b3867ef8c1a214109ecd1e5af7fcc28e0f05728d0` |
| extra | `d83c2ec9cecc0ad092d34ea4080b28a4fd7199579356b6d5a8fc6cd53ff93299` |

The uncompressed words are not asserted identical. In coordinates
`(a,b,u,v,w,z)=(600,601,123,175,183,202)`, their local map is

\[
M=\begin{pmatrix}
1&0&0&0&0&0\\
0&1&0&0&0&0\\
-1/4&1/4&1&0&0&0\\
1/4&1/4&0&1&0&0\\
1/4&1/4&0&0&1&0\\
-1/4&1/4&0&0&0&1
\end{pmatrix}.
\]

All six entering values are arbitrary. A zero *frame* means the zero binary
subspace, not a promise that the value stored in that register is zero.

Retain the original four updates to `u,z`, in original relative order:

```
z -= a/4
u -= a/4
z += b/4
u += b/4
```

Then execute

```
a += b
w += a/4
v += a/4
a -= b
```

During the two agreeing-target reads, the value of `a` is its entering value
plus the entering value of `b`. The final subtraction restores `a`, while `b`
never changes. The targets receive exactly the four rows of `M` displayed
above, retaining their arbitrary entering values. The matrix has determinant
one and inverse obtained by negating its lower-left four-by-two block. This is
an identity over the rationals and therefore also over the complex numbers;
checking all 36 matrix coefficients proves every input, without numerical
sampling or an assumption of clean helpers or targets.

All local gates use the same fixed representative `T_[45]` after each operand
reaches that frame. Hence the logical identity lifts to equality of physical
operators with the same entering and outgoing frames. For block-diagonal
frame operators `D_in,D_out`, the original and candidate both realize
`D_out M D_in^{-1}`. Binary-span equality between different representatives is
not being used. Substitution into the unchanged surrounding word is therefore
valid on every full dirty input, without replaying a complete full-word symbolic
operator or assuming an endpoint theorem for the predecessor.

## Sharp fixed-boundary frame lower bound

The independent chronological replay checks these six block boundaries on both
words, before and after the rewrite:

| register | entering frame | outgoing frame |
| --- | --- | --- |
| 600, 601 | `[45]` | `[45]` |
| 123, 175, 183, 202 | `[]` | `[45]` |

Assume the same six physical registers, the same boundaries and monotone frame
growth inside the block. Scalar couplings may otherwise be arbitrary, subject
to the format's common-frame operand rule. Each target starts at dimension zero
and ends at dimension one. The positive dimension increments on that target
are nonnegative integers summing to one. Thus each target pays exactly one
rank-1 climb. Different physical registers have separate child calls under the
existing single-register child ABI. Therefore every such rewrite pays at least

\[
H_1\geq4,\qquad \sum_r H_r r^{1-\alpha}\geq4.
\]

The four unavoidable target calls contribute exactly four; added registers or
other permitted paid work can only add nonnegative charges. The original block
and the explicit partial capture both attain `H_1=4` and no other local child.
The source helpers already enter at `[45]`, so neither has a positive local
climb to remove. This establishes a local optimum under the specified
boundaries, irrespective of scalar coupling choices. It does not establish a
global optimum after changing outside boundaries, crossing other events,
descent/reset permissions, physical target ownership, or the child ABI.

The candidate retimes target climbs inside the block: originally 183, 202, 175,
123 climb at B77, B78, B79, B80; in this candidate 202, 123, 183, 175 climb at
B77, B78, B82, B83. Their per-register frame paths are unchanged. This is not a
claim that the four chronological event indices are identical.

## Literal and canceled cleanup

The format omits target-destination gates from inverse cleanup. The only new
non-target gates are `a+=b` followed later by `a-=b`. Reversing and inverting
therefore inserts the adjacent FULL-frame pair

```
a += b
a -= b
```

at cleanup index 1225. Both helpers terminate at FULL and have no restored-helper
backing substitution. The pair is the identity on arbitrary inputs in the same
FULL frame. The unsimplified literal recipe increases from 5,225 to 5,227
records. Canceling this exact adjacent inverse pair returns the complete
original 5,225-record cleanup list, byte-for-byte at the gate-data level after
frame-basis normalization. Consequently the original cleanup remains
*semantically sufficient* for the candidate. It differs from the unsimplified
literal inverse list. A checker may reject that old list for literal-recipe
noncompliance, but must not call it a semantic failure.

## Complete invoice on both frozen words

Every positive native climb is reconstructed, including read-only source
operands, center-service descents, frame-only terminal promotions and all native
warps. All frame containments, warp images and externally prescribed frames are
checked using separate GF(2) elimination. Positive climbs are compared in
chronological order within each physical register, including their old and new
frames. No positive source visit disappears.

| item | original | literal capture | capture with pair canceled |
| --- | ---: | ---: | ---: |
| local forward ADD records | 8 | 8 | 8 |
| local source reads, 600 / 601 | 4 / 4 | 4 / 4 | 4 / 4 |
| local writes to helper 600 | 0 | 2 | 2 |
| local target writes | 8 | 6 | 6 |
| cleanup records | 5,225 | 5,227 | 5,225 |
| complete-word ADD records | 16,230 | 16,232 | 16,230 |
| complete-word SCALE records | 1,164 | 1,164 | 1,164 |
| complete executed records, including warps/corrections | 17,598 | 17,600 | 17,598 |
| source reads in complete word, 600 / 601 | 7 / 7 | 7 / 9 | 7 / 7 |
| source writes in complete word, 600 / 601 | 10 / 10 | 14 / 10 | 12 / 10 |
| positive native child calls | 3,549 | 3,549 | 3,549 |
| positive native rank mass | 5,160 | 5,160 | 5,160 |

The complete native histogram is unchanged:

`{1:2482, 2:712, 3:218, 4:109, 5:20, 8:8}`.

The complete helper-width inventory is unchanged:

`{5:28, 6:18, 7:53, 8:96, 9:213}`.

Helpers 600 and 601 each have entrance dimension one, terminal dimension nine,
width eight and the same five paid climbs `(4,1,1,1,1)`. Their exact positive
source-access addresses are:

| helper | B positions | terminal |
| --- | --- | --- |
| 600 | 936 (rank 4), 948, 1470, 1472 (rank 1 each) | rank 1 |
| 601 | 937 (rank 4), 949, 1474, 1476 (rank 1 each) | rank 1 |

`RESULT.json` contains the exact binary bases for every displayed source climb,
the full histograms, endpoint widths, per-stage read/write counts, source-byte
pins and a digest of all positive per-register chronological paths. The
verifier reconstructs the complete list; the report digest does not replace
that computation. Because this invoice is identical, any recursive power bill
with fixed caller normalization and the existing child/hosting contract is
identical for the two words. The unsimplified literal recipe increases scalar
work; canceling its inverse pair recovers the original scalar record count.
Neither version supplies a recursive-cost saving. Physical tape/controller
costs or approximation error are not newly certified by this format-level
comparison.

## Reproduction, controls and sources

From the repository root, standard-library Python:

```
python3 -B research/partial-helper-capture/independent/check.py
```

The default performs no writes and compares the deterministic result against
`independent/RESULT.json`, including the verifier's own SHA-256. To emit a fresh
receipt, use `--output` with an absolute path. The expected marker is
`PASS_PARTIAL_CAPTURE_INDEPENDENT`.

Defect-sensitive controls reject an agreeing-target sign error, capture sign
error, missing undo on arbitrary dirty sources, wrong common frame, an unpaid
read-only source frame, and a wrong cleanup inverse sign. The missing-undo
control also demonstrates why zero-source tests fail to detect that error.
Literal-list inequality and semantic sufficiency after pair cancellation are
tested separately. The construction worker's verifier was first read after
`INITIAL-DERIVATION.md` was saved. PR4076's retained audit core was read earlier
as the frame/cleanup format contract, as explicitly recorded in that initial
derivation. Neither implementation is imported at any point.

Credit: Dugongue's PR3945 words; Riquelme Soares (@hevlyo)'s PR4061 extraction,
signed-column test and explicit partial-capture follow-up; PR4045's selection
of the relevant actual helpers; PR4048's same-frame signed-capture idea; Rohan
Arun's PR4076 retention of Sagar Thakrar's PR3687 BORROW-WORD audit code, itself
crediting Arham Tahir's frame/cleanup reading. Exact exported source heads,
paths and Git blobs are
recorded in `SOURCE-EXPORT.json`. This independent derivation/checker was
produced with substantial OpenAI GPT-6.1 Sol assistance. Source material is
Apache-2.0; see the package license and notices.

No complete physical supplier, full recurrence improvement, new kappa,
selected-frontier change or broader impossibility theorem is claimed. Changed
helper entrances or terminals, larger capture sets, cross-block retiming,
different physical ownership or higher-rank delivery contracts remain open.
