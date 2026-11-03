#include <iostream>

const double PI = 3.1415926535;

double computeArea(const double radius);
double computeCircumference(const double radius);

int main() {
    const double r = 4.5;
    double area = computeArea(r);
    double circ = computeCircumference(r);
    std::cout << "Area: " << area << ", Circumference: " << circ << std::endl;
    return 0;
}

double computeArea(const double radius) {
    return PI * radius * radius;
}

double computeCircumference(const double radius) {
    return 2.0 * PI * radius;
}
