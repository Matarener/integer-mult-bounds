"""Exact symbolic replay for one two-parameter family of P112 complements.

No coefficient sampling. Uses only stdlib and the authenticated verify.py arithmetic helpers.
The exceptional product ts=-2 is covered by its complete flag form, not by
specialization of a formula that divided by 2+ts.
"""
from collections import defaultdict
from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent
# Authenticate exact source bytes before compiling, so stale .pyc files cannot
# substitute for the declared local helper. verify.py imports only stdlib.
HELPER_SHA256='63c47724a3a70916c8bcf6a01d97c3296f1e8e92a8a406bb618e911272b5a2bf'
_helper_path=HERE/'verify.py'
_helper_raw=_helper_path.read_bytes()
if sha256(_helper_raw).hexdigest()!=HELPER_SHA256:
    raise ValueError('authenticated local verify.py helper source')
_helpers={'__name__':'family_exact_helpers','__file__':str(_helper_path)}
exec(compile(_helper_raw,str(_helper_path),'exec'),_helpers)
for _name in ('F','Poly','PINS','read','mm','tr','rank','independent','inverse',
              'nullspace','eye','sub','det','dump','need','tariff'):
    globals()[_name]=_helpers[_name]

def power(p,n):
    result=Poly(1)
    for _ in range(n): result=result*p
    return result

CP=1+Poly.variable('s')*Poly.variable('t')
DP=CP+1

def divide_linear(p,constant):
    """Exact division by constant+st, using the unique Q[other][st] grouping."""
    groups=defaultdict(dict)
    for mon,coef in p.terms.items():
        s,t=mon.count('s'),mon.count('t'); k=min(s,t)
        rest=list(mon)
        for _ in range(k):rest.remove('s');rest.remove('t')
        groups[tuple(rest)][k]=coef
    answer={}
    for rest,coeffs in groups.items():
        q={}; top=max(coeffs)
        for k in range(top,0,-1):
            a=coeffs.get(k,F(0));q[k-1]=a
            coeffs[k-1]=coeffs.get(k-1,F(0))-constant*a
        if coeffs.get(0,F(0)):return None
        for k,a in q.items():
            if a:answer[tuple(sorted(rest+('s','t')*k))]=a
    return Poly.terms_result(answer)

class Rat:
    """Localized polynomials Q[s,t,...,1/(1+st),1/(2+st)]."""
    def __init__(self,n=0,c=0,d=0):
        if isinstance(n,Rat):self.n,self.c,self.d=n.n,n.c,n.d;return
        self.n,self.c,self.d=Poly(n),c,d
        if not self.n.terms:self.c=self.d=0;return
        for attr,constant in [('c',1),('d',2)]:
            while getattr(self,attr):
                q=divide_linear(self.n,constant)
                if q is None:break
                self.n=q;setattr(self,attr,getattr(self,attr)-1)
    def __add__(self,o):
        o=Rat(o);c,d=max(self.c,o.c),max(self.d,o.d)
        return Rat(self.n*power(CP,c-self.c)*power(DP,d-self.d)+o.n*power(CP,c-o.c)*power(DP,d-o.d),c,d)
    __radd__=__add__
    def __neg__(self):return Rat(-self.n,self.c,self.d)
    def __sub__(self,o):return self+-Rat(o)
    def __rsub__(self,o):return Rat(o)+-self
    def __mul__(self,o):
        o=Rat(o);return Rat(self.n*o.n,self.c+o.c,self.d+o.d)
    __rmul__=__mul__
    def __eq__(self,o):
        o=Rat(o)
        return (self-o).n==0
    def __str__(self):return '('+str(self.n)+')/c^'+str(self.c)+'/d^'+str(self.d)

def add(A,B):return [[x+y for x,y in zip(a,b)] for a,b in zip(A,B)]
def scale(A,a):return [[x*a for x in row]for row in A]
def trace(A):return sum(A[i][i]for i in range(len(A)))
def col(v):return [[x]for x in v]
def part(A,rr,cc):return [[A[i][j]for j in cc]for i in rr]
def ratmatrix(A):return [[Rat(x)for x in row]for row in A]
def outer(u,v):return [[x*y for y in v]for x in u]

