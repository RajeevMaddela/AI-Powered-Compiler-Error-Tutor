# Machine Learning Dataset Report (Module 2: M2.1 - M2.3)

## 1. Environment & Build Configuration
- **Image**: `tutor-sandbox:latest`
- **Compiler Flags**: `g++ -std=c++17 -Wall -Wextra -Werror=return-type -fno-diagnostics-show-caret -fmessage-length=0 -fdiagnostics-color=never /workspace/main.cpp -o /tmp/a.out`
- **Locale**: `LC_ALL=C, LANG=C` (straight ASCII single quotes)
- **RNG Seed**: 42 (fully reproducible build)
- **Total Seeds**: 125 (Train: 87, Val: 18, Test: 20)
- **Build Command**: `python -m ml.dataset.build_dataset --seed 42`

## 2. Dataset Distribution Summary
- **Total Mutants Accepted**: 3499
- **Total Mutants Rejected**: 1450
- **Human-Style Test Set**: 120 programs (isolated for evaluation only)
- **Out-Of-Scope Set**: 40 programs (isolated for threshold tuning)

| Category | Stage | Train | Val | Test | Total Accepted | Unique Messages | Target Status |
|---|---|---|---|---|---|:---:|:---:|
| `CONST_VIOLATION` | SEMANTIC | 85 | 20 | 19 | **124** | 18 | Adequate |
| `INVALID_DECLARATION` | SEMANTIC | 261 | 58 | 61 | **380** | 67 | Satisfied |
| `MISSING_HEADER` | SEMANTIC | 90 | 18 | 21 | **129** | 6 | Adequate |
| `MISSING_NAMESPACE` | SEMANTIC | 121 | 26 | 29 | **176** | 5 | Adequate |
| `MISSING_RETURN` | SEMANTIC | 241 | 51 | 54 | **346** | 9 | Adequate |
| `MISSING_SEMICOLON` | SYNTAX | 266 | 55 | 59 | **380** | 29 | Satisfied |
| `TYPE_MISMATCH` | SEMANTIC | 251 | 66 | 63 | **380** | 5 | Satisfied |
| `UNDECLARED_IDENTIFIER` | SEMANTIC | 263 | 56 | 61 | **380** | 94 | Satisfied |
| `UNDEFINED_REFERENCE` | LINKER | 94 | 18 | 19 | **131** | 131 | Adequate |
| `UNMATCHED_BRACES` | SYNTAX | 219 | 42 | 52 | **313** | 7 | Adequate |
| `UNMATCHED_PARENTHESES` | SYNTAX | 266 | 54 | 60 | **380** | 9 | Satisfied |
| `WRONG_ARGUMENTS` | SEMANTIC | 261 | 56 | 63 | **380** | 105 | Satisfied |

## 3. Diagnostic Message Diversity (Top Messages Per Category)
### `CONST_VIOLATION` (18 unique messages)
- `assignment of read-only variable 'testVal'` (105 records)
- `binding 'const int' to reference of type 'int&' discards qualifiers` (2 records)
- `assignment of read-only variable 'sum'` (2 records)
- `assignment of read-only variable 'tempC'` (1 records)
- `assignment of read-only variable 'number'` (1 records)

### `INVALID_DECLARATION` (67 unique messages)
- `declaration of 'auto output' has no initializer` (54 records)
- `two or more data types in declaration of 'output'` (52 records)
- `conflicting declaration 'double testVal'` (51 records)
- `variable or field 'output' declared void` (46 records)
- `declaration of 'auto testVal' has no initializer` (27 records)

### `MISSING_HEADER` (6 unique messages)
- `'cout' was not declared in this scope` (80 records)
- `'cout' is not a member of 'std'` (45 records)
- `'vector' is not a member of 'std'` (1 records)
- `'setprecision' was not declared in this scope` (1 records)
- `'vector' was not declared in this scope` (1 records)

### `MISSING_NAMESPACE` (5 unique messages)
- `'cout' was not declared in this scope` (122 records)
- `'endl' was not declared in this scope` (46 records)
- `'vector' was not declared in this scope` (4 records)
- `'string' was not declared in this scope` (3 records)
- `'map' was not declared in this scope` (1 records)

### `MISSING_RETURN` (9 unique messages)
- `control reaches end of non-void function [-Werror=return-type]` (108 records)
- `return-statement with no value, in function returning 'int' [-fpermissive]` (101 records)
- `return-statement with no value, in function returning 'double' [-fpermissive]` (75 records)
- `return-statement with no value, in function returning 'bool' [-fpermissive]` (30 records)
- `return-statement with no value, in function returning 'long long int' [-fpermissive]` (15 records)

### `MISSING_SEMICOLON` (29 unique messages)
- `expected ';' before '}' token` (175 records)
- `expected ';' before 'return'` (54 records)
- `expected ',' or ';' before 'cout'` (34 records)
- `expected ',' or ';' before 'int'` (24 records)
- `expected ',' or ';' before 'std'` (23 records)

### `TYPE_MISMATCH` (5 unique messages)
- `invalid conversion from 'const char*' to 'int' [-fpermissive]` (272 records)
- `cannot convert 'const char*' to 'double' in return` (57 records)
- `cannot convert 'const char*' to 'double' in initialization` (33 records)
- `invalid conversion from 'const char*' to 'long long int' [-fpermissive]` (15 records)
- `cannot convert 'const char*' to 'const double' in initialization` (3 records)

