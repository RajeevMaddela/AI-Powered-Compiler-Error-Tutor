import re
from typing import Dict, Any, List, Optional
from backend.app.compiler.constants import ErrorCategory

EXPLANATION_TEMPLATES: Dict[str, Dict[str, Any]] = {
    ErrorCategory.MISSING_SEMICOLON.value: {
        "title": "Missing Semicolon (;)",
        "summary": "A C++ statement, variable declaration, or struct definition is missing its terminating semicolon.",
        "what_happened": "In C++, semicolons are mandatory statement terminators. The compiler was expecting a semicolon at the end of the previous statement or declaration before reading the next token.",
        "how_to_fix": [
            "Inspect the affected line and the line immediately preceding it.",
            "Make sure every statement (assignments, declarations, cout/cin calls, return statements) ends with a semicolon ';'.",
            "If defining a `struct` or `class`, ensure a semicolon follows the closing brace: `struct MyData { ... };`.",
            "Do NOT place a semicolon after function headers like `int main()` or after `if (...)` conditions."
        ],
        "example_wrong": """int count = 10\nstd::cout << count << std::endl;""",
        "example_fixed": """int count = 10; // Added semicolon here\nstd::cout << count << std::endl;"""
    },

    ErrorCategory.UNDECLARED_IDENTIFIER.value: {
        "title": "Undeclared Identifier",
        "summary": "The name or variable is being used without having been declared, or is misspelled.",
        "what_happened": "The compiler encountered an identifier that has not been defined in the current scope. This usually means a typo in the variable/function name, using a variable before defining it, or defining it inside a different block.",
        "how_to_fix": [
            "Check for typos: verify the spelling and letter casing matches the declaration (C++ is case-sensitive).",
            "Verify that the variable is declared *above* its first use.",
            "Check variable scope: if declared inside an `if` block or `for` loop, it cannot be used outside that block."
        ],
        "example_wrong": """int totalScore = 100;\nstd::cout << totallScore; // Typo in variable name""",
        "example_fixed": """int totalScore = 100;\nstd::cout << totalScore; // Corrected spelling"""
    },

    ErrorCategory.TYPE_MISMATCH.value: {
        "title": "Type Mismatch / Incompatible Types",
        "summary": "Attempting to assign or convert between incompatible data types.",
        "what_happened": "The compiler cannot convert a value from one type to another (for example, assigning a text string to an integer variable, or returning an incompatible type).",
        "how_to_fix": [
            "Check the variable type and the value assigned to it.",
            "If converting numbers to strings or vice-versa, use `std::to_string()` or `std::stoi()`.",
            "If converting between numerical types (e.g. double to int), use explicit casting: `static_cast<int>(val)`."
        ],
        "example_wrong": """int score = "100"; // Cannot assign string literal to int""",
        "example_fixed": """int score = 100; // Directly assign integer value\n// Or: int score = std::stoi("100");"""
    },

    ErrorCategory.UNMATCHED_BRACES.value: {
        "title": "Unmatched Curly Braces { }",
        "summary": "A block is missing its opening '{' or closing '}' brace.",
        "what_happened": "The compiler reached the end of the file or encountered a misplaced statement because the opening and closing curly braces do not balance out.",
        "how_to_fix": [
            "Check indentation to see which block (function, if, loop, or class) remains unclosed.",
            "Count your opening '{' and closing '}' braces — they must always match in pairs.",
            "Look for an extra or premature '}' placed in the middle of a function."
        ],
        "example_wrong": """void show() {\n    if (true) {\n        std::cout << "Hi";\n    // Missing closing brace for if block\n}""",
        "example_fixed": """void show() {\n    if (true) {\n        std::cout << "Hi";\n    } // Added closing brace\n}"""
    },

    ErrorCategory.UNMATCHED_PARENTHESES.value: {
        "title": "Unmatched Parentheses ( )",
        "summary": "A condition or function call is missing an opening '(' or closing ')' parenthesis.",
        "what_happened": "Parentheses in an `if` statement, `while` loop, or function call are not properly balanced.",
        "how_to_fix": [
            "Check the line where the error occurred and ensure every '(' has a matching ')'.",
            "Remember that `if` and `while` conditions must be enclosed in parentheses: `if (condition)`.",
            "Check function calls: `myFunction(arg1, arg2);`."
        ],
        "example_wrong": """if (score > 50 {\n    std::cout << "Passed";\n}""",
        "example_fixed": """if (score > 50) { // Added closing parenthesis\n    std::cout << "Passed";\n}"""
    },

    ErrorCategory.MISSING_RETURN.value: {
        "title": "Missing Return Statement",
        "summary": "A non-void function finishes without returning a value.",
        "what_happened": "The function's signature declares that it returns a type (like `int` or `double`), but execution reaches the end of the function (or some branches) without executing a `return` statement.",
        "how_to_fix": [
            "If the function is not supposed to return anything, change its return type to `void`.",
            "If the function returns a value, ensure all code paths (including every `if`/`else` branch) end with `return value;`."
        ],
        "example_wrong": """int getMultiplier(bool doubleIt) {\n    if (doubleIt) return 2;\n    // Missing return when doubleIt is false\n}""",
        "example_fixed": """int getMultiplier(bool doubleIt) {\n    if (doubleIt) return 2;\n    return 1; // Return on all paths\n}"""
    },

    ErrorCategory.INVALID_DECLARATION.value: {
        "title": "Invalid or Conflicting Declaration",
        "summary": "Redeclaring an existing variable or using invalid declaration syntax.",
        "what_happened": "A variable was declared twice in the same scope with conflicting types, declared as `void`, or declared using `auto` without an initializer.",
        "how_to_fix": [
            "Check if the variable has already been declared earlier in the same function or block.",
            "Do not specify the type again when reassigning a variable (`x = 10;` instead of `int x = 10;`).",
            "Variables cannot have type `void`. If using `auto`, you must initialize it: `auto x = 5;`."
        ],
        "example_wrong": """int score = 50;\ndouble score = 75.5; // Redeclaring 'score'""",
        "example_fixed": """int score = 50;\nscore = 75; // Reassignment without redeclaring type"""
    },

    ErrorCategory.MISSING_HEADER.value: {
        "title": "Missing Header Include",
        "summary": "A standard library feature is used without including its corresponding `#include` header.",
        "what_happened": "You are using standard library classes or functions (such as `std::vector`, `std::string`, or `std::cout`), but the required `#include <...>` directive is missing from the top of the file.",
        "how_to_fix": [
            "Add the required header at the top of the file:",
            "- For `cout`, `cin`, `endl`: `#include <iostream>`",
            "- For `vector`: `#include <vector>`",
            "- For `string`: `#include <string>`",
            "- For `map`: `#include <map>`",
            "- For math functions: `#include <cmath>`"
        ],
        "example_wrong": """// Missing #include <vector>\nint main() {\n    std::vector<int> nums;\n}""",
        "example_fixed": """#include <vector> // Added required header\nint main() {\n    std::vector<int> nums;\n}"""
    },

    ErrorCategory.MISSING_NAMESPACE.value: {
        "title": "Missing Namespace Qualification (`std::`)",
        "summary": "Using standard library names without `std::` prefix or `using namespace std;`.",
        "what_happened": "C++ standard library entities live inside the `std` namespace. When referenced without `std::` or without declaring `using namespace std;`, the compiler does not recognize them.",
        "how_to_fix": [
            "Option A: Add `using namespace std;` near the top of the file after the `#include` directives.",
            "Option B (Recommended C++ style): Prefix standard entities with `std::` (e.g. `std::cout`, `std::endl`, `std::string`)."
        ],
        "example_wrong": """#include <iostream>\nint main() {\n    cout << "Hello"; // 'cout' not recognized\n}""",
        "example_fixed": """#include <iostream>\nusing namespace std; // Added using directive\nint main() {\n    cout << "Hello";\n}"""
    },

    ErrorCategory.UNDEFINED_REFERENCE.value: {
        "title": "Undefined Reference (Linker Error)",
        "summary": "A function or variable was declared and called, but never implemented (defined).",
        "what_happened": "Compilation of the syntax succeeded, but during the linking phase, the linker could not find the compiled body/definition of a function being called.",
        "how_to_fix": [
            "Check that you implemented the function body below `main` or in an included file.",
            "Check function signature: parameter types in the function definition must exactly match the prototype declaration.",
            "Ensure you did not accidentally misspell the function name in the definition."
        ],
        "example_wrong": """int computeArea(int w, int h); // Prototype\nint main() {\n    int a = computeArea(4, 5); // Called here\n}\n// Definition is missing!""",
        "example_fixed": """int computeArea(int w, int h); // Prototype\nint main() {\n    int a = computeArea(4, 5);\n}\nint computeArea(int w, int h) {\n    return w * h; // Added definition\n}"""
    },

    ErrorCategory.WRONG_ARGUMENTS.value: {
        "title": "Incorrect Function Arguments",
        "summary": "Calling a function with the wrong number of arguments or incompatible argument types.",
        "what_happened": "The function call does not match any known declaration. Either too many or too few arguments were passed, or the argument types cannot be converted to the parameter types.",
        "how_to_fix": [
            "Check the function prototype or definition to see how many parameters it expects.",
            "Verify the types of each argument being passed.",
            "Ensure default arguments (if any) are properly declared."
        ],
        "example_wrong": """int add(int a, int b) { return a + b; }\nint main() {\n    int sum = add(5); // Error: expects 2 arguments\n}""",
        "example_fixed": """int add(int a, int b) { return a + b; }\nint main() {\n    int sum = add(5, 10); // Correct: 2 arguments\n}"""
    },

    ErrorCategory.CONST_VIOLATION.value: {
        "title": "Const Violation / Modifying Read-Only Variable",
        "summary": "Attempting to modify a variable or reference declared as `const`.",
        "what_happened": "The `const` keyword promises that the value will not change. The compiler caught an attempt to reassign, increment, or modify a `const` variable or pass a `const` object to a non-const parameter.",
        "how_to_fix": [
            "If the variable needs to change over time, remove the `const` qualifier.",
            "If the variable is meant to be constant, remove or adjust the line attempting to modify it.",
            "If calling a member function on a `const` object, ensure the member method is marked `const`."
        ],
        "example_wrong": """const int maxAttempts = 3;\nmaxAttempts = 5; // Error: modifying read-only variable""",
        "example_fixed": """int maxAttempts = 3; // Removed const so variable can be updated\nmaxAttempts = 5;"""
    }
}


def generate_explanation(
    category: Optional[str],
    line: Optional[int] = None,
    column: Optional[int] = None,
    raw_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates a deterministic, structured educational explanation for the given error category.
    """
    if not category or category not in EXPLANATION_TEMPLATES:
        return {
            "title": "General Compiler Diagnostic",
            "summary": "Review the compiler message and check the affected line for syntax or type errors.",
            "what_happened": raw_message or "The compiler reported an issue at this line.",
            "where": f"Line {line}" if line else "Compilation Unit",
            "how_to_fix": [
                "Inspect the reported line and surrounding code.",
                "Review the compiler diagnostic details.",
                "Verify variable names, types, and closing delimiters."
            ],
            "example_wrong": "",
            "example_fixed": ""
        }

    template = EXPLANATION_TEMPLATES[category]
    where_text = f"Line {line}" + (f", Column {column}" if column else "") if line else "Compilation stage"

    return {
        "title": template["title"],
        "summary": template["summary"],
        "what_happened": template["what_happened"],
        "where": where_text,
        "how_to_fix": list(template["how_to_fix"]),
        "example_wrong": template["example_wrong"],
        "example_fixed": template["example_fixed"]
    }

