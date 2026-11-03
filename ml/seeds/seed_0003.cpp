#include <iostream>

using namespace std;

long long calculateFactorial(const int n);

int main() {
    const int number = 6;
    long long fact = calculateFactorial(number);
    cout << "Factorial of " << number << " is " << fact << endl;
    return 0;
}

long long calculateFactorial(const int n) {
    long long result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}
