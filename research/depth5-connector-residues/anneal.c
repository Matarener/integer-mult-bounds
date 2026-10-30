/* Simulated annealing for depth-five connector words with a fixed call-count vector, mod m.
 * Cost = sum over the 15 strictly-lower entries of the distance of the word's unitriangular
 * product to I + c E[5][0]. Moves swap two positions holding different calls. Prints a word of
 * cost 0 if found. Usage: ./anneal m c n1 n2 n3 n4 n5 seed tries sweeps
 * Only a search: a printed word is a certificate, a miss proves nothing.
 * Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
 */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int m, c, L, w[256];
static unsigned long long rs;
static unsigned rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return (unsigned)(rs >> 11); }

static int cost(void) {
    int x[6][6] = {{0}};
    for (int i = 0; i < 6; i++) x[i][i] = 1;
    for (int t = 0; t < L; t++) { int l = w[t]; for (int j = 0; j < l; j++) x[l][j] = (x[l][j] + x[l - 1][j]) % m; }
    int s = 0;
    for (int i = 1; i < 6; i++) for (int j = 0; j < i; j++) {
        int want = (i == 5 && j == 0) ? c : 0, d = (x[i][j] - want + m) % m;
        s += d < m - d ? d : m - d;
    }
    return s;
}

int main(int argc, char **argv) {
    if (argc != 11) return 2;
    m = atoi(argv[1]); c = atoi(argv[2]);
    int n[6]; L = 0;
    for (int l = 1; l <= 5; l++) { n[l] = atoi(argv[2 + l]); for (int k = 0; k < n[l]; k++) w[L++] = l; }
    rs = strtoull(argv[8], 0, 10) * 2654435761ULL + 1;
    long tries = atol(argv[9]), sweeps = atol(argv[10]);
    for (long tr = 0; tr < tries; tr++) {
        for (int i = L - 1; i > 0; i--) { int j = rnd() % (i + 1), t = w[i]; w[i] = w[j]; w[j] = t; }
        int cur = cost();
        double T = 2.0;
        for (long it = 0; it < sweeps * L && cur; it++) {
            int i = rnd() % L, j = rnd() % L;
            if (w[i] == w[j]) continue;
            int t = w[i]; w[i] = w[j]; w[j] = t;
            int nc = cost();
            if (nc <= cur || exp((cur - nc) / T) * 4294967296.0 > rnd() * 2.0) cur = nc;
            else { t = w[i]; w[i] = w[j]; w[j] = t; }
            T = 2.0 * (1.0 - (double)it / (sweeps * L)) + 0.05;
        }
        if (!cur) {
            printf("m=%d c=%d counts=%d,%d,%d,%d,%d word=", m, c, n[1], n[2], n[3], n[4], n[5]);
            for (int t = 0; t < L; t++) putchar('0' + w[t]);
            putchar('\n');
            return 0;
        }
    }
    printf("m=%d c=%d counts=%d,%d,%d,%d,%d no_word_found\n", m, c, n[1], n[2], n[3], n[4], n[5]);
    return 1;
}
