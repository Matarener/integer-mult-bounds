"""root gauge for route_b --gauge (port of MOONSHOT3/blindcode.py): BLIND biorthogonal cliques x u/z flip -> (C2,S4,L,U) with the same residual."""
import pickle,os,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); DATA=HERE+"/data"
def gauge(UZ):
    import sympy as sp
    from fractions import Fraction as Q
    E=pickle.load(open(DATA+'/exact8.pkl','rb')); A,V,R=E['A'],E['V'],E['R']
    D=pickle.load(open(DATA+'/dual.pkl','rb')); n=104
    R_=lambda x: sp.Rational(x.numerator,x.denominator)
    Vm=sp.Matrix([[R_(x) for x in row] for row in V]); Am=sp.Matrix([[R_(x) for x in row] for row in A])
    Minv=sp.Matrix([[sp.nsimplify(x) for x in D['Y'][u]] for u,z in UZ])
    Mc=sp.Matrix.hstack(*[sp.Matrix([sp.nsimplify(x) for x in D['M'][z]]) for u,z in UZ])
    P=Minv*Mc
    if not all(P[i,j]==0 for i in range(8) for j in range(8) if i!=j): return None
    A2=Am*Mc; V2=sp.diag(*[1/P[k,k] for k in range(8)])*Minv*Vm
    for k in range(8):
        a=max(abs(x) for x in A2[:,k] if x); A2[:,k]=A2[:,k]/a; V2[k,:]=V2[k,:]*a
    return np.array(A2.tolist(),dtype=float),np.array(V2.tolist(),dtype=float)
_J=None
def res0():
    global _J
    if _J is None:
        import json; J=json.load(open(os.path.dirname(HERE)+'/synth/data/sign_code.json'))
        _J=(2*np.array(J['C2'])@np.array(J['S4']))/4.0-np.eye(104)
    return _J
def make(UZ=None):
    A,V=gauge(UZ)
    if A is None: return None
    R=A@V
    T=res0()+np.eye(104); Q=np.sign(R*T); n=104
    s={0:1}; t={}; st=[('r',0)]
    while st:
        k,a=st.pop()
        for b in range(n):
            if k=='r':
                if Q[a,b]!=0 and b not in t: t[b]=Q[a,b]*s[a]; st.append(('c',b))
            else:
                if Q[b,a]!=0 and b not in s: s[b]=Q[b,a]*t[a]; st.append(('r',b))
    S=np.array([s[j] for j in range(n)]); Tt=np.array([t[i] for i in range(n)])
    C2=(S[:,None]*A); S4=(2*V*Tt[None,:])
    if not (set(np.unique(C2))<={-1,0,1} and set(np.unique(S4))<={-1,0,1}): return None
    C2=C2.astype(int); S4=S4.astype(int)
    if not np.allclose(C2@S4/2-np.eye(n),res0()): return None
    return C2,S4,[z for u,z in UZ],[u for u,z in UZ]

def gauge_uz(g):
    """gauge index 0..15 = clique g//2 of data/cliques8.pkl, u/z flip g%2 (MOONSHOT3 numbering g<clique>_<flip>)"""
    cl=pickle.load(open(DATA+'/cliques8.pkl','rb')); UZ=cl[g//2]
    return [(z,u) for u,z in UZ] if g%2 else list(UZ)
