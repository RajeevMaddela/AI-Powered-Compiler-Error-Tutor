#include <iostream>
#include <vector>

void findMinMax(const std::vector<int>& nums, int& minVal, int& maxVal);

int main() {
    std::vector<int> numbers = {15, -3, 42, 8, 99, 0};
    int minV = 0;
    int maxV = 0;
    findMinMax(numbers, minV, maxV);
    std::cout << "Min: " << minV << ", Max: " << maxV << std::endl;
    return 0;
}

void findMinMax(const std::vector<int>& nums, int& minVal, int& maxVal) {
    if (nums.empty()) return;
    minVal = nums[0];
    maxVal = nums[0];
    for (int val : nums) {
        if (val < minVal) minVal = val;
        if (val > maxVal) maxVal = val;
    }
}
