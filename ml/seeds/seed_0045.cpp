#include <iostream>

using namespace std;

// Prototype declared above main
int swapValues(int param);

int main() {
    const int testVal = 90;
    int output = swapValues(testVal);
    cout << "Result for " << testVal << " is: " << output << endl;
    return 0;
}

// Definition below main
int swapValues(int param) {
    if (param < 0) {
        return 0;
    }
    return param + 5;
}
