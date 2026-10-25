#!/usr/bin/env python3
"""Exact logical K_G identification, retaining every Gaussian column phase.

The literal mode identifies only equal G matrices. The monomial mode also
identifies exactly equal finite products of the actual signed K_G operators.
Negative opcodes mean the true adjoint, never the canonical lift of G^-1.
No physical warp or frame event is removed merely by selecting this checker.
Apache-2.0; substantial OpenAI assistance.
"""
from collections import defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json, sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
GAUSS=ROOT/'research/kappa-adaptive-continuation/native-alternatives/native-base/source/native/new/code/borrow/bw_gauss.py'


def image(columns,x):
    y=0
    for j,v in enumerate(columns):
        if x>>j&1:y^=v
    return y


def recipe(columns):
    """Column x is i**phase[x] at row permutation[x], with exact integers."""
    h=len(columns);n=1<<h
    p=tuple(image(columns,x) for x in range(n));assert len(set(p))==n
    inv=[0]*n
    for x,y in enumerate(p):inv[y]=x
    inverse_columns=[inv[1<<j] for j in range(h)]
    # M=I+G^{-T}G^{-1}; form its entries by direct column dot products.
    matrix=[[int(i==j)^((inverse_columns[i]&inverse_columns[j]).bit_count()&1)
             for j in range(h)] for i in range(h)]
    phase=[]
    for y in p:
        bits=[j for j in range(h) if y>>j&1]
        phase.append((sum(matrix[j][j] for j in bits)+
                      2*sum(matrix[i][j] for i in bits for j in bits if i<j))%4)
    return p,tuple(phase)


def adjoint(a):
    p,z=a;inv=[0]*len(p)
    for x,y in enumerate(p):inv[y]=x
    return tuple(inv),tuple(-z[inv[x]]%4 for x in range(len(p)))


def compose(a,b):
    """A B, with the right operand applied first."""
    p,z=a;q,t=b
    return tuple(p[x] for x in q),tuple((t[x]+z[q[x]])%4 for x in range(len(p)))


def serial(a):
    p,z=a
    return b''.join(int(x).to_bytes(2,'little') for x in p)+bytes(z)


