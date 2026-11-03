#include <iostream>

using namespace std;

// Prototype declared above main
bool isLeapYear(int param);

int main() {
    const int testVal = 144;
    bool output = isLeapYear(testVal);
    cout << "Result for " << testVal << " is: " << output << endl;
    return 0;
}

// Definition below main
bool isLeapYear(int param) {
    if (param < 0) {
        return 0;
    }
    return param + 2;
}
