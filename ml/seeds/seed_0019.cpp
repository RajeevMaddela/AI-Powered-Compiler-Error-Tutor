#include <iostream>

using namespace std;

double computePower(double base, int exponent);

int main() {
    const double b = 2.5;
    const int exp = 3;
    double p = computePower(b, exp);
    cout << b << " ^ " << exp << " = " << p << endl;
    return 0;
}

double computePower(double base, int exponent) {
    double result = 1.0;
    for (int i = 0; i < exponent; ++i) {
        result *= base;
    }
    return result;
}
