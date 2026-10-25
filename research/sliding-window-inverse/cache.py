# SPDX-License-Identifier: Apache-2.0
"""Exact rational principal-window inverse updates, not a physical tape compiler.
Dugongue, with substantial OpenAI Codex assistance. See PROOF.md.
"""
from fractions import Fraction as F
from hashlib import sha256
import json

def need(ok,message):
    if not ok:raise ValueError(message)

class Arithmetic:
    def __init__(self):self.counts={'add':0,'sub':0,'mul':0,'div':0}
    def add(self,a,b):self.counts['add']+=1;return a+b
    def sub(self,a,b):self.counts['sub']+=1;return a-b
    def mul(self,a,b):self.counts['mul']+=1;return a*b
    def div(self,a,b):
        need(b!=0,'nonzero exact pivot');self.counts['div']+=1;return a/b
    def total(self):return sum(self.counts.values())
    def dot(self,a,b):
        need(len(a)==len(b),'dot dimensions')
        if not a:return F(0)
        z=self.mul(a[0],b[0])
        for x,y in zip(a[1:],b[1:]):z=self.add(z,self.mul(x,y))
        return z
    def mm(self,A,B):
        if not A:return []
        return [[self.dot(row,[B[k][j] for k in range(len(B))]) for j in range(len(B[0]))] for row in A]

def identity(n):return [[F(i==j) for j in range(n)] for i in range(n)]

def dense_inverse(A,ops=None):
    o=Arithmetic() if ops is None else ops;n=len(A)
    need(n>0 and all(len(r)==n for r in A),'nonempty square inverse')
    M=[list(map(F,row))+identity(n)[i] for i,row in enumerate(A)]
    for k in range(n):
        pivot=next((i for i in range(k,n) if M[i][k]),None)
        need(pivot is not None,'nonsingular matrix')
        M[k],M[pivot]=M[pivot],M[k];d=M[k][k]
        M[k]=[o.div(v,d) for v in M[k]]
        for i in range(n):
            if i==k:continue
            c=M[i][k]
            M[i]=[o.sub(v,o.mul(c,w)) for v,w in zip(M[i],M[k])]
    return [r[n:] for r in M]

def freeze(H):
    n=len(H);need(n>1 and all(len(row)==n for row in H),'square global source')
    need(all(type(v) in (int,F) for row in H for v in row),'exact rational entries')
    return tuple(tuple(F(v) for v in row) for row in H)

def fingerprint(H):return sha256(json.dumps([[str(v) for v in row] for row in H],separators=(',',':')).encode()).hexdigest()
def principal(H,labels):return [[H[i][j] for j in labels] for i in labels]

def weighted(H,weights):
    need(len(weights)==len(H) and all(type(v) in (int,F) and v>0 for v in weights),'positive rational weights')
    return [[F(H[i][j])*F(weights[j])/F(weights[i]) for j in range(len(H))] for i in range(len(H))]

def norm_inf(A):return max((sum(abs(v) for v in row) for row in A),default=F(0))
def dominance_gap(G):return min(G[i][i]-sum(abs(v) for j,v in enumerate(G[i]) if i!=j) for i in range(len(G)))

