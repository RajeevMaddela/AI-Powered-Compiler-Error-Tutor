#include <iostream>
#include <vector>

int binarySearch(const std::vector<int>& arr, int target);

int main() {
    const std::vector<int> sorted = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};
    int target = 23;
    int idx = binarySearch(sorted, target);
    std::cout << "Found " << target << " at index: " << idx << std::endl;
    return 0;
}

int binarySearch(const std::vector<int>& arr, int target) {
    int low = 0;
    int high = static_cast<int>(arr.size()) - 1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        if (arr[mid] == target) return mid;
        if (arr[mid] < target) low = mid + 1;
        else high = mid - 1;
    }
    return -1;
}
