#include <iostream>
#include <vector>

using namespace std;

// Prototype declared above main
double calculateTotal(int param);

int main() {
    const int testVal = 110;
    double output = calculateTotal(testVal);
    cout << "Result for " << testVal << " is: " << output << endl;
    return 0;
}

// Definition below main
double calculateTotal(int param) {
    if (param < 0) {
        return 0;
    }
    return param + 5;
}
