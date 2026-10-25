/* Forward RUP checker: every proof addition must be reverse-unit-propagation entailed by the CNF
 * and the additions before it; the proof must add the empty clause. No hints are read.
 *
 * Deletion lines ("d ...") are counted and ignored. That is sound: every stored clause is entailed
 * by the CNF (originals by definition, additions because each one passed its RUP check), so keeping
 * extra clauses can only make propagation stronger, never accept a non-entailed clause.
 * Propagation uses two watched literals over a persistent top-level trail; each check assumes the
 * negation of the candidate, propagates, and backtracks to the top level.
 *
 * Usage: rupcheck FORMULA.cnf PROOF.rup     (use "-" for the proof to read stdin)
 * Prints a receipt; exits 0 only when the empty clause is RUP-derived. Stops at the first failure.
 * Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { int *lits; int n; } Clause;
static Clause *cls; static long ncls, capcls;
static int nvars;
static int **watch; static int *wn, *wcap;          /* per literal: clause ids watching it */
static signed char *val;                            /* per variable: 0 unassigned, 1 true, -1 false */
static int *trail; static long tsz, qhead;
static int top_conflict;

static int lit(int x) { return x > 0 ? 2 * x : 2 * (-x) + 1; }      /* DIMACS literal -> index */
static int neg(int l) { return l ^ 1; }
static int lval(int l) { int v = val[l >> 1]; return (l & 1) ? -v : v; }
static void assign(int l) { val[l >> 1] = (l & 1) ? -1 : 1; trail[tsz++] = l; }

static void addwatch(int l, int c) {
    if (wn[l] == wcap[l]) { wcap[l] = wcap[l] ? 2 * wcap[l] : 4; watch[l] = realloc(watch[l], sizeof(int) * wcap[l]); }
    watch[l][wn[l]++] = c;
}

/* propagate from qhead; returns 1 on conflict */
static int propagate(void) {
    while (qhead < tsz) {
        int p = trail[qhead++], fl = neg(p);           /* fl just became false */
        int *ws = watch[fl], i = 0, j = 0, n = wn[fl];
        for (; i < n; i++) {
            int c = ws[i]; int *L = cls[c].lits;
            if (L[0] == fl) { L[0] = L[1]; L[1] = fl; }
            if (lval(L[0]) == 1) { ws[j++] = c; continue; }
            int found = 0;
            for (int k = 2; k < cls[c].n; k++)
                if (lval(L[k]) != -1) { L[1] = L[k]; L[k] = fl; addwatch(L[1], c); found = 1; break; }
            if (found) continue;
            ws[j++] = c;
            if (lval(L[0]) == -1) { for (i++; i < n; i++) ws[j++] = ws[i]; wn[fl] = j; return 1; }
            assign(L[0]);
        }
        wn[fl] = j;
    }
    return 0;
}

static void backtrack(long to) { while (tsz > to) { int l = trail[--tsz]; val[l >> 1] = 0; } qhead = to; }

/* store a clause (deduplicated, non-tautological) and keep the top level propagated */
static void store(int *L, int n) {
    if (top_conflict) return;
    if (ncls == capcls) { capcls = capcls ? 2 * capcls : 1 << 16; cls = realloc(cls, sizeof(Clause) * capcls); }
    int *c = malloc(sizeof(int) * (n ? n : 1)); memcpy(c, L, sizeof(int) * n);
    /* order: non-false literals first */
    int k = 0;
    for (int i = 0; i < n; i++) if (lval(c[i]) != -1) { int t = c[k]; c[k] = c[i]; c[i] = t; k++; }
    long id = ncls++; cls[id].lits = c; cls[id].n = n;
    for (int i = 0; i < n; i++) if (lval(c[i]) == 1) return;       /* satisfied at top level: watch any two */
    if (k == 0) { top_conflict = 1; return; }
    if (n >= 2) { addwatch(c[0], id); addwatch(c[1], id); }
    if (k == 1) { assign(c[0]); if (propagate()) top_conflict = 1; }
}

static int rup(int *L, int n) {
    if (top_conflict) return 1;
    long save = tsz;
    for (int i = 0; i < n; i++) {
        int v = lval(L[i]);
        if (v == 1) { backtrack(save); return 1; }
        if (v == 0) assign(neg(L[i]));
    }
    int conflict = propagate();
    backtrack(save);
    return conflict;
}

