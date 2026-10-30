"""Materialize the exact PR5806 hybrid through protected event ordinals.

PR5806 gives the construction. Ali Romman / OpenAI Codex supplied this code.
Apache-2.0. All parent notices remain in inputs/NOTICES.md and NOTICE.
"""
from copy import deepcopy

ROLES = {41, 42, 65, 106, 240, 400, 401, 403, 405, 410, 741,
         57, 81, 92, 224, 225, 227, 229, 234, 742}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def touches(event):
    return event[1] in ROLES or (event[0] in ('ADD', 'COPY') and event[2] in ROLES)


def indices(word):
    return [i for i, event in enumerate(word['program']) if touches(event)]


def correspondence(source, target):
    left, right = indices(source), indices(target)
    need([source['program'][i] for i in left] == [target['program'][i] for i in right],
         'Complete protected trace equality')
    return dict(zip(left, right))


def r22(common, accumulated, edits):
    mapping = correspondence(common, accumulated)
    first, second = deepcopy(common), deepcopy(accumulated)
    for word in (first, second):
        need(word['frames'][1090] == edits['frames'][0], 'Existing exact R22 frame')
        for side in ('initial', 'final'):
            for key, (old, new) in edits[side].items():
                need(word[side][int(key)] == old, 'Old helper boundary')
                word[side][int(key)] = new
    replacements = []
    for old, new in edits['program']:
        found = [i for i in range(len(common['program']) - len(old) + 1)
                 if common['program'][i:i + len(old)] == old]
        need(len(found) == 1, 'Unique full-source hunk')
        begin = found[0]
        need(all(e[1] in ROLES and (e[0] not in ('ADD', 'COPY') or e[2] in ROLES)
                 for e in old + new), 'The hunk stays wholly in the protected support')
        replacements.append((list(range(begin, begin + len(old))), new))
    for word, translate in ((first, {i: i for i in mapping}), (second, mapping)):
        remove, insert = set(), {}
        for old_indices, new in replacements:
            positions = [translate[i] for i in old_indices]
            need(not remove.intersection(positions), 'Disjoint hunks')
            remove.update(positions); insert[positions[0]] = new
        out = []
        for i, event in enumerate(word['program']):
            out.extend(deepcopy(insert.get(i, [])))
            if i not in remove:
                out.append(event)
        word['program'] = out
    correspondence(first, second)
    return first, second


def second_block(common, accumulated, plan):
    mapping = correspondence(common, accumulated)
    result = deepcopy(accumulated)
    frame = plan['new_frame']
    need(len(result['frames']) == frame, 'Append one exact frame')
    result['frames'].append(plan['basis'])
    need(result['initial'][742] == result['final'][225] == 267, 'Second-block helper boundaries')
    result['initial'][742] = result['final'][225] = frame
    for i in plan['changed_scalar_source_indices']:
        e = result['program'][mapping[i]]
        need(e == common['program'][i] and e[0] in ('ADD', 'SCALE') and e[-1] == 267,
             'Exact intermediate scalar occurrence')
        e[-1] = frame
    insert = {}
    for change in plan['native_changes']:
        i = change['source_index']
        if 'old' in change:
            need(result['program'][mapping[i]] == common['program'][i] == change['old'],
                 'Exact intermediate native occurrence')
            result['program'][mapping[i]] = change['replacement'][:]
        else:
            # The source ordinal identifies the next protected role-92 event.
            need(i in mapping and common['program'][i][1] == 92,
                 'Insertion is bound to the actual next role-92 event')
            insert[mapping[i]] = change['inserted'][:]
    out = []
    for i, event in enumerate(result['program']):
        if i in insert:
            out.append(insert[i])
        out.append(event)
    result['program'] = out
    return result


def construct(common, accumulated, edits, plan):
    need(common['public'] == accumulated['public'] == 770 and accumulated['owned_fields'] == 28,
         'Exact public and owned interfaces')
    mid_common, mid_hybrid = r22(common, accumulated, edits)
    result = second_block(mid_common, mid_hybrid, plan)
    need(len(result['program']) == 25982, 'Exact final instruction count')
    need([e for e in accumulated['program'] if not touches(e)] ==
         [e for e in result['program'] if not touches(e)], 'Every complementary event is retained')
    need([e for e in accumulated['program'] if e[0] in ('INIT', 'COPY', 'CLEAR')] ==
         [e for e in result['program'] if e[0] in ('INIT', 'COPY', 'CLEAR')],
         'Every owned event and source COPY is retained')
    return result