def frozen_geometry():
    old,candidate,data=[read(n)for n in PINS]
    A=[[F(x)for x in row]for row in old['asymmetric_template_matrix']]
    I=independent(A);J=independent(tr([A[i]for i in I]))
    U=part(A,range(12),J)
    V=mm(inverse(part(A,I,J)),[A[i]for i in I])
    need(mm(U,V)==A and rank(A)==8,'literal rank-eight anchor')
    labels={r['port']:r['q']for r in data['recipes']}
    groups=[1,2,27,28,3,4]
    G=[[labels[p]for p in candidate['groups'][g]]for g in groups]
    caps={}
    for sm,tm in [(22,22),(28,28),(34,34),(5,28)]:
        caps[str(sm)+','+str(tm)]=tariff(sum((G[i]for i in range(6)if sm>>i&1),[]),sum((G[i]for i in range(6)if tm>>i&1),[]))
    need(caps=={'22,22':6,'28,28':7,'34,34':4,'5,28':5},'four exact physical tariffs')
    flags=[]
    for side in range(2):
        anchor,frame=(tr(A),tr(V))if side else(A,U)
        sideflags=[]
        for added in (4,5):
            equations=[]
            for sm in range(1,16):
                si=[3*g+a for g in range(4)if sm>>g&1 for a in range(3)]
                source=sum((G[g]for g in range(4)if sm>>g&1),[])
                for tm in range(16):
                    ti=[3*g+a for g in range(4)if tm>>g&1 for a in range(3)]
                    reader=sum((G[g]for g in range(4)if tm>>g&1),[])+G[added]
                    rect=part(anchor,si,ti)
                    if rank(rect)!=tariff(source,reader):continue
                    for kernel in nullspace(tr(rect)if ti else[],len(si)):
                        row=[F(0)]*12
                        for i,v in zip(si,kernel):row[i]=v
                        if rank(equations+[row])>len(equations):equations.append(row)
            transformed=mm(equations,frame)
            need(rank(transformed)==1,'one saturated flag per new group and side')
            sideflags.append(next(v for v in transformed if any(v)))
        flags.append(sideflags)
    f=[F(0),0,0,0,0,0,-1,0];k=[F(-1),0,0,-1,0,0,1,0]
    need(flags[0]==[f,U[2]] and flags[1]==[k,[V[i][2]for i in range(8)]],'literal frozen flags')
    return A,U,V,G,caps,f,k

def automorphisms(A,U,V):
    columns=[]
    for g in range(4):
        for i in range(3):
            for j in range(3):
                Z=[[F(0)]*12 for _ in range(12)];Z[3*g+i][3*g+j]=1
                C=sub(mm(Z,A),mm(A,Z));columns.append(sum(C,[]))
    actual=nullspace(tr(columns),36);expected=[]
    for pattern in [[(0,0),(0,1),(1,0),(2,0),(3,0),(3,1)],[(0,2)],[(3,2)]]:
        row=[F(0)]*36
        for g,i in pattern:row[9*g+3*i+i]=1
        expected.append(row)
    for i in range(1,3):
        for j in range(1,3):
            row=[F(0)]*36
            for g in(1,2):row[9*g+3*i+j]=1
            expected.append(row)
    need(len(actual)==7 and rank(actual+expected)==rank(expected)==7,'complete label-preserving centralizer')
    return {'dimension':7,'blocks':'GA=diag(l,l,a); GB=GC=diag(l,M2); GD=diag(l,l,d); l,a,d nonzero and M2 invertible'}

