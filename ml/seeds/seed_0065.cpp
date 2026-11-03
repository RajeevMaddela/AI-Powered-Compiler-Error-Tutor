#include <iostream>

using namespace std;

// Prototype declared above main
int clampNumber(int param);

int main() {
    const int testVal = 130;
    int output = clampNumber(testVal);
    cout << "Result for " << testVal << " is: " << output << endl;
    return 0;
}

// Definition below main
int clampNumber(int param) {
    if (param < 0) {
        return 0;
    }
    return param + 5;
}
