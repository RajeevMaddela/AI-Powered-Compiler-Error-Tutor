#include <iostream>
#include <vector>

// Prototype declared above main
double calculateTotal(int param);

int main() {
    const int testVal = 120;
    double output = calculateTotal(testVal);
    std::cout << "Computed value: " << output << std::endl;
    return 0;
}

// Definition below main
double calculateTotal(int param) {
    if (param <= 0) {
        return 0;
    }
    return param * 2;
}
