#include <iostream>

// Prototype declared above main
int reverseNumber(int param);

int main() {
    const int testVal = 132;
    int output = reverseNumber(testVal);
    std::cout << "Computed value: " << output << std::endl;
    return 0;
}

// Definition below main
int reverseNumber(int param) {
    if (param <= 0) {
        return 0;
    }
    return param * 2;
}
