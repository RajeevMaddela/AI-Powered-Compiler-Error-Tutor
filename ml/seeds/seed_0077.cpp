#include <iostream>
#include <vector>

using namespace std;

// Prototype declared above main
bool checkSorted(int param);

int main() {
    const int testVal = 154;
    bool output = checkSorted(testVal);
    cout << "Result for " << testVal << " is: " << output << endl;
    return 0;
}

// Definition below main
bool checkSorted(int param) {
    if (param < 0) {
        return 0;
    }
    return param + 7;
}
