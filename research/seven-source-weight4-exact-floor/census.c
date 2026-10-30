/* Exhaustive census of restored source-toggle words for the dirty F2 connector.
 *
 * A word w of length L over sources 0..n-1 is restored when every source occurs
 * an even number of times.  Its prefix parities are q_0 = 0 and
 * q_t = q_{t-1} ^ (1 << w[t-1]); a mask m is covered when m = q_a ^ q_b for
 * some 0 <= a < b < L.  The target is every nonzero mask of weight <= W.
 *
 * Words are enumerated once per relabelling class: letters are named in order
 * of first occurrence, and a new letter chooses its total multiplicity from the
 * still-unassigned multiset of the profile.
 *
 * usage: census n W c_1 ... c_n      exact maximum coverage for that profile
 *        census lift K W c_1 ... c_6 6-source words of the given profile
 *                                    covering all weight-<=W masks, each
 *                                    lifted by K copies of source 6 at every
 *                                    choice of positions
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXL 26
#define MAXN 8

typedef struct { uint64_t lo, hi; } m128;

static int n_src, L, wmax;
static int prof_left[MAXL + 1];  /* multiplicity -> unassigned sources with it */
static int remaining[MAXN];      /* per assigned label: occurrences still owed */
static int word[MAXL];
static int state[MAXL + 1];
static m128 target;
static int n_target;

static unsigned long long n_words;
static int best = -1;
static unsigned long long n_best;
static int best_word[MAXL];
static unsigned long long hist[129];

/* lift mode */
static int lift_mode, lift_k;
static unsigned long long n_full6, n_lifts;
static int lift_best = -1;
static unsigned long long n_lift_best;
static int lift_best_word[MAXL + 1];
static m128 target7;

static inline void set_bit(m128 *s, int m) {
    if (m < 64) s->lo |= 1ULL << m; else s->hi |= 1ULL << (m - 64);
}
static inline int pop_and(m128 a, m128 b) {
    return __builtin_popcountll(a.lo & b.lo) + __builtin_popcountll(a.hi & b.hi);
}

static m128 build_target(int n, int w) {
    m128 t = {0, 0};
    for (int m = 1; m < (1 << n); m++)
        if (__builtin_popcount(m) <= w) set_bit(&t, m);
    return t;
}

/* Coverage of an explicit word, recomputed from scratch (used by lift mode). */
static int coverage(const int *w, int len, m128 tgt) {
    int q[MAXL + 1];
    m128 s = {0, 0};
    q[0] = 0;
    for (int t = 1; t < len; t++) {
        q[t] = q[t - 1] ^ (1 << w[t - 1]);
        for (int a = 0; a < t; a++) set_bit(&s, q[t] ^ q[a]);
    }
    return pop_and(s, tgt);
}

static void lift_rec(const int *w6, int *pos, int depth, int start) {
    /* Choose lift_k increasing positions of the lifted word for source 6. */
    int len = L + lift_k;
    if (depth == lift_k) {
        int w7[MAXL + 1], k = 0, j = 0;
        for (int p = 0; p < len; p++)
            w7[p] = (j < lift_k && pos[j] == p) ? (j++, 6) : w6[k++];
        int cov = coverage(w7, len, target7);
        n_lifts++;
        if (cov > lift_best) {
            lift_best = cov; n_lift_best = 0;
            memcpy(lift_best_word, w7, sizeof(int) * len);
        }
        if (cov == lift_best) n_lift_best++;
        return;
    }
    for (int p = start; p <= len - (lift_k - depth); p++) {
        pos[depth] = p;
        lift_rec(w6, pos, depth + 1, p + 1);
    }
}

static void lift(const int *w6) {
    /* Insert lift_k copies of source 6 at every lift_k-subset of positions. */
    int pos[MAXL + 1];
    lift_rec(w6, pos, 0, 0);
}

static void leaf(m128 seen) {
    int cov = pop_and(seen, target);
    n_words++;
    hist[cov]++;
    if (cov > best) { best = cov; n_best = 0; memcpy(best_word, word, sizeof(int) * L); }
    if (cov == best) n_best++;
    if (lift_mode && cov == n_target) { n_full6++; lift(word); }
}

