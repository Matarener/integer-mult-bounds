"""Forward RUP checker, the same algorithm as rupcheck.c in pure Python (two watched literals,
persistent top-level trail, deletions ignored). check(cnf_lines, proof_lines) -> receipt dict."""


def parse(lines):
    """yield (is_deletion, [literals]) for each 0-terminated clause; comments and header skipped"""
    pending, dele = [], False
    for line in lines:
        line = line.strip()
        if not line or line[0] in "cp":
            continue
        toks = line.split()
        if toks[0] == "d" and not pending:
            dele, toks = True, toks[1:]
        for t in toks:
            x = int(t)
            if x == 0:
                yield dele, pending
                pending, dele = [], False
            else:
                pending.append(x)
    if pending:
        raise ValueError("unterminated clause")


class Checker:
    def __init__(self):
        self.val, self.watch, self.clauses, self.trail = {}, {}, [], []
        self.qhead, self.top_conflict = 0, False

    def lval(self, l):
        v = self.val.get(abs(l), 0)
        return v if l > 0 else -v

    def assign(self, l):
        self.val[abs(l)] = 1 if l > 0 else -1
        self.trail.append(l)

    def propagate(self):
        while self.qhead < len(self.trail):
            fl = -self.trail[self.qhead]
            self.qhead += 1
            ws = self.watch.get(fl, [])
            keep = []
            for idx, c in enumerate(ws):
                L = self.clauses[c]
                if L[0] == fl:
                    L[0], L[1] = L[1], fl
                if self.lval(L[0]) == 1:
                    keep.append(c)
                    continue
                for k in range(2, len(L)):
                    if self.lval(L[k]) != -1:
                        L[1], L[k] = L[k], fl
                        self.watch.setdefault(L[1], []).append(c)
                        break
                else:
                    keep.append(c)
                    if self.lval(L[0]) == -1:
                        keep.extend(ws[idx + 1:])
                        self.watch[fl] = keep
                        return True
                    self.assign(L[0])
            self.watch[fl] = keep
        return False

    def backtrack(self, to):
        while len(self.trail) > to:
            del self.val[abs(self.trail.pop())]
        self.qhead = to

    def store(self, L):
        if self.top_conflict:
            return
        L = sorted(L, key=lambda l: self.lval(l) == -1)
        if any(self.lval(l) == 1 for l in L):
            self.clauses.append(L)
            return
        k = sum(1 for l in L if self.lval(l) != -1)
        self.clauses.append(L)
        if k == 0:
            self.top_conflict = True
            return
        if len(L) >= 2:
            c = len(self.clauses) - 1
            self.watch.setdefault(L[0], []).append(c)
            self.watch.setdefault(L[1], []).append(c)
        if k == 1:
            self.assign(L[0])
            if self.propagate():
                self.top_conflict = True

    def rup(self, L):
        if self.top_conflict:
            return True
        save = len(self.trail)
        for l in L:
            v = self.lval(l)
            if v == 1:
                self.backtrack(save)
                return True
            if v == 0:
                self.assign(-l)
        conflict = self.propagate()
        self.backtrack(save)
        return conflict


def normalize(L):
    s = list(dict.fromkeys(L))
    return None if any(-l in s for l in s) else s


def check(cnf_lines, proof_lines):
    ch, formula, adds, dels = Checker(), 0, 0, 0
    for dele, L in parse(cnf_lines):
        if dele:
            raise ValueError("deletion in formula")
        formula += 1
        L = normalize(L)
        if L is not None:
            ch.store(L)
    for dele, L in parse(proof_lines):
        if dele:
            dels += 1
            continue
        adds += 1
        L = normalize(L)
        if L is None:
            continue
        if not ch.rup(L):
            return {"status": "REJECTED", "failed_addition": adds}
        if not L:
            return {"status": "RUP_REFUTATION_VERIFIED", "formula_clauses": formula,
                    "additions_checked": adds, "deletions_ignored": dels}
        ch.store(L)
    return {"status": "NO_EMPTY_CLAUSE", "additions_checked": adds}
