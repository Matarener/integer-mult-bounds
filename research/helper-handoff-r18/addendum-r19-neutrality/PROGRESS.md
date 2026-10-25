# R19 checkpoint log (hand-off-enabled native block)
## M0 setup
- worktree ~/imb-r19 branch r19-handoff-block (from r18-helper-handoff ce96fe974). Work dir ~/imb-harness/r19.
- Key accounting observation: per register, paid rank mass of climbs between two anchors is fixed (dim N - dim P);
  re-flagging a register through a mid frame F only splits a jump: cost g(a,b)=f(a)+f(b)-f(a+b), the SAME
  concave function as the hand-off gain. g(1,1)=1.39C, g(1,2)=1.91C, g(1,8)=3.14C, g(4,5)=6.18C (C~0.003).
  => a hand-off nets positive iff the forced lifts' g-sum < hand-off g. Plan: priced-lift relay screen on
  #4610 word (generalises R18 relay/presub), then construct+replay any positive candidate exactly.
## M1 priced-lift screen on #4610 word (tools/lift.py, exact rows; float pricing)
- Every helper (224..631), every event, every mid frame F on its flag; holders of h_in not at F must be LIFTED
  (re-chosen climb chain P->F->N between anchors, cost g); then (h_in,()) in span(R_F + lifted) with extra lifts.
- maxmand=6 run: 0 net-positive both orientations (lift_forward/backward.txt). All points that pass holders fail span.
- DIAG anatomy (diag_*.txt, anatomy.py): residual of D = port inputs (e.g. L188,L193 / L3,L8,L95,L370..) held only by
  registers whose current frames are dim 5-8 and NOT contained in F (P<=F False): data has moved up incomparable flags.
  Unliftable for any budget in the lift family (forward 69/69, backward 174/174 (helper,dF) pairs).
## M2 designed blocks (tools/block.py, nreplay exact, F2^9 flag frames, 56 params x 2 families)
- plain conduit (h starts at its load frame): HAND - BASE = 0 exactly (x lift costs g(b-a,9-b) = gain).
- bottom-holder conduit (h starts at 0, presub y): HAND beats BASE by up to +0.002907, but LATER ENTRANCE (no hand-off)
  dominates: best hand-off word - best non-hand-off word <= -0.004192 on all 56.
- rerun full screen without holder cap (liftall_*.txt) in progress.