static void dfs(int t, int labels, m128 seen) {
    /* t letters placed; state[0..t] known; covered differences among them in seen. */
    if (t == L - 1) {
        /* The last letter is forced (the only label still owing one occurrence)
         * and returns the parity to zero, adding no new state. */
        for (int l = 0; l < labels; l++)
            if (remaining[l] == 1) { word[t] = l; break; }
        leaf(seen);
        return;
    }
    for (int l = 0; l <= labels && l < n_src; l++) {
        int newlab = (l == labels);
        int mult_lo = newlab ? 2 : 0, mult_hi = newlab ? L : 0;
        for (int mult = mult_lo; mult <= mult_hi; mult += newlab ? 2 : 1) {
            if (newlab) {
                if (prof_left[mult] == 0) continue;
                prof_left[mult]--; remaining[l] = mult;
            } else if (remaining[l] == 0) {
                continue;
            }
            remaining[l]--;
            word[t] = l;
            int s = state[t] ^ (1 << l);
            state[t + 1] = s;
            m128 ns = seen;
            for (int a = 0; a <= t; a++) set_bit(&ns, s ^ state[a]);
            dfs(t + 1, labels + newlab, ns);
            remaining[l]++;
            if (newlab) { prof_left[mult]++; remaining[l] = 0; }
            if (!newlab) break;
        }
    }
}

static void print_word(const int *w, int len) {
    for (int i = 0; i < len; i++) printf("%s%d", i ? " " : "", w[i]);
}

int main(int argc, char **argv) {
    int argi = 1;
    if (argc > 2 && strcmp(argv[1], "lift") == 0) {
        lift_mode = 1; n_src = 6; lift_k = atoi(argv[2]); argi = 3;
        if (lift_k < 2 || lift_k % 2) { fprintf(stderr, "bad lift multiplicity\n"); return 2; }
    }
    else if (argc > 1) n_src = atoi(argv[argi++]);
    if (argc < argi + 1 + n_src || n_src < 1 || n_src > 7) {
        fprintf(stderr, "usage: census n W c_1..c_n | census lift K W c_1..c_6\n");
        return 2;
    }
    wmax = atoi(argv[argi++]);
    L = 0;
    for (int i = 0; i < n_src; i++) {
        int c = atoi(argv[argi++]);
        if (c < 2 || c % 2 || c > MAXL) { fprintf(stderr, "bad multiplicity %d\n", c); return 2; }
        prof_left[c]++; L += c;
    }
    if (L > MAXL || (lift_mode && L + lift_k > MAXL)) { fprintf(stderr, "word too long\n"); return 2; }
    target = build_target(n_src, wmax);
    n_target = pop_and(target, target);
    target7 = build_target(7, wmax);
    state[0] = 0;
    m128 zero = {0, 0};
    dfs(0, 0, zero);

    printf("{\"n\":%d,\"W\":%d,\"L\":%d,\"profile\":[", n_src, wmax, L);
    int first = 1;
    for (int c = MAXL; c >= 2; c--)
        for (int k = 0; k < prof_left[c]; k++) { printf("%s%d", first ? "" : ",", c); first = 0; }
    (void)first;
    printf("],\"targets\":%d,\"canonical_words\":%llu,\"max_coverage\":%d,"
           "\"words_at_max\":%llu,\"first_word_at_max\":\"", n_target, n_words, best, n_best);
    print_word(best_word, L);
    printf("\",\"histogram\":{");
    first = 1;
    for (int c = 0; c <= 128; c++)
        if (hist[c]) { printf("%s\"%d\":%llu", first ? "" : ",", c, hist[c]); first = 0; }
    printf("}");
    if (lift_mode) {
        printf(",\"lift_k\":%d,\"full_coverage_6source_words\":%llu,\"lifts\":%llu,"
               "\"lift_targets\":%d,\"lift_max_coverage\":%d,\"lifts_at_max\":%llu,"
               "\"first_lift_at_max\":\"",
               lift_k, n_full6, n_lifts, pop_and(target7, target7), lift_best, n_lift_best);
        if (lift_best >= 0) print_word(lift_best_word, L + lift_k);
        printf("\"");
    }
    printf("}\n");
    return 0;
}
