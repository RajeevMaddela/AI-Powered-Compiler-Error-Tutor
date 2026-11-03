#include <iostream>
using namespace std;

int computeBonus(int salary) {
    if (salary > 1000) {
        return salary * 2;
    }
    // No return on false branch
}

int main() {
    cout << computeBonus(540) << endl;
    return 0;
}
