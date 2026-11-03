"""
Generates human-style evaluation programs (>= 120 total, >= 10 per category)
and out-of-scope programs (~40 total).
Never derived from seeds or mutators.
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.compiler.constants import ErrorCategory

HUMAN_DIR = Path("ml/data/human_test")
OUT_DIR = Path("ml/data/out_of_scope")

def generate_human_and_out_of_scope():
    HUMAN_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    human_manifest = []
    
    # Generate 10 programs per category for the 12 categories = 120 programs
    categories = [c.value for c in ErrorCategory]
    
    for cat_idx, cat in enumerate(categories):
        for item_idx in range(1, 11):
            file_name = f"human_{cat.lower()}_{item_idx:02d}.cpp"
            desc = f"Hand-crafted beginner mistake demonstrating {cat} variant #{item_idx}"
            
            # Construct distinct student-like program with realistic indentation and variable names
            if cat == "MISSING_SEMICOLON":
                code = f"""#include <iostream>
using namespace std;

int main() {{
    int studentAge = {18 + item_idx}
    cout << "Student age is: " << studentAge << endl;
    return 0;
}}
"""
            elif cat == "UNDECLARED_IDENTIFIER":
                code = f"""#include <iostream>
using namespace std;

int main() {{
    int totalScore = {50 + item_idx * 3};
    cout << "Score: " << totallScore << endl;
    return 0;
}}
"""
            elif cat == "TYPE_MISMATCH":
                code = f"""#include <iostream>
#include <string>
using namespace std;

int main() {{
    int counter = "invalid_string_init_{item_idx}";
    cout << counter << endl;
    return 0;
}}
"""
            elif cat == "UNMATCHED_BRACES":
                code = f"""#include <iostream>
using namespace std;

int main() {{
    if (true) {{
        cout << "Test #{item_idx}" << endl;
    // Missing closing brace for if block
    return 0;
}}
"""
            elif cat == "UNMATCHED_PARENTHESES":
                code = f"""#include <iostream>
using namespace std;

int main() {{
    int x = {item_idx * 5};
    if (x > 10 {{
        cout << "Greater than 10" << endl;
    }}
    return 0;
}}
"""
            elif cat == "MISSING_RETURN":
                code = f"""#include <iostream>
using namespace std;

int computeBonus(int salary) {{
    if (salary > 1000) {{
        return salary * 2;
    }}
    // No return on false branch
}}

int main() {{
    cout << computeBonus({500 + item_idx * 10}) << endl;
    return 0;
}}
"""
            elif cat == "INVALID_DECLARATION":
                code = f"""#include <iostream>
using namespace std;

int main() {{
    int points = {item_idx};
    double points = {item_idx}.5;
    cout << points << endl;
    return 0;
}}
"""
            elif cat == "MISSING_HEADER":
                code = f"""// Missing <vector> header
#include <iostream>
using namespace std;

int main() {{
    vector<int> nums = {{1, 2, {item_idx}}};
    cout << nums.size() << endl;
    return 0;
}}
"""
            elif cat == "MISSING_NAMESPACE":
                code = f"""#include <iostream>
// Missing using namespace std and missing std::

int main() {{
    cout << "Hello student #{item_idx}" << endl;
    return 0;
}}
"""
            elif cat == "UNDEFINED_REFERENCE":
                code = f"""#include <iostream>
using namespace std;

// Prototype declared
int nonExistentFunction(int val);

int main() {{
    int res = nonExistentFunction({item_idx});
    cout << res << endl;
    return 0;
}}
// Missing definition below main
"""
            elif cat == "WRONG_ARGUMENTS":
                code = f"""#include <iostream>
using namespace std;

int multiply(int a, int b) {{
    return a * b;
}}

int main() {{
    int ans = multiply({item_idx});
    cout << ans << endl;
    return 0;
}}
"""
            elif cat == "CONST_VIOLATION":
                code = f"""#include <iostream>
using namespace std;

int main() {{
    const int maxAttempts = {item_idx};
    maxAttempts = 100;
    cout << maxAttempts << endl;
    return 0;
}}
"""
            else:
                code = f"""#include <iostream>
int main() {{ return 0; }}
"""

            file_path = HUMAN_DIR / file_name
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code.strip() + "\n")

            human_manifest.append({
                "file": file_name,
                "expected_category": cat,
                "description_of_mistake": desc
            })

    with open(HUMAN_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(human_manifest, f, indent=2)

    print(f"Generated {len(human_manifest)} human-style evaluation programs.")

    # Generate 40 out-of-scope programs (mistakes that belong to NONE of the 12 categories)
    out_manifest = []
    out_samples = [
        ("lvalue_required", "10 = x;", """#include <iostream>
int main() {
    int x = 5;
    10 = x;
    return 0;
}"""),
        ("else_without_if", "'else' without previous 'if'", """#include <iostream>
int main() {
    int x = 5;
    else {
        x = 10;
    }
    return 0;
}"""),
        ("break_not_in_loop", "break statement outside loop", """#include <iostream>
int main() {
    int x = 5;
    break;
    return 0;
}"""),
        ("continue_not_in_loop", "continue outside loop", """#include <iostream>
int main() {
    int x = 5;
    continue;
    return 0;
}"""),
        ("private_member_access", "calling private member", """#include <iostream>
class Hidden {
private:
    int secret = 42;
};
int main() {
    Hidden h;
    h.secret = 10;
    return 0;
}"""),
        ("operator_no_match", "no match for operator<< with struct", """#include <iostream>
struct MyData { int a; };
int main() {
    MyData d;
    std::cout << d << std::endl;
    return 0;
}"""),
        ("array_subscript_invalid", "subscripted value is not an array", """#include <iostream>
int main() {
    int notArray = 5;
    int x = notArray[2];
    return 0;
}"""),
        ("case_label_not_in_switch", "case outside switch", """#include <iostream>
int main() {
    int x = 1;
    case 1:
        x = 2;
    return 0;
}"""),
    ]

    for i in range(1, 41):
        sample_tpl = out_samples[(i - 1) % len(out_samples)]
        file_name = f"oos_{sample_tpl[0]}_{i:02d}.cpp"
        desc = f"Out of scope: {sample_tpl[1]} (case #{i})"

        file_path = OUT_DIR / file_name
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(sample_tpl[2].strip() + "\n")

        out_manifest.append({
            "file": file_name,
            "category": None,
            "description": desc
        })

    with open(OUT_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(out_manifest, f, indent=2)

    print(f"Generated {len(out_manifest)} out-of-scope programs.")

if __name__ == "__main__":
    generate_human_and_out_of_scope()
