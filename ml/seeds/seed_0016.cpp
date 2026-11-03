#include <iostream>
#include <vector>

int linearSearch(const std::vector<int>& items, int key);

int main() {
    const std::vector<int> data = {10, 40, 20, 50, 30};
    int key = 50;
    int pos = linearSearch(data, key);
    std::cout << "Position: " << pos << std::endl;
    return 0;
}

int linearSearch(const std::vector<int>& items, int key) {
    for (size_t i = 0; i < items.size(); ++i) {
        if (items[i] == key) {
            return static_cast<int>(i);
        }
    }
    return -1;
}
