/* Independent second enumerator (different arithmetic and symmetry).
   Points are base-3 integers; addition uses a digit-wise table.  Pair sums
   are marked; a mask is served when mask - q_c is a marked pair sum.
   Symmetry: labels in first-occurrence order, and the path is rotated so
   that its last event differs from its first (always possible for n >= 2).
   Sharding splits at depth 8, so it needs 3n > 8.
   Usage: independent n nshards shard */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
static int n, L, NS, SH, P3, path[24], cnt[8], used;
static uint64_t leaves, sols, ctr;
static int add_tab[2187][2187];
static int pw[8], binmask3[256];
static int addv(int a, int b) {
    int r = 0;
    for (int j = 0; j < n; j++) r += ((a / pw[j] % 3 + b / pw[j] % 3) % 3) * pw[j];
    return r;
}
static int sub_tab[2187][2187];
static uint32_t stampv[2187], gen;
static int order[128];
static int check(void) {
    int q[24]; q[0] = 0;
    for (int t = 1; t < L; t++) q[t] = add_tab[q[t - 1]][pw[path[t - 1]]];
    gen++;
    for (int a = 0; a < L; a++)
        for (int b = a; b < L; b++) stampv[add_tab[q[a]][q[b]]] = gen;
    for (int k = 0; k < (1 << n) - 1; k++) {   /* mask = q_a + q_b + q_c iff mask - q_c is a pair sum */
        int m = binmask3[order[k]], ok = 0;
        for (int c = 0; c < L && !ok; c++) ok = stampv[sub_tab[m][q[c]]] == gen;
        if (!ok) return 0;
    }
    return 1;
}
static void rec(int t) {
    if (t == 8 && (ctr++ % NS) != (uint64_t)SH) return;
    if (t == L) {
        if (path[L - 1] == path[0]) return;
        leaves++;
        if (check()) { sols++; if (sols <= 5) { printf("SOLUTION"); for (int i = 0; i < L; i++) printf(" %d", path[i]); printf("\n"); } }
        return;
    }
    int top = used < n ? used + 1 : n;
    for (int s = 0; s < top; s++) {
        if (cnt[s] == 3) continue;
        int ou = used; if (s == used) used++;
        cnt[s]++; path[t] = s; rec(t + 1); cnt[s]--; used = ou;
    }
}
int main(int argc, char **argv) {
    if (argc != 4) { fprintf(stderr, "usage: independent n nshards shard\n"); return 2; }
    n = atoi(argv[1]); NS = atoi(argv[2]); SH = atoi(argv[3]); L = 3 * n;
    if (n < 2 || n > 7 || NS < 1 || SH < 0 || SH >= NS) return 2;
    P3 = 1; for (int j = 0; j < n; j++) { pw[j] = P3; P3 *= 3; }
    for (int a = 0; a < P3; a++) for (int b = 0; b < P3; b++) add_tab[a][b] = addv(a, b);
    for (int a = 0; a < P3; a++) for (int b = 0; b < P3; b++) sub_tab[addv(a, b)][b] = a;
    { int k = 0; for (int w = n; w >= 1; w--) for (int m = 1; m < (1 << n); m++) if (__builtin_popcount(m) == w) order[k++] = m; }
    for (int m = 0; m < (1 << n); m++) { int r = 0; for (int j = 0; j < n; j++) if (m >> j & 1) r += pw[j]; binmask3[m] = r; }
    rec(0);
    printf("RESULT n=%d shard=%d/%d leaves=%llu solutions=%llu\n", n, SH, NS, (unsigned long long)leaves, (unsigned long long)sols);
    return 0;
}
