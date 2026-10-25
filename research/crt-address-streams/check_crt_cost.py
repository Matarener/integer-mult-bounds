"""Exact exponent identities; all-size cost argument is in PROOF.md."""
from fractions import Fraction as F


def check():
    a=F(997,1000);e=F(3,1000);tau=F(332353,332929)
    beta=F(41544341,41616125);phi=F('0.99827619697')
    if beta!=1-a*(1-tau) or not a<beta<phi or a+e!=1:
        raise ValueError('complete caller exponent arithmetic')
    gaps={'beta_minus_D':str(beta-a),'Phi_minus_beta':str(phi-beta)}
    return dict(tau=str(tau),beta=str(beta),Phi=str(phi),gaps=gaps,
                multiplication_conversions=3,padding_passes=6)
