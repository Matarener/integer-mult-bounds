"""Seek a pure monomial stage endpoint by changing both boundary planes.

The interior query construction stays fixed. The test z W'=H W with
H=W'(1) is necessary and sufficient for a polynomial one-parameter
representation. Numerical residuals are not endpoint certificates.
"""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from scipy.optimize import least_squares


def search(args):
    data=json.loads(args.projectors.read_text());n=data['n'];d=n-2
    fixed=[np.array([[float(x) for x in row] for row in p]) for p in data['projectors']]
    ident=np.eye(n,dtype=complex)
    left=np.column_stack([ident[:,0],-ident[:,1],*[ident[:,j]-ident[:,1] for j in range(2,n)]])
    right=np.column_stack([np.array([(-1)**(j+1) for j in range(n)]),ident[:,0],
                           *[ident[:,j]-ident[:,0] for j in range(1,n-1)]])
    bases=[left,right];inverses=[np.linalg.inv(x) for x in bases]
    count=4*d

    def projector(parameters,basis,inv):
        a,b=parameters[:d],parameters[d:]
        p=np.zeros((n,n),dtype=complex);p[0,0]=p[1,1]=1;p[0,1]=-b@a
        p[2:,1],p[0,2:]=a,b
        dp=np.zeros((2*d,n,n),dtype=complex)
        for i in range(d):
            dp[i,i+2,1]=dp[i+d,0,i+2]=1
            dp[i,0,1],dp[i+d,0,1]=-b[i],-a[i]
        return basis@p@inv,basis@dp@inv

    def calculate(x):
        parameters=x[:count]+1j*x[count:]
        ends=[projector(parameters[i*2*d:(i+1)*2*d],bases[i],inverses[i]) for i in range(2)]
        p0,pn=ends[0][0],ends[1][0]
        dp0=np.zeros((count,n,n),dtype=complex);dp0[:2*d]=ends[0][1]
        dpn=np.zeros((count,n,n),dtype=complex);dpn[2*d:]=ends[1][1]
        ps=[p0]+fixed+[pn]
        dps=[dp0]+[np.zeros((count,n,n),dtype=complex) for _ in fixed]+[dpn]
        word=[ident];derivatives=[np.zeros((count,n,n),dtype=complex)]
        for p,dp in zip(ps,dps):
            old,od=word,derivatives
            word=[(ident-p)@old[0]]
            derivatives=[(ident-p)@od[0]-dp@old[0]]
            for i in range(1,len(old)):
                word.append((ident-p)@old[i]+p@old[i-1])
                derivatives.append((ident-p)@od[i]+p@od[i-1]+dp@(old[i-1]-old[i]))
            word.append(p@old[-1]);derivatives.append(p@od[-1]+dp@old[-1])
        h=sum(i*a for i,a in enumerate(word));dh=sum(i*a for i,a in enumerate(derivatives))
        values=[];jac=[]
        for i,(a,da) in enumerate(zip(word,derivatives)):
            values.append((h@a-i*a).ravel())
            jac.append((h@da+dh@a-i*da).reshape(count,-1).T)
        f=np.concatenate(values);j=np.vstack(jac)
        return np.r_[f.real,f.imag],np.block([[j.real,-j.imag],[j.imag,j.real]]),word

    rng=np.random.default_rng(args.seed)
    test=rng.normal(0,.05,2*count);_,j,_=calculate(test)
    for i in range(2*count):
        dx=np.zeros(2*count);dx[i]=1e-6
        fd=(calculate(test+dx)[0]-calculate(test-dx)[0])/2e-6
        if np.max(abs(fd-j[:,i]))>1e-3:
            raise ValueError('The boundary derivative control fails')
    rows=[];best=None;started=time.monotonic()
    for trial in range(args.trials):
        x=np.zeros(2*count) if trial==0 else rng.normal(0,.2,2*count)
        result=least_squares(lambda x:calculate(x)[0],x,jac=lambda x:calculate(x)[1],
                             max_nfev=args.steps,ftol=1e-11,xtol=1e-11,gtol=1e-11)
        row={'trial':trial,'norm':float(np.linalg.norm(result.fun)),
             'max_residual':float(np.max(abs(result.fun))),'evaluations':result.nfev}
        rows.append(row)
        if best is None or row['norm']<best['norm']:
            best=row|{'parameters':result.x.tolist()};print(json.dumps(row),flush=True)
        if row['max_residual']<1e-9:
            break
    return {'n':n,'best':best,'records':rows,'seconds':time.monotonic()-started,
            'status':'NUMERICAL_DISCOVERY_ONLY','analytic_derivative_control':'PASS','new_kappa':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--projectors',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--trials',type=int,default=24)
    parser.add_argument('--steps',type=int,default=500)
    parser.add_argument('--seed',type=int,default=6210)
    args=parser.parse_args();result=search(args)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('best','records')}),flush=True)
