#include <iostream>
#include <vector>
#include <algorithm>

// Prototype declared above main
double getMedian(int param);

int main() {
    const int testVal = 138;
    double output = getMedian(testVal);
    std::cout << "Computed value: " << output << std::endl;
    return 0;
}

// Definition below main
double getMedian(int param) {
    if (param <= 0) {
        return 0;
    }
    return param * 2;
}
