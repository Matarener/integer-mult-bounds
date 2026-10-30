# Final scoped package review

Reviewed the root-authored README, verifier wrapper, finite-control checker,
and source checker in `research/bit-joint-dirty-pair`. The all-parameter proof
was checked only for consistency with those claims, not independently
re-reviewed by its author. No full suite was rerun. The root owns final normal,
optimized, read-only-export, and mutant runs; their manifest/results were not
complete when this review began.

## Verdict

No remaining blocking mathematical or implementation finding in the reviewed
bytes. One source-to-execution binding issue was reported and fixed during
review. The README accurately limits the optimum to the uniform unary-query
full-endpoint model and keeps native packing and changed-tail questions open.

## Reported issue and verified correction

The initial `verify.py` hashed each child source and subsequently executed its
pathname. The bytes executed were therefore not bound to the authenticated
snapshot. This was an integrity gap, not a counterexample to the mathematics.

The corrected `verify.py:10-17,44-47` bootstrap reads the child once, compares
its hash with the retained manifest value, and compiles those identical bytes.
It sets the correct `__file__` and `__name__` and retains isolated/optimized
interpreter flags. At lines50-57 the expected receipt is parsed from the
authenticated bytes, and package bytes/inventory are checked again afterward.
A focused wrong-hash subprocess probe rejected with
`executed checker hash check.py` before producing any checker output. This
probe did not execute either full checker.

## Claim and capacity checks

- **Full endpoint and clean continuation (README:42-52).** The source pair is
  compared at a common cut with all ordinary rows independently arbitrary.
  The same injective suffix must act on the same extended state space. The
  added clarification correctly gives new ancillary slots identity
  continuation, or an identical injective continuation in both words. Later
  new cleanup gates change that extended suffix even when old records remain.
  The corresponding clarification was added, under explicit parent ownership
  authorization, to the proof's application paragraph. Public-output equality
  alone remains insufficient.

- **Product carrier (README:94-101).** The proposed encoding is injective:
  with `H(x,y)=f(x)+g(y)` and `c=f(0)`, recover
  `g(y)=H(0,y)+c`, `g(0)=H(0,0)+c`, and
  `f(x)=H(x,0)+H(0,0)+c`. A linear address map fixes zero, so the same slice
  identities decode after applying `diag(p,q)`. Reordering the two address
  halves identifies this map with `S(P direct_sum Q)`, whose projector rank
  is four. However the carrier has `N^2` VALUE cells plus the anchor, versus
  `2N` original cells. The text does not invoice this larger payload as a
  native original-size rank-four call or omit the unpriced encoding/cleanup.

- **Tagged interface (README:103-110).** Choosing `p` or `q` according to a
  bank tag is not the stated single linear partial swap on the original
  address carrier. Conjugating one target to a common label does not make the
  bank's address adapters free. The text preserves both missing obligations:
  an admitted joint primitive and its actual carrier/adapter tariff.

- **Hypothetical margin (README:112-117).** For `x=2^(1-b)` in `[1,2]`,
  `Phi_m(4)=m^b x^2` and the optimistic saving is
  `m^b*x*(2-x)=m^b*(1-(x-1)^2) <= m^b=Phi_m(1)`. Thus one extra ordinary
  positive-rank query eliminates any strict saving under this hypothetical
  price. At `b=1` it exactly consumes the margin; at `b=0` the initial margin
  is zero. No positive saving is claimed. This is a necessary overhead screen,
  not proof of an implementable tagged supplier.

- **Tariff and geometry scope (README:3-16,37-40,54-90).** The price parameter
  `m` is separated from address half-dimension `d`. Distinct/noncommuting
  rational projector geometry is not used as a faithful representation of
  payload `F_2[G]`. The finite-field kernel example supports the caution, while
  the actual uniform lifting step remains a written proof. The minimum is
  conditioned on a fixed finite word, scalar address-independent free gates,
  one VALUE stream per paid query, and the complete endpoint.

## Code coverage assessment

`check.py` correctly implements bit-packed GF(2) row elimination and matrix
multiplication for the stated dimensions. The 32768 Sylvester cases are all
512 binary 3-by-3 matrices times all64 binary 3-by-2 matrices. Its four-column
and one-output positive controls prevent treating the three-column/two-output
obstruction as universal. The direct permutation controls measure Boolean
defect rank, rather than merely substituting the predicted formula. Their
coordinate-projector samples are expressly finite controls, not an exhaustive
test of all rational projectors. The S4 toggle computation really sums all24
distinct formal labels and cancels on every F3 address; the F5 tuple has24
distinct images. No fixed-field faithfulness is inferred.

`source_check.py` authenticates the frozen compressed inputs before
decompressing those same bytes. Its prefix replay checks660 independent
columns, common frames, private-slot guards, and the exact inverse. The quiet
window predicates cover both reads and writes of the two selected helpers;
therefore moving the two queries across that window does not silently cross a
reader. Local retiming compares every row and frame and checks its literal
inverse. Exact rational geometry reconstructs P,Q from the supplied lines,
checks idempotence/rank/nesting/dyadic entries, and verifies the specified
commutator and nonzero rank-four minor. These are sufficient for the stated
source pair; they are not a new full-word precision or changed-tail audit.

The wrapper compares complete canonical JSON receipts, including Boolean
values distinct from integer one, and all substantive checks use explicit
exceptions rather than assertions. This supports equal normal/optimized
coverage, subject to the root's pending complete executions.

The omitted-query negative control in the source checker accepts any
`ValueError`; its current fixture is rejected by the next frame contract.
Making that control reason-specific would be optional hardening. No present
claim relies on interpreting an unrelated exception as a mathematical proof,
and this review does not treat that stylistic improvement as a blocker.

## Reviewed content hashes

| File | SHA256 |
|---|---|
| README.md | `b307851d4260d59391ff77c25a7332baf81bba59f8843a98e77b97959ab8f3b1` |
| verify.py | `bcb67a10939ba0b5c42005972f2c9bf9bb7e0dad8d1067c17b10ec179a9abfc0` |
| check.py | `c1cf94026e5733784dfa1d92ba007a7b6e2d3148e33e7daf88630cdfdef7c01b` |
| source_check.py | `cfd840feef006198d3efe27560cf034719dea6831825e48b466360851b7bf421` |
| PROOF.md (consistency only) | `be917cba2bac53328ca6471c9a40720b11b3b686d93d3654758be9c10e1c7e69` |

This review does not certify the not-yet-generated manifest/receipts, a native
cost conversion, publication, human review, or a formal-kernel theorem.
