"""Complete eight-point matroid and marked-support certificate replay.

Standard library only, no searches for field representations, no network, no
writes. Full modular-cut generation proves catalogue coverage. Nick Petalas'
credited, hash-bound seven-point extension routine supplies the simple bases.
New enumeration, support classification and certificate integration prepared
by flyingviper with substantial OpenAI Codex and separate-agent assistance.
Apache-2.0. See MATROID-PROOF.md for the exact scope and reduction argument.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRE_PATH = 'research/p112-five-term-reader-floor/verify.py'
PRE_SHA = '9bbe2c9b404e519ae41835eb3e7ebc586ea60ec2612204258130cc95b8bde038'
PERMS = tuple(permutations(range(5)))
MASK_TRANSFORMS = tuple(tuple(sum(1 << p[i] for i in range(5) if s >> i & 1)
                              for s in range(32)) for p in PERMS)
FAMILY_CACHE = {}
FIELD_CACHE = {}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def no_duplicate_keys(items):
    result = {}
    for key, value in items:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def read_json(name):
    with (HERE / name).open('rb') as stream:
        raw = stream.read(2_097_153)
    need(len(raw) <= 2_097_152, 'certificate capacity')
    return json.loads(raw, object_pairs_hook=no_duplicate_keys)


def load_predecessor():
    path = ROOT / PRE_PATH
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == PRE_SHA, 'seven-point generator source hash')
    module = ModuleType('credited_seven_point_extension')
    module.__file__ = str(path)
    # Execute authenticated source directly, never a potentially stale .pyc.
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module

def circuit_list(ranks,n):
    return tuple(m for m in range(1,1<<n) if ranks[m]<m.bit_count() and all(ranks[m^(1<<i)]==m.bit_count()-1 for i in range(n) if m>>i&1))

def canonical_matroid(ranks,n):
    circuits=circuit_list(ranks,n)
    signatures=[tuple(sum(1 for c in circuits if c>>i&1 and c.bit_count()==k) for k in range(1,n+1)) for i in range(n)]
    blocks=[[i for i in range(n) if signatures[i]==s] for s in sorted(set(signatures))]
    # Color refinement by the pair-incidence counts of all circuit sizes.
    while True:
        colors={v:k for k,b in enumerate(blocks) for v in b}
        enhanced=[]
        for i in range(n):
            pair_profiles=[]
            for b in blocks:
                pair_profiles.append(tuple(sorted(tuple(sum(1 for c in circuits if c>>i&1 and c>>j&1 and c.bit_count()==k) for k in range(1,n+1)) for j in b if j!=i)))
            enhanced.append((colors[i],tuple(pair_profiles)))
        fresh=[[i for i in range(n) if enhanced[i]==s] for s in sorted(set(enhanced))]
        if len(fresh)==len(blocks):
            break
        blocks=fresh
    best=None;best_order=None
    # Uniform and free matroids have invariant full size layers.
    counts=Counter(c.bit_count() for c in circuits)
    uniform=all(count==len(list(combinations(range(n),size))) for size,count in counts.items())
    orders=[tuple(range(n))] if uniform else (sum(pieces,()) for pieces in product(*(permutations(b) for b in blocks)))
    for order in orders:
        mapping=[0]*n
        for i,j in enumerate(order):mapping[j]=1<<i
        code=tuple(sorted(sum(mapping[i] for i in range(n) if c>>i&1) for c in circuits))
        if best is None or code<best:
            best,best_order=code,order
    mapped=tuple(ranks[sum(1<<best_order[i] for i in range(n) if mask>>i&1)] for mask in range(1<<n))
    return best,mapped

def compositions(total,k):
    if k==1:
        if total>=1:yield(total,)
        return
    for first in range(1,total-k+2):
        for rest in compositions(total-first,k-1):yield(first,)+rest

def rank3_seven():
    old=load_predecessor()
    types={()};answer={};counts=[]
    for n in range(1,8):
        types=set().union(*(old.extensions(lines,n-1) for lines in types))
        counts.append(len(types))
        if n<3:continue
        simple=[lines for lines in types if ((1<<n)-1,)!=lines]
        for lines in simple:
            for active in range(n,8):
                for multiplicities in compositions(active,n):
                    owner=sum(([i]*m for i,m in enumerate(multiplicities)),[])+[-1]*(7-active)
                    ranks=[]
                    for mask in range(128):
                        reduced=0
                        for i in range(7):
                            if mask>>i&1 and owner[i]>=0:reduced|=1<<owner[i]
                        ranks.append(old.old_rank(reduced,lines))
                    key,table=canonical_matroid(ranks,7)
                    answer[key]=table
    if len(answer)!=108 or counts!=[1,1,2,3,5,10,24]:raise ValueError(('rank3 count',len(answer),counts))
    return sorted(answer.values())

def cut_data(ranks,n):
    flats=[mask for mask in range(1<<n) if all(ranks[mask|1<<i]>ranks[mask] for i in range(n) if not mask>>i&1)]
    index={f:i for i,f in enumerate(flats)}
    upper=[sum(1<<j for j,h in enumerate(flats) if f&h==f) for f in flats]
    intersections=[[index[f&h] if ranks[f]+ranks[h]==ranks[f&h]+ranks[f|h] else -1 for h in flats] for f in flats]
    closure_index=[]
    for mask in range(1<<n):
        flat=mask
        for i in range(n):
            if ranks[mask|1<<i]==ranks[mask]:flat|=1<<i
        closure_index.append(index[flat])
    return flats,upper,intersections,closure_index

def cuts(ranks,n):
    flats,upper,inter,closure_index=cut_data(ranks,n)
    def close(seed):
        present=0;todo=seed
        while todo:
            bit=todo&-todo;todo^=bit
            if present&bit:continue
            i=bit.bit_length()-1
            prior=present;present|=bit
            todo|=upper[i]&~present
            while prior:
                other=prior&-prior;prior^=other
                j=inter[i][other.bit_length()-1]
                if j>=0 and not present>>j&1:todo|=1<<j
        return present
    current=0
    while True:
        if current:
            yield tuple(ranks[mask]+(not(current>>closure_index[mask]&1)) for mask in range(1<<n))
        for i in range(len(flats)-1,-1,-1):
            if current>>i&1:continue
            prefix=(1<<i)-1
            candidate=close((current&prefix)|(1<<i))
            if candidate&prefix==current&prefix:
                current=candidate
                break
        else:break

def minimum_family(masks):
    kept = []
    for s in sorted(masks,key=lambda s:(s.bit_count(),s)):
        if not any(t & s == t for t in kept):
            kept.append(s)
    return sum(1 << s for s in kept)

def unpack(family):
    return [s for s in range(32) if family >> s & 1]

def family_images(family):
    if family not in FAMILY_CACHE:
        masks = unpack(family)
        FAMILY_CACHE[family] = tuple(sum(1 << table[s] for s in masks)
                                     for table in MASK_TRANSFORMS)
    return FAMILY_CACHE[family]

def canonical_requests(pairs):
    images = [(family_images(a),family_images(b)) for a,b in pairs]
    best = None
    witness = None
    for p in range(120):
        values = [(a[p],b[p]) for a,b in images]
        for transpose in (False,True):
            data = [(b,a) for a,b in values] if transpose else values
            order = tuple(sorted(range(3),key=lambda j:(data[j],j)))
            key = tuple(data[j] for j in order)
            if best is None or key < best:
                best = key
                witness = {'query_permutation':PERMS[p], 'target_order':order,
                           'transpose':transpose}
    return best,witness

def marking_data():
    result = []
    for marks in combinations(range(8),3):
        markmask = sum(1 << i for i in marks)
        queries = [i for i in range(8) if i not in marks]
        qsets = tuple(sum(1 << queries[i] for i in range(5) if s >> i & 1)
                      for s in range(32))
        result.append((marks,markmask,queries,qsets))
    return result

def derive(ranks,marks,markmask,qsets):
    pairs = []
    for mark in marks:
        bit = 1 << mark
        others = markmask ^ bit
        source = minimum_family(a for a in range(32)
                                if ranks[qsets[31^a]|markmask] > ranks[qsets[31^a]|others])
        reader = minimum_family(s for s in range(32)
                                if ranks[qsets[s]|bit] == ranks[qsets[s]])
        need(source and reader and not(source & 1) and not(reader & 1),
             'nonempty active source/reader request families')
        pairs.append((source,reader))
    return tuple(pairs)

def orthogonality(pairs):
    return all((a & b).bit_count() != int(i != j)
               for i in range(3) for j in range(3)
               for a in unpack(pairs[i][0]) for b in unpack(pairs[j][1]))

def validate_rank_table(r,total_rank):
    need(len(r)==256 and r[0]==0 and r[255]==total_rank,'rank-table shape')
    # Local rank axioms imply monotonicity/submodularity for a rank function.
    for S in range(256):
        need(0 <= r[S] <= min(total_rank,S.bit_count()),'rank range')
        missing = [i for i in range(8) if not(S >> i & 1)]
        for i in missing:
            need(r[S] <= r[S|1<<i] <= r[S]+1,'rank one-element increment')
        for i,j in combinations(missing,2):
            need(r[S|1<<i]+r[S|1<<j] >= r[S]+r[S|1<<i|1<<j],
                 'local submodularity')

def reducible(r,queries,total_rank):
    for i,j in combinations(queries,2):
        pair = (1<<i)|(1<<j)
        if r[pair] <= 1:
            return {'side':'source','query_elements':[i,j]}
        if 2+r[255^pair]-total_rank <= 1:
            return {'side':'reader','query_elements':[i,j]}
    return None

def field(degree,polynomial):
    key=(degree,polynomial)
    if key not in FIELD_CACHE:
        size=1<<degree
        need(2<=degree<=5 and polynomial.bit_length()==degree+1,'field polynomial degree')
        def multiply(a,b):
            c=0
            while b:
                if b&1:
                    c^=a
                b>>=1
                a<<=1
                if a&size:
                    a^=polynomial
            return c
        table=[[multiply(a,b) for b in range(size)] for a in range(size)]
        inv=[0]
        for a in range(1,size):
            choices=[b for b in range(1,size) if table[a][b]==1]
            need(len(choices)==1,'every nonzero polynomial residue has a unique inverse')
            inv.append(choices[0])
        FIELD_CACHE[key]=(table,inv)
    return FIELD_CACHE[key]

def subset_ranks(columns,table,inv):
    bases=[()]
    ranks=[0]
    for mask in range(1,256):
        bit=mask&-mask
        base=bases[mask^bit]
        v=list(columns[bit.bit_length()-1])
        for pivot,row in base:
            factor=v[pivot]
            if factor:
                v=[x^table[factor][y] for x,y in zip(v,row)]
        if any(v):
            p=next(i for i,x in enumerate(v) if x)
            row=tuple(table[inv[v[p]]][x] for x in v)
            base=tuple(sorted(base+((p,row),)))
        bases.append(base)
        ranks.append(len(base))
    return ranks

def parse_catalogue(document):
    need(document['schema_version'] == 1, 'matroid schema')
    need(set(document['rank_tables']) == {'3', '4'}, 'both required ranks')
    tables = {}
    for total_rank, expected in ((3, 325), (4, 940)):
        lines = document['rank_tables'][str(total_rank)]
        need(len(lines) == expected and len(set(lines)) == expected, 'distinct catalogue rows')
        need(all(type(line) is str and len(line) == 256
                 and set(line) <= set('01234') for line in lines), 'bounded rank-table encoding')
        tables[total_rank] = [tuple(map(int, line)) for line in lines]
        for table in tables[total_rank]:
            validate_rank_table(table, total_rank)
    return tables


def regenerate_catalogues(tables):
    """All simplifications/multiplicities, dual bases, and nonempty modular cuts."""
    seven = rank3_seven()
    need(len(seven) == 108, 'seven-element base count')
    counts = {}
    for total_rank in (3, 4):
        bases = seven if total_rank == 3 else [
            tuple(mask.bit_count() + row[127 ^ mask] - 3 for mask in range(128))
            for row in seven]
        generated = {}
        extensions = 0
        for base in bases:
            for extension in cuts(base, 7):
                key, table = canonical_matroid(base + extension, 8)
                generated[key] = table
                extensions += 1
        # Equality of every indexed rank table, not an appeal to the known count.
        need(sorted(generated.values()) == tables[total_rank], 'complete regenerated rank tables')
        need(extensions == {3: 3435, 4: 33982}[total_rank], 'complete modular-cut multiplicity')
        counts[total_rank] = extensions
        print(json.dumps({'stage': 'complete_modular_cut_catalogue', 'rank': total_rank,
                          'extensions': extensions, 'types': len(generated)}), flush=True)
    return counts


def verify_certificates(document, tables):
    represented, excluded, unresolved = set(), set(), set()
    literal_field_ranks = {}
    fields = Counter()
    seen = set()
    need(len(document['certificates']) == 1265, 'one certificate status per table')
    for record in document['certificates']:
        rank, index = record['rank'], record['index']
        need(type(rank) is int and rank in tables and type(index) is int
             and 0 <= index < len(tables[rank]), 'certificate table address')
        key = (rank, index)
        need(key not in seen, 'duplicate certificate address')
        seen.add(key)
        table = tables[rank][index]
        status = record['status']
        if status == 'represented':
            degree, polynomial = record['degree'], record['polynomial']
            need(type(degree) is int and type(polynomial) is int, 'field integer parameters')
            mult, inverse = field(degree, polynomial)
            columns = record['columns']
            need(len(columns) == 8 and all(len(column) == rank for column in columns),
                 'field matrix dimensions')
            need(all(type(value) is int and 0 <= value < 1 << degree
                     for column in columns for value in column), 'field entries')
            actual = tuple(subset_ranks(columns, mult, inverse))
            need(actual == table, 'all 256 literal extension-field subset ranks')
            represented.add(key)
            literal_field_ranks[key] = actual
            fields[degree] += 1
        elif status == 'ingleton-excluded':
            proof = record['ingleton']
            a, b, c, d = proof['sets']
            need(all(type(s) is int and 0 <= s < 256 for s in (a, b, c, d)), 'Ingleton masks')
            lhs = table[a|b]+table[a|c]+table[a|d]+table[b|c]+table[b|d]
            rhs = table[a]+table[b]+table[c|d]+table[a|b|c]+table[a|b|d]
            need(lhs == proof['lhs'] and rhs == proof['rhs'] and lhs < rhs,
                 'strict Ingleton violation')
            excluded.add(key)
        else:
            need(status == 'unresolved', 'explicit unresolved status')
            unresolved.add(key)
    need(seen == {(rank, index) for rank, rows in tables.items() for index in range(len(rows))},
         'certificate partition coverage')
    need((len(represented), len(excluded), len(unresolved)) == (1150, 39, 76),
         'verified certificate census')
    need(dict(fields) == {2: 19, 3: 101, 4: 1024, 5: 6}, 'field certificate counts')
    return represented, excluded, literal_field_ranks


def unpacked_key(key):
    """The receipt uses lexicographic minimal-mask lists as stable class IDs."""
    return tuple((tuple(unpack(a)), tuple(unpack(b))) for a, b in key)


def marked_classes(tables, represented, excluded):
    classes = {}
    canonical_cache = {}
    markings = marking_data()
    counts = Counter()
    rank_keys = {3: set(), 4: set()}
    for total_rank, rows in sorted(tables.items()):
        for index, table in enumerate(rows):
            address = (total_rank, index)
            for marks, markmask, queries, qsets in markings:
                if table[markmask] != 3 or table[qsets[31]] != total_rank:
                    continue
                pairs = derive(table, marks, markmask, qsets)
                need(orthogonality(pairs), 'literal circuit/cocircuit support orthogonality')
                raw = min(tuple(sorted(pairs)), tuple(sorted((b, a) for a, b in pairs)))
                if raw not in canonical_cache:
                    canonical_cache[raw] = canonical_requests(raw)[0]
                key = canonical_cache[raw]
                rank_keys[total_rank].add(key)
                if key not in classes:
                    classes[key] = {'key': key, 'matroids': set(), 'marked_instances': 0,
                                    'possible_marked_instances': 0, 'all_possible_reducible': True}
                item = classes[key]
                item['matroids'].add(address)
                item['marked_instances'] += 1
                if address not in excluded:
                    item['possible_marked_instances'] += 1
                    if reducible(table, queries, total_rank) is None:
                        item['all_possible_reducible'] = False
                counts[total_rank] += 1
    need(dict(counts) == {3: 9554, 4: 41386}, 'every independent spanning marking')
    need({rank: len(keys) for rank, keys in rank_keys.items()} == {3: 1949, 4: 7664},
         'each rank marked-signature census')
    ordered = [item for _, item in sorted(classes.items(), key=lambda kv: unpacked_key(kv[0]))]
    need(len(ordered) == 9377, 'complete combined support-signature census')
    for index, item in enumerate(ordered):
        item['index'] = index
        if item['matroids'] & represented:
            item['closure'] = 'field'
        elif not (item['matroids'] - excluded):
            item['closure'] = 'ingleton'
        elif item['all_possible_reducible']:
            item['closure'] = 'merge'
        else:
            item['closure'] = 'open'
    closure = Counter(item['closure'] for item in ordered)
    need(dict(closure) == {'field': 8329, 'ingleton': 347, 'merge': 22, 'open': 679},
         'conservative universal closure partition')
    return ordered


def verify_selective(document, classes, literal_fields, excluded):
    need(document['schema_version'] == 1, 'support schema')
    expected_counts = {'rank3_markings': 9554, 'rank4_markings': 41386,
                       'classes': 9377, 'field_closed': 8329, 'ingleton_closed': 347,
                       'merge_closed': 22, 'merge_markings': 186,
                       'selective_closed': 544, 'remaining': 135}
    need(document['counts'] == expected_counts, 'support census receipt')
    merged = [item['index'] for item in classes if item['closure'] == 'merge']
    need(merged == document['merge_class_indices'], 'every universal merge class')
    merge_instances = sum(item['possible_marked_instances'] for item in classes
                          if item['closure'] == 'merge')
    need(merge_instances == 186, 'all actual non-Ingleton merge provenances')
    safe = {}
    for witness in document['field_markings']:
        class_index, rank, index = witness['class_index'], witness['rank'], witness['index']
        need(type(class_index) is int and 0 <= class_index < len(classes), 'safe class address')
        need(class_index not in safe, 'one literal field marking per safe class')
        need((rank, index) in literal_fields, 'verified literal field matrix')
        table = literal_fields[(rank, index)]
        marks = witness['marks']
        need(len(marks) == 3 and sorted(set(marks)) == marks
             and all(type(x) is int and 0 <= x < 8 for x in marks), 'literal target marking')
        markmask = sum(1 << i for i in marks)
        queries = [i for i in range(8) if i not in marks]
        qsets = tuple(sum(1 << queries[i] for i in range(5) if s >> i & 1) for s in range(32))
        need(table[markmask] == 3 and table[qsets[31]] == rank, 'literal independent spanning targets')
        key = canonical_requests(derive(table, marks, markmask, qsets))[0]
        need(key == classes[class_index]['key'], 'literal field marked-signature equality')
        need(classes[class_index]['closure'] == 'field', 'represented safe signature')
        safe[class_index] = key
    need(len(safe) == 228, 'complete supplied literal safe markings')
    closed = set()
    used_safe = set()
    inclusions = 0
    for witness in document['selective_witnesses']:
        index, target_index = witness['old_class_index'], witness['safe_class_index']
        need(type(index) is int and 0 <= index < len(classes), 'selective old address')
        need(index not in closed and classes[index]['closure'] == 'open', 'distinct open selective class')
        need(target_index in safe, 'selective witness bound to literal field marking')
        perm = witness['query_permutation']
        target_map = witness['old_target_to_safe_slot']
        transpose = witness['transpose_old']
        need(sorted(perm) == list(range(5)) and all(type(v) is int for v in perm), 'query bijection')
        need(sorted(target_map) == list(range(3)) and all(type(v) is int for v in target_map),
             'target bijection')
        need(type(transpose) is bool, 'explicit transpose flag')
        for j, pair in enumerate(classes[index]['key']):
            if transpose:
                pair = pair[::-1]
            for family, safe_family in zip(pair, safe[target_index][target_map[j]]):
                for mask in unpack(family):
                    transformed = sum(1 << perm[i] for i in range(5) if mask >> i & 1)
                    need(any(s & transformed == s for s in unpack(safe_family)),
                         'literal minimal-support subset inclusion')
                    inclusions += 1
        closed.add(index)
        used_safe.add(target_index)
    need(len(closed) == 544 and used_safe == set(safe) and inclusions == 10433,
         'complete selective transfer receipt')
    remaining = []
    for item in classes:
        if item['closure'] != 'open' or item['index'] in closed:
            continue
        remaining.append({'index': item['index'],
                          'source_minimal_masks': [unpack(a) for a, b in item['key']],
                          'reader_minimal_masks': [unpack(b) for a, b in item['key']],
                          'matroid_indices': [list(p) for p in sorted(item['matroids'] - excluded)]})
    need(remaining == document['remaining_classes'] and len(remaining) == 135,
         'exact complete remaining support families')
    need(len({tuple(p) for row in remaining for p in row['matroid_indices']}) == 61,
         'remaining provenance census')
    return {'marked_safe_signatures': len(safe), 'selective_closures': len(closed),
            'minimal_support_inclusions': inclusions, 'merge_markings': merge_instances,
            'remaining_classes': len(remaining)}


def load_frontier():
    """Return saved canonical family rows for the separate cost replay.

    This convenience reader does not replace this module's full verification.
    The registered run verifies these exact receipt rows before pricing them.
    """
    return read_json('SUPPORT-TRANSFER.json')['remaining_classes']


def controls():
    bad = [min(mask.bit_count(), 3) for mask in range(256)]
    bad[3] = 3
    try:
        validate_rank_table(bad, 3)
    except ValueError:
        pass
    else:
        raise ValueError('malformed rank table accepted')
    try:
        field(4, 21)
    except ValueError:
        pass
    else:
        raise ValueError('reducible field polynomial accepted')
    need(not any(s & 3 == s for s in (5, 6)), 'containment is not equal-size intersection')


def main():
    controls()
    document = read_json('MATROIDS.json')
    tables = parse_catalogue(document)
    extensions = regenerate_catalogues(tables)
    represented, excluded, literal_fields = verify_certificates(document, tables)
    classes = marked_classes(tables, represented, excluded)
    receipt = verify_selective(read_json('SUPPORT-TRANSFER.json'), classes, literal_fields, excluded)
    print(json.dumps({'status': 'PASS_MATROID_SUPPORT_CLASSIFICATION',
                      'rank3_tables': len(tables[3]), 'rank4_tables': len(tables[4]),
                      'modular_cut_extensions': extensions,
                      'field_matrices': len(represented), 'field_subset_ranks': 256 * len(represented),
                      'ingleton_exclusions': len(excluded), 'marked_classes': len(classes),
                      **receipt}, separators=(',', ':')))


if __name__ == '__main__':
    main()
