/* Exhaust all 4x4 matrices with entries in {-1,0,1}; exact integer arithmetic. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define SIDE 4
#define TOTAL 43046721ULL
#define SIGNATURES (1u << 16)

static int permutations[24][SIDE];
static int permutation_sign[24];
static int permutation_count;
static unsigned char structural[SIGNATURES];
static unsigned char seen[SIGNATURES];
static unsigned char binary_seen[SIGNATURES];
static signed char witness[SIGNATURES][16];
static int matrix_values[16];

static void permute(int depth, int *values, int used) {
    if (depth == SIDE) {
        int inversions = 0;
        for (int i = 0; i < SIDE; ++i)
            for (int j = i + 1; j < SIDE; ++j)
                inversions += values[i] > values[j];
        memcpy(permutations[permutation_count], values, SIDE * sizeof(int));
        permutation_sign[permutation_count] = (inversions & 1) ? -1 : 1;
        ++permutation_count;
        return;
    }
    for (int column = 0; column < SIDE; ++column) {
        if (!(used & (1 << column))) {
            values[depth] = column;
            permute(depth + 1, values, used | (1 << column));
        }
    }
}

static int support_has_matching(unsigned mask) {
    for (int p = 0; p < 24; ++p) {
        int matched = 1;
        for (int row = 0; row < SIDE; ++row) {
            if ((mask & (1u << (4 * row + permutations[p][row]))) == 0) {
                matched = 0;
                break;
            }
        }
        if (matched) return 1;
    }
    return 0;
}

static int determinant_three(const int *matrix, const int *rows, const int *columns) {
    int a = matrix[4 * rows[0] + columns[0]];
    int b = matrix[4 * rows[0] + columns[1]];
    int c = matrix[4 * rows[0] + columns[2]];
    int d = matrix[4 * rows[1] + columns[0]];
    int e = matrix[4 * rows[1] + columns[1]];
    int f = matrix[4 * rows[1] + columns[2]];
    int g = matrix[4 * rows[2] + columns[0]];
    int h = matrix[4 * rows[2] + columns[1]];
    int i = matrix[4 * rows[2] + columns[2]];
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
}

static int count_signatures(const unsigned char *table) {
    int count = 0;
    for (unsigned i = 0; i < SIGNATURES; ++i) count += table[i] != 0;
    return count;
}

int main(void) {
    int permutation[SIDE];
    permute(0, permutation, 0);
    if (permutation_count != 24) return 2;
    for (unsigned mask = 0; mask < SIGNATURES; ++mask)
        structural[mask] = (unsigned char)support_has_matching(mask);

    uint64_t invertible = 0;
    uint64_t binary_invertible = 0;
    int rows[3], columns[3], cofactors[SIDE][SIDE];
    for (uint64_t code = 0; code < TOTAL; ++code) {
        uint64_t digits = code;
        unsigned support = 0;
        int is_binary = 1;
        for (int i = 0; i < 16; ++i) {
            int digit = (int)(digits % 3ULL);
            digits /= 3ULL;
            matrix_values[i] = digit - 1;
            if (digit != 1) support |= 1u << i;
            if (digit == 0) is_binary = 0;
        }
        if (!structural[support]) continue;

        for (int row = 0; row < SIDE; ++row) {
            int row_index = 0;
            for (int candidate = 0; candidate < SIDE; ++candidate)
                if (candidate != row) rows[row_index++] = candidate;
            for (int column = 0; column < SIDE; ++column) {
                int column_index = 0;
                for (int candidate = 0; candidate < SIDE; ++candidate)
                    if (candidate != column) columns[column_index++] = candidate;
                int minor = determinant_three(matrix_values, rows, columns);
                cofactors[row][column] = ((row + column) & 1) ? -minor : minor;
            }
        }
        int determinant = 0;
        for (int column = 0; column < SIDE; ++column)
            determinant += matrix_values[column] * cofactors[0][column];
        if (!determinant) continue;
        ++invertible;
        if (is_binary) ++binary_invertible;

        unsigned signature = 0;
        for (int message = 0; message < SIDE; ++message) {
            int source_ports = 0;
            int reader_ports = 0;
            for (int coordinate = 0; coordinate < SIDE; ++coordinate) {
                if (matrix_values[4 * coordinate + message]) source_ports |= 1 << coordinate;
                if (cofactors[coordinate][message]) reader_ports |= 1 << coordinate;
            }
            int source_planes = (source_ports & 3 ? 1 : 0) + (source_ports & 12 ? 2 : 0);
            int reader_planes = (reader_ports & 3 ? 1 : 0) + (reader_ports & 12 ? 2 : 0);
            if (!source_planes || !reader_planes) return 3;
            unsigned term = (unsigned)(source_planes * 4 + reader_planes);
            signature |= term << (4 * message);
        }
        if (!seen[signature]) {
            seen[signature] = 1;
            for (int i = 0; i < 16; ++i)
                witness[signature][i] = (signed char)matrix_values[i];
        }
        if (is_binary) binary_seen[signature] = 1;
    }

    int signature_count = count_signatures(seen);
    int binary_signature_count = count_signatures(binary_seen);
    if (invertible != 27947520ULL || signature_count != 439
            || binary_invertible != 22560ULL || binary_signature_count != 391)
        return 4;

    printf("TERNARY_SCREEN_V1 total=%llu invertible=%llu signatures=%d "
           "binary_invertible=%llu binary_signatures=%d\n",
           (unsigned long long)TOTAL, (unsigned long long)invertible, signature_count,
           (unsigned long long)binary_invertible, binary_signature_count);
    for (unsigned signature = 0; signature < SIGNATURES; ++signature) {
        if (!seen[signature]) continue;
        printf("%04x", signature);
        for (int i = 0; i < 16; ++i) printf(" %d", (int)witness[signature][i]);
        putchar('\n');
    }
    return 0;
}
