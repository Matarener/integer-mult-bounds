#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay of the partial P112 decoder-wall package (results a-e of README.md), end to end.

The orchestrator is standard library only.  The vendored checks it runs need numpy, pynauty (orbit enumeration), a C compiler,
kissat and drat-trim (SAT/DRAT items), and scipy + networkx (optional CT8 orbits 3 and 4).  See README.md for how to get them.

  python3 -I -B verify.py [--jobs N] [--only a,b,..] [--work DIR] [--out DIR] [--no-ct8-dfs] [--allow-missing]
Groups (default all):  fw  im8  corea  coreb  ct8  coversat
  --jobs N   parallel chains (default: $HEAVY_THREADS, else 1).  Serial total about 2 h; with 4 jobs about 50 min.
  --skip-cuts   skip the COVERSAT cut-stage shards (data/coversat_cut_shards.json; 6-110 MB CNFs, a few minutes each)
Environment: DRAT_TRIM, KISSAT (paths; else found on PATH).
Prints PASS_P112_DECODER_WALL_PARTIAL on success; writes <out>/receipt.json.
"""
from __future__ import annotations

import argparse, concurrent.futures as cf, hashlib, json, lzma, os, re, shutil, subprocess, sys, tempfile, threading, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "src"
T0 = time.time()
LOCK = threading.Lock()
RESULTS: list[dict] = []          # one record per step
ap = argparse.ArgumentParser()
ap.add_argument("--jobs", type=int, default=int(os.environ.get("HEAVY_THREADS", "1") or 1))
ap.add_argument("--only", default="")
ap.add_argument("--work", default="")
ap.add_argument("--out", default="")
ap.add_argument("--no-ct8-dfs", action="store_true")
ap.add_argument("--skip-cuts", action="store_true", help="skip the COVERSAT cut-stage shards (stage 1 only)")
ap.add_argument("--allow-missing", action="store_true")
ARGS = ap.parse_args()
WORK = Path(ARGS.work) if ARGS.work else Path(tempfile.mkdtemp(prefix="wallpkg_"))
OUT = None if ARGS.out == "-" else (Path(ARGS.out) if ARGS.out else HERE / "data")
if OUT: OUT.mkdir(parents=True, exist_ok=True)
LOGS = WORK / "logs"; LOGS.mkdir(parents=True, exist_ok=True)
if not (WORK / "src").exists():
    shutil.copytree(SRC, WORK / "src", ignore=shutil.ignore_patterns("__pycache__"))
W = WORK / "src"
PY = sys.executable


def say(msg: str) -> None:
    with LOCK:
        print(f"[{time.time() - T0:7.1f}s] {msg}", flush=True)


def tool(name: str, env: str | None = None) -> str | None:
    return (os.environ.get(env) if env else None) or shutil.which(name)


KISSAT = tool("kissat", "KISSAT")
DRAT = tool("drat-trim", "DRAT_TRIM")
CC = tool("cc") or tool("gcc") or tool("clang")


def have_mod(m: str) -> bool:
    r = subprocess.run([PY, "-I", "-c", f"import {m}"], capture_output=True)
    return r.returncode == 0


NEEDS = {"fw": ["numpy", "pynauty", "cc"], "im8": ["numpy", "kissat", "drat-trim"],
         "corea": ["numpy", "pynauty"], "coreb": ["numpy"], "ct8": [], "coversat": ["kissat", "drat-trim"]}


def clean(text: str) -> str:
    return text.replace(str(WORK), "<work>")


def record(group, name, status, secs, detail=""):
    rec = dict(group=group, step=name, status=status, seconds=round(secs, 1), detail=detail)
    with LOCK:
        RESULTS.append(rec)
    say(f"{group:8s} {name:34s} {status:8s} {secs:7.1f}s  {detail}")
    return status == "PASS"


def run(group, name, argv, cwd, expect=(), check=None, timeout=3600, env=None, ok_codes=(0,), save=True):
    """Run one step; PASS iff exit code in ok_codes, every regex in `expect` occurs, and check(output) returns no problem."""
    t = time.time(); argv = [str(a) for a in argv]
    e = dict(os.environ); e.update(env or {})
    pr = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=e, start_new_session=True)
    try:
        out, _ = pr.communicate(timeout=timeout); code = pr.returncode
    except subprocess.TimeoutExpired:
        try: os.killpg(pr.pid, 9)          # our own child process group only
        except OSError: pass
        out, _ = pr.communicate(); out = (out or "") + "\n[timeout]"; code = -9
    out = clean(out)
    if save:
        (LOGS / (re.sub(r"[^A-Za-z0-9_.-]+", "_", f"{group}_{name}") + ".log")).write_text(out)
    problems = []
    if code not in ok_codes:
        problems.append(f"exit {code}")
    for rx in expect:
        if not re.search(rx, out):
            problems.append(f"missing /{rx}/")
    if check and not problems:
        problems += check(out) or []
    ok = not problems
    record(group, name, "PASS" if ok else "FAIL", time.time() - t, "; ".join(problems)[:300])
    return ok, out


def pyrun(group, name, script, args=(), cwd=None, **kw):
    return run(group, name, [PY, "-I", "-B", script, *map(str, args)], cwd or str(Path(script).parent), **kw)


def table(out, rx):
    return re.findall(rx, out)


# --------------------------------------------------------------------------------------------------------------------
# (a) FULLWALL: every P112 decoder with m <= 8 terms costs >= 64
def group_fw():
    g = "fw"; d = str(W / "fullwall")
    if not pyrun(g, "base: 1260 frames, labels, Bd form", f"{d}/base.py", expect=[r"frames 1260 labels distinct 112"])[0]:
        return
    ORB = [1, 5, 24, 98, 193, 141, 50, 10, 1]; SUMS = [112, 6216, 155092, 1557690, 2783900, 763987, 43173, 510, 1]

    def chk_orb(out):
        rows = [(int(a), int(b), int(c)) for a, b, c in table(out, r"dim (\d+) orbits (\d+) subspaces (\d+)")]
        return [] if [(i + 1, ORB[i], SUMS[i]) for i in range(9)] == rows else [f"orbit census {rows}"]
    ok, _ = pyrun(g, "xorb: label-closed subspace orbits (pynauty)", f"{d}/xorb.py", check=chk_orb)
    if not ok:
        return
    # independent C count of ALL label-spanned subspaces, must equal the orbit-size sums
    pyrun(g, "labels.txt", f"{d}/mklabels.py", cwd=d)
    ok, _ = run(g, "cc cntsub.c", [CC, "-O2", "-o", "cntsub", "cntsub.c"], d)
    if ok:
        def chk_cnt(out):
            rows = [int(b) for a, b in table(out, r"dim (\d+) label-spanned (\d+)")]
            return [] if rows[1:] == SUMS else [f"C counts {rows}"]
        run(g, "cntsub: independent subspace count", ["./cntsub"], d, check=chk_cnt)
    COST = [1584, 8860, 17558, 13276, 4598, 832, 99, 3, 1]

    def chk_rect(out):
        rows = {int(a): int(b) for a, b in table(out, r"cost (\d+) orbits (\d+)")}
        return [] if [rows.get(c) for c in range(1, 10)] == COST else [f"rect census {rows}"]
    ok, _ = pyrun(g, "rect2: maximal rectangles up to Aut x T", f"{d}/rect2.py", check=chk_rect)
    if not ok:
        return
    ok1, _ = pyrun(g, "m8: R1+R2 kill all rectangles of cost <= 7", f"{d}/m8.py",
                   expect=[r"cost<=7 maximal rectangles surviving R1\+R2: 0"])
    ok2, _ = pyrun(g, "xcheck_m8: independent raw-rectangle check", f"{d}/xcheck_m8.py", expect=[r"XCHECK_M8 PASS 510583"])


# --------------------------------------------------------------------------------------------------------------------
# (b) INT-M8: MIX-8
def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def group_im8():
    g = "im8"; d = str(W / "intm8")
    pyrun(g, "lsplit: level-split identity", f"{d}/lsplit.py", expect=[r"LSPLIT PASS 2000"])
    shas = {}
    for line in Path(d, "shas.txt").read_text().split("\n"):
        if line.strip():
            h, n = line.split(); shas[n] = h
    # step A (no extra zero): regenerate CNF, compare sha, check the shipped DRAT proof with drat-trim
    ok, _ = pyrun(g, "rigz50: regenerate CNF", f"{d}/rigz.py", ["rigz50.cnf", 50, 1], cwd=d)
    if ok:
        got = sha_file(f"{d}/rigz50.cnf"); want = shas["rigz50.cnf"]
        record(g, "rigz50.cnf sha256", "PASS" if got == want else "FAIL", 0, got[:16])
        with lzma.open(f"{d}/rigz50.drat.xz") as fi, open(f"{d}/rigz50.drat", "wb") as fo:
            shutil.copyfileobj(fi, fo)
        run(g, "rigz50: drat-trim on shipped proof", [DRAT, "rigz50.cnf", "rigz50.drat", "-t", "3000"], d, expect=[r"s VERIFIED"])
        os.remove(f"{d}/rigz50.drat")
    # step B (the tie): two independent generators, kissat UNSAT + drat-trim
    for nm, script, extra, env in (("tie8nm", "tie8.py", [], {"NEARMISS": "1"}), ("xtie8", "xtie8.py", [], {})):
        ok, _ = pyrun(g, f"{nm}: generate CNF", f"{d}/{script}", [f"{nm}.cnf", *extra], cwd=d, env=env)
        if not ok:
            continue
        got = sha_file(f"{d}/{nm}.cnf"); record(g, f"{nm}.cnf sha256", "PASS" if got == shas[f"{nm}.cnf"] else "FAIL", 0, got[:16])
        run(g, f"{nm}: kissat UNSAT", [KISSAT, "-q", f"{nm}.cnf", f"{nm}.drat"], d, ok_codes=(20,))
        run(g, f"{nm}: drat-trim", [DRAT, f"{nm}.cnf", f"{nm}.drat", "-t", "3000"], d, expect=[r"s VERIFIED"])
        for f in (f"{nm}.cnf", f"{nm}.drat"):
            if os.path.exists(f"{d}/{f}"): os.remove(f"{d}/{f}")
    ok, _ = pyrun(g, "xtie8 control (no disjointness)", f"{d}/xtie8.py", ["xtie8_nod.cnf", "nod"], cwd=d)
    if ok:
        run(g, "control: kissat SAT", [KISSAT, "-q", "xtie8_nod.cnf"], d, ok_codes=(10,))


# --------------------------------------------------------------------------------------------------------------------
# (c) CORE3 + CORE-RES
def group_corea():
    g = "corea"; d3 = str(W / "core3"); dr = str(W / "coreres")
    if not pyrun(g, "mkaut: Aut(Bd) = 172,032 permutations", f"{d3}/mkaut.py", expect=[r"G built \(172032, 112\)"])[0]:
        return
    FLAT = [1, 1, 5, 16, 51, 91, 105, 41, 1]

    def chk_flats(out):
        rows = [(int(a), int(b)) for a, b in table(out, r"rank (\d) flat orbits (\d+)")]
        r0 = table(out, r"rank 0 orbits (\d+)")
        bad = []
        if rows != [(r, FLAT[r]) for r in range(1, 9)]: bad.append(f"flat orbits {rows}")
        return bad
    ok, _ = pyrun(g, "flats: all flats of the line matroid up to Aut", f"{d3}/flats.py", [8], cwd=d3,
                  expect=[r"signed-linear: OK", r"exact flat re-verification: bad = 0", r"m8 \(codim-1 max lines\) 64  m7 \(codim-2\) 36  m6 \(codim-3\) 20"],
                  check=chk_flats)
    if not ok:
        return
    ok, _ = pyrun(g, "stats: label statistics of H^c(q)", f"{d3}/stats.py", cwd=d3,
                  expect=[r"I1 max \|Z\| over rank-7 flats .*: 59", r"I3 min D over rank-7 flats: 8"])
    if not ok:
        return
    pyrun(g, "core3: V1, V2, V3", f"{d3}/core3.py", cwd=d3,
          expect=[r"V1 failures: 0", r"V3 danger configs x ratios checked: 172032 .*MIN = 2"])

    def chk_s4(out):
        bad = []
        for h, cnt in ((2, 28672), (3, 229376), (4, 229376), (5, 0)):
            if not re.search(rf"Part A h={h}: configs {cnt}, failures 0", out): bad.append(f"Part A h={h}")
        losses = table(out, r"loss distribution over 7-dim Y: (\[.*\])")
        if not losses: bad.append("no Part B lines")
        for L in losses:
            if any(int(k) > 1 for k, _ in eval(L, {"__builtins__": {}})): bad.append("loss > 1")
        return bad
    pyrun(g, "s4: Part A (hurt configurations), Part B (losses)", f"{d3}/s4.py", cwd=d3, check=chk_s4)
    pyrun(g, "xcheck: independent V0-V3 (G2 form)", f"{d3}/xcheck.py", cwd=d3,
          expect=[r"orbits per rank \[1, 1, 5, 16, 51, 91, 105, 41\]", r"V0 max \|Z\| on rank-7 flats: 59", r"V1 failures: 0",
                  r"do NOT span Q\^8: 0"])
    ok, _ = pyrun(g, "lossy: lossy flats for every 7-dim Y", f"{dr}/lossy.py", cwd=dr)
    if ok:
        pyrun(g, "star: A_{m-1} star + N-part, h in {0,1} only", f"{dr}/star.py", cwd=dr, check=chk_star)
        pyrun(g, "a8star: A8 CSP (960 simplices)", f"{dr}/a8star.py", cwd=dr,
              expect=[r"A8 subsystems with a consistent \(Y_k\) assignment: 0"])


def chk_star(out):
    m = re.search(r"by h: (\[.*\])", out)
    if not m: return ["no 'by h' line"]
    hs = [h for h, _ in eval(m.group(1), {"__builtins__": {}})]
    return [] if all(h in (0, 1) for h in hs) else [f"survivors with h not in 0,1: {hs}"]


def group_coreb():
    g = "coreb"; dr = str(W / "coreres")
    pyrun(g, "r8bin: R8 binomial/torus lattice (frame 0)", f"{dr}/r8bin.py", [0], cwd=dr, expect=[r"binomial equations 4608", r"rank of T' \(mod p\): 215", r"in the kernel of every binomial exponent vector: OK"])
    pyrun(g, "xr8: independent R8 lattice, own geometry", f"{dr}/xr8.py", cwd=dr, expect=[r"XCHECK PASS", r"det = 1"])
    pyrun(g, "kcsp: K7-vertex CSP", f"{dr}/kcsp.py", cwd=dr, expect=[r"h 0 : simplices 960 with a consistent K7 assignment: 0"])
    pyrun(g, "xa2: independent functional-based CSP", f"{dr}/xa2.py", cwd=dr,
          expect=[r"\(X4\+X5\) h=0,1: simplices 1248 surviving arc consistency: 0"])

    def chk_pa(out):
        return [] if all(re.search(rf"h={h} configs {c} failures 0", out) for h, c in ((2, 28672), (3, 229376), (4, 229376), (5, 0))) else ["Part A counts"]
    pyrun(g, "xpartA: independent Part A (stdlib)", f"{dr}/xpartA.py", cwd=dr, check=chk_pa)


# --------------------------------------------------------------------------------------------------------------------
# (e) CT8
def group_ct8():
    g = "ct8"; d = str(W / "ct8"); dd = HERE / "data"
    for o in (2, 5):
        pyrun(g, f"orbit {o}: exact LP-dual certificate (stdlib)", f"{d}/dual_check.py", [o, str(dd / f"ct8_orbit{o}_dual.json")], cwd=d,
              expect=[rf"DUAL_CERT_OK orbit {o}"])
    if ARGS.no_ct8_dfs:
        return
    if not (have_mod("scipy") and have_mod("networkx") and have_mod("numpy")):
        record(g, "orbits 3,4 (LP+DFS)", "SKIPPED", 0, "needs numpy, scipy, networkx"); return
    pyrun(g, "orbit 3: LP bound + exact DFS (scipy)", f"{d}/certify.py", [3, "SA", 7], cwd=d, timeout=3000,
          expect=[r"feasible multisets 0"])
    pyrun(g, "orbit 4: LP bound + exact DFS (scipy)", f"{d}/certify.py", [4, "SA", 7], cwd=d, timeout=3000,
          expect=[r"feasible multisets 0"])


# --------------------------------------------------------------------------------------------------------------------
# (d) COVERSAT stage 1 (pure cover model), orbits 0,1,3,4
def shard_task(o, lam, sha=None):
    d = str(W / "coversat")
    name = f"o{o}_b7_{''.join(map(str, lam))}"
    ok, out = run("coversat", name, [PY, "-I", "-B", f"{d}/shard.py", o, ",".join(map(str, lam)), str(WORK / "cs_tmp")] + (["--sha", sha] if sha else []), d,
                  expect=[r"UNSAT VERIFIED"], timeout=3500, save=False)
    return ok


def stage1_list():
    snap = json.loads((HERE / "data" / "coversat_snapshot.json").read_text())
    return [(s["orbit"], s["lam"], s.get("sha256")) for s in snap["stage1"] if s["claimed"] == "DRAT"]


# --------------------------------------------------------------------------------------------------------------------
def main():
    only = set(ARGS.only.split(",")) if ARGS.only else None
    miss = []
    have = {"numpy": have_mod("numpy"), "pynauty": have_mod("pynauty"), "cc": bool(CC), "kissat": bool(KISSAT), "drat-trim": bool(DRAT)}
    say("tools: " + ", ".join(f"{k}={'yes' if v else 'NO'}" for k, v in have.items()) + f"; python {sys.version.split()[0]}; jobs {ARGS.jobs}")
    chains = {"fw": group_fw, "im8": group_im8, "corea": group_corea, "coreb": group_coreb, "ct8": group_ct8}
    tasks = []
    for k, fn in chains.items():
        if only and k not in only: continue
        lack = [n for n in NEEDS[k] if not have.get(n, True)]
        if lack:
            record(k, "(group)", "MISSING", 0, "needs " + ", ".join(lack)); miss.append(k); continue
        tasks.append((k, fn))
    if not only or "coversat" in only:
        lack = [n for n in NEEDS["coversat"] if not have.get(n, True)]
        if lack:
            record("coversat", "(group)", "MISSING", 0, "needs " + ", ".join(lack)); miss.append("coversat")
        else:
            for (o, lam, sha) in stage1_list():
                tasks.append(("coversat", (lambda o=o, lam=lam, sha=sha: shard_task(o, lam, sha))))
            if not ARGS.skip_cuts:
                for sh in cut_list():
                    tasks.append(("coversat", (lambda sh=sh: cut_task(sh))))
    say("scheduled: " + ", ".join(sorted({k for k, _ in tasks})) + f" ({len(tasks)} tasks)")
    # long chains first
    order = {"fw": 0, "corea": 1, "coreb": 2, "im8": 3, "ct8": 4, "coversat": 5}
    tasks.sort(key=lambda t: order[t[0]])
    with cf.ThreadPoolExecutor(max_workers=max(1, ARGS.jobs)) as ex:
        futs = [ex.submit(fn) for _, fn in tasks]
        for f in futs:
            try: f.result()
            except Exception as e:  # a crashed chain is a failure, not a pass
                record("harness", "exception", "FAIL", 0, repr(e)[:200])
    total = time.time() - T0
    bad = [r for r in RESULTS if r["status"] not in ("PASS",)]
    optional_ok = all(r["status"] in ("PASS", "SKIPPED") for r in RESULTS)
    summary = summarise()
    receipt = dict(package="p112-decoder-wall-partial", python=sys.version.split()[0], jobs=ARGS.jobs, seconds=round(total, 1),
                   tools={k: bool(v) for k, v in have.items()}, steps=RESULTS, results=summary, only=sorted(only) if only else "all")
    if OUT: (OUT / ("receipt_partial.json" if only else "receipt.json")).write_text(json.dumps(receipt, indent=1))
    n = {s: sum(1 for r in RESULTS if r["status"] == s) for s in ("PASS", "FAIL", "MISSING", "SKIPPED")}
    say(f"steps: {n}; wall {total:.0f}s")
    for line in summary: say("  " + line)
    if bad and not (ARGS.allow_missing and all(r["status"] in ("MISSING", "SKIPPED") for r in bad)):
        say("FAILED: " + "; ".join(f"{r['group']}/{r['step']}={r['status']}" for r in bad)); sys.exit(1)
    say("PASS_P112_DECODER_WALL_PARTIAL" if not only else "PASS_SELECTED_GROUPS")


def cut_list():
    spec = json.loads((HERE / "data" / "coversat_cut_shards.json").read_text())
    return [dict(sh, pool=spec["pools"][str(sh["orbit"])][: sh["npool"]]) for sh in spec["shards"] if sh["status"] in ("cut-DRAT", "cut+certified-nogood") and sh["orbit"] != 2]


def cut_task(sh):
    d = str(W / "coversat"); pf = WORK / f"pool_{sh['name']}.json"
    pf.write_text(json.dumps(sh["pool"]))
    extra = []
    if sh.get("certs"):
        cf_ = WORK / f"certs_{sh['name']}.json"
        cf_.write_text(json.dumps([str(HERE / "data" / "coversat_certs" / c) for c in sh["certs"]])); extra = ["--certs", str(cf_)]
    ok, _ = run("coversat", sh["name"] + (" (cuts+certs)" if extra else " (cuts)"), [PY, "-I", "-B", f"{d}/shard.py", sh["orbit"], ",".join(map(str, sh["lam"])), str(WORK / "cs_tmp"),
                "--cuts", str(pf), "--it", sh["it"]] + (["--sha", sh["sha256"]] if sh.get("sha256") and not extra else []) + extra, d, expect=[r"UNSAT VERIFIED"], timeout=3500, save=False)
    return ok


def summarise():
    def st(group, prefix=None):
        rs = [r for r in RESULTS if r["group"] == group and (prefix is None or r["step"].startswith(prefix))]
        if not rs: return "NOT RUN"
        return "PASS" if all(r["status"] == "PASS" for r in rs) else "INCOMPLETE/FAIL"
    return [f"(a) FULLWALL m<=8 >= 64: {st('fw')}",
            f"(b) INT-M8 MIX-8: {st('im8')}",
            f"(c) CORE3 + CORE-RES (rank M = 8, m = 9): {st('corea')} / {st('coreb')}",
            f"(d) COVERSAT DRAT shards (stage 1 + cut model): {st('coversat')}",
            f"(e) CT8 orbits 2,5 (dual) + 3,4 (DFS): {st('ct8')}"]


if __name__ == "__main__":
    main()
