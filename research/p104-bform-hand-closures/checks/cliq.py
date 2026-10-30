# Lemma P, second half: compatibility graph of planes from pairs_exact.pkl (written by planes.py): degrees, shared classes, maximal families. Apache-2.0.
import pickle, collections, time
D = pickle.load(open('pairs_exact.pkl', 'rb')); P = D['planes']; E = D['pairs']
adj = collections.defaultdict(set)
for i, j in E: adj[i].add(j); adj[j].add(i)
print('vertices', len(adj), 'edges', len(E))
print('degree hist', sorted(collections.Counter([len(a) for a in adj.values()]).items()))
inter = collections.Counter(len(set(P[i]) & set(P[j])) for i, j in E)
print('pairs by shared classes', sorted(inter.items()))
def cliques():
    # maximal cliques (Bron-Kerbosch with pivot)
    out = []
    def bk(R, Pp, X):
        if not Pp and not X: out.append(R); return
        u = max(Pp | X, key=lambda w: len(adj[w] & Pp))
        for w in list(Pp - adj[u]):
            bk(R | {w}, Pp & adj[w], X & adj[w]); Pp = Pp - {w}; X = X | {w}
    bk(set(), set(adj), set())
    return out
cs = collections.Counter(len(c) for c in cliques())
print('maximal clique sizes', sorted(cs.items()))
