#include <iostream>
#include <vector>

using namespace std;

int sumMatrix(const vector<vector<int>>& mat);

int main() {
    vector<vector<int>> matrix = {
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9}
    };
    int total = sumMatrix(matrix);
    cout << "Total matrix sum: " << total << endl;
    return 0;
}

int sumMatrix(const vector<vector<int>>& mat) {
    int sum = 0;
    for (const auto& row : mat) {
        for (int val : row) {
            sum += val;
        }
    }
    return sum;
}