def generic(A,U,V,f,k):
    c,d=Rat(CP),Rat(DP);ic,id=Rat(1,1,0),Rat(1,0,1)
    s,t=Rat(Poly.variable('s')),Rat(Poly.variable('t'))
    u=[Rat(1),s,Rat(0)];v=[Rat(1),t,Rat(0)];e0=[Rat(1),Rat(0),Rat(0)]
    h=[Rat(U[6][i])+t*U[7][i]for i in range(8)]
    q=[Rat(V[i][6])+s*V[i][7]for i in range(8)]
    Pi=add(add(scale(outer(q,h),ic),outer([V[i][1]for i in range(8)],U[1])),outer([V[i][11]for i in range(8)],U[11]))
    P0=sub(eye(8),Pi)
    need(mm(Pi,Pi)==Pi and trace(Pi)==3,'family complement projection')
    a3=mm([f],P0)[0];b3=[r[0]for r in mm(P0,col(k))]
    a4=U[2];b4=[V[i][2]for i in range(8)]
    need(mm([a3],col(b3))==[[-d*ic]],'generic flag pairing gamma=-d/c')
    need(mm([a3],col(b4))==[[0]] and mm([a4],col(b3))==[[0]],'cross flags vanish')
    Z=add(sub(P0,outer(b4,a4)),scale(outer(b3,a3),c*id))
    need(mm(Z,Z)==Z and trace(Z)==3,'three-dimensional common anchor projection')
    E=scale(outer(u,v),ic);S=sub(eye(3),scale(outer(u,v),id));Sinv=add(eye(3),outer(u,v))
    need(mm(S,Sinv)==eye(3),'generic B compression inverse')
    VB=part(V,range(8),range(3,6));UB=U[3:6]
    X=mm(mm(Z,VB),Sinv);Y=mm(UB,Z)
    need(mm(Y,X)==eye(3) and mm(X,Y)==Z,'complete common anchor frames')
    L=mm(U,X);R=mm(Y,V)
    need(L[3:6]==eye(3) and part(R,range(3),range(3,6))==S,'B frame compression')
    need(L[6:9]==sub(eye(3),outer(e0,v)),'C source dependence')
    need(part(R,range(3),range(6,9))==mm(S,sub(eye(3),outer(u,e0))),'C reader dependence')
    W=mm(part(R,range(3),range(6,12)),L[6:12])
    w=[e0[i]-u[i]*id for i in range(3)]
    need(W==add(eye(3),outer(w,e0)),'literal cap28 common operator')
    need(mm(U[3:12],col(b4))==[[0]]*9 and mm([a4],part(V,range(8),range(3,12)))==[[0]*9],'fixed-one flag invisible in B,C,D')
    ZA=mm(part(V,range(8),range(0,3)),U[0:3]);ZC=mm(part(V,range(8),range(6,9)),U[6:9])
    tau=trace(mm(mm(mm(Pi,ZA),Pi),ZC))
    need(tau==ic,'continuous label-preserving invariant tau=1/c')
    x=[Rat(Poly.variable('x'+str(i)))for i in range(3)]
    y=[Rat(Poly.variable('y'+str(i)))for i in range(3)]
    RR=outer(x,y);T=sub(RR,E);AA=mm(T,Sinv)
    S4=[row+[r[0]]for row,r in zip(sub(eye(3),T),mm(T,col(u)))]+[mm([v],T)[0]+[-mm(mm([v],T),col(u))[0][0]]]
    htr=trace(RR);ee=trace(mm(E,RR))
    g22=det(S4);gI=det(sub(eye(3),AA))
    need(g22==c*(1-htr),'rank-one cap22 determinant')
    need(gI==(c+2)*(1-htr)+ee,'rank-one complementary determinant')
    qlast=2-trace(AA);trace_defect=mm([e0],mm(AA,col(w)))[0][0]-qlast
    need(trace_defect==RR[0][0]-d*d*ic+c*gI-d*d*ic*g22,'generic trace certificate with exact remainder')
    # Exhaustive factor branches of (v*x)(y*u)=0. Verify identities without
    # dividing by any x/y coordinate or by t or s.
    xx=[-t*x[1],x[1],x[2]];R1=outer(xx,y);A1=mm(sub(R1,E),Sinv);h1=mm([y],col(xx))[0][0]
    need(mm(A1,col(xx))==col([h1*z for z in xx]),'ER=0 branch eigenvector')
    need(mm([v],mm(A1,col(w)))==[[-1]],'ER=0 branch nonzero vector')
    yy=[-s*y[1],y[1],y[2]];R2=outer(x,yy);A2=mm(sub(R2,E),Sinv);h2=mm([yy],col(x))[0][0]
    need(mm([yy],A2)==[[h2*z for z in yy]],'RE=0 branch left eigenvector')
    need(mm([e0],mm(A2,col(u)))==[[-d]],'RE=0 branch nonzero row')
    need(W!=eye(3),'mutation: removing cap28 correction is detected')
    return {'parameter_domain':'c=1+ts !=0; d=2+ts !=0','flag_pairing':'-d/c',
        'invariant':'tr(Pi Z_A Pi Z_C)=1/c','common_projection':'F=I-Pi-b4 a4+(c/d)b3 a3',
        'source_frame':'F V_B (I+u v^t)','reader_frame':'U_B F',
        'cap28_operator':'diag(I3+(e0-u/d)e0^t,0)',
        'determinants':['det(S4)=c(1-tr R)','det(I3-A)=(c+2)(1-tr R)+tr(E R)'],
        'trace_identity':'tr((W4-I)Q)=R00-d^2/c+c det(I3-A)-(d^2/c)det(S4)',
        'conclusion':'R00=d^2/c!=0, but either ER=0 forces x0=0 or RE=0 forces y0=0.'}

