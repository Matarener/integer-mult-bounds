"""Search a cyclic query frame with a finite-order advancing stage.

The root-of-unity evaluations are numerical discovery only. A small
residual requires an exact coefficient replay and a complete caller bill.
"""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from scipy.optimize import least_squares
from exact_replay import canonical


def search(args):
    n = args.n
    us, vs, raw = canonical(n)
    ident = np.eye(n, dtype=complex)
    ts = np.array(raw, dtype=complex)
    c = np.column_stack([*ident[:, 1:].T, np.array(us[-1])])
    ci = np.linalg.inv(c)
    powers = [np.linalg.matrix_power(c, i) for i in range(n+1)]
    inverses = [np.linalg.matrix_power(ci, i) for i in range(n+1)]
    if max(np.max(abs(p@ts[0]@q-ts[i])) for i, (p,q) in enumerate(zip(powers,inverses))) > 1e-10:
        raise ValueError('The cyclic query control fails')
    v = np.array(vs[0])
    a = -ident[:, 1]
    basis = np.column_stack([ident[:, 0], a, *[ident[:, j]-v[j]*a for j in range(2,n)]])
    bi = np.linalg.inv(basis)
    count = 2*(n-2)
    roots = [np.exp(2j*np.pi*k/args.period) for k in range(1,args.period)]

    def calculate(x):
        parameters = x[:count]+1j*x[count:]
        av, bv = parameters[:n-2], parameters[n-2:]
        p = np.zeros((n,n), dtype=complex)
        p[0,0] = p[1,1] = 1
        p[0,1] = -bv@av
        p[2:,1], p[0,2:] = av, bv
        dp = np.zeros((count,n,n), dtype=complex)
        for j in range(n-2):
            dp[j,j+2,1] = dp[j+n-2,0,j+2] = 1
            dp[j,0,1], dp[j+n-2,0,1] = -bv[j], -av[j]
        p = basis@p@bi
        dp = basis@dp@bi
        ps = [c@p@ci for c,ci in zip(powers,inverses)]
        dps = [c@dp@ci for c,ci in zip(powers,inverses)]
        values, derivatives = [], []
        for z in roots:
            plus, minus = ident.copy(), ident.copy()
            jp = np.zeros((count,n,n),dtype=complex)
            jm = jp.copy()
            for p,dp,t in zip(ps,dps,ts):
                d = ident+(z-1)*p
                dd = (z-1)*dp
                jp = d@jp+dd@plus
                jm = d@t@jm+dd@t@minus
                plus, minus = d@plus, d@t@minus
            values.append((plus+minus).ravel())
            derivatives.append((jp+jm).reshape(count,-1).T)
        f = np.concatenate(values); j = np.vstack(derivatives)
        return np.r_[f.real,f.imag], np.block([[j.real,-j.imag],[j.imag,j.real]])

    rng = np.random.default_rng(args.seed)
    test = rng.normal(0,.05,2*count)
    _, jac = calculate(test)
    for i in range(2*count):
        delta = np.zeros(2*count);delta[i] = 1e-6
        fd = (calculate(test+delta)[0]-calculate(test-delta)[0])/2e-6
        if np.max(abs(fd-jac[:,i])) > 1e-3:
            raise ValueError('The derivative control fails')
    best, records = None, []
    started = time.monotonic()
    for trial in range(args.trials):
        x = np.zeros(2*count) if trial == 0 else rng.normal(0,.2,2*count)
        result = least_squares(lambda x: calculate(x)[0], x, jac=lambda x: calculate(x)[1],
                               max_nfev=args.steps, ftol=1e-11, xtol=1e-11, gtol=1e-11)
        row = {'trial':trial,'norm':float(np.linalg.norm(result.fun)),
               'max_residual':float(np.max(abs(result.fun))),'evaluations':result.nfev}
        records.append(row)
        if best is None or row['norm'] < best['norm']:
            best = row|{'parameters':result.x.tolist()}
            print(json.dumps(row),flush=True)
        if row['max_residual'] < 1e-9:
            break
    return {'n':n,'period':args.period,'best':best,'records':records,
            'seconds':time.monotonic()-started,'status':'NUMERICAL_DISCOVERY_ONLY',
            'analytic_derivative_control':'PASS','new_kappa':False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--n',type=int,default=8)
    parser.add_argument('--period',type=int,default=7)
    parser.add_argument('--trials',type=int,default=12)
    parser.add_argument('--steps',type=int,default=300)
    parser.add_argument('--seed',type=int,default=6201)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    result = search(args)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('best','records')}),flush=True)
