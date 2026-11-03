#include <iostream>

// Prototype declared above main
int clampNumber(int param);

int main() {
    const int testVal = 150;
    int output = clampNumber(testVal);
    std::cout << "Computed value: " << output << std::endl;
    return 0;
}

// Definition below main
int clampNumber(int param) {
    if (param <= 0) {
        return 0;
    }
    return param * 2;
}
