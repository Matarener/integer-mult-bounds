# Diagnostic (not registered): #4436's direct flow with a forced lockstep depth G <= G0 = floor(log5(N/m)).
# Run from this directory: python3.12 -B depth_variants.py
import math
exec(open('overlap_flow_depth.py').read())
W = {5: 420, 6: 270, 7: 840, 8: 1395, 9: 3195, 25: 448, 41: 448, 57: 448, 121: 224}
P = {1: 37305, 2: 10695, 3: 3360, 4: 1530, 5: 300, 8: 1464, 16: 448, 32: 448, 48: 448}
m, ts = 121, 0.9973135109511491
for N in (20000, 100000, 400000, 2000000):
    G0 = 0
    while 5 ** (G0 + 1) <= N // m:
        G0 += 1
    for G in range(max(0, G0 - 3), G0 + 1):
        R = flow(N, W, P, G)
        S, X = R['S'], R['X']
        ident = sum(s * v for s, v in S.items()) - sum(e * v for e, v in X.items()) == 608 * R['col']
        st = sum(v * s ** ts for s, v in S.items()); xt = sum(v * e ** ts for e, v in X.items())
        g = sum(v * s ** ts * math.log(s) for s, v in S.items()) / st - sum(v * e ** ts * math.log(e) for e, v in X.items()) / xt
        k = sum(v * e ** 0.999 for e, v in X.items()) / sum(v * s ** 0.999 for s, v in S.items())
        low = sum(v for s, v in S.items() if m * s <= N) / sum(S.values())
        print(N, G0, G, ident, f"g={g:.4f} kappa(0.001)={k:.6f} (eta 0.994220) source mass <= N/m: {low:.3g}")
