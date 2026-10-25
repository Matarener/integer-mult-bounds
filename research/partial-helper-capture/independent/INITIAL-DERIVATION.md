# Initial independent derivation

This derivation was saved before reading another worker's construction code.
Only the two frozen words, their export/provenance records, the predecessor
README/TASK, and PR4076's `audit_core.py` frame/cleanup format contract were
read. The independent verifier will not import that module or any construction
checker. This is AI mathematical review, not independent human review.

Let `a=ell_600`, `b=ell_601` and order the four arbitrary target inputs as
`(u,v,w,z)=(ell_123,ell_175,ell_183,ell_202)`. The source bytes at zero-based
`B[77:85]` on both frozen words give

`(a,b,u,v,w,z) -> (a,b,u+(-a+b)/4,v+(a+b)/4,w+(a+b)/4,z+(-a+b)/4)`.

Every gate here uses the identical frame list `[45]`. Take the four retained
updates to `u,z` using the original `a,b`, then execute

`a += b;  v += a/4;  w += a/4;  a -= b`.

The helper pair is restored for every dirty `a,b`; each target retains its
arbitrary entering value. This is an identity of rational 6 by 6 matrices,
not a clean-input test. The matrix has full rank six, with inverse obtained
by subtracting each displayed source contribution from its target.

There are eight forward ADD records before and after. Source reads remain
eight in total (four from each helper): the two discarded reads of `b` for
agreeing targets are replaced by its two capture/uncapture reads. The helper
`a` gains two writes; target writes fall from eight to six. The source-only
subword is `a+=b; a-=b`, so its reverse inverse cleanup is again an adjacent
inverse pair once target writes are omitted. The literal inverse generator
therefore adds two records, but exact scalar cancellation removes both with
no semantic defect. Old cleanup can consequently be algebraically sufficient
even though it is not the unsimplified literal generated list.

At the block boundary all six registers have the same physical frame as
before. Therefore, for any fixed invertible representative `T_[45]`, the
logical scalar matrix identity lifts to exactly the same physical operator;
there is no appeal to binary-span equality between different representatives.
The added helper shears occur at their existing frame and cost zero native
climb rank. Both helpers remain read in `[45]` by the retained targets 123 and
202. Native source/target climbs and fixed entrance/terminal boundaries do not
change under this explicit rewrite. Endpoint widths therefore do not change.
Full-word chronology and histogram checks remain to be implemented.

Scope: the explicit partial capture of this block, or a comparison that keeps
all external frame boundaries and their paid itinerary fixed. This is not a
lower bound against changed helper entrances/terminals, other source pairs,
retiming across outside events, changed child contracts, or global resynthesis.
Even exact scalar cancellation of the added cleanup gives no paid recursive
child saving. No supplier or kappa improvement follows.
