"""Check the native ranks for every chart in the fixed subspace interval.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The exact Clifford implementation is retained from the credited source export.
"""
from contextlib import ExitStack
import gzip
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from sources import sources, load, need
from construct import span, interval


def basis(space):
    out, seen = [], frozenset({0})
    for v in sorted(space):
        if v not in seen:
            out.append(v)
            seen = span(out)
    need(seen == frozenset(space), 'Exact basis of the listed space')
    return out


def run():
    word = json.loads(gzip.decompress((HERE/'WORD.json.gz').read_bytes()))
    certificate = interval(word)
    with ExitStack() as contexts:
        cursor, _ = contexts.enter_context(sources())
        for depth in range(5):
            cursor, root = contexts.enter_context(load(cursor/'sources.py','rank_source_'+str(depth)).sources())
        C = load(root/'research/p104-native-channel/vendor/clifford_exact.py','block_native_rank')
        def chart(vectors):
            op = C.canonical_frame(9,tuple(vectors))
            space = span(vectors)
            images = op.tab[9:]
            need(C.rank([x|(z<<9) for x,z,_ in images]) == 9,'Full Pauli image dimension')
            need(all(x in space and all(((x^z)&u).bit_count()%2 == 0 for u in vectors)
                     for x,z,_ in images), 'Exact native Lagrangian L(W)')
            return op
        incoming = [e[2] for e in word['program'] if e[0]=='MOVE' and e[3]==1090]
        outgoing = [e[3] for e in word['program'] if e[0]=='MOVE' and e[2]==1090]
        ids = set(incoming+outgoing+[word['initial'][405],word['final'][741]])
        charts = {i:chart(word['frames'][i]) for i in ids}
        def cost(a,b):
            return C.rank([x for x,z,p in a.adjoint().then(b).tab[9:]])
        def check(vectors):
            d = len(vectors)
            op = chart(vectors)
            need(all(cost(charts[i],op) == d-3 for i in incoming),'Eight actual incoming native ranks')
            need(all(cost(op,charts[i]) == len(word['frames'][i])-d for i in outgoing),
                 'Eight actual outgoing native ranks')
            need(cost(charts[word['initial'][405]],op) == d
                 and cost(op,charts[word['final'][741]]) == 9-d,'Both actual productive native ranks')
        for space in certificate['subspaces']:
            vectors = basis(space)
            if frozenset(space) == span(word['frames'][1090]):
                vectors = word['frames'][1090]
            if frozenset(space) == span(word['frames'][477]):
                vectors = word['frames'][477]
            check(vectors)
        try:
            check(word['frames'][1090][:-1])
        except ValueError:
            pass
        else:
            raise ValueError('Illegal rank-three frame accepted')
        print('PASS_ALL_67_NATIVE_CHARTS_1206_RANKS_AND_RANK3_REJECTION')


def main():
    with tempfile.TemporaryDirectory(prefix='block-rank-cache-') as cache:
        sys.pycache_prefix = cache
        run()


if __name__ == '__main__':
    main()
