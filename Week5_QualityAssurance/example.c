#include <stdio.h>

void main() {
    char name[255];
    printf("Enter your name: ");
    scanf("%s", &name);
    printf("Hello %s!", name);
}
