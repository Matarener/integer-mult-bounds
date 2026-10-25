"""Наибольшее lost-free множество портов P112 (CP-SAT), с видимым прогрессом.

Что показывает экран:
  [время] НАЙДЕНО |S| = n   — решатель нашёл lost-free множество размера n (сохраняется в best-n.json)
  [время] граница <= B      — доказано, что больше B не бывает; если B опустится до 32, рекорд 32 — максимум
Цель: |S| >= 37 даёт декодер плоскостей дешевле 224. Остановить: Ctrl+C (лучшее найденное уже сохранено).
"""
import importlib.util, json, re, sys, time
from pathlib import Path
from ortools.sat.python import cp_model

HERE = Path(__file__).resolve().parent
ROOT = Path(r"D:\Math\integer-mult-bounds")
spec = importlib.util.spec_from_file_location("v", ROOT / "research/paired-plane-minrank-bracket-audit/verify.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
q, _, _ = V.load_model((ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes(),
                       (ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_bytes())
dot = V.parity_dot
N = 112
T0 = time.time()
LOG = open(HERE / "progress.log", "a", encoding="utf-8")


def say(msg):
    line = "[%s, %5.0f мин] %s" % (time.strftime("%H:%M:%S"), (time.time() - T0) / 60, msg)
    print(line, flush=True)
    LOG.write(line + "\n"); LOG.flush()


bits = lambda v: [i for i in range(9) if v >> i & 1]
m = cp_model.CpModel()
x = [m.NewBoolVar("x%d" % a) for a in range(N)]
z = [[m.NewBoolVar("z%d_%d" % (a, i)) for i in range(9)] for a in range(N)]


def parity(lits, odd, enforce=None):
    k = m.NewIntVar(0, len(lits), "")
    c = m.Add(sum(lits) == 2 * k + (1 if odd else 0))
    if enforce:
        c.OnlyEnforceIf(enforce)


for a in range(N):
    parity([z[a][i] for i in bits(q[a])], False)   # r_a . q_a = 0
    parity(z[a], True)                             # r_a . r_a = 1
edges = [(a, b) for a in range(N) for b in range(a + 1, N) if dot(q[a], q[b]) == 0]
for a, b in edges:
    en = [x[a], x[b]]
    parity([z[b][i] for i in bits(q[a])], False, en)
    parity([z[a][i] for i in bits(q[b])], False, en)
    p = []
    for i in range(9):
        v = m.NewBoolVar("")
        m.AddBoolAnd([z[a][i], z[b][i]]).OnlyEnforceIf(v)
        m.AddBoolOr([z[a][i].Not(), z[b][i].Not()]).OnlyEnforceIf(v.Not())
        p.append(v)
    parity(p, False, en)
nb = [frozenset(j for j in range(N) if j != i and dot(q[i], q[j]) == 0) for i in range(N)]
K5 = []
def grow(cl, cand):
    if len(cl) == 5:
        K5.append(cl); return
    for u in sorted(cand):
        if u > cl[-1]:
            grow(cl + [u], cand & nb[u])
for v in range(N):
    grow([v], frozenset(u for u in nb[v] if u > v))
for c in K5:
    m.Add(sum(x[a] for a in c) <= 4)
# resume: best saved solution as hint, best proven bound from the log as a constraint
bests = sorted(HERE.glob("best-*.json"), key=lambda p: int(p.stem.split("-")[1]))
hint_path = bests[-1] if bests else HERE / "hint-32.json"
hint = json.load(open(hint_path))
prev_bound = None
if (HERE / "progress.log").exists():
    for line in open(HERE / "progress.log", encoding="utf-8"):
        mm = re.search(r"<= (\d+)", line)
        if mm and ("граница" in line):
            b = int(mm.group(1)); prev_bound = b if prev_bound is None else min(prev_bound, b)
if prev_bound is not None:
    m.Add(sum(x) <= prev_bound)
for a in range(N):
    m.AddHint(x[a], 1 if str(a) in hint else 0)
    if str(a) in hint:
        for i in range(9):
            m.AddHint(z[a][i], hint[str(a)] >> i & 1)
import os
FIX = int(os.environ.get("LF_FIX", str(min(int(k) for k in hint))))
m.Add(x[FIX] == 1)   # symmetry breaking: one fixed port in S
for a in range(N):   # a port of S keeps at most 28 of its 52 q-orthogonal neighbours plane-orthogonal
    m.Add(sum(x[b] for b in nb[a]) <= 28).OnlyEnforceIf(x[a])
# lex-leader symmetry breaking (valid: the label set is port-transitive, symmetry.json):
# order ports with FIX first; require x >=_lex x o g for sampled group elements g (lex-max representative)
LEX = int(os.environ.get("LF_LEX", "120"))
if LEX and (HERE / "symmetry.json").exists():
    perms = json.load(open(HERE / "symmetry.json"))["perms"][:LEX]
    order = [FIX] + [a for a in range(N) if a != FIX]
    for g in perms:
        inv = [0] * N
        for a, b in enumerate(g):
            inv[b] = a
        u = [x[a] for a in order]                 # indicator of S
        w = [x[inv[a]] for a in order]            # indicator of g(S)
        eq = m.NewConstant(1)
        for k in range(N):
            m.Add(u[k] >= w[k]).OnlyEnforceIf(eq)
            if k == N - 1:
                break
            nxt = m.NewBoolVar("")
            # nxt == eq and (u_k == w_k)
            m.AddImplication(nxt, eq)
            m.Add(u[k] == w[k]).OnlyEnforceIf(nxt)
            diff = m.NewBoolVar("")
            m.Add(u[k] != w[k]).OnlyEnforceIf(diff)
            m.Add(u[k] == w[k]).OnlyEnforceIf(diff.Not())
            m.AddBoolOr([nxt, eq.Not(), diff])
            eq = nxt
    say("отсечение симметрий: %d элементов группы (lex-leader), порт %d первый" % (len(perms), FIX))
m.Maximize(sum(x))
say("модель готова: %d портов, %d пар, %d запретов на 5 попарно ортогональных" % (N, len(edges), len(K5)))
say("усиление: порт %d закреплён в S, у каждого порта S не больше 28 ортогональных соседей в S" % FIX)
say("продолжение: старт с %s (|S| = %d), уже доказанная граница <= %s; цель |S| >= 37" % (hint_path.name, len(hint), prev_bound))

state = {"bound": prev_bound, "best": len(hint)}


import threading
state_last = {"bound": None}


def heartbeat():
    while True:
        time.sleep(120)
        b = state_last["bound"] if state_last["bound"] is not None else state["bound"]
        say("работает: лучшее |S| = %d, текущая граница <= %s" % (state["best"], "?" if b is None else int(b)))


def on_log(line):
    m_b = re.search(r"#Bound\s+[\d.]+s\s+best:([\-\d.e+inf]+)\s+next:\[([\d.]+),([\d.]+)\]", line)
    if m_b:
        hi = float(m_b.group(3))
        state_last["bound"] = hi if state_last["bound"] is None else min(state_last["bound"], hi)
        if state["bound"] is None or hi < state["bound"]:
            state["bound"] = hi
            say("граница <= %d" % int(hi))


class Sol(cp_model.CpSolverSolutionCallback):
    def __init__(self):
        super().__init__()

    def on_solution_callback(self):
        n = int(round(self.ObjectiveValue()))
        if n > state["best"]:
            state["best"] = n
            S = {a: sum(self.Value(z[a][i]) << i for i in range(9)) for a in range(N) if self.Value(x[a])}
            json.dump({str(a): r for a, r in S.items()}, open(HERE / ("best-%d.json" % n), "w"))
            say("НАЙДЕНО |S| = %d (граница <= %d)" % (n, int(self.BestObjectiveBound())))


s = cp_model.CpSolver()
WORKERS = int(__import__("os").environ.get("LF_WORKERS", "4"))
s.parameters.num_workers = WORKERS
say("рабочих потоков: %d из %d (примерно %d%% процессора)" % (WORKERS, __import__("os").cpu_count(), 100 * WORKERS // __import__("os").cpu_count()))
s.parameters.log_search_progress = True
s.parameters.log_to_stdout = False
s.parameters.repair_hint = True
s.parameters.hint_conflict_limit = 100000
s.log_callback = on_log
if len(sys.argv) > 1:
    s.parameters.max_time_in_seconds = float(sys.argv[1])
threading.Thread(target=heartbeat, daemon=True).start()
st = s.Solve(m, Sol())
say("ИТОГ: %s, лучшее |S| = %s, граница <= %d" % (s.StatusName(st), state["best"], int(s.BestObjectiveBound())))
if st == cp_model.OPTIMAL:
    say("ДОКАЗАНО: максимум lost-free множества = %d" % state["best"])
