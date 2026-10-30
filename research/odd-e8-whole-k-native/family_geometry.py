from pathlib import Path
from itertools import product
from fractions import Fraction as F
from hashlib import sha256
from collections import Counter
from decimal import Decimal,localcontext
import argparse,json

HERE=Path(__file__).resolve().parent
INPUT=HERE/'inputs/NORMALIZERS.json'
PIN='ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def basis(rows):
    piv={}
    for x in rows:
        while x:
            k=x.bit_length()-1
            if k in piv:x^=piv[k]
            else:piv[k]=x;break
    return list(piv.values())
def dot(x,y):return (x&y).bit_count()&1
def pairing(A,B):return len(basis(sum(dot(a,b)<<j for j,b in enumerate(B)) for a in A))
def member(B,x):return len(basis(B+[x]))==len(B)
raw=INPUT.read_bytes();need(sha256(raw).hexdigest()==PIN,'normalizer bytes')
d=json.loads(raw);roots=list(zip(*d['mode_columns']));q=[x['q'] for x in d['ports']]
groups={}
for i,r in enumerate(roots):groups.setdefault(tuple(j for j,c in enumerate(r) if c),[]).append(i)
groups=sorted(groups.items());need(len(groups)==14 and all(len(g)==8 for _,g in groups),'14 cubes')
cubes=[];base_nonzero=0
for tetrad,ports in groups:
    parity=[]
    for i in ports:
        root=roots[i];sign=root[tetrad[0]]
        parity.append(sum(root[j]*sign<0 for j in tetrad[1:])%2)
    K=[[F(i==j)-F(sum(a*b for a,b in zip(roots[ports[i]],roots[ports[j]])),4) for j in range(8)] for i in range(8)]
    need(all(sum(K[i][j]*K[j][k] for j in range(8))==F(i==k) for i,k in product(range(8),repeat=2)),'base involution')
    need(all(sum(bool(x) for x in row)==4 and all(not x or abs(x)==F(1,2) for x in row) for row in K),'four dyadic neighbors')
    need(all(not K[i][j] or parity[i]!=parity[j] for i,j in product(range(8),repeat=2)),'base cross parity')
    B=[basis(q[ports[i]] for i in range(8) if parity[i]==p) for p in (0,1)]
    need(all(len(b)==3 and pairing(b,b)==1 for b in B) and pairing(B[0],B[1])==0,'base degenerate 3-space geometry')
    cubes.append({'ports':ports,'parity':parity,'K':K})
    base_nonzero+=sum(bool(x) for row in K for x in row)
U=[1|(1<<9)|(1<<18)]+[(1<<(9*b))^(1<<(9*b+j)) for b in range(3) for j in range(1,9)]
need(len(basis(U))==pairing(U,U)==25,'nondegenerate U25')
classes=Counter();ports_seen=0;representatives=[];basis_pairings=0
for cube_tuple in product(range(14),repeat=3):
    local=[cubes[i] for i in cube_tuple];Q=[[],[]]
    for a,b,c in product(range(8),repeat=3):
        p=(local[0]['parity'][a]+local[1]['parity'][b]+local[2]['parity'][c])%2
        label=q[local[0]['ports'][a]]|(q[local[1]['ports'][b]]<<9)|(q[local[2]['ports'][c]]<<18)
        need(dot(label,label)==1 and label!=(1<<27)-1,'odd nonambient-characteristic port')
        Q[p].append(label)
    B=[basis(x) for x in Q]
    need(len(Q[0])==len(Q[1])==256 and len(B[0])==len(B[1])==9,'product parity class size/span')
    need(pairing(B[0],B[1])==0 and pairing(B[0],B[0])==pairing(B[1],B[1])==1,'product orthogonality/radical')
    need(len(basis(B[0]+B[1]))==10,'product cube joint span')
    # All generators of every class are actual q in U25; the basis pairing
    # certifies orthogonality of all256^2 source/reader pairs, not samples.
    for p in (0,1):
        need(all(dot(label,v)==0 for label in Q[1-p] for v in B[p]),'source9 subset every opposite reader hyperplane')
    classes[(9,1,8,256)]+=2;ports_seen+=512;basis_pairings+=len(B[0])*len(B[1])
    if not representatives:representatives.append({'cube_tuple':cube_tuple,'source_class0_basis27':B[0],'source_class1_basis27':B[1]})
