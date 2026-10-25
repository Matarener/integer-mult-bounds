# Frame bill for events 9894 and 9895

The forward core and the canonical word are the pinned inputs named in
`SOURCES.json`. Frames are lists of integer axes. Frame 0 is `[]` and frame 4
is `[459]`.

A climb from frame `a` to frame `b` of recorded rank `r` is legal only when
every axis of `a` lies in the `F_2`-span of the axes of `b` and
`r = |b| - |a| > 0`. It then sets that register's current frame to `b`.
A scalar operation annotated with frame `f` is legal only when every `L`
operand's current frame is already `f`. These are the checks in `verify.py`.

Event 9894 is `['climb', 'A', 546, 0, 4, 1]`. It is the first climb in the
word, so every register is still at `start`. `start[546] = 0` and
`start[561] = 4`. Empty axes sit in the span of `[459]`, and `1 = 1 - 0`,
so the climb is legal and leaves `L546` in frame 4. `L561` is not the
climbed register.

Event 9895 is `['scalar', ['add', ['L', 546], ['L', 561], -1, 1], 4]`.
Both current frames equal 4, so the annotation is legal. The event does not
write a new frame. No earlier scalar writes `L561`. The only earlier event
that names 561 is the entrance wrapper
`['residual_adapter', 'pre', 561, 4]`, which the same contract requires to
repeat the entrance frame.

The retained coefficient count for a positive numerator and a power-of-two
denominator is: one clear, one step per bit after the leading bit, one step
per `1` bit, one step per halving, then `+2` for the signed accumulation and
the work clear. For absolute value 1 and denominator 1 that count is 4.
The invoice's real-step total is twice that count, so 8. The same count
applies to `+1`.

The pair's rank histogram therefore gains one rank-1 child and no scalar
rank child. Adding `L561` back, with coefficient `+1` and the same frame, is
legal in that state and costs another 4 scalar steps. It restores the
post-climb value of `L546` and leaves both frames at 4.

The recipe table contains `(old, new) = (0, 4)` at rank 1 and does not
contain `(4, 0)`. The published `final` vector puts both registers at frame
1. The forward replay that applies every climb reaches that vector, so the
word never uses a rank-decreasing climb to undo event 9894.

No six-tape origin is read here. A zero frame delta is not a zero physical
layout bill.
