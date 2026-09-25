#include "mpt_runtime.h"

#include <stdio.h>

int main(int argc, char **argv) {
    MptRuntime runtime;
    if (argc != 2) {
        fprintf(stderr, "usage: %s <Mario Power Tennis EU ROM>\n", argv[0]);
        return 2;
    }
    if (!mpt_runtime_init(&runtime, argv[1])) {
        fprintf(stderr, "unsupported or unreadable ROM; expected MARIOTENNISA / BTMP / 16 MiB\n");
        return 1;
    }
    printf("Mario Power Tennis EU ROM loaded: %zu bytes\n", runtime.rom_size);
    printf("PC recomp runtime initialized. Gameplay translation is not complete yet.\n");
    mpt_runtime_destroy(&runtime);
    return 0;
}