need(ports_seen==112**3,'whole port partition')
# The eight scalar eigenvalues certify the polynomial involution under Ki^2=I.
need(all(((a+b+c-a*b*c)/2)**2==1 for a,b,c in product((-1,1),repeat=3)),'odd-majority involution polynomial')
# One literal512-port K matrix: every row has12 single-factor and64
# three-factor entries, all cross parity. Different terms have disjoint supports.
K0=cubes[0]['K'];p0=cubes[0]['parity'];nonzero=0;first_row=[]
for a,b,c in product(range(8),repeat=3):
    row={}
    src=(a,b,c)
    for axis in range(3):
        for j in range(8):
            if K0[src[axis]][j]:
                dst=list(src);dst[axis]=j;key=tuple(dst)
                row[key]=row.get(key,F(0))+K0[src[axis]][j]/2
    for j,k,l in product(range(8),repeat=3):
        coeff=-K0[a][j]*K0[b][k]*K0[c][l]/2
        if coeff:row[(j,k,l)]=row.get((j,k,l),F(0))+coeff
    row={key:value for key,value in row.items() if value}
    need(len(row)==76,'product row degree')
    need(Counter(abs(x) for x in row.values())=={F(1,4):12,F(1,16):64},'product row coefficient profile')
    parity=(p0[a]+p0[b]+p0[c])%2
    need(all((p0[j]+p0[k]+p0[l])%2!=parity for j,k,l in row),'product K cross parity')
    nonzero+=len(row)
    if not first_row:first_row=[[list(t),z.numerator,z.denominator] for t,z in sorted(row.items())]
v=112**3
with localcontext() as c:
    c.prec=70;a=Decimal('0.003027288235');sigma=1-a
    power=lambda r:(Decimal(r).ln()*sigma).exp()
    saving=(10+power(8)+2*power(15))-(power(8)+power(9)+power(15)+power(16))
receipt={'status':'PASS_GLOBAL_K_ONLY_SCALAR_COMMON_FRAME','normalizer_sha256':PIN,'base_cubes':14,'product_cubes':2744,'ports':v,'main_fields':2*v,'source_reader_classes':5488,'class_contract_histogram':{str(k):n for k,n in classes.items()},'all_literal_ports_checked':ports_seen,'cross_class_basis_pairings_checked':basis_pairings,'all_reader_against_source_basis_checks':2744*2*256*9,'common_frames_degenerate':True,'common_frame_dimension':9,'common_frame_restricted_pairing_rank':1,'common_frame_radical_dimension':8,'opposite_classes_orthogonal':True,'all_source_q_odd_nonambient_characteristic':True,'source_q_is_a_restricted_characteristic_representative':True,'source_entry_contains_q':True,'reader_q_perp_contains_source_frame':True,'paid_per_port':{'8':1,'9':1,'15':1,'16':1},'whole_paid_profile':{str(r):v for r in (8,9,15,16)},'paid_rank_mass':48*v,'ordinary_scalar_ADD_per_port':76,'ordinary_scalar_ADD_whole':76*v,'owned_scratch_required':0,'helpers_required':0,'COPY_required':0,'ordinary_restore_required':0,'reader_arbitrary_old_input_retained':True,'source_logical_contents_preserved':True,'direct_word_schema':['for each product cube and source parity p:','source X[p]: own_line -> S9[p], H8','reader Y[1-p]: ground -> S9[p], H9','for each nonzero K[r,s]: Y[r] += K[r,s] X[s] at exactly S9[p]','source X[p]: S9[p] -> R25, H16','reader Y[1-p]: S9[p] -> own_q_perp, H15'],'K_eigenvalue_polynomial_assignments_checked':8,'literal_representative_K_nonzeros_checked':nonzero,'literal_representative_first_K_row':first_row,'representative_geometry':representatives,'display_main_moment_saving_per_port_vs_old_planning_at_selected_a':str(saving),'limits':['Only the whole block-diagonal K_odd native scalar interface is settled here; no H side blocks or F3 decoding compatibility is claimed.','The four native ranks follow from nested canonical-frame flags, including degenerateS9; this geometry audit does not duplicate the separate native phase compiler.','The original q is not the characteristic of ambient U25. In the degenerateS9 restricted form, every odd q represents the characteristic functional; no noncharacteristic-inside-S9 condition is needed or true.','The K-only endpoint is source R25 x and reader Phi_(qperp)(y+Kx), with supplied source line entrances. This is not already the identity-transfer or a complete global caller.','Ordinary arithmetic, all wrappers, precision, storage and compiler costs must be carried by the eventual full caller.']}
ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
if args.write:(HERE/'FAMILY.json').write_text(json.dumps(receipt,indent=2)+'\n')
else:need(json.loads((HERE/'FAMILY.json').read_bytes())==json.loads(json.dumps(receipt)),'frozen read-only global family receipt')
print(json.dumps({k:receipt[k] for k in ['status','product_cubes','ports','common_frame_dimension','common_frame_restricted_pairing_rank','paid_per_port','paid_rank_mass','ordinary_scalar_ADD_whole','helpers_required','COPY_required','display_main_moment_saving_per_port_vs_old_planning_at_selected_a']}))