def exceptional(A,U,V,f,k):
    H=[[U[6][j]+U[7][j]for j in range(8)]+[F(0)],U[1]+[F(0)],U[11]+[F(0)]]
    K=[[V[i][6]-2*V[i][7]for i in range(8)]+[F(0)],[V[i][1]for i in range(8)]+[F(0)],[V[i][11]for i in range(8)]+[F(0)]]
    need(mm(H,tr(K))==[[-1,0,0],[0,1,0],[0,0,1]],'exceptional complement pairing')
    X=tr(nullspace(H,9));Y=inverse([row+[K[j][i]for j in range(3)]for i,row in enumerate(X)])[:6]
    a=mm([f+[F(0)],U[2]+[F(0)]],X)
    b=mm(Y,tr([k+[F(0)],[V[i][2]for i in range(8)]+[F(0)]]))
    b3=[r[0]for r in b];b4=[r[1]for r in b];basis=[b3]
    for z in nullspace(a,6):
        if rank(basis+[z])>len(basis):basis.append(z)
    last=[F(0)]*6;p=next(i for i,x in enumerate(a[0])if x);last[p]=1/a[0][p]
    last=[x-sum(y*z for y,z in zip(a[1],last))*w for x,w in zip(last,b4)]
    D=tr([b4]+basis+[last]);L=mm(mm([r+[F(0)]for r in U],X),D);R=mm(mm(inverse(D),Y),V+[[F(0)]*12])
    need(mm(a,D)==[[0,0,0,0,0,1],[1,0,0,0,0,0]],'complete exceptional flag coordinates')
    need(mm(inverse(D),b)==[[0,1],[1,0],[0,0],[0,0],[0,0],[0,0]],'exceptional forced projector images/kernel')
    need(mm(Y,X)==eye(6),'exceptional combined new-pair identity')
    Z=mm(part(R,range(6),range(6,12)),L[6:12])
    Z5=[[F(i==j and i!=3)for j in range(5)]for i in range(5)];Z5[4][0]=1;Z5[4][1]=-1
    need(Z==[[F(0)]*6]+[[F(0)]+row for row in Z5],'literal exceptional cap28 operator')
    need(all(L[i][4]==0 for i in range(12)),'external coordinate has no anchor source image')
    alpha=[Poly.variable('a'+str(i))for i in range(2)]
    xs=[[Poly.variable('x'+str(j)+str(i))for i in range(2)]for j in range(3)]
    ys=[[Poly.variable('y'+str(j)+str(i))for i in range(2)]for j in range(3)]
    beta=[Poly.variable('b'+str(i))for i in range(2)]
    XX=[alpha]+xs+[[Poly(0)]*2]
    YY=tr([[Poly(0)]*2]+ys+[beta])
    Q5=mm(XX,YY);Q=[[Poly(i==j==0)for j in range(6)]for i in range(6)]
    for i in range(5):
        for j in range(5):Q[i+1][j+1]=Q5[i][j]
    B=mm(mm(L[3:6],Q),part(R,range(6),range(3,6)))
    E=outer([-1,2,0],[1,1,0]);residual=add(E,B)
    XB=[xs[0],alpha,xs[1]];YP=tr([[ys[0][i]-beta[i]for i in range(2)],beta,ys[1]])
    FF=mm(XB,YP);correction=outer([0,1,0],[1,-1,0])
    left=[[1,F(1,2),0],[0,F(1,2),0],[0,0,1]]
    right=mm([[-1,2,0],[0,-2,0],[0,0,1]],[[-1,1,0],[1,0,0],[0,0,1]])
    need(det(left)!=0 and det(right)!=0 and mm(mm(left,residual),right)==add(FF,correction),'exceptional cap34 rank-preserving transformation')
    delta=sub(outer(beta,[alpha[i]-xs[0][i]for i in range(2)]),outer(ys[2],xs[2]))
    need(sub(mm(mm(YY,Z5),XX),mm(YY,XX))==delta,'exceptional cap28 factor relation')
    need(mm(YP,XB)==add(mm(YY,XX),delta),'rank-two projector F after cap28')
    # The rank-drop lemma in the proof forces F e1=e1. Therefore X beta
    # is b3+mu*external. The following literal minor is independent of mu.
    rr=[0,1,2,6,7,8];cc=[6,7,8,9]
    minor=[[A[i][j]for j in cc]+[L[i][0],L[i][1]]for i in rr]
    need(det(minor)==-1,'exceptional six-dimensional minor at tariff five')
    mutation=[row[:]for row in minor];mutation[2][4]=0
    need(det(mutation)==0,'mutation: lost forced b4 column is detected')
    return {'canonical_parameters':{'t':1,'s':-2},'all_parameters_covered':'(t,s)->(alpha*t,s/alpha), alpha=1/t, valid because ts=-2',
        'coordinate_change':dump(D),'source_frames':dump(L),'reader_frames':dump(R),'cap28_operator':dump(Z5),
        'flag_form':'P=diag(1,P5), rank(P5)=2, P5 e0=0, e4^t P5=0',
        'cap34_left':dump(left),'cap34_right':dump(right),
        'rank_drop':'rank(F)=2, F^2=F, rank(F+e1(e0-e1)^t)<=1 imply F e1=e1',
        'forced_image':'b3+mu*external lies in im(P5); mu!=0',
        'minor_rows_physical':[0,1,2,6,7,8],'minor_anchor_columns':[6,7,8,9],
        'minor_added_columns':['b4','b3+mu*external'],'minor':dump(minor),'determinant':-1,'tariff':5,
        'conclusion':'Every exceptional projector satisfying masks34 and28 violates rectangle(5,28).'}

