"""Observer-only actual Axis/Exponentials execution; no oracle values supplied."""
from collections import Counter
from fractions import Fraction as Q
import oracle


def arguments(s,t,u,w):
    rho=Q(t,s);theta=rho-1;beta=[rho*j-(rho*j+Q(1,2)).__floor__() for j in range(s)]
    phase=[(rho*j+Q(1,2)).__floor__()-j for j in range(s)]
    F=max((u/(4*theta)).__ceil__(),(u*(rho*w+Q(1,2))**2).__ceil__())
    out=[]
    for j,b in enumerate(beta):
        if s-j<j:continue
        out.extend([('weight_pair',u*(Q(1,4)-b*b)/theta,False,0),('weight_pair',u*b*b,True,2*u)])
    for d in range(1,w+1):out.append(('kernel_entry',u*rho*d*d,False,0))
    for i in range(s):
        for j in range(s):
            if i==j:continue
            delta=j-i;direct=abs(delta)<=w
            if not direct:
                if s-abs(delta)>w:continue
                delta=delta-s if delta>0 else delta+s
            if direct and phase[i]==phase[j]:continue
            f=u*((rho*delta+beta[i])**2-beta[j]**2)
            oracle.need(0<=f<=F,'rational Axis argument domain')
            out.append(('matrix_entry',f,False,0))
    return F,out


def run(helper):
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_axis import Axis
    from gaussian_exponentials import Exponentials
    from gaussian_rationals import Rational
    from ring_words import Signed
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope,erase_marker,sealed_constructors
    raw=[];tag=['isolated'];saved=Exponentials.grid_interval
    def snap(v):return helper.tape_bytes(v.tape)
    def wrapped(self,f,growth=False,binary_scale=None):
        argument=(f.numerator.negative,snap(f.numerator.magnitude),snap(f.denominator))
        scale=None if binary_scale is None else snap(binary_scale)
        steps,early=self.taylor_steps,self.early_stops
        result=saved(self,f,growth,binary_scale)
        raw.append({'tag':tag[0],'argument':argument,'growth':growth,'scale':scale,
                    'lower':snap(result[0]),'upper':snap(result[1]),
                    'P':snap(self.precision),'F':snap(self.argument_bound),
                    'R':snap(self.R),'k':snap(self.k),'N':snap(self.terms),'J':snap(self.J),
                    'steps':self.taylor_steps-steps,'early':self.early_stops-early})
        return result
    saved_methods={name:getattr(Axis,name) for name in ('weight_pair','kernel_entry','matrix_entry')}
    def label(name,method):
        def call(self,*args):
            old=tag[0];tag[0]=name
            try:return method(self,*args)
            finally:tag[0]=old
        return call
    Exponentials.grid_interval=wrapped
    for name,method in saved_methods.items():setattr(Axis,name,label(name,method))
    pool=ScratchPool(512);scope=OuterScope(pool);axis=None;failures=[]
    try:
        with owned(*(Count.literal(v)for v in (13,14,1,1,24))) as params:
            with sealed_constructors(),scope.installed():
                try:
                    with no_decode():axis=Axis(*params,pool)
                    for P,F in ((24,4),(1,1)):
                        with owned(Count.literal(P),Count.literal(F)) as (precision,bound):
                            exp=None
                            try:
                                with no_decode():exp=Exponentials(precision,bound)
                                for numerator,denominator,growth,sigma in ((0,1,False,0),(1,3,False,0),(F,1,True,0),(F,1,False,0),(1,3,True,513)):
                                    with owned(Rational(Signed(Count.literal(numerator)),Count.literal(denominator)),Count.literal(sigma)) as (f,scale):
                                        with no_decode():lo,hi=exp.grid_interval(f,growth,scale)
                                        lo.close();hi.close()
                                for fval in (-1,F+1):
                                    with owned(Rational.literal(fval)) as (f,):
                                        try:
                                            with no_decode():exp.positive_interval(f)
                                        except ValueError:failures.append((P,F,fval))
                                        else:raise ValueError('invalid source argument accepted')
                            finally:
                                if exp is not None:exp.close()
                finally:
                    if axis is not None:axis.close()
                    pool.empty()
    finally:
        Exponentials.grid_interval=saved
        for name,method in saved_methods.items():setattr(Axis,name,method)
    for tape in pool.tapes:erase_marker(tape)
    oracle.need(not pool.live and all(t.head==1 and all(x==4 for x in t.cells)for t in pool.tapes),'all source scratch restored')
    rows=[]
    for record in raw:
        sign,n,d=record['argument'];f=Q((-1 if sign else 1)*helper.count(n),helper.count(d))
        row={key:helper.count(record[key])for key in ('lower','upper','P','F','R','k','N','J')}
        row.update(tag=record['tag'],argument=[f.numerator,f.denominator],growth=record['growth'],sigma=0 if record['scale'] is None else helper.count(record['scale']),steps=record['steps'],early=record['early'])
        oracle.need(0<=f<=row['F'],'actual argument admitted')
        lo,hi=oracle.interval(f,row['P'],row['growth'],row['sigma'])
        oracle.need(Q(row['lower'],1<<row['P'])<=lo<=hi<=Q(row['upper'],1<<row['P']),'entire independent oracle enclosed')
        oracle.need(0<=row['upper']-row['lower']<=2,'proved two-target-ulp width')
        X=4*row['F'];k=(8*(X+1)-1).bit_length();H=row['P']+X+k+16;c=(H-1).bit_length();R=row['P']+4*X+4*k+2*c+64
        oracle.need((row['R'],row['k'],row['N'],row['J'])==(R,k,(R+2)//3+8,(R+3)//4+8),'actual precision and ceiling policy')
        row['oracle']=[[x.numerator,x.denominator]for x in (lo,hi)];rows.append(row)
    F,expected=arguments(13,14,1,1)
    actual=[(r['tag'],Q(*r['argument']),r['growth'],r['sigma'])for r in rows if r['tag']!='isolated']
    oracle.need(Counter(actual)==Counter(expected),'actual Axis argument multiset including reflected reuse and wrap')
    oracle.need(len(failures)==4,'source domain rejection count')
    growth=next(r for r in rows if r['tag']=='isolated' and r['P']==24 and r['growth'] and r['argument']==[4,1])
    decay=oracle.interval(Q(4),24,False)
    oracle.need(decay[1]<Q(growth['lower'],1<<24),'wrong growth sign rejected')
    scaled=next(r for r in rows if r['P']==24 and r['sigma']==513)
    unscaled=oracle.interval(Q(*scaled['argument']),24,True)
    oracle.need(unscaled[0]>Q(scaled['upper'],1<<24),'omitted binary normalization rejected')
    oracle.need(any(Q(*r['oracle'][0])>Q(r['lower'],1<<r['P']) for r in rows),'collapsed upper endpoint rejected')
    oracle.need(any(r['tag']=='matrix_entry' for r in rows),'cross-cell backend actually exercised')
    return {'axis':{'s':13,'t':14,'u':1,'w':1,'P':24,'F':F,'calls':len(actual)},'rows':rows,'domain_rejections':failures,'controls':['growth-sign','binary-normalization','collapsed-upper-endpoint','actual-cross-cell-calls'],'cleanup':'owned scratch blank, markers erased, heads restored'}
