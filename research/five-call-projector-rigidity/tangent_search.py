"""Search the exact first-derivative chart for a full query endpoint.

This is numerical discovery with an analytic Jacobian. No small residual
is an exact certificate or a complete caller.
"""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from scipy.optimize import least_squares
import sympy as s


def search(args):
    data=json.loads(args.chart.read_text())
    n=data['n']; variables=s.symbols(data['free']); d=len(variables)
    ps=[s.Matrix([[s.sympify(v) for v in row] for row in p]) for p in data['projectors']]
    zero={v:0 for v in variables}
    origins=np.array([p.subs(zero).tolist() for p in ps],dtype=complex)
    directions=np.array([[p.diff(v).tolist() for v in variables] for p in ps],dtype=complex)
    qs=s.Matrix([s.sympify(v) for v in data['quadratics']])
    qfun=s.lambdify([variables],qs,'numpy');jfun=s.lambdify([variables],qs.jacobian(variables),'numpy')
    ts=np.array(data['queries'],dtype=complex)
    ident=np.eye(n,dtype=complex)
    period = data.get('period', n)
    roots=[np.exp(2j*np.pi*k/period) for k in range(1,period)]

    def calculate(x):
        z=x[:d]+1j*x[d:]
        projectors=origins+np.einsum('k,skij->sij',z,directions)
        values=[np.asarray(qfun(z)).ravel()]
        derivatives=[np.asarray(jfun(z))]
        for value in roots:
            plus=ident.copy();minus=ts[0].copy()
            jp=np.zeros((d,n,n),dtype=complex);jm=jp.copy()
            for i,p in enumerate(projectors):
                stage=ident+(value-1)*p
                dp=(value-1)*directions[i]
                jp=stage @ jp + dp @ plus
                jm=stage @ ts[i+1] @ jm + dp @ ts[i+1] @ minus
                plus=stage @ plus;minus=stage @ ts[i+1] @ minus
            error=ts[-1] @ minus+plus
            deriv=ts[-1] @ jm+jp
            values.append(error.ravel())
            derivatives.append(deriv.reshape(d,-1).T)
        f=np.concatenate(values);j=np.vstack(derivatives)
        return np.r_[f.real,f.imag],np.block([[j.real,-j.imag],[j.imag,j.real]])

    cached_x,cached_value=None,None
    def cached(x):
        nonlocal cached_x,cached_value
        if cached_x is None or not np.array_equal(x,cached_x):
            cached_x=x.copy();cached_value=calculate(x)
        return cached_value
    # A separate finite difference checks the analytic derivative before search.
    rng=np.random.default_rng(args.seed);test=rng.normal(0,.2,2*d)
    _,jac=calculate(test)
    for i in range(2*d):
        delta=np.zeros(2*d);delta[i]=1e-6
        numerical=(calculate(test+delta)[0]-calculate(test-delta)[0])/2e-6
        if np.max(abs(numerical-jac[:,i]))>2e-5:
            raise ValueError('The analytic Jacobian control fails')
    records=[];best=None;start=time.monotonic()
    for trial in range(args.trials):
        x=np.zeros(2*d) if trial==0 else rng.normal(0,args.scale,2*d)
        answer=least_squares(lambda x:cached(x)[0],x,jac=lambda x:cached(x)[1],
                             max_nfev=args.steps,ftol=1e-12,xtol=1e-12,gtol=1e-12)
        row={'trial':trial,'norm':float(np.linalg.norm(answer.fun)),
             'max_residual':float(np.max(abs(answer.fun))), 'evaluations':answer.nfev}
        records.append(row)
        if best is None or row['norm']<best['norm']:
            best=row|{'parameters':answer.x.tolist()};print(json.dumps(row),flush=True)
        if row['max_residual']<1e-9:break
    result={'status':'NUMERICAL_DISCOVERY_ONLY','n':n,'period':period,'trials':len(records),'steps':args.steps,
            'seed':args.seed,'scale':args.scale,'free_complex_parameters':d,
            'best':best,'records':records,'seconds':time.monotonic()-start,
            'analytic_jacobian_control':'PASS','new_kappa':False}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'seconds':result['seconds']}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--chart',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--trials',type=int,default=24);p.add_argument('--steps',type=int,default=500)
    p.add_argument('--scale',type=float,default=.4);p.add_argument('--seed',type=int,default=6166)
    search(p.parse_args())
