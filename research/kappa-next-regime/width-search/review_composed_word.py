#!/usr/bin/env python3
"""Independent literal review of the three permanent R437 covector changes.

Uses only Python's standard library: no candidate constructor, optimizer, native
counter, or inherited geometry checker is imported. This is a local interface
and cost audit; the complete physical invoice remains a separate release gate.
Apache-2.0; substantial OpenAI assistance.
"""
from __future__ import annotations

from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from math import gcd
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
REGIME = HERE.parent
SOURCE = REGIME / 'sources/PR3647/research/bit-p111-r437-gl464-470-20261018/data/r0042/R437-COMPOSED-WORD.json.gz'
CANDIDATE = REGIME / 'word-search/candidate/WORD.json.gz'
PINS = {
    'source_archive': 'e432182d5b62c8bbefeb871fce30317234d707e5e18d4295e65ac21f7fd8365e',
    'source_content': 'da77deaf11368d016622348227657b98404b6afbc7e4f3d6fe9a246baae0dcce',
    'candidate_archive': 'ee42c58fb0cd23bad942ec472c7fb4f87db8261ce6ee4b2bc7e812212d8b836e',
    'candidate_content': '3f7de7e1d8a6ff9da8ab7650209b559062da4cc053de2b2566b306eb4fbeffd0',
}


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def content(word):
    return json.dumps(word, sort_keys=True, separators=(',', ':')).encode()


def flatten(gates):
    return [(f, target, source) for f, target, sources in gates for source in sources]


