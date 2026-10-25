/* Literal full-guard header census over GL_m(F_q), q in {2, 3, 4, 5}.
 *
 * A header G passes a request R when the leading principal minors of G R G^-1 of orders
 * 1..rank(R) are all nonzero (tested by elimination without pivoting). Every matrix over F_q
 * is enumerated; invertible ones are the headers. Families, in canonical bases (e_i unit vectors):
 *   pair     I - e1 e1^T, I - e2 e2^T                         (#4261, #4273)
 *   oneway   I - e1 (e1 + e2)^T, I - e2 e2^T                  (#4274)
 *   k3, k4   I - e_t e_t^T for t = 1..3 (resp. 1..4)          (#4275)
 *   laminar  e1 e1^T inside e1 e1^T + e2 e2^T                 (#4259)
 *   split    e1 e1^T + e2 e2^T with e1 e1^T and e2 e2^T       (#4259's binary obstruction)
 * Build: cc -O2 -o headers headers.c ; run: ./headers q m
 * Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXM 6
static int q, m, ADD[5][5], MUL[5][5], NEG[5], INV[5];

static void field(void) {
    for (int a = 0; a < q; a++)
        for (int b = 0; b < q; b++) {
            if (q == 4) {   /* GF(4) = {0, 1, x, x+1} as bit pairs, x^2 = x + 1 */
                ADD[a][b] = a ^ b;
                int p = 0, aa = a, bb = b;
                for (int i = 0; i < 2; i++) if (bb >> i & 1) p ^= aa << i;
                if (p & 4) p ^= 4 | 3;
                MUL[a][b] = p;
            } else { ADD[a][b] = (a + b) % q; MUL[a][b] = a * b % q; }
        }
    for (int a = 0; a < q; a++) {
        for (int b = 0; b < q; b++) if (ADD[a][b] == 0) NEG[a] = b;
        INV[a] = 0;
        for (int b = 0; b < q; b++) if (MUL[a][b] == 1) INV[a] = b;
    }
}

typedef int Mat[MAXM][MAXM];

static int inverse(Mat g, Mat out) {
    Mat a; memcpy(a, g, sizeof a);
    for (int i = 0; i < m; i++) for (int j = 0; j < m; j++) out[i][j] = i == j;
    for (int c = 0; c < m; c++) {
        int p = -1;
        for (int r = c; r < m; r++) if (a[r][c]) { p = r; break; }
        if (p < 0) return 0;
        for (int j = 0; j < m; j++) { int t = a[c][j]; a[c][j] = a[p][j]; a[p][j] = t; t = out[c][j]; out[c][j] = out[p][j]; out[p][j] = t; }
        int iv = INV[a[c][c]];
        for (int j = 0; j < m; j++) { a[c][j] = MUL[a[c][j]][iv]; out[c][j] = MUL[out[c][j]][iv]; }
        for (int r = 0; r < m; r++) {
            if (r == c || !a[r][c]) continue;
            int f = NEG[a[r][c]];
            for (int j = 0; j < m; j++) { a[r][j] = ADD[a[r][j]][MUL[f][a[c][j]]]; out[r][j] = ADD[out[r][j]][MUL[f][out[c][j]]]; }
        }
    }
    return 1;
}

static void mul(Mat x, Mat y, Mat out) {
    for (int i = 0; i < m; i++) for (int j = 0; j < m; j++) {
        int s = 0;
        for (int k = 0; k < m; k++) s = ADD[s][MUL[x[i][k]][y[k][j]]];
        out[i][j] = s;
    }
}

static int passes(Mat g, Mat gi, Mat r, int rank) {
    Mat t, a;
    mul(g, r, t); mul(t, gi, a);
    for (int k = 0; k < rank; k++) {             /* pivots of elimination without row exchanges */
        if (!a[k][k]) return 0;
        int iv = INV[a[k][k]];
        for (int i = k + 1; i < m; i++) {
            if (!a[i][k]) continue;
            int f = NEG[MUL[a[i][k]][iv]];
            for (int j = k; j < m; j++) a[i][j] = ADD[a[i][j]][MUL[f][a[k][j]]];
        }
    }
    return 1;
}

static void unit_proj(Mat r, int i) { memset(r, 0, sizeof(Mat)); r[i][i] = 1; }
static void minus_from_id(Mat r) {
    for (int i = 0; i < m; i++) for (int j = 0; j < m; j++) r[i][j] = ADD[i == j][NEG[r[i][j]]];
}

int main(int argc, char **argv) {
    if (argc != 3) return 2;
    q = atoi(argv[1]); m = atoi(argv[2]);
    if (q < 2 || q > 5 || m < 2 || m > MAXM) return 2;
    field();
    enum { NREQ = 8 };
    Mat R[NREQ]; int rk[NREQ];
    for (int t = 0; t < 4 && t < m; t++) { unit_proj(R[t], t); minus_from_id(R[t]); rk[t] = m - 1; }   /* I - e_t e_t^T */
    memset(R[4], 0, sizeof(Mat)); R[4][0][0] = 1; R[4][0][1] = 1; minus_from_id(R[4]); rk[4] = m - 1;   /* I - e1 (e1+e2)^T */
    unit_proj(R[5], 0); rk[5] = 1;                                                                       /* e1 e1^T */
    unit_proj(R[6], 1); rk[6] = 1;                                                                       /* e2 e2^T */
    memset(R[7], 0, sizeof(Mat)); R[7][0][0] = R[7][1][1] = 1; rk[7] = 2;                                /* e1 e1^T + e2 e2^T */
    long long gl = 0, c_pair = 0, c_oneway = 0, c_k3 = 0, c_k4 = 0, c_lam = 0, c_split = 0, c_one = 0;
    long long total = 1;
    for (int i = 0; i < m * m; i++) total *= q;
    Mat g, gi;
    for (long long code = 0; code < total; code++) {
        long long c = code;
        for (int i = 0; i < m; i++) for (int j = 0; j < m; j++) { g[i][j] = c % q; c /= q; }
        if (!inverse(g, gi)) continue;
        gl++;
        int p[NREQ];
        for (int t = 0; t < NREQ; t++) p[t] = (t < 4 && t >= m) ? 0 : -1;
        #define P(t) (p[t] < 0 ? (p[t] = passes(g, gi, R[t], rk[t])) : p[t])
        if (P(0)) c_one++;
        if (P(0) && P(1)) c_pair++;
        if (P(4) && P(1)) c_oneway++;
        if (m >= 3 && P(0) && P(1) && P(2)) c_k3++;
        if (m >= 4 && P(0) && P(1) && P(2) && P(3)) c_k4++;
        if (P(7) && P(5)) c_lam++;
        if (P(7) && P(5) && P(6)) c_split++;
    }
    printf("q=%d m=%d GL=%lld one=%lld pair=%lld oneway=%lld k3=%lld k4=%lld laminar=%lld split=%lld\n",
           q, m, gl, c_one, c_pair, c_oneway, c_k3, c_k4, c_lam, c_split);
    return 0;
}
