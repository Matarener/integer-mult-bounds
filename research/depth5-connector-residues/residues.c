/* Exact residue sets of the depth-five chain connector for one call-count vector, mod M.
 *
 * Calls l and k commute when |l - k| >= 2, so a word's interval counts N[i..j] (Lemma 1 of #4281)
 * depend only on: the subword M of calls 2, 3, 4; for each call 1, the number a of calls 2 before
 * it; for each call 5, the number b of calls 4 before it. With, for every call 3 in M, k2 = calls 2
 * before it and k4 = calls 4 before it:
 *   N12 = sum (n2 - a),  N13 = sum_a sum_3 (k2-a)+,          N14 = sum_a sum_3 (k2-a)+ (n4-k4)
 *   N45 = sum b,         N35 = sum_b sum_3 (b-k4)+,          N25 = sum_b sum_3 k2 (b-k4)+
 *   N23 = sum_3 k2,      N34 = sum_3 (n4-k4)... over 4s,     N24 = sum_3 k2 (n4-k4)
 *   N15 = sum_a sum_b h(a,b),  h(a,b) = sum_3 (k2-a)+ (b-k4)+.
 * The word is correct for c iff every N is 0 mod M except N15 = c (and every n_l = 0 mod M).
 * This program enumerates every M and every multiset of levels, prints the set of reachable c and
 * one witness word per reachable c.  Build: cc -O2 -DM=5 -o residues residues.c
 * Run: ./residues n1 n2 n3 n4 n5 [target residues...]; with targets it stops once all are found
 * and the reported set is then partial (marked STOPPED_AT_TARGETS).
 * Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 16
static int n1, n2, n3, n4, n5;
static int mid[3 * MAXN], mlen;
static int found[M]; static char wit[M][8 * MAXN];
static long long mids_total, mids_pass;
static int done_early;
static int want[M], nwant, nfound_want;

/* per M */
static int nt, K2[MAXN], K4[MAXN];
static int f3[MAXN + 1], f4[MAXN + 1], g3[MAXN + 1], g2[MAXN + 1], h[MAXN + 1][MAXN + 1];

static int ones[MAXN], fives[MAXN];
/* distinct H vectors with one representative level multiset */
#define MAXH 4096
static int nh, Hv[MAXH][MAXN + 1], Hrep[MAXH][MAXN];
static int nf, Frep[1 << 14][MAXN];

static int md(long v) { v %= M; return v < 0 ? (int)v + M : (int)v; }

static void witness(int c, const int *A, const int *Bv) {
    char *w = wit[c]; int k = 0, p2 = 0, q4 = 0;
    for (int i = 0; i < n5; i++) if (Bv[i] == 0) w[k++] = '5';
    for (int t = 0; t < mlen; t++) {
        int x = mid[t];
        if (x == 2) { for (int i = 0; i < n1; i++) if (A[i] == p2) w[k++] = '1'; p2++; }
        w[k++] = (char)('0' + x);
        if (x == 4) { q4++; for (int i = 0; i < n5; i++) if (Bv[i] == q4) w[k++] = '5'; }
    }
    for (int i = 0; i < n1; i++) if (A[i] == n2) w[k++] = '1';
    w[k] = 0;
}

static void ones_rec(int i, int lo, long s12, long s13, long s14) {
    if (i == n1) {
        if (md(s12) || md(s13) || md(s14)) return;
        int H[MAXN + 1];
        for (int b = 0; b <= n4; b++) { long s = 0; for (int j = 0; j < n1; j++) s += h[ones[j]][b]; H[b] = md(s); }
        for (int k = 0; k < nh; k++) if (!memcmp(Hv[k], H, sizeof(int) * (n4 + 1))) return;
        if (nh == MAXH) { fprintf(stderr, "MAXH\n"); exit(2); }
        memcpy(Hv[nh], H, sizeof(int) * (n4 + 1)); memcpy(Hrep[nh], ones, sizeof(int) * n1); nh++;
        return;
    }
    for (int a = lo; a <= n2; a++) { ones[i] = a; ones_rec(i + 1, a, s12 + (n2 - a), s13 + f3[a], s14 + f4[a]); }
}

