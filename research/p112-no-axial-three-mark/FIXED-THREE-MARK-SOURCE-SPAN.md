# Complete canonical-source closure at one fixed three-mark placement

21 October2026. New written deduction with a small exact geometric certificate; checked by a separate AI agent. No new multiplication bound.

Fix the three canonical indicator columns c0,c1,c2 on {0,67}, {7,64}, {1,75}. Let C have those columns. Allow ANY finite number of rational queries Q=C A and arbitrary rational actual readers R such that Q R=C C^T. After restriction to the six marked actual reader ports and merging parallel axial queries, every factorization with invoice at most17 would have at most five terms. The already published five-term triple floor then rules it out. Thus the complete canonical-source family at this fixed placement has minimum18, attained by its three canonical projectors.

The new self-contained theorem is the reduction to at most five terms; the final all-term floor explicitly uses the retained five-term theorem from PR3684 at fad2e401ff63c634fb04e47146b0323449af70dd, research/p112-triad-matroid-boundary/PROOF.md and COST-PROOF.md. That result is present in canonical main12fa8c5c844be21bfefb38a19503fbd867a11244. Its archival merge does not imply independent mathematical acceptance. This note does not replay the old full classification.

## Normalization

Every reader column outside the six marked ports reconstructs zero and may be set to zero separately. This preserves the endpoint and weakly reduces every tariff. Normalize an axial query proportional to c_j to c_j by absorbing the scalar into its reader. Replace all terms with that same axial query by c_j times the sum of their readers. New support is contained in the old reader union, and fixed-source rank subadditivity makes this operation tariff-nonincreasing. Remove zero terms. Let n be the normalized active count. There is at most one axial query for each marked axis.

Because the three canonical supports are disjoint, a query with coefficient support sigma has exactly the physical source groups belonging to those marked axes. Every restricted reader uses some subset T of the six distinct physical groups, with one actual reader port in each. There are only7*63=441 nonzero support types, regardless of coefficient values or term count.

## The complete small tariff certificate

The six physical groups in marked-port order are17,18,29,30,31,32. Rebuilding the exact binary full-group pairing ranks yields:

- All support types cost at least2.
- Exactly one costs2: source sigma={c1}, reader T={75}, i.e. group32, the second copy of c2.
- Exactly41 types cost3, and every one has a singleton reader.
- Every type with at least two reader ports costs at least4.

The complete tariff histogram is {2:1,3:41,4:1,5:33,6:197,7:16,8:152}. The coefficient/reader masks for the unique cheap type are(2,32). The script authenticates both input hashes, canonical targets and physical groups, all441 tariffs and all12288 fixed-axial source-union subadditivity checks. Its compact digest commits the complete table.

## Why six or more normalized terms cannot cost17

After axial merging there is at most one cost2 term, because the only cheap type has axial source c1. Every other active term costs at least3. Hence

    cost >= 3n-1.

If n>=7, the invoice is at least20. If n=6 and cost<=17, equality in this lower bound is forced: one cost2 term and five cost3 terms. Every one has exactly one reader port. All six required endpoint columns are nonzero, so each of the six ports must be assigned exactly one of these six terms. The cost2 term would then have to reconstruct the c2 output at port75 using a nonzero multiple of c1 alone. The indicator columns are independent, so that is impossible. Thus n=6 also cannot cost<=17.

Consequently every hypothetical cheaper factorization reduces to n<=5, preserving the exact endpoint and without increasing cost. The cited five-term triple theorem excludes it. This argument treats arbitrary rational coefficients, dependent queries, null cancellations and asymmetric copies. It does not classify coefficients or enumerate reader products.

## Scope and next question

This closes every canonical-source query dictionary at this fixed three-mark placement, including the seven-query systematic non-Fano completion, regardless of term count. It does not close other placements, repeated roles, more targets, exterior directions, or changed endpoints. No claim is made that the n>=6 subfamily itself attains18; the whole family attains18 using three canonical terms.

The new reduction could be reproduced independently by rebuilding the441 table with a different binary-rank implementation. The tiny key premises are the unique2-cost off-axis singleton and the fact that every cost3 type is also singleton-reader. If these premises occur at another proposed placement, the same proof applies there, but no placement census is asserted or run.

    python3 -I -O -Werror -B research/p112-no-axial-three-mark/fixed_three_mark_source_span.py

Default execution checks its compact receipt read-only; --write-receipt explicitly regenerates it. The input and invoice model are the same two pinned foundational files used by the prior P112 packages. This is a local deduction, not a claim from PIR or network-coding literature.

The independent checker reconstructs all441 tariffs with binary span and
annihilator sets, without producer imports, and agrees on the complete table.
See INDEPENDENT-FIXED-SOURCE-SPAN-PROOF.md for its proof audit. Since the endpoint
and tariff are symmetric under transposition, the same floor holds if all
readers instead lie in this canonical span. A cheaper factorization at this
placement would need both factor families to escape the canonical span.
These are separate AI-agent checks, not independent human or formal-kernel
review. Prepared by flyingviper with substantial OpenAI Codex assistance.
Apache-2.0.
