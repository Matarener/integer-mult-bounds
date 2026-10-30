"""Derive a fresh candidate module from one authenticated integer.py source.

No file is patched and no Fraction/reference function is monkeypatched.
All complete controls must run against this candidate as an explicitly changed
integer backend. The frozen PR5864 original remains separately loadable.
Source-only at handoff: not executed by its author.
"""
from hashlib import sha256
from pathlib import Path
import types


REPLACEMENTS = [
    ('''def add_row(dst,src,n,k):
    for i,v in src.items():
        value=dst.get(i,0)+multiply(v,n,k)
        if value:dst[i]=value
        else:dst.pop(i,None)
''', '''def add_row(dst,src,n,k):
    return _integer_native.add_row(dst,src,n,k)
''', 1, 'fresh-native-sparse-add'),
    ('                        add_row(rows[r],rows[s],a,k)',
     '                        rows[r]=add_row(rows[r],rows[s],a,k)',
     1, 'ideal-adopts-fresh-row'),
    ('rows[r]={i:multiply(v,a,k) for i,v in rows[r].items()}',
     'rows[r]=_integer_native.scale_row(rows[r],a,k)',
     2, 'ideal-and-error-native-scale'),
    ('''                for i,v in rows[s].items():
                    old=rows[r].get(i,0);value=old+multiply(v,a,k);change=abs(value)-abs(old)
                    scores[r][0]+=change*w[i][0];scores[r][1]+=change*w[i][1];scores[r][2]+=change
                    if value:rows[r][i]=value
                    else:rows[r].pop(i,None)
''', '''                rows[r],native_scores=_integer_native.error_row(rows[r],rows[s],a,k,scores[r],w)
                scores[r]=list(native_scores)
''', 1, 'native-signed-error-row-and-scores'),
    ("            stream.update((str(j)+':'+','.join(str(F(v,u)) for v,u in zip(scores[r],units))+';').encode())",
     '            stream.update(_integer_native.score_bytes(j,scores[r],units))',
     1, 'exact-three-score-stream-bytes'),
    ('            for j in sorted(row,reverse=True):update_hash(h,j,row[j],S)',
     '            h.update(_integer_native.coefficient_bytes(row,S))',
     1, 'full-descending-coefficient-bytes'),
    ('''                for i,v in columns[r].items():
                    scores[i][0]+=abs(v)*w[j][0];scores[i][1]+=abs(v)*w[j][1];scores[i][2]+=abs(v)
                    update_hash(hashes[i],j,v,S)
''', '''                for i,native_scores,native_bytes in _integer_native.reverse_updates(columns[r],scores,w[j][0],w[j][1],j,S):
                    scores[i]=list(native_scores)
                    hashes[i].update(native_bytes)
''', 1, 'native-reverse-scores-and-signed-byte-chunks'),
    ('columns[r]={i:multiply(v,a,k) for i,v in columns[r].items()}',
     'columns[r]=_integer_native.scale_row(columns[r],a,k)',
     1, 'reverse-native-scale'),
    ("elif op in ('ADD','COPY'):add_row(columns[s],columns[r],a,k)",
     "elif op in ('ADD','COPY'):columns[s]=add_row(columns[s],columns[r],a,k)",
     1, 'reverse-adopts-fresh-row'),
]


def derive(source_path, native, expected_source_sha256):
    source_path = Path(source_path)
    if source_path.is_symlink() or not source_path.is_file():
        raise ValueError('integer input is a regular non-symlink source')
    raw = source_path.read_bytes()
    digest = sha256(raw).hexdigest()
    if digest != expected_source_sha256:
        raise ValueError('exact frozen integer source')
    source = raw.decode('utf-8')
    changes = []
    for before, after, count, name in REPLACEMENTS:
        if source.count(before) != count:
            raise ValueError('declared candidate seam count: ' + name)
        source = source.replace(before, after)
        changes.append(dict(name=name, count=count))
    module = types.ModuleType('integer_native_candidate')
    module.__file__ = str(source_path)
    module._integer_native = native
    exec(compile(source, '<integer-native-candidate>', 'exec'), module.__dict__)
    receipt = dict(original_integer_sha256=digest,
                   derived_integer_sha256=sha256(source.encode()).hexdigest(),
                   changes=changes,
                   integer_backend_changed=True,
                   fraction_reference_module_modified=False,
                   whole_replay_qualified=False,
                   source_only_handoff=True)
    return module, receipt
