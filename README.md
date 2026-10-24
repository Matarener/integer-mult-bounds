Clique-dual LP lower bound on the per-call tariff of a plane-port decoder (V4), run on GitHub Actions.

`v4_cg2.py`: cutting-plane LP over 2,982 cliques of pairwise non-orthogonal planes. Separation is exhaustive over all
39,087^2 ordered pairs of plane-generated spans. The final lam is re-checked in float64 over all pairs and scaled to be
feasible, so `LB_strict` in `v4_cg2_result.json` is a valid lower bound. Resumes from `v4_cg2_state.pkl`.
