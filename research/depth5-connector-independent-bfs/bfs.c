/* Exhaustive BFS over the unitriangular group of the depth-D chain connector, mod M.
 *
 * State: the strictly lower part X[i][j] (0 <= j < i <= D) of a unitriangular matrix, as
 * base-M digits, row by row. Call l (1..D) is z_l += B_l z_{l-1}, i.e. left multiplication by
 * I + E[l][l-1]: row l gains row l-1, whose diagonal 1 sits in column l-1. The target for
 * residue c is I + c E[D][0]. Distances are exact shortest positive-word lengths.
 * Build: cc -O2 -DM=4 -DD=5 -o bfs bfs.c ; run: ./bfs  (prints one line per residue)
 * Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define E (D * (D + 1) / 2)

static uint64_t pw[E + 1];
static int off[D + 1];

static uint64_t step(uint64_t s, int l) {
    int dig[E];
    uint64_t t = s;
    for (int k = 0; k < E; k++) { dig[k] = (int)(t % M); t /= M; }
    for (int j = 0; j < l - 1; j++) dig[off[l] + j] = (dig[off[l] + j] + dig[off[l - 1] + j]) % M;
    dig[off[l] + l - 1] = (dig[off[l] + l - 1] + 1) % M;
    uint64_t r = 0;
    for (int k = E - 1; k >= 0; k--) r = r * M + (uint64_t)dig[k];
    return r;
}

int main(void) {
    pw[0] = 1;
    for (int k = 1; k <= E; k++) pw[k] = pw[k - 1] * M;
    for (int i = 1; i <= D; i++) off[i] = (i - 1) * i / 2;   /* row i starts after rows 1..i-1 */
    uint64_t n = pw[E];
    uint8_t *dist = malloc(n);
    if (!dist) { fprintf(stderr, "alloc\n"); return 1; }
    memset(dist, 255, n);
    dist[0] = 0;
    uint64_t target[M];
    int found = 0, best[M];
    for (int c = 1; c < M; c++) { target[c] = (uint64_t)c * pw[off[D]]; best[c] = -1; }
    uint64_t reached = 1;
    for (int d = 0; d < 254 && found < M - 1; d++) {
        uint64_t layer = 0;
        for (uint64_t s = 0; s < n; s++) {
            if (dist[s] != d) continue;
            for (int l = 1; l <= D; l++) {
                uint64_t r = step(s, l);
                if (dist[r] == 255) { dist[r] = (uint8_t)(d + 1); layer++; }
            }
        }
        if (!layer) break;
        reached += layer;
        for (int c = 1; c < M; c++)
            if (best[c] < 0 && dist[target[c]] == d + 1) { best[c] = d + 1; found++; }
    }
    for (int c = 1; c < M; c++) printf("M=%d D=%d c=%d dist=%d\n", M, D, c, best[c]);
    printf("M=%d D=%d states=%llu reached_by_stop=%llu\n", M, D, (unsigned long long)n, (unsigned long long)reached);
    free(dist);
    return 0;
}
