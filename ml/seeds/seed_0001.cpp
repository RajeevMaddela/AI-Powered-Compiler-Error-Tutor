#include <iostream>
#include <iomanip>

using namespace std;

double celsiusToFahrenheit(const double celsius);

int main() {
    const double tempC = 25.0;
    double tempF = celsiusToFahrenheit(tempC);
    cout << fixed << setprecision(2);
    cout << "Celsius: " << tempC << " -> Fahrenheit: " << tempF << endl;
    return 0;
}

double celsiusToFahrenheit(const double celsius) {
    return (celsius * 9.0 / 5.0) + 32.0;
}
