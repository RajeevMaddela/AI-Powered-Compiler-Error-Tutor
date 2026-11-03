#include <iostream>
#include <string>
#include <map>
#include <vector>

int main() {
    std::vector<std::string> words = {"apple", "banana", "apple", "orange", "banana", "apple"};
    std::map<std::string, int> freq;

    for (const auto& w : words) {
        freq[w]++;
    }

    for (const auto& pair : freq) {
        std::cout << pair.first << ": " << pair.second << std::endl;
    }
    return 0;
}
