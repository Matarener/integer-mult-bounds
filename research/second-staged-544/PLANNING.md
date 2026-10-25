# Conditional complete-invoice screen for a second 544 entry

This is a planning lemma. The tested circuit must independently realize the
assumed signature; neither a physical provider nor a kappa follows from it.
Credit PR4091's pooled witness and PR4088/4076/4085's provider invoices.
Exact cost reference: a29bdd8f56cd18b805917775cdec09ff935eddc4,
research/staged-fourth-mixture-ceiling/PROOF.md. Source words for the actual
boundary test are separately pinned at PR4076, not silently repinned to PR4085.

Let H_r=r^p, 0<p<1. THREE has width inventory
(28,18,56,93,213) for widths (5,6,7,8,9). FOUR changes one 8 to 7 and costs
an additional d=2H1+3H3-3H4 locally. The PR4091 pooled witness uses x=1080
FOUR calls out of3240. The baseline 32-bin pattern counts include10620 of
(7,7,9,9),58320 of(6,8,9,9),1620 of(9,9,9),90720 of(5,9,9,9).

Assume a hypothetical new THREE provider changes exactly one width7 to6,
has local delta delta=3H1+H2-2H3, and has no other changed charges. For any
integer0<=y<=1080, replace y FOUR calls by this new provider. Set x=1080-y;
change just the first two pattern counts to10620-y and58320+y.
Every bin count remains unchanged. Width6 demand increases by y, width8 by y,
width7 decreases by2y, and all other widths are unchanged. All item demands
therefore match. Both changed patterns fill capacity32 completely, so all
residual child ranks remain unchanged. No helper or bin is discarded.

The complete paid cost difference is

y*(delta-d)=y*(H1+H2-5H3+3H4).

It is strictly negative for y>0. To see this for every0<p<1, let c=(1,1,-5,3)
at ranks(1,2,3,4), and S(t)=sum c_r min(r,t). Then S is0 on[0,1],
1-t on[1,2],3-2t on[2,3],3t-12 on[3,4], and0 above4.
It is nonpositive and negative on(1,4). The identity
sum c_r r^p = p*(1-p)*integral_0^infinity S(t)*t^(p-2)dt
proves the assertion. The finite integral is well defined since S vanishes
outside[1,4]. At p=1 the paid rank mass difference is zero.

This supplies a favorable fully charged *pooled* nomination, conditional on
the signature and unchanged contracts. It relaxes chronology, physical-family
exclusions and actual source windows. The target helper544 must admit the
new entrance and exact dirty restoration. Receiver-sharing composition,
other local frame cascades, native wrappers, private buffers, numerical/stock
costs and complete physical admission remain obligations. A failed exact
frame boundary invalidates the nomination before any exponent comparison.
The source's selected frontier and all-size transfer assumptions remain unchanged.
