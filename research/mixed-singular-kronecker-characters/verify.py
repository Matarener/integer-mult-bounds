"""Verify mixed singular characters against literal equations and witnesses."""
from itertools import product,permutations
from math import gcd
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import mixed as M
import oracle as O
R=Path(__file__).resolve().parent


def dot(a,b,f):
    v=0
    for x,y in zip(a,b):v=f.add(v,f.mul(x,y))
    return v


def single(side,e):
    m,n=e+(side=='L'),e+(side=='R');a=[[0]*n for _ in range(m)];b=[[0]*n for _ in range(m)]
    for i in range(e):
        a[i][i]=1
        if side=='R':b[i][i+1]=1
        else:b[i+1][i]=1
    return (a,b),(m,n)


def hom_checks():
    counts=[]
    for q in (2,3,4,5):
        f=M.Field(q);cases=dimension=0
        for src,dst in product(product(('R','L'),range(4)),repeat=2):
            a,ad=single(*src);b,bd=single(*dst);equations,width=O.equations(a,b,ad,bd,f)
            literal=O.nullspace(equations,width,f)
            proposed=[[x for row in u+c for x in row]for u,c in M.hom_single(src,dst)]
            M.need(all(len(v)==width for v in proposed),'Complete zero-index Hom shapes')
            M.need(all(dot(row,v,f)==0 for row in equations for v in proposed),'Every explicit off-diagonal intertwiner')
            M.need(len(literal)==len(proposed)==width-len(O.nullspace(proposed,width,f)),'Complete Hom basis and linear independence')
            cases+=1;dimension+=len(literal)
        counts.append(dict(field=q,ordered_pairs=cases,total_Hom_dimension=dimension))
    return counts


DOMAINS=[
 (2,[('R',1,1),('R',2,1)],True),
 (3,[('R',1,1),('R',2,1)],True),
 (4,[('R',1,1),('L',1,1)],True),
 (3,[('R',0,1),('R',2,1)],False),
 (3,[('L',0,1),('L',2,1)],False),
 (5,[('R',1,1),('L',2,1)],False),
 (3,[('R',1,2),('L',0,1)],False),
 (2,[('R',0,2),('L',0,2)],True),
 (4,[('R',2,1),('R',4,1)],False),
 (3,[('R',1,1),('R',3,1)],False),
 (3,[('L',1,1),('L',3,1)],False),
 (2,[('R',0,1),('R',1,1),('L',0,1),('L',1,1)],True),
]


def oracle_checks():
    reports=[]
    for q,model,all_actions in DOMAINS:
        f=M.Field(q);a,b=M.slices(model);m,n=len(a),len(a[0]);data=M.character_data(model)
        basis=M.fixed_slice_basis(model);equations,width=O.equations((a,b),(a,b),(m,n),(m,n),f)
        literal=O.nullspace(equations,width,f)
        M.need(len(literal)==len(basis)==width-len(O.nullspace(basis,width,f)),'Complete mixed fixed-slice dimension')
        M.need(all(dot(row,v,f)==0 for row in equations for v in basis),'All mixed Hom coefficients satisfy literal equations')
        actions=list(M.old.general_linear_two(f)) if all_actions else [[[z,0],[0,1]]for z in range(1,q)]
        image=set();accepted=0;tested=0
        for action in actions:
            kernel=O.stabilizer_space(a,b,action,f);M.need(len(kernel)==len(literal),'Every slice action has full expected dimension')
            pairs,count=O.enumerate_space(kernel,m,n,f);z=O.determinant(action,f)
            image.update((x,y,z)for x,y in pairs);accepted+=count;tested+=q**len(kernel)
        predicted={triple for triple in product(range(1,q),repeat=3)if M.accepts(model,triple,f)}
        M.need(image==predicted,'Literal full mixed determinant image')
        index=(q-1)**3//len(image);M.need(index==gcd(q-1,data['power_index']),'Exact finite-field orbit count')
        reports.append(dict(field=q,model=model,dimensions=[m,n],endomorphism_dimension=len(literal),slice_actions=len(actions),
                            all_slice_actions=all_actions,linear_solutions_tested=tested,stabilizers=accepted,
                            determinant_image=sorted(image),special_linear_orbits=index))
        print('PASS_LITERAL_DOMAIN',q,model,flush=True)
    return reports


