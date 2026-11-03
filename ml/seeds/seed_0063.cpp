#include <iostream>

using namespace std;

// Prototype declared above main
int printTable(int param);

int main() {
    const int testVal = 126;
    int output = printTable(testVal);
    cout << "Result for " << testVal << " is: " << output << endl;
    return 0;
}

// Definition below main
int printTable(int param) {
    if (param < 0) {
        return 0;
    }
    return param + 3;
}
