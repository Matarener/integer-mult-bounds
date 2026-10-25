# A raw marked correction count, valid for every d

Prepared by conorholds, with substantial OpenAI Codex assistance. Apache-2.0.

Use the E8/P112 code and actual-basis definitions of the marked invoice theorem. In particular the eight frame roots f_i are orthogonal, C_h(s)=(r_s,h), F=(q_1,...,q_m) is an actual basis of a space S containing C, and phi_j is its dual basis. Write

    phi_j(C_h)=(x_j,h),
    C_h = sum_j (x_j,h)q_j.

A corrected member has x_j a nonzero scalar multiple of a frame root f_i and z_i in U(q_j). Assume a marked index k has x_k=gamma v, gamma!=0, with v a nonframe root. Assume m<=11. Then

    n_c <= m-2.

The claim requires neither a condition on T=S_(<=7) nor the witness g, an invoice cap, minimum-weight basis choices, normalized projected rows, or distinct corrected LOW frame indices.

## Proof

A nonframe root v has nonzero pairing with exactly four frame roots. Let J be their four indices, so v belongs to the four-dimensional span of {f_i:i in J}. In particular x_k is not a frame direction, so k is uncorrected and n_c<=m-1.

Suppose n_c=m-1. Every j!=k is then corrected. For each frame index i let G_i be the group of those indices j with x_j proportional to f_i.

Take i outside J and apply the code expansion to h=f_i. The marked coefficient is zero, and orthogonality of the frame gives

    C_(f_i) = sum_(j in G_i) (x_j,f_i)q_j.                 (1)

The left side is nonzero. Thus G_i is nonempty. If G_i={a}, equation(1) forces q_a to be a nonzero scalar multiple of C_(f_i). But a frame codeword has label span W_i=z_i^perp, which excludes z_i because beta(z_i,z_i)=1. Thus a would be uncorrected, contradicting its membership in G_i. Consequently |G_i|>=2 for every one of the four indices outside J. These four groups contain at least eight corrected members.

The restricted duals x_j span the full eight-dimensional normal space: a normal orthogonal to all x_j would have C_h=0 by the expansion, hence h=0 by injectivity of the code map. Let r be the number of nonempty corrected groups G_i with i in J. All restricted duals lie in

    span{f_i:i outside J} + span{f_i:i in J,G_i nonempty} + span{v}.

The dimension of this sum is at most 4+r+1. Full rank8 therefore requires r>=3. These groups contribute at least three further corrected members, so n_c>=8+3=11. This contradicts n_c=m-1<=10. Hence n_c<=m-2. QED.

The two geometric inputs are the standard nonframe-root four-axis incidence and the frame codeword span/noncarrying fact. Both are explicitly stated and verified in the existing marked d=0 package (PROOF.md G2/G5 and CONSUMER.md Section2); no source normalization is used.

## Exact positive-d consequence and boundary

For the tight t2 basis m=10, this gives raw n_c<=8 for EVERY d. It supplies
the numerical N8 premise used for the source's marked t2 peeling budget
without merging projected rows. The source's separate peeling lemma,
T-level exclusions and filters are not revalidated here. In particular this
counting lemma does not certify the completeness of the 35-list or kill
any of its multisets.

For the tight t3 basis m=11, the same proof gives only raw n_c<=9. The source's 280 multisets were enumerated with slack<=8. A complete actual marked positive-d t3 treatment must additionally exclude n_c=9 or include its possible slack9 configurations. The present lemma makes no exhaustive-list claim for t3 and no positive-d invoice conclusion.

Sources: DreamingOfClouds' PR3154 at `708f0ad8928c383de8294aea3c126e9461d2066d`, CONJ-G Section 0 and CONJG2 Sections 0/3; PR2816's one-sided-decoders-all-m Section 3.1, whose normalization is not invoked. This is a written algebraic proof. The E8 incidence and frame-span inputs are authenticated and checked by the package replay; the new counting argument itself is not formalized.