def witness_checks():
    reports=[];all_models=[(q,model)for q,model,_ in DOMAINS]
    all_models += [(5,[('R',1,2),('L',2,1)]),(4,[('R',0,1),('L',3,1)]),(3,[('L',2,3)]),(5,[('R',4,1),('R',5,1)]),(3,[('R',1,2),('R',2,2)]),(5,[('R',1,1),('L',1,1)]),(5,[('R',1,1),('R',3,1),('L',1,1)])]
    for q,model in all_models:
        f=M.Field(q);a,b=M.slices(model);yes=no=0
        for triple in product(range(1,q),repeat=3):
            if M.accepts(model,triple,f):
                M.witness(model,triple,f)
                maps=[M.old.identity(len(a)),M.old.identity(len(a[0])),M.old.identity(2)]
                for matrix,value in zip(maps,triple):
                    matrix[0][0]=value
                    if len(matrix)>1:matrix[0][1]=1
                M.correct_given_map(model,maps,f);yes+=1
            else:
                try:M.witness(model,triple,f)
                except ValueError:no+=1
                else:raise ValueError('Excluded determinant triple accepted')
        data=M.character_data(model);lifts=0
        for action in M.old.general_linear_two(f):
            # Both constant and nonconstant type determinants are tested.
            for choice in (0,1):
                scalars=[1+(choice+i)%(q-1) for i in range(len(data['types']))]
                w=M.lift(model,action,scalars,f)
                M.need(M.old.fixes(a,b,w,f),'Every GL2 literal mixed lift')
                triple=tuple(M.old.determinant(x,f)for x in w)
                M.need(M.accepts(model,triple,f),'Every lift has the stated character')
                # The converse also permits the same prescribed non-diagonal action.
                M.witness(model,triple,f,action);lifts+=1
        reports.append(dict(field=q,model=model,accepted_triples=yes,excluded_triples=no,special_linear_corrections=yes,lifts=lifts,
                            power_index=data['power_index'],character_exponents=list(data['ell'])+[data['character_slice_exponent']]))
    return reports


def controls():
    f=M.Field(5);model=[('R',1,1),('L',2,1)];data=M.character_data(model);a,b=M.slices(model)
    wrong_shift=[]
    for triple in product(range(1,5),repeat=3):
        x,y,z=triple;wrong=f.mul(f.power(x,data['ell'][0]),f.power(y,data['ell'][1]))
        if (wrong==1)!=M.accepts(model,triple,f):wrong_shift.append(triple)
    M.need(wrong_shift,'Slice determinant cannot be omitted')
    noncommuting=[[1,1],[0,1]];w=M.lift(model,noncommuting,[2,3],f)
    M.need(not M.old.fixes(a,b,(w[0],M.old.transpose(w[1]),w[2]),f),'Missing Q transpose control')
    M.need(not M.old.fixes(a,b,(w[0],w[1],M.old.transpose(w[2])),f),'Slice action orientation control')
    M.need(len(M.fixed_slice_basis([('R',1,1),('R',2,1)]))==4,'Unequal right indices have off-diagonal mixing')
    M.need(len(M.fixed_slice_basis([('R',1,1),('L',1,1)]))==4,'Left-to-right mixing is present')
    M.need(not M.hom_single(('R',1),('L',1)),'Forbidden reverse cross-orientation map')
    M.need(M.character_data([('R',1,2),('R',2,2)])['power_index']==1,'Multiplicity does not multiply the index lattice')
    M.need(M.character_data([('R',1,1),('L',1,1)])['power_index']==3,'Cross-orientation uses e+f+1')
    rejected=[]
    for name,model in [('empty',[]),('unknown_side',[('Z',1,1)]),('negative_index',[('R',-1,1)]),('zero_multiplicity',[('R',1,0)]),('zero_rows',[('R',0,1)]),('zero_columns',[('L',0,1)]),('too_large_index',[('R',6,1)]),('noninteger_index',[('R',True,1)]),('combined_multiplicity',[('R',1,2),('R',1,2)])]:
        try:M.types(model)
        except ValueError:rejected.append(name)
        else:raise ValueError('Invalid model accepted '+name)
    for name,triple in [('zero_determinant',(0,1,1)),('outside_field',(5,1,1)),('wrong_arity',(1,1))]:
        try:M.accepts([('R',1,1)],triple,f)
        except ValueError:rejected.append(name)
        else:raise ValueError('Invalid triple accepted '+name)
    # Compare elimination with Leibniz on every matrix in the stated tiny domains.
    determinant_cases=0
    for q,n in [(2,3),(3,2),(4,2),(5,2)]:
        ff=M.Field(q)
        for values in product(range(q),repeat=n*n):
            matrix=[list(values[i*n:(i+1)*n])for i in range(n)];value=0
            for perm in permutations(range(n)):
                term=1
                for i,j in enumerate(perm):term=ff.mul(term,matrix[i][j])
                if sum(perm[i]>perm[j]for i in range(n)for j in range(i+1,n))%2:term=ff.neg(term)
                value=ff.add(value,term)
            M.need(value==O.determinant(matrix,ff)==M.old.determinant(matrix,ff),'Independent permutation determinant')
            determinant_cases+=1
    return dict(wrong_slice_shift_triples=len(wrong_shift),mathematical_controls=['slice_shift','Q_transpose','slice_orientation','unequal_right_mixing','left_to_right_mixing','forbidden_reverse_mixing','multiplicity_index','cross_orientation_sum'],malformed_rejections=rejected,permutation_determinant_cases=determinant_cases)


def run():
    return dict(status='PASS_MIXED_SINGULAR_KRONECKER_CHARACTERS',hom_domains=hom_checks(),
                literal_oracles=oracle_checks(),constructive_witnesses=witness_checks(),controls=controls(),
                scope='All-field proof for supplied purely singular direct sums; bounded executable F2/F3/F4/F5 models. Regular factors, arbitrary extraction and physical pricing remain open.')


def main():
    result=json.loads(json.dumps(run()))
    if '--write'in sys.argv:(R/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:M.need(result==json.loads((R/'RESULT.json').read_text()),'Exact published result')
    print(result['status'],flush=True)


if __name__=='__main__':main()
