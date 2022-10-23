
#include <stdio.h>

int main(void) {
    int i = 0;
    for (int j = 0; j < 100; j++) {
        i = i + j;
    }
    printf("%i\n", i);
    return 0;
}
