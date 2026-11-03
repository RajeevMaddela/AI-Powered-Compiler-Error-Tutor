#include <iostream>

using namespace std;

// Prototype declared above main
int reverseNumber(int param);

int main() {
    const int testVal = 178;
    int output = reverseNumber(testVal);
    cout << "Result for " << testVal << " is: " << output << endl;
    return 0;
}

// Definition below main
int reverseNumber(int param) {
    if (param < 0) {
        return 0;
    }
    return param + 9;
}
