# R429 overcomplete flat-reader cost floor

Scientific source pin `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
This is a local lower bound for a precisely stated linear compensation model.
It does not establish a new conditional multiplication exponent.

Let `R` be the actual 9-by-111 binary readout matrix reconstructed from the
retained R438 `D,A` word, after restricting its retained helper rows to source
columns. The factor in the R429 compensation is `K R`, with `K` full column
rank9. Hence a factorization of `K R` by readout rows is also a factorization
of `R`, after a left inverse of `K`. The saved producer reconstructs both
matrices from frozen source and checks equality to the later local receipt.

Consider any binary linear factorization `R = B C`. A row `C_i` may be
outside rowspace(R). Its support consists of source root lines, and let `d_i`
be the rational dimension of their span. Charge this row at least `d_i`.
This is the separate native COPY model in which the prepared readout is
materialized at its containing frame. The proof does not assume it is an
admitted physical circuit: all gathering, copied-field storage, dirty
restoration and target delivery would still have to be paid.

Then

`sum_i d_i >= 49`.

The exact 511-codeword replay gives minimum Hamming weight48 for rowspace(R),
rank9, and all111 nonzero source columns. Only the original nine readouts
have rational support-span rank7; the other502 directions have rank8. Thus
a basis contained in rowspace(R) has minimum cost63. The 49 floor also
covers overcomplete readouts outside that rowspace.

Delete dependent rows of C and adjust B. This only decreases the bill, so
suppose C has t independent rows. Its span U contains the dimension9 code
D=rowspace(R). Any t−8 rows of C span a subspace V with

`dim(V intersect D) >= (t−8)+9−t = 1`.

Consequently the union of their supports contains a nonzero codeword of D
and has size at least48.

An E8 root-spanned flat of rational dimension d contains at most

`M_d = (0,1,3,6,12,20,36,63,120)[d]`

unoriented root lines. For completeness, take a generic point in the
orthogonal complement of the flat. The roots perpendicular to it are
exactly the roots in that flat. Move that point to a closed Weyl chamber;
its vanishing simple roots generate a standard parabolic root subsystem.
The maximum numbers of positive roots at ranks1 through8 are attained by
A1,A2,A3,D4,D5,E6,E7,E8 respectively, giving the displayed capacities.
Puncturing can only decrease these bounds. This uses the ordinary finite
E8 root-system/parabolic classification, not a formal-kernel certificate.

For any sorted rank profile of cost at most48, apply the support-union
condition to the t−8 cheapest rows. The executable enumerates every
partition of a number at most48 into parts1 through8. The only profiles
not already excluded by the relaxed sum-of-capacities test are:

| Readouts | Rank each | Cost | Remaining contradiction |
| --- | --- | --- | --- |
|12|4|48|Every four must have disjoint supports of size12. Any two belong to some four, so all12 are pairwise disjoint and require144 source coordinates, exceeding111.|
|16|3|48|Their total support union has size at most16·6=96, below111.|
|24|2|48|Their total support union has size at most24·3=72, below111.|

This excludes cost48 and every smaller cost. The method does not claim an
attaining49-cost factorization.

The separate tensor-lift rank36 is retained as a weaker control. Express
each root in the saved integral E8 lattice basis and reduce its coordinates
u_p modulo2. The 72-by-111 matrix with columns `R[:,p] tensor u_p` has binary
rank36. If `R=B C`, its term for reader i has columns `B[:,i] tensor u_p`
on the support of `C_i` and zero elsewhere. Its binary rank is at most d_i:
the integral coordinate matrix on a rational d_i-flat has every larger
minor zero over Z, hence also modulo2. Subadditivity gives cost at least36.
This tensor rank is distinct from rational support-span dimension and from
the rank of a routed ADDRESS operator.

Reproduce in this directory with `python3 -B readout_floor.py` and
`python3 -O -B readout_floor.py`. `--write` regenerates this lane's receipt.
No predecessor producer or upstream artifact is modified. Negative controls
change an actual R bit and weaken the rank4 capacity; both alter the
proof-relevant computed data. All matrices, roots and source hashes are in
`READOUT-FLOOR.json`.

The model can be changed by sharing native calls among readouts, using
operator-valued/nonlinear readers, changing the source code or changing the
caller so it consumes compensation before full materialization. Such a
construction requires its own paid native identity and dirty restoration.

Credit: retained E8/R438/PR555,543,545,510 geometry and scalar interface,
Ali Romman's source-boundary deletion, Sagar Thakrar's transported R438
word, and the preceding local R429 compensation construction. The finite
E8 flat capacity method is also recorded in the earlier E8 joint-reader
work by Chi Zhao, Philipp and Joel Pulikkan/GamingPuzzled. This lane adds
the arbitrary overcomplete-extension support-union floor for the actual
R429 reader code. Substantial OpenAI Codex assistance; Apache-2.0.
