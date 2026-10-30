"""Shared linearisation weights for every lattice screen (retime, evretime, reorder, dims_relax).
kappa solves f(k)=sum_T n r^(1-k) - sum_P n r^(1-k) = 0 and f is DECREASING in k.  A table move adding m calls at rank d to T or removing them from P
changes f(k0) by +m*d^(1-k0) EXACTLY (linear in the counts), and kappa rises iff f(k0) rises; dk = dF/D to first order, D=-f'(k0).
The old tables cwT[d]=delta(T+18)-k0, cwP[d]=k0-delta(P+18) were each a finite difference with its own curvature, cwT[d] != cwP[d] by ~3e-4 relative
(2.3e-8 at d=1 on #5660).  A T-move and a P-move at the same rank cancel EXACTLY in the true kappa but the model credited the curvature difference
(RETIMEGAP: #5660 helper rank 7->6 with paid 7->6, model +3.26e-8, exact 0).  Here cwT[d]==cwP[d]==18*d^(1-k0)/D (x1e16, integer): model is the exact
first-order functional, so the model gain of any set of moves = F-gain/D with residual only second order in the TOTAL table change."""
import math
def weights(pc,calls=18,scale=1e16):
    k=pc.k;e=1-k
    D=sum(n*r**e*math.log(r) for r,n in pc.T.items())-sum(n*r**e*math.log(r) for r,n in pc.P.items())
    w={d:round(scale*calls*d**e/D) for d in range(1,10)}
    return dict(w),dict(w)
def native_objective(M,tl=120):
    """Objective of the model evaluated at its own hint (the input word's native assignment): clone, fix every variable to its hinted value, solve.  None if infeasible/unknown.
    gain_model = (ObjectiveValue_after_solve - native_objective)/1e16 -- the number the regression test compares with the exact price."""
    from ortools.sat.python import cp_model
    C=M.clone()
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=tl;s.parameters.num_workers=1;s.parameters.fix_variables_to_their_hinted_value=True
    st=s.Solve(C)
    return s.ObjectiveValue() if st in (cp_model.OPTIMAL,cp_model.FEASIBLE) else None