def primitive(row):
    divisor = 0
    for value in row:
        divisor = gcd(divisor, value)
    if not divisor:
        return tuple(row)
    if next(value for value in row if value) < 0:
        divisor = -divisor
    return tuple(value // divisor for value in row)


def remainder(vector, echelon):
    row = tuple(vector)
    for pivot, basis_row in echelon:
        coefficient = row[pivot]
        if coefficient:
            row = primitive([basis_row[pivot] * a - coefficient * b
                             for a, b in zip(row, basis_row)])
    return row


def basis(vectors):
    echelon = []
    for vector in vectors:
        row = remainder(vector, echelon)
        if any(row):
            pivot = next(j for j, value in enumerate(row) if value)
            echelon.append((pivot, primitive(row)))
            echelon.sort()
    return echelon


def geometry(word):
    require((word['h'], word['v'], word['R'], word['form']) ==
            (8, 111, 437, '<x,y>/2'), 'published literal dimensions and form')
    lines = word['lines']
    require(len(lines) == len(set(map(tuple, lines))) == 111, 'distinct 111 SOURCE lines')
    require(all(len(row) == 8 and sum(x*x for x in row) == 4 for row in lines),
            'rank-eight norm-four rational line presentation')
    require(sorted(word['ports_geom'] + word['punctured']) == list(range(120)),
            'published ports and nine punctures partition120')
    require(len(word['punctured']) == 9, 'nine punctures')
    dimensions, root_masks = [], []
    for frame in word['frames']:
        require(len(frame) == len(set(frame)) and all(0 <= j < 111 for j in frame),
                'unique valid roots in frame')
        echelon = basis([lines[j] for j in frame])
        closure = {j for j, line in enumerate(lines) if not any(remainder(line, echelon))}
        require(closure == set(frame), 'frame is exact rational root closure')
        dimensions.append(len(echelon))
        root_masks.append(sum(1 << j for j in frame))
    require(len(dimensions) == 636 and dimensions[:2] == [0, 8], 'original frame catalogue')
    require(len(word['start']) == len(word['final']) == 659, '659 complete endpoints')
    for j, line in enumerate(lines):
        require(dimensions[word['start'][j]] == 1 and j in word['frames'][word['start'][j]],
                'SOURCE entrance is its own rank-one line')
        require(word['final'][j] == 1, 'SOURCE exit is FULL')
        perpendicular = {k for k, other in enumerate(lines) if sum(a*b for a,b in zip(line, other)) == 0}
        require(set(word['frames'][word['final'][111+j]]) == perpendicular and
                dimensions[word['final'][111+j]] == 7, 'Y exit is exact orthogonal hyperplane')
    require(word['start'][111:] == [0]*548, 'Y and helpers have rank-zero entrances')
    require(word['final'][222:] == [1]*437, '437 full rank-eight helper widths')
    require(len(word['ret']) == len(set(word['ret'])) == 9 and
            all(222 <= r < 659 for r in word['ret']), 'nine distinct helper captures')
    return dimensions, root_masks


def multiply(left, right):
    return [[sum(a*b for a,b in zip(row,column)) for column in zip(*right)] for row in left]


def subtract(left, right):
    return [[a-b for a,b in zip(x,y)] for x,y in zip(left,right)]


def unit(size):
    return [[Fraction(i == j) for j in range(size)] for i in range(size)]


def inverse(matrix):
    size = len(matrix)
    augmented = [[Fraction(x) for x in row]+identity for row,identity in zip(matrix,unit(size))]
    for pivot in range(size):
        chosen = next(i for i in range(pivot,size) if augmented[i][pivot])
        augmented[pivot],augmented[chosen] = augmented[chosen],augmented[pivot]
        divisor = augmented[pivot][pivot]
        augmented[pivot] = [x/divisor for x in augmented[pivot]]
        for row in range(size):
            if row != pivot:
                coefficient = augmented[row][pivot]
                augmented[row] = [x-coefficient*y for x,y in zip(augmented[row],augmented[pivot])]
    return [row[size:] for row in augmented]


def native_gauge(projector):
    complement = subtract(unit(8),projector)
    return [a+b for a,b in zip(complement,projector)]+[a+b for a,b in zip(projector,complement)]


def exact_changed_gauges(word, old_paths, new_paths, changed_roles, dims):
    pairs = sorted({(a,b) for role in changed_roles for a,b in zip(new_paths[role],new_paths[role][1:])})
    old_pairs = {(a,b) for role in changed_roles for a,b in zip(old_paths[role],old_paths[role][1:])}
    projectors = {}
    for frame in sorted({f for pair in pairs for f in pair}):
        vectors = [row for _,row in basis([word['lines'][j] for j in word['frames'][frame]])]
        if vectors:
            transpose = list(map(list,zip(*vectors)))
            projector = multiply(multiply(transpose,inverse(multiply(vectors,transpose))),vectors)
        else:
            projector = [[Fraction(0)]*8 for _ in range(8)]
        require(projector == list(map(list,zip(*projector))), 'exact symmetric orthogonal projector')
        require(multiply(projector,projector) == projector, 'exact idempotent orthogonal projector')
        projectors[frame] = projector
    checks = []
    for a,b in pairs:
        A,B = projectors[a],projectors[b]
        require(multiply(A,B) == multiply(B,A) == A, 'exact nested rational projector products')
        delta = subtract(B,A)
        require(multiply(delta,delta) == delta, 'exact rational increment projector')
        increment = native_gauge(delta)
        require(multiply(increment,native_gauge(A)) == native_gauge(B),
                'exact 16-dimensional native gauge composition D_(B-A) D_A = D_B')
        require(multiply(increment,increment) == unit(16), 'exact inverse native increment')
        checks.append({'from_frame':a,'to_frame':b,'rank':dims[b]-dims[a],
                       'new_pair_on_changed_paths':(a,b) not in old_pairs})
    return {'arithmetic':'exact rational, no modular specialization',
            'projector_dimension':8,'native_matrix_dimension':16,
            'identity':'D_(P_B-P_A) D_(P_A) = D_(P_B); D_(P_B-P_A)^2 = I',
            'distinct_transitions_checked':len(checks),'transitions':checks,
            'projector_sha256':{frame:sha256(json.dumps([[str(x) for x in row] for row in P],separators=(',',':')).encode()).hexdigest()
                                for frame,P in projectors.items()}}


def literal_edits(source, word):
    unchanged = sorted(k for k in source if k not in ('A', 'C'))
    require(set(source) == set(word) and all(source[k] == word[k] for k in unchanged),
            'only A/C changed: endpoints, geometry, B, D and capture schedule unchanged')
    old = flatten(source['A'])
    removed = {
        1995: (506,241,322), 1999: (506,340,322), 2006: (506,349,322),
        2033: (509,444,271), 2040: (509,413,271), 2043: (509,413,371),
    }
    inserted = {1995: (122,463,322), 2033: (184,469,271), 2043: (391,468,371)}
    require(old[229] == (94,469,92), 'exact previous load at scalar A229')
    require(all(old[j] == gate for j, gate in removed.items()), 'six declared source contacts exist')
    expected = []
    for j, gate in enumerate(old):
        if j in inserted:
            expected.append(inserted[j])
        if j not in removed:
            expected.append((184,469,92) if j == 229 else gate)
    require(flatten(word['A']) == expected, 'candidate has precisely declared scalar edits and frames')
    expected_cleanup = [[1,d,ss] for _,d,ss in reversed(word['A']+word['B']) if not 111 <= d < 222]
    require(word['C'] == expected_cleanup, 'C is literal grouped FULL inverse of changed A/B')
    for section in ('A','C'):
        require(all(not 111 <= d < 222 for _,d,_ in word[section]), 'A/C have no Y writes')
    require(all(f == 0 and 111 <= d < 222 and all(s >= 222 for s in ss)
                for f,d,ss in word['D']), 'D is zero-frame dirty-helper compensation')
    # Reconstruct each frozen donor covector at the insertion, independently of
    # the optimizer's pair identities. Inspect every subsequent carrier contact.
    initial = [1 << r for r in range(659)]
    rows = initial[:]
    updates = {463: (1995,322), 469: (2033,271), 468: (2043,371)}
    frozen = {}
    contacts = {a: [] for a in updates}
    for j, (_,d,s) in enumerate(old):
        for a,(lo,b) in updates.items():
            if j == lo:
                frozen[a] = rows[b]
            if j >= lo and (a == d or a == s):
                contacts[a].append({'scalar_A_index': j, 'target': d, 'source': s})
        rows[d] ^= rows[s]
    require(all(all(c['target'] != a for c in cs) for a,cs in contacts.items()),
            'each carrier is never written after its insertion in original A')
    require(all(not any(a == d or a in ss for _,d,ss in source['B']) for a in updates),
            'permanent carriers have no B contacts')
    require(not set(updates) & set(source['ret']), 'permanent carriers are not captured')
    new = initial[:]
    for _,d,s in flatten(word['A']):
        new[d] ^= new[s]
    differences = {r: rows[r] ^ new[r] for r in range(659) if rows[r] != new[r]}
    require(differences == frozen, 'exact full dirty A output differs only by three frozen donor covectors')
    return {'unchanged_fields': unchanged, 'removed_scalar_contacts': removed,
            'inserted_scalar_contacts': inserted, 'original_carrier_contacts_after_insert': contacts,
            'A_output_changed_roles': sorted(differences),
            'frozen_donor_rows_hex': {a:hex(row) for a,row in frozen.items()},
            'unchanged_A_output_roles': 656, 'literal_cleanup': True}


def replay(word, dims, masks):
    n, v = 659, 111
    rows = [1 << r for r in range(n)]
    current = word['start'][:]
    paths = [[frame] for frame in current]
    hist, section_adds = Counter(), Counter()
    source_writes, captures = [], []
    all_ops, guard_count = [], 0
    source_mask = (1 << v)-1

    def advance(role, frame):
        before = current[role]
        require(masks[before] & ~masks[frame] == 0, 'all actual frame contacts are nested over Q')
        if before != frame:
            step = dims[frame]-dims[before]
            require(step > 0, 'strict positive dimension for distinct nested frames')
            hist[step] += 1
            current[role] = frame
            paths[role].append(frame)

    def gates(section):
        nonlocal guard_count
        for frame, target, sources in word[section]:
            require(0 <= frame < len(dims) and 0 <= target < n and len(sources) == len(set(sources)),
                    'well formed gate')
            require(all(0 <= s < n and s != target and not v <= s < 2*v for s in sources),
                    'gate sources are distinct non-Y roles, never target')
            for r in [target]+sources:
                advance(r, frame)
            for source in sources:
                rows[target] ^= rows[source]
                section_adds[section] += 1
                all_ops.append((target,source))
            if not v <= target < 2*v:
                require(rows[target] & source_mask & ~masks[frame] == 0,
                        'SOURCE component supported in exact current frame after every gate')
                guard_count += 1
            if target < v:
                source_writes.append((section,target,rows[target]))

    gates('D'); gates('A')
    for j, role in enumerate(word['ret']):
        frame = current[role]
        require(dims[frame] == 7, 'actual unchanged rank-seven capture')
        recipients = [v+t for t,ss in enumerate(word['scatter']) if j in ss]
        require(recipients and all(current[t] == 0 for t in recipients), 'all COPY recipients at zero frame')
        before, address = rows[role], current[role]
        work = rows[role]
        for target in recipients:
            rows[target] ^= work
            all_ops.append((target,role))
            section_adds['SCATTER'] += 1
        require(rows[role] == before and current[role] == address, 'captured source and ADDRESS immutable')
        work ^= rows[role]
        require(work == 0, 'literal same-original ERASE empties WORK')
        captures.append({'role':role, 'frame':frame, 'rank':dims[frame],
                         'recipients':recipients, 'full_row_hex':hex(before),
                         'WORK_after_erase':0})
        hist[7] += 1
    gates('B'); gates('C')
    for role, frame in enumerate(word['final']):
        advance(role, frame)
    require(current == word['final'], 'all final frames reached')
    wanted = [(1 << r) ^ ((1 << (r-v)) if v <= r < 2*v else 0) for r in range(n)]
    require(rows == wanted, 'full 659 by659 matrix has Y+=X and exact arbitrary dirty restoration')
    norm, reverse_norm = [1]*n, [1]*n
    maximum = reverse_maximum = 1
    for d,s in all_ops:
        norm[d] += norm[s]
        maximum = max(maximum,norm[d])
    for d,s in reversed(all_ops):
        reverse_norm[d] += reverse_norm[s]
        reverse_maximum = max(reverse_maximum,reverse_norm[d])
    return {'profile':dict(sorted(hist.items())), 'rank_mass':sum(r*c for r,c in hist.items()),
            'paths':paths, 'source_writes':source_writes, 'captures':captures,
            'scalar_ADDs':dict(section_adds), 'SOURCE_support_guards':guard_count,
            'forward_scalar_l1_bits':maximum.bit_length(),
            'reverse_scalar_l1_bits':reverse_maximum.bit_length()}


def raw_compensation(word):
    rows = [1 << r for r in range(659)]
    for section in ('A','B'):
        if section == 'B':
            for j,r in enumerate(word['ret']):
                for t,ss in enumerate(word['scatter']):
                    if j in ss:
                        rows[111+t] ^= rows[r]
        for _,d,s in flatten(word[section]):
            rows[d] ^= rows[s]
    expected = []
    for t in range(111):
        row = rows[111+t]
        require(row & ((1 << 222)-1) == (1 << t) ^ (1 << (111+t)),
                'raw target SOURCE/Y columns have exact desired interface')
        dirty = [r for r in range(222,659) if row >> r & 1]
        if dirty:
            expected.append([0,111+t,dirty])
    require(word['D'] == expected, 'D independently equals complete raw dirty response K')


def column_check(word):
    # Literal single-column state engine with a physically explicit temporary
    # role. No row matrices or forward results enter this calculation.
    operations = [(d,s) for section in ('D','A') for _,d,s in flatten(word[section])]
    for j,r in enumerate(word['ret']):
        operations.append((659,r))
        operations.extend((111+t,659) for t,ss in enumerate(word['scatter']) if j in ss)
        operations.append((659,r))
    operations.extend((d,s) for section in ('B','C') for _,d,s in flatten(word[section]))
    for reverse in (False,True):
        stream = operations[::-1] if reverse else operations
        for column in range(659):
            state = 1 << column
            for target,source in stream:
                if state >> source & 1:
                    state ^= 1 << target
            wanted = (1 << column) ^ ((1 << (111+column)) if column < 111 else 0)
            require(state == wanted, f'literal {"inverse" if reverse else "forward"} dirty column {column} and WORK zero')
    return {'independent_columns_per_direction':659, 'directions':['forward','inverse'],
            'literal_scalar_operations_including_COPY_ERASE':len(operations),
            'explicit_WORK_role':659, 'WORK_zero_for_every_column_in_both_directions':True}


def whole_rows(word):
    rows = [1 << r for r in range(659)]
    for section in ('D','A','B','C'):
        if section == 'B':
            for j,r in enumerate(word['ret']):
                for t,ss in enumerate(word['scatter']):
                    if j in ss:
                        rows[111+t] ^= rows[r]
        for _,d,s in flatten(word[section]):
            rows[d] ^= rows[s]
    return rows


def negative_controls(source, word, dims, masks):
    expected = whole_rows(word)
    stale = deepcopy(word); stale['C'] = source['C']
    require(whole_rows(stale) != expected, 'stale cleanup mutation detected')
    missing = deepcopy(word)
    j = next(j for j,g in enumerate(missing['A']) if g == [122,463,[322]])
    del missing['A'][j]
    require(whole_rows(missing) != expected, 'missing carrier mutation detected')
    dirty = deepcopy(word); dirty['D'] = dirty['D'][1:]
    require(whole_rows(dirty) != expected, 'missing dirty compensation mutation detected')
    frame = deepcopy(word); frame['A'][j][0] = 0
    try:
        replay(frame,dims,masks)
    except AssertionError:
        pass
    else:
        raise AssertionError('underpaid inserted frame mutation escaped')
    return ['stale original C', 'missing permanent carrier update',
            'missing dirty compensation row', 'rank-zero underpriced insertion frame']


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=HERE/'COMPOSED-WORD-INDEPENDENT-REVIEW.json')
    args = ap.parse_args()
    words = []
    for label,path in [('source',SOURCE),('candidate',CANDIDATE)]:
        raw = path.read_bytes(); word = json.loads(gzip.decompress(raw))
        require(sha256(raw).hexdigest() == PINS[label+'_archive'], label+' archive SHA256')
        require(sha256(content(word)).hexdigest() == PINS[label+'_content'], label+' canonical SHA256')
        words.append(word)
    source,word = words
    edits = literal_edits(source,word)
    dims,masks = geometry(word)
    old,new = replay(source,dims,masks),replay(word,dims,masks)
    require(old['profile'] == {1:1320,2:1344,3:77,4:43,5:102,6:11,7:18}, 'complete original local histogram')
    require(new['profile'] == {1:1322,2:1342,3:74,4:46,5:103,6:10,7:18}, 'complete new local histogram')
    require(new['rank_mass'] == old['rank_mass'] == 5113, 'unchanged complete local rank mass')
    require(new['captures'] == old['captures'], 'all nine full dirty capture rows and recipients unchanged')
    require(new['source_writes'] == old['source_writes'], 'all SOURCE write histories including dirty components unchanged')
    require(new['paths'][:222] == old['paths'][:222], 'all SOURCE and Y frame paths unchanged')
    changed_paths = [r for r in range(659) if old['paths'][r] != new['paths'][r]]
    require(set(changed_paths) <= {271,322,371,463,468,469}, 'only donor/carrier frame paths change')
    native_gauges = exact_changed_gauges(word,old['paths'],new['paths'],changed_paths,dims)
    delta = Counter(new['profile']); delta.subtract(old['profile'])
    delta = {r:c for r,c in sorted(delta.items()) if c}
    require(delta == {1:2,2:-2,3:-3,4:3,5:1,6:-1}, 'composed actual histogram, not additive assumption')
    raw_compensation(word)
    columns = column_check(word)
    controls = negative_controls(source,word,dims,masks)
    result = {'status':'PASS_INDEPENDENT_COMPOSED_R437_LOCAL_GEOMETRY_DIRTY_COPY_PROFILE',
              'script_sha256':sha256(Path(__file__).read_bytes()).hexdigest(), 'pins':PINS,
              'review_imports':'Python standard library only; no constructor, optimizer, native counter, or inherited geometry checker',
              'literal_edits':edits, 'geometry':{'frames':636,'exact_rational_frame_closure_checks':636*111,
                  'dimension':8,'helpers':437,'helper_width_histogram':{8:437},
                  'SOURCE_and_Y_frame_paths_unchanged':True,
                  'changed_helper_paths':{r:{'old':old['paths'][r],'new':new['paths'][r]} for r in changed_paths}},
              'columns':columns, 'capture_records':new['captures'],
              'exact_changed_native_gauges':native_gauges,
              'SOURCE_full_dirty_write_history_unchanged':True,
              'D_equals_complete_independently_reconstructed_dirty_response':True,
              'local_profile_before':old['profile'], 'local_profile_after':new['profile'],
              'actual_composed_profile_delta':delta,'rank_mass_before':old['rank_mass'],'rank_mass_after':new['rank_mass'],
              'scalar_ADDs_before':old['scalar_ADDs'], 'scalar_ADDs_after':new['scalar_ADDs'],
              'SOURCE_support_guards_after':new['SOURCE_support_guards'],
              'forward_scalar_l1_bits':new['forward_scalar_l1_bits'],
              'reverse_scalar_l1_bits':new['reverse_scalar_l1_bits'],
              'negative_controls':controls,
              'scope':'Local exact geometry, full arbitrary dirty forward/inverse scalar interface, literal COPY/ERASE and complete local cost profile. Native physical records, complete global owner/INDEX/ROW invoice and whole kappa certification are separate gates; this receipt alone asserts no new supplier admission.'}
    with args.out.open('x') as handle:
        json.dump(result,handle,sort_keys=True,indent=2); handle.write('\n')
    print(result['status'], 'delta',delta, 'changed paths',changed_paths, flush=True)


if __name__ == '__main__':
    main()
