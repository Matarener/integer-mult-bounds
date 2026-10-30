// SPDX-License-Identifier: Apache-2.0
// Scoped replay of Nick Petalas's retained PR3471 three-role premise.
#define main retained_main
#include "inputs/pr3471-search.cpp"
#undef main

int main(int argc, char** argv) {
    try {
        require(argc == 2, "usage: finite OUTPUT_DIRECTORY");
        const auto t = table();
        search(3, 3, 4, {"333", "335"}, "r3-three", argv[1], t);
        search(3, 1, 2, {"222", "224", "242"}, "positive-control", argv[1], t);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }
}