static int buf[1 << 20];
/* read one 0-terminated clause; returns length, -1 at EOF; sets *del for a "d" line */
static int readclause(FILE *f, int *del, long *line) {
    int n = 0, c, x, sign; *del = 0;
    for (;;) {
        c = getc(f);
        while (c == ' ' || c == '\n' || c == '\r' || c == '\t') { if (c == '\n') (*line)++; c = getc(f); }
        if (c == EOF) return n ? (fprintf(stderr, "unterminated clause\n"), exit(2), -1) : -1;
        if (c == 'c' || c == 'p') { while (c != '\n' && c != EOF) c = getc(f); (*line)++; continue; }
        if (c == 'd' && n == 0) { *del = 1; continue; }
        sign = 1; if (c == '-') { sign = -1; c = getc(f); }
        if (c < '0' || c > '9') { fprintf(stderr, "bad token at line %ld\n", *line); exit(2); }
        x = 0; while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = getc(f); }
        ungetc(c, f);
        if (x == 0) return n;
        if (x > nvars) { fprintf(stderr, "variable %d > %d\n", x, nvars); exit(2); }
        if (n == (int)(sizeof buf / sizeof *buf)) { fprintf(stderr, "clause too long\n"); exit(2); }
        buf[n++] = lit(sign * x);
    }
}

/* drop duplicate literals; return -1 for a tautology */
static int normalize(int *L, int n, int *mark) {
    int k = 0, taut = 0;
    for (int i = 0; i < n; i++) {
        if (mark[L[i]]) continue;
        if (mark[neg(L[i])]) taut = 1;
        mark[L[i]] = 1; L[k++] = L[i];
    }
    for (int i = 0; i < k; i++) mark[L[i]] = 0;
    return taut ? -1 : k;
}

int main(int argc, char **argv) {
    if (argc != 3) { fprintf(stderr, "usage: rupcheck FORMULA.cnf PROOF.rup\n"); return 2; }
    FILE *f = fopen(argv[1], "r"); if (!f) { perror("cnf"); return 2; }
    long header_clauses = -1; char hdr[256];
    while (fgets(hdr, sizeof hdr, f)) if (hdr[0] == 'p') { if (sscanf(hdr, "p cnf %d %ld", &nvars, &header_clauses) != 2) return 2; break; }
    if (header_clauses < 0) { fprintf(stderr, "no header\n"); return 2; }
    val = calloc(nvars + 1, 1); trail = malloc(sizeof(int) * (nvars + 1));
    watch = calloc(2 * nvars + 2, sizeof(int *)); wn = calloc(2 * nvars + 2, sizeof(int)); wcap = calloc(2 * nvars + 2, sizeof(int));
    int *mark = calloc(2 * nvars + 2, sizeof(int));
    long line = 0, read_cls = 0, tauts = 0; int del, n;
    while ((n = readclause(f, &del, &line)) >= 0) {
        if (del) { fprintf(stderr, "deletion in formula\n"); return 2; }
        read_cls++;
        n = normalize(buf, n, mark);
        if (n < 0) { tauts++; continue; }
        store(buf, n);
    }
    fclose(f);
    if (read_cls != header_clauses) { fprintf(stderr, "clause count %ld != header %ld\n", read_cls, header_clauses); return 2; }
    FILE *p = strcmp(argv[2], "-") ? fopen(argv[2], "r") : stdin; if (!p) { perror("proof"); return 2; }
    long adds = 0, dels = 0, proof_line = 0, empty_at = -1, total_lits = 0;
    while ((n = readclause(p, &del, &proof_line)) >= 0) {
        if (del) { dels++; continue; }
        adds++;
        int m = normalize(buf, n, mark);
        if (m < 0) continue;                                   /* tautologies are entailed */
        if (!rup(buf, m)) {
            printf("{\"status\": \"REJECTED\", \"failed_addition\": %ld, \"proof_line\": %ld}\n", adds, proof_line);
            return 1;
        }
        total_lits += m;
        if (m == 0) { empty_at = adds; break; }
        store(buf, m);
    }
    printf("{\"status\": \"%s\", \"variables\": %d, \"formula_clauses\": %ld, \"formula_tautologies\": %ld, "
           "\"additions_checked\": %ld, \"deletions_ignored\": %ld, \"addition_literals\": %ld, \"empty_clause_at_addition\": %ld}\n",
           empty_at >= 0 ? "RUP_REFUTATION_VERIFIED" : "NO_EMPTY_CLAUSE", nvars, read_cls, tauts, adds, dels, total_lits, empty_at);
    return empty_at >= 0 ? 0 : 1;
}
