"""Observer-only execution of the unchanged encoded old-H producer.
Reuses kumagi/PR5319 raw snapshot decoding; all arithmetic is source arithmetic.
JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import algebra as a


def run(helper):
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_axis import Axis
    import gaussian_matrix as gm
    import gaussian_window as gw
    from ring_words import Signed
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, erase_marker, sealed_constructors

    observed={}; writes=[]
    saved_lu, saved_close=gw.lu,gw.Window.close_dense

    def observed_lu(matrix):
        saved_set=gm.Matrix.set; names={}
        def observed_set(self,row,column,value):
            result=saved_set(self,row,column,value)
            if id(self) not in names:names[id(self)]='L' if not names else 'U'
            writes.append((names[id(self)],helper.tape_bytes(row.tape),
                           helper.tape_bytes(column.tape),helper.matrix_snapshot(self)))
            return result
        gm.Matrix.set=observed_set
        try:return saved_lu(matrix)
        finally:gm.Matrix.set=saved_set

    def observed_close(self):
        if self.schur is not None:
            observed['dense']={name:helper.matrix_snapshot(getattr(self,name))
                               for name in ('principal','schur','rounded_schur','lower','upper')}
        return saved_close(self)

    pool=ScratchPool(512);scope=OuterScope(pool);axis=window=None
    gw.lu,gw.Window.close_dense=observed_lu,observed_close
    try:
        with owned(*(Count.literal(v) for v in (13,14,1,1,24))) as parameters:
            with sealed_constructors(),scope.installed():
                try:
                    with no_decode():axis=Axis(*parameters,pool)
                    observed['H']=helper.matrix_snapshot(axis.matrix)
                    observed['weights']=helper.matrix_snapshot(axis.weights)
                    with owned(Signed(Count.literal(11)),Count.literal(8),
                               Signed(Count.literal(12)),Count.literal(4),Count.literal(16)) as args:
                        with no_decode():window=gw.Window(axis,*args,pool)
                        a.need(all(getattr(window,n) is None for n in
                                   ('principal','schur','rounded_schur','lower','upper')),
                               'actual Window released its dense setup')
                finally:
                    if window is not None:window.close()
                    if axis is not None:axis.close()
                    pool.empty()
    finally:
        gw.lu,gw.Window.close_dense=saved_lu,saved_close
    for tape in pool.tapes:erase_marker(tape)
    a.need(not pool.live and all(t.head==1 and all(x==4 for x in t.cells) for t in pool.tapes),
           'producer scratch and markers restored')

    H=helper.matrix(observed['H']);weights=helper.matrix(observed['weights'])
    dense={name:helper.matrix(value) for name,value in observed['dense'].items()}
    selected=list(range(Q(13*21,28).__ceil__(),Q(13*37,28).__ceil__()))
    cells=[];previous=None
    for position,j in enumerate(selected):
        key=(j//13,weights[j%13][2])
        if key!=previous:cells.append([])
        cells[-1].append(position);previous=key
    I=[i for cell in cells if len(cell)>4 for i in cell[1:-1]]
    B=[i for cell in cells for i in (cell[:1]+cell[-1:] if len(cell)>4 else cell)]
    principal=[[H[i%13][j%13] for j in selected] for i in selected]
    a.need(principal==dense['principal'],'actual principal old-H reference')
    a.need(B==[i for i in range(len(selected)) if i not in I],'natural source boundary order')
    S=a.schur(principal,I)
    a.need(S==dense['schur'],'independent Schur equals original source')
    A=a.truncate(S,24)
    a.need(A==dense['rounded_schur'] and A!=S,'actual nonzero first Schur truncation')
    a.need(a.gap(H)>=Q(1,128) and a.norm(H)<2,'fixture old-H premise check')
    a.need(a.gap(S)>=a.gap(H) and a.norm(S)<=a.norm(H),'source Schur premise propagation')
    a.need(a.gap(A)>a.gap(S)-Q(1,1<<24) and a.norm(A)<=a.norm(S),'source one-entry gap loss')
    L,U,stages=a.analyze(A,16)
    a.need((L,U)==(dense['lower'],dense['upper']),'actual exact factors versus independent Schur elimination')
    n=len(A);expected=[]
    for i in range(n):
        expected.append(('L',i,i))
        expected += [('U',i,j) for j in range(i,n)]
        expected += [('L',j,i) for j in range(i+1,n)]
    a.need(len(writes)==len(expected),'actual Doolittle write count')
    partial={key:[[Q() for j in range(n)]for i in range(n)]for key in ('L','U')}
    final={'L':L,'U':U}
    for raw,want in zip(writes,expected):
        name,row,col,snapshot=raw;got=(name,helper.count(row),helper.count(col))
        a.need(got==want,'actual Doolittle write order')
        _,i,j=want;partial[name][i][j]=final[name][i][j]
        a.need(helper.matrix(snapshot)==partial[name],'every source write state versus independent factors')
    a.need(all(not matrix[i][j] for matrix in (A,L,U) for i in range(n) for j in range(n)
               if abs(i-j)>2),'actual bandwidth support')
    wrong=a.stage_lu(S)[:2]
    a.need(wrong!=(L,U),'unrounded-S factors cannot replace actual producer')
    # A source schedule mutation is discriminated without changing source execution.
    altered=list(expected);altered[0],altered[1]=altered[1],altered[0]
    actual=[(name,helper.count(i),helper.count(j))for name,i,j,_ in writes]
    a.need(actual!=altered,'factor write-order mutation rejected')
    return a.encode({'source_case':{'s':13,'t':14,'u':1,'w':1,'p':16,'P':24,
                                    'source_rows':len(selected),'interior_rows':len(I),'boundary_rows':len(B)},
                     'H_gap':a.gap(H),'H_norm':a.norm(H),'S_gap':a.gap(S),'S_norm':a.norm(S),
                     'rounded_gap':a.gap(A),'rounded_norm':a.norm(A),
                     'norms':{'L':a.norm(L),'U':a.norm(U),'L_inverse':a.norm(a.inverse(L)),
                              'U_inverse':a.norm(a.inverse(U))},
                     'stage_envelopes':[{k:z[k]for k in ('pivot','gap','norm','pivot_gap')}for z in stages],
                     'actual_factor_write_states':len(writes),'bandwidth':2,
                     'controls':['unrounded-S-factor-substitution','factor-write-order'],
                     'scope':'actual physical setup only; finite p16/P24 is not production precision',
                     'cleanup':'all owned source pool cells blank, markers erased and heads restored'})
