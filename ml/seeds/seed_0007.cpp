#include <iostream>
#include <vector>

using namespace std;

char computeLetterGrade(double average);

int main() {
    vector<double> scores = {85.0, 92.5, 78.0, 90.0};
    double sum = 0.0;
    for (double score : scores) {
        sum += score;
    }
    double avg = sum / scores.size();
    char grade = computeLetterGrade(avg);
    cout << "Average: " << avg << " -> Grade: " << grade << endl;
    return 0;
}

char computeLetterGrade(double average) {
    if (average >= 90.0) return 'A';
    if (average >= 80.0) return 'B';
    if (average >= 70.0) return 'C';
    if (average >= 60.0) return 'D';
    return 'F';
}
