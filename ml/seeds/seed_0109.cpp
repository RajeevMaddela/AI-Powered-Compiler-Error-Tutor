#include <iostream>

using namespace std;

// Prototype declared above main
long long calculateCube(int param);

int main() {
    const int testVal = 218;
    long long output = calculateCube(testVal);
    cout << "Result for " << testVal << " is: " << output << endl;
    return 0;
}

// Definition below main
long long calculateCube(int param) {
    if (param < 0) {
        return 0;
    }
    return param + 9;
}
