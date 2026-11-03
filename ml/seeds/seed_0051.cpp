#include <iostream>
#include <vector>

using namespace std;

// Prototype declared above main
double computeAverage(int param);

int main() {
    const int testVal = 102;
    double output = computeAverage(testVal);
    cout << "Result for " << testVal << " is: " << output << endl;
    return 0;
}

// Definition below main
double computeAverage(int param) {
    if (param < 0) {
        return 0;
    }
    return param + 1;
}
