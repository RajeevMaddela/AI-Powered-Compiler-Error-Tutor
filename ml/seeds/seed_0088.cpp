#include <iostream>

// Prototype declared above main
double calculateDiscriminant(int param);

int main() {
    const int testVal = 264;
    double output = calculateDiscriminant(testVal);
    std::cout << "Computed value: " << output << std::endl;
    return 0;
}

// Definition below main
double calculateDiscriminant(int param) {
    if (param <= 0) {
        return 0;
    }
    return param * 2;
}
