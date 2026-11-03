#include <iostream>

using namespace std;

int computeGCD(int a, int b);
int computeLCM(int a, int b);

int main() {
    int x = 24;
    int y = 36;
    int g = computeGCD(x, y);
    int l = computeLCM(x, y);
    cout << "GCD: " << g << ", LCM: " << l << endl;
    return 0;
}

int computeGCD(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

int computeLCM(int a, int b) {
    if (a == 0 || b == 0) return 0;
    return (a * b) / computeGCD(a, b);
}
