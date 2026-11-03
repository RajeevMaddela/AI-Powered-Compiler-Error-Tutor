#include <iostream>

using namespace std;

// Prototype declared above main
int sumDigits(int param);

int main() {
    const int testVal = 194;
    int output = sumDigits(testVal);
    cout << "Result for " << testVal << " is: " << output << endl;
    return 0;
}

// Definition below main
int sumDigits(int param) {
    if (param < 0) {
        return 0;
    }
    return param + 7;
}