static void fives_rec(int i, int lo, long s45, long s35, long s25) {
    if (i == n5) {
        if (md(s45) || md(s35) || md(s25)) return;
        if (nf == (1 << 14)) { fprintf(stderr, "MAXF\n"); exit(2); }
        memcpy(Frep[nf++], fives, sizeof(int) * n5);
        return;
    }
    for (int b = lo; b <= n4; b++) { fives[i] = b; fives_rec(i + 1, b, s45 + b, s35 + g3[b], s25 + g2[b]); }
}

static void leaf(void) {
    mids_total++;
    int c2 = 0, c4 = 0; nt = 0; long N34 = 0;
    for (int t = 0; t < mlen; t++) {
        if (mid[t] == 2) c2++;
        else if (mid[t] == 3) { K2[nt] = c2; K4[nt] = c4; nt++; }
        else { c4++; }
    }
    long N23 = 0, N24 = 0;
    for (int k = 0; k < nt; k++) { N23 += K2[k]; N24 += (long)K2[k] * (n4 - K4[k]); N34 += n4 - K4[k]; }
    if (md(N23) || md(N34) || md(N24)) return;
    mids_pass++;
    for (int a = 0; a <= n2; a++) {
        long s3 = 0, s4 = 0;
        for (int k = 0; k < nt; k++) { int x = K2[k] - a; if (x > 0) { s3 += x; s4 += (long)x * (n4 - K4[k]); } }
        f3[a] = md(s3); f4[a] = md(s4);
    }
    for (int b = 0; b <= n4; b++) {
        long s3 = 0, s2 = 0;
        for (int k = 0; k < nt; k++) { int y = b - K4[k]; if (y > 0) { s3 += y; s2 += (long)K2[k] * y; } }
        g3[b] = md(s3); g2[b] = md(s2);
    }
    for (int a = 0; a <= n2; a++) for (int b = 0; b <= n4; b++) {
        long s = 0;
        for (int k = 0; k < nt; k++) { int x = K2[k] - a, y = b - K4[k]; if (x > 0 && y > 0) s += (long)x * y; }
        h[a][b] = md(s);
    }
    nh = 0; ones_rec(0, 0, 0, 0, 0);
    if (!nh) return;
    nf = 0; fives_rec(0, 0, 0, 0, 0);
    for (int k = 0; k < nh; k++)
        for (int f = 0; f < nf; f++) {
            long s = 0;
            for (int i = 0; i < n5; i++) s += Hv[k][Frep[f][i]];
            int c = md(s);
            if (!found[c]) { found[c] = 1; witness(c, Hrep[k], Frep[f]); if (want[c] && ++nfound_want == nwant) done_early = 1; }
        }
}

static void mid_rec(int r2, int r3, int r4) {
    if (done_early) return;
    if (!r2 && !r3 && !r4) { leaf(); return; }
    if (r2) { mid[mlen++] = 2; mid_rec(r2 - 1, r3, r4); mlen--; }
    if (r3) { mid[mlen++] = 3; mid_rec(r2, r3 - 1, r4); mlen--; }
    if (r4) { mid[mlen++] = 4; mid_rec(r2, r3, r4 - 1); mlen--; }
}

int main(int argc, char **argv) {
    if (argc < 6) return 2;
    for (int i = 6; i < argc; i++) { int c = atoi(argv[i]); if (c > 0 && c < M && !want[c]) { want[c] = 1; nwant++; } }
    n1 = atoi(argv[1]); n2 = atoi(argv[2]); n3 = atoi(argv[3]); n4 = atoi(argv[4]); n5 = atoi(argv[5]);
    if (n1 > MAXN || n2 > MAXN || n3 > MAXN || n4 > MAXN || n5 > MAXN) return 2;
    mid_rec(n2, n3, n4);
    printf("M=%d counts=%d,%d,%d,%d,%d middles=%lld passing=%lld %s reachable=", M, n1, n2, n3, n4, n5, mids_total, mids_pass, done_early ? "STOPPED_AT_TARGETS" : "COMPLETE");
    for (int c = 1; c < M; c++) if (found[c]) printf("%d,", c);
    printf("\n");
    for (int c = 1; c < M; c++) if (found[c]) printf("witness c=%d %s\n", c, wit[c]);
    return 0;
}