### `UNDECLARED_IDENTIFIER` (94 unique messages)
- `'paramX' was not declared in this scope` (69 records)
- `'testValX' was not declared in this scope` (48 records)
- `'outputX' was not declared in this scope` (38 records)
- `'param' was not declared in this scope` (33 records)
- `'testVal' was not declared in this scope` (32 records)

### `UNDEFINED_REFERENCE` (131 unique messages)
- `C:\Users\RAJEEV\AppData\Local\Temp\ccmbR1iB.o:main.cpp:(.text+0x54): undefined reference to `reverseString(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)'` (1 records)
- `C:\Users\RAJEEV\AppData\Local\Temp\ccU3rHOf.o:main.cpp:(.text+0x4d): undefined reference to `countVowels(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)'` (1 records)
- `C:\Users\RAJEEV\AppData\Local\Temp\cc3t9xCB.o:main.cpp:(.text+0x66): undefined reference to `binarySearch(std::vector<int, std::allocator<int> > const&, int)'` (1 records)
- `C:\Users\RAJEEV\AppData\Local\Temp\ccCTtM4q.o:main.cpp:(.text+0x66): undefined reference to `linearSearch(std::vector<int, std::allocator<int> > const&, int)'` (1 records)
- `C:\Users\RAJEEV\AppData\Local\Temp\ccikE6vV.o:main.cpp:(.text+0x13f): undefined reference to `sumMatrix(std::vector<std::vector<int, std::allocator<int> >, std::allocator<std::vector<int, std::allocator<int> > > > const&)'` (1 records)

### `UNMATCHED_BRACES` (7 unique messages)
- `expected '}' at end of input` (202 records)
- `a function-definition is not allowed here before '{' token` (97 records)
- `expected '}' before ';' token` (8 records)
- `expected '}' before 'else'` (2 records)
- `expected declaration before '}' token` (2 records)

### `UNMATCHED_PARENTHESES` (9 unique messages)
- `expected ')' before ';' token` (192 records)
- `expected initializer before ')' token` (90 records)
- `expected ')' before '{' token` (87 records)
- `expected ')' before 'return'` (4 records)
- `expected '(' before 'const'` (3 records)

### `WRONG_ARGUMENTS` (105 unique messages)
- `cannot convert 'const char*' to 'double' in initialization` (34 records)
- `too few arguments to function 'int reverseNumber(int)'` (7 records)
- `too many arguments to function 'int swapValues()'` (7 records)
- `too many arguments to function 'int printTable(int)'` (7 records)
- `too many arguments to function 'int countEvenNumbers(int)'` (7 records)


## 4. Rejection Analysis
Breakdown of reasons for rejected candidate mutants:
- **no_primary_diagnostic**: 331 mutants
- **unmatched_braces.unmatched_msg: expected unqualified-id before 'return'**: 271 mutants
- **wrong_arguments.unmatched_msg: invalid conversion from 'const char*' to 'int' [-fpermissive]**: 142 mutants
- **wrong_arguments.unmatched_msg: expected identifier before string constant**: 102 mutants
- **unmatched_parentheses.unmatched_msg: expected initializer before 'param'**: 87 mutants
- **unmatched_braces.unmatched_msg: expected initializer before 'int'**: 85 mutants
- **unmatched_braces.unmatched_msg: expected initializer before 'if'**: 79 mutants
- **semicolon.unmatched_msg: expected initializer before 'int'**: 55 mutants
- **undefined_reference.unmatched_msg: cannot convert 'char*' to 'double' in return**: 25 mutants
- **undefined_reference.unmatched_msg: invalid operands of types 'char*' and 'int' to binary 'operator*'**: 18 mutants

## 5. Category Analysis & Notes
- **`MISSING_HEADER` & `MISSING_NAMESPACE`**: Introductory C++ seed programs contain 1-2 headers and a single `using namespace std;` or explicit prefix. Mutating them produces 1-2 clean mutants per seed before hitting deduplication or transitive include preservation.
- **`UNDEFINED_REFERENCE`**: Exactly 117 seeds contained a separate function prototype and definition below `main` suitable for generating clean linker errors.
- **`CONST_VIOLATION`**: Seeds with explicit `const` variables produced 124 distinct mutants.
- **High-volume categories** (`MISSING_SEMICOLON`, `UNDECLARED_IDENTIFIER`, `TYPE_MISMATCH`, `UNMATCHED_PARENTHESES`, `INVALID_DECLARATION`): Successfully saturated at the 380 record target cap (capped at 6 records per seed to prevent dominance).

## 6. Privacy & Leakage Audits
- **Grouped Split Audit**: Confirmed zero seed overlap across train, val, and test splits (tested via `test_grouped_split_leakage`).
- **Human Test Isolation**: Confirmed that none of the 120 human-style evaluation programs or 40 out-of-scope programs share source hashes with the training dataset (tested via `test_human_test_isolation`).
- **Model-Facing CSV Privacy**: Confirmed that all exported CSV files (`train.csv`, `val.csv`, `test.csv`, `human_test.csv`, `out_of_scope.csv`) contain zero raw source code lines, satisfying M2.10 requirements (tested via `test_csv_privacy`).
