#!/usr/bin/env python3
"""Exact Gaussian-dyadic 128-port local extension of the modern omitted core.

This is a finite changed local contract, not a global supplier or kappa claim.
SPDX-License-Identifier: Apache-2.0
Substantial OpenAI Codex assistance under user direction.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
WORKSPACE = REPO.parent
COMPONENT = WORKSPACE / "recovered-involutory/modern_native_component.py"
COMPONENT_SHA = "f6769f1ecd6b2e582748805b3afcf4c65824ba108ce7f23a4d011c45f8b724de"
INPUTS = WORKSPACE / "recovered-involutory/modern-source/inputs"
SX = (224, 225, 227, 229, 240, 241, 256, 257)
TX = (231, 232, 233, 234, 235, 236, 237, 238)


class G:
    __slots__ = ("r", "i")
    def __init__(self, r=0, i=0):
        if isinstance(r,G): self.r,self.i=r.r,r.i
        else: self.r,self.i=F(r),F(i)
    def __add__(a,b):
        b=G(b);return G(a.r+b.r,a.i+b.i)
    __radd__=__add__
    def __neg__(a):return G(-a.r,-a.i)
    def __sub__(a,b):return a+-G(b)
    def __rsub__(a,b):return G(b)+-a
    def __mul__(a,b):
        b=G(b);return G(a.r*b.r-a.i*b.i,a.r*b.i+a.i*b.r)
    __rmul__=__mul__
    def __truediv__(a,b):
        b=G(b);n=b.r*b.r+b.i*b.i
        return G((a.r*b.r+a.i*b.i)/n,(a.i*b.r-a.r*b.i)/n)
    def __bool__(a):return bool(a.r or a.i)
    def __eq__(a,b):
        b=G(b);return a.r==b.r and a.i==b.i
    def norm(a):return abs(a.r)+abs(a.i)
    def data(a):return [a.r.numerator,a.r.denominator,a.i.numerator,a.i.denominator]
    @staticmethod
    def read(v):return G(F(v[0],v[1]),F(v[2],v[3]))


def add(dst,src,q=G(1)):
    q=G(q)
    if not q:return
    for k,a in src.items():
        value=dst.get(k,G())+q*a
        if value:dst[k]=value
        else:dst.pop(k,None)


def module(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def scalar(op,target,source=None,q=G(1),frame=0):
    return ["gaussian_scalar",op,list(target),list(source) if source is not None else None,G(q).data(),frame]


def gate_add(i,j,q,frame):return scalar("add",("L",i),("L",j),q,frame)
def gate_scale(i,q,frame):return scalar("scale",("L",i),q=q,frame=frame)


def reverse_gate(e,transpose=False,inverse=False,frame=None):
    _,op,target,source,q,f=e;q=G.read(q)
    if op=="add":
        if inverse:q=-q
        if transpose:target,source=source,target
    else:
        assert op=="scale"
        if inverse:q=G(1)/q
    return scalar(op,target,source,q,f if frame is None else frame)


def inverse(events,frame):return [reverse_gate(e,inverse=True,frame=frame) for e in reversed(events)]
def invtranspose(events,frame):return [reverse_gate(e,transpose=True,inverse=True,frame=frame) for e in events]
def transpose(events,frame):return [reverse_gate(e,transpose=True,frame=frame) for e in reversed(events)]


def normalization(H):
    """Construct B with H B=[4I on SX,8iI on TX], by invertible gates."""
    basis=[[H[i].get(h,F()) for h in SX] for i in range(8)]
    rowops=[]
    def plus(i,j,q):
        nonlocal basis
        basis[i]=[a+q*b for a,b in zip(basis[i],basis[j])]
        rowops.append(gate_add(SX[i],SX[j],G(q),0))
    def scale(i,q):
        basis[i]=[q*a for a in basis[i]]
        rowops.append(gate_scale(SX[i],G(q),0))
    for col in range(8):
        p=next(i for i in range(col,8) if basis[i][col])
        if p!=col:
            plus(col,p,F(1));plus(p,col,F(-1));plus(col,p,F(1));scale(p,F(-1))
        q=1/basis[col][col];scale(col,q)
        for i in range(8):
            if i!=col and basis[i][col]:plus(i,col,-basis[i][col])
    assert basis==[[F(i==j) for j in range(8)] for i in range(8)]
    result=[gate_scale(h,G(4),0) for h in SX]
    for i,row in enumerate(H):
        for h,a in sorted(row.items()):
            if h not in SX:result.append(gate_add(SX[i],h,G(-a),0))
        result.append(gate_add(SX[i],TX[i],G(0,8),0))
    result+=rowops
    return result


def apply_gate(state,event):
    if event[0]=="gaussian_scalar":
        _,op,t,s,q,_=event;t=tuple(t);q=G.read(q)
        if op=="clear":state[t]={}
        elif op=="scale":state[t]={k:a*q for k,a in state[t].items() if a*q}
        else:
            assert op=="add";add(state.setdefault(t,{}),state[tuple(s)],q)
    else:
        gate=event[1];op,t=gate[0],tuple(gate[1])
        if op=="clear":state[t]={}
        elif op=="copy":state[t]=state[tuple(gate[2])].copy()
        elif op=="scale":
            q=G(F(gate[2],gate[3]));state[t]={k:a*q for k,a in state[t].items() if a*q}
        else:
            assert op=="add";add(state.setdefault(t,{}),state[tuple(gate[2])],G(F(gate[3],gate[4])))


def replay(events,n=632):
    state={("L",r):{(r,()):G(1)} for r in range(n)}
    peak=F(1);norms={("L",r):F(1) for r in range(n)}
    for index,e in enumerate(events):
        tag=e[0]
        if tag in ("scalar","gaussian_scalar"):
            apply_gate(state,e)
            if tag=="gaussian_scalar":
                _,op,t,s,q,_=e;t=tuple(t);q=G.read(q)
            else:
                g=e[1];op,t=g[0],tuple(g[1]);s=g[2] if op in ("add","copy") else None
                q=G(F(g[3],g[4])) if op=="add" else G(F(g[2],g[3])) if op=="scale" else G(1)
            if op=="clear":norms[t]=F()
            elif op=="copy":norms[t]=norms[tuple(s)]
            elif op=="scale":norms[t]*=q.norm()
            else:
                # Include the integer numerator accumulator before dyadic
                # division, as in the retained scalar triangle certificate.
                peak=max(peak,(abs(q.r.numerator)+abs(q.i.numerator))*norms[tuple(s)])
                norms[t]=norms.get(t,F())+q.norm()*norms[tuple(s)]
            peak=max(peak,norms[t])
        elif tag=="warp":
            t=tuple(e[1]);op=e[2];row={}
            for (j,w),a in state[t].items():
                key=(j,w[1:] if w and w[0]==-op else (op,)+w)
                add(row,{key:a})
            state[t]=row
        elif tag=="zero_buffer":
            t=("Z",e[2])
            if e[1]=="alloc":state[t]={};norms[t]=F()
            else:assert not state[t],("dirty owned buffer",index)
        else:assert tag in ("phase","climb","adapter","residual_adapter")
    bits=peak.numerator.bit_length()-peak.denominator.bit_length()
    if F(2)**bits<peak:bits+=1
    return state,bits


def matrix(rows,cols):
    return [{j:G(row.get(j,0)) for j in cols if row.get(j,0)} for row in rows]


def product(left,right):
    out=[]
    for row in left:
        r={}
        for j,a in row.items():add(r,right[j],a)
        out.append(r)
    return out


def postcode(Qrows,bank,frame):
    out=[]
    for row in Qrows:
        out.append(scalar("clear",("C",0),frame=frame))
        for j,a in sorted(row.items()):out.append(scalar("add",("C",0),("L",bank[j]),a,frame))
        for j,a in sorted(row.items()):out.append(scalar("add",("L",bank[j]),("C",0),-a/G(4),frame))
        out.append(scalar("clear",("C",0),frame=0))
    return out


def boundary_check(events,eligible,phase):
    allowed=({*range(112,224),*eligible} if phase==0 else {*range(112),*eligible})
    dirty=False
    for e in events:
        assert e[0]=="gaussian_scalar"
        _,op,t,s,q,f=e
        assert f==phase or op=="clear"
        for reg in (t,s):
            if reg is None:continue
            assert reg[0]=="C" and reg[1]==0 or reg[0]=="L" and reg[1] in allowed
        if t[0]=="C":dirty=op!="clear"
        for a in (G.read(q).r,G.read(q).i):
            assert not a or a.denominator&(a.denominator-1)==0
    assert not dirty


def gaussian_bill(events,component):
    original=[e for e in events if e[0]=="scalar"]
    total=component.scalar_bill(original)["real_primitives"]
    macros=Counter();i_rotations=0
    for e in events:
        if e[0]!="gaussian_scalar":continue
        _,op,t,s,q,f=e;q=G.read(q);macros[op]+=1
        if op=="clear":total+=2;continue
        if op=="scale":
            assert not q.i
            a,b=abs(q.r.numerator),q.r.denominator
            assert a and a&(a-1)==0 and b&(b-1)==0
            total+=2*(abs(a.bit_length()-b.bit_length())+int(q.r<0))
            continue
        assert op=="add"
        # Two real-coordinate additions for each real/imaginary component.
        # The imaginary source is a swapped coordinate pair, with one sign.
        for a in (q.r,q.i):
            if a:
                p,d=abs(a.numerator),a.denominator
                total+=2*(3+p.bit_length()-1+p.bit_count()+d.bit_length()-1)
        if q.i:total+=2;i_rotations+=1
    return {"real_primitives_upper":total,"new_gaussian_macros":dict(macros),
            "imaginary_additions":i_rotations,
            "lowering":"(a+ib)(u+iv)=(au-bv)+i(bu+av); independent real dyadic additions, swapped source coordinates and sign; no recursive native child"}


def main():
    if not __debug__:
        raise RuntimeError("Assertions must be enabled")
    if sha256(COMPONENT.read_bytes()).hexdigest()!=COMPONENT_SHA:
        raise ValueError("Reviewed modern component source pin")
    c=module("modern_component_for_extended_source",COMPONENT)
    c.need(c.digest(INPUTS/"NATIVE-RECEIPT.json")==c.NATIVE_RECEIPT_SHA,"PR3734 native receipt pin")
    receipt=c.read(INPUTS/"NATIVE-RECEIPT.json")
    out={"status":"PASS_FINITE_SYMMETRIC_128_PORT_COMPONENT",
         "script_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
         "component_source_sha256":sha256(COMPONENT.read_bytes()).hexdigest(),
         "claim_scope":"Finite local Gaussian-dyadic component only; zero-label extra ports require a new global geometry and physical allocation",
         "providers":{}}
    dest=HERE/"symmetric-extended-results";dest.mkdir(exist_ok=True)
    for name,item in receipt["providers"].items():
        loc=INPUTS/"native-cache"/item["word_sha256"] / "local"
        for basename in ("CANONICAL-WORD.json.gz","LOCAL-PROGRAMS.json.gz","CLIFFORD-RECIPES.json","RESIDUAL-ADAPTERS.json"):
            c.need(c.digest(loc/basename)==item["complete_native_files"]["local/"+basename],"PR3734 native cache pin "+basename)
        w=c.read(loc/"CANONICAL-WORD.json.gz");programs=c.read(loc/"LOCAL-PROGRAMS.json.gz")
        R,K,P,J,_,_=c.clean_reconstruction(w,programs)
        before=c.replay(programs["forward"][:programs["forward"].index(["phase","centers"])])
        H=[{j:a for (j,ws),a in before["L",p].items() if j>=224 and not ws} for p in w["centers"]]
        eligible=[h for h in range(224,632) if w["start"][h]==0 and w["final"][h]==1]
        assert len(eligible)==213
        used=set(SX)|set(TX)
        HY=tuple(h for h in eligible if h not in used)[:16]
        X=tuple(range(112))+SX+TX;Y=tuple(range(112,224))+HY
        assert len(X)==len(Y)==128 and len(set(X)|set(Y))==256
        b=normalization(H)
        bs,_=replay(b)
        hb=[]
        for row in H:
            image={}
            for h,a in row.items():add(image,bs["L",h],G(a))
            hb.append(image)
        assert hb==[{(SX[i],()):G(4),(TX[i],()):G(0,8)} for i in range(8)]
        invb=inverse(b,1)
        ident,_=replay(b+invb)
        assert all(ident["L",i]=={(i,()):G(1)} for i in range(632))
        qr=[]
        for i,row in enumerate(R):
            qr.append({**{j:G(a) for j,a in row.items()},112+i:G(4),120+i:G(0,8)})
        qt=[{i:row[p] for i,row in enumerate(qr) if p in row} for p in range(128)]
        assert product(qr,qt)==[{i:G(8)} for i in range(8)]
        D=product(qt,qr)
        D=[{j:-a/G(4) for j,a in row.items()} for row in D]
        for i,row in enumerate(D):add(row,{i:G(1)})
        assert product(D,D)==[{i:G(1)} for i in range(128)]
        assert all(D[i].get(j,G())==D[j].get(i,G()) for i in range(128) for j in range(128))
        for p in range(112):
            assert {j:a for j,a in D[p].items() if j<112}=={j:G(a) for j,a in J[p].items()}
        fcode=postcode(qr,X,1);bcode=postcode(qr,Y,0)
        finject=[gate_add(HY[i],X[112+i],G(1),1) for i in range(16)]
        binject=[]
        for i,row in enumerate(D):
            for j,a in row.items():
                if j>=112:binject.append(gate_add(X[i],Y[j],-a,1))
        boundary_check(b,eligible,0);boundary_check(invb,eligible,1)
        boundary_check(fcode+finject,eligible,1);boundary_check(bcode,eligible,0)
        boundary_check(binject,eligible,1)
        changed={};checks={}
        for orientation in ("forward","backward"):
            core=programs[orientation];a=core.index(["phase","centers"]);z=core.index(["phase","B"])
            core=core[:a]+[["phase","centers"]]+core[z:]
            profile=c.core_frame_check(w,core)
            assert profile==Counter({1:2440,2:725,3:224,4:102,5:20})
            if orientation=="forward":events=b+core+invb+fcode+finject
            else:
                pre=invtranspose(b,0);post=transpose(b,1)
                boundary_check(pre,eligible,0);boundary_check(post,eligible,1)
                events=bcode+pre+core+post+binject
            state,bits=replay(events)
            assert all(not row for reg,row in state.items() if reg[0] in ("C","Z"))
            for i in range(632):
                expected={(i,()):G(1)}
                if i in X:
                    p=X.index(i)
                    if orientation=="forward":expected={(X[j],()):a for j,a in D[p].items()}
                    else:add(expected,{(Y[p],()):G(-1)})
                elif i in Y:
                    p=Y.index(i)
                    if orientation=="forward":add(expected,{(X[j],()):a for j,a in D[p].items()})
                    else:expected={(Y[j],()):a for j,a in D[p].items()}
                assert state["L",i]==expected,(name,orientation,i)
            changed[orientation]=events
            checks[orientation]={"input_columns":632,"extended_source":128,"extended_target":128,
                "arbitrary_helpers_restored":376,"owned_zero_buffers":91,"rank_mass":5070,
                "profile":dict(sorted(profile.items())),"scalar_invoice":gaussian_bill(events,c),
                "scalar_prefix_ceiling_log2":bits,"retained_scalar_cap_192_satisfied":bits<=192}
            print("PASS_SYMMETRIC_EXTENDED",name,orientation,"columns632 data256 helpers376 rank5070 prefixbits",bits,flush=True)
        payload=json.dumps(changed,sort_keys=True,separators=(",",":")).encode()
        (dest/f"PROGRAMS-{name}.json.gz").write_bytes(gzip.compress(payload,mtime=0))
        out["providers"][name]={"borrow_word_sha256":item["word_sha256"],"payload_sha256":sha256(payload).hexdigest(),
            "source_helper_ports":list(SX+TX),"target_helper_ports":list(HY),"H_support":len({h for row in H for h in row}),
            "normalization_gates":len(b),"normalization_is_invertible_dyadic":True,
            "Q_Q_transpose":"8 I","D_symmetric":True,"D_squared":"I","checks":checks,
            "extra_port_labels":[0]*16,"extra_port_start_rank":0,"extra_port_final_source_rank":9,
            "extra_port_final_target_rank":9,
            "native_scope":"All retained core native operations reused; newly added Gaussian scalar gates are only at literal common I or FULL frames"}
    (dest/"RESULT.json").write_text(json.dumps(out,indent=2)+"\n")
    print(out["status"],flush=True)


if __name__=="__main__":main()
