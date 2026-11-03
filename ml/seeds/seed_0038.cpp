#include <iostream>
#include <vector>

// Prototype declared above main
int countEvenNumbers(int param);

int main() {
    const int testVal = 114;
    int output = countEvenNumbers(testVal);
    std::cout << "Computed value: " << output << std::endl;
    return 0;
}

// Definition below main
int countEvenNumbers(int param) {
    if (param <= 0) {
        return 0;
    }
    return param * 2;
}
