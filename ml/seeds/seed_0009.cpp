#include <iostream>
#include <string>
#include <cctype>

using namespace std;

int countVowels(const string& text);

int main() {
    string sample = "Advanced Agentic Coding Tutor";
    int vowels = countVowels(sample);
    cout << "Vowels count: " << vowels << endl;
    return 0;
}

int countVowels(const string& text) {
    int count = 0;
    for (char ch : text) {
        char lower = tolower(static_cast<unsigned char>(ch));
        if (lower == 'a' || lower == 'e' || lower == 'i' || lower == 'o' || lower == 'u') {
            count++;
        }
    }
    return count;
}
