"""Residue-assisted, fully charged recovery of Gaussian convolution outputs.
Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
The Gaussian execution is Mason Hale's unchanged backend. The new modular
lane performs ONE explicitly recorded exact product of smaller packed inputs.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
from math import gcd, prod
from copy import copy
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parent


def need(ok,message):
    if not ok: raise ValueError(message)


def authenticate():
    for name,digest in json.loads((ROOT/'INPUTS.json').read_text(encoding='utf8'))['sha256'].items():
        p=(ROOT/name).resolve()
        need(p.is_relative_to(ROOT) and p.is_file(),'source path')
        need(hashlib.sha256(p.read_bytes()).hexdigest()==digest,'source hash '+name)


authenticate()
sys.path.insert(0,str(ROOT/'vendor'))
from gaussian import GaussianLine
from pipeline import tensor_transform
from intervals import ceildiv, in_disk, grid_point, cmul, inward_quantize


def residue_lane(a,b,k):
    """Exact Kronecker lane: no carry crosses a coefficient slot."""
    need(type(k) is int and k>=1 and a and b,'residue lane domain')
    need(all(type(x) is int and x>=0 for x in a+b),'nonnegative digits')
    modulus=1 << k
    overlap=min(len(a),len(b))
    guard=(overlap-1).bit_length()
    width=2*k+guard
    packed_a=sum((x%modulus) << (j*width) for j,x in enumerate(a))
    packed_b=sum((x%modulus) << (j*width) for j,x in enumerate(b))
    # The only exact multiplication of two input-dependent packed integers.
    # This is charged, not treated as a free oracle or original-input product.
    paid_product=packed_a*packed_b
    count=len(a)+len(b)-1
    residues=[((paid_product >> (j*width)) & ((1 << width)-1))%modulus for j in range(count)]
    bill={'exact_child_calls':1,'residue_bits':k,'slot_bits':width,
          'overlap':overlap,'coefficient_count':count,
          'left_child_bits':packed_a.bit_length(),'right_child_bits':packed_b.bit_length(),
          'left_child_bound':k+(len(a)-1)*width,'right_child_bound':k+(len(b)-1)*width,
          'slot_coefficient_bound':overlap*(modulus-1)**2,
          'slot_capacity':1 << width}
    need(bill['slot_coefficient_bound']<bill['slot_capacity'],'carry-free modular slots')
    return residues,bill


def lift(center,radius,residue,modulus):
    """Unique residue-class representative in a certified real interval."""
    need(type(modulus) is int and modulus>=1 and type(residue) is int and 0<=residue<modulus,'residue class')
    center,radius=F(center),F(radius)
    need(0<=radius and 2*radius<modulus,'strict residue spacing')
    low=(center-radius-residue)/modulus
    high=(center+radius-residue)/modulus
    first=ceildiv(low.numerator,low.denominator)
    last=high.numerator//high.denominator
    need(first==last,'one residue representative in interval')
    return residue+modulus*first


def seed_lines():
    lines=[GaussianLine(s,t,5) for s,t in ((5,8),(7,16),(13,32))]
    for line in lines:line.certify_operator()
    return lines


def precision_view(seeds,p):
    """Reuse unchanged prepared matrices; explicitly recheck every p-domain."""
    views=[]
    for old in seeds:
        need(type(p) is int and 100<p<=old.p and old.alpha**2<p,'precision view range')
        need(2<=old.s<old.t<(1 << p),'original resampling integer domain')
        need(old.bits>p+2*old.alpha**2+32,'working grid guard')
        need(F(old.t-old.s,old.s)>F(p,old.alpha**4),'resampling theta domain')
        need(old.operator_error is not None and old.operator_error<F(1,1 << (p+8)),'operator certificate')
        slope=2*(old.t.bit_length()+1)*(1 << old.gamma)
        # There are log2(t) butterfly levels plus two matrix extractions.
        # t.bit_length()+1 = log2(t)+2 for power-of-two t.
        line=copy(old);line.p=p
        line.uniform_error=old.uniform_error+slope*(F(1,1 << p)-F(1,1 << old.p))
        views.append(line)
    return views


def certificate(lines,digit_bits,k):
    need(lines and type(digit_bits) is int and digit_bits>0,'certificate domain')
    need(type(k) is int and 0<=k<=digit_bits,'residue precision')
    p,bits=lines[0].p,lines[0].bits
    need(all(l.p==p and l.bits==bits for l in lines),'common grid')
    shape=[l.s for l in lines];size=prod(shape)
    need(all(gcd(a,b)==1 for i,a in enumerate(shape) for b in shape[:i]),'coprime source axes')
    error=sum(l.uniform_error for l in lines)
    need(error<F(1,100) and digit_bits+2<=p,'uniform disk and exact input grid')
    scale=size*size*(1 << (2*digit_bits+4))
    radius=scale*(3*error+F(2,1 << p)+F(8,1 << bits))
    need(2*radius < (1 << k),'uniform modular-recovery precision')
    return {'precision':p,'working_bits':bits,'digit_bits':digit_bits,'residue_bits':k,
            'shape':shape,'source_scale':scale,'radius':[radius.numerator,radius.denominator],
            'maximum_input_digits':(size+1)//2}


def least_precision(seeds,digit_bits,k):
    for p in range(max(101,digit_bits+2,max(l.alpha**2+1 for l in seeds)),seeds[0].p+1):
        views=precision_view(seeds,p)
        try:cert=certificate(views,digit_bits,k)
        except ValueError:continue
        return views,cert
    raise ValueError('no certified precision in frozen range')


def multiply(left,right,lines,digit_bits=64,k=16,input_bits=None):
    """Actual Gaussian path plus the explicitly charged low-residue lane.

    The ordering, embedding, tensor calls, product rounding and carry scan
    follow Mason Hale's pipeline.py, with the integer decoder replaced by lift.
    """
    need(type(left) is int and type(right) is int and left>=0 and right>=0,'nonnegative inputs')
    uniform=certificate(lines,digit_bits,k)
    p,bits=lines[0].p,lines[0].bits;shape=tuple(l.s for l in lines);size=prod(shape)
    need(k>=1,'positive exact residue lane')
    width=max(1,left.bit_length(),right.bit_length()) if input_bits is None else input_bits
    need(type(width) is int and width>=max(1,left.bit_length(),right.bit_length()),'declared input width')
    digits=max(1,ceildiv(width,digit_bits))
    need(2*digits-1<=size,'no cyclic wrap')
    radix=1 << digit_bits
    a=[(left >> (j*digit_bits))%radix for j in range(digits)]
    b=[(right >> (j*digit_bits))%radix for j in range(digits)]
    residues,bill=residue_lane(a,b,k)
    residues += [0]*(size-len(residues))
    coordinates=list(product(*(range(s) for s in shape)))
    positions={c:i for i,c in enumerate(coordinates)}
    index=[positions[tuple(j%s for s in shape)] for j in range(size)]
    need(len(set(index))==size,'CRT address bijection')
    u=[(0,0)]*size;v=[(0,0)]*size
    for j in range(digits):
        u[index[j]]=(a[j] << (p-digit_bits-2),0)
        v[index[j]]=(b[j] << (p-digit_bits-2),0)
    fu,eu,cu=tensor_transform(u,lines)
    fv,ev,cv=tensor_transform(v,lines)
    paired=[];ep=F(0)
    for x,y in zip(fu,fv):
        z=cmul(grid_point(x,p,bits),grid_point(y,p,bits))
        rounded,local=inward_quantize(z,p)
        need(in_disk(rounded,p),'pointwise product disk')
        paired.append(rounded);ep=max(ep,local)
    result,eo,co=tensor_transform(paired,lines,opposite=True)
    scale=uniform['source_scale'];radius=scale*(eu+ev+ep+eo)
    need(radius<=F(*uniform['radius']),'actual error within uniform certificate')
    coefficients=[]
    for j,position in enumerate(index):
        real,imag=result[position]
        center=F(real*scale,1 << p)
        need(abs(F(imag*scale,1 << p))<=radius,'zero imaginary coefficient enclosed')
        value=lift(center,radius,residues[j],1 << k)
        need(0<=value<=digits*(radix-1)**2,'admissible convolution coefficient')
        coefficients.append(value)
    carry=0;output=[]
    for value in coefficients:
        carry,digit=divmod(value+carry,radix);output.append(digit)
    while carry:
        carry,digit=divmod(carry,radix);output.append(digit)
    answer=sum(value << (j*digit_bits) for j,value in enumerate(output))
    need(answer.bit_length()<=2*width,'output width')
    bill.update({'declared_input_bits':width,'strictly_smaller_child_bound':max(bill['left_child_bound'],bill['right_child_bound'])<width})
    return answer,{'precision':p,'uniform_radius':uniform['radius'],'actual_radius':[radius.numerator,radius.denominator],
                   'exact_lane':bill,'coefficients':coefficients,'gaussian_line_executions':cu+cv+co,
                   'pointwise_products':size,'source_scale':scale}
