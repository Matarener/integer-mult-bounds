#!/usr/bin/env python3
"""Exact per-port hybrid seed and necessary uniform common-prefix budget.

Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from hashlib import sha256
import argparse
import gzip
import json
from global_kernel_boost import HERE,RAW,basis,contains
from cold_cosets import need

# F2[N]/(N^2-1), monomial bits I=1,N=2.
def mul(a,b):
    z=0
    for i in range(2):
        for j in range(2):
            if a>>i&1 and b>>j&1:z^=1<<((i+j)%2)
    return z

def mm(A,B):
    return [[mul(A[i][0],B[0][j])^mul(A[i][1],B[1][j])for j in range(2)]for i in range(2)]

def receipt():
    raw=json.loads(gzip.decompress(RAW.read_bytes()));Bs=[basis(raw['lines'][p]for p in f)for f in raw['frames']]
    current=raw['start'][:]
    for f,h,ss in raw['A']:
        for r in[h]+ss:current[r]=f
    census=[]
    for d in range(1,8):
        E=basis(raw['lines'][:d])
        lifted=[p for p in range(111)if not all(contains(Bs[raw['final'][111+p]],q)for q in E)]
        C=[len(basis(Bs[current[h]]+E))-d for h in raw['ret']]
        cap=111-len(lifted);bill=sum(C)
        need(cap<=bill,'coordinate-plane uniform caller has no positive uncovered dividend')
        census.append({'E_axes':list(range(d)),'target_FULL_lifts':len(lifted),'remaining_cap_ports':cap,
                       'nine_COPY_ranks':C,'private_query_rank':bill,'D_per_call_upper':cap-bill})
    need([(z['remaining_cap_ports'],z['private_query_rank'])for z in census]==[(56,56),(28,52),(12,44),(11,35),(3,27),(2,18),(1,9)],'frozen coordinate-plane price census')
    F0=[[1,0],[2,1]];B0=[[1,2],[0,1]]
    F1=[[1,0],[1,2]];B1=[[2,1],[0,1]]
    T0=mm(mm(F0,B0),F0);T1=mm(mm(F1,B1),F1)
    need(T0==[[0,2],[2,0]],'old cap FBF seed')
    need(T1==[[3,2],[1,3]]and mm(T1,T1)==[[2,0],[0,2]],'FULL hybrid FBF and squared seed')
    return {'status':'PASS_EXACT_HYBRID_SEEDS_AND_COORDINATE_PLANE_NECESSARY_BUDGET','no_new_kappa':True,
            'source':{str(RAW):sha256(RAW.read_bytes()).hexdigest()},'ring':'F2[N]/(N^2-I)',
            'coefficient_encoding':{'0':0,'1':'I','2':'N','3':'I+N'},
            'cap_F':F0,'cap_B':B0,'FULL_F':F1,'FULL_B':B1,'cap_FBF':T0,'FULL_FBF':T1,
            'FULL_FBF_squared':mm(T1,T1),'coordinate_planes':census,
            'written_all_parameter_rank_argument':'In a fixed port put d=I+N, d^2=0. Each normalized hybrid local call equals an invertible constant bank matrix times I+d*R with rank(R)=1. Arbitrary constant bank-GL adapters preserve that rank. In a product, the coefficient of d is a sum of k conjugated rank-one matrices because all degree>=2 terms vanish. A final common N on n independent banks requires this sum to equal I_n after the constant endpoint is removed, hence n<=k by rank subadditivity. There are111 common-rank units per bank, while each call already pays one common unit on every FULL-lifted target port plus all nine private COPY query ranks. Therefore D<=111*n-k*(number_FULL_lifts+private_rank)<=k*(remaining_cap_ports-private_rank). All seven stored coordinate planes give D<=0.',
            'domain':'Uniform repeated hybrid local family and common-prefix scalar bank-GL callers, all111 ports retained, every target lift and copied-total tariff charged. No owner/stock premise is used for this necessary rejection.',
            'limits':['Port-mixing operator-valued bank adapters, nonuniform E families, changed public codes or source cuts are outside this rank argument.','No all-parameter native supplier or formal-kernel proof is claimed.']}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();out=receipt();p=HERE/'HYBRID-BUDGET.json'
    if a.write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==out,'saved hybrid budget differs')
    print(out['status']);print('D_per_call_upper',[z['D_per_call_upper']for z in out['coordinate_planes']])

if __name__=='__main__':main()
