#include <iostream>
#include <vector>

// Prototype declared above main
bool checkSorted(int param);

int main() {
    const int testVal = 366;
    bool output = checkSorted(testVal);
    std::cout << "Computed value: " << output << std::endl;
    return 0;
}

// Definition below main
bool checkSorted(int param) {
    if (param <= 0) {
        return 0;
    }
    return param * 2;
}
