from enum import Enum
from typing import List, Dict

# Compile command & flags shared between runtime runner and ML dataset generator
COMPILER_FLAGS: List[str] = [
    "g++",
    "-std=c++17",
    "-Wall",
    "-Wextra",
    "-Werror=return-type",
    "-fno-diagnostics-show-caret",
    "-fmessage-length=0",
    "-fdiagnostics-color=never",
    "/workspace/main.cpp",
    "-o",
    "/tmp/a.out"
]

COMPILER_ENV: Dict[str, str] = {
    "LC_ALL": "C",
    "LANG": "C"
}

# The 12 target C++ diagnostic categories
class ErrorCategory(str, Enum):
    MISSING_SEMICOLON = "MISSING_SEMICOLON"
    UNDECLARED_IDENTIFIER = "UNDECLARED_IDENTIFIER"
    TYPE_MISMATCH = "TYPE_MISMATCH"
    UNMATCHED_BRACES = "UNMATCHED_BRACES"
    UNMATCHED_PARENTHESES = "UNMATCHED_PARENTHESES"
    MISSING_RETURN = "MISSING_RETURN"
    INVALID_DECLARATION = "INVALID_DECLARATION"
    MISSING_HEADER = "MISSING_HEADER"
    MISSING_NAMESPACE = "MISSING_NAMESPACE"
    UNDEFINED_REFERENCE = "UNDEFINED_REFERENCE"
    WRONG_ARGUMENTS = "WRONG_ARGUMENTS"
    CONST_VIOLATION = "CONST_VIOLATION"

CATEGORY_STAGES: Dict[str, str] = {
    ErrorCategory.MISSING_SEMICOLON.value: "SYNTAX",
    ErrorCategory.UNDECLARED_IDENTIFIER.value: "SEMANTIC",
    ErrorCategory.TYPE_MISMATCH.value: "SEMANTIC",
    ErrorCategory.UNMATCHED_BRACES.value: "SYNTAX",
    ErrorCategory.UNMATCHED_PARENTHESES.value: "SYNTAX",
    ErrorCategory.MISSING_RETURN.value: "SEMANTIC",
    ErrorCategory.INVALID_DECLARATION.value: "SEMANTIC",
    ErrorCategory.MISSING_HEADER.value: "SEMANTIC",
    ErrorCategory.MISSING_NAMESPACE.value: "SEMANTIC",
    ErrorCategory.UNDEFINED_REFERENCE.value: "LINKER",
    ErrorCategory.WRONG_ARGUMENTS.value: "SEMANTIC",
    ErrorCategory.CONST_VIOLATION.value: "SEMANTIC",
}