class WindowCache:
    """Frozen source and read-only inverse view. Trusted methods preserve its invariant."""
    def __init__(self,H,labels,weights=None):
        self._source=freeze(H);self.source_digest=fingerprint(self._source)
        self.weights=tuple(F(v) for v in (weights if weights is not None else [1]*len(H)))
        self.gap=dominance_gap(weighted(self._source,self.weights));need(self.gap>0,'weighted strict diagonal dominance')
        need(len(labels)>0 and len(set(labels))==len(labels) and all(type(i) is int and 0<=i<len(H) for i in labels),'distinct valid source labels')
        self.labels=tuple(labels);self.ops=Arithmetic()
        self._inverse=tuple(map(tuple,dense_inverse(principal(self._source,labels),self.ops)))
        self.initial_operations=self.ops.total()
    @property
    def inverse(self):return self._inverse
    def slide(self,incoming,source_digest=None,method='schur'):
        need(source_digest is None or source_digest==self.source_digest,'source identity changed')
        need(type(incoming) is int and 0<=incoming<len(self._source),'incoming source label')
        need(incoming not in self.labels[1:],'incoming aliases retained label')
        need(method in ('schur','woodbury'),'known update method')
        before=self.ops.total();n=len(self.labels);o=self.ops
        # Move outgoing first coordinate to the end by simultaneous row/column permutation.
        perm=list(range(1,n))+[0];Q=[[self._inverse[i][j] for j in perm] for i in perm]
        old_labels=self.labels[1:]+self.labels[:1];new_labels=self.labels[1:]+(incoming,)
        H=self._source
        if method=='schur':
            k=n-1;need(Q[k][k]!=0,'principal downdate pivot')
            f=[o.div(Q[i][k],Q[k][k]) for i in range(k)]
            E=[[o.sub(Q[i][j],o.mul(f[i],Q[k][j])) for j in range(k)] for i in range(k)]
            u=[H[i][incoming] for i in new_labels[:-1]];v=[H[incoming][j] for j in new_labels[:-1]]
            w=[o.dot(row,u) for row in E];z=[o.dot(v,[E[i][j] for i in range(k)]) for j in range(k)]
            sigma=o.sub(H[incoming][incoming],o.dot(v,w));inv=o.div(F(1),sigma)
            wi=[o.mul(a,inv) for a in w]
            Z=[[o.add(E[i][j],o.mul(wi[i],z[j])) for j in range(k)]+[-wi[i]] for i in range(k)]
            Z.append([-o.mul(inv,a) for a in z]+[inv])
        else:
            last=n-1
            col=[o.sub(H[new_labels[i]][incoming],H[old_labels[i]][old_labels[-1]]) for i in range(n)]
            row=[o.sub(H[incoming][new_labels[j]],H[old_labels[-1]][old_labels[j]]) for j in range(n)]
            row[-1]=F(0) # diagonal difference is counted in the column, exactly once.
            U=[[col[i],F(i==last)] for i in range(n)]
            V=[[F(j==last) for j in range(n)],row]
            QU=o.mm(Q,U);VQ=o.mm(V,Q);core=o.mm(V,QU)
            for i in range(2):core[i][i]=o.add(core[i][i],F(1))
            a,b=core[0];c,d=core[1];det=o.sub(o.mul(a,d),o.mul(b,c));need(det!=0,'Woodbury core pivot')
            C=[[o.div(d,det),o.div(-b,det)],[o.div(-c,det),o.div(a,det)]]
            correction=o.mm(o.mm(QU,C),VQ)
            Z=[[o.sub(Q[i][j],correction[i][j]) for j in range(n)] for i in range(n)]
        self.labels=new_labels;self._inverse=tuple(map(tuple,Z))
        return self.ops.total()-before
    def apply(self,b):
        need(len(b)==len(self.labels),'payload length')
        return tuple(sum((a*F(v) for a,v in zip(row,b)),F(0)) for row in self._inverse)

def rounded_weighted_inverse(cache,bits):
    need(type(bits) is int and bits>=0,'dyadic precision');S=1<<bits;D=[cache.weights[i] for i in cache.labels]
    Z=weighted(cache.inverse,D)
    return [[F(int(v*S),S) for v in row] for row in Z]

def residual_certificate(H,labels,weights,Z):
    G=weighted(principal(H,labels),[weights[i] for i in labels]);n=len(G)
    need(len(Z)==n and all(len(r)==n for r in Z),'candidate inverse shape')
    need(all(type(v) in (int,F) for row in Z for v in row),'exact candidate entries')
    product=[[sum((G[i][k]*Z[k][j] for k in range(n)),F(0)) for j in range(n)] for i in range(n)]
    rho=norm_inf([[F(i==j)-product[i][j] for j in range(n)] for i in range(n)])
    gap=dominance_gap(G);need(gap>0 and rho<1,'sufficient inverse residual')
    return {'residual':str(rho),'gap':str(gap),'inverse_error_bound':str(rho/gap),
            'neumann_inverse_bound':str(norm_inf(Z)/(1-rho))}


def publish_owned(memory,ports,values):
    need(len(ports)==len(values) and len(set(ports))==len(ports),'injective output port map')
    result=dict(memory)
    for port,value in zip(ports,values):result[port]=value
    return result

def round_nearest_integer(value):
    value=F(value)+F(1,2)
    return value.numerator//value.denominator


def apply_owned(cache,memory,ports):
    need(len(ports)==len(cache.labels) and len(set(ports))==len(ports),'injective caller ports')
    return publish_owned(memory,ports,cache.apply([memory[i] for i in ports]))

def block_energy_factor(width,gap):
    need(type(width) is int and width>0 and gap>0,'block bound inputs')
    needed=F(width)/(gap*gap);depth=0
    while F(4)**depth<needed:depth+=1
    return depth,F(4)**depth


def recover_known_integer(approximate,error_bound):
    """Requires the exact target to be integral and the supplied bound to be proved."""
    need(type(error_bound) in (int,F) and 0<=error_bound<F(1,2),'strict known-integer error bound')
    return tuple(round_nearest_integer(v) for v in approximate)

def inverse_height_bound(H,width):
    B=max(max(abs(F(v).numerator).bit_length(),F(v).denominator.bit_length()) for row in H for v in row)
    return width*(width+1)*B+width*(max(width,2)-1).bit_length()+3
