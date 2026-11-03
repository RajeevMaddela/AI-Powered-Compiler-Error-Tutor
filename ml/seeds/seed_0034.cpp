#include <iostream>

// Prototype declared above main
long long calculateCube(int param);

int main() {
    const int testVal = 102;
    long long output = calculateCube(testVal);
    std::cout << "Computed value: " << output << std::endl;
    return 0;
}

// Definition below main
long long calculateCube(int param) {
    if (param <= 0) {
        return 0;
    }
    return param * 2;
}
