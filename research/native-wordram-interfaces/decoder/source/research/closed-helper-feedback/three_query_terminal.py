"""Three-query closed feedback workspace on the actual original native word.
Extends PR5457 (Ali Romman, substantial OpenAI Codex assistance); Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F

def check(m, source, bank, mutation=None):
    core, act, need, QSYM, KBASE = m.core, m.act, m.need, m.QSYM, m.KBASE
    queries = [dict(bank['queries'][j],query_index=i)for i,j in enumerate((0,16,32))]
    c = source['canonical']
    owners = bank['cold_helper_owners']
    raw_start, obs_start, scratch = 633, 636, 639
    rows = [core.identity(i) for i in range(640)]
    charts = c['start'][:] + [None]*8
    paid, ordinary = Counter(), Counter()
    def clear(slot, chart):
        need(slot>=632, 'No persistent erasure')
        rows[slot],charts[slot]={},chart
        ordinary['owned_clear']+=1
    def copy(dst,src):
        need(dst>=633 and not rows[dst], 'Owned COPY needs a cleared target')
        rows[dst],charts[dst]=rows[src].copy(),charts[src]
        ordinary['owned_copy']+=1
    need(all(c['start'][owner]==0 for owner in owners), 'Cold basis has common ground chart')
    # These three source first-departure rows are the original input identities.
    cold_index={owner:i for i,owner in enumerate(owners)}
    for q in queries:
        need(bank['T_rows'][cold_index[q['native_role']]]==[[cold_index[q['native_role']], '1']], 'Selected query has identity entrance row')
    bank_inputs=[r.copy() for r in rows[:632]]
    for q in queries:
        j, owner = q['query_index'], q['native_role']
        clear(raw_start+j,0);copy(raw_start+j,owner)
        event=source['programs']['forward'][q['source_event']]
        need(event[0]=='climb' and event[2:]==[owner,0,q['first_chart'],1], 'Exact selected query cut')
        charts[raw_start+j]=q['first_chart'];paid[1]+=1
        clear(obs_start+j,q['first_chart']);copy(obs_start+j,raw_start+j)
        rows[obs_start+j]=act(rows[owner],QSYM,-(KBASE+j));charts[obs_start+j]=0
    def invariant(j):
        q=queries[j];owner=q['native_role']
        need(rows[raw_start+j]==rows[owner], 'Raw cache current')
        need(rows[obs_start+j]==act(rows[owner],QSYM,-(KBASE+j)), 'Observation cache current')
        need(charts[raw_start+j]==q['first_chart'], 'Raw chart current')
    feedbacks=[(0,1,1),(1,2,1),(0,1,-1),(1,2,-1)]
    for h,k,coefficient in feedbacks:
        invariant(h);invariant(k)
        wh,wk=queries[h]['native_role'],queries[k]['native_role']
        clear(scratch,0);copy(scratch,obs_start+h)
        rows[scratch]=act(rows[scratch],KBASE+k);ordinary['monomial_map']+=1
        core.add(rows[wk],rows[scratch],F(coefficient));ordinary['scalar_add']+=1
        clear(scratch,0);copy(scratch,wh)
        rows[scratch]=act(rows[scratch],QSYM,QSYM,-(KBASE+h));ordinary['monomial_map']+=1
        core.add(rows[obs_start+k],rows[scratch],F(coefficient));ordinary['scalar_add']+=1
        rows[scratch]=act(rows[wh],KBASE+k,QSYM,-(KBASE+h));charts[scratch]=queries[k]['first_chart'];ordinary['monomial_map']+=1
        core.add(rows[raw_start+k],rows[scratch],F(coefficient));ordinary['scalar_add']+=1
        clear(scratch,0);invariant(h);invariant(k)
    # Keep the coupled helper inputs through the original physical source.
    entered=[row.copy()for row in rows[:632]]
    for j in range(3):clear(obs_start+j,0)
    by_event={q['source_event']:q for q in queries};cuts=0
    for event_index, e in enumerate(source['programs']['forward']):
        if event_index in by_event:
            q = by_event[event_index]
            owner, rawslot = q['native_role'], raw_start+q['query_index']
            need(charts[owner] == 0 and charts[rawslot] == q['first_chart'], 'Replacement charts')
            need(rows[owner] == rows[rawslot], 'Replacement row on all original and owned inputs')
            rows[owner], rows[rawslot] = rows[rawslot], rows[owner]
            if not (mutation == 'chart_swap' and cuts == 0):
                charts[owner], charts[rawslot] = charts[rawslot], charts[owner]
            need(charts[owner] == q['first_chart'] and charts[rawslot] == 0, 'Replacement chart transport')
            ordinary['physical_field_swap'] += 1
            clear(rawslot, 0)
            cuts += 1
            continue
        kind = e[0]
        if kind == 'scalar':
            gate, chart = e[1:]
            dst = gate[1][1]+(632 if gate[1][0] == 'C' else 0)
            if gate[0] == 'clear':
                need(dst == 632, 'Native persistent erasure')
                rows[dst], charts[dst] = {}, chart
                continue
            need(charts[dst] == chart, 'Native scalar destination chart')
            if gate[0] in ('copy','add'):
                src = gate[2][1]+(632 if gate[2][0] == 'C' else 0)
                need(charts[src] == chart, 'Native scalar source chart')
                if gate[0] == 'copy':
                    need(dst == 632, 'Native persistent overwrite')
                    rows[dst] = rows[src].copy()
                else:
                    core.add(rows[dst], rows[src], F(gate[3],gate[4]))
            else:
                need(gate[0] == 'scale', 'Known native scalar')
                rows[dst] = {key:F(gate[2],gate[3])*v for key,v in rows[dst].items()}
        elif kind == 'warp':
            _, ref, op, before, after = e
            owner = ref[1]+(632 if ref[0] == 'C' else 0)
            need(charts[owner] == before, 'Native warp chart')
            rows[owner], charts[owner] = core.warp(rows[owner], op, False), after
        elif kind in ('climb','center'):
            if kind == 'climb':
                _,_,owner,before,after,rank = e
                need(rank == len(c['frames'][after])-len(c['frames'][before]), 'Native climb rank')
            else:
                _,index,before,after,rank = e
                owner = 632+index
                need(rank == abs(len(c['frames'][after])-len(c['frames'][before])), 'Native center rank')
            need(charts[owner] == before, 'Native paid chart')
            charts[owner] = after
            paid[rank] += 1
        else:
            need(kind in ('phase','adapter','residual_adapter'), 'Known native marker')

    for owner in range(632):
        expected=entered[owner].copy()
        if 112<=owner<224:core.add(expected,entered[owner-112],F(1))
        need(rows[owner]==expected, 'Original source on coupled helper inputs')
    need(all(c['final'][q['native_role']]==1 for q in queries), 'Selected helpers already full at source exit')
    h,k=queries[0]['native_role'],queries[2]['native_role']
    clear(scratch,1);copy(scratch,h)
    rows[scratch]=act(rows[scratch],KBASE+2,QSYM,QSYM,-KBASE);ordinary['monomial_map']+=1
    if mutation!='omit_terminal_decode':core.add(rows[k],rows[scratch],F(-1))
    ordinary['scalar_add']+=1;clear(scratch,1)
    for owner in range(632):need(rows[owner]==core.expected(owner,False), 'Original independent terminal endpoint')
    need(charts[:632]==c['final'], 'Original endpoint charts')
    need(paid==Counter(m.PROFILE), 'Original paid Gaussian profile preserved')
    need(all(not row for row in rows[632:]), 'All arbitrary owned input cleared')
    need(ordinary==Counter(owned_clear=26,owned_copy=15,physical_field_swap=3,scalar_add=13,monomial_map=13),'Complete closed workspace invoice')
    return {'status':'PASS_THREE_QUERY_TERMINAL_DECODER','original_inputs':632,'arbitrary_owned_inputs':8,
            'additional_owned_fields':7,'replacement_cuts':cuts,'paid':dict(sorted(paid.items())),
            'ordinary':dict(ordinary),'basis_adds':0,'basis_scales':0,
            'observation_normalizers':3,'completion_calls':0,'target_abi':'exact original independent helper/main ABI',
            'new_kappa':False,'feedbacks':feedbacks,'source_query_indices':[0,16,32]}
