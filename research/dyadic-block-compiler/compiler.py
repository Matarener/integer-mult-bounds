"""Exact dyadic column-lattice factorization and one-temporary block compiler.
Apache-2.0; Dugongue with substantial OpenAI assistance.
"""
from fractions import Fraction as Q

def need(ok, why):
    if not ok: raise ValueError(why)

def dyadic(value):
    value=Q(value)
    need(value.denominator & (value.denominator-1)==0, 'Native scalars must be dyadic')
    return value

def factor(matrix):
    M=[[dyadic(x) for x in row] for row in matrix]
    need(M and M[0] and all(len(row)==len(M[0]) for row in M),'Nonempty rectangular matrix')
    m,n=len(M),len(M[0]);scale=max(x.denominator for row in M for x in row)
    # Invariant: A * S = scale * M; inverse column moves update rows of S.
    A=[[int(x*scale) for x in row] for row in M]
    S=[[int(i==j) for j in range(n)] for i in range(n)]
    pivots=[];p=0;operations=0
    def swap(a,b):
        for row in A:row[a],row[b]=row[b],row[a]
        S[a],S[b]=S[b],S[a]
    for i in range(m):
        j=next((j for j in range(p,n) if A[i][j]),None)
        if j is None:continue
        swap(p,j)
        for j in range(p+1,n):
            while A[i][j]:
                q=A[i][j]//A[i][p]
                for row in A:row[j]-=q*row[p]
                # col_j -= q * col_p; inverse action is row_p += q * row_j.
                S[p]=[a+q*b for a,b in zip(S[p],S[j])]
                operations+=1
                if A[i][j]:swap(p,j)
        if A[i][p]<0:
            for row in A:row[p]=-row[p]
            S[p]=[-x for x in S[p]]
        pivots.append(i);p+=1
        if p==n:break
    need(all(not any(row[p:]) for row in A),'Zero trailing columns')
    U=[[Q(x,scale) for x in row[:p]] for row in A];V=[[Q(x) for x in row]for row in S[:p]]
    need(all(sum((U[i][k]*V[k][j] for k in range(p)),Q(0))==M[i][j] for i in range(m) for j in range(n)),'Exact factorization')
    return {'matrix':M,'left':U,'right':V,'rank':p,'pivot_rows':pivots,'euclidean_steps':operations}

def add_cost(value):
    q=dyadic(value);n,d=abs(q.numerator),q.denominator
    if not n:return 0
    return 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)

def emit_factor(U, V, query_rank):
    need(isinstance(query_rank,int) and query_rank>=0,'Nonnegative query rank')
    r=len(V)
    need(U and all(len(row)==r for row in U), 'Factor dimensions')
    if r:need(V[0] and all(len(row)==len(V[0]) for row in V), 'Right factor dimensions')
    U=[[dyadic(x) for x in row] for row in U];V=[[dyadic(x) for x in row] for row in V]
    program=[]
    for k in range(r):
        program.append(['clear',['T',0]])
        for i,q in enumerate(V[k]):
            if q:program.append(['add',['T',0],['X',i],q.numerator,q.denominator])
        # Kept even at rank zero: a rank-zero physical map can have monomial work.
        program.append(['query',['T',0],query_rank])
        for j,row in enumerate(U):
            q=row[k]
            if q:program.append(['add',['Y',j],['T',0],q.numerator,q.denominator])
        program.append(['clear',['T',0]])
    cost=sum(2 if e[0]=='clear' else add_cost(Q(e[3],e[4])) if e[0]=='add' else 0 for e in program)
    return {'program':program,'owned_peak':int(r>0),'productive_temporary_credit':0,'conditional_paid':{query_rank:r}if query_rank and r else {},'scalar_allowance':cost,'monomial_route_episodes':r,'declared_query_rank':query_rank}


def compile_block(matrix, query_rank=0):
    """Rank bill is conditional on the caller's exact physical query contract.
    Same-chart source cases below supply the identity query, whose rank is zero.
    """
    f=factor(matrix)
    return f|emit_factor(f['left'],f['right'],query_rank)

def dual_factor(left,right):
    """Factor -M^T as (-V^T) U^T, with identical coefficient allowances."""
    r=len(right)
    need(r>0,'Use the identity directly for a zero block')
    return [[-right[k][i] for k in range(r)] for i in range(len(right[0]))], [[left[j][k] for j in range(len(left))]for k in range(r)]

def encode(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {str(k):encode(v) for k,v in value.items()}
    if isinstance(value,list):return [encode(v) for v in value]
    return value

def main():
    import argparse,json
    from pathlib import Path
    ap=argparse.ArgumentParser(description='Compile a dyadic matrix into a one-temporary shear. Query rank is a declared interface premise, not certified by this compiler.')
    ap.add_argument('matrix',type=Path)
    ap.add_argument('--query-rank',type=int,default=0)
    args=ap.parse_args()
    result=compile_block(json.loads(args.matrix.read_text(encoding='utf-8')),args.query_rank)
    print(json.dumps(encode(result),indent=2))

if __name__=='__main__':main()
