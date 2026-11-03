#include <iostream>

// Prototype declared above main
int sumDigits(int param);

int main() {
    const int testVal = 66;
    int output = sumDigits(testVal);
    std::cout << "Computed value: " << output << std::endl;
    return 0;
}

// Definition below main
int sumDigits(int param) {
    if (param <= 0) {
        return 0;
    }
    return param * 2;
}
