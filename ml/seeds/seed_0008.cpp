#include <iostream>

bool isPrime(int n);

int main() {
    const int val = 29;
    if (isPrime(val)) {
        std::cout << val << " is a prime number." << std::endl;
    } else {
        std::cout << val << " is not prime." << std::endl;
    }
    return 0;
}

bool isPrime(int n) {
    if (n <= 1) return false;
    for (int i = 2; i * i <= n; ++i) {
        if (n % i == 0) return false;
    }
    return true;
}
