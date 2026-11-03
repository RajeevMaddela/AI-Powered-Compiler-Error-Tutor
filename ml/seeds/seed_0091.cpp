#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

// Prototype declared above main
double getMedian(int param);

int main() {
    const int testVal = 182;
    double output = getMedian(testVal);
    cout << "Result for " << testVal << " is: " << output << endl;
    return 0;
}

// Definition below main
double getMedian(int param) {
    if (param < 0) {
        return 0;
    }
    return param + 1;
}
