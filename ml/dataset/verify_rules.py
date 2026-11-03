import re
from typing import Tuple, Optional
from backend.app.compiler.constants import ErrorCategory
from backend.app.compiler.parser import ParsedDiagnostic

def verify_diagnostic(
    category: str,
    primary: Optional[ParsedDiagnostic],
    is_linker_error: bool,
    mutated_line: int
) -> Tuple[bool, str]:
    """
    Loose verification rules ensuring the primary compiler diagnostic
    accurately matches the intended category from the deterministic mutator.
    """
    if primary is None:
        return False, "no_primary_diagnostic"

    msg = primary.message.lower()
    all_notes = " ".join(primary.notes).lower()

    if category == ErrorCategory.MISSING_SEMICOLON.value:
        patterns = [
            "expected ';'", "expected ',' or ';'", "expected primary-expression before ';'",
            "expected ';' at end", "before '}'", "before 'return'"
        ]
        if any(p in msg for p in patterns) or ";" in msg:
            return True, "semicolon.pattern_matched"
        return False, f"semicolon.unmatched_msg: {primary.message}"

    elif category == ErrorCategory.UNDECLARED_IDENTIFIER.value:
        patterns = [
            "was not declared in this scope", "has not been declared",
            "not declared in this scope", "was not declared"
        ]
        if any(p in msg for p in patterns):
            return True, "undeclared.pattern_matched"
        return False, f"undeclared.unmatched_msg: {primary.message}"

    elif category == ErrorCategory.TYPE_MISMATCH.value:
        patterns = [
            "cannot convert", "invalid conversion", "incompatible type",
            "conversion from", "invalid operands of types", "no viable conversion"
        ]
        if any(p in msg for p in patterns):
            return True, "type_mismatch.pattern_matched"
        return False, f"type_mismatch.unmatched_msg: {primary.message}"

    elif category == ErrorCategory.UNMATCHED_BRACES.value:
        patterns = [
            "expected '}'", "expected '{'", "expected declaration before '}'",
            "at end of input", "unmatched '}'", "expected primary-expression before '}'"
        ]
        if any(p in msg for p in patterns) or "}" in msg or "{" in msg:
            return True, "unmatched_braces.pattern_matched"
        return False, f"unmatched_braces.unmatched_msg: {primary.message}"

    elif category == ErrorCategory.UNMATCHED_PARENTHESES.value:
        patterns = [
            "expected ')'", "expected '('", "before ')'", "before '('",
            "unmatched '('", "unmatched ')'"
        ]
        if any(p in msg for p in patterns) or ")" in msg or "(" in msg:
            return True, "unmatched_parentheses.pattern_matched"
        return False, f"unmatched_parentheses.unmatched_msg: {primary.message}"

    elif category == ErrorCategory.MISSING_RETURN.value:
        patterns = [
            "control reaches end of non-void function",
            "no return statement in function returning non-void",
            "return-statement with no value"
        ]
        if any(p in msg for p in patterns):
            return True, "missing_return.pattern_matched"
        return False, f"missing_return.unmatched_msg: {primary.message}"

    elif category == ErrorCategory.INVALID_DECLARATION.value:
        patterns = [
            "redeclaration of", "redefinition of", "conflicting declaration",
            "declared void", "has no initializer", "two or more data types",
            "previous declaration", "declared here"
        ]
        if any(p in msg for p in patterns):
            return True, "invalid_declaration.pattern_matched"
        return False, f"invalid_declaration.unmatched_msg: {primary.message}"

    elif category == ErrorCategory.MISSING_HEADER.value:
        patterns = [
            "has not been declared", "was not declared in this scope",
            "not defined in this scope", "incomplete type", "did you forget to",
            "is not a member of 'std'"
        ]
        if any(p in msg for p in patterns) or "include" in all_notes or "did you forget" in all_notes:
            return True, "missing_header.pattern_matched"
        return False, f"missing_header.unmatched_msg: {primary.message}"

    elif category == ErrorCategory.MISSING_NAMESPACE.value:
        patterns = [
            "did you mean 'std::", "was not declared in this scope",
            "is not a member of 'std'", "has not been declared",
            "'cout' was not declared", "'cin' was not declared", "'endl' was not declared"
        ]
        if any(p in msg for p in patterns) or "did you mean 'std::" in all_notes:
            return True, "missing_namespace.pattern_matched"
        return False, f"missing_namespace.unmatched_msg: {primary.message}"

    elif category == ErrorCategory.UNDEFINED_REFERENCE.value:
        if is_linker_error or "undefined reference to" in msg:
            return True, "undefined_reference.linker_matched"
        return False, f"undefined_reference.unmatched_msg: {primary.message}"

    elif category == ErrorCategory.WRONG_ARGUMENTS.value:
        patterns = [
            "too few arguments", "too many arguments", "no matching function for call",
            "candidate expects", "cannot convert", "for argument"
        ]
        if any(p in msg for p in patterns):
            return True, "wrong_arguments.pattern_matched"
        return False, f"wrong_arguments.unmatched_msg: {primary.message}"

    elif category == ErrorCategory.CONST_VIOLATION.value:
        patterns = [
            "assignment of read-only", "read-only variable",
            "discards qualifiers", "increment of read-only", "cannot assign to"
        ]
        if any(p in msg for p in patterns):
            return True, "const_violation.pattern_matched"
        return False, f"const_violation.unmatched_msg: {primary.message}"

    return False, f"unknown_category: {category}"
