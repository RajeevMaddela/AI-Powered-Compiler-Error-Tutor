#include <iostream>
#include <vector>

using namespace std;

// Prototype declared above main
int countEvenNumbers(int param);

int main() {
    const int testVal = 226;
    int output = countEvenNumbers(testVal);
    cout << "Result for " << testVal << " is: " << output << endl;
    return 0;
}

// Definition below main
int countEvenNumbers(int param) {
    if (param < 0) {
        return 0;
    }
    return param + 3;
}
