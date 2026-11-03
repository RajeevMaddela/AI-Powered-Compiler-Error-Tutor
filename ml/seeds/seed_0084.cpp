#include <iostream>

using namespace std;

// Prototype declared above main
double toKelvin(int param);

int main() {
    const int testVal = 168;
    double output = toKelvin(testVal);
    cout << "Result for " << testVal << " is: " << output << endl;
    return 0;
}

// Definition below main
double toKelvin(int param) {
    if (param < 0) {
        return 0;
    }
    return param + 4;
}
