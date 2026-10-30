"""Literal admissible completed defects for the frozen 19-bit counterexample."""
from fractions import Fraction as F
from hashlib import sha256


def need(ok,message):
    if not ok:raise ValueError(message)


def response(word,sites,target):
    row={target:F(1)};coefficients={}
    for j in reversed(range(len(word['program']))):
        e=word['program'][j];op,r=e[:2];v=row.get(r,F(0))
        if j in sites and v:coefficients[j]=v
        if op in ('INIT','CLEAR'):row.pop(r,None)
        elif op=='SCALE':
            if v:row[r]=v*F(e[-2])
        elif op in ('ADD','COPY'):
            if v:
                s=e[2];value=row.get(s,F(0))+v*F(e[-2])
                if value:row[s]=value
                else:row.pop(s,None)
            if op=='COPY':row.pop(r,None)
    return row,coefficients


def replay(word,sites,certificate,causal,extra_bits=0,return_defects=False):
    n,coefficient_scale,ops=causal.setup(word);E=coefficient_scale.bit_length()-1
    initial=certificate['initial'];target=certificate['target'];guard=certificate['guard'];Q=certificate['grid_bits']
    need(len(initial)==n and all(type(x) is int and abs(x)<=1 for x in initial),'unit input field bounds')
    need(0<=target<word['public'] and guard==19 and Q==96,'counterexample parameters')
    row,coefs=response(word,sites,target);S=1<<(Q+E);values=[x*S for x in initial];u=F(1,1<<(guard+extra_bits));error_sum=F(0);used=0;stream=sha256();first_budget=None;defects={}
    for j,(op,r,q,s) in enumerate(ops):
        if j in sites:
            budget=abs(values[r])
            if op=='ADD':budget+=abs(causal.scaled(values[s],q))
            elif op=='SCALE':budget=abs(causal.scaled(values[r],q))
            else:need(op=='MOVE','declared relative site')
            delta=((budget>>(E+guard+extra_bits))<<E)
            delta=delta if coefs.get(j,0)>0 else -delta if coefs.get(j,0)<0 else 0
            need(F(abs(delta))<=u*budget,'actual-input defect allowance')
            if budget and first_budget is None:first_budget=budget
        else:delta=0
        if op in ('INIT','CLEAR'):values[r]=0
        elif op=='COPY':values[r]=causal.scaled(values[s],q)
        elif op=='SCALE':values[r]=causal.scaled(values[r],q)
        elif op=='ADD':values[r]+=causal.scaled(values[s],q)
        values[r]+=delta
        if delta:
            used+=1;error_sum+=coefs[j]*F(delta,S);defects[j]=F(delta,S)
        stream.update(f'{j}:{values[r]}:{delta};'.encode())
    exact=sum((row.get(i,F(0))*x for i,x in enumerate(initial)),F(0));error=F(values[target],S)-exact
    need(error==error_sum,'independent adjoint error sum')
    threshold=F(1,1<<extra_bits)
    need(error>threshold,'admissible 19-bit failure')
    if extra_bits==0:need(str(error)==certificate['error'],'recorded exact counterexample')
    # One grid unit above the actual allowance must fail the same predicate.
    too_large=(u*first_budget).__floor__()+1
    need(F(too_large)>u*first_budget,'over-budget defect rejected')
    result=dict(guard=guard,extra_bits=extra_bits,target=target,nonzero_defects=used,error=error,
                allowed_output_error=threshold,scaled_error=error/threshold,trace_sha256=stream.hexdigest(),
                actual_allowances_checked=len(sites),over_budget_control=True)
    return (result,defects) if return_defects else result


def transported(word,records,gauges,initial,defects,guard):
    values=list(map(F,initial));u=F(1,1<<guard);checks=0
    for j,(event,record) in enumerate(zip(word['program'],records)):
        op,r=event[:2];kind,index=record[:2]
        delta=gauges[j]*defects.get(index,F(0)) if kind=='source' else F(0)
        if delta:
            need(op in ('MOVE','ADD'),'family witness uses only retained native and ADD sites')
            budget=abs(values[r])
            if op=='ADD':budget+=abs(F(event[-2]))*abs(values[event[2]])
            need(abs(delta)<=u*budget,'transported actual-input allowance');checks+=1
        if op in ('INIT','CLEAR'):values[r]=F(0)
        elif op=='COPY':values[r]=F(event[-2])*values[event[2]]
        elif op=='SCALE':values[r]*=F(event[-2])
        elif op=='ADD':values[r]+=F(event[-2])*values[event[2]]
        values[r]+=delta
    return values,checks
