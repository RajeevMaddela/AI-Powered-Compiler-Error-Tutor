import os
import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

SEEDS_DIR = Path(__file__).resolve().parent

# Templates for 125 unique C++17 programs covering intro through intermediate topics
# Ensuring each satisfies:
# 1. 10-60 lines
# 2. Compiles with 0 errors, 0 warnings under -std=c++17 -Wall -Wextra -Werror=return-type
# 3. Features prototypes above main, definitions below main, classes, const, vectors, strings, maps, loops

PROGRAMS = [
    # 1. Temperature Conversion (using namespace std)
    {
        "id": "seed_0001",
        "topic": "temperature_conversion",
        "style": "using_namespace_std",
        "headers": ["iostream", "iomanip"],
        "features": ["has_helper_function", "has_prototype", "has_const"],
        "code": """#include <iostream>
#include <iomanip>

using namespace std;

// Prototype
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
"""
    },
    # 2. Circle Area & Circumference (std_prefix)
    {
        "id": "seed_0002",
        "topic": "geometry_circle",
        "style": "std_prefix",
        "headers": ["iostream"],
        "features": ["has_helper_function", "has_prototype", "has_const"],
        "code": """#include <iostream>

const double PI = 3.1415926535;

double computeArea(const double radius);
double computeCircumference(const double radius);

int main() {
    const double r = 4.5;
    double area = computeArea(r);
    double circ = computeCircumference(r);
    std::cout << "Area: " << area << ", Circumference: " << circ << std::endl;
    return 0;
}

double computeArea(const double radius) {
    return PI * radius * radius;
}

double computeCircumference(const double radius) {
    return 2.0 * PI * radius;
}
"""
    },
    # 3. Factorial iterative (using namespace std)
    {
        "id": "seed_0003",
        "topic": "factorial_iterative",
        "style": "using_namespace_std",
        "headers": ["iostream"],
        "features": ["has_helper_function", "has_prototype", "has_loop", "has_const"],
        "code": """#include <iostream>

using namespace std;

long long calculateFactorial(const int n);

int main() {
    const int number = 6;
    long long fact = calculateFactorial(number);
    cout << "Factorial of " << number << " is " << fact << endl;
    return 0;
}

long long calculateFactorial(const int n) {
    long long result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}
"""
    },
    # 4. Fibonacci Array Generator (std_prefix)
    {
        "id": "seed_0004",
        "topic": "fibonacci_vector",
        "style": "std_prefix",
        "headers": ["iostream", "vector"],
        "features": ["has_helper_function", "has_prototype", "uses_vector", "has_loop", "has_const"],
        "code": """#include <iostream>
#include <vector>

std::vector<int> generateFibonacci(const int count);

int main() {
    const int count = 8;
    std::vector<int> fib = generateFibonacci(count);
    for (int val : fib) {
        std::cout << val << " ";
    }
    std::cout << std::endl;
    return 0;
}

std::vector<int> generateFibonacci(const int count) {
    std::vector<int> seq;
    if (count <= 0) return seq;
    seq.push_back(0);
    if (count == 1) return seq;
    seq.push_back(1);
    for (int i = 2; i < count; ++i) {
        seq.push_back(seq[i - 1] + seq[i - 2]);
    }
    return seq;
}
"""
    },
    # 5. String Reversal (using namespace std)
    {
        "id": "seed_0005",
        "topic": "string_reversal",
        "style": "using_namespace_std",
        "headers": ["iostream", "string"],
        "features": ["has_helper_function", "has_prototype", "uses_string", "has_loop"],
        "code": """#include <iostream>
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
"""
    },
    # 6. Bank Account Class (std_prefix)
    {
        "id": "seed_0006",
        "topic": "bank_account_class",
        "style": "std_prefix",
        "headers": ["iostream", "string"],
        "features": ["has_class", "has_const", "uses_string"],
        "code": """#include <iostream>
#include <string>

class BankAccount {
private:
    std::string owner;
    double balance;

public:
    BankAccount(const std::string& name, double initial) : owner(name), balance(initial) {}

    void deposit(double amount) {
        if (amount > 0.0) {
            balance += amount;
        }
    }

    double getBalance() const {
        return balance;
    }

    std::string getOwner() const {
        return owner;
    }
};

int main() {
    BankAccount account("Alice", 150.0);
    account.deposit(75.5);
    std::cout << account.getOwner() << " has balance: " << account.getBalance() << std::endl;
    return 0;
}
"""
    },
    # 7. Student Grade Calculator (using namespace std)
    {
        "id": "seed_0007",
        "topic": "student_grades",
        "style": "using_namespace_std",
        "headers": ["iostream", "vector", "string"],
        "features": ["has_helper_function", "has_prototype", "uses_vector", "uses_string", "has_loop", "has_const"],
        "code": """#include <iostream>
#include <vector>
#include <string>

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
"""
    },
    # 8. Prime Number Checker (std_prefix)
    {
        "id": "seed_0008",
        "topic": "prime_checker",
        "style": "std_prefix",
        "headers": ["iostream"],
        "features": ["has_helper_function", "has_prototype", "has_loop", "has_const"],
        "code": """#include <iostream>

bool isPrime(int n);

int main() {
    const int val = 29;
    if (isPrime(val)) {
        std::cout << val << " is a prime number." << std::endl;
    } else {
        std::cout << val << " is not prime." << std::endl;
    }
    return 0;
}

bool isPrime(int n) {
    if (n <= 1) return false;
    for (int i = 2; i * i <= n; ++i) {
        if (n % i == 0) return false;
    }
    return true;
}
"""
    },
    # 9. Vowel Count in String (using namespace std)
    {
        "id": "seed_0009",
        "topic": "vowel_counter",
        "style": "using_namespace_std",
        "headers": ["iostream", "string", "cctype"],
        "features": ["has_helper_function", "has_prototype", "uses_string", "has_loop"],
        "code": """#include <iostream>
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
"""
    },
    # 10. Word Frequency Map (std_prefix)
    {
        "id": "seed_0010",
        "topic": "word_frequency",
        "style": "std_prefix",
        "headers": ["iostream", "string", "map", "vector"],
        "features": ["uses_map", "uses_vector", "uses_string", "has_loop"],
        "code": """#include <iostream>
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
"""
    }
]

def generate_all_seeds():
    SEEDS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    
    # We load or expand the full 125 programs
    # Write modular generator script that creates seeds 0001 through 0125
    from ml.seeds.seed_generator_data import ALL_125_SEEDS
    
    for seed_data in ALL_125_SEEDS:
        seed_id = seed_data["id"]
        filename = f"{seed_id}.cpp"
        file_path = SEEDS_DIR / filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(seed_data["code"].strip() + "\n")
            
        manifest.append({
            "seed_id": seed_id,
            "file": filename,
            "topic": seed_data["topic"],
            "style": seed_data["style"],
            "headers": seed_data["headers"],
            "features": seed_data["features"]
        })
        
    manifest_path = SEEDS_DIR / "seeds_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Generated {len(manifest)} seed programs and saved to {manifest_path}")

if __name__ == "__main__":
    generate_all_seeds()
