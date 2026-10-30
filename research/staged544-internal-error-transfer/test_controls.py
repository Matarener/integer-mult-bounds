"""Independent dense oracles and discriminating mutations; Apache-2.0."""
from fractions import Fraction as Q
import copy,gzip,json,subprocess,sys,tempfile
import verify as v

def matmul(a,b):return [[sum((x*y for x,y in zip(row,col)),Q(0)) for col in zip(*b)] for row in a]
def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def direct(seq,n,blocks=1,operators=None,inject=None):
    M=eye(n*blocks)
    for i,g in enumerate(seq):
        G=eye(n*blocks);kind,t=g[:2]
        if kind=='add':
            W=eye(blocks)
            for op in reversed(g[4]):W=matmul(operators[op],W)
            for x in range(blocks):
                for y in range(blocks):G[t*blocks+x][g[2]*blocks+y]+=g[3]*W[x][y]
        elif kind=='scale':
            for x in range(blocks):G[t*blocks+x][t*blocks+x]=g[2]
        else:
            for x in range(blocks):
                for y in range(blocks):G[t*blocks+x][t*blocks+y]=operators[g[2]][x][y]
        M=matmul(G,M)
    return M

def evaluate_rows(rows,n,operators):
    out=[[Q(0) for _ in range(n*2)] for _ in range(n*2)]
    for r,row in rows.items():
        for (s,word),q in row.items():
            W=eye(2)
            for op in reversed(word):W=matmul(operators[op],W)
            for x in range(2):
                for y in range(2):out[2*r+x][2*s+y]+=q*W[x][y]
    return out

