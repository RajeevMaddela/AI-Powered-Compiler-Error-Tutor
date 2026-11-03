#include <iostream>
#include <string>

using namespace std;

string reverseString(const string& input);

int main() {
    string word = "CompilerTutor";
    string rev = reverseString(word);
    cout << "Original: " << word << ", Reversed: " << rev << endl;
    return 0;
}

string reverseString(const string& input) {
    string output = input;
    int left = 0;
    int right = static_cast<int>(output.length()) - 1;
    while (left < right) {
        char temp = output[left];
        output[left] = output[right];
        output[right] = temp;
        left++;
        right--;
    }
    return output;
}
