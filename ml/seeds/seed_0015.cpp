#include <iostream>

using namespace std;

struct ComplexNumber {
    double real;
    double imag;
};

ComplexNumber addComplex(const ComplexNumber& a, const ComplexNumber& b);

int main() {
    ComplexNumber c1 = {3.0, 4.5};
    ComplexNumber c2 = {1.5, 2.0};
    ComplexNumber sum = addComplex(c1, c2);
    cout << "Sum: " << sum.real << " + " << sum.imag << "i" << endl;
    return 0;
}

ComplexNumber addComplex(const ComplexNumber& a, const ComplexNumber& b) {
    ComplexNumber res;
    res.real = a.real + b.real;
    res.imag = a.imag + b.imag;
    return res;
}
