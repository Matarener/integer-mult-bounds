// SPDX-License-Identifier: Apache-2.0
// Bounded, iterative exact cover. Each row contains exactly eight columns.
#include <cstdint>
#include <iostream>
#include <stdexcept>

namespace {
constexpr int max_rows = 4032;
constexpr int max_columns = 112;
constexpr int max_nodes = max_rows * 8 + max_columns + 1;
constexpr std::uint64_t max_budget = 60000000;

void need(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

struct Level { int column = 0; int row = 0; };

class Cover {
    int left[max_nodes]{}, right[max_nodes]{}, up[max_nodes]{}, down[max_nodes]{}, column[max_nodes]{}, row_id[max_nodes]{};
    int size[max_columns + 1]{};
    int head[max_rows]{};
    int rows[max_rows][8]{};
    int selected[14]{};
    Level levels[14]{};
    int columns = 0, row_count = 0, fixed = 0, next = 0;
    std::uint64_t budget = 0, nodes = 0;

    void cover(int c) {
        const int previous = left[c], following = right[c];
        left[following] = previous; right[previous] = following;
        int i = down[c];
        for (int count = 0; count < max_rows && i != c; ++count, i = down[i]) {
            int j = right[i];
            for (int k = 0; k < 7; ++k, j = right[j]) {
                const int below = down[j], above = up[j], owner = column[j];
                up[below] = above; down[above] = below; --size[owner];
            }
        }
        need(i == c, "column traversal bound");
    }

    void uncover(int c) {
        int i = up[c];
        for (int count = 0; count < max_rows && i != c; ++count, i = up[i]) {
            int j = left[i];
            for (int k = 0; k < 7; ++k, j = left[j]) {
                const int owner = column[j], below = down[j], above = up[j];
                ++size[owner]; up[below] = j; down[above] = j;
            }
        }
        need(i == c, "reverse column traversal bound");
        const int following = right[c], previous = left[c];
        left[following] = c; right[previous] = c;
    }

    void undo_choice(int depth) {
        const int i = levels[depth].row;
        int j = left[i];
        for (int k = 0; k < 7; ++k, j = left[j]) uncover(column[j]);
        levels[depth].row = down[i];
    }

    int least_column() const {
        int best = right[0], j = right[best];
        for (int count = 0; count < max_columns && j != 0; ++count, j = right[j]) {
            if (size[j] < size[best]) best = j;
        }
        need(j == 0, "header traversal bound");
        return best;
    }

    void add_row(int id) {
        const int first = next;
        head[id] = first;
        bool seen[max_columns]{};
        for (int k = 0; k < 8; ++k) {
            int p = -1;
            need(static_cast<bool>(std::cin >> p), "missing row entry");
            need(p >= 0 && p < columns && !seen[p], "invalid row column");
            seen[p] = true; rows[id][k] = p;
            const int c = p + 1;
            column[next] = c; row_id[next] = id;
            const int previous = up[c];
            up[next] = previous; down[next] = c; down[previous] = next; up[c] = next;
            ++size[c]; left[next] = next - 1; right[next] = next + 1; ++next;
        }
        left[first] = next - 1; right[next - 1] = first;
    }

public:
    void read() {
        need(static_cast<bool>(std::cin >> columns >> row_count >> fixed >> budget),
             "missing header");
        need(columns >= 1 && columns <= max_columns && row_count >= 1 &&
             row_count <= max_rows && fixed >= 0 && fixed <= 14 && budget <= max_budget,
             "header bounds");
        for (int k = 0; k < fixed; ++k) {
            need(static_cast<bool>(std::cin >> selected[k]), "missing fixed row");
            need(selected[k] >= 0 && selected[k] < row_count, "fixed row range");
        }
        for (int c = 0; c <= columns; ++c) {
            left[c] = c - 1; right[c] = c + 1; up[c] = c; down[c] = c;
        }
        left[0] = columns; right[columns] = 0; next = columns + 1;
        for (int id = 0; id < row_count; ++id) add_row(id);
        std::cin >> std::ws; need(std::cin.eof(), "trailing input");
        bool occupied[max_columns]{};
        for (int k = 0; k < fixed; ++k) {
            for (int p : rows[selected[k]]) {
                need(!occupied[p], "intersecting fixed rows"); occupied[p] = true;
            }
            const int i = head[selected[k]];
            cover(column[i]); int j = right[i];
            for (int t = 0; t < 7; ++t, j = right[j]) cover(column[j]);
        }
    }

    const char* solve(int& total) {
        int depth = 0;
        bool enter = true;
        for (std::uint64_t step = 0; step < 4 * budget + 100; ++step) {
            if (enter) {
                if (right[0] == 0) { total = fixed + depth; return "SAT"; }
                if (++nodes > budget) return "UNKNOWN";
                const int c = least_column();
                if (size[c] == 0) {
                    if (depth == 0) return "UNSAT";
                    --depth; undo_choice(depth); enter = false; continue;
                }
                need(fixed + depth < 14, "search depth bound");
                cover(c); levels[depth] = {c, down[c]}; enter = false;
            } else {
                Level& level = levels[depth];
                if (level.row == level.column) {
                    uncover(level.column);
                    if (depth == 0) return "UNSAT";
                    --depth; undo_choice(depth); continue;
                }
                selected[fixed + depth] = row_id[level.row];
                int j = right[level.row];
                for (int k = 0; k < 7; ++k, j = right[j]) cover(column[j]);
                ++depth; enter = true;
            }
        }
        throw std::runtime_error("transition bound");
    }

    void print(const char* status, int total) const {
        std::cout << "{\"status\":\"" << status << "\",\"nodes\":" << nodes
                  << ",\"rows\":[";
        for (int k = 0; k < total; ++k) {
            if (k != 0) std::cout << ',';
            std::cout << selected[k];
        }
        std::cout << "]}\n";
        need(static_cast<bool>(std::cout), "output failure");
    }
};
}

int main() {
    try {
        Cover solver;
        solver.read();
        int total = 0;
        const char* status = solver.solve(total);
        solver.print(status, total);
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 2;
    }
}
