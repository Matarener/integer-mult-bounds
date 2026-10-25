/* Independent bounded iterative census; raw coordinates and generic tables. */
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define MAX_K 5
#define MAX_N 20
#define MAX_NODES UINT64_C(100000000)
struct frame { int counts[MAX_K], introduced, next, entered; uint32_t served; };
static struct frame frames[MAX_N + 1];
static int history[MAX_N + 1][MAX_K];
static uint64_t factorial[MAX_N + 1];
static uint32_t cube[1 << (2 * MAX_K)];
static int past_options[5][5], future_options[5];
static int k, length;
static uint32_t full;
static int target;

static int bit_count(uint32_t value) {
    int result = 0;
    for (int bit = 0; bit < 32; bit++) result += (int)((value >> bit) & 1U);
    return result;
}

static void make_tables(void) {
    for (int current = 0; current <= 4; current++) {
        for (int prior = 0; prior <= 4; prior++) {
            for (int future = current; future <= 4; future++) {
                int residue = (prior + future) % 4;
                if (residue <= 1) past_options[current][prior] |= 1 << residue;
            }
        }
        for (int a = current; a <= 4; a++) for (int b = a; b <= 4; b++) {
            int residue = (a + b) % 4;
            if (residue <= 1) future_options[current] |= 1 << residue;
        }
    }
    for (int code = 0; code < (1 << (2 * k)); code++) {
        for (int mask = 0; mask < (1 << k); mask++) {
            int possible = 1;
            for (int j = 0; j < k; j++) {
                int options = (code >> (2 * j)) & 3;
                if (!(options & (1 << ((mask >> j) & 1)))) possible = 0;
            }
            if (possible) cube[code] |= UINT32_C(1) << mask;
        }
    }
}

static uint64_t completions(const struct frame *f, int depth) {
    uint64_t denominator = factorial[k - f->introduced];
    for (int j = 0; j < k; j++) denominator *= factorial[4 - f->counts[j]];
    if (factorial[length - depth] % denominator != 0) exit(3);
    return factorial[length - depth] / denominator;
}

static uint32_t update_served(uint32_t served, int depth) {
    for (int t = 0; t <= depth; t++) {
        int mask = 0, valid = 1;
        for (int j = 0; j < k; j++) {
            int residue = (history[t][j] + history[depth][j]) % 4;
            if (residue > 1) { valid = 0; break; }
            mask |= residue << j;
        }
        if (valid) served |= UINT32_C(1) << mask;
    }
    return served;
}

static uint32_t possible_masks(uint32_t served, int depth) {
    int code = 0;
    for (int j = 0; j < k; j++) code |= future_options[history[depth][j]] << (2 * j);
    uint32_t possible = served | cube[code];
    for (int t = 0; t <= depth && possible != full; t++) {
        code = 0;
        for (int j = 0; j < k; j++)
            code |= past_options[history[depth][j]][history[t][j]] << (2 * j);
        possible |= cube[code];
    }
    return possible;
}

static int census(int pruning) {
    uint64_t nodes = 0, pruned = 0, accounted = 0, solutions = 0, leaves = 0;
    uint64_t pruned_depth[MAX_N + 1] = {0};
    int depth = 0;
    frames[0].served = 1;
    for (uint64_t steps = 0; steps < MAX_NODES * 3 && depth >= 0; steps++) {
        struct frame *f = &frames[depth];
        if (!f->entered) {
            f->entered = 1;
            if (++nodes > MAX_NODES) return 4;
            f->served = update_served(f->served, depth);
            uint32_t possible = pruning ? possible_masks(f->served, depth) : full;
            if (bit_count(f->served) >= target || bit_count(possible) < target || depth == length) {
                uint64_t ways = completions(f, depth);
                accounted += ways;
                if (bit_count(f->served) >= target) solutions += ways;
                else if (bit_count(possible) < target) { pruned++; pruned_depth[depth]++; }
                else leaves++;
                depth--;
                continue;
            }
        }
        int j = f->next;
        for (; j < k && j <= f->introduced; j++) if (f->counts[j] < 4) break;
        f->next = j + 1;
        if (j == k || j > f->introduced) { depth--; continue; }
        struct frame child = *f;
        child.counts[j]++;
        child.introduced += j == f->introduced;
        child.next = 0;
        child.entered = 0;
        depth++;
        frames[depth] = child;
        for (int v = 0; v < k; v++) history[depth][v] = child.counts[v];
    }
    uint64_t denominator = factorial[k];
    for (int j = 0; j < k; j++) denominator *= factorial[4];
    uint64_t expected = factorial[length] / denominator;
    if (printf("{\"k\":%d,\"target\":%d,\"pruning\":%d,\"nodes\":%" PRIu64 ",\"pruned\":%" PRIu64
           ",\"accounted\":%" PRIu64 ",\"expected\":%" PRIu64 ",\"solutions\":%" PRIu64
           ",\"leaves\":%" PRIu64 ",\"pruned_depth\":[", k, target, pruning, nodes, pruned,
           accounted, expected, solutions, leaves) < 0) return 6;
    for (int t = 0; t <= length; t++)
        if (printf("%s%" PRIu64, t ? "," : "", pruned_depth[t]) < 0) return 6;
    if (puts("]}") == EOF || fflush(stdout) == EOF) return 6;
    return depth == -1 && accounted == expected ? 0 : 5;
}

int main(int argc, char **argv) {
    if (argc != 4) return 2;
    char *tail = NULL;
    errno = 0;
    long requested = strtol(argv[1], &tail, 10);
    if (errno || tail == argv[1] || *tail || requested < 1 || requested > MAX_K) return 2;
    k = (int)requested;
    errno = 0;
    requested = strtol(argv[2], &tail, 10);
    if (errno || tail == argv[2] || *tail || (requested != 0 && requested != 1)) return 2;
    errno = 0;
    long wanted = strtol(argv[3], &tail, 10);
    if (errno || tail == argv[3] || *tail || wanted < 1 || wanted > (1 << k)) return 2;
    target = (int)wanted;
    length = 4 * k;
    full = (uint32_t)((UINT64_C(1) << (1 << k)) - 1);
    factorial[0] = 1;
    for (int i = 1; i <= length; i++) factorial[i] = factorial[i - 1] * (uint64_t)i;
    make_tables();
    return census((int)requested);
}
