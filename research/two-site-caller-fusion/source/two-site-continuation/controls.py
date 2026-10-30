#!/usr/bin/env python3
"""Exact noncommuting control for the two-unary correction order.
Apache-2.0; substantial OpenAI Codex assistance.
"""
import hashlib,json,argparse
from two_site import *

def produce():
 n,m=2,4;N=n_pair(m,0);P0=plane_swap(m,0,1)
 events=[{'kind':'NATIVE','bank':0,'x_monomial':N.data(),'rank_per_f':2,'label':'old first'},
         {'kind':'ADD','dst':1,'src':0,'coefficient':'1','label':'couple1'},
         {'kind':'ADD','dst':0,'src':1,'coefficient':'1','label':'couple2'},
         {'kind':'ADDRESS_OR_UNIT','bank':1,'x_monomial':P0.data(),'rank_per_f':0,'label':'old second'}]
 I=eye(n,m);A,B=pair_columns(events,0,3,n,m);V=qc.replay(events[1:],n,m);Vi=qc.replay(inverse(events[1:],m),n,m)
 X,Y=mono(P0@N),mono(N.inv());DX=eye(n,m);DX[0][0]=X;DY=eye(n,m);DY[1][1]=Y
 C=mm(DY,mm(V,mm(DX,Vi)));result,status,equation=solve(C,A,B,1,I)
 need(status=='accepted'and result==(X,Y),'independently assembled noncommuting product recovers both exact factors')
 need(mm(V,Vi)==mm(Vi,V)==I,'independent intervening word inverse')
 wrong=mm(V,mm(DX,mm(Vi,DY)));bad,bstatus,_=solve(wrong,A,B,1,I)
 need(bad!=(X,Y),'reversing correction order does not preserve the claimed factors')
 return{'status':'PASS_EXACT_NONCOMMUTING_TWO_SITE_CONTROLS','correct_order':'C=Y_j V X_i V^-1','wrong_order_rejection':bstatus,
         'equation':list(equation),'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'solver_sha256':hashlib.sha256((HERE/'two_site.py').read_bytes()).hexdigest()}
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();out=produce();path=HERE/'CONTROLS.json'
 if a.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(path.read_text())==out,'saved two-site controls differ')
 print(out['status'])
if __name__=='__main__':main()
