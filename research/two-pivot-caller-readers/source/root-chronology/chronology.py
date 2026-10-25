#!/usr/bin/env python3
"""Exact signed native-block permutation algebra. Apache-2.0; Codex assistance.

This small census covers only one source N, one target T, source S wrappers,
one delivery ADD. It neither enumerates general monomial circuits nor callers.
"""
from dataclasses import dataclass
from itertools import permutations
from pathlib import Path
import argparse, hashlib, json

def need(p, m):
    if not p:
        raise ValueError(m)

@dataclass(frozen=True)
class Op:
    sign: int
    mask: int
    perm: tuple

    def __matmul__(self, b):
        moved = sum(1 << self.perm[i] for i in range(len(self.perm)) if b.mask >> i & 1)
        phase = -1 if (self.mask & moved).bit_count() % 2 else 1
        return Op(self.sign * b.sign * phase, self.mask ^ moved,
                  tuple(self.perm[b.perm[i]] for i in range(len(self.perm))))

    def inverse(self):
        ip = tuple(self.perm.index(i) for i in range(len(self.perm)))
        mask = sum(1 << ip[i] for i in range(len(ip)) if self.mask >> i & 1)
        return Op(self.sign * (-1 if self.mask.bit_count() % 2 else 1), mask, ip)

    def data(self):
        return dict(sign=self.sign, native_blocks=[i for i in range(len(self.perm)) if self.mask >> i & 1],
                    block_permutation=list(self.perm), native_arity=2*self.mask.bit_count())

def ident(b):
    return Op(1, 0, tuple(range(b)))

def native(b, i):
    return Op(1, 1 << i, tuple(range(b)))

def swap(b, i):
    p = list(range(b)); p[0], p[i] = p[i], p[0]
    return Op(1, 0, tuple(p))

def conj(a, b):
    return a @ b @ a.inverse()

def run():
    b=4; I=ident(b); N=native(b,0); T=native(b,1); S=swap(b,1)
    need(S @ N == T @ S, 'native/address covariance')
    for a in [I,N,T,S,N@S,T@N@S]:
        need(a @ a.inverse() == I == a.inverse() @ a, 'literal two-sided inverse')
    # All interleavings of S_before,N,S_after on source and T on target,
    # with one ADD. Source S,N,S order is fixed. The source remains T.
    orders=[]; kernels={}
    for order in permutations(('S_before','N','S_after','T','ADD')):
        if not (order.index('S_before') < order.index('N') < order.index('S_after')):
            continue
        src=I; target=I; cross=None
        for event in order:
            if event.startswith('S_'):
                src=S@src
            elif event=='N':
                src=N@src
            elif event=='T':
                target=T@target
                if cross is not None:
                    cross=T@cross
            else:
                cross=src
        need(src==T and target==T and cross is not None, 'clean global fresh diagonal')
        kernel=T.inverse()@cross
        kernels[kernel]=kernels.get(kernel,0)+1
        orders.append(dict(events=order,kernel=kernel.data()))
    F=native(b,1)@native(b,2)@native(b,3)
    cases=[]
    for K,multiplicity in sorted(kernels.items(),key=lambda z:(z[0].mask,z[0].perm,z[0].sign)):
        # Re-label the one fresh block to make chronological pair i1,j2.
        relabel=Op(1,0,(0,2,1,3)); Ki=K; Kj=conj(relabel,K)
        D=native(b,1)
        cases.append(dict(kernel=K.data(),multiplicity=multiplicity,
                          final_single_response=(F@K).data(),
                          old_first_at_between_cut=conj(D,Ki@Kj).data(),
                          new_first_at_between_cut=conj(D,Kj@Ki).data()))
    full=[z for z in cases if z['final_single_response']['native_arity']==2*b]
    need(len(full)==1, 'one full-width single-response type in restricted chronology')
    need(full[0]['kernel']['native_blocks']==[0], 'full response is common N times swap')
    need(full[0]['old_first_at_between_cut']['native_arity']==0, 'old-first is monomial')
    need(full[0]['new_first_at_between_cut']['native_arity']==4, 'new-first costs rank4')
    # Deliberately reversing the cut product cannot inherit monomial price.
    need(full[0]['new_first_at_between_cut']['native_arity'] != 0, 'wrong product order rejected')
    return dict(status='PASS_RESTRICTED_ONE_ADD_LOCAL_CHRONOLOGY',no_new_kappa=True,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                block_count=b, complete_orders=len(orders), distinct_kernels=len(kernels),
                orders=orders,cases=cases,
                algebra='N_a commute; N_a^2=-I; P N_a P^-1=N_P(a). Exact phases and block permutations retained.',
                scope='S,N,S source chronology and one fresh target T, one delivery ADD; no common U, extra bank bridge or general local synthesis. Endpoint test is a single isolated response F_all K only.',
                all_f='Algebra holds for the independently pinned phase-normalized N_f. Native arity 2 per occupied block is 2f at chunk size f. Permutation adapters preserve native rank.',
                limits=['No general caller obstruction. A coupled word can combine several responses.',
                        'No actual whole supplier, improved BIT, joint transfer or new kappa.'])

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    out=json.loads(json.dumps(run()));dest=Path(__file__).with_name('CHRONOLOGY.json')
    if args.write:
        dest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:
        need(json.loads(dest.read_text())==out,'saved chronology differs')
    print(out['status'],out['complete_orders'],'orders',out['distinct_kernels'],'kernels')

if __name__=='__main__':
    main()
