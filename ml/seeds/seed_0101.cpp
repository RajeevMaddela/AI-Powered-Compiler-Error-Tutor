#include <iostream>
#include <string>

using namespace std;

// Prototype declared above main
int getStringLength(int param);

int main() {
    const int testVal = 202;
    int output = getStringLength(testVal);
    cout << "Result for " << testVal << " is: " << output << endl;
    return 0;
}

// Definition below main
int getStringLength(int param) {
    if (param < 0) {
        return 0;
    }
    return param + 1;
}
