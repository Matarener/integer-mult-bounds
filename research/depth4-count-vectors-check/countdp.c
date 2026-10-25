/* Reachable products by exact call-count vector for the depth-four chain connector, mod M.
 *
 * R(n) is the set of products of positive words with exactly n_l calls l (l = 1..4) in the
 * lower unitriangular group mod M; call l adds row l-1 (diagonal 1 in column l-1) to row l.
 * The adjacent entries of every element of R(n) are n_l mod M, so R(n) is stored as a bitset
 * over the six other entries. R(n) = union over l with n_l > 0 of g_l R(n - e_l).
 * Prints every count vector (entries <= B) whose R(n) contains I + c E[4][0], per residue c.
 * Build: cc -O2 -DM=3 -o countdp countdp.c ; run: ./countdp B
 * Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FREE 6
static const int FR[FREE] = {2, 3, 3, 4, 4, 4}, FC[FREE] = {0, 0, 1, 0, 1, 2};
static int NF, WORDS, B;

static int decode(int f, int a[5][5], const int adj[5]) {
    memset(a, 0, sizeof(int) * 25);
    for (int k = 0; k < FREE; k++) { a[FR[k]][FC[k]] = f % M; f /= M; }
    for (int l = 1; l <= 4; l++) a[l][l - 1] = adj[l];
    return 0;
}

static int encode(int a[5][5]) {
    int f = 0;
    for (int k = FREE - 1; k >= 0; k--) f = f * M + a[FR[k]][FC[k]];
    return f;
}

static size_t idx(const int n[5]) { return (((size_t)n[1] * (B + 1) + n[2]) * (B + 1) + n[3]) * (B + 1) + n[4]; }

int main(int argc, char **argv) {
    B = argc > 1 ? atoi(argv[1]) : 3 * M;
    NF = 1;
    for (int k = 0; k < FREE; k++) NF *= M;
    WORDS = (NF + 63) / 64;
    size_t nv = (size_t)(B + 1) * (B + 1) * (B + 1) * (B + 1);
    uint64_t *R = calloc(nv * WORDS, 8);
    if (!R) { fprintf(stderr, "alloc\n"); return 1; }
    int n[5] = {0, 0, 0, 0, 0};
    R[0] |= 1;                                   /* the identity: all free entries 0 */
    for (n[1] = 0; n[1] <= B; n[1]++)
    for (n[2] = 0; n[2] <= B; n[2]++)
    for (n[3] = 0; n[3] <= B; n[3]++)
    for (n[4] = 0; n[4] <= B; n[4]++) {
        if (!(n[1] | n[2] | n[3] | n[4])) continue;
        uint64_t *dst = R + idx(n) * WORDS;
        for (int l = 1; l <= 4; l++) {
            if (!n[l]) continue;
            int p[5]; memcpy(p, n, sizeof p); p[l]--;
            int adj[5] = {0};
            for (int k = 1; k <= 4; k++) adj[k] = p[k] % M;
            const uint64_t *src = R + idx(p) * WORDS;
            for (int f = 0; f < NF; f++) {
                if (!((src[f >> 6] >> (f & 63)) & 1)) continue;
                int a[5][5];
                decode(f, a, adj);
                for (int j = 0; j < l - 1; j++) a[l][j] = (a[l][j] + a[l - 1][j]) % M;
                int g = encode(a);
                dst[g >> 6] |= 1ULL << (g & 63);
            }
        }
    }
    for (int c = 1; c < M; c++) {
        int a[5][5] = {{0}};
        a[4][0] = c;
        int t = encode(a);
        for (n[1] = 0; n[1] <= B; n[1]++)
        for (n[2] = 0; n[2] <= B; n[2]++)
        for (n[3] = 0; n[3] <= B; n[3]++)
        for (n[4] = 0; n[4] <= B; n[4]++) {
            int ok = 1;
            for (int k = 1; k <= 4; k++) ok &= n[k] % M == 0;   /* other adjacent entries must vanish */
            if (ok && ((R[idx(n) * WORDS + (t >> 6)] >> (t & 63)) & 1))
                printf("M=%d B=%d c=%d n=%d,%d,%d,%d\n", M, B, c, n[1], n[2], n[3], n[4]);
        }
    }
    free(R);
    return 0;
}
