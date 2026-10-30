"""Small dense and free-word negative controls independent of source receipts."""
from fractions import Fraction as Q
import algebra as A

def main():
    x={((),7):Q(3,2)}
    y=A.plus({},x,ops=(1,2,-2,-1));A.need(y==x,'adjacent cancellation')
    z=A.plus({},x,ops=(1,2,-1,-2));A.need(z!=x,'noncommuting commutator erased')
    A.need(A.plus(x,x,Q(-1))=={},'rational cancellation')
    A.need(A.plus(x,x,Q(2))=={((),7):Q(9,2)},'aliased addition')
    A.need(A.reduce_word((2,),(-2,1))==(1,),'correction composition')
    # Rank-two witness has disjoint output supports and independent input forms.
    U=[[Q(0),Q(1,2)],[Q(1,2),Q(0)],[Q(-1),Q(0)],[Q(0),Q(-1)]]
    A.need(U[0][0]*U[1][1]-U[0][1]*U[1][0]==Q(-1,4),'rank-two minor')
    print('PASS_STAGING_ALGEBRA_CONTROLS groups=6')
if __name__=='__main__':main()
