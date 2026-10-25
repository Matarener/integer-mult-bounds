# Volume normalization of the support gates

The support statements and exact operator identities in this lane are
unweighted and do not require equal helper volumes. Extra arbitrary
dirty banks are included in the full bank/address matrix.

A conclusion from unweighted native rank mass to the complete moment
uses the separately stated **equal-volume full-bank native-child
normalization**: each width-m field has the same physical volume,
rank-r children have their retained `V/2^(r f)` slice multiplicities,
and the full independent-output stock is n equal-width fields. Fixed
positive relative helper volumes alone do not justify replacing that
weighted moment by an unweighted rank-mass sum.

Growing ADDs require the parent's positive-volume literal-full-scan
premises in [FULL-SCAN-TRANSFER.md](../root-joint/FULL-SCAN-TRANSFER.md).
Partial/local scans, a fused implementation and different owner volumes
must retain their real weights. The support gate by itself neither
admits nor excludes those implementation changes.

The optional individually paid source-circuit extension has the same
boundary. In the exact telescope for R, replace each monomial S_s by
an invertible source circuit of row-branching resource
`b_s=sum(native_arities)+binary_ADD_count`. R then has support at most
`2^(2qf+sum_(s in{1,2,5,7,...,k}) b_s)`. Its added resource is a subset
of the resources paid in the prefix. Therefore separate additive
accounting cannot remove the native/scan support deficit; the source
charge cancels any relaxation of the cleanup lower bound. A source
circuit fused with the existing J query is a changed invoice and is
not covered by that additive argument.
