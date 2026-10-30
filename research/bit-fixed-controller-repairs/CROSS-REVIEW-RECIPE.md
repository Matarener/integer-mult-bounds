# Cross-review of the fixed-involution repair proof

Read-only mathematical review of `b07-recipe-review/PROOF.md`, SHA-256
`9601bf1cfdd196e30c885f2d880f6322c3e1d11c898a1689ad8087259b573988`.
This is an independent proof reading, not another execution of its checker.
Prepared with substantial OpenAI Codex assistance.

The all-B endpoint derivation is correct. Starting with
`t0=X0+NY0`, direct substitution through the positive bridge, local forward
call and negative bridge gives
`t_(j+1)=X_(j+1)+Y_(j+1)+N(Xj+tj)`.
Writing `tj=Xj+Sj+epsilon*bj` yields the stated recurrence
`b_(j+1)=bj+Sj`. The descending X bridges add neighboring `p` rows while
the Y bridges telescope through suffix sums of `q` rows. This gives the
displayed endpoint on every arbitrary bank input, including B=1.

The block formula `C=L^T L` is exact: its `(j,k)` entry counts indices
`ell>=max(j,k)`. Both C and D are invertible. For the repair coefficient
`M=A+I`, row j of `DC` for j>=1 is the row with ones exactly at `k<j`.
The Schur complement therefore has rows `e_j` for j>=1 and first row
`C[0,*]`; its first pivot is `B mod2`. This proves rank `2B` for odd B
and `2B-1` for even B. Trace M is one, since the dimension is even and
the only diagonal coefficient of A is its y0 entry.

Both attaining projector decompositions are valid. In the odd case,
the y0 column splits into two rank-one projectors whose added coordinate
projectors cancel. All other diagonal pairings are one. In the even
case, the kernel relation
`m_y0=sum_(j odd) m_xj` reconstructs the omitted y0 column. The x-column
readout `e_xj^T+[j odd]e_y0^T` still pairs to one: the y0 row of D is
supported only at x0, and j=0 is even. All retained y-column diagonal
pairings are one. A basis beginning with u and completing with `ker(v^T)`
implements each claimed scalar conjugation exactly.

The restored-spectator quantifier is justified. The required coefficient
is `M direct-sum 0`, with every spectator row and column included, so
rank and trace give the same lower bounds in any larger finite ambient
bank space. No spectator is specialized to zero. The attaining words
extend by identity and therefore restore every spectator literally.

The insertion extension is also sound for complete repair gates with
constant term I. Moving a repair to the terminal cut conjugates its
epsilon coefficient by the constant part of an invertible fixed suffix
(equivalently the corresponding fixed prefix in the opposite product
convention). The result remains a rank-one projector with trace one;
epsilon terms in the conjugating product do not contribute because
`epsilon^2=0`. Multiple repairs commute at that coefficient level.
This does not license extra unpaired scalar mixing or changes to the
original recipe, as the proof correctly states.

No mathematical defect was found in the stated theorem or construction.
The proof does not extend to changing the local alphabet, altering the
original scalar topology, or treating the formal free mixing as native
physical work. Its conversion of seven B4 calls into 777 rank-one
children remains explicitly conditional on a separately admitted
111-child implementation.
