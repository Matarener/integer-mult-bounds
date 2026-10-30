# Overcomplete readout floor53 and the fixed three-seed consequence

Scientific pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
This combines an exact finite census with a written all-L implication. It is
not a formal proof certificate or an unrestricted native-circuit bound.

The BIT lane's READOUT-FLOOR supplies the actual binary rank9 reader code
`D=rowspace(R)` on111 source coordinates, minimum nonzero weight48, and the
E8 root-flat capacities `M_d=(1,3,6,12,20,36,63,120)`. Its separate-reader
model writes `R=B C` and charges each row of C at least the rational dimension
of the flat containing its source-root support. Readouts outside D are allowed.
This model excludes shared native queries and COPY into a nonzero target frame.

Prune dependent rows of C, leaving t independent rows spanning V, with D
contained in V. Any `t-9+k` rows span a subspace meeting D in dimension at
least k. A k-dimensional binary subcode has `2^k-1` nonzero words. Each
has weight at least48; each coordinate in their support appears in exactly
`2^(k-1)` words. Therefore their union has at least

    b_k = ceil(48*(2^k-1)/2^(k-1))

coordinates. Use the stronger actual full-code support111 for k=9. For
k=1,...,9 the bounds are48,72,84,90,93,95,96,96,111.

For any sorted reader-rank profile, the `t-9+k` cheapest readers have union
capacity at most the sum of their M_d. `overcomplete_pressure.py` enumerates
all340260 partitions of a cost at most52 into ranks1,...,8 and checks these
nine necessary inequalities. Exactly one profile survives:13 rank4 readers.
Any six of those readers must cover at least72 coordinates. Their total
capacity is exactly72, so those six have disjoint supports of size12.
Every pair occurs in such a six. All13 supports would therefore be pairwise
disjoint and require156 coordinates, exceeding111. Hence cost is at least53.
No attaining53-cost construction is asserted.

This changes the three-seed budget decisively. Grant deletion of all nine old
compensation helpers and keep only the unchanged R429 bulk histogram

    {1:1295, 2:1342, 3:79, 4:44, 5:93, 6:11, 7:9}.

Its mass is4986=`14*111+8*429`. It is independently recovered from the pinned
FULL-target profile by removing the111 charged rank1 target lifts. The
three-seed star's common-axis credit is222. If each seed is repaired in the
reader model above, its available deficit is at most `222-3*53=63`.

For every L>=3, parent arity `m=1+7L>=22`, and primitive exponent a>=.002,
the three bulk profiles alone exert pressure

    sum_r 3*r*c_r*((m/r)^a-1)
      >= (3/500) sum_r r*c_r*ln(22/r)
      > 72.34417105 > 63.

The executable's bound is an exact fraction obtained from32 positive terms
of the atanh series for each logarithm. All omitted reader, idle, padding
and owner pressure is nonnegative. Thus there is no reliance on438 versus429
helpers, a particular packing schedule, or an unproved native admission.
The result is conditional on retaining the specified bulk and common-axis
credit. Shared queries, a changed code, a different copied-frame contract or
a different caller can escape its premises and require fresh analysis.

Run `python3 overcomplete_pressure.py` and `python3 -O overcomplete_pressure.py`.
The producer reconstructs R and K from the source word, verifies source hashes,
replays all511 nonzero reader combinations, enumerates all profiles, and
checks controls weakening the distance premise and the earlier49-cost floor.
The latter floor alone does not yield this storage-independent contradiction.

Credit: the BIT lane supplied the source-bound factor, overcomplete-reader
model, flat capacities and preceding49 floor. Root supplied the generalized
support argument, strengthened census, equality rejection and pressure transfer.
Underlying E8/R438 and R429 sources retain their authorship and notices.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
