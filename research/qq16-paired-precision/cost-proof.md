# A finite-width comparison with declared units

The literal words have the following complete local counts, independently
recounted by numeric-cost.py. All prices below are prescribed reference bills,
not lower bounds on optimal machines.

| Quantity | PR4015 | PR4106 |
|---|---:|---:|
| Unit ADD |1920|1820|
| Quarter ADD |896|896|
| CLEAR |416|416|
| Signed H1 calls |224|224|
| Monomial wrappers |448|448|
| Covers |352|352|
| Private peak |16|16|
| Logical scalar allowance |26944|26144|

Under the common sufficient width W=P+28+6(lambda-1) and quantum supplied by the
range audit, neither reference needs extra relative precision. If one allowance
unit is assigned a common positive tariff tau_L(W), the prescribed scalar
allowance decreases by exactly800 tau_L(W). This restates a logical allowance
comparison; it does not measure actual processor instructions or recursive cost.

For a distinct, explicit numeric reference, let N=2^(73lambda) complex payload
coordinates per owner. A complex unit ADD costs2N real adds/subtractions. A quarter
ADD costs2N exact shifts by two (one W-bit shift primitive per component) and2N adds/subtractions. The grid proof covers the two intermediate halvings without pricing two shift instructions. CLEAR costs2N zero stores.
A coordinate Gaussian line uses the direct C_q pair-first formula in range-proof.md: at most4N
real additions,2N exact halvings and4N component copies. There are lambda such
lines per rank-one H1 call. A signed monomial uses2N sign operations and4N copies; a cover uses4N copies. Each permutation writes2N components into one reusable complex buffer and copies2N components back to the original fixed external bank. This pays the return leg without relying on handle rebinding. Address construction, control work and physical movement tariffs are outside this numeric count.

Thus the prescribed numeric bounds per owner are

```
PR4015: (12352 + 2240 lambda) N
PR4106: (12152 + 2240 lambda) N.
```

The difference is **200N numeric word operations**, distinct from800 logical
allowance units. Their scalar-only numeric bills are8256N and8056N; unchanged
wrappers/covers contribute4096N and Gaussian interiors2240lambda N. The reference
can use at most930N+12 signed W-bit component slots:448 persistent complex fields,
16 private complex fields, one complex permutation buffer and12 scalar temporaries.
This counts logical numeric storage, not a verified placement or recursive native
workspace. The literal words never overlap private scopes with native calls.

For any common strictly positive primitive tariff tau(W), the reference bound
falls by200N tau(W). For example tau(W)=W gives the symbolic bit-operation reference
bill200NW less. This deliberately declares one uniform price for every counted
primitive; an actual machine can instead attach distinct positive prices, in
which case the only differing counts are200N real additions/subtractions, so the
saving is200N times their common-width price. Unchanged primitive counts cancel
only when both runs use the same tariff and implementation contract.

If candidate and baseline widths differ, the uniform-tariff break-even condition is

```
tau(W_candidate)/tau(W_baseline)
    < (12352+2240lambda)/(12152+2240lambda).
```

For tau(W)=W and W_candidate=W_baseline+Delta, this is
`Delta < 200 W_baseline/(12152+2240lambda)`. The logical allowance comparison alone
instead has ratio threshold26944/26144. Equal width satisfies both strict
conditions for every lambda>=1 and W>0. These are useful failure boundaries if a
later native/caller contract forces extra candidate precision; there is no claim
that the current sufficient W is minimal for either word.

The pair-first coordinate reference is an explicitly permitted implementation
premise for this numerical count. It is **not** a replacement at no cost for a
charged recursive H1 child. The actual child can have a different error/width
contract and tariff. Neither this count nor exact-grid execution prices physical
addresses, movement/placement, native recursive workspace, entry conversion,
recursive usage or supplier caps. Those obligations prevent admission of a new
supplier or a change in kappa. The result closes the relative scalar-width issue
in the declared finite arithmetic domain and gives exact conditions for extending it.
