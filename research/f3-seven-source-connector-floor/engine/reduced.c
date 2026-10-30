/* Enumerate restored unsigned F3 connector source paths (n sources, each used
   three times) and decide whether one readout triple serves every nonzero
   binary mask.  Usage: reduced n nshards shard sym(0|1) [print_limit]
   sym=1: labels in first-occurrence order, source 0 at position 0, and the
   first gap of source 0 equal to the minimum cyclic gap of the path.
   sym=0: every path (no reduction), for cross-validation. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define MAXN 8
#define MAXL (3 * MAXN)

static int n, L, nshards, shard, sym, print_limit;
static int path[MAXL], cnt[MAXN], first[MAXN], last[MAXN];
static int used_labels, g0;
static uint64_t leaves, solutions, prefix_counter;
static uint32_t stamp[1 << (2 * MAXN)];
static uint32_t gen;
static int mask_order[1 << MAXN];
static int split_depth;

static inline void add3(int alo, int ahi, int blo, int bhi, int *clo, int *chi) {
    int an = ~(alo | ahi), bn = ~(blo | bhi);
    *clo = (alo & bn) | (blo & an) | (ahi & bhi);
    *chi = (ahi & bn) | (bhi & an) | (alo & blo);
}

static int check(void) {
    int lo[MAXL], hi[MAXL], full = (1 << n) - 1;
    lo[0] = hi[0] = 0;
    for (int t = 1; t < L; t++) {           /* q_t = q_{t-1} + e_{path[t-1]} */
        int b = 1 << path[t - 1];
        add3(lo[t - 1], hi[t - 1], b, 0, &lo[t], &hi[t]);
        lo[t] &= full; hi[t] &= full;
    }
    gen++;
    if (gen == 0) { for (int i = 0; i < (1 << (2 * n)); i++) stamp[i] = 0; gen = 1; }
    for (int i = 0; i < L; i++)
        for (int j = i; j < L; j++) {
            int sl, sh;
            add3(lo[i], hi[i], lo[j], hi[j], &sl, &sh);
            stamp[(sl & full) | ((sh & full) << n)] = gen;
        }
    for (int k = 0; k < full; k++) {
        int m = mask_order[k], ok = 0;
        for (int c = 0; c < L && !ok; c++) {
            int dl, dh;                       /* m - q_c = m + (-q_c) */
            add3(m, 0, hi[c], lo[c], &dl, &dh);
            if (stamp[(dl & full) | ((dh & full) << n)] == gen) ok = 1;
        }
        if (!ok) return 0;
    }
    return 1;
}

static void rec(int t) {
    if (t == split_depth) {
        if ((prefix_counter++ % nshards) != (uint64_t)shard) return;
    }
    if (t == L) {
        leaves++;
        if (check()) {
            solutions++;
            if (solutions <= (uint64_t)print_limit) {
                printf("SOLUTION");
                for (int i = 0; i < L; i++) printf(" %d", path[i]);
                printf("\n");
            }
        }
        return;
    }
    int top = sym ? (used_labels < n ? used_labels + 1 : n) : n;
    for (int s = 0; s < top; s++) {
        if (cnt[s] == 3) continue;
        if (sym) {
            if (t < g0 && s == 0 && t != 0) continue;     /* source 0 waits */
            if (t == g0 && s != 0) continue;              /* second 0 at g0 */
            if (cnt[s] > 0 && t - last[s] < g0) continue;
            if (cnt[s] == 2 && L - t + first[s] < g0) continue;
        }
        int ol = last[s], of = first[s], ou = used_labels;
        if (cnt[s] == 0) { first[s] = t; if (s == used_labels) used_labels++; }
        last[s] = t; cnt[s]++; path[t] = s;
        rec(t + 1);
        cnt[s]--; last[s] = ol; first[s] = of; used_labels = ou;
    }
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: reduced n nshards shard sym [print_limit]\n"); return 2; }
    n = atoi(argv[1]); nshards = atoi(argv[2]); shard = atoi(argv[3]); sym = atoi(argv[4]);
    print_limit = argc > 5 ? atoi(argv[5]) : 5;
    if (n < 1 || n > MAXN || nshards < 1 || shard < 0 || shard >= nshards) return 2;
    L = 3 * n;
    split_depth = L < 9 ? L : 9;
    /* hardest masks first: by descending weight */
    int k = 0;
    for (int w = n; w >= 1; w--)
        for (int m = 1; m < (1 << n); m++)
            if (__builtin_popcount(m) == w) mask_order[k++] = m;
    if (sym) {
        for (g0 = 1; 3 * g0 <= L; g0++) {
            prefix_counter = 0;
            for (int s = 0; s < n; s++) cnt[s] = 0;
            used_labels = 0;
            rec(0);
        }
    } else {
        prefix_counter = 0; used_labels = n;
        rec(0);
    }
    printf("RESULT n=%d sym=%d shard=%d/%d leaves=%llu solutions=%llu\n", n, sym, shard, nshards,
           (unsigned long long)leaves, (unsigned long long)solutions);
    return 0;
}
