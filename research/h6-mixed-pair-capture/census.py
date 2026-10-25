"""Complete reduced-geometry census, not a 30960-square matrix replay."""
from collections import Counter
from hashlib import sha256
import json
from fractions import Fraction as F
from e8_exact import dot,need
from pair_factor import mixed_block,rank,factor_columns,product,invoice


def digest(data):
    return sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()


def compute(roots,pure,root_sig,buckets):
    root_rows=[];root_pairings=Counter()
    for u in roots:
        row=[dot(u,v)//4 for v in roots]
        need(all(dot(u,v)%4==0 for v in roots),'integral complete root table')
        c=Counter(abs(v) for v in row)
        need(c=={0:63,1:56,2:1},'every root association degree')
        root_rows.append(row);root_pairings.update(row)
    pure_compat=[]
    for u in roots:
        number=0
        for members in buckets.values():
            values=[dot(u,pure[i])//4 for i in members]
            need(all(dot(u,pure[i])%4==0 for i in members),'integral complete root/pure table')
            need(len({v%2 for v in values})==1,'whole pure fiber has one compatibility parity')
            if values[0]%2:
                need(all(abs(v)==1 for v in values),'compatible pure targets have only unit pairing')
                number+=1
        need(number==72,'every root has72 compatible pure-label buckets')
        pure_compat.append(number)
    pure_rows=[];pure_label_degrees=[];pure_root_degrees=[]
    representatives=[pure[m[0]] for m in buckets.values()]
    for v in pure:
        row=Counter(abs(dot(v,w)//4) for w in pure)
        need(all(dot(v,w)%4==0 for w in pure),'integral complete pure table')
        need(row[1]==448 and row[3]==64 and row[4]==1,'every pure source has512 edges,64 of magnitude5/16')
        pure_rows.append(dict(sorted(row.items())))
        degree=sum((dot(v,w)//4)&1 for w in representatives)
        need(degree==64,'pure target-label degree')
        root_degree=sum((dot(v,w)//4)&1 for w in roots)
        need(root_degree==64,'pure-to-root label degree')
        pure_label_degrees.append(degree);pure_root_degrees.append(root_degree)
    classes=[]
    for A in (-1,0,1,2):
        for B in (-1,0,1,2):
            matrix=mixed_block(A,B)
            r=rank(matrix)
            sigma=(1 if B==0 and A%2 else -1 if A==0 and B%2 else None)
            if not r:need((A+B)%2==0,'zero mixed block is incompatible')
            elif sigma is not None:need(r==1,'signed capture has rank1')
            else:
                need(r==2 and (A==2 or B==2) and (A+B)%2==1,'full-rank mixed exception')
                need(abs(matrix[0][0]*matrix[1][1]-matrix[0][1]*matrix[1][0])==F(3,32),'full-rank exception determinant')
            G,D=factor_columns(matrix,sigma)
            need(product(D,G)==matrix,'every attainable two-by-two factor identity')
            classes.append({'A':A,'B':B,'rank':r,'sigma':sigma,'C':[[str(c) for c in row] for row in matrix]})
    # Counts are products of the fully verified association degrees above.
    mixed_caps=2*64*56
    pure_caps=2*72
    R_mixed=120**2*2*(mixed_caps+pure_caps)
    R_pure=2*135*8*(120*64+64)
    E_mm=120**2*mixed_caps*4
    E_mp=120**2*pure_caps*16
    E_pp=2*1080*(448+64)
    E5_mm=120**2*(2*56)*2
    E5_pp=2*1080*64
    need(R_mixed+R_pure==227312640,'independently reconstructed baseline helper count')
    need(E_mm+2*E_mp+E_pp==480337920 and E5_mm+E5_pp==3363840,'independently reconstructed complete coefficient census')
    bill=invoice()
    need(bill['capture_entries_old_and_new']==R_mixed+R_pure,'new capture entries are not helper count')
    return {'root_lines':120,'pure_lines_per_block':1080,'pure_labels_per_block':135,'pure_label_multiplicity':8,
            'full_E8_cosets':256,'H6_ports':30960,'mixed_labels':14400,'all_labels':14670,
            'root_pair_table_entries':120**2,'root_pure_table_entries':120*1080,'pure_pair_table_entries':1080**2,
            'root_points_sha256':digest(roots),'pure_points_sha256':digest(pure),
            'root_pair_table_sha256':digest(root_rows),'pure_pair_count_rows_sha256':digest(pure_rows),
            'root_signature_sha256':digest(root_sig),'pure_fibers_sha256':digest(list(buckets.values())),
            'pure_fiber_partition_sha256':digest(sorted(sorted(v) for v in buckets.values())),
            'mixed_cap_degree':mixed_caps,'pure_cap_degree_from_mixed':pure_caps,
            'rank1_mixed_caps_per_mixed_source_label':2*63*56,
            'rank2_mixed_caps_per_mixed_source_label':2*56,
            'new_helpers_per_mixed_source_label':2*63*56+2*2*56+2*72,
            'mixed_block_classes':classes,
            'baseline_helper_parts':{'mixed_source':R_mixed,'pure_source':R_pure},
            'baseline_scatter_parts':{'mixed_mixed':E_mm,'mixed_pure_each_orientation':E_mp,'pure_pure':E_pp},
            'baseline_abs5_over16_parts':{'mixed_mixed':E5_mm,'pure_pure':E5_pp},
            'invoice':bill}
