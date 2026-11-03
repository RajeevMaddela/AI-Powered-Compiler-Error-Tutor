#include <iostream>
using namespace std;

// Prototype declared
int nonExistentFunction(int val);

int main() {
    int res = nonExistentFunction(7);
    cout << res << endl;
    return 0;
}
// Missing definition below main