class OperatorQuotient:
    def __init__(self,word,mode='literal'):
        assert mode in ('literal','monomial');self.mode=mode
        self.groups=defaultdict(list);self.alias={};self.operators={}
        for op,entry in enumerate(word['warps'],1):self.groups[tuple(entry[2])].append(op)
        for columns,ops in self.groups.items():
            a=recipe(columns)
            for op in ops:
                self.alias[op]=ops[0];self.alias[-op]=-ops[0]
                self.operators[op]=a;self.operators[-op]=adjoint(a)
        n=len(next(iter(self.operators.values()))[0]);self.identity=(tuple(range(n)),(0,)*n)
        self.word_cache={():()};self.matrix_cache={():self.identity};self.representatives={serial(self.identity):()}
        self.nonfree_identifications=[]

    def normalize(self,word):
        word=tuple(word)
        if word in self.word_cache:return self.word_cache[word]
        reduced=[]
        for op in word:
            op=self.alias[op]
            if reduced and reduced[-1]==-op:reduced.pop()
            else:reduced.append(op)
        reduced=tuple(reduced)
        if self.mode=='literal':answer=reduced
        elif reduced in self.word_cache:answer=self.word_cache[reduced]
        else:
            a=self.identity
            for op in reversed(reduced):a=compose(self.operators[op],a)
            key=serial(a)
            answer=self.representatives.get(key)
            if answer is None:
                answer=reduced;self.representatives[key]=answer;self.matrix_cache[answer]=a
            elif answer!=reduced:
                self.nonfree_identifications.append({'word':list(reduced),'representative':list(answer),'matrix_sha256':sha256(key).hexdigest()})
            self.word_cache[reduced]=answer
        self.word_cache[word]=answer
        return answer

    def transformed(self,row,op,left=True):
        out={}
        for (variable,word),coefficient in row.items():
            w=self.normalize((op,)+word if left else word+(op,))
            key=(variable,w);value=out.get(key,Q(0))+coefficient
            if value:out[key]=value
            else:out.pop(key,None)
        return out

    def certificate(self):
        # Independent retained Gaussian implementation checks all 512 columns,
        # all four exact phases, and both signs for every physical opcode.
        import importlib.util
        spec=importlib.util.spec_from_file_location('equal_g_gauss',GAUSS)
        gauss=importlib.util.module_from_spec(spec);spec.loader.exec_module(gauss)
        import numpy as np
        checks=[]
        for columns,ops in self.groups.items():
            other=gauss.monomial(columns,9)
            actual=(tuple(map(int,other[0])),tuple(map(int,other[1])))
            assert actual==self.operators[ops[0]]
            for op in ops:
                for sign in (1,-1):
                    expected=self.operators[sign*op]
                    dense=gauss.apply_mono(gauss.eye(9),other,sign)
                    p,z=expected;real=np.zeros((512,512),dtype=np.int64);imag=real.copy()
                    units=((1,0),(0,1),(-1,0),(0,-1))
                    for x in range(512):real[p[x],x],imag[p[x],x]=units[z[x]]
                    assert dense[2]==0 and np.array_equal(dense[0],real) and np.array_equal(dense[1],imag)
                    assert compose(self.operators[op],self.operators[-op])==self.identity
            checks.append({'opcodes':ops,'G_columns':list(columns),'forward_sha256':sha256(serial(actual)).hexdigest(),
                           'adjoint_sha256':sha256(serial(adjoint(actual))).hexdigest(),'columns_checked_per_sign':512})
        first=next(iter(self.groups));bad=gauss.monomial(first,9,qmut=(0,2))
        phase_control=(tuple(map(int,bad[0])),tuple(map(int,bad[1])))
        assert phase_control!=recipe(first),'wrong quadratic phase must reject despite same permutation'
        return {'status':'EXACT_512_COLUMN_LOGICAL_OPERATOR_QUOTIENT_PASS','mode':self.mode,'physical_opcodes':len(self.alias)//2,
                'literal_distinct_G':len(self.groups),'equal_G_classes':[v for v in self.groups.values() if len(v)>1],
                'forward_and_true_adjoint_checked':True,'wrong_quadratic_phase_control_rejected':True,'classes':checks,
                'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),GAUSS)}}


def install(word,mode='literal'):
    """Install only into loaded Python modules; frozen files are never edited."""
    import network_search as n
    import exact_rows as e
    import response_routes as r
    quotient=OperatorQuotient(word,mode)
    original_execute=e.execute

    def execute(rows,event):
        if event[0]=='warp':rows[event[1]]=quotient.transformed(rows[event[1]],event[2],True)
        else:original_execute(rows,event)

    def replay(w,source_only=False):
        live=set(range(704))-set(w['removed'])
        rows={v:{(v,()):Q(1)} if not source_only or v<112 else {} for v in live}
        for term in w['initial_corrections']:
            s=term['source'];assert not 112<=s<224
            if not source_only or s<112:
                e.add(rows[term['target']],{(s,quotient.normalize(term['operator_word'])):Q(1)},Q(term['coefficient']))
        for event in w['precondition']+w['compensation']+w['A']:execute(rows,event)
        captures={v:dict(rows[v]) for v in w['centers']}
        for event in w['cut']+n.F.expand(w)['B']+w['restore']:execute(rows,event)
        for v in w['helper_final']:rows[704+int(v)]={}
        for event in w['cleanup']:execute(rows,event)
        return rows,captures

    def backward(columns,event):
        kind,d=event[:2]
        if kind=='add':e.add(columns[event[2]],columns[d],Q(event[3],event[4]))
        elif kind=='scale':columns[d]={k:Q(event[2],event[3])*v for k,v in columns[d].items() if Q(event[2],event[3])*v}
        elif kind=='warp':columns[d]=quotient.transformed(columns[d],event[2],False)
        else:raise ValueError(kind)

    e.execute=execute;e.replay=replay;n.execute=execute;n.replay=replay;r.backward=backward
    return quotient