def main():
    A,U,V,G,caps,f,k=frozen_geometry()
    result={'status':'PASS_COMPLETE_TWO_PARAMETER_FAMILY_OBSTRUCTION','input_sha256':PINS,'helper_sha256':HELPER_SHA256,'physical_tariffs':caps,
        'scope':'Fixed rank8 asymmetric anchor and H_t=<C0+tC1,A1,D2>, K_s=<C0+sC1,A1,D2>, 1+ts!=0. All rational rank9 extensions in this common-complement family fail physical tariffs. Other complement flags and other anchors remain open; no decoder bound changes.',
        'source_flag':list(map(str,f)),'reader_flag':list(map(str,k)),
        'automorphisms':automorphisms(A,U,V),'generic':generic(A,U,V,f,k),'exceptional':exceptional(A,U,V,f,k),
        'coefficient_samples':0,'geometry_samples':0,'mutation_controls_rejected':2}
    import sys
    receipt=HERE/'FAMILY-RESULT.json'
    if sys.argv[1:]==['--write-receipt']:
        receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:
        need(not sys.argv[1:],'only --write-receipt is accepted')
        need(json.loads(receipt.read_text(encoding='utf-8'))==result,'committed family receipt matches recomputation')
    print(json.dumps({k:result[k]for k in['status','physical_tariffs','scope','coefficient_samples','mutation_controls_rejected']},indent=2))

if __name__=='__main__':main()
