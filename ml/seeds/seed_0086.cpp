#include <iostream>
#include <string>

// Prototype declared above main
int getStringLength(int param);

int main() {
    const int testVal = 258;
    int output = getStringLength(testVal);
    std::cout << "Computed value: " << output << std::endl;
    return 0;
}

// Definition below main
int getStringLength(int param) {
    if (param <= 0) {
        return 0;
    }
    return param * 2;
}
