# A joint cut counts crossings, not their ranks

The eight unchanged producer values are required as observations at their
retained one-dimensional delivery frames. They may be produced at different
times and erased afterward. All original public inputs remain independent;
owned INIT supplies zero and CLEAR deletes a row. Scalar contacts use one
common frame; public transport ascends and owned transport descends in frame
inclusion. This is the same literal row/frame model as PROOF-loss-space.md.

Let W be the span of the eight delivery lines. The source-bound certificate
gives dim W=8. Partition original input symbols into those whose entry frames
are contained in W, and the outside symbols whose entry frames are not.
Project every scalar row onto the latter coordinates.

Consider the span K of the projected rows that have ever appeared in registers
whose current frames are contained in W. Retain observations in K after their
physical registers are cleared or moved out. Initially K=0: each inside
register contains its own independent input, whose entry frame is inside W.
Common-frame scalar operations inside W only take linear combinations of
already available rows. Outside operations remain outside, and public ascent
cannot move an outside frame into W. INIT contributes zero and CLEAR cannot
increase K. An owned descent from outside W to inside W introduces one scalar
row and can increase dim K by at most one. Owned descents staying on the same
side contribute nothing new to this count.

If the demanded observations have outside-coordinate matrix R, then

    number of owned descents crossing into W >= rank(R).

The argument permits sequential outputs and arbitrary storage reuse: K is a
mathematical record of information ever available inside W, not an additional
physical register or an assumption that all outputs coexist. Any public
upward transport carrying an observed row out of W leaves that row in K; its
later return cannot invalidate the lower bound.

`verify_joint_cut(word, producer_receipt)` reconstructs R from the exact
initial-input covectors and actual delivery scale factors. There are 112
outside input roles and rank R=8. The receipt contains eight witness input
columns, the full rational 8-by-8 minor and its nonzero determinant. The source
has exactly eight crossing MOVE events, one for each owned role735--742, so it
attains this crossing-count floor.

Two controls show the scope: duplicating one observation lowers the rank to7;
using the whole ambient space as W leaves no outside inputs and gives rank0.

This does not prove a cost of8H7. Each crossing has its own rank, and the cut
only counts scalar rows that cross. Sharing cannot reduce the crossing count
below8 for these unchanged eight observations, but might still reduce their
ranks or other paid work. Removing a demanded intermediate value, changing its
payload or delivery frame, or changing the row/frame operation model is outside
the statement. No improved bound or whole-word tariff optimum is claimed.

Prepared with OpenAI Codex assistance; no proof-kernel or independent human
acceptance is claimed.