def main():
    seq=[('add',0,1,Q(2),(),'a'),('scale',1,Q(-1,2),'a'),('add',2,0,Q(3,4),(),'b'),('add',0,1,Q(4),(),'b'),('scale',2,Q(2),'b'),('add',1,2,Q(-1),(),'c')]
    rows,fw=v.forward([0,1,2],seq);cols,fault,rw=v.backward([0,1,2],seq);M=direct(seq,3)
    for r in range(3):
        for s in range(3):v.need(rows[r].get((s,()),0)==M[r][s],'dense endpoint')
    expected=[Q(0)]*3
    for i,g in enumerate(seq):
        suffix=direct(seq[i+1:],3)
        for r in range(3):expected[r]+=abs(suffix[r][g[1]])
    v.need(expected==[fault[r] for r in range(3)],'independent dense fault oracle')
    def inverse(M):
        n=len(M);A=[list(row)+e for row,e in zip(M,eye(n))]
        for c in range(n):
            pivot=next(i for i in range(c,n) if A[i][c]);A[c],A[pivot]=A[pivot],A[c];q=A[c][c];A[c]=[x/q for x in A[c]]
            for r in range(n):
                if r!=c:
                    q=A[r][c];A[r]=[x-q*y for x,y in zip(A[r],A[c])]
        return [row[n:] for row in A]
    peak=Q(3);column_sum=Q(0);full_sum=Q(3)
    for i,g in enumerate(seq):
        B=inverse(direct(seq[:i+1],3));peak=max(peak,sum(max(abs(row[c]) for row in B) for c in range(3)));column_sum+=max(abs(row[g[1]]) for row in B);full_sum+=sum(max(abs(row[c]) for row in B) for c in range(3))
    inv=v.inverse_prefix([0,1,2],seq)
    v.need(Q(inv['inverse_prefix_column_sum_bound'])==peak,'dense inverse-prefix range')
    v.need(Q(inv['inverse_prefix_fault_column_sum'])==column_sum,'dense inverse-prefix fault columns')
    v.need(Q(inv['inverse_prefix_full_state_cut_sum'])==full_sum,'dense all-register cut transfer')
    R=[[Q(0),Q(-1)],[Q(1),Q(0)]];Ri=[[Q(0),Q(1)],[Q(-1),Q(0)]];F=[[Q(1),Q(0)],[Q(0),Q(-1)]]
    ops={1:R,-1:Ri,2:F,-2:F}
    a=[('warp',0,1,'a'),('add',1,0,Q(-3,2),(2,1),'b'),('warp',0,-1,'c'),('add',2,1,Q(1,4),(-2,),'c')]
    rows,_=v.forward([0,1,2],a);v.need(evaluate_rows(rows,3,ops)==direct(a,3,2,ops),'noncommuting dense oracle')
    def inverse_capture(i,cols):
        rows={r:{} for r in range(3)}
        for source,col in cols.items():
            for (target,word),q in col.items():rows[target][source,word]=q
        v.need(evaluate_rows(rows,3,ops)==inverse(direct(a[:i+1],3,2,ops)),'noncommuting inverse-prefix oracle')
    v.inverse_prefix([0,1,2],a,capture=inverse_capture)
    v.need(v.reduce_word((1,2),(-2,-1))==(),'inverse cancellation')
    v.need(v.reduce_word((1,2),(-1,-2))==(1,2,-1,-2),'do not commute')
    v.need(v.max_bits(Q(1335))==11 and v.max_bits(Q(4841))==13,'guard bits')
    # The all-cut positive path bounds dominate every concrete prefix fault sum.
    A=Q(fw['positive_path_all_cut_fault_gain'])
    for stop in range(1,len(seq)+1):
        sums=[Q(0)]*3
        for i,g in enumerate(seq[:stop]):
            S=direct(seq[i+1:stop],3)
            for r in range(3):sums[r]+=abs(S[r][g[1]])
        v.need(max(sums)<=A,'all-cut fault envelope')
    # Input/source mutation rejects before expensive scientific work.
    b=(v.P/'inputs/WORD-base.json.gz').read_bytes();meta=json.loads((v.P/'FROZEN-SOURCES.json').read_text())['files']['inputs/WORD-base.json.gz']
    v.need(v.hashlib.sha256(b+b' ').hexdigest()!=meta['sha256'],'source mutation predicate')
    with tempfile.TemporaryDirectory() as d:
        root=v.Path(d);(root/'verify.py').write_bytes((v.P/'verify.py').read_bytes());(root/'FROZEN-SOURCES.json').write_bytes((v.P/'FROZEN-SOURCES.json').read_bytes())
        first=next(iter(json.loads((v.P/'FROZEN-SOURCES.json').read_text())['files']))
        target=root/first;target.parent.mkdir(parents=True);target.write_bytes((v.P/first).read_bytes()+b' ')
        r=subprocess.run([sys.executable,'-B',str(root/'verify.py')],capture_output=True,text=True)
        v.need(r.returncode!=0 and 'source hash '+first in r.stderr and 'checked ' not in r.stdout,'production source mutation rejection')
    # Production omission of compensation must violate actual endpoint identity.
    w=json.loads(gzip.decompress(b));z=copy.deepcopy(w);z['compensation']=[]
    rejected=[]
    try:v.analyze(z)
    except ValueError as e:
        v.need(str(e)=='live-input shear contract','wrong compensation rejection');rejected.append('omit compensation')
    else:raise ValueError('accepted missing compensation')
    # One bad cleanup scalar must spoil the full arbitrary-dirty identity.
    z=copy.deepcopy(w);g=next(g for g in z['cleanup'] if g[0]=='add');g[3]=-g[3]
    try:v.analyze(z)
    except ValueError as e:
        v.need(str(e) in ('private buffer identity','live-input shear contract'),'wrong cleanup rejection');rejected.append('flip cleanup coefficient')
    else:raise ValueError('accepted cleanup corruption')
    z=copy.deepcopy(w);buf=704+min(map(int,w['helper_final']));z['cleanup'].append(['add',112,buf,1,1,[]])
    try:v.analyze(z)
    except ValueError as e:
        v.need(str(e)=='private buffer leakage','wrong buffer-leak rejection');rejected.append('inject dirty buffer into live target')
    else:raise ValueError('accepted dirty-buffer leakage')
    z=copy.deepcopy(w);z['cleanup'].append(['scale',buf,2,1,[]])
    try:v.analyze(z)
    except ValueError as e:
        v.need(str(e)=='private buffer identity','wrong buffer-return rejection');rejected.append('double private buffer return')
    else:raise ValueError('accepted dirty-buffer self-map corruption')
    protected=v.P/'RESULT.json';before=protected.read_bytes()
    r=subprocess.run([sys.executable,'-B',str(v.P/'verify.py'),'--emit',str(protected)],capture_output=True,text=True)
    v.need(r.returncode!=0 and 'outside frozen package' in r.stderr and protected.read_bytes()==before,'emit protects frozen package')
    with tempfile.TemporaryDirectory() as d:
        p=v.Path(d)/'existing.json';p.write_text('sentinel')
        r=subprocess.run([sys.executable,'-B',str(v.P/'verify.py'),'--emit',str(p)],capture_output=True,text=True)
        v.need(r.returncode!=0 and 'already exists' in r.stderr and p.read_text()=='sentinel','emit protects existing output')
    print(json.dumps({'PASS':True,'dense_scalar_fault_oracle':True,'noncommuting_unitary_oracle':True,'all_cut_fault_envelope':True,'source_mutation':True,'production_rejections':rejected},sort_keys=True))
if __name__=='__main__':main()
