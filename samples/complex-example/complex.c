
#include <stdio.h>
#include <string.h>

int main(void) {
    int i = 0;
    const char src[50] = "http://www.tutorialspoint.com";
    char dest[50];
    strcpy(dest,"Heloooo!!");
    printf("Before memcpy dest = %s\n", dest);
    memcpy(dest, src, strlen(src)+1);
    puts(dest);
    printf("%i\n", i);
    return 0;
}
