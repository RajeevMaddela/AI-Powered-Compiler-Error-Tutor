#include <iostream>
#include <string>

bool isPalindrome(const std::string& str);

int main() {
    std::string test = "racecar";
    if (isPalindrome(test)) {
        std::cout << test << " is a palindrome." << std::endl;
    } else {
        std::cout << test << " is not a palindrome." << std::endl;
    }
    return 0;
}

bool isPalindrome(const std::string& str) {
    int i = 0;
    int j = static_cast<int>(str.length()) - 1;
    while (i < j) {
        if (str[i] != str[j]) return false;
        i++;
        j--;
    }
    return true;
}
