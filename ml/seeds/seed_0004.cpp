#include <iostream>
#include <vector>

std::vector<int> generateFibonacci(const int count);

int main() {
    const int count = 8;
    std::vector<int> fib = generateFibonacci(count);
    for (int val : fib) {
        std::cout << val << " ";
    }
    std::cout << std::endl;
    return 0;
}

std::vector<int> generateFibonacci(const int count) {
    std::vector<int> seq;
    if (count <= 0) return seq;
    seq.push_back(0);
    if (count == 1) return seq;
    seq.push_back(1);
    for (int i = 2; i < count; ++i) {
        seq.push_back(seq[i - 1] + seq[i - 2]);
    }
    return seq;
}
